# from rich.console import Console
# from rich.panel import Panel
# from rich.table import Table
# from rich.layout import Layout
# from rich.live import Live
# from rich.prompt import Prompt
# from rich.text import Text
# from rich import box
# from rich.align import Align
# from rich.style import Style
# from rich.columns import Columns
# from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
# from rich.rule import Rule
# from rich.markdown import Markdown
# from rich.padding import Padding
# from rich.console import Group
# from datetime import datetime
# import os
# from pathlib import Path
# from .core import DevOpsAITools

# class TextDashboard:
#     """An enhanced text-based dashboard for SynteraAI DevOps."""
    
#     def __init__(self):
#         self.console = Console()
#         self.devops_tools = DevOpsAITools()
#         self.layout = Layout()
        
#         # Create a more structured layout
#         self.layout.split_column(
#             Layout(name="header", size=3),
#             Layout(name="body", ratio=8),
#             Layout(name="footer", size=3)
#         )
        
#         # Split the body into tools panel and content area with better proportions
#         self.layout["body"].split_row(
#             Layout(name="tools", ratio=1),
#             Layout(name="content", ratio=3)
#         )
        
#         # Track the active tool for highlighting
#         self.active_tool = None
#         self.github_repo_url = None  # To store the GitHub repository URL

#     def _create_header(self) -> Panel:
#         """Create an enhanced header panel with more information."""
#         current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
#         header_group = Group(
#             Rule("SynteraAI DevOps", style="bright_cyan"),
#             Text.from_markup("[bold cyan]🤖 SynteraAI DevOps Dashboard[/bold cyan]"),
#             Text.from_markup(f"[dim]Your AI-powered DevOps assistant | {current_time}[/dim]")
#         )
        
#         return Panel(
#             header_group,
#             border_style="bright_blue", 
#             box=box.HEAVY_EDGE,
#             title="[bold white on blue] DevOps AI [/bold white on blue]",
#             title_align="center"
#         )

#     def _create_tools_panel(self) -> Panel:
#         """Create an enhanced tools panel with better visual indicators."""
#         tools_group = Group()
        
#         # Add a title with better styling
#         tools_group.renderables.append(Text("Available Tools", style="bold magenta underline"))
#         tools_group.renderables.append(Text(""))
        
#         # Define tool options with better visual indicators and descriptions
#         tools = [
#             # {"key": "1", "icon": "📊", "name": "Analyze Logs", "desc": "Analyze log files for patterns and errors"},
#             {"key": "1", "icon": "🐳", "name": "Docker Generation", "desc": "Generate Docker and docker-compose files"},
#             {"key": "2", "icon": "🏗️", "name": "Infrastructure", "desc": "Get infrastructure recommendations"},
#             # {"key": "3", "icon": "🔒", "name": "Security Scan", "desc": "Perform security vulnerability scanning"},
#             # {"key": "4", "icon": "⚡", "name": "Optimize", "desc": "Get performance optimization suggestions"},
#             # {"key": "5", "icon": "⚙️", "name": "Git Ingest", "desc": "Ingest and process a GitHub repository"},
#             # {"key": "6", "icon": "🧑‍💻", "name": "Code Quality", "desc": "Analyze code quality and maintainability"},
#             # {"key": "7", "icon": "📦", "name": "Dependency Check", "desc": "Check for outdated or vulnerable dependencies"},
#             # {"key": "8", "icon": "👥", "name": "Contributors", "desc": "Show contributor statistics and activity"},
            
#             # {"key": "10", "icon": "🔍", "name": "Repo Analyze", "desc": "Analyze the GitHub repository for insights"},
#             {"key": "3","icon": "📈","name": "Monitoring Audit","desc": "Analyze Prometheus and Grafana configurations for observability, alerting, and visualization insights"}
             
#         ]
        
#         # Add each tool with proper styling and highlighting for active tool
#         for tool in tools:
#             tool_text = Text()
            
#             # Highlight active tool
#             if self.active_tool == tool["key"]:
#                 prefix = "► "
#                 style = "bold white on blue"
#                 box_style = "on blue"
#             else:
#                 prefix = "  "
#                 style = "cyan"
#                 box_style = ""
            
#             # Format tool entry
#             tool_text.append(f"{prefix}{tool['key']}. {tool['icon']} ", style=style)
#             tool_text.append(f"{tool['name']}\n", style=style)
#             tool_text.append(f"   {tool['desc']}\n", style="dim")
            
#             tools_group.renderables.append(tool_text)
        
