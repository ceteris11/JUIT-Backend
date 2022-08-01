import os
import json


def get_config():
    if os.environ.get("PHASE").lower() == "prod":
        to_open_file = "prod_config.json"
    else:
        to_open_file = "dev_config.json"

    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), to_open_file)) as f:
        config = json.load(f)

    return {"url": config["api_url"], "port": config["port"], "user": config["user"], "pwd": config["pwd"]}
