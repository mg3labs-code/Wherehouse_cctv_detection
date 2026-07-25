"""Start GLS Safety API (backend for the React dashboard)."""
from __future__ import annotations

import argparse
import subprocess
import sys


PORT = 8001
HOST = "0.0.0.0"


def _windows_pids_on_port(port: int) -> list[int]:
    """Return PIDs listening on TCP port (Windows netstat)."""
    try:
        out = subprocess.check_output(
            ["netstat", "-ano", "-p", "tcp"],
            text=True,
            errors="ignore",
        )
    except Exception:
        return []
    pids: list[int] = []
    # Match ":8001" as a local port (not remote)
    for line in out.splitlines():
        upper = line.upper()
        if "LISTENING" not in upper:
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        local = parts[1]  # e.g. 0.0.0.0:8001 or [::]:8001
        if not (local.endswith(f":{port}") or local.endswith(f"]:{port}")):
            continue
        try:
            pid = int(parts[-1])
        except ValueError:
            continue
        if pid > 0 and pid not in pids:
            pids.append(pid)
    return pids


def _kill_pids(pids: list[int]) -> None:
    for pid in pids:
        try:
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/F"],
                check=False,
                capture_output=True,
                text=True,
            )
            print(f"Stopped process PID {pid}")
        except Exception as exc:
            print(f"Could not stop PID {pid}: {exc}", file=sys.stderr)


def _print_busy(pids: list[int]) -> None:
    print(f"\nERROR: Port {PORT} is already in use.", file=sys.stderr)
    if pids:
        print(f"Process(es) holding it: {', '.join(str(p) for p in pids)}", file=sys.stderr)
        print("Fix:", file=sys.stderr)
        for pid in pids:
            print(f"  taskkill /PID {pid} /F", file=sys.stderr)
        print("Or restart with:  python run_api.py --kill", file=sys.stderr)
    else:
        print(f"Find it with:  netstat -ano | findstr :{PORT}", file=sys.stderr)
    print("", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GLS Safety API on port 8001")
    parser.add_argument(
        "--kill",
        action="store_true",
        help="Stop whatever is already listening on port 8001, then start",
    )
    args = parser.parse_args()

    pids = _windows_pids_on_port(PORT)
    if pids:
        if args.kill:
            _kill_pids(pids)
            import time
            time.sleep(1.0)
            pids = _windows_pids_on_port(PORT)
            if pids:
                _print_busy(pids)
                sys.exit(1)
        else:
            _print_busy(pids)
            sys.exit(1)

    import uvicorn

    uvicorn.run(
        "src.api.app:app",
        host=HOST,
        port=PORT,
        reload=False,
    )
