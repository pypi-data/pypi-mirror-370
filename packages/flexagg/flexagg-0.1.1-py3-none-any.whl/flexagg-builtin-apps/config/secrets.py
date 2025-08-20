import hashlib
import pathlib
import os
import shutil
import subprocess
import sys
from getpass import getpass
from pathlib import Path
from typing import Optional, List, Dict, Any

import typer
from typer import Typer, Option

from flexagg.config import (
    config,
    PlaintextSecretsConfig,
    GPGSecretsConfig,
    CryptoSecretsConfig,
)
from flexagg.utils import echo, panic
from flexagg.utils.secrets import (
    get_symmetric_env_hint_lines,
    PlainSecretsBackend,
    GPGSecretsBackend,
    CryptoSecretsBackend,
    SECRETS_DIR, SecretsBackend,
)

app = Typer()


def _gpg_available() -> bool:
    return shutil.which("gpg") is not None


def _platform_install_hint() -> str:
    if sys.platform == "darwin":
        return "brew install gnupg pinentry-mac"
    if sys.platform.startswith("linux"):
        return (
            "Debian/Ubuntu: sudo apt-get update && sudo apt-get install -y gnupg pinentry-tty\n"
            "CentOS/RHEL: sudo yum install -y gnupg2 pinentry\n"
            "Arch: sudo pacman -S gnupg pinentry"
        )
    if sys.platform.startswith("win"):
        return "安装 Gpg4win 并确保 gpg 在 PATH"
    return "请安装系统 GPG (gnupg) 并确保 gpg 在 PATH"


def _gpg_env() -> dict:
    env = dict(os.environ)
    if isinstance(config.secrets, GPGSecretsConfig) and config.secrets.home:
        env["GNUPGHOME"] = str(config.secrets.home)
    return env


def _iter_secret_groups() -> set:
    d = SECRETS_DIR
    d.mkdir(parents=True, exist_ok=True)
    groups: set = set()
    for p in d.glob("*.yaml"):
        groups.add(p.stem)
    for p in d.glob("*.yaml.gpg"):
        if p.name.endswith(".yaml.gpg"):
            groups.add(p.name[:-9])  # strip .yaml.gpg
    for p in d.glob("*.yaml.enc"):
        if p.name.endswith(".yaml.enc"):
            groups.add(p.name[:-9])  # strip .yaml.enc
    return groups


def _get_backend(secrets_config=None) -> SecretsBackend:
    if secrets_config is None:
        secrets_config = config.secrets
    if isinstance(secrets_config, GPGSecretsConfig):
        return GPGSecretsBackend()
    if isinstance(secrets_config, CryptoSecretsConfig):
        return CryptoSecretsBackend()
    return PlainSecretsBackend()


class SecretsMigrator:
    """
    封装密钥文件迁移流程：预检查 → 写入 → 删除。

    - 仅删除被读取(load)的源文件；
    - 写入前检查所有目标文件不存在（除非与源相同）；
    - 失败回滚，保证原子性。
    """

    def __init__(self, new_config: Any) -> None:
        self.new_config = new_config
        self.old_config = config.secrets
        self.current_backend = _get_backend()
        self.new_backend = _get_backend(new_config)
        self.groups = sorted(_iter_secret_groups())
        self.loaded: Dict[str, Dict[str, Any]] = {}
        self.src_map: Dict[str, pathlib.Path] = {}
        self.dst_map: Dict[str, pathlib.Path] = {}
        self.created_targets: List[pathlib.Path] = []

    def _src_path(self, group: str) -> pathlib.Path:
        plain = SECRETS_DIR / f"{group}.yaml"
        gpgf = SECRETS_DIR / f"{group}.yaml.gpg"
        encf = SECRETS_DIR / f"{group}.yaml.enc"
        if isinstance(self.old_config, GPGSecretsConfig):
            return gpgf if gpgf.exists() else plain
        if isinstance(self.old_config, CryptoSecretsConfig):
            return encf if encf.exists() else plain
        return plain

    def _dst_path(self, group: str) -> pathlib.Path:
        if isinstance(self.new_config, PlaintextSecretsConfig):
            return SECRETS_DIR / f"{group}.yaml"
        if isinstance(self.new_config, GPGSecretsConfig):
            return SECRETS_DIR / f"{group}.yaml.gpg"
        return SECRETS_DIR / f"{group}.yaml.enc"

    def preflight(self) -> None:
        read_errors: List[str] = []
        conflict_errors: List[str] = []
        for group in self.groups:
            try:
                data = self.current_backend.load_group(group)
                self.loaded[group] = data
            except Exception as e:
                read_errors.append(f"failed to load group '{group}': {e}")
                continue
            src = self._src_path(group)
            dst = self._dst_path(group)
            self.src_map[group] = src
            self.dst_map[group] = dst
            if dst.exists() and dst.resolve() != src.resolve():
                conflict_errors.append(f"target already exists: {dst}")
        if read_errors:
            panic("read check before migration failed:", *read_errors)
        if conflict_errors:
            panic("preflight conflict check failed:", *conflict_errors)

    def write_all(self) -> None:
        try:
            for group, data in self.loaded.items():
                src = self.src_map[group]
                dst = self.dst_map[group]
                if src.resolve() == dst.resolve():
                    continue
                config.secrets = self.new_config  # type: ignore[assignment]
                self.new_backend.save_group(group, data)  # type: ignore[attr-defined]
                if not dst.exists():
                    raise RuntimeError(f"expected target not created: {dst}")
                self.created_targets.append(dst)
        except Exception as e:
            for p in self.created_targets:
                try:
                    if p.exists():
                        p.unlink()
                except Exception:
                    pass
            config.secrets = self.old_config
            panic(f"failed to save in new provider: {e}")
        finally:
            config.secrets = self.old_config

    def cleanup_sources(self) -> None:
        for group in self.loaded.keys():
            src = self.src_map[group]
            dst = self.dst_map[group]
            if src.resolve() == dst.resolve():
                continue
            if src.exists():
                try:
                    src.unlink()
                except Exception:
                    echo.warning(f"failed to delete source file: {src}")

    def run(self) -> None:
        self.preflight()
        self.write_all()
        self.cleanup_sources()


