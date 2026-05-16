import http.server
import socket
import socketserver
from pathlib import Path

PORT = 3000
ROOT = Path(__file__).parent  # frontend/


class FrontendHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]  # strip query string
        if path == "/":
            path = "/index.html"

        file_path = ROOT / path.lstrip("/")

        if not file_path.exists() or not file_path.is_file():
            self.send_error(404, "Not found")
            return

        content = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} {fmt % args}")


def local_ip():
    """Return the IP of the first non-loopback, non-Docker interface (prefers wlan/eth)."""
    try:
        import subprocess
        out = subprocess.check_output(["ip", "addr"], text=True)
        # Prefer wlan then eth, skip docker/bridge interfaces
        for iface_prefix in ("wlan", "eth", "en"):
            for line in out.splitlines():
                if "inet " in line and iface_prefix in line.split()[-1]:
                    return line.strip().split()[1].split("/")[0]
    except Exception:
        pass
    # Fallback: route-based detection
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "localhost"


if __name__ == "__main__":
    ip = local_ip()
    with socketserver.TCPServer(("0.0.0.0", PORT), FrontendHandler) as httpd:
        httpd.allow_reuse_address = True
        print(f"Frontend running on:")
        print(f"  http://localhost:{PORT}")
        print(f"  http://{ip}:{PORT}  <- share this on WiFi")
        print("Press Ctrl+C to stop.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
