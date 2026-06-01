# ──────────────────────────────────────────────────
# .zshrc — ZSH configuration
# ──────────────────────────────────────────────────

# ── History ─────────────────────────────────────
HISTSIZE=10000
SAVEHIST=10000
HISTFILE=~/.zsh_history
setopt HIST_IGNORE_ALL_DUPS
setopt HIST_FIND_NO_DUPS
setopt SHARE_HISTORY

# ── Prompt ──────────────────────────────────────
autoload -Uz promptinit && promptinit
PROMPT='%F{cyan}%n%f@%F{green}%m%f %F{yellow}%~%f %# '

# ── Key bindings ────────────────────────────────
bindkey -e

# ── Completion ──────────────────────────────────
autoload -Uz compinit && compinit
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'

# ── Aliases ─────────────────────────────────────
[ -f ~/.aliases ] && source ~/.aliases

# ── NVM ─────────────────────────────────────────
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && source "$NVM_DIR/bash_completion"

# ── PATH additions ──────────────────────────────
export PATH="$HOME/.local/bin:$PATH"

# ── FZF ─────────────────────────────────────────
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh
