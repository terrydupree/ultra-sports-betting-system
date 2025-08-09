#!/usr/bin/env python3
"""
Ultra Sports Betting System Setup Script
One-command initialization for the complete system
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict

def print_banner():
    """Print setup banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║              Ultra Sports Betting System                     ║
    ║                   Setup & Installation                       ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def create_virtual_environment():
    """Create Python virtual environment."""
    print("\n📦 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_python_dependencies():
    """Install Python dependencies."""
    print("\n📥 Installing Python dependencies...")
    
    # Create requirements.txt if it doesn't exist
    requirements = [
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "redis>=4.6.0",
        "pytest>=7.4.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
        "jupyter>=1.0.0"
    ]
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        with open(requirements_file, "w") as f:
            f.write("\n".join(requirements))
        print("✅ Created requirements.txt")
    
    # Install dependencies
    try:
        pip_path = "venv/bin/pip" if os.name != "nt" else "venv\\Scripts\\pip"
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✅ Python dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False

def setup_web_interface():
    """Setup React web interface."""
    print("\n🌐 Setting up web interface...")
    
    web_dir = Path("web_interface")
    if not web_dir.exists():
        try:
            # Create React app
            subprocess.run([
                "npx", "create-react-app", "web_interface", 
                "--template", "typescript"
            ], check=True)
            
            # Install additional dependencies
            os.chdir("web_interface")
            additional_deps = [
                "@types/react", "@types/react-dom",
                "axios", "react-router-dom", 
                "tailwindcss", "recharts"
            ]
            subprocess.run(["npm", "install"] + additional_deps, check=True)
            os.chdir("..")
            
            print("✅ Web interface setup complete")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to setup web interface: {e}")
            return False
    else:
        print("✅ Web interface already exists")
        return True

def create_environment_file():
    """Create .env file with default configuration."""
    print("\n⚙️ Creating environment configuration...")
    
    env_content = """# Ultra Sports Betting System Configuration

# API Keys (Replace with your actual keys)
ESPN_API_KEY=your_espn_api_key_here
SPORTSRADAR_API_KEY=your_sportsradar_api_key_here
ODDS_API_KEY=your_odds_api_key_here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/ultra_sports
REDIS_URL=redis://localhost:6379

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000

# Betting Configuration
DEFAULT_BANKROLL=10000
MAX_BET_PERCENTAGE=0.05
MIN_EV_THRESHOLD=1.0
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Environment file created (.env)")
        print("⚠️  Please update .env with your actual API keys and configuration")
    else:
        print("✅ Environment file already exists")

def setup_database_structure():
    """Create database initialization scripts."""
    print("\n🗄️ Setting up database structure...")
    
    db_dir = Path("database")
    
    # Create database schema
    schema_sql = """
-- Ultra Sports Betting System Database Schema

-- Sports table
CREATE TABLE IF NOT EXISTS sports (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Teams table
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    sport_id INTEGER REFERENCES sports(id),
    external_id VARCHAR(100),
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100),
    abbreviation VARCHAR(10),
    conference VARCHAR(50),
    division VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Games table
CREATE TABLE IF NOT EXISTS games (
    id SERIAL PRIMARY KEY,
    sport_id INTEGER REFERENCES sports(id),
    external_id VARCHAR(100) UNIQUE,
    home_team_id INTEGER REFERENCES teams(id),
    away_team_id INTEGER REFERENCES teams(id),
    game_date TIMESTAMP NOT NULL,
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'scheduled',
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id),
    model_name VARCHAR(100) NOT NULL,
    home_win_probability DECIMAL(5,4),
    away_win_probability DECIMAL(5,4),
    predicted_home_score DECIMAL(5,2),
    predicted_away_score DECIMAL(5,2),
    confidence_score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Odds table
CREATE TABLE IF NOT EXISTS odds (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id),
    bookmaker VARCHAR(100) NOT NULL,
    market_type VARCHAR(50) NOT NULL,
    team_name VARCHAR(100),
    odds_american INTEGER,
    odds_decimal DECIMAL(6,3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default sports
INSERT INTO sports (name, display_name) VALUES 
    ('mlb', 'Major League Baseball'),
    ('nfl', 'National Football League'),
    ('nba', 'National Basketball Association'),
    ('nhl', 'National Hockey League'),
    ('soccer', 'Soccer'),
    ('tennis', 'Tennis'),
    ('golf', 'Golf'),
    ('mma', 'Mixed Martial Arts')
ON CONFLICT (name) DO NOTHING;
"""
    
    schema_file = db_dir / "schema.sql"
    with open(schema_file, "w") as f:
        f.write(schema_sql)
    
    print("✅ Database schema created")

def create_docker_configuration():
    """Create Docker configuration for easy deployment."""
    print("\n🐳 Creating Docker configuration...")
    
    # Dockerfile
    dockerfile_content = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    # Docker Compose
    docker_compose_content = """
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/ultra_sports
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - .:/app
    
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=ultra_sports
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/schema.sql:/docker-entrypoint-initdb.d/schema.sql
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
"""
    
    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose_content)
    
    print("✅ Docker configuration created")

def create_gitignore():
    """Create comprehensive .gitignore file."""
    print("\n📝 Creating .gitignore...")
    
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/settings.json
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3

# Node.js (for web interface)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# React build
web_interface/build/

# Jupyter Notebooks
.ipynb_checkpoints/

# Model files
*.pkl
*.joblib
models/saved/

# Data files
data/raw/
data/processed/
*.csv
*.json

# Testing
.coverage
.pytest_cache/
htmlcov/

# Documentation
docs/_build/
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    
    print("✅ .gitignore created")

def run_initial_tests():
    """Run initial system tests."""
    print("\n🧪 Running initial tests...")
    
    try:
        python_path = "venv/bin/python" if os.name != "nt" else "venv\\Scripts\\python"
        
        # Test imports
        test_script = """
try:
    import pandas as pd
    import numpy as np
    import fastapi
    print("✅ All core dependencies imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
"""
        
        result = subprocess.run([python_path, "-c", test_script], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout.strip())
            return True
        else:
            print(f"❌ Initial tests failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main setup function."""
    print_banner()
    
    # Step-by-step setup
    steps = [
        ("Checking Python version", check_python_version),
        ("Creating virtual environment", create_virtual_environment),
        ("Installing Python dependencies", install_python_dependencies),
        ("Creating environment configuration", create_environment_file),
        ("Setting up database structure", setup_database_structure),
        ("Creating Docker configuration", create_docker_configuration),
        ("Creating .gitignore", create_gitignore),
        ("Running initial tests", run_initial_tests),
    ]
    
    success_count = 0
    total_steps = len(steps)
    
    for step_name, step_function in steps:
        try:
            if step_function():
                success_count += 1
            else:
                print(f"⚠️  {step_name} completed with warnings")
        except Exception as e:
            print(f"❌ {step_name} failed: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Setup completed: {success_count}/{total_steps} steps successful")
    
    if success_count == total_steps:
        print("\n🎉 Ultra Sports Betting System setup completed successfully!")
        print("\nNext steps:")
        print("1. Update .env file with your API keys")
        print("2. Start the development server: uvicorn api.main:app --reload")
        print("3. Visit http://localhost:8000/docs for API documentation")
        print("4. Run tests: python -m pytest tests/")
    else:
        print("\n⚠️  Setup completed with some issues. Please review the errors above.")
    
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()