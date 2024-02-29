import os

import django


def parse_dot_env(path):
    values = {}
    with open(path) as f:
        lines = f.readlines()
        for line in lines:
            if line and "=" in line:
                s = line.split("=")
                values[s[0].strip()] = s[1].strip()
    return values


def set_env(env_dict):
    for key in env_dict:
        os.environ.setdefault(key, env_dict[key])


def init(env_path):
    # connects to local/remote DB
    set_env(parse_dot_env(env_path))  # first load the productive .env
    set_env(parse_dot_env(".env"))  # load our analysis .env file which changes the SQL user to a less privileged user

    os.environ["DJANGO_SETTINGS_MODULE"] = "backend.backend.settings"
    # os.environ["SQL_HOST"] = "10.32.x.x"  # add remote DB IP if needed
    # os.environ["SQL_PORT"] = "1234"  # remote DB port

    django.setup()  # takes a few moments
