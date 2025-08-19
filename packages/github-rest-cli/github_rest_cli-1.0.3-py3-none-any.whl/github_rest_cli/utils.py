from rich import print as rprint


def rich_output(message: str, format_str: str = "bold green"):
    rprint(f"[{format_str}]{message}[/{format_str}]")
