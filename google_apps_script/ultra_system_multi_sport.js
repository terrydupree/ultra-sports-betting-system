/**
 * Ultra Sports Betting System - Enhanced Multi-Sport Google Apps Script
 * Comprehensive integration for MLB, NFL, NBA, NHL, Soccer, Tennis, Golf, and MMA
 * 
 * @version 2.0
 * @author Ultra Sports Betting System
 */

// Configuration object for all sports
const ULTRA_CONFIG = {
  apiBaseUrl: 'https://your-api-url.com',  // Replace with your actual API URL
  updateInterval: 300000, // 5 minutes in milliseconds
  maxRetries: 3,
  sports: {
    mlb: {
      name: 'MLB',
      displayName: 'Major League Baseball',
      season: 'April-October',
      sheetName: 'MLB_Analysis',
      color: '#FF6B6B'
    },
    nfl: {
      name: 'NFL', 
      displayName: 'National Football League',
      season: 'September-February',
      sheetName: 'NFL_Analysis',
      color: '#4ECDC4'
    },
    nba: {
      name: 'NBA',
      displayName: 'National Basketball Association', 
      season: 'October-June',
      sheetName: 'NBA_Analysis',
      color: '#45B7D1'
    },
    nhl: {
      name: 'NHL',
      displayName: 'National Hockey League',
      season: 'October-June', 
      sheetName: 'NHL_Analysis',
      color: '#96CEB4'
    },
    soccer: {
      name: 'Soccer',
      displayName: 'Soccer',
      season: 'Year-round',
      sheetName: 'Soccer_Analysis',
      color: '#FFEAA7'
    },
    tennis: {
      name: 'Tennis',
      displayName: 'Tennis',
      season: 'Year-round',
      sheetName: 'Tennis_Analysis', 
      color: '#DDA0DD'
    },
    golf: {
      name: 'Golf',
      displayName: 'Golf',
      season: 'Year-round',
      sheetName: 'Golf_Analysis',
      color: '#98D8C8'
    },
    mma: {
      name: 'MMA',
      displayName: 'Mixed Martial Arts',
      season: 'Year-round',
      sheetName: 'MMA_Analysis',
      color: '#F7DC6F'
    }
  }
};

/**
 * Initialize the Ultra Sports Betting System
 * Creates sheets for all sports and sets up automation
 */
function initializeUltraSystem() {
  try {
    Logger.log('🚀 Initializing Ultra Sports Betting System...');
    
    const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    
    // Create overview dashboard
    createOverviewDashboard(spreadsheet);
    
    // Create sheets for each sport
    Object.keys(ULTRA_CONFIG.sports).forEach(sportKey => {
      const sport = ULTRA_CONFIG.sports[sportKey];
      createSportSheet(spreadsheet, sportKey, sport);
    });
    
    // Setup automated triggers
    setupAllTriggers();
    
    // Create configuration sheet
    createConfigurationSheet(spreadsheet);
    
    Logger.log('✅ Ultra Sports Betting System initialized successfully!');
    
    // Show completion message
    SpreadsheetApp.getUi().alert(
      'Ultra Sports System Initialized',
      'All sport sheets have been created with automated data refresh. ' +
      'Please update the Configuration sheet with your API keys.',
      SpreadsheetApp.getUi().ButtonSet.OK
    );
    
  } catch (error) {
    Logger.log('❌ Error initializing system: ' + error.toString());
    throw error;
  }
}

/**
 * Create overview dashboard sheet
 */
function createOverviewDashboard(spreadsheet) {
  let dashboardSheet = spreadsheet.getSheetByName('Dashboard');
  
  if (!dashboardSheet) {
    dashboardSheet = spreadsheet.insertSheet('Dashboard');
  }
  
  // Clear existing content
  dashboardSheet.clear();
  
  // Set up header
  const headers = [
    ['Ultra Sports Betting System Dashboard'],
    ['Last Updated: ' + new Date().toString()],
    [''],
    ['Sport', 'Status', 'Last Refresh', 'Games Today', 'Positive EV Bets', 'Top Recommendation']
  ];
  
  dashboardSheet.getRange(1, 1, headers.length, 6).setValues(headers);
  
  // Format header
  dashboardSheet.getRange(1, 1, 1, 6).merge().setFontSize(16).setFontWeight('bold')
    .setBackground('#4285f4').setFontColor('white').setHorizontalAlignment('center');
  
  dashboardSheet.getRange(4, 1, 1, 6).setFontWeight('bold').setBackground('#f0f0f0');
  
  // Add sport rows
  let row = 5;
  Object.keys(ULTRA_CONFIG.sports).forEach(sportKey => {
    const sport = ULTRA_CONFIG.sports[sportKey];
    dashboardSheet.getRange(row, 1).setValue(sport.displayName);
    dashboardSheet.getRange(row, 2).setValue('🔄 Initializing...');
    dashboardSheet.getRange(row, 1, 1, 6).setBackground(sport.color);
    row++;
  });
  
  // Auto-resize columns
  dashboardSheet.autoResizeColumns(1, 6);
}

