"""Member management endpoint handlers"""

from typing import List
from ..models import RoUser
from ..utils import validate_discord_id, validate_roblox_id
from ..exceptions import ValidationError

class MemberEndpoints:
    """Handles member-related API endpoints"""
    
    def __init__(self, client):
        self.client = client
    
    def get_member(self, guild_id: str, user_id: str) -> RoUser:
        """
        Get RoUser information for a Discord user in a guild
        
        Args:
            guild_id (str): Discord guild ID
            user_id (str): Discord user ID
            
        Returns:
            RoUser: User information including linked Roblox account
            
        Raises:
            ValidationError: Invalid parameters
            AuthenticationError: Invalid or expired token
            NotFoundError: Guild or user not found
        """
        guild_id = validate_discord_id(guild_id)
        user_id = validate_discord_id(user_id)
        
        data = self.client._make_request('GET', f'/guilds/{guild_id}/members/{user_id}')
        return RoUser(**data)
    
    def get_members_by_roblox_id(self, guild_id: str, roblox_id: int) -> List[str]:
        """
        Get Discord user IDs linked to a Roblox account in a guild
        
        Args:
            guild_id (str): Discord guild ID  
            roblox_id (int): Roblox user ID
            
        Returns:
            List[str]: List of Discord user IDs
            
        Raises:
            ValidationError: Invalid parameters
            AuthenticationError: Invalid or expired token
            NotFoundError: Guild not found
        """
        guild_id = validate_discord_id(guild_id)
        roblox_id = validate_roblox_id(roblox_id)
        
        data = self.client._make_request('GET', f'/guilds/{guild_id}/members/roblox/{roblox_id}')
        return data  # API returns array of discord_ids