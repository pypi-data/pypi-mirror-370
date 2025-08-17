#!/usr/bin/env python3
"""
IvyBloom CLI - Main entry point
"""

import sys
import click
try:
    from click_didyoumean import DYMGroup
except Exception:
    DYMGroup = click.Group
try:
    import click_completion
except Exception:
    click_completion = None
try:
    from click_repl import repl
except Exception:
    repl = None
from pathlib import Path
from rich.console import Console
from rich.text import Text
from rich.align import Align

try:
    from . import __version__
    from .utils.config import Config
    from .utils.welcome import show_welcome_screen
    from .utils.colors import get_console
    from .commands.auth import auth
    from .commands.jobs import jobs
    from .commands.projects import projects
    from .commands.tools import tools
    from .commands.run import run
    from .commands.account import account
    from .commands.config import config
    from .commands.workflows import workflows
    from .commands.batch import batch
    from .commands.data import data
except ImportError:
    # Direct execution - use absolute imports
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    from ivybloom_cli import __version__
    from utils.config import Config
    from utils.welcome import show_welcome_screen
    from commands.auth import auth
    from commands.jobs import jobs
    from commands.projects import projects
    from commands.tools import tools
    from commands.run import run
    from commands.account import account
    from commands.config import config
    from commands.workflows import workflows
    from commands.batch import batch
    from commands.data import data
    from utils.colors import get_console

console = get_console()

@click.group(invoke_without_command=True, cls=DYMGroup)
@click.option('--config-file', type=click.Path(), help='Path to configuration file')
@click.option('--api-url', help='API base URL (overrides config)')
@click.option('--debug', is_flag=True, help='Enable debug output')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output-format', default='table', type=click.Choice(['json', 'yaml', 'table', 'csv']), help='Output format')
@click.option('--timeout', default=30, type=int, help='Request timeout in seconds')
@click.option('--retries', default=3, type=int, help='Number of retry attempts')
@click.option('--quiet', '-q', is_flag=True, help='Suppress non-essential output')
@click.option('--no-progress', is_flag=True, help='Disable progress bars and spinners')
@click.option('--offline', is_flag=True, help='Enable offline mode (use cached data)')
@click.option('--profile', is_flag=True, help='Enable performance profiling')
@click.version_option(version=__version__, prog_name='ivybloom')
@click.pass_context
def cli(ctx, config_file, api_url, debug, verbose, output_format, timeout, retries, quiet, no_progress, offline, profile):
    """🌿 IvyBloom CLI - Computational Biology & Drug Discovery Platform
    
    Advanced molecular modeling, drug design, and bioinformatics at your fingertips.
    
    GETTING STARTED:
    
      1. Authenticate:     ivybloom auth login --browser
      2. Explore tools:    ivybloom tools list  
      3. Run analysis:     ivybloom run esmfold protein_sequence=MKLLVL
      4. Monitor jobs:     ivybloom jobs list --status running
    
    MAIN COMMAND GROUPS:
    
      🔐 auth       → Authentication and account management
      🧬 tools      → Discover computational biology tools  
      🚀 run        → Execute tools with your data
      📋 jobs       → Monitor and manage computational jobs
      📁 projects   → Organize jobs into projects
      👤 account    → View account info and usage
      ⚙️  config     → Manage CLI configuration
    
    QUICK EXAMPLES:
    
      # Protein structure prediction (5 min)
      ivybloom run esmfold sequence="MKWVTFISLLFLFSSAYSRGVFRRD"
      
      # Molecular docking (30 min)
      ivybloom run diffdock protein_file="protein.pdb" ligand_smiles="CCO"
      
      # Drug design (1 hour)
      ivybloom run reinvent target_smiles="CC(=O)OC1=CC=CC=C1C(=O)O"
      
      # ADMET analysis (10 min)
      ivybloom run admetlab3 smiles="CCO" properties="solubility,toxicity"
      
      # Synthesis planning (2.5 hours)
      ivybloom run aizynthfinder target_smiles="CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"
    
    HELP & DISCOVERY:
    
      📋 Tool Information:
      • List all tools:           ivybloom tools list
      • Tool overview:            ivybloom tools info <tool_name>
      • Detailed parameters:      ivybloom tools info <tool_name> --detailed
      • Full parameter schema:    ivybloom tools schema <tool_name>
      • Schema with constraints:  ivybloom tools schema <tool_name> --constraints
      • Quick parameter help:     ivybloom run <tool_name> --show-schema
      • Usage examples:           ivybloom tools schema <tool_name> --examples
      
      🔧 General Help:
      • Command help:             ivybloom <command> --help
      • Download results:         ivybloom jobs download <job_id>
    
    💡 TIP: Use 'ivybloom tools info <tool_name> --detailed' for comprehensive parameter info!
    
    For detailed documentation: https://docs.ivybiosciences.com/cli
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Initialize configuration
    config = Config(config_file)
    if api_url:
        config.set('api_url', api_url)
    if debug:
        config.set('debug', True)
    if verbose:
        config.set('verbose', True)
    if output_format:
        config.set('output_format', output_format)
    if timeout:
        config.set('timeout', timeout)
    if retries:
        config.set('retries', retries)
    if quiet:
        config.set('quiet', True)
    if no_progress:
        config.set('no_progress', True)
    if offline:
        config.set('offline', True)
    if profile:
        config.set('profile', True)
    
    ctx.obj['config'] = config
    ctx.obj['debug'] = debug
    ctx.obj['verbose'] = verbose
    ctx.obj['output_format'] = output_format
    ctx.obj['quiet'] = quiet
    ctx.obj['no_progress'] = no_progress
    ctx.obj['offline'] = offline
    ctx.obj['profile'] = profile

    # Show welcome screen if no subcommand was invoked
    if ctx.invoked_subcommand is None:
        show_welcome_screen(__version__)
        click.echo(ctx.get_help())
        return

    # Initialize shell completion (if available) once CLI is invoked
    if click_completion is not None:
        try:
            click_completion.init()
        except Exception:
            pass

@cli.command()
@click.pass_context
def version(ctx):
    """Show version information with welcome screen"""
    show_welcome_screen(__version__)

@cli.command()
def shell():
    """Start an interactive CLI shell (if available)."""
    if repl is None:
        click.echo("Interactive shell not available (click-repl not installed)")
        return
    repl(cli)

# Add command groups
cli.add_command(auth)
cli.add_command(jobs)
cli.add_command(projects) 
cli.add_command(tools)
cli.add_command(account)
cli.add_command(config)
cli.add_command(workflows)
cli.add_command(batch)
cli.add_command(data)

# Add the run command as a top-level command
cli.add_command(run)

def main():
    """Main CLI entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

if __name__ == '__main__':
    main()