from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedSeq
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as dq

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.preserve_quotes = True
yaml.representer.ignore_aliases = lambda x: True  # disable anchors

# Wrap lists in CommentedSeq for ruamel features
def make_flow_list(items):
    seq = CommentedSeq(items)
    seq.fa.set_flow_style()  # force inline format [ ... ]
    return seq

ledger_file = "ledger.json"
load_command = {"command": make_flow_list([dq("--ledgerfile"), dq(ledger_file)])}
net_command = {"command": make_flow_list([dq("--net")])}

data = {
    "load_service": load_command,
    "net_service": net_command
}

with open("docker-compose.yml", "w") as f:
    yaml.dump(data, f)

# Also print to console
import sys
yaml.dump(data, sys.stdout)
