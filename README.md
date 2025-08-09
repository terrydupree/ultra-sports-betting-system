# Ultra Sports Betting System

A comprehensive, professional-grade multi-sport betting analysis system with complete VS Code automation and Google Apps Script integration.

## 🏆 Features

- **Multi-Sport Support**: MLB, NFL, NBA, NHL, Soccer, Tennis, Golf, and MMA
- **VS Code Integration**: Complete workspace automation with tasks, debugging, and snippets
- **Google Apps Script**: Automated spreadsheet integration for all sports
- **Real-time Data**: Live odds monitoring and game data acquisition
- **Advanced Analytics**: Expected Value (EV) calculations, Kelly Criterion, and arbitrage detection
- **Professional Architecture**: Modular design for easy sport additions
- **One-Command Setup**: Complete system initialization with a single script

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 16+ (for web interface)
- Git
- VS Code (recommended)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/terrydupree/ultra-sports-betting-system.git
cd ultra-sports-betting-system
```

2. **Run the setup script**:
```bash
python scripts/setup.py
```

3. **Configure your environment**:
   - Update `.env` file with your API keys
   - Configure database connections
   - Set up Google Apps Script integration

4. **Start the development server**:
```bash
uvicorn api.main:app --reload
```

5. **Access the system**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 📁 Project Structure

```
ultra-sports-betting-system/
├── .vscode/                     # VS Code workspace configuration
│   ├── settings.json           # Development environment settings
│   ├── tasks.json             # Automated build/test/deploy tasks
│   ├── launch.json            # Debug configurations
│   ├── extensions.json        # Required VS Code extensions
│   └── snippets/              # Code templates for rapid development
├── core/                       # Core system modules
│   ├── data_acquisition/      # API integrations and data fetching
│   ├── processing/            # Data normalization and cleaning
│   ├── models/               # Machine learning models
│   ├── analysis/             # Statistical analysis and EV calculations
│   └── utils/                # Shared utilities and helpers
├── sports/                     # Sport-specific modules
│   ├── mlb/                   # Major League Baseball
│   ├── nfl/                   # National Football League
│   ├── nba/                   # National Basketball Association
│   ├── nhl/                   # National Hockey League
│   ├── soccer/                # Soccer/Football
│   ├── tennis/                # Tennis
│   ├── golf/                  # Golf
│   └── mma/                   # Mixed Martial Arts
├── google_apps_script/         # Google Sheets integration
├── api/                       # REST API endpoints
├── web_interface/             # React frontend (coming soon)
├── database/                  # Database schemas and migrations
├── deployment/                # Cloud deployment configurations
├── tests/                     # Automated testing suite
├── docs/                      # Documentation
└── scripts/                   # Automation and utility scripts
```

## 🎯 Core Components

### Data Acquisition Engine
- **Multiple API Integrations**: ESPN, SportsRadar, The Odds API
- **Rate Limiting**: Intelligent request throttling
- **Error Handling**: Robust retry logic and fallback mechanisms
- **Real-time Updates**: Live game data and odds monitoring

### Processing Pipeline
- **Data Normalization**: Consistent format across all sports
- **Feature Engineering**: Sport-specific statistical features
- **Quality Validation**: Automated data quality checks
- **Performance Monitoring**: Real-time processing metrics

### Analysis Framework
- **Expected Value (EV)**: Precise betting opportunity identification
- **Kelly Criterion**: Optimal bet sizing calculations
- **Arbitrage Detection**: Cross-bookmaker opportunity scanning
- **Risk Assessment**: Portfolio-level risk management

### VS Code Automation
- **One-Click Operations**: Deploy, test, and refresh with single commands
- **Intelligent Debugging**: Multi-language debugging configurations
- **Code Templates**: Rapid development with sport-specific snippets
- **Task Automation**: Integrated build, test, and deployment workflows

## 🔧 VS Code Commands

Access these through VS Code Command Palette (`Ctrl+Shift+P`):

- **Ultra Sports: Setup System** - Initialize complete system
- **Ultra Sports: Refresh Data** - Update all sport data
- **Ultra Sports: Train Models** - Execute model training
- **Ultra Sports: Deploy** - Deploy to cloud platforms
- **Ultra Sports: Create Sport Module** - Add new sport support

## 📊 Google Apps Script Integration

### Features
- **Automated Sheet Creation**: Individual sheets for each sport
- **Real-time Data Sync**: 5-minute update intervals
- **Custom Formulas**: Sport-specific calculations
- **Mobile-Friendly**: Responsive design for mobile access
- **Notification System**: Alerts for high-value opportunities

### Setup
1. Open Google Sheets
2. Go to Extensions > Apps Script
3. Copy code from `google_apps_script/ultra_system_multi_sport.js`
4. Run `initializeUltraSystem()` function
5. Configure API keys in the Configuration sheet

## 🏈 Sport-Specific Features

### MLB (Major League Baseball)
- **Pitcher Analysis**: Starting pitcher matchup evaluation
- **Weather Impact**: Game condition considerations
- **Run Prediction**: Accurate scoring forecasts
- **Bullpen Strength**: Relief pitcher analysis

### NFL (National Football League)
- **Spread Analysis**: Point spread prediction and evaluation
- **Situational Factors**: Primetime, division games, rest advantages
- **Weather Conditions**: Impact on scoring and game flow
- **Injury Reports**: Player availability considerations

### NBA (Basketball) - Coming Soon
- **Pace Analysis**: Game tempo predictions
- **Player Props**: Individual performance betting
- **Back-to-back**: Schedule impact analysis
- **Home Court**: Venue-specific advantages

### NHL (Hockey) - Coming Soon
- **Goalie Matchups**: Starting goaltender analysis
- **Power Play**: Special teams effectiveness
- **Puck Line**: Hockey spread betting
- **Total Goals**: Over/under predictions

## 📈 API Endpoints

### Core Endpoints
- `GET /` - System information
- `GET /health` - Health check
- `GET /api/sports` - Supported sports list

### Sport-Specific Endpoints
- `GET /api/{sport}/games` - Game data for specific sport
- `GET /api/{sport}/teams/{team_id}/stats` - Team statistics
- `POST /api/{sport}/predict` - Game outcome predictions
- `POST /api/{sport}/recommendations` - Betting recommendations

### Example Usage
```bash
# Get today's MLB games
curl http://localhost:8000/api/mlb/games

