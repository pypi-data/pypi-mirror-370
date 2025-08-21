from .base_module import BaseModule
from rich.console import Console

class Module(BaseModule):
    @property
    def commands(self) -> list[str]:
        return ["php"]

    def get_help(self) -> dict:
        return {
            "php": ("", "Start an interactive PHP shell (`php -a`). Type 'exit' to return.")
        }

    def execute(self, args: list[str]):
        self.console.print("[cyan]Entering interactive PHP shell. Type 'exit' to leave.[/cyan]")
        while True:
            try:
                php_code = self.console.input("[bold magenta]php>[/bold magenta] ")
                if php_code.lower() == 'exit':
                    break
                payload = {'action': 'php_interactive', 'cmd': php_code}
                res = self.conn.send_request(payload, timeout=60)

                if res.get('status') == 'success':
                    output = res.get('output', '')
                    # Clean up PHP interactive prompt garbage
                    clean_output = '\n'.join([line for line in output.splitlines() if not line.startswith('Interactive shell')])
                    self.console.print(clean_output.strip())
                else:
                    self.console.print(f"[red]Error: {res.get('message')}[/red]")
            except KeyboardInterrupt:
                self.console.print()
                continue
            except EOFError:
                break