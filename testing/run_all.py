import subprocess
import sys
import time
from pathlib import Path


def main():
    project_root = Path(__file__).parent
    create_new_console = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)

    # Start server
    server = subprocess.Popen(
        [sys.executable, "server.py"],
        cwd=project_root,
        creationflags=create_new_console,
    )
    time.sleep(1.0)  # small delay to let the server start listening

    # Start two clients
    clients = []
    for _ in range(2):
        p = subprocess.Popen(
            [sys.executable, "client.py"],
            cwd=project_root,
            creationflags=create_new_console,
        )
        clients.append(p)
        time.sleep(0.3)

    print(f"Server PID: {server.pid}")
    print(f"Client PIDs: {[p.pid for p in clients]}")
    print("All processes started. Press Ctrl+C to exit the launcher (children keep running).")

    try:
        server.wait()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

