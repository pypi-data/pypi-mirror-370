import os
from .functions import (
    get_player_summaries, get_friend_list, get_player_bans,
    get_user_group_list, get_owned_games, get_recently_played_games,
    get_steam_level, get_badges, get_community_badge_progress,
    get_player_achievements, get_user_stats_for_game,
    get_global_achievement_percentages, get_number_of_current_players,
    get_news_for_app, resolve_vanity, pretty
)

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


mcp = FastMCP("steam-info-mcp")


def ok(msg: str) -> TextContent:
    return TextContent(type="text", text=msg)


def _get_steamid64(user_identifier: str) -> str:
    # Check if input is already a SteamID64 (17 digits starting with 7656)
    if user_identifier.isdigit() and len(user_identifier) == 17 and user_identifier.startswith("7656"):
        return user_identifier
    
    # Otherwise, resolve vanity name to SteamID64
    api_key = require_env("STEAM_API_KEY")
    return resolve_vanity(user_identifier, api_key)


@mcp.tool("steam-player-summaries", description="Get player summaries for a user (vanity name or SteamID64)")
def player_summaries(user_identifier: str) -> TextContent:
    steamid = _get_steamid64(user_identifier)
    api_key = require_env("STEAM_API_KEY")
    data = get_player_summaries(steamid, api_key)
    return ok(pretty(data))


@mcp.tool("steam-owned-games", description="Get owned games for a user (vanity name or SteamID64)")
def owned_games(user_identifier: str) -> TextContent:
    steamid = _get_steamid64(user_identifier)
    api_key = require_env("STEAM_API_KEY")
    data = get_owned_games(steamid, api_key)
    return ok(pretty(data))


@mcp.tool("steam-global-achievements", description="Get global achievement percentages for an appid")
def global_achievements(appid: int) -> TextContent:
    api_key = require_env("STEAM_API_KEY")
    data = get_global_achievement_percentages(appid, api_key)
    return ok(pretty(data))


@mcp.tool("steam-current-players", description="Get number of current players for an appid")
def current_players(appid: int) -> TextContent:
    api_key = require_env("STEAM_API_KEY")
    data = get_number_of_current_players(appid, api_key)
    return ok(pretty(data))


@mcp.tool("steam-friend-list", description="Get friend list for a user (vanity name or SteamID64)")
def friend_list(user_identifier: str, relationship: str = "all") -> TextContent:
    steamid = _get_steamid64(user_identifier)
    api_key = require_env("STEAM_API_KEY")
    data = get_friend_list(steamid, api_key, relationship)
    return ok(pretty(data))


@mcp.tool("steam-player-bans", description="Get player bans for a user (vanity name or SteamID64)")
def player_bans(user_identifier: str) -> TextContent:
    steamid = _get_steamid64(user_identifier)
    api_key = require_env("STEAM_API_KEY")
    data = get_player_bans(steamid, api_key)
    return ok(pretty(data))


@mcp.tool("steam-user-groups", description="Get user groups for a user (vanity name or SteamID64)")
def user_groups(user_identifier: str) -> TextContent:
    steamid = _get_steamid64(user_identifier)
    api_key = require_env("STEAM_API_KEY")
    data = get_user_group_list(steamid, api_key)
    return ok(pretty(data))


@mcp.tool("steam-resolve-vanity", description="Resolve a vanity name to SteamID64")
def resolve_vanity_tool(vanity: str) -> TextContent:
    api_key = require_env("STEAM_API_KEY")
    steamid = resolve_vanity(vanity, api_key)
    if not steamid:
        return ok(f"Could not resolve vanity '{vanity}'")
    return ok(f"Vanity '{vanity}' -> SteamID64: {steamid}")


@mcp.tool("steam-recently-played", description="Get recently played games for a user (vanity name or SteamID64)")
def recently_played(user_identifier: str, count: int = 5) -> TextContent:
    steamid = _get_steamid64(user_identifier)
    api_key = require_env("STEAM_API_KEY")
    data = get_recently_played_games(steamid, api_key, count)
    return ok(pretty(data))


@mcp.tool("steam-level", description="Get Steam level for a user (vanity name or SteamID64)")
def steam_level(user_identifier: str) -> TextContent:
    steamid = _get_steamid64(user_identifier)
    api_key = require_env("STEAM_API_KEY")
    data = get_steam_level(steamid, api_key)
    return ok(pretty(data))


@mcp.tool("steam-badges", description="Get badges for a user (vanity name or SteamID64)")
def badges(user_identifier: str) -> TextContent:
    steamid = _get_steamid64(user_identifier)
    api_key = require_env("STEAM_API_KEY")
    data = get_badges(steamid, api_key)
    return ok(pretty(data))


@mcp.tool("steam-community-badge-progress", description="Get community badge progress for a user (vanity name or SteamID64)")
def community_badge_progress(user_identifier: str, badgeid: int = 2) -> TextContent:
    steamid = _get_steamid64(user_identifier)
    api_key = require_env("STEAM_API_KEY")
    data = get_community_badge_progress(steamid, api_key, badgeid)
    return ok(pretty(data))


@mcp.tool("steam-player-achievements", description="Get player achievements for a user (vanity name or SteamID64) and appid")
def player_achievements(user_identifier: str, appid: int) -> TextContent:
    steamid = _get_steamid64(user_identifier)
    api_key = require_env("STEAM_API_KEY")
    data = get_player_achievements(steamid, appid, api_key)
    return ok(pretty(data))


@mcp.tool("steam-user-stats", description="Get user stats for a user (vanity name or SteamID64) and game")
def user_stats(user_identifier: str, appid: int) -> TextContent:
    steamid = _get_steamid64(user_identifier)
    api_key = require_env("STEAM_API_KEY")
    data = get_user_stats_for_game(steamid, appid, api_key)
    return ok(pretty(data))


@mcp.tool("steam-news", description="Get news for an app")
def news(appid: int, count: int = 3, maxlength: int = 300) -> TextContent:
    api_key = require_env("STEAM_API_KEY")
    data = get_news_for_app(appid, api_key, count, maxlength)
    return ok(pretty(data))


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()


