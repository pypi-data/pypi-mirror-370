# sccb/cli.py
import typer
import json
import subprocess
import pyperclip
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer()

CONFIG_PATH = Path.home() / ".sccb.json"


def load_config():
    if not CONFIG_PATH.exists():
        return {"snippets": {}, "commands": {}}
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        console.print(
            f"[bold red]Error:[/bold red] Could not parse {CONFIG_PATH} (invalid JSON)"
        )
        raise typer.Exit(1)


def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


@app.command()
def ls():
    """
    List all saved snippets and commands
    """
    config = load_config()

    # Commands table
    if config["commands"]:
        table = Table(title="Commands", show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Command", style="green")
        for name, data in config["commands"].items():
            table.add_row(name, data["value"])
        console.print(table)
    else:
        console.print("[bold magenta]Commands:[/bold magenta] (none)")

    # Snippets table
    if config["snippets"]:
        table = Table(title="Snippets", show_header=True, header_style="bold yellow")
        table.add_column("Name", style="cyan")
        table.add_column("Snippet", style="green")
        for name, data in config["snippets"].items():
            table.add_row(name, data["value"])
        console.print(table)
    else:
        console.print("[bold yellow]Snippets:[/bold yellow] (none)")


@app.command("add")
@app.command("add$")
def add_command(entry: str):
    """
    Add a new COMMAND shortcut.
    Example:
      sccb add gitall:"git add . && git commit -m 'msg' && git push"
      sccb add$ gitall:"git add . && git commit -m 'msg' && git push"
    """
    if ":" not in entry:
        typer.echo("Error: must be in format name:\"value\"")
        raise typer.Exit(1)

    name, value = entry.split(":", 1)
    name = name.strip()
    value = value.strip().strip('"').strip("'")

    config = load_config()
    config["commands"][name] = {"type": "command", "value": value}
    save_config(config)
    typer.echo(f"Added command: {name} -> {value}")


@app.command("add@")
def add_snippet(entry: str):
    """
    Add a new SNIPPET shortcut.
    Example:
      sccb add@ greet:"Hello, how are you?"
    """
    if ":" not in entry:
        typer.echo("Error: must be in format name:\"value\"")
        raise typer.Exit(1)

    name, value = entry.split(":", 1)
    name = name.strip()
    value = value.strip().strip('"').strip("'")

    config = load_config()
    config["snippets"][name] = {"type": "snippet", "value": value}
    save_config(config)
    typer.echo(f"Added snippet: {name} -> {value}")


@app.command()
def run(name: str, *args: str):
    """
    Run or print a shortcut.
    - Commands:
        sccb gitall             -> prints the command (with defaults if any)
        sccb gitall !           -> executes the command
        sccb gitall msg:"Fix" ! -> replaces {msg} with "Fix" and executes
    - Snippets:
        sccb greet              -> copies text to clipboard (supports {vars})
    """
    config = load_config()

    if name in config["commands"]:
        cmd = config["commands"][name]["value"]
        defaults = config["commands"][name].get("defaults", {})

        # Parse args like msg:"Fixed bug"
        variables = {}
        execute = False
        for arg in args:
            if arg == "!":
                execute = True
            elif ":" in arg:
                k, v = arg.split(":", 1)
                variables[k] = v.strip('"').strip("'")

        # Merge defaults with overrides
        merged = {**defaults, **variables}

        # Replace placeholders
        try:
            cmd = cmd.format(**merged)
        except KeyError as e:
            typer.echo(f"Missing variable: {e}")
            raise typer.Exit(1)

        if execute:
            typer.echo(f"Executing: {cmd}")
            subprocess.run(cmd, shell=True)
        else:
            typer.echo(cmd)

    elif name in config["snippets"]:
        val = config["snippets"][name]["value"]
        defaults = config["snippets"][name].get("defaults", {})

        # Parse args for snippets too
        variables = {}
        for arg in args:
            if ":" in arg:
                k, v = arg.split(":", 1)
                variables[k] = v.strip('"').strip("'")

        merged = {**defaults, **variables}

        try:
            val = val.format(**merged)
        except KeyError as e:
            typer.echo(f"Missing variable: {e}")
            raise typer.Exit(1)

        pyperclip.copy(val)
        typer.echo(f"Copied snippet '{name}' to clipboard")

    else:
        typer.echo(f"No shortcut named '{name}' found")

@app.command()
def rm(name: str):
    """
    Remove a shortcut by name.
    Example: sccb rm xyz
    """
    config = load_config()

    if name in config["commands"]:
        del config["commands"][name]
        save_config(config)
        typer.echo(f"Removed command: {name}")
    elif name in config.get("snippets", {}):
        del config["snippets"][name]
        save_config(config)
        typer.echo(f"Removed snippet: {name}")
    else:
        typer.echo(f"No shortcut named '{name}' found")


@app.command()
def edit():
    """
    Open the config file in your default editor
    """
    editor = os.environ.get("EDITOR", "nano")  # fallback to nano
    subprocess.run([editor, str(CONFIG_PATH)])


@app.command()
def help():
    """
    Show a guide to all sccb commands
    """
    console.print("[bold cyan]SCCB - Shortcut Clipboard + Command Binder[/bold cyan]\n")

    console.print("[bold magenta]Adding Shortcuts[/bold magenta]")
    console.print("  sccb add name:\"command\"     -> Add a command (default)")
    console.print("  sccb add$ name:\"command\"    -> Add a command (explicit)")
    console.print("  sccb add@ name:\"snippet\"    -> Add a snippet (clipboard text)\n")

    console.print("[bold magenta]Using Shortcuts[/bold magenta]")
    console.print("  sccb name        -> Print command OR copy snippet to clipboard")
    console.print("  sccb name !      -> Execute command")
    console.print("  sccb ls          -> List all saved commands and snippets")
    console.print("  sccb rm name     -> Remove a shortcut")
    console.print("  sccb edit        -> Open config file in your editor\n")

    console.print("[bold magenta]Examples[/bold magenta]")
    console.print("  sccb add gitall:\"git add . && git commit -m 'msg' && git push\"")
    console.print("  sccb gitall      -> Prints the git command")
    console.print("  sccb gitall !    -> Runs the git command")
    console.print("  sccb add@ greet:\"Hello!\"")
    console.print("  sccb greet       -> Copies 'Hello!' to clipboard\n")

    console.print(
        "[bold green]Tip:[/bold green] Use [cyan]add@[/cyan] for snippets and [cyan]add$[/cyan] for commands."
    )


if __name__ == "__main__":
    app()