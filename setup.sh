#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== IP Guardian Setup ==="

# 1. Install Python dependencies
echo "[1/3] Installing Python dependencies..."
pip3 install -r "$SCRIPT_DIR/requirements.txt"

# 2. Generate CLI wrappers
echo "[2/3] Generating CLI guard wrappers..."
cd "$SCRIPT_DIR"
python3 -c "
from ip_guardian.cli_guard import generate_rc
from ip_guardian.config import load_config
config = load_config()
generate_rc(config['cli_commands'], config['allowed_ips'])
print('Generated ~/.ip_guardian_rc')
"

# 3. Inject source line into .zshrc if needed
ZSHRC="$HOME/.zshrc"
if ! grep -q 'ip_guardian_rc' "$ZSHRC" 2>/dev/null; then
    echo "[3/3] Adding source line to .zshrc..."
    echo "" >> "$ZSHRC"
    echo "# IP Guardian CLI protection" >> "$ZSHRC"
    echo "source ~/.ip_guardian_rc" >> "$ZSHRC"
    echo "Added to .zshrc"
else
    echo "[3/3] .zshrc already configured, skipping."
fi

echo ""
echo "=== Setup complete ==="
echo ""
echo "Edit config.json to set your allowed IP:"
echo "  $SCRIPT_DIR/config.json"
echo ""
echo "Then run IP Guardian:"
echo "  cd $SCRIPT_DIR && python3 -m ip_guardian.app"
echo ""
echo "To set your current IP as allowed:"
echo "  IP=\$(curl -fsS https://ifconfig.me/ip || curl -fsS https://api.ipify.org || curl -fsS https://ipv4.icanhazip.com)"
echo "  echo \"Your IP: \$IP\""
