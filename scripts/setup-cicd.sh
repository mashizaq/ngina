#!/bin/bash
# Setup script for CI/CD pipeline

set -e

echo "🚀 Setting up CI/CD pipeline for ngina..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "📦 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python ${PYTHON_VERSION}${NC}"

# Check Node.js
echo "📦 Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 20+${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js ${NODE_VERSION}${NC}"

# Check Docker
echo "📦 Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠ Docker not found. Docker builds will be skipped.${NC}"
else
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    echo -e "${GREEN}✓ Docker ${DOCKER_VERSION}${NC}"
fi

# Install Python dependencies
echo ""
echo "📚 Installing Python dependencies..."
pip install -q -r requirements.txt
pip install -q pytest pytest-cov black flake8 isort pylint
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Install Node dependencies
echo ""
echo "📚 Installing Node.js dependencies..."
npm install -q
cd src/backend
npm install -q
cd - > /dev/null
echo -e "${GREEN}✓ Node.js dependencies installed${NC}"

# Run tests
echo ""
echo "🧪 Running tests..."
echo "   Python tests..."
pytest tests/ -q --tb=short 2>/dev/null || echo -e "${YELLOW}⚠ Some tests failed${NC}"

echo "   Node.js tests..."
cd src/backend
npm test -q 2>/dev/null || echo -e "${YELLOW}⚠ Some tests failed${NC}"
cd - > /dev/null

# Run linters
echo ""
echo "🔍 Running linters..."
echo "   Python linting..."
black --quiet app.py
flake8 app.py --count --show-source 2>/dev/null || echo -e "${YELLOW}⚠ Linting issues found${NC}"

echo "   TypeScript linting..."
cd src/backend
npm run lint -q 2>/dev/null || echo -e "${YELLOW}⚠ Linting issues found${NC}"
cd - > /dev/null

# Summary
echo ""
echo "=============================="
echo -e "${GREEN}✅ CI/CD setup complete!${NC}"
echo "=============================="
echo ""
echo "📝 Next steps:"
echo "1. Configure GitHub secrets (see .github/CI-CD-SETUP.md):"
echo "   - DOCKER_HUB_USERNAME"
echo "   - DOCKER_HUB_TOKEN"
echo ""
echo "2. Push to main or develop/ngina-orchestrator branch to trigger CI/CD"
echo ""
echo "3. Monitor at: https://github.com/YOUR_ORG/ngina/actions"
echo ""
echo "📚 Useful commands:"
echo "   make help              - Show all available commands"
echo "   make test              - Run all tests"
echo "   make lint              - Run all linters"
echo "   make docker-up         - Start services with Docker Compose"
echo ""