/**
 * Create sport-specific analysis sheet
 */
function createSportSheet(spreadsheet, sportKey, sport) {
  try {
    let sheet = spreadsheet.getSheetByName(sport.sheetName);
    
    if (!sheet) {
      sheet = spreadsheet.insertSheet(sport.sheetName);
    }
    
    // Clear existing content
    sheet.clear();
    
    // Set up headers based on sport type
    const headers = getSportHeaders(sportKey);
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    
    // Format headers
    const headerRange = sheet.getRange(1, 1, 1, headers.length);
    headerRange.setFontWeight('bold')
      .setBackground(sport.color)
      .setFontColor('white')
      .setHorizontalAlignment('center');
    
    // Add sport info
    sheet.getRange(2, 1).setValue(`${sport.displayName} - Season: ${sport.season}`);
    sheet.getRange(2, 1, 1, headers.length).merge()
      .setBackground('#f8f9fa')
      .setFontStyle('italic')
      .setHorizontalAlignment('center');
    
    // Auto-resize columns
    sheet.autoResizeColumns(1, headers.length);
    
    Logger.log(`✅ Created ${sport.displayName} sheet`);
    
  } catch (error) {
    Logger.log(`❌ Error creating ${sport.displayName} sheet: ` + error.toString());
  }
}

/**
 * Get sport-specific headers
 */
function getSportHeaders(sportKey) {
  const commonHeaders = [
    'Game ID', 'Date', 'Home Team', 'Away Team', 'Status'
  ];
  
  const sportSpecificHeaders = {
    mlb: [
      ...commonHeaders,
      'Home Score', 'Away Score', 'Inning', 'Pitcher Matchup',
      'Predicted Home Runs', 'Predicted Away Runs', 'O/U Line', 'O/U Prediction',
      'Home ML Odds', 'Away ML Odds', 'Home EV%', 'Away EV%', 'Recommendation'
    ],
    nfl: [
      ...commonHeaders,
      'Home Score', 'Away Score', 'Quarter', 'Spread', 'Predicted Spread',
      'Total', 'Predicted Total', 'Home ML', 'Away ML', 'Spread EV%', 'Total EV%', 'Recommendation'
    ],
    nba: [
      ...commonHeaders,
      'Home Score', 'Away Score', 'Quarter', 'Spread', 'Predicted Spread',
      'Total', 'Predicted Total', 'Home ML', 'Away ML', 'Best Bet', 'EV%'
    ],
    nhl: [
      ...commonHeaders,
      'Home Score', 'Away Score', 'Period', 'Puck Line', 'Predicted Line',
      'Total Goals', 'Predicted Total', 'Best Value', 'EV%'
    ],
    soccer: [
      ...commonHeaders,
      'Home Score', 'Away Score', 'Time', '1X2 Odds', 'Predicted Result',
      'Goals Total', 'Predicted Goals', 'Best Market', 'EV%'
    ],
    tennis: [
      ...commonHeaders,
      'Set Score', 'Current Set', 'Match Winner Odds', 'Predicted Winner',
      'Set Betting', 'Game Totals', 'Best Value', 'EV%'
    ],
    golf: [
      'Tournament', 'Round', 'Player', 'Current Position', 'Strokes',
      'Outright Odds', 'Top 10 Odds', 'Predicted Finish', 'Best Bet', 'EV%'
    ],
    mma: [
      'Event', 'Fighter A', 'Fighter B', 'Weight Class', 'Method Odds',
      'Predicted Winner', 'Predicted Method', 'Round Totals', 'Best Bet', 'EV%'
    ]
  };
  
  return sportSpecificHeaders[sportKey] || commonHeaders;
}

/**
 * Create configuration sheet for API keys and settings
 */
