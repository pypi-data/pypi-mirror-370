import os
import base64
from .base_module import BaseModule
from rich.progress import Progress, BarColumn, TextColumn, TransferSpeedColumn, TimeRemainingColumn

class Module(BaseModule):
    @property
    def commands(self) -> list[str]:
        return ["cd", "upload", "download", "archive"]

    def get_help(self) -> dict:
        return {
            "cd": ("<path>", "Change the current remote working directory."),
            "upload": ("<local_file> <remote_dest>", "Upload a file to the server."),
            "download": ("<remote_file> <local_dest>", "Download a file from the server."),
            "archive": ("<remote_dir> <local_zip>", "ZIPs a remote directory and downloads it.")
        }

    def execute(self, args: list[str]):
        cmd = args.pop(0)
        if cmd == "cd": self._handle_cd(args)
        elif cmd == "upload": self._handle_upload(args)
        elif cmd == "download": self._handle_download(args)
        elif cmd == "archive": self._handle_archive(args)

    def _handle_cd(self, args: list[str]):
        target_path = args[0] if args else "~"
        verify_cmd = f"cd {self.shell.current_path} && cd {target_path} && pwd"
        data = self.shell.execute_command(verify_cmd)
        if data.get('status') == 'success' and data.get('output'):
            self.shell.current_path = data['output'].strip()
            self.shell._update_prompt_info() # Refresh user/path info
        else:
            self.console.print(f"[red]cd failed: {data.get('message', 'Directory not found')}[/red]")

    def _handle_upload(self, args: list[str]):
        if len(args) != 2: return self.console.print("[red]Usage: upload <local_file> <remote_dest>[/red]")
        local, remote = args
        remote = os.path.join(self.shell.current_path, remote) if not os.path.isabs(remote) else remote
        if not os.path.exists(local): return self.console.print(f"[red]Local file not found: {local}[/red]")

        with open(local, 'rb') as f: content = base64.b64encode(f.read()).decode()
        payload = {'action': 'upload', 'path': remote, 'data': content}
        res = self.conn.send_request(payload, timeout=300)

        if res.get('status') == 'success': self.console.print(f"[green]Uploaded '{local}' to '{remote}'[/green]")
        else: self.console.print(f"[red]Upload failed: {res.get('message')}[/red]")

    def _handle_download(self, args: list[str]):
        if len(args) != 2: return self.console.print("[red]Usage: download <remote_file> <local_dest>[/red]")
        remote, local = args
        remote = os.path.join(self.shell.current_path, remote) if not os.path.isabs(remote) else remote

        res = self.conn.send_request({'action': 'download', 'path': remote}, timeout=300)

        if res.get('status') == 'success':
            content = base64.b64decode(res.get('data', ''))
            with open(local, 'wb') as f: f.write(content)
            self.console.print(f"[green]Downloaded '{remote}' to '{local}'[/green]")
        else: self.console.print(f"[red]Download failed: {res.get('message')}[/red]")

    def _handle_archive(self, args: list[str]):
        if len(args) != 2: return self.console.print("[red]Usage: archive <remote_dir> <local_zip_file>[/red]")
        remote_dir, local_zip = args
        remote_path = os.path.join(self.shell.current_path, remote_dir) if not os.path.isabs(remote_dir) else remote_dir

        with self.console.status("[yellow]Archiving remote directory...", spinner="earth"):
            res = self.conn.send_request({'action': 'archive', 'path': remote_path}, timeout=600)

        if res.get('status') == 'success':
            content = base64.b64decode(res.get('data', ''))
            with open(local_zip, 'wb') as f: f.write(content)
            self.console.print(f"[green]Successfully archived '{remote_path}' to '{local_zip}'[/green]")
        else: self.console.print(f"[red]Archive failed: {res.get('message')}[/red]")