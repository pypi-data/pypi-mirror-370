import abc
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
from base64 import b64encode, b64decode
from os import urandom
from typing import Optional, Dict, Any, List

import yaml

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
except Exception:
    AESGCM = None  # type: ignore
    Scrypt = None  # type: ignore

from flexagg.config import config, GPGSecretsConfig
from .panic import panic

_cache: Dict[str, Dict[str, Any]] = {}

# 全局密钥目录常量，供其他模块引用（如内置 CLI）
SECRETS_DIR = pathlib.Path("~/.fa/secrets").expanduser()
if not SECRETS_DIR.exists():
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_gpg_available() -> None:
    if shutil.which("gpg"):
        return
    # Provide platform-specific installation hints
    if sys.platform == "darwin":
        hint = "brew install gnupg pinentry-mac"
    elif sys.platform.startswith("linux"):
        hint = (
            "Debian/Ubuntu: sudo apt-get update && sudo apt-get install -y gnupg pinentry-tty\n"
            "CentOS/RHEL: sudo yum install -y gnupg2 pinentry\n"
            "Arch: sudo pacman -S gnupg pinentry"
        )
    elif sys.platform.startswith("win"):
        hint = "安装 Gpg4win 并确保 gpg 在 PATH"
    else:
        hint = "请安装系统 GPG (gnupg) 并确保 gpg 在 PATH"
    panic("gpg not found in PATH.", details=f"Install GnuPG first.\n{hint}")


def _gpg_env() -> Dict[str, str]:
    env = os.environ.copy()
    if isinstance(config.secrets, GPGSecretsConfig) and config.secrets.home:
        env["GNUPGHOME"] = str(config.secrets.home)
    # Help gpg/pinentry find the controlling TTY in interactive terminals
    try:
        if "GPG_TTY" not in env and sys.stdin.isatty():
            env["GPG_TTY"] = os.ttyname(sys.stdin.fileno())
    except Exception:
        pass
    return env


class SecretsBackend(abc.ABC):
    """所有 Secrets 后端的公共基类。"""

    def load_group(self, group: str) -> Dict[str, Any]:
        raise NotImplementedError

    def save_group(self, group: str, data: Dict[str, Any]) -> None:
        raise NotImplementedError


class PlainSecretsBackend(SecretsBackend):
    def load_group(self, group: str) -> Dict[str, Any]:
        path = SECRETS_DIR / f"{group}.yaml"
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as fp:
            data = yaml.safe_load(fp) or {}
        if not isinstance(data, dict):
            return {}
        return data

    def save_group(self, group: str, data: Dict[str, Any]) -> None:
        path = SECRETS_DIR / f"{group}.yaml"
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(SecretsManager.SECRET_FILE_NOTE)
            yaml.safe_dump(data, fp)


class GPGSecretsBackend(SecretsBackend):
    def load_group(self, group: str) -> Dict[str, Any]:
        _ensure_gpg_available()
        gpg_file = SECRETS_DIR / f"{group}.yaml.gpg"
        if not gpg_file.exists():
            # fallback to plaintext for migration convenience
            return PlainSecretsBackend().load_group(group)

        proc = subprocess.run(
            ["gpg", "--batch", "--yes", "--decrypt", str(gpg_file)],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_gpg_env(),
        )
        if proc.returncode != 0:
            panic(
                f"Failed to decrypt secrets file: {gpg_file}",
                details=proc.stderr.decode(errors="ignore"),
            )
        text = proc.stdout.decode("utf-8", errors="strict")
        data = yaml.safe_load(text) or {}
        if not isinstance(data, dict):
            return {}
        return data

    def save_group(self, group: str, data: Dict[str, Any]) -> None:
        _ensure_gpg_available()
        recipients = config.secrets.recipients if isinstance(config.secrets, GPGSecretsConfig) else []
        if not recipients:
            panic("secrets.gpg.recipients is required when provider is 'gpg'")

        gpg_file = SECRETS_DIR / f"{group}.yaml.gpg"

        payload = yaml.safe_dump(data).encode("utf-8")

        proc = subprocess.run(
            [
                "gpg",
                "--batch",
                "--yes",
                "--encrypt",
                *sum([["--recipient", r] for r in recipients], []),
                "-o",
                str(gpg_file),
            ],
            input=payload,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_gpg_env(),
        )
        if proc.returncode != 0:
            panic(
                f"Failed to encrypt secrets file: {gpg_file}",
                details=proc.stderr.decode(errors="ignore"),
            )
        try:
            os.chmod(gpg_file, 0o600)
        except Exception:
            pass


def get_symmetric_env_hint_lines() -> List[str]:
    return [
        "ENV FA_PASS is required for crypto provider.",
        "Set passphrase (hidden input) and verify before exporting:",
        "========= shell =========",
        "stty -echo; printf 'Passphrase: '; IFS= read -r P; stty echo; printf '\n'; if FA_PASS=\"$P\" fa secrets verify; then export FA_PASS=\"$P\"; else unset FA_PASS; fi; unset P",
        "========= shell end ====",
    ]


