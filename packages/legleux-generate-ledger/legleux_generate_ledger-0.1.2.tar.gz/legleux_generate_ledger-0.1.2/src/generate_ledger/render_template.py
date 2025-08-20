from string import Template
# import yaml
stack_name = "antithesis"
val_name = "val"
app_image = "legleux/rippled:latest"
# default_entrypoint = ["rippled"]

with open("docker-compose.yml.tpl") as f:
    t = Template(f.read())

# c = {"name": val_name}
num_vals = 3
vals = []
depends = "fuck"
for i in range(num_vals):
    v = {
        "name": f"{val_name}{i}",
        "hostname": f"{val_name}{i}",
        "container_name": val_name,
        "image": app_image,
    }
    # vals.append({
        # "entrypoint": default_entrypoint,
    # })
    if i == 0:
        v["entrypoint"] = f'v["entrypoint-{i}"]'
    else:
        v["depends"] = "depends"
    vals.append(v)
validators = "\n".join([f"{val}" for val in vals ])
context = dict(
    stack_name="butts",
    val_name=val_name,
    validators=validators,
    container_name=val_name,
    # app_image=app_image,
    # app_command='["python","-m","myapp"]',
    # app_env="development",
    # app_port_host="8000",
    # app_port_container="8000",
)
# rendered = t.substitute(**context)

context = {
    "stack_name": "cool",
    "val_name": "val_name",
    "validators": ["1:a", "2:b"],
    }
rendered = t.substitute(**context)
# yaml.safe_load(rendered)  # validate
open("docker-compose.yml", "w").write(rendered)
