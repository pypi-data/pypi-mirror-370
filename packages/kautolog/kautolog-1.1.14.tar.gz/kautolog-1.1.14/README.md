# kautolog

[![PyPI version](https://img.shields.io/pypi/v/kautolog.svg)](https://pypi.org/project/kautolog/)

Auto-log **everything you see** in every terminal tab on Kali/Linux using `script(1)`. Captures prompt, commands, output, ANSI colors, and ncurses apps with optional timing/replay, tmux per-pane logs, logrotate, and rclone cloud sync.

## Install

Recommended:

```bash
pipx install kautolog
kautolog install
```

This will:

- Hook into both `~/.bashrc` and `~/.zshrc` for Zsh and Bash auto-logging.
- Install kautolog-replay script into `~/.local/bin`.

### `kautolog install` Options

| Flag | Default | Description |
|------|---------|-------------|
| `--logdir PATH` | `~/terminal-logs` | Custom log output directory |
| `--with-tmux` | `False` | Add autologging to `~/.tmux.conf` |
| `--with-logrotate / --no-logrotate` | `True` | Install user-level logrotate config |
| `--with-sync remote:path` | *(none)* | Enable rclone sync (e.g. `gdrive:kautolog-logs`) |
| `--interval N` | `10` | Sync interval in minutes for systemd timer |

## Replaying logs

To replay a session with timing:

```bash
kautolog replay ~/terminal-logs/2025/08/10/kali-33608-203123
```

To instantly dump the log without delay:

```bash
kautolog replay -i ~/terminal-logs/2025/08/10/kali-33608-203123
```

### `kautolog replay` Options

| Flag / Arg | Description | Notes |
|------------|-------------|-------|
| `<log_base>` | Path to `.log` file or base name (no extension) | Required |
| `-i` | Instant dump (no timing) | Just prints the `.log` file |
| `-d <num>` | Speed divisor (multiplier) | `-d 2` = 2× faster, `-d 10` = 10× faster, `-d 0.5` = 2× slower |
| `-m <secs>`, `--maxdelay <secs>` | Maximum delay between lines | Clamps long pauses (e.g. `-m 0.1`) |
| `--target <secs>` | Normalize total replay to target duration | Auto-computes divisor; also sets `--maxdelay 0.12` if not provided |

## Log Format

Logs are saved to:

```bash
~/terminal-logs/YYYY/MM/DD/hostname-PID-TIMESTAMP.log
~/terminal-logs/YYYY/MM/DD/hostname-PID-TIMESTAMP.timing
```

If `--with-tmux` is used, each tmux pane logs independently.

## Enabling Automatic Log Cleanup (Optional)

By default, `kautolog install` places a logrotate config at:

```bash
~/.config/logrotate.d/terminal-logs
```

Most systems **do not run** logrotate from this location.  
To enable automatic log cleanup, copy it to the system logrotate directory:

```bash
sudo cp ~/.config/logrotate.d/terminal-logs /etc/logrotate.d/terminal-logs
```

This will:

- Rotate logs daily
- Keep 14 days of logs
- Compress old logs
- Prevent unlimited disk usage

## Uninstall

```bash
kautolog uninstall
```

Removes all shell hooks and scripts cleanly.

If you installed using pipx:

```bash
pipx uninstall kautolog
```

## License

The scripts and documentation in this project are released under the [MIT License](https://github.com/marksowell/kautolog/blob/main/LICENSE)
