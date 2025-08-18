import os, sys, re, subprocess, shlex
from pathlib import Path
from typing import Optional

PKG_DIR = Path(__file__).resolve().parent
HOME = Path.home()
BASHRC = HOME / ".bashrc"
ZSHRC  = HOME / ".zshrc"
TMUX_CONF = HOME / ".tmux.conf"
CONFIG_DIR = HOME / ".config"
LOGROTATE_USER_DIR = CONFIG_DIR / "logrotate.d"
SYSTEMD_USER_DIR = CONFIG_DIR / "systemd" / "user"

MARKER_START = "# >>> KAUTOLOG START >>>"
MARKER_END   = "# <<< KAUTOLOG END <<<"

def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""

def _write_text(path: Path, data: str, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")
    os.chmod(path, mode)

def _append_unique(file: Path, block: str, marker_start: str, marker_end: str) -> bool:
    cur = _read_text(file)
    if marker_start in cur and marker_end in cur:
        return False
    # ensure exactly one blank line before our block
    if not cur.endswith("\n\n"):
        cur = cur.rstrip("\n") + "\n\n"
    new = cur + block.rstrip() + "\n"
    _write_text(file, new)
    return True

def _remove_block(file: Path, marker_start: str, marker_end: str) -> bool:
    cur = _read_text(file)
    if marker_start not in cur or marker_end not in cur:
        return False
    pattern = re.compile(re.escape(marker_start) + r".*?" + re.escape(marker_end), re.DOTALL)
    new = pattern.sub("", cur).rstrip() + "\n"
    _write_text(file, new)
    return True

def install_rc_files(logdir: Optional[str]) -> None:
    if logdir is None:
        logdir = str(HOME / "terminal-logs")
    # Bash
    bash_block = (PKG_DIR / "templates" / "bashrc_autologger.sh").read_text(encoding="utf-8")
    bash_block = bash_block.replace("__KAUTOLOG_LOGDIR__", shlex.quote(str(Path(logdir).expanduser())))
    _append_unique(BASHRC, bash_block, MARKER_START, MARKER_END)
    # Zsh
    zsh_block = (PKG_DIR / "templates" / "zshrc_autologger.sh").read_text(encoding="utf-8")
    zsh_block = zsh_block.replace("__KAUTOLOG_LOGDIR__", shlex.quote(str(Path(logdir).expanduser())))
    _append_unique(ZSHRC, zsh_block, MARKER_START, MARKER_END)

def install_tmux() -> None:
    tmux_block = (PKG_DIR / "templates" / "tmux_autologger.conf").read_text(encoding="utf-8")
    _append_unique(TMUX_CONF, tmux_block, MARKER_START, MARKER_END)

def install_logrotate(logdir: Optional[str]) -> None:
    if logdir is None:
        logdir = str(HOME / "terminal-logs")
    absdir = str(Path(logdir).expanduser().resolve())
    tpl = (PKG_DIR / "templates" / "logrotate_terminal-logs").read_text(encoding="utf-8")
    tpl = tpl.replace("__KAUTOLOG_ABS_LOGDIR__", absdir).replace("__USER__", os.environ.get("USER", "user"))
    _write_text(LOGROTATE_USER_DIR / "terminal-logs", tpl)

def _systemd_available() -> bool:
    try:
        subprocess.run(["systemctl", "--user", "--version"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def install_systemd_sync(logdir: Optional[str], remote: str, interval_min: int) -> None:
    if not _systemd_available():
        print("[kautolog] systemd --user unavailable; skipping sync timer.", file=sys.stderr)
        return
    if logdir is None:
        logdir = str(HOME / "terminal-logs")
    absdir = str(Path(logdir).expanduser().resolve())

    service_tpl = (PKG_DIR / "templates" / "systemd" / "autologger-rclone-sync.service").read_text(encoding="utf-8")
    timer_tpl = (PKG_DIR / "templates" / "systemd" / "autologger-rclone-sync.timer").read_text(encoding="utf-8")

    service = service_tpl.replace("__KAUTOLOG_ABS_LOGDIR__", absdir).replace("__KAUTOLOG_REMOTE__", remote)
    timer = timer_tpl.replace("__KAUTOLOG_INTERVAL__", str(interval_min))

    service_path = SYSTEMD_USER_DIR / "autologger-rclone-sync.service"
    timer_path = SYSTEMD_USER_DIR / "autologger-rclone-sync.timer"

    _write_text(service_path, service, mode=0o644)
    _write_text(timer_path, timer, mode=0o644)

    subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    subprocess.run(["systemctl", "--user", "enable", "--now", "autologger-rclone-sync.timer"], check=False)

def uninstall_systemd_sync() -> None:
    if _systemd_available():
        subprocess.run(["systemctl", "--user", "disable", "--now", "autologger-rclone-sync.timer"], check=False)
        subprocess.run(["systemctl", "--user", "disable", "--now", "autologger-rclone-sync.service"], check=False)
    try:
        (SYSTEMD_USER_DIR / "autologger-rclone-sync.timer").unlink(missing_ok=True)
        (SYSTEMD_USER_DIR / "autologger-rclone-sync.service").unlink(missing_ok=True)
    except Exception:
        pass

def install_helpers() -> None:
    """Install the kautolog-replay helper to ~/.local/bin."""
    bin_dir = HOME / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    src = PKG_DIR / "templates" / "kautolog-replay"
    dst = bin_dir / "kautolog-replay"
    data = src.read_text(encoding="utf-8")
    _write_text(dst, data, mode=0o755)
    if str(bin_dir) not in os.environ.get("PATH", "").split(":"):
        print(f"[kautolog] Note: {bin_dir} is not on PATH. Add this to your shell rc:")
        print('  export PATH="$HOME/.local/bin:$PATH"')

def install_all(logdir: Optional[str], enable_tmux: bool, enable_logrotate: bool, rclone_remote: Optional[str], sync_interval_min: int) -> bool:
    try:
        install_rc_files(logdir)
        install_helpers()
        if enable_tmux:
            install_tmux()
        if enable_logrotate:
            install_logrotate(logdir)
        if rclone_remote:
            install_systemd_sync(logdir, rclone_remote, sync_interval_min)
        print("[kautolog] Installed. Open a new terminal session to start logging (Zsh or Bash).")
        return True
    except Exception as e:
        print(f"[kautolog] Install error: {e}", file=sys.stderr)
        return False

def uninstall_all() -> bool:
    try:
        _remove_block(BASHRC, MARKER_START, MARKER_END)
        _remove_block(ZSHRC, MARKER_START, MARKER_END)
        _remove_block(TMUX_CONF, MARKER_START, MARKER_END)
        try:
            (Path.home() / ".config" / "logrotate.d" / "terminal-logs").unlink(missing_ok=True)
        except Exception:
            pass
        uninstall_systemd_sync()
        try:
            (HOME / ".local" / "bin" / "kautolog-replay").unlink(missing_ok=True)
        except Exception:
            pass
        print("[kautolog] Uninstalled. Remove ~/terminal-logs if you also want to delete logs.")
        return True
    except Exception as e:
        print(f"[kautolog] Uninstall error: {e}", file=sys.stderr)
        return False

def get_status() -> str:
    lines = []
    lines.append("kautolog status")
    try:
        bashrc_txt = BASHRC.read_text(encoding="utf-8", errors="ignore")
        lines.append(f"bashrc: {'present' if MARKER_START in bashrc_txt else 'absent'}")
    except Exception:
        lines.append("bashrc: unknown")
    try:
        zshrc_txt = ZSHRC.read_text(encoding="utf-8", errors="ignore")
        lines.append(f"zshrc: {'present' if MARKER_START in zshrc_txt else 'absent'}")
    except Exception:
        lines.append("zshrc: unknown")
    try:
        tmux_txt = TMUX_CONF.read_text(encoding="utf-8", errors="ignore")
        lines.append(f"tmux: {'present' if MARKER_START in tmux_txt else 'absent'}")
    except Exception:
        lines.append("tmux: unknown")

    # systemd timer status
    if _systemd_available():
        out = subprocess.run(["systemctl", "--user", "is-enabled", "autologger-rclone-sync.timer"],
                             capture_output=True, text=True)
        enabled = (out.returncode == 0 and out.stdout.strip() == "enabled")
        lines.append(f"sync timer: {'enabled' if enabled else 'disabled'}")
    else:
        lines.append("sync timer: unavailable")

    # recent logs
    logdir = Path.home() / "terminal-logs"
    if logdir.exists():
        recent = sorted(logdir.rglob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
        lines.append("recent logs:")
        for p in recent:
            lines.append(f"  - {p}")
    else:
        lines.append("recent logs: (none yet)")
    return "\n".join(lines)
