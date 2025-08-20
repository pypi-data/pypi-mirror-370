from jinja2 import Template

# Data for rendering
context = {
    "service_name": "rippled",
    "image": "ripple/rippled:latest",
    "command": ["--ledgerfile", "ledger.json"],
    "healthcheck": {
        "test": ["CMD", "/usr/bin/curl", "--insecure", "https://localhost:51235/health"],
        "interval": 5,
        "start_period": 45,
    }
}

with open("docker-compose.yml.j2") as f:
    template = Template(f.read())

output = template.render(**context)

with open("docker-compose.yml", "w") as f:
    f.write(output)

print(output)
