#!/usr/bin/env python3
# mixdhttpdev - by mixddev ❤️

import argparse
import os
import sys
import socket
import threading
import http.server
import socketserver
import time
import random
import string
import subprocess
import webbrowser
import ssl
from rich.console import Console
from rich.panel import Panel
from urllib.parse import unquote
from base64 import b64decode

console = Console()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_external_ip():
    try:
        output = subprocess.check_output(
            "ip -o -4 addr list | grep -v '127.0.0.1'",
            shell=True, stderr=subprocess.DEVNULL
        ).decode().strip()
        for line in output.splitlines():
            ip = line.split()[3].split('/')[0]
            if ip:
                return ip
    except Exception:
        pass
    try:
        output = subprocess.check_output("hostname -I", shell=True, stderr=subprocess.DEVNULL).decode().strip()
        if output:
            return output.split()[0]
    except Exception:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        pass
    return None

def generate_password(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def generate_username(length=8):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def save_log(log_file, text):
    with open(log_file, "a") as f:
        f.write(text + "\n")

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    server_version = "mixd/1.0"
    sys_version = ""

    def __init__(self, *args, directory=None, log_file=None, enable_logs=True, log_level="info",
                 username=None, password=None, require_auth=False, no_logs=False, **kwargs):
        self.log_file = log_file
        self.enable_logs = enable_logs
        self.log_level = log_level
        self.username = username
        self.password = password
        self.require_auth = require_auth
        self.no_logs = no_logs
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format, *args):
        if self.no_logs:
            return
        msg = "%s - - [%s] %s" % (
            self.client_address[0],
            self.log_date_time_string(),
            format % args
        )
        console.log(msg)
        if self.log_file:
            save_log(self.log_file, msg)

    def do_HEAD(self):
        if self.require_auth and not self.check_auth():
            self.send_auth_request()
            return
        return super().do_HEAD()

    def do_GET(self):
        if self.require_auth and not self.check_auth():
            self.send_auth_request()
            return
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            index_path = os.path.join(path, "index.html")
            if os.path.exists(index_path):
                self.path = os.path.join(self.path, "index.html")
                return super().do_GET()
            else:
                return self.list_directory(path)
        else:
            if not os.path.exists(path):
                return self.serve_404()
            return super().do_GET()

    def serve_404(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content = """
        <html><head><title>404 Not Found</title></head>
        <body style="font-family:sans-serif; text-align:center; margin-top:50px;">
        <h1>404 - page not found</h1>
        <p>Oops! The page you requested does not exist.</p>
        </body></html>
        """
        self.wfile.write(content.encode('utf-8'))

    def list_directory(self, path):
        try:
            listing = os.listdir(path)
        except OSError:
            self.send_error(404, "No permission to list directory")
            return None
        listing.sort(key=lambda a: a.lower())
        r = []
        displaypath = unquote(self.path)
        r.append(f'<!DOCTYPE html><html><head><title>Directory listing for {displaypath}</title><style>body{{font-family:sans-serif; background:#f9f9f9;}}ul{{list-style:none;padding:0;}}li{{margin:5px 0;}}a{{text-decoration:none;color:#0366d6;}}a:hover{{text-decoration:underline;}}</style></head>')
        r.append(f'<body>')
        r.append(f'<h2>Directory listing for {displaypath}</h2>')
        r.append('<hr><ul>')
        for name in listing:
            fullname = os.path.join(path, name)
            displayname = name + ("/" if os.path.isdir(fullname) else "")
            linkname = name + ("/" if os.path.isdir(fullname) else "")
            r.append(f'<li><a href="{linkname}">{displayname}</a></li>')
        r.append('</ul><hr></body></html>')
        encoded = '\n'.join(r).encode('utf-8')
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
        return None

    def check_auth(self):
        if not self.require_auth:
            return True
        auth_header = self.headers.get("Authorization")
        if auth_header is None or not auth_header.startswith("Basic "):
            return False
        encoded = auth_header.split(" ", 1)[1].strip()
        decoded = b64decode(encoded).decode('utf-8')
        username, password = decoded.split(":", 1)
        return username == self.username and password == self.password

    def send_auth_request(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="mixd"')
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Authentication required")

def run_cloudflared(port):
    try:
        subprocess.run(["cloudflared", "--version"], check=True, stdout=subprocess.DEVNULL)
    except Exception:
        console.print("[red]cloudflared is not installed or not in PATH[/red]")
        sys.exit(1)

    console.print("[cyan]Starting cloudflared tunnel...[/cyan]")
    proc = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    def grab_url():
        for line in proc.stdout:
            if "trycloudflare.com" in line:
                url = line.strip().split()[-1]
                console.print(f"[bold green]Cloudflare Tunnel:[/bold green] {url}")
                break

    threading.Thread(target=grab_url, daemon=True).start()
    return proc

def run_server(args):
    clear_console()
    console.print(Panel.fit(f"🚀  starting {args.mode} server", style="bold green"))

    directory = os.getcwd()
    file_to_serve = f"{args.file}.html"

    if not os.path.exists(os.path.join(directory, file_to_serve)):
        console.print("[red]index not found, stopped[/red]")
        sys.exit(1)

    username = None
    password = None
    require_auth = False

    if args.mode == "dev" and (args.cloudflared or not args.no_pass):
        password = args.set_password if args.set_password else generate_password()
        username = generate_username()
        require_auth = True
        console.print(f"[bold yellow]username:[/bold yellow] {username}")
        console.print(f"[bold yellow]password:[/bold yellow] {password}")

    log_file = os.path.join(directory, f"server_{time.strftime('%Y%m%d_%H%M%S')}.log") if args.logs else None

    class HandlerFactory:
        def __call__(self, *handler_args, **handler_kwargs):
            return CustomHTTPRequestHandler(*handler_args,
                directory=directory,
                log_file=log_file,
                enable_logs=args.logs,
                log_level=args.minlog,
                username=username,
                password=password,
                require_auth=require_auth,
                no_logs=not args.logs,
                **handler_kwargs)

    with socketserver.ThreadingTCPServer(("localhost", args.port), HandlerFactory()) as httpd:
        httpd.allow_reuse_address = True
        ext_ip = get_external_ip()

        # HTTPS setup
        cert_file = os.path.join(directory, "cert.pem")
        key_file = os.path.join(directory, "key.pem")

        if not (os.path.exists(cert_file) and os.path.exists(key_file)):
            console.print("[yellow]Generating self-signed certificate...[/yellow]")
            subprocess.run([
                "openssl", "req", "-new", "-x509", "-days", "365",
                "-nodes", "-out", cert_file, "-keyout", key_file,
                "-subj", "/CN=localhost"
            ], check=True)

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=cert_file, keyfile=key_file)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

        console.print(f"[bold cyan]mode[/bold cyan] {args.mode}")
        console.print(f"[bold cyan]host[/bold cyan] localhost")
        console.print(f"[bold cyan]port[/bold cyan] {args.port}")
        console.print(f"[bold cyan]file[/bold cyan] {file_to_serve}")
        console.print(f"[bold cyan]directory[/bold cyan] {directory}")
        console.print(f"HTTPS enabled: {cert_file} + {key_file}")

        if args.cloudflared:
            run_cloudflared(args.port)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            console.print("[red]Server stopped[/red]")
            httpd.server_close()

def main():
    parser = argparse.ArgumentParser(description="Mixd HTTP Dev Server")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--file", type=str, default="index")
    parser.add_argument("--mode", choices=["dev", "prod"], default="dev")
    parser.add_argument("--cloudflared", action="store_true")
    parser.add_argument("--logs", action="store_true")
    parser.add_argument("--minlog", choices=["debug", "info", "warn"], default="info")
    parser.add_argument("--no-pass", action="store_true")
    parser.add_argument("--set-password", type=str, help="Set custom password")
    args = parser.parse_args()

    run_server(args)
