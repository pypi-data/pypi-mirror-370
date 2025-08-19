"""
Configuration loader for rust-crate-pipeline.
Loads configuration from JSON files and provides a clean interface.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads and manages configuration from JSON files."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration loader.

        Args:
            config_path: Path to configuration JSON file. If None, uses default.
        """
        if config_path is None:
            # Try to find config in standard locations
            possible_paths = [
                "configs/instance_config.json",
                "instance_config.json",
                "config.json",
                "~/.rust_crate_pipeline/config.json",
            ]

            for path in possible_paths:
                expanded_path = os.path.expanduser(path)
                if os.path.exists(expanded_path):
                    config_path = expanded_path
                    break
            else:
                # Use default config
                config_path = "configs/instance_config.json"

        self.config_path = config_path
        self._config = None
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._config = json.load(f)
            logger.info(f"✅ Loaded configuration from {self.config_path}")
        except FileNotFoundError:
            logger.warning(f"⚠️  Configuration file {self.config_path} not found, using defaults")
            self._config = self._get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in configuration file {self.config_path}: {e}")
            self._config = self._get_default_config()
        except Exception as e:
            logger.error(f"❌ Error loading configuration: {e}")
            self._config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for A100 instance."""
        return {
            "hardware_profile": {
                "gpu_model": "A100-SXM4-40GB",
                "gpu_vram_gb": 40,
                "cpu_cores": 30,
                "cpu_threads": 30,
                "ram_gb": 200,
                "storage_gb": 500,
            },
            "llm_config": {
                "model_path": "~/models/deepseek-coder-33b-instruct.Q4_K_M.gguf",
                "provider": "llama-cpp-python",
                "temperature": 0.1,
                "max_tokens": 4096,
                "timeout": 120,
                "max_retries": 4,
                "context_length": 8192,
                "batch_size": 4096,
                "gpu_layers": 50,
                "cpu_threads": 16,
                "batch_threads": 16,
                "gpu_optimizations": {
                    "offload_kqv": True,
                    "mul_mat_q": True,
                    "f16_kv": True,
                    "flash_attn": True,
                    "use_mmap": True,
                    "use_mlock": True,
                    "rope_scaling_type": 1,
                    "rope_freq_base": 10000.0,
                },
            },
            "pipeline_config": {
                "max_workers": 8,
                "batch_size": 8,
                "enable_gpu": True,
                "gpu_memory_fraction": 0.9,
                "crate_limit": 100,
                "output_dir": "./output",
                "log_level": "INFO",
                "use_batch_processing": True,
                "batch_enrichment_size": 8,
                "llm_batch_size": 32,
                "enable_gpu_optimizations": True,
                "reduce_cpu_overhead": True,
                "enable_caching": True,
                "cache_ttl": 3600,
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'llm_config.temperature')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration section."""
        return self._config.get("llm_config", {})

    def get_pipeline_config(self) -> Dict[str, Any]:
        """Get pipeline configuration section."""
        return self._config.get("pipeline_config", {})

    def get_hardware_profile(self) -> Dict[str, Any]:
        """Get hardware profile section."""
        return self._config.get("hardware_profile", {})

    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing configuration section."""
        return self._config.get("processing_config", {})

    def get_validation_config(self) -> Dict[str, Any]:
        """Get validation configuration section."""
        return self._config.get("validation_config", {})

    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration section."""
        return self._config.get("monitoring_config", {})

    def get_caching_config(self) -> Dict[str, Any]:
        """Get caching configuration section."""
        return self._config.get("caching_config", {})

    def get_error_handling_config(self) -> Dict[str, Any]:
        """Get error handling configuration section."""
        return self._config.get("error_handling", {})

    def get_performance_tuning_config(self) -> Dict[str, Any]:
        """Get performance tuning configuration section."""
        return self._config.get("performance_tuning", {})

    def update(self, key: str, value: Any) -> None:
        """
        Update configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'llm_config.temperature')
            value: New value
        """
        keys = key.split(".")
        config = self._config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value

    def save(self, path: Optional[str] = None) -> None:
        """
        Save current configuration to file.

        Args:
            path: Path to save configuration. If None, uses original path.
        """
        save_path = path or self.config_path

        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Configuration saved to {save_path}")
        except Exception as e:
            logger.error(f"❌ Error saving configuration: {e}")

    def validate(self) -> bool:
        """
        Validate configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Check required sections
            required_sections = ["llm_config", "pipeline_config", "hardware_profile"]
            for section in required_sections:
                if section not in self._config:
                    logger.error(f"❌ Missing required configuration section: {section}")
                    return False

            # Validate hardware profile
            hw = self.get_hardware_profile()
            if hw.get("gpu_vram_gb", 0) <= 0:
                logger.error("❌ Invalid GPU VRAM configuration")
                return False

            # Validate LLM config
            llm = self.get_llm_config()
            if not llm.get("model_path"):
                logger.error("❌ Model path not specified")
                return False

            logger.info("✅ Configuration validation passed")
            return True

        except Exception as e:
            logger.error(f"❌ Configuration validation failed: {e}")
            return False

    def get_optimized_config_for_hardware(self) -> Dict[str, Any]:
        """
        Get configuration optimized for the current hardware profile.

        Returns:
            Optimized configuration dictionary
        """
        hw = self.get_hardware_profile()
        gpu_vram = hw.get("gpu_vram_gb", 8)
        cpu_cores = hw.get("cpu_cores", 4)

        # Auto-optimize based on hardware
        optimized = self._config.copy()

        # Adjust GPU layers based on VRAM
        if gpu_vram >= 40:  # A100
            optimized["llm_config"]["gpu_layers"] = 50
            optimized["llm_config"]["batch_size"] = 4096
            optimized["pipeline_config"]["batch_size"] = 8
        elif gpu_vram >= 24:  # L4
            optimized["llm_config"]["gpu_layers"] = 35
            optimized["llm_config"]["batch_size"] = 2048
            optimized["pipeline_config"]["batch_size"] = 4
        elif gpu_vram >= 16:  # V100
            optimized["llm_config"]["gpu_layers"] = 30
            optimized["llm_config"]["batch_size"] = 1024
            optimized["pipeline_config"]["batch_size"] = 2
        else:  # CPU only or small GPU
            optimized["llm_config"]["gpu_layers"] = 0
            optimized["llm_config"]["batch_size"] = 512
            optimized["pipeline_config"]["batch_size"] = 1

        # Adjust CPU threads
        optimized["llm_config"]["cpu_threads"] = min(cpu_cores, 16)
        optimized["llm_config"]["batch_threads"] = min(cpu_cores, 16)

        return optimized


# Global configuration instance
_config_loader: Optional[ConfigLoader] = None


def get_config_loader(config_path: Optional[str] = None) -> ConfigLoader:
    """
    Get global configuration loader instance.

    Args:
        config_path: Path to configuration file

    Returns:
        ConfigLoader instance
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader(config_path)
    return _config_loader


def get_config(key: str, default: Any = None) -> Any:
    """
    Get configuration value.

    Args:
        key: Configuration key
        default: Default value

    Returns:
        Configuration value
    """
    return get_config_loader().get(key, default)
