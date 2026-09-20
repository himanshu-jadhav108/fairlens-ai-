"""
Gemini LLM Provider for FairLens AI Research.

Adapts Google Generative AI for research experiments with explicit provenance,
deterministic parameters, strict API-key isolation, and multi-credential rotation.
"""
import time
import os
import re
from typing import Optional, Dict, Any, List, Tuple
from .base import BaseLLMProvider
from ..schemas import LLMGenerationConfig, LLMResponse

try:
    import google.generativeai as genai
    _GENAI_AVAILABLE = True
    _GENAI_VERSION = getattr(genai, "__version__", "unknown")
except ImportError:
    genai = None
    _GENAI_AVAILABLE = False
    _GENAI_VERSION = "not_installed"


# Global persistence for credential health and cooldowns across provider instances
_GLOBAL_INCOMPATIBLE_ALIASES = set()
_GLOBAL_CRED_COOLDOWNS: Dict[str, float] = {}
_GLOBAL_CRED_IDX = 0


def _discover_gemini_credentials() -> List[Tuple[str, str]]:
    """
    Discovers available Gemini credentials across research/.env, backend/.env, .env,
    and os.environ, prioritizing default and specific account keys.
    Returns list of (alias, api_key) pairs.
    """
    credentials: List[Tuple[str, str]] = []
    seen_keys = set()

    def add_cred(alias: str, key: Optional[str]):
        if not key:
            return
        key_clean = key.strip().strip('"').strip("'")
        if key_clean and key_clean not in seen_keys:
            seen_keys.add(key_clean)
            credentials.append((alias, key_clean))

    # 1. Environment variables
    add_cred("gemini_account_default", os.environ.get("GEMINI_API_KEY"))
    add_cred("gemini_account_default", os.environ.get("GEMINI_API_KEY_DEFAULT"))
    add_cred("gemini_account_3", os.environ.get("GEMINI_API_KEY_ACCOUNT_3"))
    add_cred("gemini_account_1", os.environ.get("GEMINI_API_KEY_ACCOUNT_1"))
    add_cred("gemini_account_2", os.environ.get("GEMINI_API_KEY_ACCOUNT_2"))

    # 2. Local env files — only load from disk if environment is not mocked/cleared
    if not credentials and ("PATH" in os.environ or "SYSTEMROOT" in os.environ or "USERNAME" in os.environ):
        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        for rel_path in ["research/.env", "backend/.env", ".env"]:
            env_file = os.path.join(workspace_root, rel_path)
            if os.path.exists(env_file):
                try:
                    with open(env_file, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#") and "=" in line:
                                k, v = line.split("=", 1)
                                k = k.strip()
                                v = v.strip().strip('"').strip("'")
                                if k == "GEMINI_API_KEY" or k == "GEMINI_API_KEY_DEFAULT":
                                    add_cred("gemini_account_default", v)
                                elif k.startswith("GEMINI_API_KEY_"):
                                    alias = k.replace("GEMINI_API_KEY_", "").lower()
                                    add_cred(f"gemini_{alias}", v)
                except Exception:
                    pass

    return credentials


class GeminiProvider(BaseLLMProvider):
    """
    Research-grade provider for Google Gemini API.
    Enforces strict model adherence (no fallback to Lite) and credential rotation.
    """

    def __init__(self, api_key: Optional[str] = None):
        global _GLOBAL_CRED_IDX
        if not _GENAI_AVAILABLE:
            raise ImportError(
                "google-generativeai package is not installed. "
                "Install it via: pip install google-generativeai"
            )

        self._credentials: List[Tuple[str, str]] = []
        if api_key:
            self._credentials.append(("gemini_custom_key", api_key))
        else:
            self._credentials = _discover_gemini_credentials()

        if not self._credentials:
            raise ValueError(
                "GEMINI_API_KEY is not set. Please set the GEMINI_API_KEY environment variable. "
                "For testing without an API key, use MockLLMProvider."
            )

        self._current_cred_idx = _GLOBAL_CRED_IDX % len(self._credentials)
        self._incompatible_aliases = set(_GLOBAL_INCOMPATIBLE_ALIASES)
        self._configure_active_credential()

    def _configure_active_credential(self) -> Tuple[str, str]:
        """Configures genai with the currently selected credential."""
        alias, key = self._credentials[self._current_cred_idx]
        genai.configure(api_key=key)
        return alias, key

    def _rotate_credential(self, preferred_aliases: Optional[List[str]] = None) -> Tuple[str, str]:
        """Rotates to the next available compatible credential, optionally prioritizing preferred_aliases."""
        global _GLOBAL_CRED_IDX
        n_creds = len(self._credentials)

        # If preferred aliases are provided, try to switch to one of them first
        if preferred_aliases:
            for i in range(1, n_creds + 1):
                idx = (self._current_cred_idx + i) % n_creds
                alias, key = self._credentials[idx]
                if alias in preferred_aliases and alias not in self._incompatible_aliases and alias not in _GLOBAL_INCOMPATIBLE_ALIASES:
                    self._current_cred_idx = idx
                    _GLOBAL_CRED_IDX = idx
                    print(f"[*] GeminiProvider: Rotating to ready credential '{alias}'...", flush=True)
                    genai.configure(api_key=key)
                    return alias, key

        for _ in range(n_creds):
            self._current_cred_idx = (self._current_cred_idx + 1) % n_creds
            _GLOBAL_CRED_IDX = self._current_cred_idx
            alias, key = self._credentials[self._current_cred_idx]
            if alias not in self._incompatible_aliases and alias not in _GLOBAL_INCOMPATIBLE_ALIASES:
                print(f"[*] GeminiProvider: Rotating to credential '{alias}'...", flush=True)
                genai.configure(api_key=key)
                return alias, key
        alias, key = self._credentials[self._current_cred_idx]
        genai.configure(api_key=key)
        return alias, key

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def sdk_version(self) -> str:
        return f"google-generativeai-{_GENAI_VERSION}"

    def generate(
        self,
        prompt: str,
        config: Optional[LLMGenerationConfig] = None
    ) -> LLMResponse:
        """
        Executes generation using Gemini API with exact research configuration.
        Strictly enforces the requested model without silent fallbacks.
        Rotates credentials and handles rate limits deterministically.
        """
        global _GLOBAL_INCOMPATIBLE_ALIASES, _GLOBAL_CRED_COOLDOWNS
        cfg = config or LLMGenerationConfig()
        start_time = time.time()

        gen_config = {
            "temperature": cfg.temperature,
            "max_output_tokens": cfg.max_output_tokens,
            "top_p": cfg.top_p,
        }

        # STRICT MODEL ENFORCEMENT: Never silently fallback to gemini-flash-lite-latest
        target_model_name = cfg.model_name
        max_attempts = max(20, len(self._credentials) * 5)
        response = None
        used_alias = self._credentials[self._current_cred_idx][0]
        last_error = None

        for attempt in range(max_attempts):
            alias, key = self._credentials[self._current_cred_idx]
            used_alias = alias

            # Skip known incompatible credentials
            if alias in _GLOBAL_INCOMPATIBLE_ALIASES or alias in self._incompatible_aliases:
                self._rotate_credential()
                continue

            try:
                model = genai.GenerativeModel(
                    model_name=target_model_name,
                    generation_config=gen_config,
                    system_instruction=cfg.system_instruction
                )
                response = model.generate_content(prompt)
                break
            except Exception as e:
                last_error = e
                err_str = str(e)
                err_lower = err_str.lower()

                # If this is the last attempt, don't sleep or rotate further
                if attempt == max_attempts - 1:
                    break

                # Case 1: Model not available for this key/account (404, no longer available, not found)
                if "404" in err_lower or "no longer available" in err_lower or "not available" in err_lower or "not found" in err_lower:
                    print(f"[!] GeminiProvider: Credential '{alias}' does not have access to '{target_model_name}'.", flush=True)
                    _GLOBAL_INCOMPATIBLE_ALIASES.add(alias)
                    self._incompatible_aliases.add(alias)
                    self._rotate_credential()
                    continue

                # Case 2: 429 Quota or rate limit exceeded
                if "429" in err_lower or "resourceexhausted" in err_lower or "rate limit" in err_lower or "quota exceeded" in err_lower:
                    # Extract suggested retry delay from error message
                    retry_delay = 12.0
                    m_delay = re.search(r"Please retry in ([\d\.]+)s", err_str)
                    if m_delay:
                        try:
                            retry_delay = float(m_delay.group(1)) + 1.5
                        except ValueError:
                            pass
                    else:
                        m_sec = re.search(r"seconds:\s*(\d+)", err_str)
                        if m_sec:
                            try:
                                retry_delay = float(m_sec.group(1)) + 1.5
                            except ValueError:
                                pass

                    _GLOBAL_CRED_COOLDOWNS[alias] = time.time() + retry_delay
                    print(f"[*] GeminiProvider: Credential '{alias}' hit quota/rate limit (cooldown: {retry_delay:.1f}s).", flush=True)

                    compatible = [c for c in self._credentials if c[0] not in _GLOBAL_INCOMPATIBLE_ALIASES and c[0] not in self._incompatible_aliases]
                    ready_creds = [c[0] for c in compatible if _GLOBAL_CRED_COOLDOWNS.get(c[0], 0) <= time.time()]

                    if ready_creds:
                        self._rotate_credential(preferred_aliases=ready_creds)
                        continue
                    else:
                        # All compatible credentials are in cooldown; wait for earliest to expire
                        earliest_ready = min(_GLOBAL_CRED_COOLDOWNS.get(c[0], 0) for c in compatible) if compatible else (time.time() + retry_delay)
                        wait_time = max(1.0, earliest_ready - time.time())
                        print(f"[*] GeminiProvider: All available credentials in cooldown. Waiting {wait_time:.1f}s for quota window reset (attempt {attempt + 1}/{max_attempts})...", flush=True)
                        time.sleep(wait_time)
                        ready_now = [c[0] for c in compatible if _GLOBAL_CRED_COOLDOWNS.get(c[0], 0) <= time.time()]
                        if ready_now:
                            self._rotate_credential(preferred_aliases=ready_now)
                        else:
                            self._rotate_credential()
                        continue

                # Any other unexpected failure -> break to raise
                break

        if response is None:
            raise RuntimeError(
                f"Gemini API generation failed after {round(time.time() - start_time, 3)}s: {last_error}"
            )

        latency = round(time.time() - start_time, 3)

        finish_reason = "STOP"
        if hasattr(response, "candidates") and response.candidates:
            finish_reason = str(getattr(response.candidates[0], "finish_reason", "STOP"))

        text = ""
        try:
            text = response.text
        except Exception:
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                    parts_text = [getattr(p, "text", "") for p in candidate.content.parts if hasattr(p, "text")]
                    text = "".join(parts_text)

        if not text.strip():
            raise RuntimeError(
                f"Gemini API returned an empty explanation (finish_reason: {finish_reason}). "
                f"Empty responses are not permitted to enter the research evaluation pipeline."
            )

        usage = getattr(response, "usage_metadata", None)
        prompt_tokens = getattr(usage, "prompt_token_count", None) if usage else None
        completion_tokens = getattr(usage, "candidates_token_count", None) if usage else None

        # Polite 3.5-second pacing to stay safely under the 15 RPM free tier boundary
        time.sleep(3.5)

        return LLMResponse(
            raw_text=text,
            provider_name=self.provider_name,
            model_name=target_model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_seconds=latency,
            finish_reason=finish_reason,
            metadata={
                "temperature": cfg.temperature,
                "max_output_tokens": cfg.max_output_tokens,
                "top_p": cfg.top_p,
                "seed": cfg.seed,
                "credential_alias": used_alias
            }
        )
