from pathlib import Path
import json

somefile = Path("/testnet/data")
data = {"cool": "beans"}


def generate_testnet():
    print(Path(".").resolve())
    with somefile.open(mode="w", encoding="utf-8") as f:
        json.dump(data, f)
    return "wtf generate_testnet"
