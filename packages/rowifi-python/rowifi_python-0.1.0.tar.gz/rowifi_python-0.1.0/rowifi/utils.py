"""Utility functions for validation and helpers"""

import re
from typing import Union
from .exceptions import ValidationError

def validate_discord_id(discord_id: Union[str, int]) -> str:
    """Validate and normalize Discord ID"""
    if isinstance(discord_id, int):
        discord_id = str(discord_id)
    
    if not isinstance(discord_id, str):
        raise ValidationError("Discord ID must be a string or integer")
    
    if not discord_id.isdigit():
        raise ValidationError("Discord ID must contain only digits")
    
    if len(discord_id) < 10 or len(discord_id) > 25:
        raise ValidationError("Discord ID must be between 10 and 25 digits")
    
    return discord_id

def validate_roblox_id(roblox_id: Union[str, int]) -> int:
    """Validate and normalize Roblox user ID"""
    try:
        roblox_id = int(roblox_id)
    except (ValueError, TypeError):
        raise ValidationError("Roblox ID must be a valid integer")
    
    if roblox_id <= 0:
        raise ValidationError("Roblox ID must be a positive integer")
    
    if roblox_id > 2**63 - 1:  # Max safe integer
        raise ValidationError("Roblox ID is too large")
    
    return roblox_id

def validate_xp(xp: Union[str, int]) -> int:
    """Validate XP value"""
    try:
        xp = int(xp)
    except (ValueError, TypeError):
        raise ValidationError("XP must be a valid integer")
    
    if xp < -2**31 or xp > 2**31 - 1:  # 32-bit integer range
        raise ValidationError("XP value out of valid range")
    
    return xp

def validate_rank_id(rank_id: Union[str, int]) -> int:
    """Validate Roblox group rank ID"""
    try:
        rank_id = int(rank_id)
    except (ValueError, TypeError):
        raise ValidationError("Rank ID must be a valid integer")
    
    if not (1 <= rank_id <= 255):
        raise ValidationError("Rank ID must be between 1 and 255")
    
    return rank_id

def validate_group_id(group_id: Union[str, int]) -> int:
    """Validate Roblox group ID"""
    try:
        group_id = int(group_id)
    except (ValueError, TypeError):
        raise ValidationError("Group ID must be a valid integer")
    
    if group_id <= 0:
        raise ValidationError("Group ID must be a positive integer")
    
    return group_id