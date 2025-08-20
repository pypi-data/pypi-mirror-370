"""
Interactive configuration setup for Autocoder
Creates a minimal config.yaml through user prompts
"""

import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from utils.provider_validator import ProviderValidator
from utils.agent_prompts import AGENT_SYSTEM_PROMPTS

class InteractiveConfigSetup:
    """Interactive setup for creating configuration file"""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.config: Dict[str, Any] = {}
        self.validator = ProviderValidator()
        self.fetched_models = []  # Will be populated dynamically
        
        # Available providers (models will be fetched dynamically)
        self.providers = {
            'openai': {
                'name': 'OpenAI',
                'api_key_env': 'OPENAI_API_KEY',
                'requires_key': True
            },
            'anthropic': {
                'name': 'Anthropic (Claude)',
                'api_key_env': 'ANTHROPIC_API_KEY',
                'requires_key': True
            },
            'google': {
                'name': 'Google Gemini',
                'api_key_env': 'GOOGLE_API_KEY',
                'requires_key': True
            },
            'ollama': {
                'name': 'Ollama (Local)',
                'requires_key': False,
                'base_url': 'http://localhost:11434'
            },
            'openai_compatible': {
                'name': 'OpenAI Compatible API',
                'api_key_env': 'OPENAI_COMPATIBLE_API_KEY',
                'requires_key': True,
                'requires_base_url': True
            }
        }
        
        # Default agent roles
        self.agents = [
            'planner',
            'developer', 
            'tester',
            'ui_ux_expert',
            'db_expert',
            'devops_expert'
        ]
    
    def run(self, output_path: str = "config.yaml") -> bool:
        """
        Run the interactive setup process
        
        Args:
            output_path: Path to save the configuration file
            
        Returns:
            True if successful, False if cancelled
        """
        try:
            self.console.print(Panel.fit(
                "[bold cyan]🚀 Autocoder Configuration Setup[/bold cyan]\n\n"
                "This wizard will help you create a minimal configuration file.\n"
                "You can always edit the config.yaml file later for advanced settings.",
                padding=(1, 2)
            ))
            
            # Step 1: Choose provider
            if not self._select_provider():
                return False
            
            # Step 2: Configure API key if needed
            if not self._configure_api_key():
                return False
            
            # Step 3: Select default model
            if not self._select_model():
                return False
            
            # Step 4: Configure agents
            if not self._configure_agents():
                return False
            
            # Step 5: Additional settings
            if not self._configure_additional_settings():
                return False
            
            # Step 6: Review and save
            if self._review_and_confirm():
                return self._save_config(output_path)
            
            return False
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Setup cancelled by user[/yellow]")
            return False
        except Exception as e:
            self.console.print(f"[red]Error during setup: {e}[/red]")
            return False
    
    def _select_provider(self) -> bool:
        """Select the AI provider"""
        self.console.print("\n[bold]Step 1: Select AI Provider[/bold]")
        
        # Create provider table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Option", width=8)
        table.add_column("Provider", width=20)
        table.add_column("Description", width=40)
        
        table.add_row("1", "OpenAI", "GPT-4, GPT-3.5 (Requires API key)")
        table.add_row("2", "Anthropic", "Claude 3.5, Claude 3 (Requires API key)")
        table.add_row("3", "Google Gemini", "Gemini Pro, Flash (Requires API key)")
        table.add_row("4", "Ollama", "Local models (No API key required)")
        table.add_row("5", "OpenAI Compatible", "Custom API endpoint (Requires base URL + key)")
        
        self.console.print(table)
        
        choice = Prompt.ask(
            "\nSelect provider",
            choices=["1", "2", "3", "4", "5"],
            default="1"
        )
        
        provider_map = {
            "1": "openai",
            "2": "anthropic",
            "3": "google",
            "4": "ollama",
            "5": "openai_compatible"
        }
        
        self.selected_provider = provider_map[choice]
        provider_info = self.providers[self.selected_provider]
        
        self.console.print(f"[green]✓ Selected: {provider_info['name']}[/green]")
        
        return True
    
    def _configure_api_key(self) -> bool:
        """Configure API key for the selected provider with validation"""
        provider_info = self.providers[self.selected_provider]
        
        # Handle OpenAI Compatible provider
        if self.selected_provider == 'openai_compatible':
            self.console.print("\n[bold]Step 2: Configure OpenAI Compatible API[/bold]")
            
            # Get base URL
            base_url = Prompt.ask(
                "Enter the API base URL",
                default="http://localhost:8000/v1"
            )
            self.base_url = base_url
            
            # Get API key
            env_var = provider_info['api_key_env']
            self.console.print(f"\nYou need an API key for this endpoint.")
            self.console.print(f"You can either:")
            self.console.print(f"  1. Enter the API key directly (will be saved in config)")
            self.console.print(f"  2. Use environment variable {env_var}")
            
            use_env = Confirm.ask("\nUse environment variable?", default=False)
            
            if use_env:
                self.api_key = f"env:{env_var}"
                self.console.print(f"[green]✓ Will use environment variable: {env_var}[/green]")
                return True
            else:
                return self._get_and_validate_api_key()
        
        # Handle Ollama
        if not provider_info.get('requires_key', True):
            if 'base_url' in provider_info:
                self.console.print("\n[bold]Step 2: Configure Connection[/bold]")
                base_url = Prompt.ask(
                    f"Enter base URL for {provider_info['name']}",
                    default=provider_info['base_url']
                )
                self.base_url = base_url
                
                # Validate Ollama connection
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task("Checking Ollama connection...", total=None)
                    is_valid, models, error = self.validator.validate_and_fetch_models(
                        self.selected_provider, 
                        base_url=base_url
                    )
                    
                if is_valid:
                    self.fetched_models = models
                    self.console.print(f"[green]✓ Connected to Ollama ({len(models)} models available)[/green]")
                else:
                    self.console.print(f"[yellow]⚠ {error}[/yellow]")
                    if not Confirm.ask("Continue anyway?", default=True):
                        return False
            return True
        
        # Standard providers with API keys
        self.console.print("\n[bold]Step 2: Configure API Key[/bold]")
        
        env_var = provider_info['api_key_env']
        
        self.console.print(f"You need an API key for {provider_info['name']}.")
        self.console.print(f"You can either:")
        self.console.print(f"  1. Enter the API key directly (will be saved in config)")
        self.console.print(f"  2. Use environment variable {env_var}")
        
        use_env = Confirm.ask("\nUse environment variable?", default=False)
        
        if use_env:
            self.api_key = f"env:{env_var}"
            self.console.print(f"[green]✓ Will use environment variable: {env_var}[/green]")
            self.console.print(f"[dim]Make sure to set: export {env_var}=your_api_key[/dim]")
            return True
        else:
            return self._get_and_validate_api_key()
    
    def _get_and_validate_api_key(self, retry_count: int = 0) -> bool:
        """Get API key from user and validate it"""
        max_retries = 3
        
        api_key = Prompt.ask("Enter your API key", password=True)
        if not api_key:
            self.console.print("[red]API key is required[/red]")
            return False
        
        # Validate the API key
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Validating API key and fetching models...", total=None)
            
            base_url = getattr(self, 'base_url', None)
            is_valid, models, error = self.validator.validate_and_fetch_models(
                self.selected_provider,
                api_key=api_key,
                base_url=base_url
            )
        
        if is_valid:
            self.api_key = api_key
            self.fetched_models = models
            self.console.print(f"[green]✓ API key validated successfully![/green]")
            if models:
                self.console.print(f"[green]✓ Found {len(models)} available models[/green]")
            return True
        else:
            self.console.print(f"[red]✗ {error}[/red]")
            
            if retry_count < max_retries - 1:
                self.console.print(f"\n[yellow]Attempt {retry_count + 1} of {max_retries}[/yellow]")
                retry = Confirm.ask("Would you like to try again?", default=True)
                if retry:
                    return self._get_and_validate_api_key(retry_count + 1)
            else:
                self.console.print(f"\n[yellow]Maximum retry attempts reached[/yellow]")
                skip = Confirm.ask("Continue without validation?", default=False)
                if skip:
                    self.api_key = api_key
                    self.console.print("[yellow]⚠ Continuing with unvalidated API key[/yellow]")
                    return True
            
            return False
    
    def _select_model(self) -> bool:
        """Select the default model from dynamically fetched list"""
        self.console.print("\n[bold]Step 3: Select Default Model[/bold]")
        
        provider_info = self.providers[self.selected_provider]
        
        # Use fetched models if available, otherwise fetch now
        if hasattr(self, 'fetched_models') and self.fetched_models:
            models = self.fetched_models
        else:
            # Try to fetch models if not already done
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Fetching available models...", total=None)
                
                api_key = getattr(self, 'api_key', None)
                base_url = getattr(self, 'base_url', None)
                
                # Handle environment variable API keys
                if api_key and api_key.startswith('env:'):
                    # Can't validate env vars, use fallback models
                    models = self.validator.fallback_models.get(self.selected_provider, ['default'])
                else:
                    is_valid, models, error = self.validator.validate_and_fetch_models(
                        self.selected_provider,
                        api_key=api_key if api_key and not api_key.startswith('env:') else None,
                        base_url=base_url
                    )
                    
                    if not models:
                        models = self.validator.fallback_models.get(self.selected_provider, ['default'])
                        self.console.print(f"[yellow]Using default model list[/yellow]")
        
        if not models:
            self.console.print("[red]No models available[/red]")
            manual_model = Prompt.ask("Enter model name manually")
            if manual_model:
                self.selected_model = manual_model
                self.console.print(f"[green]✓ Using model: {self.selected_model}[/green]")
                return True
            return False
        
        self.console.print(f"Available models for {provider_info['name']}:")
        for i, model in enumerate(models[:20], 1):  # Limit to 20 models for display
            self.console.print(f"  {i}. {model}")
        
        if len(models) > 20:
            self.console.print(f"  [dim]... and {len(models) - 20} more[/dim]")
        
        choice = Prompt.ask(
            "\nSelect model",
            choices=[str(i) for i in range(1, min(len(models) + 1, 21))],
            default="1"
        )
        
        self.selected_model = models[int(choice) - 1]
        self.console.print(f"[green]✓ Selected model: {self.selected_model}[/green]")
        
        return True
    
    def _configure_agents(self) -> bool:
        """Configure agents with the selected model"""
        self.console.print("\n[bold]Step 4: Configure Agents[/bold]")
        
        use_same = Confirm.ask(
            f"Use {self.selected_model} for all agents?",
            default=True
        )
        
        if use_same:
            self.console.print("[green]✓ All agents will use the same model[/green]")
            self.use_same_model = True
        else:
            self.console.print("[yellow]You can configure different models per agent in the config file later[/yellow]")
            self.use_same_model = True  # For now, keep it simple
        
        return True
    
    def _configure_additional_settings(self) -> bool:
        """Configure additional settings"""
        self.console.print("\n[bold]Step 5: Additional Settings[/bold]")
        
        # Output directory
        self.output_dir = Prompt.ask(
            "Default output directory for generated files",
            default="output"
        )
        
        # Logging level
        self.log_level = Prompt.ask(
            "Default logging level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default="WARNING"
        )
        
        self.console.print("[green]✓ Settings configured[/green]")
        return True
    
    def _review_and_confirm(self) -> bool:
        """Review configuration and confirm"""
        self.console.print("\n[bold]Review Configuration[/bold]")
        
        provider_info = self.providers[self.selected_provider]
        
        review_panel = Panel.fit(
            f"[cyan]Provider:[/cyan] {provider_info['name']}\n"
            f"[cyan]Model:[/cyan] {self.selected_model}\n"
            f"[cyan]Output Directory:[/cyan] {self.output_dir}\n"
            f"[cyan]Logging Level:[/cyan] {self.log_level}\n"
            f"[cyan]API Key:[/cyan] {'Environment variable' if hasattr(self, 'api_key') and self.api_key.startswith('env:') else 'Configured'}",
            title="Configuration Summary",
            padding=(1, 2)
        )
        
        self.console.print(review_panel)
        
        return Confirm.ask("\nSave this configuration?", default=True)
    
    def _build_config(self) -> Dict[str, Any]:
        """Build the configuration dictionary"""
        config = {
            'version': '1.0',
            'default_model': {
                'provider': self.selected_provider,
                'model': self.selected_model
            },
            'providers': {},
            'agents': {},
            'output': {
                'directory': self.output_dir,
                'create_project_folder': True
            },
            'logging': {
                'level': self.log_level,
                'file': 'autocoder.log'
            }
        }
        
        # Configure provider
        provider_info = self.providers[self.selected_provider]
        provider_config = {
            'enabled': True
        }
        
        if provider_info.get('requires_key', True):
            if hasattr(self, 'api_key'):
                provider_config['api_key'] = self.api_key
        
        # Add base URL for providers that need it
        if hasattr(self, 'base_url'):
            provider_config['base_url'] = self.base_url
        elif self.selected_provider == 'ollama':
            provider_config['base_url'] = self.base_url if hasattr(self, 'base_url') else 'http://localhost:11434'
        
        config['providers'][self.selected_provider] = provider_config
        
        # Configure API keys section
        if hasattr(self, 'api_key'):
            config['api_keys'] = {
                f"{self.selected_provider}_api_key": self.api_key
            }
        
        # Configure agents with professional descriptions and prompts
        agent_descriptions = {
            'planner': 'Strategic planning and task breakdown - transforms high-level intents into concrete plans',
            'developer': 'Code implementation and development - writes clean, maintainable, efficient code',
            'tester': 'Testing and quality assurance - ensures reliability, correctness, and performance',
            'ui_ux_expert': 'User interface and experience design - creates intuitive, accessible interfaces',
            'db_expert': 'Database design and optimization - designs efficient, scalable data solutions',
            'devops_expert': 'Deployment and infrastructure - handles CI/CD, monitoring, and operations'
        }
        
        for agent in self.agents:
            # Get the professional system prompt from agent_prompts.py
            system_prompt = AGENT_SYSTEM_PROMPTS.get(agent, f"You are a {agent.replace('_', ' ')} agent.")
            
            config['agents'][agent] = {
                'description': agent_descriptions.get(agent, f"Specialized {agent.replace('_', ' ')} agent"),
                'model': {
                    'provider': self.selected_provider,
                    'model': self.selected_model,
                    'temperature': 0.7 if agent == 'planner' else 0.3 if agent == 'developer' else 0,
                    'max_tokens': 2000 if agent == 'planner' else 2048
                },
                'system_prompt': system_prompt,
                'tools_enabled': agent == 'developer',  # Enable tools for developer by default
                'available_tools': ['code_search', 'file_reader', 'web_search'] if agent == 'developer' else []
            }
        
        # Add workflow configuration
        config['workflow'] = {
            'parallel_execution': False,
            'max_iterations': 3,
            'enable_human_feedback': False
        }
        
        return config
    
    def _save_config(self, output_path: str) -> bool:
        """Save configuration to file"""
        try:
            config = self._build_config()
            
            # Create path if it doesn't exist
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            with open(output_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False, indent=2)
            
            self.console.print(f"\n[green]✅ Configuration saved to {output_path}[/green]")
            
            # Show next steps
            self.console.print("\n[bold]Next Steps:[/bold]")
            if hasattr(self, 'api_key') and self.api_key.startswith('env:'):
                env_var = self.api_key[4:]
                self.console.print(f"1. Set your API key: [cyan]export {env_var}=your_actual_api_key[/cyan]")
                self.console.print(f"2. Run a task: [cyan]autocoder run \"Create a simple web app\"[/cyan]")
            else:
                self.console.print(f"1. Run a task: [cyan]autocoder run \"Create a simple web app\"[/cyan]")
            
            self.console.print(f"3. Start web interface: [cyan]autocoder web[/cyan]")
            self.console.print(f"4. Edit config for advanced settings: [cyan]{output_path}[/cyan]")
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]Failed to save configuration: {e}[/red]")
            return False


if __name__ == "__main__":
    # Test the setup
    console = Console()
    setup = InteractiveConfigSetup(console)
    setup.run("test_config.yaml")
