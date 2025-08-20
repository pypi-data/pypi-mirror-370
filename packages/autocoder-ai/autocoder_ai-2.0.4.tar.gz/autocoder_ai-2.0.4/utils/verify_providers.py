#!/usr/bin/env python3
"""
Script to verify installed LangChain model providers
"""

import sys
from typing import Dict, List, Tuple, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def check_provider(provider_name: str, import_path: str, test_func=None) -> Tuple[bool, str]:
    """Check if a provider is installed and optionally test it"""
    try:
        # Try to import the module
        module = __import__(import_path, fromlist=[''])
        
        # If a test function is provided, run it
        if test_func:
            result = test_func(module)
            if result:
                return True, "✅ Installed and verified"
            else:
                return True, "⚠️ Installed but test failed"
        
        return True, "✅ Installed"
    except ImportError as e:
        return False, f"❌ Not installed: {str(e).split('No module named')[1] if 'No module named' in str(e) else str(e)}"
    except Exception as e:
        return False, f"⚠️ Error: {str(e)}"

def check_langchain_providers() -> Dict[str, Tuple[bool, str]]:
    """Check all LangChain providers"""
    providers = {
        # Core providers
        "OpenAI": ("langchain_openai", None),
        "Anthropic": ("langchain_anthropic", None),
        "Google Generative AI": ("langchain_google_genai", None),
        
        # Additional providers (from requirements-providers.txt)
        "Azure AI": ("langchain_azure_ai", None),
        "AWS Bedrock": ("langchain_aws", None),
        "Cohere": ("langchain_cohere", None),
        "HuggingFace": ("langchain_huggingface", None),
        "Ollama": ("langchain_ollama", None),
        "Mistral AI": ("langchain_mistralai", None),
        "Together AI": ("langchain_together", None),
        "Groq": ("langchain_groq", None),
        "Google Vertex AI": ("langchain_google_vertexai", None),
        "NVIDIA AI": ("langchain_nvidia_ai_endpoints", None),
        "Fireworks AI": ("langchain_fireworks", None),
        "MongoDB": ("langchain_mongodb", None),
    }
    
    results = {}
    for provider_name, (import_path, test_func) in providers.items():
        results[provider_name] = check_provider(provider_name, import_path, test_func)
    
    return results

def check_base_libraries() -> Dict[str, Tuple[bool, str]]:
    """Check base AI/ML libraries"""
    libraries = {
        "OpenAI SDK": ("openai", None),
        "Anthropic SDK": ("anthropic", None),
        "Google AI SDK": ("google.generativeai", None),
        "Cohere SDK": ("cohere", None),
        "HuggingFace Hub": ("huggingface_hub", None),
        "Transformers": ("transformers", None),
        "Boto3 (AWS)": ("boto3", None),
        "Mistral SDK": ("mistralai", None),
        "Ollama": ("ollama", None),
        "Replicate": ("replicate", None),
        "LlamaCpp": ("llama_cpp", None),
    }
    
    results = {}
    for lib_name, (import_path, test_func) in libraries.items():
        results[lib_name] = check_provider(lib_name, import_path, test_func)
    
    return results

def check_tools_and_utilities() -> Dict[str, Tuple[bool, str]]:
    """Check additional tools and utilities"""
    tools = {
        "FastMCP": ("fastmcp", None),
        "Wikipedia": ("wikipedia", None),
        "DuckDuckGo Search": ("duckduckgo_search", None),
        "Arxiv": ("arxiv", None),
        "Tavily": ("tavily", None),
        "E2B": ("e2b", None),
    }
    
    results = {}
    for tool_name, (import_path, test_func) in tools.items():
        results[tool_name] = check_provider(tool_name, import_path, test_func)
    
    return results

def display_results(title: str, results: Dict[str, Tuple[bool, str]]):
    """Display results in a nice table"""
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Provider/Library", style="cyan", width=30)
    table.add_column("Status", width=50)
    
    installed_count = 0
    for name, (is_installed, status) in results.items():
        if is_installed:
            installed_count += 1
        table.add_row(name, status)
    
    console.print(table)
    console.print(f"\nSummary: {installed_count}/{len(results)} installed")
    return installed_count, len(results)

def main():
    """Main function"""
    console.print(Panel.fit(
        "[bold blue]🔍 LangChain Model Provider Verification[/bold blue]\n"
        "Checking installed providers and dependencies",
        border_style="blue"
    ))
    
    # Check LangChain providers
    console.print("\n[bold]Checking LangChain Providers...[/bold]")
    langchain_results = check_langchain_providers()
    lc_installed, lc_total = display_results("LangChain Providers", langchain_results)
    
    # Check base libraries
    console.print("\n[bold]Checking Base AI/ML Libraries...[/bold]")
    base_results = check_base_libraries()
    base_installed, base_total = display_results("Base Libraries", base_results)
    
    # Check tools and utilities
    console.print("\n[bold]Checking Tools & Utilities...[/bold]")
    tools_results = check_tools_and_utilities()
    tools_installed, tools_total = display_results("Tools & Utilities", tools_results)
    
    # Overall summary
    total_installed = lc_installed + base_installed + tools_installed
    total_checked = lc_total + base_total + tools_total
    
    console.print(Panel.fit(
        f"[bold green]✅ Verification Complete[/bold green]\n\n"
        f"Total: {total_installed}/{total_checked} components installed\n"
        f"LangChain Providers: {lc_installed}/{lc_total}\n"
        f"Base Libraries: {base_installed}/{base_total}\n"
        f"Tools & Utilities: {tools_installed}/{tools_total}",
        border_style="green"
    ))
    
    # Recommendations
    if total_installed < total_checked:
        console.print("\n[yellow]📝 Recommendations:[/yellow]")
        console.print("To install additional providers, run:")
        console.print("  [cyan]pip install -r requirements-providers.txt[/cyan]")
        console.print("\nFor specific providers:")
        
        missing_providers = []
        for name, (is_installed, _) in {**langchain_results, **base_results}.items():
            if not is_installed:
                missing_providers.append(name)
        
        if missing_providers:
            console.print(f"  Missing: {', '.join(missing_providers[:5])}")
            if len(missing_providers) > 5:
                console.print(f"  ... and {len(missing_providers) - 5} more")
    
    return 0 if total_installed == total_checked else 1

if __name__ == "__main__":
    sys.exit(main())
