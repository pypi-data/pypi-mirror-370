from mako.template import Template
from pathlib import Path
from types import SimpleNamespace
# # mytemplate = Template(filename='mako.template')
# mytemplate = Template(filename='docker-compose.yml.mako')
# # x = SimpleNamespace(x=[1,2,3])
# print(mytemplate.render())

from mako.template import Template
from mako.lookup import TemplateLookup

services = {
    "app": {
        "image": "my-python-app:dev",
        "command": '["uv","run","python","-m","myapp"]',
        "environment": {"PYTHONUNBUFFERED": "1"},
        "ports": ["8000:8000"],
    },
    "worker": {
        "image": "my-python-app:dev",
        "command": '["uv","run","python","-m","myapp.worker"]',
        "environment": {"PYTHONUNBUFFERED": "1"},
        "ports": [],
    },
}
lookup = TemplateLookup(directories=["."])
tmpl = Template(filename="docker-compose.yml.mako", lookup=lookup)
custom_net = {"name0": {"beans": "bro"}}
custom_net = {"whut":"huh"}
# name = 'whoa'
c = {
    "stack_name":"python-stack",
    "services":services,
    "volumes": [
        "pgdata",
        "redisdata"
    ],
    "networks": custom_net,
    "net_name": "butts"
}

rendered = tmpl.render(**c)

open("docker-compose.yml", "w").write(rendered)
