# from rich.console import Console
# from rich.layout import Layout
# from rich.live import Live
# from rich.prompt import Prompt
# from datetime import datetime

# from typing import Dict, Callable, Tuple
# from .ui.panels import (
#     create_header,
#     create_tools_panel,
#     create_content_panel,
#     create_footer,
#     create_input_panel,
#     create_result_table
# )
# from .ui.tool_handlers import ToolHandlers

# import keyboard

# from .core import DevOpsAITools


# class TextDashboard:
#     """An enhanced text-based dashboard for SynteraAI DevOps with keyboard navigation."""

#     def __init__(self):
#         self.console = Console()
#         self.layout = Layout()
#         self.devops_tools = DevOpsAITools()
#         self.tool_handlers = ToolHandlers(self.devops_tools, self.console)

#         # Track active tool for highlighting
#         self.active_tool_index = 0
#         self.github_repo_url = None

#     def _display_result(self, result: str, title: str) -> None:
#         """Display the result in a structured and visually appealing way."""
#         result_group = create_result_table(result, title)
#         self.layout["content"].update(create_content_panel(result_group))

#     def run(self):
#         """Run the dashboard with keyboard navigation and scrolling."""
#         self.console.clear()

#         # Setup layout structure
#         self.layout.split_column(
#             Layout(name="header", size=3),
#             Layout(name="body", ratio=8),
#             Layout(name="input", size=3),
#             Layout(name="footer", size=2),
#         )

#         self.layout["body"].split_row(
#             Layout(name="tools", ratio=1),
#             Layout(name="content", ratio=3),
#         )

#         # Initial layout setup
#         self.layout["header"].update(create_header())
#         self.layout["tools"].update(self._render_tools_panel())
#         self.layout["content"].update(create_content_panel())
#         self.layout["input"].update(create_input_panel())
#         self.layout["footer"].update(create_footer())

#         # Prompt for GitHub repository URL at startup
#         self.console.print("\n")
#         self.github_repo_url = Prompt.ask(
#             "[bold green]►[/bold green] [bold cyan]Enter the GitHub repository URL to work on[/bold cyan]",
#             default="https://github.com/example/repo "
#         )
#         clone_output, self.local_repo_path = self.tool_handlers.set_repository(self.github_repo_url)
#         if clone_output:
#             self._display_result(clone_output, "Git Clone Output")

#         handlers = {
#             # "1": self.tool_handlers.analyze_logs,
#             "1": self.tool_handlers.docker_generation,
#             "2": self.tool_handlers.infrastructure,
#             # "3": self.tool_handlers.security_scan,
#             # "4": self.tool_handlers.optimize,
#             # "5": self.tool_handlers.git_ingest,
#             # "6": self.tool_handlers.code_quality,
#             # "7": self.tool_handlers.dependency_check,
#             # "8": self.tool_handlers.contributors,
            
#             # "10": self.tool_handlers.analyze_repo,
#             "3":self.tool_handlers.analyze_grafana_repo
#         }

#         # Start Live rendering
#         with Live(self.layout, refresh_per_second=10, screen=True) as live:
#             while True:
#                 key = self._get_keypress()

#                 if key == "q":
#                     break
#                 elif key == "KEY_UP" or key == "k":
#                     self.active_tool_index = max(0, self.active_tool_index - 1)
#                 elif key == "KEY_DOWN" or key == "j":
#                     self.active_tool_index = min(10, self.active_tool_index + 1)
                
#                 # Update only the tools panel with the current tool
#                 self.layout["tools"].update(self._render_tools_panel())
#                 live.refresh()  # Refresh is essential for real-time updates

#                 if key == "\r":  # Enter key pressed
#                     active_tool_key = str(self.active_tool_index + 1)
#                     self.layout["input"].update(create_input_panel(f"Running {active_tool_key}..."))
#                     live.refresh()

#                     handler = handlers.get(active_tool_key)
#                     if handler:
#                         live.stop()
#                         result, title = handler()
#                         live.start()
#                         self._display_result(result, title)

#                     self.layout["input"].update(create_input_panel())
#                     live.refresh()

#     def _render_tools_panel(self):
#         tools = [
#             {"key": "1", "icon": "🐳", "name": "Docker Generation", "desc": "Generate Docker and docker-compose files"},

#             {"key": "2", "icon": "🏗️", "name": "Infrastructure", "desc": "Get infrastructure recommendations"},
           
#             {"key": "3","icon": "📈","name": "Monitoring Audit","desc": "Analyze Prometheus and Grafana configurations for observability, alerting, and visualization insights"}

#         ]

#         # Get the current tool
#         current_tool = tools[self.active_tool_index]

#         return create_tools_panel(current_tool)

