from .base_module import BaseModule
from rich.table import Table

class Module(BaseModule):
    @property
    def commands(self) -> list[str]:
        return ["enum"]

    def get_help(self) -> dict:
        return {
            "enum": ("<sysinfo|ps|netstat|suid>", "Perform system enumeration.")
        }

    def execute(self, args: list[str]):
        if not args:
            return self.console.print("[red]Usage: enum <sysinfo|ps|netstat|suid>[/red]")
        sub_cmd = args[0]

        with self.console.status(f"[cyan]Running enum: {sub_cmd}...", spinner="dots"):
            if sub_cmd == "sysinfo": self._sysinfo()
            elif sub_cmd == "ps": self._ps()
            elif sub_cmd == "netstat": self._netstat()
            elif sub_cmd == "suid": self._suid()
            else: self.console.print(f"[red]Unknown enum command: {sub_cmd}[/red]")

    def _sysinfo(self):
        cmds = {"OS": "uname -a", "User": "id", "Network": "ip a || ifconfig", "Release": "cat /etc/*release"}
        results = {key: self.shell.execute_command(cmd).get('output', '[ERROR]') for key, cmd in cmds.items()}
        table = Table(title="💻 Remote System Information", border_style="magenta")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        for key, value in results.items(): table.add_row(key, value.strip())
        self.console.print(table)

    def _ps(self):
        cmd = "ps aux"
        res = self.shell.execute_command(cmd)
        self.shell.handle_output(res.get('output', ''))

    def _netstat(self):
        cmd = "netstat -tulnp"
        res = self.shell.execute_command(cmd)
        self.shell.handle_output(res.get('output', ''))

    def _suid(self):
        cmd = "find / -type f -perm -04000 -ls 2>/dev/null"
        res = self.shell.execute_command(cmd)
        self.shell.handle_output(res.get('output', ''))