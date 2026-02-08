#!/data/data/com.termux/files/usr/bin/bash

echo "[*] Installing NeoTermOS dependencies..."

pkg install python -y

chmod +x main.py

echo "[✓] Installation complete!"
echo ""
echo "Run NeoTermOS with:"
echo "python main.py"
