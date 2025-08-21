#!/bin/bash
# MakeMCP Quick Install Script

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}MakeMCP Installer${NC}"
echo "=================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv (super-fast Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
    
    echo -e "${GREEN}✓${NC} uv installed"
    echo ""
fi

# Install MakeMCP
echo "📦 Installing MakeMCP..."
uv pip install git+https://github.com/leifmarkthaler/makemcp.git

# Create a test file
cat > hello.py << 'EOF'
from makemcp.quick import tool, run

@tool
def hello(name: str = "World") -> str:
    """Say hello."""
    return f"Hello, {name}! 👋"

@tool  
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

if __name__ == "__main__":
    print("MakeMCP server ready! Run this file to start.")
    print("Tools available: hello, add")
    run()
EOF

echo ""
echo -e "${GREEN}✅ MakeMCP installed successfully!${NC}"
echo ""
echo "Created hello.py - a simple example server"
echo ""
echo "To run it:"
echo "  python hello.py"
echo ""
echo "Happy coding! 🚀"