@app.command("show")
def show():
    """Show current secrets provider status"""
    if isinstance(config.secrets, GPGSecretsConfig):
        echo.info("provider: gpg")
        echo.print(f"recipients: {config.secrets.recipients}")
        echo.print(f"use_agent: {config.secrets.use_agent}")
        echo.print(f"home: {config.secrets.home}")

        # gpg availability
        if _gpg_available():
            try:
                proc = subprocess.run(["gpg", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                ver = proc.stdout.decode(errors="ignore").splitlines()[0] if proc.returncode == 0 else "unknown"
                echo.print(f"gpg: available ({ver})")
            except Exception:  # noqa
                echo.print("gpg: available")
        else:
            echo.print("gpg: not found")
    elif isinstance(config.secrets, CryptoSecretsConfig):
        echo.info("provider: crypto")
    else:
        echo.info("provider: plaintext")


@app.command("set-plaintext")
def set_plaintext():
    """Switch to plaintext provider and migrate all secret files (decrypt)"""
    # Confirm migration
    proceed = typer.confirm(
        "This will decrypt and rewrite all encrypted secret files to plaintext. Proceed?",
        default=False,
    )
    if not proceed:
        echo.warning("aborted")
        raise typer.Exit(1)

    new_conf = PlaintextSecretsConfig()
    SecretsMigrator(new_conf).run()
    config.secrets = new_conf
    config.save()
    echo.success("secrets provider set to plaintext")


@app.command("set-gpg")
def set_gpg(
    recipients: List[str] = Option(..., "--recipient", help="Repeat to add multiple recipients", metavar="RECIPIENT"),
    home: Optional[Path] = Option(None, "--home", help="GNUPGHOME path"),
    use_agent: bool = Option(True, "--use-agent/--no-use-agent", help="Use gpg-agent"),
):
    """Switch to GPG asymmetric provider and migrate all plaintext files (encrypt)"""
    if not _gpg_available():
        echo.error("gpg not found. Please install first:")
        echo.print(_platform_install_hint())
        raise typer.Exit(1)

    # Pre-validate the provided values without saving
    errs = []
    if not recipients:
        errs.append("recipients is empty. at least one --recipient is required")
    if home and not home.exists():
        errs.append(f"GNUPGHOME not exists: {home}")
    # Check each recipient exists in keyring (with candidate GNUPGHOME)
    env = dict(os.environ)
    if home:
        env["GNUPGHOME"] = str(home)
    for r in recipients:
        proc = subprocess.run([
            "gpg", "--list-keys", "--with-colons", r
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        if proc.returncode != 0:
            errs.append(f"recipient key not found in keyring: {r}")
    if errs:
        panic(*errs)

    # Confirm migration
    proceed = typer.confirm(
        "This will encrypt and rewrite all plaintext secret files. If any recipient's private key is lost, decryption will be impossible. Proceed?",
        default=False,
    )
    if not proceed:
        echo.warning("aborted")
        raise typer.Exit(1)

    # Save after validation passed and migrate
    new_conf = GPGSecretsConfig(recipients=recipients, use_agent=use_agent, home=home)
    SecretsMigrator(new_conf).run()
    config.secrets = new_conf
    config.save()
    echo.success("gpg config saved")


@app.command("set-crypto")
def set_crypto():
    """Switch to built-in crypto (AES-256-GCM) provider and migrate all plaintext files (encrypt)"""
    # Require ENV first; if missing, guide user
    val = os.environ.get("FA_PASS")
    if not val:
        panic(*get_symmetric_env_hint_lines())
    # Retype to confirm
    p2 = getpass("Retype passphrase for confirmation (hidden): ")
    if val != p2:
        panic("passphrase mismatch")

    # Confirm migration
    proceed = typer.confirm(
        "This will encrypt and rewrite all plaintext secret files. If the passphrase is lost, decryption will be impossible. Proceed?",
        default=False,
    )
    if not proceed:
        echo.warning("aborted")
        raise typer.Exit(1)

    # Save after validation passed and migrate
    phash = hashlib.sha256(val.encode("utf-8")).hexdigest()
    new_conf = CryptoSecretsConfig(passphrase_hash=phash)
    SecretsMigrator(new_conf).run()
    config.secrets = new_conf
    config.save()
    echo.success("crypto config saved")