function createConfigurationSheet(spreadsheet) {
  let configSheet = spreadsheet.getSheetByName('Configuration');
  
  if (!configSheet) {
    configSheet = spreadsheet.insertSheet('Configuration');
  }
  
  // Clear existing content
  configSheet.clear();
  
  const configData = [
    ['Ultra Sports Betting System Configuration'],
    [''],
    ['API Settings', 'Value', 'Description'],
    ['API Base URL', ULTRA_CONFIG.apiBaseUrl, 'Base URL for your API server'],
    ['Update Interval (minutes)', ULTRA_CONFIG.updateInterval / 60000, 'How often to refresh data'],
    [''],
    ['API Keys (Replace with your actual keys)', '', ''],
    ['ESPN API Key', 'your_espn_api_key_here', 'ESPN Sports API key'],
    ['SportsRadar API Key', 'your_sportsradar_api_key_here', 'SportsRadar API key'],
    ['Odds API Key', 'your_odds_api_key_here', 'The Odds API key'],
    [''],
    ['Betting Configuration', '', ''],
    ['Default Bankroll', '10000', 'Default bankroll amount'],
    ['Max Bet %', '5', 'Maximum percentage of bankroll per bet'],
    ['Min EV Threshold', '1.0', 'Minimum expected value to recommend bet'],
    [''],
    ['Sport Activation', 'Enabled', 'Enable/Disable sport data'],
  ];
  
  // Add sport activation controls
  Object.keys(ULTRA_CONFIG.sports).forEach(sportKey => {
    const sport = ULTRA_CONFIG.sports[sportKey];
    configData.push([sport.displayName, 'TRUE', `Enable ${sport.displayName} data collection`]);
  });
  
  configSheet.getRange(1, 1, configData.length, 3).setValues(configData);
  
  // Format configuration sheet
  configSheet.getRange(1, 1, 1, 3).merge().setFontSize(14).setFontWeight('bold')
    .setBackground('#34a853').setFontColor('white').setHorizontalAlignment('center');
  
  configSheet.getRange(3, 1, 1, 3).setFontWeight('bold').setBackground('#f0f0f0');
  configSheet.getRange(7, 1, 1, 3).setFontWeight('bold').setBackground('#f0f0f0');
  configSheet.getRange(12, 1, 1, 3).setFontWeight('bold').setBackground('#f0f0f0');
  configSheet.getRange(17, 1, 1, 3).setFontWeight('bold').setBackground('#f0f0f0');
  
  // Auto-resize columns
  configSheet.autoResizeColumns(1, 3);
}

/**
 * Refresh data for all active sports
 */
function refreshAllSportsData() {
  try {
    Logger.log('🔄 Starting data refresh for all sports...');
    
    const startTime = new Date();
    const results = {};
    
    // Get configuration
    const config = getConfiguration();
    
    // Refresh each active sport
    Object.keys(ULTRA_CONFIG.sports).forEach(sportKey => {
      if (config.sports[sportKey]) {
        try {
          const result = refreshSportData(sportKey);
          results[sportKey] = result;
          Logger.log(`✅ ${ULTRA_CONFIG.sports[sportKey].displayName}: ${result.success ? 'Success' : 'Failed'}`);
        } catch (error) {
          Logger.log(`❌ Error refreshing ${sportKey}: ` + error.toString());
          results[sportKey] = { success: false, error: error.toString() };
        }
      }
    });
    
    // Update dashboard
    updateDashboard(results);
    
    const endTime = new Date();
    const duration = (endTime - startTime) / 1000;
    
    Logger.log(`🏁 Data refresh completed in ${duration} seconds`);
    
  } catch (error) {
    Logger.log('❌ Error in refreshAllSportsData: ' + error.toString());
  }
}

/**
 * Refresh data for a specific sport
 */
function refreshSportData(sportKey) {
  try {
    const sport = ULTRA_CONFIG.sports[sportKey];
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sport.sheetName);
    
    if (!sheet) {
      throw new Error(`Sheet ${sport.sheetName} not found`);
    }
    
    // Fetch data from API
    const apiUrl = `${ULTRA_CONFIG.apiBaseUrl}/api/${sportKey}/games`;
    const response = makeApiRequest(apiUrl);
    
    if (!response || !response.games) {
      return { success: false, error: 'No data received from API' };
    }
    
    // Process and update sheet
    const processedData = processSportData(response.games, sportKey);
    updateSportSheet(sheet, processedData, sportKey);
    
    return {
      success: true,
      gameCount: response.games.length,
      timestamp: new Date()
    };
    
  } catch (error) {
    Logger.log(`Error refreshing ${sportKey}: ` + error.toString());
    return { success: false, error: error.toString() };
  }
}