#         # Add navigation help
#         tools_group.renderables.append(Text(""))
#         help_text = Text()
#         help_text.append("Navigation:\n", style="bold yellow")
#         help_text.append("• Enter 1-5 to select tool\n", style="dim")
#         help_text.append("• Press 'q' to quit", style="dim")
#         tools_group.renderables.append(help_text)
        
#         return Panel(
#             Padding(tools_group, (1, 2)),
#             title="[bold white on blue] Tools [/bold white on blue]",
#             border_style="bright_blue",
#             box=box.HEAVY,
#             title_align="center"
#         )

#     def _create_content_panel(self, content: str = "") -> Panel:
#         """Create an enhanced content panel with better formatting."""
#         if not content:
#             welcome_md = """
#             # Welcome to SynteraAI DevOps Dashboard
            
#             This dashboard provides AI-powered tools to help with your DevOps tasks.
            
#             ## Getting Started
#             1. Select a tool from the left panel
#             2. Provide the required input
#             3. View the AI-generated results here
            
#             ## Available Tools
#             - **Analyze Logs**: Find patterns and issues in your log files
#             - **Infrastructure**: Get recommendations for your infrastructure
#             - **Security Scan**: Identify security vulnerabilities
#             - **Optimize**: Discover performance optimization opportunities
#             """
#             content = Markdown(welcome_md)
        
#         return Panel(
#             Padding(content, (1, 2)),
#             title="[bold white on blue] Results [/bold white on blue]",
#             border_style="bright_blue",
#             box=box.HEAVY,
#             title_align="center"
#         )

#     def _create_footer(self) -> Panel:
#         """Create an enhanced footer panel with more information."""
#         footer_group = Group(
#             Text.from_markup("[bold green]Input Instructions:[/bold green]"),
#             Text.from_markup("[white]1. Type the number (1-4) to select a tool[/white]"),
#             Text.from_markup("[white]2. Press Enter to confirm your selection[/white]"),
#             Text.from_markup("[white]3. Type 'q' to quit the application[/white]")
#         )
        
#         return Panel(
#             Align.center(footer_group),
#             border_style="bright_green",
#             box=box.HEAVY_EDGE,
#             title="[bold white on green] Help [/bold white on green]",
#             title_align="center"
#         )

#     def _display_result(self, result: str, title: str) -> None:
#         """Display the result in a more structured and visually appealing way."""
#         # Create a more structured table with multiple columns
#         table = Table(
#             title=title,
#             show_header=True,
#             header_style="bold magenta",
#             border_style="bright_blue",
#             title_style="bold cyan",
#             box=box.HEAVY,
#             expand=True
#         )
        
#         # Add columns for better organization
#         table.add_column("#", style="dim", width=3)
#         table.add_column("Finding", style="white", ratio=1)
        
#         # Process the result into sections
#         sections = result.split("\n\n")
#         for i, section in enumerate(sections, 1):
#             if section.strip():
#                 table.add_row(str(i), section)
        
#         # Create a group with a header and the table
#         result_group = Group(
#             Rule(title, style="bright_cyan"),
#             table
#         )
        
#         # Update the content panel
#         self.layout["content"].update(self._create_content_panel(result_group))

#     def _create_input_panel(self, prompt_text="Select a tool (1-5) or 'q' to quit") -> Panel:
#         """Create a dedicated input panel for better visibility."""
#         input_text = Text()
#         input_text.append("\n")
#         input_text.append("► ", style="bold green")
#         input_text.append(prompt_text, style="bold cyan")
#         input_text.append("\n")
        
#         return Panel(
#             input_text,
#             title="[bold white on green] Input [/bold white on green]",
#             border_style="bright_green",
#             box=box.HEAVY,
#             title_align="center",
#             padding=(1, 2)
#         )
        
#     def run(self):
#         """Run the enhanced dashboard with better user experience."""
#         self.console.clear()

