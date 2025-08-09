# Setup Guide for Ultra Sports Betting System

This comprehensive guide will help you set up the Ultra Sports Betting System on your local machine or cloud platform.

## Prerequisites

### System Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Ubuntu 18.04+
- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher (for web interface)
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: At least 2GB free space
- **Internet**: Stable internet connection for API access

### Software Dependencies
- **Git**: For version control
- **VS Code**: Recommended IDE with extensions
- **Docker** (optional): For containerized deployment
- **PostgreSQL** (optional): For production database

## Quick Setup (Automated)

### One-Command Installation

The easiest way to set up the system is using our automated setup script:

```bash
# Clone the repository
git clone https://github.com/terrydupree/ultra-sports-betting-system.git
cd ultra-sports-betting-system

# Run the automated setup
python scripts/setup.py
```

This script will:
1. ✅ Check Python version compatibility
2. ✅ Create a virtual environment
3. ✅ Install all Python dependencies
4. ✅ Set up environment configuration
5. ✅ Create database schema
6. ✅ Configure Docker (optional)
7. ✅ Run initial system tests

### What the Setup Script Does

The `setup.py` script performs the following operations:

1. **Environment Preparation**
   - Creates Python virtual environment (`venv/`)
   - Installs all required packages from `requirements.txt`
   - Sets up development environment variables

2. **Configuration Files**
   - Creates `.env` file with default settings
   - Generates database schema (`database/schema.sql`)
   - Sets up Docker configuration files

3. **Development Tools**
   - Configures VS Code workspace
   - Sets up automated tasks and debugging
   - Installs recommended extensions

## Manual Setup (Step-by-Step)

If you prefer manual setup or encounter issues with the automated script:

### Step 1: Clone Repository

```bash
git clone https://github.com/terrydupree/ultra-sports-betting-system.git
cd ultra-sports-betting-system
```

### Step 2: Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Environment Configuration

Create a `.env` file in the project root:

```bash
# Copy the example environment file
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# API Keys (Replace with your actual keys)
ESPN_API_KEY=your_espn_api_key_here
SPORTSRADAR_API_KEY=your_sportsradar_api_key_here
ODDS_API_KEY=your_odds_api_key_here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/ultra_sports
REDIS_URL=redis://localhost:6379

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000

# Betting Configuration
DEFAULT_BANKROLL=10000
MAX_BET_PERCENTAGE=0.05
MIN_EV_THRESHOLD=1.0
```

### Step 4: Database Setup (Optional)

For production use, set up PostgreSQL and Redis:

```bash
# Install PostgreSQL and Redis
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib redis-server

# macOS with Homebrew:
brew install postgresql redis

# Start services
sudo systemctl start postgresql redis-server

# Create database
sudo -u postgres createdb ultra_sports

# Run database schema
psql -U postgres -d ultra_sports -f database/schema.sql
```

### Step 5: Verify Installation

```bash
# Run system tests
python scripts/test_system.py

# Start the API server
uvicorn api.main:app --reload

# Test API endpoints
curl http://localhost:8000/health
```

## API Keys Setup

### Required API Keys

1. **ESPN API** (Optional but recommended)
   - Free tier available
   - Sports data and schedules
   - Sign up at: https://developer.espn.com/

2. **SportsRadar API** (Optional)
   - Comprehensive sports statistics
   - Free trial available
   - Sign up at: https://developer.sportradar.com/

3. **The Odds API** (Required for betting odds)
   - Live betting odds data
   - Free tier: 500 requests/month
   - Sign up at: https://the-odds-api.com/

### Adding API Keys

Add your API keys to the `.env` file:

```bash
# Method 1: Edit .env file directly
nano .env

# Method 2: Use environment variables
export ESPN_API_KEY="your_key_here"
export ODDS_API_KEY="your_key_here"

# Method 3: Set in VS Code launch configuration
# Edit .vscode/launch.json to include API keys
```

## Google Apps Script Setup

### Step 1: Create Google Sheets Integration

1. Open Google Sheets: https://sheets.google.com
2. Create a new spreadsheet
3. Go to **Extensions > Apps Script**
4. Delete the default code
5. Copy the code from `google_apps_script/ultra_system_multi_sport.js`
6. Save the project as "Ultra Sports Betting System"

### Step 2: Configure Permissions

1. Click **Run** to execute `initializeUltraSystem()`
2. Grant required permissions when prompted
3. The script will create sheets for all sports automatically

### Step 3: Set Up Triggers

1. Click on the **Triggers** icon (alarm clock)
2. Add a new trigger:
   - Function: `refreshAllSportsData`
   - Event source: Time-driven
   - Type: Minutes timer
   - Every: 5 minutes

