# Utilities to be used on the server
# Created on 12/23/2025
# Last Modified:

import socket
import sys


# Get local ip 
def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_probe:
            s_probe.connect(("8.8.8.8", 80))
            return s_probe.getsockname()[0]
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


# Enhanced bind funcion
def bind_safe(s: socket.socket, local_ip:str ,port: int) -> None:
    try:
        s.bind((local_ip,port))
    except socket.error as e: 
        print(f"Bind failed on {local_ip}:{port} -> {e}")
        sys.exit(1)

# Uses defauld magnitude set above
def create_matrix(magnitude: int, fill: int) -> list: 
    return [[fill]*magnitude for _ in range(magnitude)]