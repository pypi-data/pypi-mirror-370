# Steam Info MCP

A Model Context Protocol (MCP) server that exposes Steam Web API tools for retrieving game statistics, player information, and more.

## Features

- **Player Information**: Get summaries, friends, bans, and groups
- **Game Library**: Access owned games and recently played
- **Achievements & Stats**: Retrieve player achievements and game statistics
- **Steam News**: Get latest news for any Steam app
- **Global Data**: Access global achievement percentages and player counts

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
- `steam-player-summaries(vanity_name:str)` - Get player summaries for a vanity user
- `steam-friend-list(vanity_name:str, relationship:str="all")` - Get friend list for a vanity user
- `steam-player-bans(vanity_name:str)` - Get player bans for a vanity user
- `steam-user-groups(vanity_name:str)` - Get user groups for a vanity user
- `steam-resolve-vanity(vanity:str)` - Resolve vanity name to SteamID64

### Game Library
- `steam-owned-games(vanity_name:str)` - Get owned games for a vanity user
- `steam-recently-played(vanity_name:str, count:int=5)` - Get recently played games
- `steam-level(vanity_name:str)` - Get Steam level for a vanity user
- `steam-badges(vanity_name:str)` - Get badges for a vanity user
- `steam-community-badge-progress(vanity_name:str, badgeid:int=2)` - Get badge progress

### Game Statistics
- `steam-player-achievements(vanity_name:str, appid:int)` - Get achievements for a vanity user and app
- `steam-user-stats(vanity_name:str, appid:int)` - Get user stats for a vanity user and game
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