### Step 4: Configure API Access

1. In your Google Apps Script, go to **Project Settings**
2. Add script properties:
   - `API_KEY`: Your system's API key
   - `API_BASE_URL`: Your API server URL

## VS Code Setup

### Recommended Extensions

The system will automatically prompt you to install these extensions:

- **Python** - Python language support
- **Pylint** - Python linting
- **Black Formatter** - Python code formatting
- **REST Client** - API testing
- **GitLens** - Enhanced Git capabilities
- **Docker** - Container support
- **Thunder Client** - API testing alternative

### VS Code Tasks

Access these through `Ctrl+Shift+P` > `Tasks: Run Task`:

- **Setup Ultra Sports System** - Run complete setup
- **Install Dependencies** - Install Python packages
- **Run All Tests** - Execute test suite
- **Refresh All Data** - Update sports data
- **Train All Models** - Run ML model training
- **Start API Server** - Launch development server
- **Deploy to Cloud** - Deploy to cloud platform

### Debugging Configuration

The system includes pre-configured debug settings:

- **Python: Ultra Sports System Main** - Debug the main API
- **Python: MLB Analyzer** - Debug MLB-specific code
- **Python: NFL Analyzer** - Debug NFL-specific code
- **FastAPI: Debug Server** - Debug API server with hot reload

## Testing the Installation

### Quick Health Check

```bash
# Check system health
python scripts/test_system.py

# Test API server
uvicorn api.main:app --reload &
curl http://localhost:8000/health

# Test individual components
python -c "from sports.mlb.mlb_analyzer import MLBAnalyzer; print('MLB OK')"
python -c "from sports.nfl.nfl_analyzer import NFLAnalyzer; print('NFL OK')"
```

### Comprehensive Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Test specific sport
python -m pytest tests/mlb/ -v

# Test with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### API Testing

```bash
# Test core endpoints
curl http://localhost:8000/
curl http://localhost:8000/api/sports
curl http://localhost:8000/api/mlb/games

# Test with sample data
curl -X POST http://localhost:8000/api/mlb/predict \
  -H "Content-Type: application/json" \
  -d '{"home_team": "Yankees", "away_team": "Red Sox", "game_id": "test"}'
```

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

2. **API key errors**
   ```bash
   # Check .env file exists and contains keys
   cat .env | grep API_KEY
   
   # Verify environment variables are loaded
   python -c "import os; print(os.getenv('ODDS_API_KEY'))"
   ```

3. **Database connection errors**
   ```bash
   # Check PostgreSQL is running
   sudo systemctl status postgresql
   
   # Test database connection
   psql -U postgres -d ultra_sports -c "SELECT 1;"
   ```

4. **Port already in use**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   
   # Kill the process or use different port
   uvicorn api.main:app --port 8001
   ```

### Getting Help

1. **Check the logs**:
   ```bash
   # API logs
   tail -f logs/api.log
   
   # System logs
   python -c "from core.utils.logger import get_logger; logger = get_logger('test'); logger.info('Test log')"
   ```

2. **Validate configuration**:
   ```bash
   # Run configuration validation
   python scripts/validate_config.py
   ```

3. **Reset the system**:
   ```bash
   # Clean slate setup
   rm -rf venv/
   rm .env
   python scripts/setup.py
   ```

## Advanced Configuration

### Production Deployment

For production deployment, see:
- [Docker Deployment Guide](DOCKER_DEPLOYMENT.md)
- [Cloud Deployment Guide](CLOUD_DEPLOYMENT.md)
- [Security Configuration](SECURITY.md)

### Performance Optimization

- **Database Indexing**: Add indexes for frequently queried columns
- **Caching**: Configure Redis for API response caching
- **Load Balancing**: Use Nginx for multiple API instances
- **Monitoring**: Set up application performance monitoring

### Custom Sports Integration

To add support for additional sports:

```bash
# Use the sport module generator
python scripts/create_sport_module.py cricket

# Follow the generated instructions
# Implement sport-specific logic
# Add API endpoints
# Update Google Apps Script
```

## Next Steps

After successful setup:

1. **Configure your betting parameters** in the `.env` file
2. **Set up Google Apps Script** for spreadsheet integration
3. **Test the system** with sample data
4. **Start collecting real data** by running data refresh
5. **Monitor system performance** and adjust as needed

For detailed usage instructions, see the [User Guide](USER_GUIDE.md).

---

**Need help?** Check our [FAQ](FAQ.md) or open an issue on GitHub.