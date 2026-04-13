#!/usr/bin/env bash
# Launch leafy-loft in a bottom tmux pane.
# Usage: bash leafy-loft/launch.sh [height]   (default: 32)
#
# Mouse: click on the leafy-loft pane to interact, click your code pane to type.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HEIGHT="${1:-32}"
CMD="python3 '$SCRIPT_DIR/leafy-loft.py' --height $HEIGHT"

if [ -z "$TMUX" ]; then
    echo "Starting tmux with leafy-loft docked at the bottom..."
    echo "  Click the bottom pane to interact with plants."
    echo "  Click the top pane to type/code."
    echo "  Ctrl+C in the plant pane to quit."
    tmux new-session -d -s leafy-loft -x "$(tput cols)" -y "$(tput lines)" \; \
        set-option -g mouse on \; \
        split-window -v -l "$HEIGHT" "$CMD" \; \
        select-pane -t 0 \; \
        attach
else
    tmux set-option -g mouse on 2>/dev/null
    tmux split-window -v -l "$HEIGHT" "$CMD"
fi