/**
 * Process sport-specific data for sheet display
 */
function processSportData(games, sportKey) {
  return games.map(game => {
    const baseData = [
      game.game_id || '',
      game.date || '',
      game.home_team || '',
      game.away_team || '',
      game.status || ''
    ];
    
    // Add sport-specific data
    switch (sportKey) {
      case 'mlb':
        return [
          ...baseData,
          game.home_score || 0,
          game.away_score || 0,
          game.inning || '',
          game.pitcher_matchup || '',
          game.predicted_home_runs || '',
          game.predicted_away_runs || '',
          game.over_under_line || '',
          game.predicted_total || '',
          game.home_ml_odds || '',
          game.away_ml_odds || '',
          game.home_ev_percent || '',
          game.away_ev_percent || '',
          game.recommendation || ''
        ];
        
      case 'nfl':
        return [
          ...baseData,
          game.home_score || 0,
          game.away_score || 0,
          game.quarter || '',
          game.spread || '',
          game.predicted_spread || '',
          game.total || '',
          game.predicted_total || '',
          game.home_ml || '',
          game.away_ml || '',
          game.spread_ev_percent || '',
          game.total_ev_percent || '',
          game.recommendation || ''
        ];
        
      default:
        return baseData;
    }
  });
}

/**
 * Update sport sheet with new data
 */
function updateSportSheet(sheet, data, sportKey) {
  try {
    // Clear existing data (keep headers)
    if (sheet.getLastRow() > 3) {
      sheet.getRange(4, 1, sheet.getLastRow() - 3, sheet.getLastColumn()).clear();
    }
    
    // Add new data
    if (data.length > 0) {
      const range = sheet.getRange(4, 1, data.length, data[0].length);
      range.setValues(data);
      
      // Apply conditional formatting for recommendations
      applyConditionalFormatting(sheet, sportKey);
    }
    
    // Update timestamp
    sheet.getRange(2, 1).setValue(
      `${ULTRA_CONFIG.sports[sportKey].displayName} - Last Updated: ${new Date().toString()}`
    );
    
  } catch (error) {
    Logger.log(`Error updating sheet for ${sportKey}: ` + error.toString());
  }
}

/**
 * Apply conditional formatting based on recommendations
 */
function applyConditionalFormatting(sheet, sportKey) {
  try {
    const lastRow = sheet.getLastRow();
    const lastCol = sheet.getLastColumn();
    
    if (lastRow > 3) {
      // Get recommendation column (usually last column)
      const recColIndex = lastCol;
      const recRange = sheet.getRange(4, recColIndex, lastRow - 3, 1);
      
      // Clear existing conditional formatting
      recRange.clearFormat();
      
      // Apply formatting rules
      const rules = [
        SpreadsheetApp.newConditionalFormatRule()
          .whenTextEqualTo('BET')
          .setBackground('#d4edda')
          .setFontColor('#155724')
          .setRanges([recRange])
          .build(),
        SpreadsheetApp.newConditionalFormatRule()
          .whenTextEqualTo('CONSIDER')
          .setBackground('#fff3cd')
          .setFontColor('#856404')
          .setRanges([recRange])
          .build(),
        SpreadsheetApp.newConditionalFormatRule()
          .whenTextEqualTo('AVOID')
          .setBackground('#f8d7da')
          .setFontColor('#721c24')
          .setRanges([recRange])
          .build()
      ];
      
      sheet.setConditionalFormatRules(rules);
    }
    
  } catch (error) {
    Logger.log(`Error applying conditional formatting: ` + error.toString());
  }
}

/**
 * Update dashboard with latest results
 */
