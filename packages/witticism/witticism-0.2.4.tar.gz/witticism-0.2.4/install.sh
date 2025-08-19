#!/bin/bash
# One-command installer for Witticism
# Handles everything: GPU detection, dependencies, auto-start

set -e

echo "🎙️ Installing Witticism..."

# Install system dependencies for pyaudio
if command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    echo "📦 Installing system dependencies..."
    if ! dpkg -l | grep -q portaudio19-dev; then
        echo "Installing PortAudio development headers (required for voice input)..."
        sudo apt-get update && sudo apt-get install -y portaudio19-dev
    fi
elif command -v dnf &> /dev/null; then
    # Fedora/RHEL
    echo "📦 Installing system dependencies..."
    if ! rpm -qa | grep -q portaudio-devel; then
        echo "Installing PortAudio development headers (required for voice input)..."
        sudo dnf install -y portaudio-devel
    fi
elif command -v pacman &> /dev/null; then
    # Arch Linux
    echo "📦 Installing system dependencies..."
    if ! pacman -Q portaudio &> /dev/null; then
        echo "Installing PortAudio (required for voice input)..."
        sudo pacman -S --noconfirm portaudio
    fi
fi

# 1. Install pipx if not present
if ! command -v pipx &> /dev/null; then
    echo "📦 Installing pipx package manager..."
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    export PATH="$HOME/.local/bin:$PATH"
    echo "✓ pipx installed"
else
    echo "✓ pipx already installed"
fi

# 2. Detect GPU and install with right CUDA
if nvidia-smi &> /dev/null; then
    CUDA_VERSION=$(nvidia-smi | grep "CUDA Version" | sed 's/.*CUDA Version: \([0-9]*\.[0-9]*\).*/\1/')
    echo "🎮 GPU detected with CUDA $CUDA_VERSION"
    
    if [[ $(echo "$CUDA_VERSION >= 12.1" | bc) -eq 1 ]]; then
        INDEX_URL="https://download.pytorch.org/whl/cu121"
    elif [[ $(echo "$CUDA_VERSION >= 11.8" | bc) -eq 1 ]]; then
        INDEX_URL="https://download.pytorch.org/whl/cu118"
    else
        INDEX_URL="https://download.pytorch.org/whl/cpu"
    fi
else
    echo "💻 No GPU detected - using CPU version"
    INDEX_URL="https://download.pytorch.org/whl/cpu"
fi

# 3. Install Witticism
echo "📦 Installing Witticism with dependencies..."
echo "⏳ This may take several minutes as PyTorch and WhisperX are large packages"
echo ""
pipx install witticism --verbose --pip-args="--index-url $INDEX_URL --extra-index-url https://pypi.org/simple --verbose"

# 4. Set up auto-start
echo "Setting up auto-start..."
mkdir -p ~/.config/autostart

cat > ~/.config/autostart/witticism.desktop << EOF
[Desktop Entry]
Type=Application
Name=Witticism
Comment=Voice transcription that types anywhere
Exec=$HOME/.local/bin/witticism
Icon=microphone
StartupNotify=false
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

echo "✅ Installation complete!"
echo ""
echo "Witticism will:"
echo "  • Start automatically when you log in"
echo "  • Run in your system tray"
echo "  • Use GPU acceleration (if available)"
echo ""
echo "To start now: witticism"
echo "To disable auto-start: rm ~/.config/autostart/witticism.desktop"