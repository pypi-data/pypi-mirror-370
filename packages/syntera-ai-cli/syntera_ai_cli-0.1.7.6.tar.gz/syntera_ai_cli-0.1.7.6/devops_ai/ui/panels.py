# devops_ai/ui/panels.py

from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.table import Table
from rich.markdown import Markdown
from rich.padding import Padding
from rich.rule import Rule
from rich.align import Align
from rich.box import HEAVY, ROUNDED
from rich.style import Style
from datetime import datetime
from rich.console import Group, Console
from rich.progress import BarColumn, Progress
from rich import box

def create_header() -> Panel:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a more visually appealing header with gradient styling
    header_group = Group(
        Rule("✨ SynteraAI DevOps ✨", style="gradient(magenta,cyan)"),
        Text.from_markup("[bold cyan]🤖 SynteraAI DevOps Dashboard[/bold cyan]"),
        Text.from_markup(f"[dim]Your AI-powered DevOps assistant | [bold]{current_time}[/bold][/dim]")
    )

    return Panel(
        Padding(header_group, (1, 1)),
        border_style="bright_blue",
        box=ROUNDED,
        title="[bold white on bright_blue] 🚀 SynteraAI DevOps [/bold white on bright_blue]",
        title_align="center",
        subtitle="[dim italic]Powered by AI[/dim italic]",
        subtitle_align="right"
    )




def create_tools_panel(selected_tool: dict = None) -> Panel:
    """
    Displays only the currently selected tool in a focused panel with enhanced styling.
    
    Args:
        selected_tool (dict): The tool dictionary containing name, description, icon, etc.
    """
    if selected_tool is None:
        selected_tool = {
            "key": "?",
            "icon": "❓",
            "name": "No Tool Selected",
            "desc": "Use ↑ ↓ keys to navigate and press ENTER to select.",
        }

    # Create a progress bar to visually indicate selection
    progress = Progress(
        "[bright_blue]{task.description}",
        BarColumn(bar_width=20, style="bright_blue", complete_style="bright_cyan"),
        "[bright_blue]{task.percentage:>3.0f}%",
        expand=False
    )
    
    # Add a task that's 100% complete to show a full bar
    task_id = progress.add_task("Selected", total=100)
    progress.update(task_id, completed=100)
    
    # Build the tool display with enhanced styling
    tool_group = Group(
        Text.from_markup(f"[bold bright_cyan on bright_blue] {selected_tool['key']} [/bold bright_cyan on bright_blue] [bold white on bright_blue]{selected_tool['icon']} {selected_tool['name']}[/bold white on bright_blue]"),
        Text(""),  # Spacer
        Text.from_markup(f"[italic bright_white]{selected_tool['desc']}[/italic bright_white]"),
        Text(""),  # Spacer
        progress
    )

    return Panel(
        Padding(tool_group, (1, 1)),
        title="[bold white on bright_blue] 🔧 Selected Tool [/bold white on bright_blue]",
        border_style="bright_cyan",
        box=ROUNDED,
        subtitle="[dim italic]Press ENTER to run[/dim italic]",
        subtitle_align="right"
    )


def create_content_panel(content=None) -> Panel:
    if not content:
        welcome_md = """
        # 🌟 Welcome to SynteraAI DevOps Dashboard 🌟
        
        This intelligent dashboard provides AI-powered tools to streamline your DevOps workflow.
        
        ## 🚀 Getting Started
        1. Use ↑↓ keys or numbers 1-9 to navigate the tool list
        2. Press ENTER to activate the selected tool
        3. View detailed analysis and results in this panel
        
        ## 💡 Available Features
        - Log analysis and error detection
        - Infrastructure recommendations
        - Security vulnerability scanning
        - Performance optimization
        - Code quality assessment
        - And much more!
        """
        content = Markdown(welcome_md)

    return Panel(
        Padding(content, (1, 2)),
        title="[bold white on bright_blue] 📊 Results & Analysis [/bold white on bright_blue]",
        border_style="bright_cyan",
        box=ROUNDED,
        title_align="center",
        subtitle="[dim italic]Real-time insights[/dim italic]",
        subtitle_align="right"
    )


def create_footer() -> Panel:
    footer_group = Group(
        Text.from_markup("[bold bright_green]📝 Navigation Guide:[/bold bright_green]"),
        Text(""),  # Spacer
        Text.from_markup("[bright_white]• [bright_cyan]↑↓[/bright_cyan] or [bright_cyan]j/k[/bright_cyan] - Navigate through tools[/bright_white]"),
        Text.from_markup("[bright_white]• [bright_cyan]1-9[/bright_cyan] - Directly select a tool by number[/bright_white]"),
        Text.from_markup("[bright_white]• [bright_cyan]ENTER[/bright_cyan] - Run the selected tool[/bright_white]"),
        Text.from_markup("[bright_white]• [bright_cyan]q[/bright_cyan] - Quit the application[/bright_white]")
    )

    return Panel(
        Padding(Align.center(footer_group), (1, 1)),
        border_style="bright_green",
        box=ROUNDED,
        title="[bold white on bright_green] 💡 Help & Navigation [/bold white on bright_green]",
        title_align="center",
        subtitle="[dim italic]Keyboard shortcuts[/dim italic]",
        subtitle_align="right"
    )


def create_input_panel(prompt_text="Select a tool (↑↓/1-9), ENTER to confirm, Q to quit") -> Panel:
    input_text = Text()
    input_text.append("▶ ", style="bold bright_green")
    input_text.append(prompt_text, style="bold bright_cyan")
    
    return Panel(
        Padding(input_text, (1, 1)),
        border_style="bright_green",
        box=ROUNDED,
        title="[bold white on bright_green] 🔤 Command Input [/bold white on bright_green]",
        title_align="center",
        subtitle="[dim italic]Ready[/dim italic]",
        subtitle_align="right"
    )


def create_result_table(result: str, title: str) -> Group:
    # Create a more visually appealing table with better styling
    table = Table(
        title=title,
        show_header=True,
        header_style="bold bright_magenta",
        border_style="bright_cyan",
        title_style="bold bright_cyan",
        box=box.ROUNDED,
        expand=True,
        row_styles=["bright_white", "bright_white dim"]
    )

    table.add_column("#", style="bright_cyan", width=3, justify="center")
    table.add_column("Finding", style="bright_white", ratio=1)

    sections = result.split("\n\n")
    for i, section in enumerate(sections, 1):
        if section.strip():
            table.add_row(str(i), section)

    return Group(
        Rule(f"✨ {title} ✨", style="gradient(cyan,magenta)"),
        Text(""),  # Spacer
        table
    )