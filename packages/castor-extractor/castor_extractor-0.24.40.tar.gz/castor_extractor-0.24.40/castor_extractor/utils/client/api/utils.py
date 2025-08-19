from typing import Optional


def build_url(host: Optional[str], endpoint: str):
    if not host:
        return endpoint
    if not host.startswith("https://"):
        host = "https://" + host
    return f"{host.strip('/')}/{endpoint}"