#         # Prompt for GitHub repository URL at the start
#         self.console.print("\n")
#         self.github_repo_url = Prompt.ask(
#             "[bold green]►[/bold green] [bold cyan]Enter the GitHub repository URL to work on[/bold cyan]",
#             default="https://github.com/example/repo" # Provide a default or leave empty
#         )
#         # Clone the repo if not already present
#         repo_name = self.github_repo_url.rstrip('/').split('/')[-1]
#         local_repo_path = os.path.join(os.getcwd(), repo_name)
#         if not os.path.exists(local_repo_path):
#             self.console.print(f"[bold cyan]Cloning repository to:[/] [italic blue]{local_repo_path}[/italic blue]\n")
#             import subprocess
#             try:
#                 result = subprocess.run([
#                     "git", "clone", self.github_repo_url, local_repo_path
#                 ], capture_output=True, text=True, check=True)
#                 clone_output = result.stdout + "\n" + result.stderr
#                 self._display_result(clone_output, "Git Clone Output")
#             except subprocess.CalledProcessError as e:
#                 error_output = e.stdout + "\n" + e.stderr
#                 self._display_result(error_output, "Git Clone Error")
#         else:
#             self.console.print(f"[bold green]Repository already cloned at:[/] [italic blue]{local_repo_path}[/italic blue]\n")
#         self.local_repo_path = local_repo_path
#         self.console.print(f"[bold cyan]Working with repository:[/] [italic blue]{self.github_repo_url}[/italic blue]\n")
        
#         # Create a more structured layout with dedicated input area
#         self.layout.split_column(
#             Layout(name="header", size=3),
#             Layout(name="body", ratio=8),
#             Layout(name="input", size=3),
#             Layout(name="footer", size=2)
#         )
        
#         # Split the body into tools panel and content area with better proportions
#         self.layout["body"].split_row(
#             Layout(name="tools", ratio=1),
#             Layout(name="content", ratio=3)
#         )
        
#         # Initial layout setup
#         self.layout["header"].update(self._create_header())
#         self.layout["tools"].update(self._create_tools_panel())
#         self.layout["content"].update(self._create_content_panel())
#         self.layout["input"].update(self._create_input_panel())
#         self.layout["footer"].update(self._create_footer())
        
#         # Display the initial layout
#         with Live(self.layout, refresh_per_second=4, auto_refresh=False) as live:
#             live.refresh()
            
#             while True:
#                 # Exit the Live context to get user input
#                 live.stop()
                
#                 # Get user input with better visibility
#                 self.console.print("\n")
#                 choice = Prompt.ask(
#                     "[bold green]►[/bold green] [bold cyan]Select a tool[/bold cyan]",
#                     # "4", "5", "6", "7", "8", "9", "10","11"
#                     choices=["1", "2", "3","q"],
#                     default="q"
#                 )
                
#                 # Resume the Live display
#                 live.start()
                
#                 if choice == "q":
#                     break
                
#                 # Update active tool for highlighting
#                 self.active_tool = choice
#                 self.layout["tools"].update(self._create_tools_panel())
#                 live.refresh()
                
#                 # Process based on choice with enhanced status indicators
#                 # if choice == "1":
#                 #     # Update input panel with specific prompt
#                 #     self.layout["input"].update(self._create_input_panel("Enter log file path"))
#                 #     live.refresh()
                    
#                 #     # Exit Live context to get input
#                 #     live.stop()
#                 #     self.console.print("\n")
#                 #     log_file = Prompt.ask("[bold green]►[/bold green] [bold cyan]Enter log file path[/bold cyan]")
#                 #     live.start()
                    
#                 #     # Show progress
#                 #     with Progress(
#                 #         SpinnerColumn(),
#                 #         TextColumn("[bold cyan]Analyzing logs...[/bold cyan]"),
#                 #         BarColumn(bar_width=40),
#                 #         TextColumn("[bold cyan]Please wait[/bold cyan]"),
#                 #     ) as progress:
#                 #         task = progress.add_task("Analyzing", total=100)
#                 #         progress.update(task, advance=50)
#                 #         result = self.devops_tools._analyze_logs(log_file)
#                 #         progress.update(task, advance=50)
                    
#                 #     self._display_result(result, "📊 Log Analysis Results")
                
#                 if choice == "2":
#                     # Check if GitHub repo URL is available
#                     if self.github_repo_url:
#                         self.layout["input"].update(self._create_input_panel(f"Generating infrastructure suggestions for {self.github_repo_url}"))
#                         live.refresh()

#                         live.stop()
#                         with Progress(
#                             SpinnerColumn(),
#                             TextColumn("[bold cyan]Analyzing repository and generating infrastructure suggestions...[/bold cyan]"),
#                             BarColumn(bar_width=40),
#                             TextColumn("[bold cyan]Please wait[/bold cyan]"),
#                         ) as progress:
#                             task = progress.add_task("Infrastructure Analysis", total=100)
#                             progress.update(task, advance=50)

#                             # Use local repo path for deeper analysis
#                             result = self.devops_tools._infra_suggest(
#                                 context="",
#                                 repo_path=self.local_repo_path
#                             )
#                             progress.update(task, advance=50)
#                     else:
#                         # No GitHub repo set, ask for manual context input
#                         self.layout["input"].update(self._create_input_panel("Enter infrastructure context"))
#                         live.refresh()

