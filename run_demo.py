"""One-command presentation launcher.   python run_demo.py [--app-port 8501] [--site-port 8080] [--no-browser] [--skip-check]
Starts the Streamlit app and serves the website, then opens the website (its Launch buttons point to the app).
Binds to 0.0.0.0 so both PC and mobile devices on the same Wi-Fi can connect. Ctrl+C stops both.
"""
import argparse
import functools
import http.server
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
import webbrowser

ROOT = Path(__file__).resolve().parent


def get_lan_ip() -> str:
    """Detect local network IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def port_open(p: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", p)) == 0


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app-port", type=int, default=8501)
    ap.add_argument("--site-port", type=int, default=8080)
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--skip-check", action="store_true", help="skip the model load/predict test")
    a = ap.parse_args()

    for p in (a.app_port, a.site_port):
        if port_open(p):
            sys.exit(f"Port {p} is already in use (old demo still running?). Close it or pass --app-port/--site-port.")

    if not a.skip_check:
        r = subprocess.run([sys.executable, str(ROOT / "check_setup.py")], cwd=ROOT)
        if r.returncode:
            sys.exit("Fix the [!!] items above, then run again (or use --skip-check).")

    # Start Streamlit listening on 0.0.0.0
    app = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.port",
            str(a.app_port),
            "--server.address",
            "0.0.0.0",
            "--server.headless",
            "true",
            "--browser.gatherUsageStats",
            "false",
        ],
        cwd=ROOT,
    )

    # Start website HTTP server listening on 0.0.0.0
    handler = functools.partial(Quiet, directory=str(ROOT / "website"))
    site = http.server.ThreadingHTTPServer(("0.0.0.0", a.site_port), handler)
    threading.Thread(target=site.serve_forever, daemon=True).start()

    lan_ip = get_lan_ip()
    local_site_url = f"http://localhost:{a.site_port}/?app=http://localhost:{a.app_port}"
    local_app_url = f"http://localhost:{a.app_port}"
    network_site_url = f"http://{lan_ip}:{a.site_port}/?app=http://{lan_ip}:{a.app_port}"
    network_app_url = f"http://{lan_ip}:{a.app_port}"

    try:
        for _ in range(90):
            if port_open(a.app_port):
                break
            if app.poll() is not None:
                sys.exit("Streamlit exited early; run `streamlit run app.py` to see the error.")
            time.sleep(1)

        print("\n" + "=" * 65)
        print("  🌿 KRISHI NETRA DEMO RUNNING SUCCESSFULLY")
        print("=" * 65)
        print("\n  🖥️  ON THIS LAPTOP:")
        print(f"      Showcase Website : {local_site_url}")
        print(f"      Streamlit AI App : {local_app_url}")
        print("\n  📱 ON YOUR PHONE (Same Wi-Fi network):")
        print(f"      Showcase Website : {network_site_url}")
        print(f"      Streamlit AI App : {network_app_url}")
        print("\n  Press Ctrl+C to stop both servers.")
        print("=" * 65 + "\n")

        if not a.no_browser:
            webbrowser.open(local_site_url)
        app.wait()
    except KeyboardInterrupt:
        pass
    finally:
        site.shutdown()
        app.terminate()
        try:
            app.wait(10)
        except Exception:
            app.kill()


if __name__ == "__main__":
    main()
