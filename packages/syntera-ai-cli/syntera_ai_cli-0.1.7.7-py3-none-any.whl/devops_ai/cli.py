# import os
# from typing import Optional
# from pathlib import Path

# import typer
# from rich.console import Console
# from rich.panel import Panel
# from rich.table import Table
# from rich.progress import Progress, SpinnerColumn, TextColumn,BarColumn
# from rich.syntax import Syntax
# from dotenv import load_dotenv
# from .core import DevOpsAITools
# from .dashboard import TextDashboard

# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Initialize Typer app
# app = typer.Typer(help="SynteraAI - AI-powered DevOps CLI tool")
# console = Console()

# # Load environment variables
# load_dotenv()

# # Initialize tools
# devops_tools = DevOpsAITools()

# def _display_result(result: str, title: str):
#     """Display results in a formatted table"""
#     table = Table(
#         title=title,
#         show_header=True,
#         header_style="bold magenta",
#         border_style="blue",
#         title_style="bold cyan"
#     )
#     table.add_column("Content", style="dim")
    
#     # Split the result into sections and format them
#     sections = result.split("\n\n")
#     for section in sections:
#         if section.strip():
#             # Try to detect code blocks and apply syntax highlighting
#             if "```" in section:
#                 code_blocks = section.split("```")
#                 for i, block in enumerate(code_blocks):
#                     if i % 2 == 1:  # Code block
#                         try:
#                             highlighted = Syntax(block, "python", theme="monokai")
#                             table.add_row(highlighted)
#                         except Exception as e:
#                             logger.error(f"Error highlighting code block: {e}")
#                             table.add_row(block)
#                     else:  # Regular text
#                         table.add_row(block)
#             else:
#                 table.add_row(section)
    
#     console.print(table)

# @app.command()
# def dashboard():
#     """Launch the SynteraAI DevOps Dashboard."""
#     TextDashboard().run()


# @app.command()
# def infra_suggest(
#     context: Optional[str] = typer.Argument(
#         None,
#         help="Optional natural language context for infrastructure suggestions"
#     ),
#     repo_path: Optional[str] = typer.Option(
#         None,
#         "--repo",
#         "-r",
#         help="Path to local Git repository for contextual analysis"
#     )
# ):
#     """
#     🏗️ Get AI-powered infrastructure suggestions.
    
#     Example:
#       infra-suggest "Python Flask app with Redis cache and PostgreSQL DB" --repo ./myapp
#     """
#     with Progress(
#         SpinnerColumn(),
#         TextColumn("[bold cyan]Generating infrastructure suggestions...[/bold cyan]"),
#         BarColumn(bar_width=40),
#         TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
#         expand=True
#     ) as progress:
#         task = progress.add_task("Processing", total=100)
#         progress.update(task, advance=20)

#         try:
#             if repo_path:
#                 logger.info(f"Using repository context from {repo_path}")
#                 result = devops_tools._infra_suggest(context=context, repo_path=repo_path)
#             else:
#                 logger.info("No repository provided, using only manual context")
#                 result = devops_tools._infra_suggest(context=context)
#         except Exception as e:
#             logger.error(f"Error generating infrastructure suggestion: {e}")
#             result = f"[ERROR] {str(e)}"

#         progress.update(task, completed=100)

#     _display_result(result, "🏗️ Infrastructure Recommendations")



# def main():
#     """Main entry point for the CLI"""
#     app()

# if __name__ == "__main__":
#     main() 
import os
from typing import Optional
from pathlib import Path
from rich.table import Table
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.syntax import Syntax
from dotenv import load_dotenv
from .core import DevOpsAITools
from .dashboard import TextDashboard

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Typer app
app = typer.Typer(help="SynteraAI - AI-powered DevOps CLI tool")
console = Console()

# Load environment variables
load_dotenv()

# Initialize tools
devops_tools = DevOpsAITools()

def _display_result(result: str, title: str):
    """Display results in a formatted table"""
    table = Table(
        title=title,
        show_header=True,
        header_style="bold magenta",
        border_style="blue",
        title_style="bold cyan"
    )
    table.add_column("Content", style="dim")
    
    # Split the result into sections and format them
    sections = result.split("\n\n")
    for section in sections:
        if section.strip():
            table.add_row(section)
    
    console.print(table)

@app.command()
def dashboard():
    """Launch the SynteraAI DevOps Dashboard."""
    TextDashboard().run()

# ... rest of your existing commands ...

@app.command()
def infra_suggest(
    context: Optional[str] = typer.Argument(
        None,
        help="Optional natural language context for infrastructure suggestions"
    ),
    repo_path: Optional[str] = typer.Option(
        None,
        "--repo",
        "-r",
        help="Path to local Git repository for contextual analysis"
    )
):
    """
    🏗️ Get AI-powered infrastructure suggestions.
    
    Example:
      infra-suggest "Python Flask app with Redis cache and PostgreSQL DB" --repo ./myapp
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]Generating infrastructure suggestions...[/bold cyan]"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        expand=True
    ) as progress:
        task = progress.add_task("Processing", total=100)
        progress.update(task, advance=20)

        try:
            if repo_path:
                logger.info(f"Using repository context from {repo_path}")
                result = devops_tools._infra_suggest(context=context, repo_path=repo_path)
            else:
                logger.info("No repository provided, using only manual context")
                result = devops_tools._infra_suggest(context=context)
        except Exception as e:
            logger.error(f"Error generating infrastructure suggestion: {e}")
            result = f"[ERROR] {str(e)}"

        progress.update(task, completed=100)

    _display_result(result, "🏗️ Infrastructure Recommendations")

def main():
    """Main entry point for the CLI"""
    app()

if __name__ == "__main__":
    main()