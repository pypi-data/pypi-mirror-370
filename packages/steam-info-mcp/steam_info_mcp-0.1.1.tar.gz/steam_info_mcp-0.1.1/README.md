# Steam Info MCP

A Model Context Protocol (MCP) server that exposes Steam Web API tools for retrieving game statistics, player information, and more.

## Features

- **Player Information**: Get summaries, friends, bans, and groups
- **Game Library**: Access owned games and recently played
- **Achievements & Stats**: Retrieve player achievements and game statistics
- **Steam News**: Get latest news for any Steam app
- **Global Data**: Access global achievement percentages and player counts
- **Smart ID Handling**: Accept both vanity names (e.g., "gaben") and SteamID64s (e.g., "76561197960287930")

## Installation

### From PyPI
```bash
pip install steam-info-mcp
```

### Development Installation
```bash
git clone https://github.com/beta/steam-info-mcp
cd steam-info-mcp
pip install -e .
```

## Configuration

Set the following environment variables in your MCP client configuration:

- `STEAM_API_KEY`: Your Steam Web API key

### Example Configuration

```json
{
  "mcpServers": {
    "Steam Info MCP": {
      "command": "uvx",
      "args": ["steam-info-mcp"],
      "env": {
        "STEAM_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Available Tools

### Player Information
- `steam-player-summaries(user_identifier:str)` - Get player summaries for a user (vanity name or SteamID64)
- `steam-friend-list(user_identifier:str, relationship:str="all")` - Get friend list for a user (vanity name or SteamID64)
- `steam-player-bans(user_identifier:str)` - Get player bans for a user (vanity name or SteamID64)
- `steam-user-groups(user_identifier:str)` - Get user groups for a user (vanity name or SteamID64)
- `steam-resolve-vanity(vanity:str)` - Resolve vanity name to SteamID64

### Game Library
- `steam-owned-games(user_identifier:str)` - Get owned games for a user (vanity name or SteamID64)
- `steam-recently-played(user_identifier:str, count:int=5)` - Get recently played games
- `steam-level(user_identifier:str)` - Get Steam level for a user (vanity name or SteamID64)
- `steam-badges(user_identifier:str)` - Get badges for a user (vanity name or SteamID64)
- `steam-community-badge-progress(user_identifier:str, badgeid:int=2)` - Get badge progress

### Game Statistics
- `steam-player-achievements(user_identifier:str, appid:int)` - Get achievements for a user (vanity name or SteamID64) and app
- `steam-user-stats(user_identifier:str, appid:int)` - Get user stats for a user (vanity name or SteamID64) and game
- `steam-global-achievements(appid:int)` - Get global achievement percentages for an app
- `steam-current-players(appid:int)` - Get current player count for an app

### News & Updates
- `steam-news(appid:int, count:int=3, maxlength:int=300)` - Get app news

## Usage

### Command Line
```bash
steam-info-mcp
```

### As MCP Server
The server runs over stdio and can be integrated with any MCP-compatible client.

## Requirements

- Python 3.9+
- Steam Web API key
- Internet connection

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

