#!/usr/bin/env bash
# Launch cozy-cats in a bottom tmux pane.
# Usage: bash cozy-cats/launch.sh [height]   (default: 32)
#
# Mouse: click on the cozy-cats pane to interact, click your code pane to type.
# tmux mouse mode is enabled so pane switching works via click.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HEIGHT="${1:-32}"
CMD="python3 '$SCRIPT_DIR/cozy-cats.py' --height $HEIGHT"

# Enable tmux mouse mode so you can click between panes
enable_mouse() {
    tmux set-option -g mouse on 2>/dev/null
}

if [ -z "$TMUX" ]; then
    echo "Starting tmux with cozy-cats docked at the bottom..."
    echo "  Click the bottom pane to interact with cats."
    echo "  Click the top pane to type/code."
    echo "  Ctrl+C in the cat pane to quit."
    tmux new-session -d -s cozy-cats -x "$(tput cols)" -y "$(tput lines)" \; \
        set-option -g mouse on \; \
        split-window -v -l "$HEIGHT" "$CMD" \; \
        select-pane -t 0 \; \
        attach
else
    enable_mouse
    tmux split-window -v -l "$HEIGHT" "$CMD"
fi
