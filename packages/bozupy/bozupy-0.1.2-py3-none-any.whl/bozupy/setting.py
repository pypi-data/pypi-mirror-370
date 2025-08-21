import os
import logging
from pathlib import Path

import dotenv

_env_file: Path = Path("~/.env").expanduser().absolute()
if _env_file.exists() and os.environ.get("NO_LOAD_DEFAULT_DOTENV", "false").lower() != "true":
    dotenv.load_dotenv(_env_file, override=True)
_current_env_file: Path = Path(os.getcwd()) / ".env"
if _current_env_file.exists():
    dotenv.load_dotenv(_current_env_file, override=True)
_filepaths: list[Path] = [Path(fp).expanduser().absolute() for fp in os.environ.get("DOT_ENV_FILES", "").split(",") if fp]
for _filepath in _filepaths:
    if _filepath.exists():
        dotenv.load_dotenv(_filepath, override=True)

BOZUPY_VERSION: str = "0.1.2"

logging.debug(f"BOZUPY_VERSION: {BOZUPY_VERSION}")
USER_AGENT: str = os.environ.get("USER_AGENT", f"bozupy:v{BOZUPY_VERSION}")
DEFAULT_CYBOZU_SUBDOMAIN: str = os.environ.get("CYBOZU_SUBDOMAIN", "")
DEFAULT_CYBOZU_USERNAME: str = os.environ.get("CYBOZU_USERNAME", "")
DEFAULT_CYBOZU_PASSWORD: str = os.environ.get("CYBOZU_PASSWORD", "")
_is_dev_domain: bool = os.environ.get("CYBOZU_IS_DEV_DOMAIN", "false").lower() == "true"
DEFAULT_OTP_SECRET: str = os.environ.get("CYBOZU_OTP_SECRET", "")
DEFAULT_CYBOZU_REGION: str = os.environ.get("CYBOZU_REGION", "jp").lower()
DEFAULT_HOST: str = DEFAULT_CYBOZU_SUBDOMAIN + "." + ("cybozu-dev" if _is_dev_domain else "cybozu") + ".com"

DEFAULT_APP_TOKENS: dict[int, str] = {}
for key, value in os.environ.items():
    if key.startswith("KINTONE_APP_TOKEN_"):
        try:
            app_id: int = int(key.split("_")[3])
        except ValueError:
            logging.warning(f"Invalid app_id: {key}")
            continue
        DEFAULT_APP_TOKENS[app_id] = value
        logging.debug(f"App token for app_id {app_id} is set")
