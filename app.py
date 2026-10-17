import os
from pathlib import Path

import yaml
from dotenv import dotenv_values
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

app = FastAPI(title="12-Factor Config Precedence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def coerce(key, value):
    if key in ("port", "workers"):
        return int(value)

    if key == "debug":
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"true", "1", "yes", "on"}

    if isinstance(value, bool):
        return str(value).lower()

    return str(value)


def effective_config(overrides):
    config = DEFAULTS.copy()

    env_name = os.environ.get("APP_ENV", "development")
    yaml_path = BASE_DIR / f"config.{env_name}.yaml"

    if yaml_path.exists():
        with yaml_path.open(encoding="utf-8") as file:
            yaml_config = yaml.safe_load(file) or {}
        config.update(yaml_config)

    # Read .env without changing the process environment.
    env_file = dotenv_values(BASE_DIR / ".env")
    for key, value in env_file.items():
        if value is None:
            continue
        if key == "NUM_WORKERS":
            config["workers"] = value
        elif key.startswith("APP_"):
            config[key[4:].lower()] = value
        else:
            config[key.lower()] = value

    # OS-level APP_* variables override values from files.
    for key, value in os.environ.items():
        if key.startswith("APP_"):
            config[key[4:].lower()] = value

    # Query parameters are highest precedence.
    for key, value in overrides:
        if key:
            config[key.lower()] = value

    config = {key: coerce(key, value) for key, value in config.items()}
    config["api_key"] = "****"
    return config


@app.get("/")
def root():
    return {"message": "Config Precedence API", "docs": "/docs"}


@app.get("/effective-config")
def get_effective_config(set_values: list[str] = Query(default=[], alias="set")):
    overrides = []
    for item in set_values:
        key, separator, value = item.partition("=")
        if separator and key.strip():
            overrides.append((key.strip(), value))
    return effective_config(overrides)
