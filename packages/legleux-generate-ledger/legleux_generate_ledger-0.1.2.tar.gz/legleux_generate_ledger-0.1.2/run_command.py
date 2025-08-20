import json
from urllib import request
from urllib.error import HTTPError, URLError
import sys

ip = "172.17.0.7"
url =  f"http://{ip}:5005"


def make_payment(src, dst, secret, amt):
    return {
        "method": "submit",
        "params": [{
            "secret": secret,
            "tx_json": {
                "TransactionType": "Payment",
                "Account": src,
                "Destination": dst,
                "Amount": str(amt),
            }
        }]
    }

def pay(src, dst, secret, amt):
    """Get the status of the ledger"""
    payment_txn = make_payment(src, dst, secret, amt)
    req = request.Request(url, data=json.dumps(payment_txn).encode())
    try:
        data = json.loads(request.urlopen(req, timeout=3).read())
        result = data["result"]
        print(f"--> returning {result}", file=sys.stderr)
    except (HTTPError, URLError, TimeoutError) as err:
        result = {"exception": str(err), "status": f"node not running"}
    except Exception as err:
        result = {"exception": str(err), "status": f"exception"}

accounts = [
    [
     "rBuzwZcJRArXLVTFWPEJGTMeFECBYvpAFy",
     "ssK3VjRegtAYmgMyKGUKKFNFCQEN7"
    ],
    [
    "rPdTJanihCjjGsuYmDjTpb89LwfBGMQhX9",
    "snNNecbbfJ5cAheXhJYayXzAgY4jX"
    ]
]
src = accounts[0][0]
secret = accounts[0][1]
dst = accounts[1][0]
amt = "10000000"

pay(src, dst, secret, amt)
