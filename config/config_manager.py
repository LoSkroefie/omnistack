from typing import Any, Dict, Optional
import os
import yaml
from pathlib import Path
from dataclasses import dataclass
import json

@dataclass
class AIConfig:
    model_name: str
    batch_size: int
    max_sequence_length: int
    temperature: float
    cache_size: int

@dataclass
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str
    database: str
    pool_size: int

@dataclass
class APIConfig:
    host: str
    port: int
    workers: int
    timeout: int
    cors_origins: list[str]

@dataclass
class MonitoringConfig:
    telemetry_enabled: bool
    log_level: str
    sentry_dsn: Optional[str]
    metrics_port: int

class ConfigManager:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config.yaml"
        self.config: Dict[str, Any] = {}
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.load_config()
    
    def load_config(self):
        """Load configuration from file and environment variables."""
        # Load base config
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        
        # Load environment-specific config
        env_config_path = f"config.{self.environment}.yaml"
        if os.path.exists(env_config_path):
            with open(env_config_path, 'r') as f:
                env_config = yaml.safe_load(f)
                self.config = self._deep_merge(self.config, env_config)
        
        # Override with environment variables
        self._override_from_env()
    
    def get_ai_config(self) -> AIConfig:
        """Get AI-related configuration."""
        config = self.config.get('ai', {})
        return AIConfig(
            model_name=config.get('model_name', 'microsoft/codebert-base'),
            batch_size=config.get('batch_size', 32),
            max_sequence_length=config.get('max_sequence_length', 512),
            temperature=config.get('temperature', 0.7),
            cache_size=config.get('cache_size', 1000)
        )
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration."""
        config = self.config.get('database', {})
        return DatabaseConfig(
            host=config.get('host', 'localhost'),
            port=config.get('port', 5432),
            username=config.get('username', 'postgres'),
            password=config.get('password', ''),
            database=config.get('database', 'omnistack'),
            pool_size=config.get('pool_size', 10)
        )
    
    def get_api_config(self) -> APIConfig:
        """Get API configuration."""
        config = self.config.get('api', {})
        return APIConfig(
            host=config.get('host', '0.0.0.0'),
            port=config.get('port', 8000),
            workers=config.get('workers', 4),
            timeout=config.get('timeout', 30),
            cors_origins=config.get('cors_origins', ['*'])
        )
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration."""
        config = self.config.get('monitoring', {})
        return MonitoringConfig(
            telemetry_enabled=config.get('telemetry_enabled', True),
            log_level=config.get('log_level', 'INFO'),
            sentry_dsn=config.get('sentry_dsn'),
            metrics_port=config.get('metrics_port', 9090)
        )
    
    def _override_from_env(self):
        """Override configuration with environment variables."""
        for key, value in os.environ.items():
            if key.startswith('OMNISTACK_'):
                path = key[10:].lower().split('_')
                self._set_nested_value(self.config, path, value)
    
    def _set_nested_value(
        self,
        config: Dict,
        path: list[str],
        value: Any
    ):
        """Set nested dictionary value using path."""
        current = config
        for part in path[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Convert value to appropriate type
        try:
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif '.' in value:
                value = float(value)
            else:
                value = int(value)
        except (ValueError, AttributeError):
            # Keep as string if conversion fails
            pass
        
        current[path[-1]] = value
    
    def _deep_merge(
        self,
        dict1: Dict,
        dict2: Dict
    ) -> Dict:
        """Deep merge two dictionaries."""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if (
                key in result and
                isinstance(result[key], dict) and
                isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def save_config(self):
        """Save current configuration to file."""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags configuration."""
        return self.config.get('feature_flags', {})
    
    def update_feature_flags(self, flags: Dict[str, bool]):
        """Update feature flags configuration."""
        self.config['feature_flags'] = flags
        self.save_config()

class FeatureManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.features = self.config_manager.get_feature_flags()
    
    def is_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled."""
        return self.features.get(feature_name, False)
    
    def enable_feature(self, feature_name: str):
        """Enable a feature."""
        self.features[feature_name] = True
        self.config_manager.update_feature_flags(self.features)
    
    def disable_feature(self, feature_name: str):
        """Disable a feature."""
        self.features[feature_name] = False
        self.config_manager.update_feature_flags(self.features)
