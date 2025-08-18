# >>> KAUTOLOG START >>>
# Auto logging (text + timing) for every interactive Zsh shell
if [[ -o interactive ]] && [[ -t 1 ]] && [[ -z "$UNDER_SCRIPT" ]]; then
  export UNDER_SCRIPT=1
  base="$HOME/terminal-logs/$(date +%Y)/$(date +%m)/$(date +%d)"
  mkdir -p "$base"
  export logbase="$base/$(hostname)-$$-$(date +%H%M%S)"
  exec /usr/bin/script -fqe -t"$logbase.timing" "$logbase.log"
fi
# <<< KAUTOLOG END <<<