#                         live.stop()
#                         self.console.print("\n")
#                         context = Prompt.ask("[bold green]►[/bold green] [bold cyan]Enter infrastructure context[/bold cyan]")
#                         live.start()

#                         with Progress(
#                             SpinnerColumn(),
#                             TextColumn("[bold cyan]Generating infrastructure suggestions...[/bold cyan]"),
#                             BarColumn(bar_width=40),
#                         ) as progress:
#                             task = progress.add_task("Generating", total=100)
#                             progress.update(task, advance=50)
#                             result = self.devops_tools._infra_suggest(context=context)
#                             progress.update(task, advance=50)

#                     self._display_result(result, "🏗️ Infrastructure Recommendations")
#                 # elif choice == "3":
#                 #     # Update input panel with specific prompt
#                 #     self.layout["input"].update(self._create_input_panel("Enter target to scan"))
#                 #     live.refresh()
                    
#                 #     # Exit Live context to get input
#                 #     live.stop()
#                 #     self.console.print("\n")
#                 #     target = Prompt.ask("[bold green]►[/bold green] [bold cyan]Enter target to scan[/bold cyan]")
#                 #     live.start()
                    
#                 #     with Progress(
#                 #         SpinnerColumn(),
#                 #         TextColumn("[bold cyan]Scanning for security issues...[/bold cyan]"),
#                 #         BarColumn(bar_width=40),
#                 #     ) as progress:
#                 #         task = progress.add_task("Scanning", total=100)
#                 #         progress.update(task, advance=50)
#                 #         result = self.devops_tools._security_scan(target)
#                 #         progress.update(task, advance=50)
                    
#                 #     self._display_result(result, "🔒 Security Scan Results")
                
#                 # elif choice == "4":
#                 #     # Update input panel with specific prompt
#                 #     self.layout["input"].update(self._create_input_panel("Enter optimization context"))
#                 #     live.refresh()
                    
#                 #     # Exit Live context to get input
#                 #     live.stop()
#                 #     self.console.print("\n")
#                 #     context = Prompt.ask("[bold green]►[/bold green] [bold cyan]Enter optimization context[/bold cyan]")
#                 #     live.start()
                    
#                 #     with Progress(
#                 #         SpinnerColumn(),
#                 #         TextColumn("[bold cyan]Generating optimization recommendations...[/bold cyan]"),
#                 #         BarColumn(bar_width=40),
#                 #     ) as progress:
#                 #         task = progress.add_task("Optimizing", total=100)
#                 #         progress.update(task, advance=50)
#                 #         result = self.devops_tools._optimize(context)
#                 #         progress.update(task, advance=50)
                    
#                 #     self._display_result(result, "⚡ Optimization Recommendations")

#                 # elif choice == "5":
#                 #     if not self.github_repo_url:
#                 #         self.console.print("[bold red]GitHub repository URL not set. Please restart or set it.[/bold red]")
#                 #         live.refresh()
#                 #         continue

#                 #     self.layout["input"].update(self._create_input_panel(f"Processing Git Ingest for {self.github_repo_url}"))
#                 #     live.refresh()
                    
#                 #     with Progress(
#                 #         SpinnerColumn(),
#                 #         TextColumn("[bold cyan]Ingesting repository...[/bold cyan]"),
#                 #         BarColumn(bar_width=40),
#                 #         TextColumn("[bold cyan]Please wait[/bold cyan]"),
#                 #     ) as progress:
#                 #         task = progress.add_task("Ingesting", total=100)
#                 #         progress.update(task, advance=50)
#                 #         try:
#                 #             result = self.devops_tools._git_ingest(self.github_repo_url) 
#                 #         except AttributeError:
#                 #             result = f"Git ingest functionality for '{self.github_repo_url}' is under development."
#                 #         progress.update(task, advance=50)
                    
#                 #     self._display_result(result, "⚙️ Git Ingest Results")
                    
#                 #     # Reset active tool after operation
#                 #     self.active_tool = None
#                 #     self.layout["tools"].update(self._create_tools_panel())
#                 #     self.layout["input"].update(self._create_input_panel())
#                 #     live.refresh()

#                 # elif choice == "6":
#                 #     if not self.github_repo_url:
#                 #         self.console.print("[bold red]GitHub repository URL not set. Please restart or set it.[/bold red]")
#                 #         live.refresh()
#                 #         continue

