from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


def port_is_free(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.25)
        return probe.connect_ex((host, port)) != 0


def find_port(host: str, start_port: int, max_port: int) -> int:
    for port in range(start_port, max_port + 1):
        if port_is_free(host, port):
            return port
    raise RuntimeError(f"No free port found from {start_port} to {max_port}.")


def wait_for_health(url: str, timeout_seconds: float) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=1.0) as response:
                if response.status == 200:
                    return True
        except URLError:
            time.sleep(0.35)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Start the N.E.X.U.S FastAPI server in the background.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--max-port", type=int, default=8010)
    parser.add_argument("--timeout", type=float, default=8.0)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    app_root = project_root / "app"
    data_root = project_root / "data"
    data_root.mkdir(exist_ok=True)

    venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    python = venv_python if venv_python.exists() else Path(sys.executable)
    port = find_port(args.host, args.port, args.max_port)

    stdout_log = data_root / f"nexus-server-{port}.out.log"
    stderr_log = data_root / f"nexus-server-{port}.err.log"
    pid_file = data_root / f"nexus-server-{port}.pid"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(app_root)

    command = [
        str(python),
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        args.host,
        "--port",
        str(port),
    ]

    creationflags = 0
    if sys.platform == "win32":
        creationflags = (
            subprocess.CREATE_NEW_PROCESS_GROUP
            | subprocess.CREATE_NO_WINDOW
            | subprocess.DETACHED_PROCESS
        )

    with stdout_log.open("ab") as stdout, stderr_log.open("ab") as stderr:
        process = subprocess.Popen(
            command,
            cwd=app_root,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            creationflags=creationflags,
        )

    pid_file.write_text(str(process.pid), encoding="utf-8")

    health_url = f"http://{args.host}:{port}/api/health"
    ready = wait_for_health(health_url, args.timeout)
    result = {
        "ok": ready,
        "pid": process.pid,
        "url": f"http://{args.host}:{port}",
        "health": health_url,
        "stdout_log": str(stdout_log),
        "stderr_log": str(stderr_log),
        "pid_file": str(pid_file),
    }
    print(json.dumps(result, indent=2))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
