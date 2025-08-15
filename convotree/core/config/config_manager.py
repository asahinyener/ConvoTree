#!/usr/bin/env python3
"""
Configuration Management System for ConvoTree
Provides flexible, environment-aware configuration with validation
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class ModelConfig:
    """Configuration for LLM models"""
    name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return asdict(self)

@dataclass 
class CacheConfig:
    """Configuration for caching system"""
    enabled: bool = True
    size: int = 1000
    ttl: int = 300  # seconds
    cleanup_threshold: int = 1200  # when to trigger cleanup
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return asdict(self)

@dataclass
class DatabaseConfig:
    """Configuration for database"""
    path: str = "conversations.db"
    timeout: float = 10.0
    backup_interval: int = 3600  # seconds
    max_conversations: int = 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return asdict(self)

@dataclass
class UIConfig:
    """Configuration for user interface"""
    debug_mode: bool = False
    verbose_logging: bool = True
    show_performance_stats: bool = False
    auto_save_interval: int = 300  # seconds
    max_history_display: int = 50
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return asdict(self)

@dataclass
class SecurityConfig:
    """Configuration for security settings"""
    api_key_validation: bool = True
    rate_limiting: bool = False
    max_requests_per_minute: int = 60
    enable_audit_log: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return asdict(self)

@dataclass
class ConvoTreeConfig:
    """Main configuration container"""
    model: ModelConfig
    cache: CacheConfig
    database: DatabaseConfig
    ui: UIConfig
    security: SecurityConfig
    version: str = "2.0.0"
    environment: str = "development"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConvoTreeConfig':
        """Create config from dictionary"""
        return cls(
            model=ModelConfig(**data.get('model', {})),
            cache=CacheConfig(**data.get('cache', {})),
            database=DatabaseConfig(**data.get('database', {})),
            ui=UIConfig(**data.get('ui', {})),
            security=SecurityConfig(**data.get('security', {})),
            version=data.get('version', '2.0.0'),
            environment=data.get('environment', 'development')
        )

class ConfigManager:
    """Manages configuration loading, validation, and environment-specific settings"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else self._find_config_file()
        self._config: Optional[ConvoTreeConfig] = None
        self._config_loaded_at: Optional[datetime] = None
        
    def _find_config_file(self) -> Optional[Path]:
        """Find configuration file in standard locations"""
        possible_paths = [
            Path(".convotree.yaml"),
            Path(".convotree.yml"), 
            Path("config/convotree.yaml"),
            Path("convotree.yaml"),
            Path.home() / ".config" / "convotree" / "config.yaml",
            Path("/etc/convotree/config.yaml")
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def load_config(self, force_reload: bool = False) -> ConvoTreeConfig:
        """Load configuration with environment variable overrides"""
        if self._config is not None and not force_reload:
            return self._config
        
        # Start with defaults
        config_data = self._get_default_config()
        
        # Load from file if exists
        if self.config_path and self.config_path.exists():
            try:
                file_config = self._load_config_file(self.config_path)
                config_data = self._merge_configs(config_data, file_config)
            except Exception as e:
                print(f"⚠️ Error loading config file {self.config_path}: {e}")
                print("Using default configuration")
        
        # Apply environment variable overrides
        config_data = self._apply_env_overrides(config_data)
        
        # Validate configuration
        self._validate_config(config_data)
        
        # Create config object
        self._config = ConvoTreeConfig.from_dict(config_data)
        self._config_loaded_at = datetime.now()
        
        return self._config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        default_config = ConvoTreeConfig(
            model=ModelConfig(),
            cache=CacheConfig(),
            database=DatabaseConfig(),
            ui=UIConfig(),
            security=SecurityConfig()
        )
        return default_config.to_dict()
    
    def _load_config_file(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from YAML or JSON file"""
        with open(config_path, 'r') as f:
            if config_path.suffix.lower() in ['.yml', '.yaml']:
                return yaml.safe_load(f) or {}
            elif config_path.suffix.lower() == '.json':
                return json.load(f)
            else:
                raise ValueError(f"Unsupported config file format: {config_path.suffix}")
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two configuration dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides"""
        env_mappings = {
            # Model settings
            'CONVOTREE_MODEL': ('model', 'name'),
            'CONVOTREE_TEMPERATURE': ('model', 'temperature'),
            'CONVOTREE_MAX_TOKENS': ('model', 'max_tokens'),
            'CONVOTREE_TIMEOUT': ('model', 'timeout'),
            
            # Cache settings
            'CONVOTREE_CACHE_SIZE': ('cache', 'size'),
            'CONVOTREE_CACHE_TTL': ('cache', 'ttl'),
            'CONVOTREE_CACHE_ENABLED': ('cache', 'enabled'),
            
            # Database settings  
            'CONVOTREE_DB_PATH': ('database', 'path'),
            'CONVOTREE_DB_TIMEOUT': ('database', 'timeout'),
            
            # UI settings
            'CONVOTREE_DEBUG': ('ui', 'debug_mode'),
            'CONVOTREE_VERBOSE': ('ui', 'verbose_logging'),
            
            # Environment
            'CONVOTREE_ENV': ('environment',),
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Navigate to the config location
                current = config
                for key in config_path[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                
                # Convert value to appropriate type
                final_key = config_path[-1]
                current[final_key] = self._convert_env_value(value)
        
        return config
    
    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Convert environment variable string to appropriate type"""
        # Boolean values
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Numeric values
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # String value
        return value
    
    def _validate_config(self, config: Dict[str, Any]):
        """Validate configuration values"""
        errors = []
        
        # Validate model settings
        model_config = config.get('model', {})
        if model_config.get('temperature', 0) < 0 or model_config.get('temperature', 0) > 2:
            errors.append("Model temperature must be between 0 and 2")
        
        if model_config.get('max_tokens', 0) <= 0:
            errors.append("Model max_tokens must be positive")
        
        # Validate cache settings
        cache_config = config.get('cache', {})
        if cache_config.get('size', 0) <= 0:
            errors.append("Cache size must be positive")
        
        if cache_config.get('ttl', 0) <= 0:
            errors.append("Cache TTL must be positive")
        
        # Validate database settings
        db_config = config.get('database', {})
        if not db_config.get('path'):
            errors.append("Database path cannot be empty")
        
        # Security validation
        if not os.getenv('OPENAI_API_KEY'):
            errors.append("OPENAI_API_KEY environment variable is required")
        
        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors))
    
    def save_config(self, config: ConvoTreeConfig, path: Optional[Path] = None):
        """Save configuration to file"""
        save_path = path or self.config_path or Path("convotree.yaml")
        
        config_dict = config.to_dict()
        
        with open(save_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        
        print(f"✅ Configuration saved to {save_path}")
    
    def create_sample_config(self, path: Optional[Path] = None):
        """Create a sample configuration file"""
        sample_path = path or Path("convotree.sample.yaml")
        
        sample_config = ConvoTreeConfig(
            model=ModelConfig(),
            cache=CacheConfig(),
            database=DatabaseConfig(),
            ui=UIConfig(),
            security=SecurityConfig()
        )
        
        sample_dict = sample_config.to_dict()
        
        # Add comments for documentation
        sample_content = f"""# ConvoTree Configuration File
# Generated on: {datetime.now().isoformat()}

# Model configuration for LLM interactions
model:
  name: "{sample_dict['model']['name']}"  # Model to use (gpt-4o-mini, gpt-4, etc.)
  temperature: {sample_dict['model']['temperature']}  # Response randomness (0.0-2.0)
  max_tokens: {sample_dict['model']['max_tokens']}  # Maximum response length
  timeout: {sample_dict['model']['timeout']}  # API timeout in seconds
  max_retries: {sample_dict['model']['max_retries']}  # Number of retry attempts
  retry_delay: {sample_dict['model']['retry_delay']}  # Delay between retries

# Caching configuration for performance
cache:
  enabled: {sample_dict['cache']['enabled']}  # Enable/disable caching
  size: {sample_dict['cache']['size']}  # Maximum cache items
  ttl: {sample_dict['cache']['ttl']}  # Cache time-to-live in seconds
  cleanup_threshold: {sample_dict['cache']['cleanup_threshold']}  # When to cleanup cache

# Database configuration
database:
  path: "{sample_dict['database']['path']}"  # SQLite database file path
  timeout: {sample_dict['database']['timeout']}  # Database timeout in seconds
  backup_interval: {sample_dict['database']['backup_interval']}  # Backup frequency in seconds
  max_conversations: {sample_dict['database']['max_conversations']}  # Maximum conversations to keep

# User interface configuration
ui:
  debug_mode: {sample_dict['ui']['debug_mode']}  # Enable debug output
  verbose_logging: {sample_dict['ui']['verbose_logging']}  # Detailed logging
  show_performance_stats: {sample_dict['ui']['show_performance_stats']}  # Show performance metrics
  auto_save_interval: {sample_dict['ui']['auto_save_interval']}  # Auto-save frequency
  max_history_display: {sample_dict['ui']['max_history_display']}  # Max history items to show

# Security configuration
security:
  api_key_validation: {sample_dict['security']['api_key_validation']}  # Validate API keys
  rate_limiting: {sample_dict['security']['rate_limiting']}  # Enable rate limiting
  max_requests_per_minute: {sample_dict['security']['max_requests_per_minute']}  # Rate limit
  enable_audit_log: {sample_dict['security']['enable_audit_log']}  # Log security events

# System information
version: "{sample_dict['version']}"
environment: "{sample_dict['environment']}"  # development, production, testing

# Environment Variables (alternative to file config):
# CONVOTREE_MODEL=gpt-4o-mini
# CONVOTREE_TEMPERATURE=0.7
# CONVOTREE_CACHE_SIZE=1000
# CONVOTREE_DEBUG=true
# OPENAI_API_KEY=your_api_key_here
"""
        
        with open(sample_path, 'w') as f:
            f.write(sample_content)
        
        print(f"📝 Sample configuration created at {sample_path}")
        print("Edit this file and rename to .convotree.yaml to use")
    
    def get_config(self) -> ConvoTreeConfig:
        """Get current configuration (loads if not already loaded)"""
        if self._config is None:
            return self.load_config()
        return self._config
    
    def reload_config(self) -> ConvoTreeConfig:
        """Force reload configuration from file"""
        return self.load_config(force_reload=True)
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get information about current configuration"""
        return {
            "config_file": str(self.config_path) if self.config_path else None,
            "config_exists": self.config_path.exists() if self.config_path else False,
            "loaded_at": self._config_loaded_at.isoformat() if self._config_loaded_at else None,
            "version": self._config.version if self._config else None,
            "environment": self._config.environment if self._config else None
        }