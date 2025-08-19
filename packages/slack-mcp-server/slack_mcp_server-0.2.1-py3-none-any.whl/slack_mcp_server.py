#!/usr/bin/env python3
"""
Slack MCP Server using FastMCP

A Model Context Protocol server for Slack workspace integration with multiuser support.
Provides tools for conversations and resources for workspace metadata.
"""

import os
import csv
import io
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import requests
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

# Initialize FastMCP server
mcp = FastMCP("Slack MCP Server")

class SlackClient:
    """Slack Web API client with token-based authentication and caching"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://slack.com/api"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Cache configuration from environment variables with better defaults
        cache_dir = os.path.expanduser("~/slack-cache")
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            try:
                os.makedirs(cache_dir, exist_ok=True)
            except Exception:
                # Fall back to current directory if can't create ~/slack-cache
                cache_dir = "."
        
        self.users_cache_file = os.environ.get("SLACK_MCP_USERS_CACHE", 
                                               os.path.join(cache_dir, "users_cache.json"))
        self.channels_cache_file = os.environ.get("SLACK_MCP_CHANNELS_CACHE", 
                                                  os.path.join(cache_dir, "channels_cache_v2.json"))
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated request to Slack API"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params or {})
        
        if response.status_code != 200:
            raise Exception(f"Slack API error: {response.status_code} - {response.text}")
            
        data = response.json()
        if not data.get("ok"):
            raise Exception(f"Slack API error: {data.get('error', 'Unknown error')}")
            
        return data
    
    def _is_cache_fresh(self, cache_file: str, cache_duration_hours: int = 24) -> bool:
        """Check if cache file exists and is fresh"""
        cache_path = Path(cache_file)
        if not cache_path.exists():
            return False
        
        cache_stat = cache_path.stat()
        cache_age = datetime.now() - datetime.fromtimestamp(cache_stat.st_mtime)
        return cache_age < timedelta(hours=cache_duration_hours)
    
    def _load_cache(self, cache_file: str) -> Optional[List[Dict[str, Any]]]:
        """Load data from cache file"""
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _save_cache(self, cache_file: str, data: List[Dict[str, Any]]) -> None:
        """Save data to cache file"""
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            # Log error but don't fail the operation
            print(f"Warning: Failed to save cache to {cache_file}: {e}")
    
    def get_cached_users(self, cache_duration_hours: int = 24) -> List[Dict[str, Any]]:
        """Get users with caching support"""
        # Check if cache is fresh
        if self._is_cache_fresh(self.users_cache_file, cache_duration_hours):
            cached_data = self._load_cache(self.users_cache_file)
            if cached_data:
                return cached_data
        
        # Fetch fresh data from API
        data = self._make_request("users.list", {"limit": 999})
        users = data.get("members", [])
        
        # Save to cache
        self._save_cache(self.users_cache_file, users)
        
        return users
    
    def get_cached_channels(self, cache_duration_hours: int = 6) -> List[Dict[str, Any]]:
        """Get channels with caching support and graceful permission handling"""
        # Check if cache is fresh
        if self._is_cache_fresh(self.channels_cache_file, cache_duration_hours):
            cached_data = self._load_cache(self.channels_cache_file)
            if cached_data:
                return cached_data
        
        # Fetch fresh data from API for all channel types
        all_channels = []
        successful_types = []
        failed_types = []
        
        for channel_type in ["public_channel", "private_channel", "im", "mpim"]:
            try:
                data = self._make_request("conversations.list", {
                    "types": channel_type,
                    "limit": 999
                })
                channels = data.get("channels", [])
                all_channels.extend(channels)
                successful_types.append(f"{channel_type}({len(channels)})")
            except Exception as e:
                # Track failed types for debugging
                failed_types.append(f"{channel_type}({str(e)})")
                continue
        
        # Save to cache even if some types failed
        if all_channels:
            self._save_cache(self.channels_cache_file, all_channels)
            # Optionally log what was successful/failed
            print(f"Channels cache updated: {len(all_channels)} channels from {len(successful_types)} types")
            if failed_types:
                print(f"Note: Some channel types failed: {failed_types}")
        else:
            print("Warning: No channels could be fetched. Check token permissions.")
        
        return all_channels
    
    def resolve_channel_id(self, channel_input: str) -> str:
        """Resolve channel name/mention to channel ID"""
        # Return as-is if already a valid channel ID format
        if channel_input.startswith('C') and len(channel_input) == 11:
            return channel_input
        
        # Load cached channels
        channels = self.get_cached_channels()
        
        # Handle #channel format
        if channel_input.startswith('#'):
            channel_name = channel_input[1:]  # Remove #
            for channel in channels:
                if channel.get('name') == channel_name:
                    return channel['id']
        
        # Handle @user_dm format for direct messages
        if channel_input.startswith('@'):
            user_name = channel_input[1:].replace('_dm', '').replace('_group', '')
            # For DMs, we need to find the user and open a conversation
            users = self.get_cached_users()
            for user in users:
                if (user.get('name') == user_name or 
                    user.get('display_name') == user_name or
                    user.get('real_name') == user_name):
                    # Open DM conversation
                    try:
                        dm_data = self._make_request("conversations.open", {"users": user['id']})
                        return dm_data['channel']['id']
                    except Exception:
                        # If opening DM fails, continue searching
                        continue
        
        # Try direct name match for channels
        for channel in channels:
            if channel.get('name') == channel_input:
                return channel['id']
        
        # Return as-is if no resolution found
        return channel_input
    
    def resolve_user_id(self, user_input: str) -> str:
        """Resolve user name/mention to user ID"""
        # Return as-is if already a valid user ID format
        if user_input.startswith('U') and len(user_input) == 11:
            return user_input
        
        # Load cached users
        users = self.get_cached_users()
        
        # Handle @username format
        if user_input.startswith('@'):
            user_name = user_input[1:]
        else:
            user_name = user_input
        
        # Search for user by various name fields
        for user in users:
            if (user.get('name') == user_name or 
                user.get('display_name') == user_name or
                user.get('real_name') == user_name or
                user.get('profile', {}).get('display_name') == user_name or
                user.get('profile', {}).get('real_name') == user_name):
                return user['id']
        
        # Return as-is if no resolution found
        return user_input

def get_slack_client() -> SlackClient:
    """Get Slack client from request context or environment"""
    token = None
    
    # Try to get token from HTTP headers with multiple approaches
    try:
        headers = get_http_headers()
        
        # Check Authorization header (Bearer format)
        auth_header = headers.get("Authorization") or headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
        
        # Also check alternative header names for Slack token
        if not token:
            for header_name in ['x-slack-token', 'slack-token', 'x-access-token', 'access-token']:
                header_value = headers.get(header_name) or headers.get(header_name.replace('-', '_'))
                if header_value:
                    token = header_value
                    break
    except Exception as e:
        # If get_http_headers() fails, that's okay, we'll fall back to environment
        print(f"Warning: Could not access HTTP headers: {e}")
    
    # Fall back to environment variable
    if not token:
        token = os.environ.get("SLACK_MCP_XOXP_TOKEN")
    
    if not token:
        raise Exception("SLACK_MCP_XOXP_TOKEN not provided in headers or environment. Please provide Slack token in Authorization header (Bearer <token>) or set SLACK_MCP_XOXP_TOKEN environment variable.")
    
    return SlackClient(token)

def parse_limit(limit_str: str, default_days: int = 1) -> Dict[str, Any]:
    """Parse limit parameter into API parameters"""
    if not limit_str:
        return {"limit": 100}
    
    # Check if it's a time-based limit (e.g., "1d", "1w", "30d")
    if limit_str.endswith(('d', 'w')):
        if limit_str.endswith('d'):
            days = int(limit_str[:-1])
        elif limit_str.endswith('w'):
            days = int(limit_str[:-1]) * 7
        
        # Convert to timestamp
        oldest_ts = (datetime.now() - timedelta(days=days)).timestamp()
        return {"oldest": str(oldest_ts), "limit": 1000}
    
    # Numeric limit
    try:
        return {"limit": min(int(limit_str), 1000)}
    except ValueError:
        return {"limit": 100}

@mcp.tool
def conversations_history(
    channel_id: str,
    include_activity_messages: bool = False,
    cursor: Optional[str] = None,
    limit: str = "1d",
    include_user_details: bool = True
) -> Dict[str, Any]:
    """
    Get messages from the channel (or DM) by channel_id with enhanced user information
    
    Args:
        channel_id: ID of the channel in format Cxxxxxxxxxx or its name starting with #... or @...
        include_activity_messages: If true, include activity messages like channel_join/leave
        cursor: Cursor for pagination
        limit: Limit of messages - time format (1d, 1w, 30d) or number (50)
        include_user_details: If true, include user details (name, real_name) for each message
    
    Returns:
        Enhanced message data with user details and metadata
    """
    client = get_slack_client()
    
    try:
        # Resolve channel name to ID
        resolved_channel_id = client.resolve_channel_id(channel_id)
        
        params = {
            "channel": resolved_channel_id,
            "include_all_metadata": include_activity_messages
        }
        
        if cursor:
            params["cursor"] = cursor
        else:
            # Apply limit only when cursor is not provided
            limit_params = parse_limit(limit)
            params.update(limit_params)
        
        data = client._make_request("conversations.history", params)
        messages = data.get("messages", [])
        
        # Enhance messages with user details if requested
        if include_user_details and messages:
            users = client.get_cached_users()
            user_lookup = {user["id"]: user for user in users}
            
            for message in messages:
                user_id = message.get("user")
                if user_id and user_id in user_lookup:
                    user_data = user_lookup[user_id]
                    message["user_details"] = {
                        "username": user_data.get("name", "unknown"),
                        "real_name": user_data.get("real_name", "Unknown"),
                        "display_name": user_data.get("profile", {}).get("display_name", ""),
                        "is_bot": user_data.get("is_bot", False)
                    }
        
        return {
            "messages": messages,
            "message_count": len(messages),
            "has_more": data.get("has_more", False),
            "next_cursor": data.get("response_metadata", {}).get("next_cursor"),
            "channel_id": resolved_channel_id,
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False,
            "channel_id": channel_id,
            "resolved_channel_id": resolved_channel_id if 'resolved_channel_id' in locals() else None
        }

@mcp.tool
def conversations_replies(
    channel_id: str,
    thread_ts: str,
    include_activity_messages: bool = False,
    cursor: Optional[str] = None,
    limit: str = "1d"
) -> Dict[str, Any]:
    """
    Get a thread of messages posted to a conversation by channelID and thread_ts
    
    Args:
        channel_id: ID of the channel in format Cxxxxxxxxxx or name starting with #... or @...
        thread_ts: Unique identifier of thread's parent message (timestamp format 1234567890.123456)
        include_activity_messages: If true, include activity messages like channel_join/leave
        cursor: Cursor for pagination
        limit: Limit of messages - time format (1d, 1w, 30d) or number (50)
    """
    client = get_slack_client()
    
    # Resolve channel name to ID
    resolved_channel_id = client.resolve_channel_id(channel_id)
    
    params = {
        "channel": resolved_channel_id,
        "ts": thread_ts,
        "include_all_metadata": include_activity_messages
    }
    
    if cursor:
        params["cursor"] = cursor
    else:
        # Apply limit only when cursor is not provided
        limit_params = parse_limit(limit)
        params.update(limit_params)
    
    data = client._make_request("conversations.replies", params)
    
    return {
        "messages": data.get("messages", []),
        "has_more": data.get("has_more", False),
        "next_cursor": data.get("response_metadata", {}).get("next_cursor")
    }

@mcp.tool
def conversations_add_message(
    channel_id: str,
    payload: str,
    thread_ts: Optional[str] = None,
    content_type: str = "text/markdown"
) -> Dict[str, Any]:
    """
    Add a message to a public channel, private channel, or direct message
    
    Note: Posting messages is disabled by default for safety. 
    Set SLACK_MCP_ADD_MESSAGE_TOOL environment variable to enable.
    
    Args:
        channel_id: ID of the channel in format Cxxxxxxxxxx or name starting with #... or @...
        payload: Message payload in specified content_type format
        thread_ts: Optional thread timestamp to reply to (format 1234567890.123456)
        content_type: Content type of message (text/markdown or text/plain)
    """
    # Check if message posting is enabled (check headers first, then environment)
    headers = get_http_headers()
    add_message_setting = (
        headers.get("SLACK_MCP_ADD_MESSAGE_TOOL") or 
        headers.get("slack_mcp_add_message_tool") or
        os.environ.get("SLACK_MCP_ADD_MESSAGE_TOOL")
    )
    if not add_message_setting:
        raise Exception("Message posting is disabled. Set SLACK_MCP_ADD_MESSAGE_TOOL in headers or environment to enable.")
    
    # If setting contains channel IDs, check if this channel is allowed
    if add_message_setting != "1" and add_message_setting.lower() != "true":
        allowed_channels = [ch.strip() for ch in add_message_setting.split(",")]
        if channel_id not in allowed_channels:
            raise Exception(f"Message posting not allowed for channel {channel_id}")
    
    client = get_slack_client()
    
    # Resolve channel name to ID
    resolved_channel_id = client.resolve_channel_id(channel_id)
    
    # Convert markdown to Slack format if needed
    text = payload
    if content_type == "text/markdown":
        # Basic markdown to Slack conversion
        text = text.replace("**", "*").replace("__", "_")
    
    params = {
        "channel": resolved_channel_id,
        "text": text
    }
    
    if thread_ts:
        params["thread_ts"] = thread_ts
    
    # Use POST for chat.postMessage
    url = f"{client.base_url}/chat.postMessage"
    response = requests.post(url, headers=client.headers, json=params)
    
    if response.status_code != 200:
        raise Exception(f"Slack API error: {response.status_code} - {response.text}")
        
    data = response.json()
    if not data.get("ok"):
        raise Exception(f"Slack API error: {data.get('error', 'Unknown error')}")
    
    return {
        "message": data.get("message", {}),
        "ts": data.get("ts"),
        "channel": data.get("channel")
    }

@mcp.tool
def conversations_search_messages(
    search_query: Optional[str] = None,
    filter_in_channel: Optional[str] = None,
    filter_in_im_or_mpim: Optional[str] = None,
    filter_users_with: Optional[str] = None,
    filter_users_from: Optional[str] = None,
    filter_date_before: Optional[str] = None,
    filter_date_after: Optional[str] = None,
    filter_date_on: Optional[str] = None,
    filter_date_during: Optional[str] = None,
    filter_threads_only: bool = False,
    cursor: str = "",
    limit: int = 20
) -> Dict[str, Any]:
    """
    Search messages in conversations using filters
    
    Args:
        search_query: Search query to filter messages or full URL of Slack message
        filter_in_channel: Filter messages in specific channel by ID or name (#general)
        filter_in_im_or_mpim: Filter messages in DM/MPIM by ID or name (@username_dm)
        filter_users_with: Filter messages with specific user by ID or display name
        filter_users_from: Filter messages from specific user by ID or display name
        filter_date_before: Filter messages before date (YYYY-MM-DD, July, Yesterday, Today)
        filter_date_after: Filter messages after date (YYYY-MM-DD, July, Yesterday, Today)
        filter_date_on: Filter messages on specific date (YYYY-MM-DD, July, Yesterday, Today)
        filter_date_during: Filter messages during period (July, Yesterday, Today)
        filter_threads_only: If true, include only messages from threads
        cursor: Cursor for pagination
        limit: Maximum number of items to return (1-100)
    """
    client = get_slack_client()
    
    if not search_query and not any([filter_in_channel, filter_in_im_or_mpim, filter_users_with, filter_users_from]):
        raise Exception("search_query is required when no filters are provided")
    
    # Check if search_query is a Slack URL
    if search_query and "slack.com/archives/" in search_query:
        # Extract channel and timestamp from URL
        # Format: https://slack.com/archives/C1234567890/p1234567890123456
        parts = search_query.split('/')
        if len(parts) >= 6:
            channel_id = parts[-2]
            ts_part = parts[-1]
            if ts_part.startswith('p'):
                # Convert permalink timestamp to message timestamp
                ts = ts_part[1:]  # Remove 'p' prefix
                ts = f"{ts[:10]}.{ts[10:]}"  # Insert decimal point
                
                # Get single message
                params = {"channel": channel_id, "ts": ts, "limit": 1}
                data = client._make_request("conversations.history", params)
                return {
                    "messages": data.get("messages", []),
                    "total": len(data.get("messages", [])),
                    "next_cursor": None
                }
    
    # Build search query with filters
    query_parts = []
    if search_query:
        query_parts.append(search_query)
    
    if filter_in_channel:
        # Resolve channel name to ID for search
        resolved_channel = client.resolve_channel_id(filter_in_channel)
        query_parts.append(f"in:{resolved_channel}")
    if filter_in_im_or_mpim:
        # Resolve channel name to ID for search
        resolved_channel = client.resolve_channel_id(filter_in_im_or_mpim)
        query_parts.append(f"in:{resolved_channel}")
    if filter_users_with:
        # Resolve user name to ID for search
        resolved_user = client.resolve_user_id(filter_users_with)
        query_parts.append(f"with:{resolved_user}")
    if filter_users_from:
        # Resolve user name to ID for search
        resolved_user = client.resolve_user_id(filter_users_from)
        query_parts.append(f"from:{resolved_user}")
    if filter_date_before:
        query_parts.append(f"before:{filter_date_before}")
    if filter_date_after:
        query_parts.append(f"after:{filter_date_after}")
    if filter_date_on:
        query_parts.append(f"on:{filter_date_on}")
    if filter_date_during:
        query_parts.append(f"during:{filter_date_during}")
    
    if filter_threads_only:
        query_parts.append("has:thread")
    
    query = " ".join(query_parts)
    
    params = {
        "query": query,
        "count": min(max(limit, 1), 100),
        "sort": "timestamp"
    }
    
    if cursor:
        params["cursor"] = cursor
    
    data = client._make_request("search.messages", params)
    
    messages = data.get("messages", {})
    return {
        "messages": messages.get("matches", []),
        "total": messages.get("total", 0),
        "next_cursor": data.get("response_metadata", {}).get("next_cursor")
    }

@mcp.tool
def user_info(
    user_ids: str,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Get detailed information about one or more users (cache-first approach)
    
    Args:
        user_ids: Single user ID/name or comma-separated list (@john, @jane, U123456789)
        use_cache: If True, try cache first before API call (default: True)
    
    Returns:
        User information for all requested users
    """
    client = get_slack_client()
    
    # Parse user IDs (support both single and multiple)
    user_list = [u.strip() for u in user_ids.split(",")]
    results = []
    cache_hits = 0
    api_calls = 0
    
    # Load cache once for all users
    cached_users = {}
    if use_cache:
        try:
            users_data = client.get_cached_users()
            cached_users = {user.get("id"): user for user in users_data if user.get("id")}
        except Exception as cache_error:
            print(f"Cache loading failed: {cache_error}")
    
    for user_input in user_list:
        if not user_input:
            continue
            
        # Resolve user name to ID
        try:
            resolved_user_id = client.resolve_user_id(user_input)
        except Exception as e:
            results.append({
                "input": user_input,
                "error": f"Could not resolve user: {str(e)}",
                "success": False
            })
            continue
        
        # Try cache first if enabled
        user_found = False
        if use_cache and resolved_user_id in cached_users:
            results.append({
                "input": user_input,
                "resolved_id": resolved_user_id,
                "user": cached_users[resolved_user_id],
                "source": "cache",
                "success": True
            })
            cache_hits += 1
            user_found = True
        
        # Fall back to API call if cache miss or disabled
        if not user_found:
            try:
                data = client._make_request("users.info", {"user": resolved_user_id})
                results.append({
                    "input": user_input,
                    "resolved_id": resolved_user_id,
                    "user": data.get("user", {}),
                    "source": "api",
                    "success": True
                })
                api_calls += 1
            except Exception as e:
                # If API fails, try cache as last resort
                if resolved_user_id in cached_users:
                    results.append({
                        "input": user_input,
                        "resolved_id": resolved_user_id,
                        "user": cached_users[resolved_user_id],
                        "source": "cache_fallback",
                        "success": True,
                        "warning": f"API failed, using cached data: {str(e)}"
                    })
                    cache_hits += 1
                else:
                    results.append({
                        "input": user_input,
                        "resolved_id": resolved_user_id,
                        "error": str(e),
                        "success": False
                    })
    
    return {
        "users": results,
        "summary": {
            "total_requested": len(user_list),
            "successful": len([r for r in results if r.get("success")]),
            "failed": len([r for r in results if not r.get("success")]),
            "cache_hits": cache_hits,
            "api_calls": api_calls
        },
        "cache_file": client.users_cache_file if use_cache else None,
        "note": f"Cache: {cache_hits} hits, API: {api_calls} calls",
        "success": True
    }

@mcp.tool
def users_list(
    filter_type: str = "active",
    include_bots: bool = False,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get a list of users with basic info (always uses cache for performance)
    
    Args:
        filter_type: Type of users to return ("active", "all", "admins", "deleted")
        include_bots: Include bot users in results
        limit: Maximum number of users to return
    
    Returns:
        List of users with basic information
    """
    client = get_slack_client()
    
    try:
        # Always use cache for listing users (performance)
        users_data = client.get_cached_users()
        
        # Filter users based on criteria
        filtered_users = []
        for user in users_data:
            # Skip deleted users unless specifically requested
            if filter_type == "active" and user.get("deleted", False):
                continue
            if filter_type == "deleted" and not user.get("deleted", False):
                continue
            if filter_type == "admins" and not user.get("is_admin", False):
                continue
            
            # Skip bots unless specifically requested
            if not include_bots and user.get("is_bot", False):
                continue
            
            # Add simplified user info
            filtered_users.append({
                "id": user.get("id"),
                "username": user.get("name", "unknown"),
                "real_name": user.get("real_name", "Unknown"),
                "display_name": user.get("profile", {}).get("display_name", ""),
                "is_admin": user.get("is_admin", False),
                "is_bot": user.get("is_bot", False),
                "is_deleted": user.get("deleted", False),
                "timezone": user.get("tz", ""),
                "title": user.get("profile", {}).get("title", "")
            })
        
        # Apply limit
        if limit > 0:
            filtered_users = filtered_users[:limit]
        
        return {
            "users": filtered_users,
            "summary": {
                "total_users": len(filtered_users),
                "filter_applied": filter_type,
                "include_bots": include_bots,
                "limit_applied": limit if len(filtered_users) >= limit else None
            },
            "cache_file": client.users_cache_file,
            "source": "cache",
            "success": True,
            "note": "User listing always uses cache for performance"
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False,
            "note": "Failed to load users from cache"
        }

@mcp.tool
def channel_info(
    channel_id: str,
    include_locale: bool = False,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Get detailed information about a specific channel (cache-first approach)
    
    Args:
        channel_id: Channel ID (C1234567890) or name (#general, @user_dm)
        include_locale: Include locale information
        use_cache: If True, try cache first before API call (default: True)
    
    Returns:
        Detailed channel information including topic, purpose, member count
    """
    client = get_slack_client()
    
    # Resolve channel name to ID
    resolved_channel_id = client.resolve_channel_id(channel_id)
    
    # Try cache first if enabled
    if use_cache:
        try:
            channels = client.get_cached_channels()
            for channel in channels:
                if channel.get("id") == resolved_channel_id:
                    return {
                        "channel": channel,
                        "source": "cache",
                        "cache_file": client.channels_cache_file,
                        "success": True,
                        "note": "Data from cache. Set use_cache=false for fresh API data."
                    }
        except Exception as cache_error:
            # If cache fails, fall back to API
            pass
    
    # Fall back to API call if cache miss or disabled
    params = {
        "channel": resolved_channel_id,
        "include_locale": include_locale
    }
    
    try:
        data = client._make_request("conversations.info", params)
        return {
            "channel": data.get("channel", {}),
            "source": "api",
            "success": True,
            "note": "Fresh data from Slack API"
        }
    except Exception as e:
        # If API also fails, try cache as last resort
        if not use_cache:
            try:
                channels = client.get_cached_channels()
                for channel in channels:
                    if channel.get("id") == resolved_channel_id:
                        return {
                            "channel": channel,
                            "source": "cache_fallback",
                            "success": True,
                            "warning": f"API failed ({str(e)}), using cached data instead"
                        }
            except:
                pass
        
        return {
            "error": str(e),
            "success": False,
            "channel_id": channel_id,
            "resolved_channel_id": resolved_channel_id,
            "note": "Both cache and API failed"
        }

@mcp.tool
def channels_detailed(
    channel_types: str = "public_channel,private_channel",
    sort: Optional[str] = None,
    limit: int = 100,
    include_detailed_info: bool = False
) -> Dict[str, Any]:
    """
    Get comprehensive list of channels with all details (EFFICIENT - avoids redundant API calls)
    
    This tool combines channels_list + channel_info functionality in a single efficient call.
    It uses channels_list (which already contains topic, purpose, member count) instead of 
    making separate channel_info calls for each channel.
    
    Args:
        channel_types: Comma-separated channel types (public_channel,private_channel,mpim,im)
        sort: Type of sorting (popularity - sort by number of members)
        limit: Maximum number of channels to return (1-999)
        include_detailed_info: If True, makes additional API calls for extra details (slower)
    
    Returns:
        Comprehensive channel information without redundant API calls
    """
    client = get_slack_client()
    
    # Validate channel types
    valid_types = {"mpim", "im", "public_channel", "private_channel"}
    types = [t.strip() for t in channel_types.split(",")]
    
    for t in types:
        if t not in valid_types:
            raise Exception(f"Invalid channel type: {t}. Valid types: {', '.join(valid_types)}")
    
    params = {
        "types": channel_types,
        "limit": min(max(limit, 1), 999)
    }
    
    try:
        # Single API call to get all channel data
        data = client._make_request("conversations.list", params)
        channels = data.get("channels", [])
        
        # Sort by popularity if requested
        if sort == "popularity":
            channels.sort(key=lambda x: x.get("num_members", 0), reverse=True)
        
        # Enhance with cached user data for DMs
        users_cache = {}
        try:
            cached_users = client.get_cached_users()
            users_cache = {user.get("id"): user for user in cached_users if user.get("id")}
        except:
            pass
        
        # Process channels and add helpful information
        processed_channels = []
        detailed_calls = 0
        
        for channel in channels:
            processed_channel = dict(channel)  # Copy original data
            
            # Add user info for DMs
            if channel.get("is_im") and channel.get("user"):
                user_id = channel["user"]
                if user_id in users_cache:
                    processed_channel["user_info"] = {
                        "name": users_cache[user_id].get("name"),
                        "real_name": users_cache[user_id].get("real_name"),
                        "display_name": users_cache[user_id].get("profile", {}).get("display_name")
                    }
            
            # Add detailed info only if explicitly requested (makes extra API calls)
            if include_detailed_info and not channel.get("is_im"):
                try:
                    detail_data = client._make_request("conversations.info", {"channel": channel["id"]})
                    detailed_info = detail_data.get("channel", {})
                    # Merge additional details without overwriting existing data
                    for key, value in detailed_info.items():
                        if key not in processed_channel or not processed_channel[key]:
                            processed_channel[key] = value
                    processed_channel["detailed_source"] = "api"
                    detailed_calls += 1
                except:
                    processed_channel["detailed_source"] = "unavailable"
            
            processed_channels.append(processed_channel)
        
        return {
            "channels": processed_channels,
            "total_channels": len(processed_channels),
            "api_calls": 1 + detailed_calls,  # 1 for conversations.list + detailed calls
            "efficiency_note": f"Used 1 conversations.list call instead of {len(processed_channels)} individual channel_info calls",
            "detailed_calls": detailed_calls if include_detailed_info else 0,
            "next_cursor": data.get("response_metadata", {}).get("next_cursor"),
            "success": True,
            "performance": "optimized" if not include_detailed_info else "detailed_mode"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False,
            "note": "Failed to get channels list"
        }

@mcp.tool
def bulk_conversations_history(
    channel_ids: str,
    limit: str = "1d", 
    include_user_details: bool = True,
    include_activity_messages: bool = False,
    filter_user: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get messages from multiple channels efficiently (BULK OPERATION - avoids multiple API calls)
    
    This tool gets conversation history from multiple channels in one operation,
    perfect for finding a user's messages across channels or getting recent activity
    from multiple channels without making N separate conversations_history calls.
    
    Args:
        channel_ids: Comma-separated channel IDs/names (#general, #random, @chris_dm)
        limit: Time format (1d, 1w, 30d) or number (50) - applies to each channel
        include_user_details: Include user name/real_name for each message
        include_activity_messages: Include join/leave messages
        filter_user: Only return messages from this user (@chris, U123456, or chris.doe)
    
    Returns:
        Messages from all channels with channel context and efficiency metrics
    """
    client = get_slack_client()
    
    # Parse channel list
    channel_list = [c.strip() for c in channel_ids.split(",")]
    
    results = []
    total_messages = 0
    api_calls = 0
    failed_channels = []
    
    # Load user cache once for all channels (efficiency)
    users_cache = {}
    if include_user_details or filter_user:
        try:
            cached_users = client.get_cached_users()
            users_cache = {user.get("id"): user for user in cached_users if user.get("id")}
            # Also create name-to-id lookup for filtering
            users_name_lookup = {}
            for user in cached_users:
                if user.get("name"):
                    users_name_lookup[user["name"]] = user["id"]
                if user.get("real_name"):
                    users_name_lookup[user["real_name"].lower()] = user["id"]
                profile = user.get("profile", {})
                if profile.get("display_name"):
                    users_name_lookup[profile["display_name"]] = user["id"]
        except:
            users_name_lookup = {}
    
    # Resolve filter_user to user ID if provided
    filter_user_id = None
    if filter_user:
        if filter_user.startswith("@"):
            filter_user_clean = filter_user[1:]
            if filter_user_clean in users_name_lookup:
                filter_user_id = users_name_lookup[filter_user_clean]
        elif filter_user.startswith("U") and len(filter_user) == 11:
            filter_user_id = filter_user
        elif filter_user in users_name_lookup:
            filter_user_id = users_name_lookup[filter_user]
        elif filter_user.lower() in users_name_lookup:
            filter_user_id = users_name_lookup[filter_user.lower()]
    
    # Process each channel
    for channel_input in channel_list:
        if not channel_input:
            continue
            
        try:
            # Resolve channel name to ID
            resolved_channel_id = client.resolve_channel_id(channel_input)
            
            # Prepare API parameters
            params = {
                "channel": resolved_channel_id,
                "include_all_metadata": include_activity_messages
            }
            
            # Apply limit
            limit_params = parse_limit(limit)
            params.update(limit_params)
            
            # Make API call
            data = client._make_request("conversations.history", params)
            messages = data.get("messages", [])
            api_calls += 1
            
            # Filter by user if specified
            if filter_user_id:
                messages = [msg for msg in messages if msg.get("user") == filter_user_id]
            
            # Enhance messages with user details
            if include_user_details and messages:
                for message in messages:
                    user_id = message.get("user")
                    if user_id and user_id in users_cache:
                        user_data = users_cache[user_id]
                        message["user_details"] = {
                            "name": user_data.get("name"),
                            "real_name": user_data.get("real_name"),
                            "display_name": user_data.get("profile", {}).get("display_name")
                        }
            
            # Add channel context to each message
            for message in messages:
                message["channel_context"] = {
                    "channel_id": resolved_channel_id,
                    "channel_input": channel_input
                }
            
            total_messages += len(messages)
            
            results.append({
                "channel_id": resolved_channel_id,
                "channel_input": channel_input,
                "messages": messages,
                "message_count": len(messages),
                "success": True
            })
            
        except Exception as e:
            failed_channels.append({
                "channel_input": channel_input,
                "error": str(e)
            })
    
    return {
        "channels": results,
        "summary": {
            "total_channels": len(channel_list),
            "successful_channels": len(results),
            "failed_channels": len(failed_channels),
            "total_messages": total_messages,
            "api_calls": api_calls,
            "filter_user": filter_user,
            "filter_user_id": filter_user_id
        },
        "failed_channels": failed_channels,
        "efficiency_note": f"Retrieved messages from {len(results)} channels with {api_calls} API calls instead of making {len(channel_list)} separate conversations_history calls",
        "success": True
    }

@mcp.tool
def channel_members(
    channel_id: str,
    limit: int = 100,
    cursor: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get list of members in a channel with their details
    
    Args:
        channel_id: Channel ID (C1234567890) or name (#general)
        limit: Maximum number of members to return
        cursor: Cursor for pagination
    
    Returns:
        List of channel members with user details
    """
    client = get_slack_client()
    
    # Resolve channel name to ID
    resolved_channel_id = client.resolve_channel_id(channel_id)
    
    params = {
        "channel": resolved_channel_id,
        "limit": min(limit, 1000)
    }
    
    if cursor:
        params["cursor"] = cursor
    
    try:
        data = client._make_request("conversations.members", params)
        member_ids = data.get("members", [])
        
        # Get cached users for detailed information
        users = client.get_cached_users()
        user_lookup = {user["id"]: user for user in users}
        
        # Enrich member list with user details
        members_with_details = []
        for member_id in member_ids:
            user_data = user_lookup.get(member_id, {"id": member_id})
            members_with_details.append({
                "id": member_id,
                "username": user_data.get("name", "unknown"),
                "real_name": user_data.get("real_name", "Unknown"),
                "display_name": user_data.get("profile", {}).get("display_name", ""),
                "is_admin": user_data.get("is_admin", False),
                "is_bot": user_data.get("is_bot", False),
                "deleted": user_data.get("deleted", False)
            })
        
        return {
            "members": members_with_details,
            "member_count": len(members_with_details),
            "has_more": data.get("response_metadata", {}).get("next_cursor") is not None,
            "next_cursor": data.get("response_metadata", {}).get("next_cursor"),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False,
            "channel_id": channel_id,
            "resolved_channel_id": resolved_channel_id
        }

@mcp.tool
def user_presence(
    user_id: str
) -> Dict[str, Any]:
    """
    Get user's presence status (online, away, etc.)
    
    Args:
        user_id: User ID (U1234567890) or username (@john)
    
    Returns:
        User presence information
    """
    client = get_slack_client()
    
    # Resolve user name to ID
    resolved_user_id = client.resolve_user_id(user_id)
    
    try:
        data = client._make_request("users.getPresence", {"user": resolved_user_id})
        return {
            "presence": data.get("presence"),
            "online": data.get("online"),
            "auto_away": data.get("auto_away"),
            "manual_away": data.get("manual_away"),
            "connection_count": data.get("connection_count"),
            "last_activity": data.get("last_activity"),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False,
            "user_id": user_id,
            "resolved_user_id": resolved_user_id
        }

@mcp.tool
def workspace_info() -> Dict[str, Any]:
    """
    Get information about the current Slack workspace/team
    
    Note: Requires 'team:read' scope. If missing, returns basic info from other sources.
    
    Returns:
        Workspace information including name, domain, plan details
    """
    client = get_slack_client()
    
    try:
        data = client._make_request("team.info")
        team = data.get("team", {})
        
        return {
            "id": team.get("id"),
            "name": team.get("name"),
            "domain": team.get("domain"),
            "email_domain": team.get("email_domain"),
            "icon": team.get("icon", {}),
            "enterprise_id": team.get("enterprise_id"),
            "enterprise_name": team.get("enterprise_name"),
            "success": True,
            "source": "team.info API"
        }
    except Exception as e:
        # Fallback: try to get workspace info from other sources
        error_msg = str(e)
        if "missing_scope" in error_msg:
            try:
                # Try to get basic info from users list (which usually works)
                users_data = client._make_request("users.list", {"limit": 1})
                if users_data.get("members"):
                    team_id = users_data["members"][0].get("team_id")
                    
                    return {
                        "id": team_id,
                        "name": "Unknown (missing team:read scope)",
                        "domain": "Unknown",
                        "success": True,
                        "source": "derived from users.list",
                        "note": "Limited info due to missing 'team:read' scope. Add this scope for full workspace details."
                    }
            except:
                pass
        
        return {
            "error": error_msg,
            "success": False,
            "note": "This tool requires 'team:read' scope. Please add this scope to your Slack app for full workspace information.",
            "required_scope": "team:read"
        }

@mcp.tool
def channels_list(
    channel_types: str,
    sort: Optional[str] = None,
    limit: int = 100,
    cursor: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get list of channels
    
    Args:
        channel_types: Comma-separated channel types (mpim,im,public_channel,private_channel)
        sort: Type of sorting (popularity - sort by number of members/participants)
        limit: Maximum number of items to return (1-1000, max 999)
        cursor: Cursor for pagination
    """
    client = get_slack_client()
    
    # Validate channel types
    valid_types = {"mpim", "im", "public_channel", "private_channel"}
    types = [t.strip() for t in channel_types.split(",")]
    
    for t in types:
        if t not in valid_types:
            raise Exception(f"Invalid channel type: {t}. Valid types: {', '.join(valid_types)}")
    
    params = {
        "types": channel_types,
        "limit": min(max(limit, 1), 999)
    }
    
    if cursor:
        params["cursor"] = cursor
    
    data = client._make_request("conversations.list", params)
    
    channels = data.get("channels", [])
    
    # Sort by popularity if requested
    if sort == "popularity":
        channels.sort(key=lambda x: x.get("num_members", 0), reverse=True)
    
    return {
        "channels": channels,
        "next_cursor": data.get("response_metadata", {}).get("next_cursor")
    }

@mcp.tool
def message_permalink(
    channel_id: str,
    message_ts: str
) -> Dict[str, Any]:
    """
    Get a permanent link to a specific message
    
    Args:
        channel_id: Channel ID (C1234567890) or name (#general)
        message_ts: Message timestamp (1234567890.123456)
    
    Returns:
        Permalink URL to the message
    """
    client = get_slack_client()
    
    # Resolve channel name to ID
    resolved_channel_id = client.resolve_channel_id(channel_id)
    
    try:
        data = client._make_request("chat.getPermalink", {
            "channel": resolved_channel_id,
            "message_ts": message_ts
        })
        return {
            "permalink": data.get("permalink"),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False,
            "channel_id": channel_id,
            "message_ts": message_ts
        }

@mcp.tool
def set_channel_topic(
    channel_id: str,
    topic: str
) -> Dict[str, Any]:
    """
    Set the topic for a channel
    
    Args:
        channel_id: Channel ID (C1234567890) or name (#general)
        topic: New topic text
    
    Returns:
        Success status and topic information
    """
    client = get_slack_client()
    
    # Resolve channel name to ID
    resolved_channel_id = client.resolve_channel_id(channel_id)
    
    try:
        data = client._make_request("conversations.setTopic", {
            "channel": resolved_channel_id,
            "topic": topic
        })
        return {
            "topic": data.get("topic"),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False,
            "channel_id": channel_id,
            "resolved_channel_id": resolved_channel_id
        }

@mcp.tool
def set_channel_purpose(
    channel_id: str,
    purpose: str
) -> Dict[str, Any]:
    """
    Set the purpose for a channel
    
    Args:
        channel_id: Channel ID (C1234567890) or name (#general)
        purpose: New purpose text
    
    Returns:
        Success status and purpose information
    """
    client = get_slack_client()
    
    # Resolve channel name to ID
    resolved_channel_id = client.resolve_channel_id(channel_id)
    
    try:
        data = client._make_request("conversations.setPurpose", {
            "channel": resolved_channel_id,
            "purpose": purpose
        })
        return {
            "purpose": data.get("purpose"),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False,
            "channel_id": channel_id,
            "resolved_channel_id": resolved_channel_id
        }

@mcp.tool
def add_reaction(
    channel_id: str,
    message_ts: str,
    emoji_name: str
) -> Dict[str, Any]:
    """
    Add an emoji reaction to a message
    
    Args:
        channel_id: Channel ID (C1234567890) or name (#general)
        message_ts: Message timestamp (1234567890.123456)
        emoji_name: Emoji name without colons (e.g., 'thumbsup', 'heart')
    
    Returns:
        Success status
    """
    client = get_slack_client()
    
    # Resolve channel name to ID
    resolved_channel_id = client.resolve_channel_id(channel_id)
    
    try:
        data = client._make_request("reactions.add", {
            "channel": resolved_channel_id,
            "timestamp": message_ts,
            "name": emoji_name
        })
        return {
            "success": data.get("ok", False)
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False,
            "channel_id": channel_id,
            "message_ts": message_ts,
            "emoji_name": emoji_name
        }

@mcp.tool
def files_list(
    channel_id: Optional[str] = None,
    user_id: Optional[str] = None,
    count: int = 10,
    types: str = "all"
) -> Dict[str, Any]:
    """
    List files in workspace, optionally filtered by channel or user
    
    Args:
        channel_id: Channel ID (C1234567890) or name (#general) to filter by
        user_id: User ID (U1234567890) or username (@john) to filter by
        count: Number of files to return (1-1000)
        types: File types (all, images, gdocs, zips, pdfs, etc.)
    
    Returns:
        List of files with metadata
    """
    client = get_slack_client()
    
    params = {
        "count": min(count, 1000),
        "types": types
    }
    
    if channel_id:
        resolved_channel_id = client.resolve_channel_id(channel_id)
        params["channel"] = resolved_channel_id
    
    if user_id:
        resolved_user_id = client.resolve_user_id(user_id)
        params["user"] = resolved_user_id
    
    try:
        data = client._make_request("files.list", params)
        return {
            "files": data.get("files", []),
            "paging": data.get("paging", {}),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False,
            "channel_id": channel_id,
            "user_id": user_id
        }

@mcp.tool
def initialize_cache() -> Dict[str, Any]:
    """
    Initialize both user and channel caches by fetching fresh data
    
    Returns:
        Status of cache initialization with file locations and sizes
    """
    client = get_slack_client()
    
    try:
        # Force cache creation by calling both cache methods
        users = client.get_cached_users()
        channels = client.get_cached_channels()
        
        # Get file info after creation
        def get_file_size(file_path: str) -> float:
            try:
                return round(os.path.getsize(file_path) / 1024, 2) if os.path.exists(file_path) else 0
            except:
                return 0
        
        users_size = get_file_size(client.users_cache_file)
        channels_size = get_file_size(client.channels_cache_file)
        
        return {
            "success": True,
            "message": "Cache initialized successfully",
            "users_cache": {
                "path": client.users_cache_file,
                "size_kb": users_size,
                "count": len(users)
            },
            "channels_cache": {
                "path": client.channels_cache_file,
                "size_kb": channels_size,
                "count": len(channels)
            },
            "total_cache_size_kb": users_size + channels_size
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool
def cache_info() -> Dict[str, Any]:
    """
    Get information about cache file locations, sizes, and last updated times
    
    Returns:
        Cache file information including paths, existence, sizes, and timestamps
    """
    client = get_slack_client()
    
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """Get detailed file information"""
        abs_path = os.path.abspath(file_path)
        
        if os.path.exists(abs_path):
            stat = os.stat(abs_path)
            return {
                "exists": True,
                "absolute_path": abs_path,
                "size_bytes": stat.st_size,
                "size_kb": round(stat.st_size / 1024, 2),
                "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "age_hours": round((datetime.now().timestamp() - stat.st_mtime) / 3600, 2),
                "is_fresh": stat.st_mtime > (datetime.now().timestamp() - 24 * 3600)  # Fresh if < 24h old
            }
        else:
            return {
                "exists": False,
                "absolute_path": abs_path,
                "size_bytes": 0,
                "size_kb": 0,
                "last_modified": None,
                "age_hours": None,
                "is_fresh": False
            }
    
    users_info = get_file_info(client.users_cache_file)
    channels_info = get_file_info(client.channels_cache_file)
    
    # Get cache directory info
    cache_dir = os.path.dirname(os.path.abspath(client.users_cache_file))
    
    return {
        "cache_directory": cache_dir,
        "users_cache": {
            "configured_path": client.users_cache_file,
            **users_info
        },
        "channels_cache": {
            "configured_path": client.channels_cache_file,
            **channels_info
        },
        "environment_variables": {
            "SLACK_MCP_USERS_CACHE": os.environ.get("SLACK_MCP_USERS_CACHE", "Not set (using default)"),
            "SLACK_MCP_CHANNELS_CACHE": os.environ.get("SLACK_MCP_CHANNELS_CACHE", "Not set (using default)")
        },
        "recommendations": {
            "users_cache_fresh": users_info["is_fresh"] if users_info["exists"] else False,
            "channels_cache_fresh": channels_info["is_fresh"] if channels_info["exists"] else False,
            "total_cache_size_kb": users_info["size_kb"] + channels_info["size_kb"]
        },
        "success": True
    }

@mcp.tool
def check_permissions() -> Dict[str, Any]:
    """
    Check what Slack API permissions/scopes are available with current token
    
    Returns:
        Results of testing various API endpoints to determine available permissions
    """
    client = get_slack_client()
    
    # Test various endpoints to see what works
    permissions = {
        "users:read": {"endpoint": "users.list", "status": "unknown"},
        "channels:read": {"endpoint": "conversations.list (public_channel)", "status": "unknown"},
        "groups:read": {"endpoint": "conversations.list (private_channel)", "status": "unknown"},
        "im:read": {"endpoint": "conversations.list (im)", "status": "unknown"},
        "mpim:read": {"endpoint": "conversations.list (mpim)", "status": "unknown"},
        "team:read": {"endpoint": "team.info", "status": "unknown"},
        "channels:history": {"endpoint": "conversations.history", "status": "unknown"},
        "chat:write": {"endpoint": "chat.postMessage", "status": "unknown"}
    }
    
    # Test users.list
    try:
        client._make_request("users.list", {"limit": 1})
        permissions["users:read"]["status"] = "✅ Available"
    except Exception as e:
        permissions["users:read"]["status"] = f"❌ Failed: {str(e)}"
    
    # Test different conversation types
    for scope, channel_type in [
        ("channels:read", "public_channel"),
        ("groups:read", "private_channel"), 
        ("im:read", "im"),
        ("mpim:read", "mpim")
    ]:
        try:
            client._make_request("conversations.list", {"types": channel_type, "limit": 1})
            permissions[scope]["status"] = "✅ Available"
        except Exception as e:
            permissions[scope]["status"] = f"❌ Failed: {str(e)}"
    
    # Test team.info
    try:
        client._make_request("team.info")
        permissions["team:read"]["status"] = "✅ Available"
    except Exception as e:
        permissions["team:read"]["status"] = f"❌ Failed: {str(e)}"
    
    # Count available vs failed
    available = len([p for p in permissions.values() if "✅" in p["status"]])
    failed = len([p for p in permissions.values() if "❌" in p["status"]])
    
    return {
        "permissions": permissions,
        "summary": {
            "available_scopes": available,
            "failed_scopes": failed,
            "total_tested": len(permissions)
        },
        "recommendations": {
            "cache_creation": "✅ Possible" if available > 0 else "❌ Needs permissions",
            "name_resolution": "✅ Possible" if permissions["channels:read"]["status"].startswith("✅") else "❌ Needs channels:read",
            "messaging": "✅ Possible" if permissions["channels:history"]["status"].startswith("✅") else "⚠️ Limited (needs channels:history)"
        },
        "success": True
    }

@mcp.tool
def clear_cache(
    cache_type: str = "both"
) -> Dict[str, Any]:
    """
    Clear cache files to force refresh from Slack API
    
    Args:
        cache_type: Which cache to clear ("users", "channels", or "both")
    
    Returns:
        Status of cache clearing operation
    """
    client = get_slack_client()
    
    results = {"success": True, "cleared": []}
    
    try:
        if cache_type in ["users", "both"]:
            if os.path.exists(client.users_cache_file):
                os.remove(client.users_cache_file)
                results["cleared"].append(f"Users cache: {client.users_cache_file}")
            else:
                results["cleared"].append("Users cache: (file didn't exist)")
        
        if cache_type in ["channels", "both"]:
            if os.path.exists(client.channels_cache_file):
                os.remove(client.channels_cache_file)
                results["cleared"].append(f"Channels cache: {client.channels_cache_file}")
            else:
                results["cleared"].append("Channels cache: (file didn't exist)")
        
        results["message"] = f"Cache cleared successfully. Files will be recreated on next API call."
        
    except Exception as e:
        results["success"] = False
        results["error"] = str(e)
    
    return results

@mcp.tool
def analytics_summary(
    date_range: str = "30d"
) -> Dict[str, Any]:
    """
    Get workspace analytics summary using cached data
    
    Args:
        date_range: Date range for analysis (7d, 30d, 90d)
    
    Returns:
        Analytics summary including user activity, channel stats, message counts
    """
    client = get_slack_client()
    
    try:
        # Get cached data for analysis
        users = client.get_cached_users()
        channels = client.get_cached_channels()
        
        # Basic analytics from cached data
        total_users = len([u for u in users if not u.get("deleted", False)])
        active_users = len([u for u in users if not u.get("deleted", False) and not u.get("is_bot", False)])
        bot_users = len([u for u in users if u.get("is_bot", False)])
        admin_users = len([u for u in users if u.get("is_admin", False)])
        
        public_channels = len([c for c in channels if not c.get("is_private", True) and not c.get("is_im", False) and not c.get("is_mpim", False)])
        private_channels = len([c for c in channels if c.get("is_private", True) and not c.get("is_im", False) and not c.get("is_mpim", False)])
        dm_channels = len([c for c in channels if c.get("is_im", False)])
        group_dm_channels = len([c for c in channels if c.get("is_mpim", False)])
        
        return {
            "date_range": date_range,
            "user_stats": {
                "total_users": total_users,
                "active_users": active_users,
                "bot_users": bot_users,
                "admin_users": admin_users
            },
            "channel_stats": {
                "public_channels": public_channels,
                "private_channels": private_channels,
                "dm_channels": dm_channels,
                "group_dm_channels": group_dm_channels,
                "total_channels": len(channels)
            },
            "success": True,
            "note": "Basic analytics from cached data. For detailed activity metrics, use conversations_search_messages with date filters."
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

@mcp.resource("slack://{workspace}/channels")
def get_channels_directory(workspace: str) -> str:
    """
    Directory of Channels - CSV format with channel metadata
    
    Args:
        workspace: Slack workspace name
    
    Returns:
        CSV directory of all channels in the workspace
    """
    client = get_slack_client()
    
    # Use cached channels data
    all_channels = client.get_cached_channels()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["id", "name", "topic", "purpose", "memberCount"])
    
    # Write channel data
    for channel in all_channels:
        name = channel.get("name", "")
        if channel.get("is_im"):
            name = f"@{name}_dm"
        elif channel.get("is_mpim"):
            name = f"@{name}_group"
        elif name:
            name = f"#{name}"
        
        writer.writerow([
            channel.get("id", ""),
            name,
            channel.get("topic", {}).get("value", ""),
            channel.get("purpose", {}).get("value", ""),
            channel.get("num_members", 0)
        ])
    
    return output.getvalue()

@mcp.resource("slack://{workspace}/users")
def get_users_directory(workspace: str) -> str:
    """
    Directory of Users - CSV format with user metadata
    
    Args:
        workspace: Slack workspace name
    
    Returns:
        CSV directory of all users in the workspace
    """
    client = get_slack_client()
    
    # Use cached users data
    users = client.get_cached_users()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["userID", "userName", "realName"])
    
    # Write user data
    for user in users:
        if not user.get("deleted", False):  # Skip deleted users
            writer.writerow([
                user.get("id", ""),
                user.get("name", ""),
                user.get("real_name", "")
            ])
    
    return output.getvalue()


def main():
    """Main entry point for the slack-mcp-server command."""
    # Run server with HTTP transport
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
        path="/mcp"
    )

if __name__ == "__main__":
    main()