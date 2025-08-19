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
        
        
def ensure_shell_integration():
    """Auto-install shell integration if not present"""
    zshrc_path = Path.home() / ".zshrc"
    
    # Check if already installed
    if zshrc_path.exists():
        with open(zshrc_path, 'r') as f:
            content = f.read()
            if "# SCCB shell integration" in content:
                return  # Already installed
    
    # Auto-install
    shell_function = '''
# SCCB shell integration
sccb() {
    if [[ "$1" == "run" ]] && [[ "$*" != *"!"* ]]; then
        local output=$(command sccb "$@" --buffer 2>/dev/null)
        if [[ "$output" == __SCCB_BUFFER__* ]]; then
            local cmd="${output#__SCCB_BUFFER__}"
            print -z "$cmd"
        else
            command sccb "$@"
        fi
    else
        command sccb "$@"
    fi
}
'''
    
    with open(zshrc_path, 'a') as f:
        f.write(shell_function)
        
    console.print("\n[bold green]✓ Shell integration installed![/bold green]")
    console.print("[bold yellow]⚠ Action required:[/bold yellow] Run this command to activate:")
    console.print(f"[bold cyan]source ~/.zshrc[/bold cyan]")
    console.print("\n[dim]Or restart your terminal. This only needs to be done once.[/dim]\n")
    raise typer.Exit(0)


@app.command()
def install_shell():
    """
    Install shell integration for buffer functionality
    """
    shell_function = '''
# SCCB shell integration
sccb() {
    if [[ "$1" == "run" ]] && [[ "$*" != *"!"* ]]; then
        local output=$(command sccb run "$@" --buffer 2>/dev/null)
        if [[ "$output" == __SCCB_BUFFER__* ]]; then
            local cmd="${output#__SCCB_BUFFER__}"
            print -z "$cmd"
        else
            command sccb "$@"
        fi
    else
        command sccb "$@"
    fi
}
'''
    
    zshrc_path = Path.home() / ".zshrc"
    bashrc_path = Path.home() / ".bashrc"
    
    # Detect shell and install
    shell = os.environ.get('SHELL', '').split('/')[-1]
    
    if 'zsh' in shell:
        with open(zshrc_path, 'a') as f:
            f.write(shell_function)
        console.print("[green]✓[/green] Shell integration installed to ~/.zshrc")
        console.print("Run: [cyan]source ~/.zshrc[/cyan] or restart your terminal")
    elif 'bash' in shell:
        # Similar for bash
        console.print("[green]✓[/green] Shell integration installed to ~/.bashrc")
    else:
        console.print("[yellow]⚠[/yellow] Unknown shell. Manual setup required.")


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


