# >>> KAUTOLOG START >>>
# Auto logging (text + timing) for every interactive Bash shell
if [[ $- == *i* ]] && [[ -t 1 ]] && [[ -z "$UNDER_SCRIPT" ]]; then
  export UNDER_SCRIPT=1
  base="$HOME/terminal-logs/$(date +%Y)/$(date +%m)/$(date +%d)"
  mkdir -p "$base"
  logbase="$base/$(hostname)-$$-$(date +%H%M%S)"
  # util-linux script wants timing as -tFILE (no space)
  exec /usr/bin/script -fqe -t"$logbase.timing" "$logbase.log"
fi

# Optional: add a timestamp + CWD marker before each prompt (safe + idempotent)
_kautolog_prompt() {
  [[ -n "$logbase" ]] || return 0
  printf "\n# [%s] %s\n" "$(date -Is)" "$(pwd)" >> "$logbase.log" 2>/dev/null
}
case "$PROMPT_COMMAND" in
  *"_kautolog_prompt"*) : ;;
  *) PROMPT_COMMAND="_kautolog_prompt; $PROMPT_COMMAND" ;;
esac
# <<< KAUTOLOG END <<<