function updateDashboard(results) {
  try {
    const dashboard = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Dashboard');
    if (!dashboard) return;
    
    // Update timestamp
    dashboard.getRange(2, 1).setValue('Last Updated: ' + new Date().toString());
    
    // Update sport statuses
    let row = 5;
    Object.keys(ULTRA_CONFIG.sports).forEach(sportKey => {
      const result = results[sportKey];
      if (result) {
        const status = result.success ? '✅ Active' : '❌ Error';
        const lastRefresh = result.timestamp ? result.timestamp.toString() : 'Never';
        const gameCount = result.gameCount || 0;
        
        dashboard.getRange(row, 2).setValue(status);
        dashboard.getRange(row, 3).setValue(lastRefresh);
        dashboard.getRange(row, 4).setValue(gameCount);
      }
      row++;
    });
    
  } catch (error) {
    Logger.log('Error updating dashboard: ' + error.toString());
  }
}

/**
 * Make API request with retry logic
 */
function makeApiRequest(url, retries = 0) {
  try {
    const options = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + getApiKey()
      }
    };
    
    const response = UrlFetchApp.fetch(url, options);
    
    if (response.getResponseCode() === 200) {
      return JSON.parse(response.getContentText());
    } else {
      throw new Error(`API request failed with status: ${response.getResponseCode()}`);
    }
    
  } catch (error) {
    if (retries < ULTRA_CONFIG.maxRetries) {
      Logger.log(`API request failed, retrying... (${retries + 1}/${ULTRA_CONFIG.maxRetries})`);
      Utilities.sleep(1000 * (retries + 1)); // Exponential backoff
      return makeApiRequest(url, retries + 1);
    } else {
      Logger.log(`API request failed after ${ULTRA_CONFIG.maxRetries} retries: ` + error.toString());
      throw error;
    }
  }
}

/**
 * Get API key from script properties
 */
function getApiKey() {
  const properties = PropertiesService.getScriptProperties();
  return properties.getProperty('API_KEY') || 'your_api_key_here';
}

/**
 * Set API key in script properties
 */
function setApiKey(apiKey) {
  const properties = PropertiesService.getScriptProperties();
  properties.setProperty('API_KEY', apiKey);
  Logger.log('✅ API key updated');
}

/**
 * Get configuration from Configuration sheet
 */
function getConfiguration() {
  try {
    const configSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Configuration');
    if (!configSheet) {
      return { sports: {} };
    }
    
    const config = {
      sports: {}
    };
    
    // Read sport activation settings
    Object.keys(ULTRA_CONFIG.sports).forEach(sportKey => {
      config.sports[sportKey] = true; // Default to enabled
    });
    
    return config;
    
  } catch (error) {
    Logger.log('Error reading configuration: ' + error.toString());
    return { sports: {} };
  }
}

/**
 * Setup automated triggers for all sports
 */
function setupAllTriggers() {
  try {
    // Delete existing triggers
    const triggers = ScriptApp.getProjectTriggers();
    triggers.forEach(trigger => {
      if (trigger.getHandlerFunction() === 'refreshAllSportsData') {
        ScriptApp.deleteTrigger(trigger);
      }
    });
    
    // Create new trigger for all sports refresh
    ScriptApp.newTrigger('refreshAllSportsData')
      .timeBased()
      .everyMinutes(5)
      .create();
    
    Logger.log('✅ Automated triggers setup complete');
    
  } catch (error) {
    Logger.log('Error setting up triggers: ' + error.toString());
  }
}

/**
 * Manual refresh functions for individual sports
 */
function refreshMLBData() { return refreshSportData('mlb'); }
function refreshNFLData() { return refreshSportData('nfl'); }
function refreshNBAData() { return refreshSportData('nba'); }
function refreshNHLData() { return refreshSportData('nhl'); }
function refreshSoccerData() { return refreshSportData('soccer'); }
function refreshTennisData() { return refreshSportData('tennis'); }
function refreshGolfData() { return refreshSportData('golf'); }
function refreshMMAData() { return refreshSportData('mma'); }

/**
 * Utility function to test API connection
 */
function testApiConnection() {
  try {
    const testUrl = `${ULTRA_CONFIG.apiBaseUrl}/api/health`;
    const response = makeApiRequest(testUrl);
    
    if (response) {
      Logger.log('✅ API connection successful');
      SpreadsheetApp.getUi().alert('API Test', 'Connection successful!', SpreadsheetApp.getUi().ButtonSet.OK);
      return true;
    } else {
      throw new Error('No response from API');
    }
    
  } catch (error) {
    Logger.log('❌ API connection failed: ' + error.toString());
    SpreadsheetApp.getUi().alert('API Test', 'Connection failed: ' + error.toString(), SpreadsheetApp.getUi().ButtonSet.OK);
    return false;
  }
}