def execute_shortcut(name: str, args: list[str]):
    """
    Execute a shortcut directly (used by main callback for unknown commands)
    """
    config = load_config()

    if name in config["commands"]:
        cmd = config["commands"][name]["value"]
        defaults = config["commands"][name].get("defaults", {})

        # Parse args like msg:"Fixed bug"
        variables = {}
        execute = False
        for arg in args or []:
            if arg == "!":
                execute = True
            elif ":" in arg:
                k, v = arg.split(":", 1)
                variables[k] = v.strip('"').strip("'")

        merged = {**defaults, **variables}

        try:
            cmd = cmd.format(**merged)
        except KeyError as e:
            typer.echo(f"Missing variable: {e}")
            raise typer.Exit(1)

        if execute:
            typer.echo(f"Executing: {cmd}")
            subprocess.run(cmd, shell=True)
        else:
            # Copy to clipboard and show (default behavior without !)
            pyperclip.copy(cmd)
            typer.echo(f"Command copied to clipboard: {cmd}")

    elif name in config["snippets"]:
        val = config["snippets"][name]["value"]
        defaults = config["snippets"][name].get("defaults", {})

        variables = {}
        for arg in args or []:
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
def run(
    name: str = typer.Argument(..., help="The shortcut name"),
    args: list[str] = typer.Argument(default=None, help="Optional arguments for variables or !"),
    buffer: bool = typer.Option(False, "--buffer", "-b", help="Put command in shell buffer (requires shell integration)")
):
    """
    Run or print a shortcut (kept for backward compatibility and buffer functionality).
    """
    # Only auto-install if buffer is not set (avoid the exit when called with --buffer)
    if not buffer:
        ensure_shell_integration()
    
    config = load_config()

    if name in config["commands"]:
        cmd = config["commands"][name]["value"]
        defaults = config["commands"][name].get("defaults", {})

        # Parse args like msg:"Fixed bug"
        variables = {}
        execute = False
        for arg in args or []:
            if arg == "!":
                execute = True
            elif ":" in arg:
                k, v = arg.split(":", 1)
                variables[k] = v.strip('"').strip("'")

        merged = {**defaults, **variables}

        try:
            cmd = cmd.format(**merged)
        except KeyError as e:
            typer.echo(f"Missing variable: {e}")
            raise typer.Exit(1)

        if execute:
            typer.echo(f"Executing: {cmd}")
            subprocess.run(cmd, shell=True)
        elif buffer:
            # Output for shell buffer integration
            print(f"__SCCB_BUFFER__{cmd}")
        else:
            # Copy to clipboard and show
            pyperclip.copy(cmd)
            typer.echo(f"Command copied to clipboard: {cmd}")

    elif name in config["snippets"]:
        val = config["snippets"][name]["value"]
        defaults = config["snippets"][name].get("defaults", {})

        variables = {}
        for arg in args or []:
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
    console.print("  sccb name var:\"value\" -> Use variables")
    console.print("  sccb ls          -> List all saved commands and snippets")
    console.print("  sccb rm name     -> Remove a shortcut")
    console.print("  sccb default name var:\"value\" -> Set default variable value")
    console.print("  sccb edit        -> Open config file in your editor\n")

    console.print("[bold magenta]Examples[/bold magenta]")
    console.print("  sccb add gitall:\"git add . && git commit -m '{msg}' && git push\"")
    console.print("  sccb default gitall msg:\"WIP commits\"  -> Set default message")
    console.print("  sccb gitall      -> Uses default: 'WIP commits'")
    console.print("  sccb gitall msg:\"Fixed bug\" -> Override with custom message")
    console.print("  sccb gitall !    -> Execute with defaults")
    console.print("  sccb add@ greet:\"Hello {name}!\"")
    console.print("  sccb greet name:\"Alice\" -> Copies 'Hello Alice!' to clipboard\n")

    console.print(
        "[bold green]Tip:[/bold green] Use [cyan]add@[/cyan] for snippets and [cyan]add$[/cyan] for commands."
    )


# Add a command to set defaults
@app.command()
def default(
    name: str = typer.Argument(..., help="Shortcut name"),
    entry: str = typer.Argument(..., help="Default in format key:value")
):
    """
    Set a default value for a shortcut variable.
    Example: sccb default gitall msg:"WIP commits"
    """
    if ":" not in entry:
        typer.echo("Error: must be in format key:\"value\"")
        raise typer.Exit(1)

    key, value = entry.split(":", 1)
    key = key.strip()
    value = value.strip().strip('"').strip("'")

    config = load_config()
    
    # Check if shortcut exists
    if name in config["commands"]:
        if "defaults" not in config["commands"][name]:
            config["commands"][name]["defaults"] = {}
        config["commands"][name]["defaults"][key] = value
        save_config(config)
        typer.echo(f"Set default for command '{name}': {key} = {value}")
    elif name in config["snippets"]:
        if "defaults" not in config["snippets"][name]:
            config["snippets"][name]["defaults"] = {}
        config["snippets"][name]["defaults"][key] = value
        save_config(config)
        typer.echo(f"Set default for snippet '{name}': {key} = {value}")
    else:
        typer.echo(f"No shortcut named '{name}' found")
        raise typer.Exit(1)


# Add a fallback command that will handle unknown commands as shortcuts
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    SCCB - Shortcut Clipboard + Command Binder
    
    Use shortcuts directly: sccb <shortcut_name>
    """
    if ctx.invoked_subcommand is None:
        # If no subcommand and no args, show help
        if not ctx.params:
            help()
            return
        
        # Get the raw arguments from sys.argv to handle the shortcut case
        import sys
        if len(sys.argv) > 1:
            # The first argument after the script name should be the shortcut
            shortcut_name = sys.argv[1]
            shortcut_args = sys.argv[2:] if len(sys.argv) > 2 else []
            
            # Check if this is actually a known command that somehow wasn't caught
            known_commands = {"add", "add$", "add@", "ls", "rm", "edit", "help", "install_shell", "run", "default"}
            if shortcut_name not in known_commands:
                # Treat as shortcut - call the shortcut function directly
                execute_shortcut(shortcut_name, shortcut_args)
                return
        
        # Fallback to help if we can't figure out what to do
        help()


if __name__ == "__main__":
    app()