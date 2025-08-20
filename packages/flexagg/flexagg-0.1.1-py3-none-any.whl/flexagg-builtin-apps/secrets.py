import hashlib
import os
import subprocess
import sys

import typer
from typer import Typer, Argument
from typing_extensions import Annotated

from flexagg.config import config, GPGSecretsConfig, CryptoSecretsConfig
from flexagg.utils import SecretsManager, echo
from flexagg.utils.secrets import require_symmetric_env_or_panic, get_symmetric_env_hint_lines, SECRETS_DIR, \
    is_crypto_passphrase_valid

app = Typer()


def key_validator(key: str) -> str:
    if key.count("/") != 1:
        echo.error("key must contain exactly one '/', like 'group/secret_name'")
        raise typer.Exit(1)
    return key


@app.command(name="set")
def set_secret(
    key: Annotated[
        str,
        Argument(help="set a secret key, like 'group/secret_name'", callback=key_validator),
    ],
):
    """Set a secret value by key"""
    # Pre-check for symmetric mode: require ENV before prompting input
    if isinstance(config.secrets, CryptoSecretsConfig):
        # Validate ENV correctness before prompting secret
        if not is_crypto_passphrase_valid():
            echo.error("crypto passphrase invalid or not set.", *get_symmetric_env_hint_lines())
            raise typer.Exit(1)
    value = typer.prompt("Secret(hidden input)", hide_input=True, show_default=False)
    SecretsManager(key).set(value)
    echo.success(f"secret {key} set successfully")


def _gpg_env() -> dict:
    env = dict(os.environ)
    if isinstance(config.secrets, GPGSecretsConfig) and getattr(config.secrets, "home", None):
        env["GNUPGHOME"] = str(config.secrets.home)
    # Help gpg/pinentry find controlling TTY
    try:
        if "GPG_TTY" not in env and sys.stdin.isatty():
            env["GPG_TTY"] = os.ttyname(sys.stdin.fileno())
    except Exception:
        pass
    return env


@app.command(name="unlock")
def secret_unlock():
    """Pre-decrypt to warm up gpg passphrase cache (plaintext/symmetric not supported)"""
    if isinstance(config.secrets, GPGSecretsConfig):
        enc_files = sorted(SECRETS_DIR.glob("*.yaml.gpg"))
        if not enc_files:
            echo.warning("no encrypted secret files found under ~/.fa/secrets")
            raise typer.Exit(0)
        target = enc_files[0]
        cmd = ["gpg", "--yes", "--decrypt", str(target)]
        proc = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            env=_gpg_env(),
        )
        if proc.returncode != 0:
            echo.error("unlock failed", proc.stderr.decode(errors="ignore"))
            raise typer.Exit(proc.returncode or 1)
        echo.success(f"unlocked via {target.name}; passphrase is now cached by gpg-agent (if enabled)")
        return

    if isinstance(config.secrets, CryptoSecretsConfig):
        # Symmetric mode does not use agent; guide user to set ENV
        echo.error(
            "crypto provider does not support unlock.",
            "Set passphrase via ENV instead:",
            *get_symmetric_env_hint_lines()[2:],
        )
        raise typer.Exit(1)

    echo.error("plaintext mode: enable encryption to unlock")
    raise typer.Exit(1)


@app.command(name="lock")
def secret_lock():
    """Clear gpg-agent cache (only for gpg provider)"""
    if isinstance(config.secrets, GPGSecretsConfig):
        subprocess.run(["gpgconf", "--kill", "gpg-agent"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["gpgconf", "--launch", "gpg-agent"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        echo.success("gpg-agent cache cleared (agent restarted)")
        return
    if isinstance(config.secrets, CryptoSecretsConfig):
        echo.error(
            "crypto provider does not support lock.",
            "Unset the passphrase ENV instead:",
            "========= shell =========",
            "unset FA_PASS",
            "========= shell end ====",
        )
        raise typer.Exit(1)
    echo.error("plaintext mode: nothing to lock")
    raise typer.Exit(1)


@app.command(name="verify")
def secret_verify():
    """Verify crypto passphrase by comparing hash (crypto provider only)"""
    if isinstance(config.secrets, CryptoSecretsConfig):
        val = require_symmetric_env_or_panic()
        phash = config.secrets.passphrase_hash
        if hashlib.sha256(val.encode("utf-8")).hexdigest() == phash:
            echo.success("verification passed")
            return
        echo.error("verification failed")
        raise typer.Exit(1)
    echo.success("verification passed")
