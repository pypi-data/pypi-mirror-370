import os
import requests
import json
from typing import Dict, Any, List, Optional

# --- Steam Web API Functions ---
# These functions provide clean wrappers around Steam Web API endpoints
# They can be imported and used by other projects or the MCP server
API_ROOT = "https://api.steampowered.com"

# --- Pretty Print ---
def pretty(data):
    return json.dumps(data, indent=2, ensure_ascii=False)


# --- Resolve SteamID64 via Each Call ---
def resolve_vanity_url(vanity_name: str, api_key: str) -> str:
    """Resolve a Steam vanity name into a SteamID64"""
    url = "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/"
    params = {"key": api_key, "vanityurl": vanity_name}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data["response"]["success"] == 1:
        return data["response"]["steamid"]
    else:
        raise ValueError(f"Could not resolve {vanity_name}, response: {data}")

def get_steamid64(vanity_name: str, api_key: str) -> str:
    return resolve_vanity_url(vanity_name, api_key)


# --- Shared GET Helper ---
def _get(path: str, params: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    q = {"key": api_key, **params}
    r = requests.get(f"{API_ROOT}/{path}", params=q, timeout=15)
    r.raise_for_status()
    return r.json()


# =======================
# ISteamUser
# =======================

def get_player_summaries(steamid: str, api_key: str) -> Dict[str, Any]:
    return _get("ISteamUser/GetPlayerSummaries/v2/", {"steamids": steamid}, api_key)

def get_friend_list(steamid: str, api_key: str, relationship: str = "all") -> Dict[str, Any]:
    return _get("ISteamUser/GetFriendList/v1/", {"steamid": steamid, "relationship": relationship}, api_key)

def get_player_bans(steamid: str, api_key: str) -> Dict[str, Any]:
    return _get("ISteamUser/GetPlayerBans/v1/", {"steamids": steamid}, api_key)

def get_user_group_list(steamid: str, api_key: str) -> Dict[str, Any]:
    """NEW: groups the user belongs to"""
    return _get("ISteamUser/GetUserGroupList/v1/", {"steamid": steamid}, api_key)

def resolve_vanity(vanity: str, api_key: str) -> Optional[str]:
    data = _get("ISteamUser/ResolveVanityURL/v1/", {"vanityurl": vanity}, api_key)
    resp = data.get("response", {})
    return resp.get("steamid") if resp.get("success") == 1 else None


# =======================
# IPlayerService (User Library/Profile Stats)
# =======================

def get_owned_games(steamid: str, api_key: str, include_appinfo: bool = True, include_played_free_games: bool = True) -> Dict[str, Any]:
    return _get("IPlayerService/GetOwnedGames/v1/", {
        "steamid": steamid,
        "include_appinfo": int(include_appinfo),
        "include_played_free_games": int(include_played_free_games),
    }, api_key)

def get_recently_played_games(steamid: str, api_key: str, count: int = 5) -> Dict[str, Any]:
    return _get("IPlayerService/GetRecentlyPlayedGames/v1/", {"steamid": steamid, "count": count}, api_key)

def get_steam_level(steamid: str, api_key: str) -> Dict[str, Any]:
    return _get("IPlayerService/GetSteamLevel/v1/", {"steamid": steamid}, api_key)

def get_badges(steamid: str, api_key: str) -> Dict[str, Any]:
    return _get("IPlayerService/GetBadges/v1/", {"steamid": steamid}, api_key)

def get_community_badge_progress(steamid: str, api_key: str, badgeid: int = 2) -> Dict[str, Any]:
    """NEW: progress towards a given community badge (2 = Pillar of Community)"""
    return _get("IPlayerService/GetCommunityBadgeProgress/v1/", {"steamid": steamid, "badgeid": badgeid}, api_key)


# =======================
# ISteamUserStats (Per-App + Global Stats; Requires APPID)
# =======================

def get_player_achievements(steamid: str, appid: int, api_key: str) -> Dict[str, Any]:
    return _get("ISteamUserStats/GetPlayerAchievements/v1/", {"steamid": steamid, "appid": appid}, api_key)

def get_user_stats_for_game(steamid: str, appid: int, api_key: str) -> Dict[str, Any]:
    return _get("ISteamUserStats/GetUserStatsForGame/v2/", {"steamid": steamid, "appid": appid}, api_key)

def get_global_achievement_percentages(appid: int, api_key: str) -> Dict[str, Any]:
    return _get("ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/", {"gameid": appid}, api_key)

def get_number_of_current_players(appid: int, api_key: str) -> Dict[str, Any]:
    return _get("ISteamUserStats/GetNumberOfCurrentPlayers/v1/", {"appid": appid}, api_key)


# =======================
# ISteamNews (Per-App News)
# =======================

def get_news_for_app(appid: int, api_key: str, count: int = 3, maxlength: int = 300) -> Dict[str, Any]:
    return _get("ISteamNews/GetNewsForApp/v2/", {"appid": appid, "count": count, "maxlength": maxlength}, api_key)