def require_symmetric_env_or_panic() -> str:
    val = os.environ.get("FA_PASS")
    if val:
        return val
    panic(*get_symmetric_env_hint_lines())


class CryptoSecretsBackend(SecretsBackend):
    @staticmethod
    def _passphrase_args() -> Dict[str, Any]:
        args: Dict[str, Any] = {}
        # Always require ENV for crypto symmetric mode
        val = require_symmetric_env_or_panic()
        args["passphrase"] = val
        return args

    def load_group(self, group: str) -> Dict[str, Any]:
        enc_file = SECRETS_DIR / f"{group}.yaml.enc"
        if not enc_file.exists():
            return PlainSecretsBackend().load_group(group)
        opts = self._passphrase_args()
        try:
            with open(enc_file, "r", encoding="utf-8") as fp:
                obj = json.load(fp)
            if obj.get("v") != 1 or obj.get("alg") != "AES-256-GCM":
                panic("unsupported crypto container")
            salt = b64decode(obj["salt"])  # 16 bytes
            nonce = b64decode(obj["nonce"])  # 12 bytes
            ct = b64decode(obj["ct"])  # ciphertext+tag
            # derive key (scrypt)
            if Scrypt is None or AESGCM is None:
                panic("cryptography package is required for crypto provider")
            kdf = Scrypt(salt=salt, length=32, n=2 ** 14, r=8, p=1)
            key = kdf.derive(opts["passphrase"].encode("utf-8"))
            data_bytes = AESGCM(key).decrypt(nonce, ct, None)
            data = yaml.safe_load(data_bytes.decode("utf-8")) or {}
        except Exception as e:
            panic(f"Failed to decrypt secrets file: {enc_file}", details=str(e))
        if not isinstance(data, dict):
            return {}
        return data

    def save_group(self, group: str, data: Dict[str, Any]) -> None:
        opts = self._passphrase_args()
        payload = yaml.safe_dump(data).encode("utf-8")
        try:
            if Scrypt is None or AESGCM is None:
                panic("cryptography package is required for crypto provider")
            salt = urandom(16)
            nonce = urandom(12)
            kdf = Scrypt(salt=salt, length=32, n=2 ** 14, r=8, p=1)
            key = kdf.derive(opts["passphrase"].encode("utf-8"))
            ct = AESGCM(key).encrypt(nonce, payload, None)
            obj = {
                "v": 1,
                "alg": "AES-256-GCM",
                "salt": b64encode(salt).decode("ascii"),
                "nonce": b64encode(nonce).decode("ascii"),
                "ct": b64encode(ct).decode("ascii"),
            }
            enc_file = SECRETS_DIR / f"{group}.yaml.enc"
            with open(enc_file, "w", encoding="utf-8") as fp:
                json.dump(obj, fp, separators=(",", ":"))
            os.chmod(enc_file, 0o600)
        except Exception as e:
            panic("Failed to encrypt secrets file (crypto)", details=str(e))


def is_crypto_passphrase_valid() -> bool:
    """仅根据配置中保存的 passphrase_hash 校验 FA_PASS。"""
    if config.secrets.provider != "crypto":
        return True
    try:
        val = require_symmetric_env_or_panic()
    except Exception:
        return False
    # 仅对比 hash
    conf = config.secrets
    phash = conf.passphrase_hash
    return hashlib.sha256(val.encode("utf-8")).hexdigest() == phash


def _get_backend():
    provider = config.secrets.provider  # pydantic guarantees presence
    if provider == "gpg":
        return GPGSecretsBackend()
    if provider == "crypto":
        return CryptoSecretsBackend()
    return PlainSecretsBackend()


class Secrets(str):

    def __new__(cls, key: str, default: Optional[str] = None, refresh: bool = False):
        group, field = key.split("/", 1)
        if refresh or group not in _cache:
            backend = _get_backend()
            _cache[group] = backend.load_group(group)
        secret = _cache[group].get(field, default)
        if secret is None:
            panic(f"Secret {key} not found, Use `fa secrets set {key}` to set it.")
        return super().__new__(cls, str(secret))


class SecretsManager:
    SECRET_FILE_NOTE = "# This file is auto-generated by flexagg, do not edit it manually.\n"

    def __init__(self, key: str):
        self.key = key

    def set(self, value: str):
        group, field = self.key.split("/", 1)
        backend = _get_backend()
        if group not in _cache:
            _cache[group] = backend.load_group(group)
        _cache[group][field] = value
        backend.save_group(group, _cache[group])

    def delete(self):
        group, field = self.key.split("/", 1)
        backend = _get_backend()
        if group not in _cache:
            _cache[group] = backend.load_group(group)
        _cache[group].pop(field, None)
        backend.save_group(group, _cache[group])
