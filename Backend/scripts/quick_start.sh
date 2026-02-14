#!/bin/bash
# Quick start script for CareOps Backend

set -e

echo "🚀 CareOps Backend Quick Start"
echo "================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.11+ required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your credentials before continuing"
    echo "   Required: SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY, SECRET_KEY"
    echo ""
    read -p "Press Enter after configuring .env..."
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment exists"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check Redis
echo "🔍 Checking Redis..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis is running"
    else
        echo "⚠️  Redis is not running. Starting Redis..."
        if command -v redis-server &> /dev/null; then
            redis-server --daemonize yes
            echo "✅ Redis started"
        else
            echo "❌ Redis not found. Please install Redis:"
            echo "   macOS: brew install redis"
            echo "   Ubuntu: sudo apt install redis-server"
            echo "   Or use Docker: docker run -d -p 6379:6379 redis:alpine"
            exit 1
        fi
    fi
else
    echo "⚠️  Redis CLI not found. Assuming Redis is running..."
fi
echo ""

# Test Supabase connection
echo "🔗 Testing Supabase connection..."
python3 -c "
from app.db.supabase_client import get_supabase_client
try:
    client = get_supabase_client()
    print('✅ Supabase connected successfully')
except Exception as e:
    print(f'❌ Supabase connection failed: {e}')
    exit(1)
" || exit 1
echo ""

# Generate secret key if needed
if grep -q "your-secret-key-here-change-in-production" .env; then
    echo "🔐 Generating SECRET_KEY..."
    secret_key=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$secret_key/" .env
    else
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$secret_key/" .env
    fi
    echo "✅ SECRET_KEY generated"
    echo ""
fi

# Run tests
echo "🧪 Running tests..."
pytest tests/test_health.py -v
echo ""

# Start services
echo "🎯 Starting CareOps Backend..."
echo ""
echo "Services will start in separate terminals:"
echo "  1. API Server (http://localhost:8000)"
echo "  2. Celery Worker"
echo "  3. Celery Beat"
echo ""
echo "📚 API Documentation: http://localhost:8000/api/v1/docs"
echo "🏥 Health Check: http://localhost:8000/health"
echo ""

# Check if tmux is available
if command -v tmux &> /dev/null; then
    echo "Starting services with tmux..."
    tmux new-session -d -s careops
    tmux send-keys -t careops "source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" C-m
    tmux split-window -t careops -h
    tmux send-keys -t careops "source venv/bin/activate && celery -A app.tasks.celery_app worker --loglevel=info" C-m
    tmux split-window -t careops -v
    tmux send-keys -t careops "source venv/bin/activate && celery -A app.tasks.celery_app beat --loglevel=info" C-m
    tmux attach -t careops
else
    echo "⚠️  tmux not found. Starting API server only..."
    echo "   To start all services, run:"
    echo "   Terminal 1: uvicorn app.main:app --reload"
    echo "   Terminal 2: celery -A app.tasks.celery_app worker --loglevel=info"
    echo "   Terminal 3: celery -A app.tasks.celery_app beat --loglevel=info"
    echo ""
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
fi
