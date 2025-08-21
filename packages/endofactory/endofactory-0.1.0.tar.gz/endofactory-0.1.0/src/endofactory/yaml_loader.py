"""YAML configuration loader for EndoFactory."""

import yaml
from pathlib import Path
from typing import Dict, Any
from .config import EndoFactoryConfig


class YAMLConfigLoader:
    """Loader for YAML configuration files."""
    
    @staticmethod
    def load_config(config_path: Path) -> EndoFactoryConfig:
        """Load configuration from YAML file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        
        return EndoFactoryConfig(**config_dict)
    
    @staticmethod
    def save_config(config: EndoFactoryConfig, output_path: Path) -> None:
        """Save configuration to YAML file."""
        config_dict = config.dict()
        
        # Convert Path objects to strings for YAML serialization
        YAMLConfigLoader._convert_paths_to_strings(config_dict)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
    
    @staticmethod
    def _convert_paths_to_strings(obj: Any) -> None:
        """Recursively convert Path objects to strings."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, Path):
                    obj[key] = str(value)
                elif isinstance(value, (dict, list)):
                    YAMLConfigLoader._convert_paths_to_strings(value)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, Path):
                    obj[i] = str(item)
                elif isinstance(item, (dict, list)):
                    YAMLConfigLoader._convert_paths_to_strings(item)
    
    @staticmethod
    def create_example_config() -> Dict[str, Any]:
        """Create an example configuration dictionary."""
        # Match example_config.yaml structure and paths
        repo_root = Path(__file__).resolve().parents[2]
        td = repo_root / "test_data"

        v1_img_str = str(td / "endoscopy_vqa_v1" / "images")
        v1_parquet_str = str(td / "endoscopy_vqa_v1" / "metadata.parquet")
        v2_img_str = str(td / "medical_vqa_v2" / "images")
        v2_parquet_str = str(td / "medical_vqa_v2" / "metadata.parquet")

        return {
            "datasets": [
                {
                    "name": "endoscopy_vqa_v1",
                    "image_path": v1_img_str,
                    "parquet_path": v1_parquet_str,
                    "weight": 0.6,
                },
                {
                    "name": "medical_vqa_v2",
                    "image_path": v2_img_str,
                    "parquet_path": v2_parquet_str,
                    "weight": 0.4,
                }
            ],
            "columns": [
                "uuid",
                "question",
                "answer",
                "options",
                "task",
                "subtask",
                "category",
                "scene",
            ],
            "task_proportions": {
                "task_proportions": {
                    "classification": 0.4,
                    "detection": 0.3,
                    "segmentation": 0.3
                },
                "subtask_proportions": {
                    "classification": {
                        "organ_classification": 0.5,
                        "disease_classification": 0.5
                    },
                    "detection": {
                        "polyp_detection": 0.7,
                        "lesion_detection": 0.3
                    }
                }
            },
            "export": {
                "output_path": "./output",
                "format": "parquet",
                "include_absolute_paths": True
            },
            "seed": 42
        }
