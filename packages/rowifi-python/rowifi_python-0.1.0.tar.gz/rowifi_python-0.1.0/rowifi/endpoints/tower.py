"""XP/Tower system endpoint handlers"""

from typing import List, Dict, Optional, Union
from ..models import XPUser
from ..utils import validate_discord_id, validate_roblox_id, validate_xp
from ..exceptions import ValidationError

class TowerEndpoints:
    """Handles XP/Tower system API endpoints"""
    
    def __init__(self, client):
        self.client = client
    
    def get_user_xp(self, guild_id: str, roblox_id: int) -> XPUser:
        """
        Get XP information for a Roblox user
        
        Args:
            guild_id (str): Discord guild ID
            roblox_id (int): Roblox user ID
            
        Returns:
            XPUser: User XP information
            
        Raises:
            ValidationError: Invalid parameters
            AuthenticationError: Invalid or expired token
            NotFoundError: Guild or user not found
        """
        guild_id = validate_discord_id(guild_id)
        roblox_id = validate_roblox_id(roblox_id)
        
        data = self.client._make_request('GET', f'/guilds/{guild_id}/tower/xp/users/{roblox_id}')
        
        return XPUser(
            user_id=data['user_id'], 
            xp=data.get('xp', 0)
        )
    
    def set_user_xp(self, guild_id: str, roblox_id: int, xp: int) -> None:
        """
        Set absolute XP value for a user (overrides previous XP)
        
        Args:
            guild_id (str): Discord guild ID
            roblox_id (int): Roblox user ID
            xp (int): XP amount to set (must be non-negative)
            
        Raises:
            ValidationError: Invalid XP value or parameters
            AuthenticationError: Invalid or expired token
            NotFoundError: Guild or user not found
        """
        guild_id = validate_discord_id(guild_id)
        roblox_id = validate_roblox_id(roblox_id)
        xp = validate_xp(xp)
        
        if xp < 0:
            raise ValidationError("XP value cannot be negative when setting absolute XP")
        
        self.client._make_request('POST', f'/guilds/{guild_id}/tower/xp/users/{roblox_id}',
                                json_data={'xp': xp})
    
    def modify_user_xp(self, guild_id: str, roblox_id: int, xp_change: int) -> XPUser:
        """
        Add or remove XP from a user (can promote/demote based on XP binds)
        
        Args:
            guild_id (str): Discord guild ID
            roblox_id (int): Roblox user ID
            xp_change (int): Amount of XP to add (positive) or remove (negative)
            
        Returns:
            XPUser: Updated user XP information
            
        Raises:
            ValidationError: Invalid XP change or parameters
            AuthenticationError: Invalid or expired token
            NotFoundError: Guild or user not found
        """
        guild_id = validate_discord_id(guild_id)
        roblox_id = validate_roblox_id(roblox_id)
        xp_change = validate_xp(xp_change)
        
        self.client._make_request('PATCH', f'/guilds/{guild_id}/tower/xp/users/{roblox_id}',
                                json_data={'xp': xp_change})
        
        # Return updated XP info
        return self.get_user_xp(guild_id, roblox_id)
    
    def add_user_xp(self, guild_id: str, roblox_id: int, xp: int) -> XPUser:
        """
        Add XP to a user (convenience method)
        
        Args:
            guild_id (str): Discord guild ID
            roblox_id (int): Roblox user ID
            xp (int): Amount of XP to add (must be positive)
            
        Returns:
            XPUser: Updated user XP information
            
        Raises:
            ValidationError: Invalid XP amount (must be positive)
        """
        if xp <= 0:
            raise ValidationError("XP amount to add must be positive")
        
        return self.modify_user_xp(guild_id, roblox_id, xp)
    
    def remove_user_xp(self, guild_id: str, roblox_id: int, xp: int) -> XPUser:
        """
        Remove XP from a user (convenience method)
        
        Args:
            guild_id (str): Discord guild ID
            roblox_id (int): Roblox user ID
            xp (int): Amount of XP to remove (must be positive)
            
        Returns:
            XPUser: Updated user XP information
            
        Raises:
            ValidationError: Invalid XP amount (must be positive)
        """
        if xp <= 0:
            raise ValidationError("XP amount to remove must be positive")
        
        return self.modify_user_xp(guild_id, roblox_id, -xp)