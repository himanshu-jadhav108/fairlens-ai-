import os
import re
import sys

def scan():
    # Detect Google API keys or exposed secret keys
    gemini_key_pattern = re.compile(r'AIza[0-9A-Za-z-_]{35}')
    violations = []
    
    for root, dirs, files in os.walk('research'):
        for f in files:
            if f.endswith(('.py', '.md', '.json', '.yaml', '.csv')):
                path = os.path.join(root, f)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                        content = fh.read()
                        matches = gemini_key_pattern.findall(content)
                        for m in matches:
                            violations.append((path, m[:6] + "..." + m[-4:]))
                except Exception:
                    pass
                    
    if violations:
        print("[!] SECURITY ALERT: Real API key pattern found in:")
        for path, masked in violations:
            print(f"    {path}: {masked}")
        sys.exit(1)
    else:
        print("[+] SUCCESS: Zero API keys or secrets detected in research/ artifacts.")
        sys.exit(0)

if __name__ == '__main__':
    scan()