#                 #     self.layout["input"].update(self._create_input_panel(f"Analyzing code quality for {self.github_repo_url}"))
#                 #     live.refresh()
                    
#                 #     with Progress(
#                 #         SpinnerColumn(),
#                 #         TextColumn("[bold cyan]Analyzing code quality...[/bold cyan]"),
#                 #         BarColumn(bar_width=40),
#                 #         TextColumn("[bold cyan]Please wait[/bold cyan]"),
#                 #     ) as progress:
#                 #         task = progress.add_task("CodeQuality", total=100)
#                 #         progress.update(task, advance=50)
#                 #         result = self.devops_tools._code_quality(self.github_repo_url)
#                 #         progress.update(task, advance=50)
                    
#                 #     self._display_result(result, "🧑‍💻 Code Quality Analysis")

#                 # elif choice == "7":
#                 #     if not self.github_repo_url:
#                 #         self.console.print("[bold red]GitHub repository URL not set. Please restart or set it.[/bold red]")
#                 #         live.refresh()
#                 #         continue

#                 #     self.layout["input"].update(self._create_input_panel(f"Checking dependencies for {self.github_repo_url}"))
#                 #     live.refresh()
                    
#                 #     with Progress(
#                 #         SpinnerColumn(),
#                 #         TextColumn("[bold cyan]Checking dependencies...[/bold cyan]"),
#                 #         BarColumn(bar_width=40),
#                 #         TextColumn("[bold cyan]Please wait[/bold cyan]"),
#                 #     ) as progress:
#                 #         task = progress.add_task("DependencyCheck", total=100)
#                 #         progress.update(task, advance=50)
#                 #         result = self.devops_tools._dependency_check(self.github_repo_url)
#                 #         progress.update(task, advance=50)
                    
#                 #     self._display_result(result, "📦 Dependency Check Results")

#                 # elif choice == "8":
#                 #     if not self.github_repo_url:
#                 #         self.console.print("[bold red]GitHub repository URL not set. Please restart or set it.[/bold red]")
#                 #         live.refresh()
#                 #         continue

#                 #     self.layout["input"].update(self._create_input_panel(f"Fetching contributors for {self.github_repo_url}"))
#                 #     live.refresh()
                    
#                 #     with Progress(
#                 #         SpinnerColumn(),
#                 #         TextColumn("[bold cyan]Fetching contributor statistics...[/bold cyan]"),
#                 #         BarColumn(bar_width=40),
#                 #         TextColumn("[bold cyan]Please wait[/bold cyan]"),
#                 #     ) as progress:
#                 #         task = progress.add_task("Contributors", total=100)
#                 #         progress.update(task, advance=50)
#                 #         result = self.devops_tools._contributors(self.github_repo_url)
#                 #         progress.update(task, advance=50)
                    
#                 #     self._display_result(result, "👥 Contributor Statistics")
                
#                 elif choice == "1":
                    
#                     if not self.github_repo_url:
#                         self.console.print("[bold red]GitHub repository URL not set. Please restart or set it.[/bold red]")
#                         live.refresh()
#                         continue

#                     self.layout["input"].update(self._create_input_panel(f"Generating Docker files for {self.github_repo_url}"))
#                     live.refresh()

#                     self.layout["input"].update(self._create_input_panel("Checking for .env file"))
#                     live.refresh()

#                     # ⚠️ Stop Live before any input prompt
#                     if live.is_started:
#                         live.stop()

                   
#                     # ✅ Resume Live rendering
#                     if not live.is_started:
#                         live.start()

#                     # Stop again before progress
#                     live.stop()
#                     with Progress(
#                         SpinnerColumn(),
#                         TextColumn("[bold cyan]Analyzing repository and generating Docker files...[/bold cyan]"),
#                         BarColumn(bar_width=40),
#                         TextColumn("[bold cyan]Please wait[/bold cyan]"),
#                     ) as progress:
#                         task = progress.add_task("DockerGeneration", total=100)
#                         progress.update(task, advance=50)
#                         result = self.devops_tools._docker_generation(self.local_repo_path)
#                         progress.update(task, advance=50)

#                     # Restart Live and show result
#                     live.start()
#                     self._display_result(result, "🐳 Docker Generation Results")



#                 # Reset input panel after any operation
#                 self.layout["input"].update(self._create_input_panel())
#                 live.refresh()

# def main():
#     """Main entry point for the dashboard."""
#     dashboard = TextDashboard()
#     dashboard.run()

# if __name__ == "__main__":
#     main()