# Get team statistics
curl http://localhost:8000/api/nfl/teams/NE/stats

# Get game prediction
curl -X POST http://localhost:8000/api/mlb/predict \
  -H "Content-Type: application/json" \
  -d '{"home_team": "Yankees", "away_team": "Red Sox"}'
```

## 🧪 Testing

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Sport-Specific Tests
```bash
python -m pytest tests/mlb/ -v
python -m pytest tests/nfl/ -v
```

### Test Coverage
```bash
python -m pytest tests/ --cov=. --cov-report=html
```

## 🚀 Deployment

### Local Development
```bash
# Start API server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Start web interface (when available)
cd web_interface && npm run dev
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Cloud Deployment
```bash
# Deploy to Google Cloud Platform
python scripts/deploy.py --platform gcp

# Deploy to AWS
python scripts/deploy.py --platform aws
```

## ⚙️ Configuration

### Environment Variables
```bash
# API Keys
ESPN_API_KEY=your_espn_key
SPORTSRADAR_API_KEY=your_sportsradar_key
ODDS_API_KEY=your_odds_api_key

# Database
DATABASE_URL=postgresql://user:pass@localhost/ultra_sports
REDIS_URL=redis://localhost:6379

# Application
DEBUG=True
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
```

### Betting Configuration
```python
DEFAULT_BANKROLL = 10000
MAX_BET_PERCENTAGE = 0.05  # 5% max per bet
MIN_EV_THRESHOLD = 1.0     # 1% minimum expected value
```

## 🔄 Data Refresh

### Automated Refresh
The system automatically refreshes data every 5 minutes for:
- Game schedules and scores
- Current betting odds
- Team statistics
- Player information

### Manual Refresh
```bash
# Refresh all sports
python scripts/data_refresh.py

# Refresh specific sport
python scripts/data_refresh.py --sport mlb

# Refresh odds only
python scripts/data_refresh.py --odds-only
```

## 🆕 Adding New Sports

### Using the Sport Module Creator
```bash
# Create a new sport module
python scripts/create_sport_module.py cricket

# Follow the generated instructions to complete integration
```

### Manual Integration
1. Create sport directory in `sports/`
2. Implement analyzer class extending `BaseAnalyzer`
3. Add API endpoints to `api/main.py`
4. Update Google Apps Script configuration
5. Add tests in `tests/`

## 📚 Documentation

- **Setup Guide**: `docs/SETUP_GUIDE.md`
- **API Reference**: `docs/API_DOCUMENTATION.md`
- **Sport Modules**: `docs/SPORT_MODULES.md`
- **Google Apps Script**: `docs/GOOGLE_APPS_SCRIPT.md`
- **Contributing**: `docs/CONTRIBUTING.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-sport`)
3. Commit your changes (`git commit -am 'Add new sport support'`)
4. Push to the branch (`git push origin feature/new-sport`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/terrydupree/ultra-sports-betting-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com/terrydupree/ultra-sports-betting-system/discussions)
- **Documentation**: [Project Wiki](https://github.com/terrydupree/ultra-sports-betting-system/wiki)

## ⚠️ Disclaimer

This software is for educational and research purposes only. Sports betting may be illegal in your jurisdiction. Please check your local laws and regulations. The authors are not responsible for any financial losses incurred through the use of this software.

## 🏅 Acknowledgments

- ESPN API for sports data
- SportsRadar for comprehensive statistics
- The Odds API for betting odds
- Google Apps Script for spreadsheet integration
- FastAPI for the web framework
- All contributors and supporters of the project

---

**Ultra Sports Betting System** - Professional sports betting analysis with complete automation and multi-sport support.
