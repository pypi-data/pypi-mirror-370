"""
Configuration Wizard for MSA Reasoning Engine
============================================

Interactive setup wizard for configuring the MSA Reasoning Engine with:
- API key setup for Azure, Daytona, and other services
- Redis/PostgreSQL configuration
- Test connection functionality
- Configuration file management
"""

import asyncio
import json
import os
from typing import Dict, Any
import click
from rich.prompt import Prompt, Confirm
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from reasoning_kernel.cli.ui import UIManager
from reasoning_kernel.security.credential_manager import CredentialValidator
from reasoning_kernel.services.daytona_service import DaytonaService


class ConfigWizard:
    """Interactive configuration wizard for MSA Reasoning Engine"""
    
    def __init__(self, verbose: bool = False):
        self.console = Console()
        self.ui = UIManager(verbose=verbose)
        self.validator = CredentialValidator()
        self.config = {}
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "user_config.json")
        
    def _print_welcome(self):
        """Display welcome message and wizard overview"""
        self.ui.print_header("MSA Reasoning Engine Setup Wizard", "bold blue")
        self.console.print(Panel.fit(
            "This wizard will help you configure the MSA Reasoning Engine.\n"
            "You'll be guided through setting up API keys, database connections,\n"
            "and other essential configuration options.",
            title="Welcome",
            border_style="blue"
        ))
        
    def _load_existing_config(self) -> Dict[str, Any]:
        """Load existing configuration if it exists"""
        # Try to load user config first
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.ui.print_warning(f"Could not load existing user config: {e}")
        
        # If no user config, try to load default config
        default_config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "default_config.json")
        if os.path.exists(default_config_file):
            try:
                with open(default_config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.ui.print_warning(f"Could not load default config: {e}")
                
        return {}
        
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            # Ensure config directory exists
            config_dir = os.path.dirname(self.config_file)
            os.makedirs(config_dir, exist_ok=True)
            
            # Save to user config file
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.ui.print_success(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.ui.print_error(f"Error saving configuration: {e}")
            
    async def _test_azure_connection(self, api_key: str, endpoint: str, deployment: str) -> bool:
        """Test Azure OpenAI connection"""
        try:
            # Import Azure OpenAI client
            try:
                from openai import AsyncAzureOpenAI
            except ImportError:
                self.ui.print_warning("Azure OpenAI SDK not installed. Skipping connection test.")
                return True
                
            # Create client and test connection
            client = AsyncAzureOpenAI(
                api_key=api_key,
                azure_endpoint=endpoint,
                api_version="2024-12-01-preview"
            )
            
            # Test with a simple request
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Testing Azure OpenAI connection...", total=None)
                
                try:
                    response = await client.chat.completions.with_raw_response.create(
                        model=deployment,
                        messages=[{"role": "user", "content": "Hello"}],
                        max_tokens=5
                    )
                    progress.update(task, completed=True)
                    self.ui.print_success("Azure OpenAI connection successful!")
                    return True
                except Exception as e:
                    progress.update(task, completed=True)
                    self.ui.print_error(f"Azure OpenAI connection failed: {e}")
                    return False
        except Exception as e:
            self.ui.print_error(f"Error testing Azure connection: {e}")
            return False
            
    async def _test_daytona_connection(self, api_key: str) -> bool:
        """Test Daytona connection"""
        try:
            # Create Daytona service and test
            daytona_service = DaytonaService()
            daytona_service.api_key = api_key
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Testing Daytona connection...", total=None)
                
                try:
                    # Test initialization
                    daytona_service._initialize_client()
                    if daytona_service.daytona_available:
                        progress.update(task, completed=True)
                        self.ui.print_success("Daytona connection successful!")
                        return True
                    else:
                        progress.update(task, completed=True)
                        self.ui.print_error("Daytona service not available")
                        return False
                except Exception as e:
                    progress.update(task, completed=True)
                    self.ui.print_error(f"Daytona connection failed: {e}")
                    return False
        except Exception as e:
            self.ui.print_error(f"Error testing Daytona connection: {e}")
            return False
            
    def _validate_api_key(self, api_key: str, service_name: str) -> bool:
        """Validate API key format"""
        if not api_key or not api_key.strip():
            self.ui.print_error(f"{service_name} API key cannot be empty")
            return False
            
        # Check for placeholder values
        placeholders = ["your_key_here", "placeholder", "changeme", "default", "test", "demo", "example", "sample"]
        if api_key.lower() in placeholders:
            self.ui.print_error(f"{service_name} API key cannot be a placeholder value")
            return False
            
        # Service-specific validation
        if service_name == "Azure OpenAI":
            # Azure keys are typically 32 characters
            if len(api_key) < 32:
                self.ui.print_warning("Azure OpenAI API key seems short. Please verify it's correct.")
                
        elif service_name == "Daytona":
            # Daytona keys should be reasonable length
            if len(api_key) < 10:
                self.ui.print_error("Daytona API key seems too short")
                return False
                
        return True
        
    async def _configure_azure_openai(self, existing_config: Dict[str, Any]) -> Dict[str, str]:
        """Configure Azure OpenAI settings"""
        self.ui.print_subheader("Azure OpenAI Configuration")
        
        # Get existing values or defaults
        default_endpoint = existing_config.get('AZURE_OPENAI_ENDPOINT', 'https://your-resource.openai.azure.com/')
        default_deployment = existing_config.get('AZURE_OPENAI_DEPLOYMENT', 'gpt-4')
        default_api_version = existing_config.get('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')
        
        # Prompt for API key
        api_key = Prompt.ask(
            "[cyan]Azure OpenAI API Key[/cyan] (enter 'skip' to skip)",
            default=existing_config.get('AZURE_OPENAI_API_KEY', ''),
            password=True
        )
        
        if api_key.lower() == 'skip':
            self.ui.print_info("Skipping Azure OpenAI configuration")
            return {}
            
        if not self._validate_api_key(api_key, "Azure OpenAI"):
            return {}
            
        # Prompt for other settings
        endpoint = Prompt.ask("[cyan]Azure OpenAI Endpoint[/cyan]", default=default_endpoint)
        deployment = Prompt.ask("[cyan]Azure OpenAI Deployment[/cyan]", default=default_deployment)
        api_version = Prompt.ask("[cyan]Azure OpenAI API Version[/cyan]", default=default_api_version)
        
        # Test connection if requested
        if Confirm.ask("Test Azure OpenAI connection?", default=True):
            success = await self._test_azure_connection(api_key, endpoint, deployment)
            if not success:
                if not Confirm.ask("Continue anyway?", default=False):
                    return {}
                    
        return {
            'AZURE_OPENAI_API_KEY': api_key,
            'AZURE_OPENAI_ENDPOINT': endpoint,
            'AZURE_OPENAI_DEPLOYMENT': deployment,
            'AZURE_OPENAI_API_VERSION': api_version
        }
        
    async def _configure_daytona(self, existing_config: Dict[str, Any]) -> Dict[str, str]:
        """Configure Daytona settings"""
        self.ui.print_subheader("Daytona Configuration")
        
        # Prompt for API key
        api_key = Prompt.ask(
            "[cyan]Daytona API Key[/cyan] (enter 'skip' to skip)",
            default=existing_config.get('DAYTONA_API_KEY', ''),
            password=True
        )
        
        if api_key.lower() == 'skip':
            self.ui.print_info("Skipping Daytona configuration")
            return {}
            
        if not self._validate_api_key(api_key, "Daytona"):
            return {}
            
        # Test connection if requested
        if Confirm.ask("Test Daytona connection?", default=True):
            success = await self._test_daytona_connection(api_key)
            if not success:
                if not Confirm.ask("Continue anyway?", default=False):
                    return {}
                    
        return {
            'DAYTONA_API_KEY': api_key
        }
        
    def _configure_redis(self, existing_config: Dict[str, Any]) -> Dict[str, str]:
        """Configure Redis settings"""
        self.ui.print_subheader("Redis Configuration")
        
        use_redis = Confirm.ask("Configure Redis?", default=bool(existing_config.get('REDIS_URL')))
        if not use_redis:
            self.ui.print_info("Skipping Redis configuration")
            return {}
            
        # Get existing values or defaults
        default_host = existing_config.get('REDIS_HOST', 'localhost')
        default_port = existing_config.get('REDIS_PORT', '6379')
        default_db = existing_config.get('REDIS_DB', '0')
        default_password = existing_config.get('REDIS_PASSWORD', '')
        
        # Prompt for settings
        host = Prompt.ask("[cyan]Redis Host[/cyan]", default=default_host)
        port = Prompt.ask("[cyan]Redis Port[/cyan]", default=default_port)
        db = Prompt.ask("[cyan]Redis Database[/cyan]", default=default_db)
        password = Prompt.ask("[cyan]Redis Password[/cyan] (optional)", password=True, default=default_password)
        
        # Build Redis URL
        if password:
            redis_url = f"redis://:{password}@{host}:{port}/{db}"
        else:
            redis_url = f"redis://{host}:{port}/{db}"
            
        return {
            'REDIS_URL': redis_url,
            'REDIS_HOST': host,
            'REDIS_PORT': port,
            'REDIS_DB': db,
            'REDIS_PASSWORD': password
        }
        
    def _configure_postgresql(self, existing_config: Dict[str, Any]) -> Dict[str, str]:
        """Configure PostgreSQL settings"""
        self.ui.print_subheader("PostgreSQL Configuration")
        
        use_postgres = Confirm.ask("Configure PostgreSQL?", default=bool(existing_config.get('DATABASE_URL')))
        if not use_postgres:
            self.ui.print_info("Skipping PostgreSQL configuration")
            return {}
            
        # Get existing values or defaults
        default_host = existing_config.get('DB_HOST', 'localhost')
        default_port = existing_config.get('DB_PORT', '5432')
        default_name = existing_config.get('DB_NAME', 'msa_reasoning')
        default_user = existing_config.get('DB_USER', 'postgres')
        default_password = existing_config.get('DB_PASSWORD', '')
        
        # Prompt for settings
        host = Prompt.ask("[cyan]Database Host[/cyan]", default=default_host)
        port = Prompt.ask("[cyan]Database Port[/cyan]", default=default_port)
        name = Prompt.ask("[cyan]Database Name[/cyan]", default=default_name)
        user = Prompt.ask("[cyan]Database User[/cyan]", default=default_user)
        password = Prompt.ask("[cyan]Database Password[/cyan] (optional)", password=True, default=default_password)
        
        # Build database URL
        if password:
            db_url = f"postgresql://{user}:{password}@{host}:{port}/{name}"
        else:
            db_url = f"postgresql://{user}@{host}:{port}/{name}"
            
        return {
            'DATABASE_URL': db_url,
            'DB_HOST': host,
            'DB_PORT': port,
            'DB_NAME': name,
            'DB_USER': user,
            'DB_PASSWORD': password
        }
        
    async def run(self) -> bool:
        """Run the configuration wizard"""
        try:
            # Load existing configuration
            existing_config = self._load_existing_config()
            
            # Display welcome
            self._print_welcome()
            
            # Initialize new configuration
            config = {}
            
            # Configure services
            self.ui.print_header("Service Configuration", "bold magenta")
            
            # Azure OpenAI configuration
            azure_config = await self._configure_azure_openai(existing_config)
            config.update(azure_config)
            
            # Daytona configuration
            daytona_config = await self._configure_daytona(existing_config)
            config.update(daytona_config)
            
            # Redis configuration
            redis_config = self._configure_redis(existing_config)
            config.update(redis_config)
            
            # PostgreSQL configuration
            postgres_config = self._configure_postgresql(existing_config)
            config.update(postgres_config)
            
            # Save configuration
            if config:
                self._save_config(config)
                
                # Show summary
                self.ui.print_header("Configuration Summary", "bold green")
                self.ui.print_dict_as_table(config, "Saved Configuration")
                
                self.ui.print_success("Configuration wizard completed successfully!")
                return True
            else:
                self.ui.print_warning("No configuration changes were made")
                return False
                
        except KeyboardInterrupt:
            self.ui.print_warning("Configuration wizard cancelled by user")
            return False
        except Exception as e:
            self.ui.print_error(f"Configuration wizard failed: {e}")
            return False


@click.group()
def wizard():
    """Configuration wizard for MSA Reasoning Engine"""
    pass


@wizard.command()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def run(verbose: bool):
    """Run the interactive configuration wizard"""
    wizard = ConfigWizard(verbose=verbose)
    asyncio.run(wizard.run())


if __name__ == "__main__":
    wizard()