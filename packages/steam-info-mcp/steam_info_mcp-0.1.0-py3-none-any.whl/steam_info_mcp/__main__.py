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


def _get_steamid64(vanity_name: str) -> str:
    api_key = require_env("STEAM_API_KEY")
    return resolve_vanity(vanity_name, api_key)


@mcp.tool("steam-player-summaries", description="Get player summaries for a vanity user")
def player_summaries(vanity_name: str) -> TextContent:
    steamid = _get_steamid64(vanity_name)
    api_key = require_env("STEAM_API_KEY")
    data = get_player_summaries(steamid, api_key)
    return ok(pretty(data))


@mcp.tool("steam-owned-games", description="Get owned games for a vanity user")
def owned_games(vanity_name: str) -> TextContent:
    steamid = _get_steamid64(vanity_name)
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


@mcp.tool("steam-friend-list", description="Get friend list for a vanity user")
def friend_list(vanity_name: str, relationship: str = "all") -> TextContent:
    steamid = _get_steamid64(vanity_name)
    api_key = require_env("STEAM_API_KEY")
    data = get_friend_list(steamid, api_key, relationship)
    return ok(pretty(data))


@mcp.tool("steam-player-bans", description="Get player bans for a vanity user")
def player_bans(vanity_name: str) -> TextContent:
    steamid = _get_steamid64(vanity_name)
    api_key = require_env("STEAM_API_KEY")
    data = get_player_bans(steamid, api_key)
    return ok(pretty(data))


@mcp.tool("steam-user-groups", description="Get user groups for a vanity user")
def user_groups(vanity_name: str) -> TextContent:
    steamid = _get_steamid64(vanity_name)
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


@mcp.tool("steam-recently-played", description="Get recently played games for a vanity user")
def recently_played(vanity_name: str, count: int = 5) -> TextContent:
    steamid = _get_steamid64(vanity_name)
    api_key = require_env("STEAM_API_KEY")
    data = get_recently_played_games(steamid, api_key, count)
    return ok(pretty(data))


@mcp.tool("steam-level", description="Get Steam level for a vanity user")
def steam_level(vanity_name: str) -> TextContent:
    steamid = _get_steamid64(vanity_name)
    api_key = require_env("STEAM_API_KEY")
    data = get_steam_level(steamid, api_key)
    return ok(pretty(data))


@mcp.tool("steam-badges", description="Get badges for a vanity user")
def badges(vanity_name: str) -> TextContent:
    steamid = _get_steamid64(vanity_name)
    api_key = require_env("STEAM_API_KEY")
    data = get_badges(steamid, api_key)
    return ok(pretty(data))


@mcp.tool("steam-community-badge-progress", description="Get community badge progress for a vanity user")
def community_badge_progress(vanity_name: str, badgeid: int = 2) -> TextContent:
    steamid = _get_steamid64(vanity_name)
    api_key = require_env("STEAM_API_KEY")
    data = get_community_badge_progress(steamid, api_key, badgeid)
    return ok(pretty(data))


@mcp.tool("steam-player-achievements", description="Get player achievements for a vanity user and appid")
def player_achievements(vanity_name: str, appid: int) -> TextContent:
    steamid = _get_steamid64(vanity_name)
    api_key = require_env("STEAM_API_KEY")
    data = get_player_achievements(steamid, appid, api_key)
    return ok(pretty(data))


@mcp.tool("steam-user-stats", description="Get user stats for a vanity user and game")
def user_stats(vanity_name: str, appid: int) -> TextContent:
    steamid = _get_steamid64(vanity_name)
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


