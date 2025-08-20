"""Data models for RoWifi API responses"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional, List

class DenylistKind(IntEnum):
    """Type of denylist entry"""
    USER = 0
    GROUP = 1

@dataclass
class RoUser:
    """Represents a linked Roblox user in a Discord guild"""
    discord_id: str
    roblox_id: int
    guild_id: str

@dataclass
class Denylist:
    """Represents a denylist entry"""
    id: int
    reason: str
    kind: DenylistKind
    user_id: Optional[int] = None
    group_id: Optional[int] = None

@dataclass
class XPUser:
    """Represents XP data for a user"""
    user_id: int
    xp: int

@dataclass
class DenylistCreate:
    """Data for creating a new denylist entry"""
    reason: str
    kind: DenylistKind
    user_id: Optional[int] = None
    group_id: Optional[int] = None
    code: Optional[str] = None

@dataclass
class SetRank:
    """Data for setting a user's rank"""
    user_id: int
    group_id: int
    rank_id: int