#     def _get_keypress(self):
#         event = keyboard.read_event()
#         if event.event_type == keyboard.KEY_DOWN:
#             key = event.name
#             if key == 'up':
#                 return "KEY_UP"
#             elif key == 'down':
#                 return "KEY_DOWN"
#             elif key == 'enter':
#                 return "\r"
#             elif key == 'q':
#                 return "q"
#             elif key.isdigit() and 1 <= int(key) <= 3:
#             # elif key.isdigit() and 1 <= int(key) <= 11:
#                 return key
#         return None


# def main():
#     """Main entry point for the dashboard."""
#     dashboard = TextDashboard()
#     dashboard.run()


# if __name__ == "__main__":
#     main()
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import ROUNDED, HEAVY
import pyfiglet
import inquirer
from typing import Callable, List, Optional, Tuple

from .ui.tool_handlers import ToolHandlers
from .core import DevOpsAITools


class TextDashboard:
    def __init__(self):
        self.console = Console()
        self.devops_tools = DevOpsAITools()
        self.tool_handlers = ToolHandlers(self.devops_tools, self.console)
        self.github_repo_url: Optional[str] = None
        self.local_repo_path: Optional[str] = None

        self.tools: List[Tuple[str, str, Optional[Callable[[], Tuple[str, str]]]]] = [
            ("🐳 Docker Generation ", "Generate Docker and docker-compose files", self.tool_handlers.docker_generation),
            ("🏗️ Infrastructure", "Get infrastructure recommendations", self.tool_handlers.infrastructure),
            ("📈 Monitoring Audit ", "Analyze Prometheus/Grafana configurations", self.tool_handlers.analyze_grafana_repo),
            ("❌ Exit", "Exit the dashboard ", None),
        ]

    def _display_ascii_logo(self):
        ascii_banner = pyfiglet.figlet_format("Syntera AI DevOps", font="slant")
        self.console.print(f"[bold cyan]{ascii_banner}[/bold cyan]")

    def _display_welcome_panel(self):
        panel = Panel.fit(
            "[bold white on blue] Welcome to SynteraAI DevOps Dashboard [/bold white on blue]",
            box=HEAVY,
            padding=(1, 4),
            style="cyan"
        )
        self.console.print(panel)

    def _display_tools_table(self):
        table = Table(
            title="🛠️ Available Tools",
            title_style="bold green",
            header_style="bold cyan",
            box=ROUNDED,
            border_style="blue"
        )
        table.add_column("Option", style="bold")
        table.add_column("Tool", style="white")
        table.add_column("Description", style="dim")

        for i, (name, desc, _) in enumerate(self.tools, start=1):
            table.add_row(str(i), name, desc)

        self.console.print(table)

    def _display_result(self, result: str, title: str) -> None:
        table = Table(
            title=title,
            show_header=True,
            header_style="bold magenta",
            border_style="blue",
            title_style="bold white",
            box=ROUNDED
        )
        table.add_column("Content", style="dim", overflow="fold")

        for section in result.strip().split("\n\n"):
            if section.strip():
                table.add_row(section.strip())

        self.console.print(table)

    def _prompt_repo_url(self) -> None:
        questions = [
            inquirer.Text(
                'repo_url',
                message="Enter the GitHub repository URL to work on",
                default="https://github.com/username/reponame"
            )
        ]
        answers = inquirer.prompt(questions)
        if answers:
            self.github_repo_url = answers['repo_url']
            self.console.print("\n[cyan]📦 Cloning repository...[/cyan]\n")
            output, self.local_repo_path = self.tool_handlers.set_repository(self.github_repo_url)
            if output:
                self._display_result(output, "Git Clone Output")

    def run(self) -> None:
        self.console.clear()
        self._display_ascii_logo()
        self._display_welcome_panel()
        self._prompt_repo_url()

        while True:
            self._display_tools_table()

            choices = [f"{label}" for label, _, _ in self.tools]
            answers = inquirer.prompt([
                inquirer.List(
                    "action",
                    message="Choose a tool to run",
                    choices=choices,
                )
            ])

            if not answers:
                break  # e.g. Ctrl+C

            selected_label = answers["action"]
            if selected_label == "❌ Exit":
                self.console.print("\n[bold red]Exiting...[/bold red]")
                break

            for name, _, handler in self.tools:
                if name == selected_label and handler:
                    self.console.print(f"\n[green]Running:[/green] {name}\n")
                    try:
                        result, title = handler()
                        self._display_result(result, title)
                    except Exception as e:
                        self.console.print(f"[red]❌ Error:[/red] {str(e)}")
                    input("\nPress [bold]Enter[/bold] to continue...")


def main():
    dashboard = TextDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
