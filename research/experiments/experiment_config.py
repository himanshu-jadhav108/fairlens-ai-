"""
Experiment Configuration Dataclass for FairLens AI Research.
Provides strong typing and serialization for configuration-driven reproducibility.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import uuid


@dataclass
class ExperimentConfig:
    """Rigorous configuration specification for a single experiment."""
    dataset_name: str
    model_name: str
    mitigation_name: str
    seed: int = 42
    
    experiment_id: Optional[str] = None
    description: str = "Fairness-Performance-Explainability evaluation"
    
    # Split configuration
    train_ratio: float = 0.60
    val_ratio: float = 0.20
    test_ratio: float = 0.20
    
    # Data source settings
    use_synthetic_benchmark: bool = False
    local_dataset_path: Optional[str] = None
    
    # Model and mitigation hyperparameters
    model_params: Dict[str, Any] = field(default_factory=dict)
    mitigation_params: Dict[str, Any] = field(default_factory=dict)
    
    # Explainability settings
    n_eval_samples: int = 150
    n_background_samples: int = 100
    explainer_type: str = "auto"
    
    def __post_init__(self):
        if self.experiment_id is None:
            short_id = str(uuid.uuid4())[:8]
            self.experiment_id = (
                f"{self.dataset_name}__{self.model_name}__{self.mitigation_name}__seed{self.seed}__{short_id}"
            )
