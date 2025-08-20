"""Rank management endpoint handlers"""

from ..models import SetRank
from ..utils import validate_discord_id, validate_roblox_id, validate_group_id, validate_rank_id
from ..exceptions import ValidationError
from typing import List

class RankEndpoints:
    """Handles rank management API endpoints"""
    
    def __init__(self, client):
        self.client = client
    
    def set_user_rank(self, guild_id: str, user_id: int, group_id: int, rank_id: int) -> None:
        """
        Set rank of a Roblox user in a Roblox group
        
        Args:
            guild_id (str): Discord guild ID
            user_id (int): Roblox user ID
            group_id (int): Roblox group ID
            rank_id (int): Rank ID (1-255)
            
        Raises:
            ValidationError: Invalid parameters
            AuthenticationError: Invalid or expired token or insufficient permissions
            NotFoundError: Guild, user, or group not found
        """
        guild_id = validate_discord_id(guild_id)
        user_id = validate_roblox_id(user_id)
        group_id = validate_group_id(group_id)
        rank_id = validate_rank_id(rank_id)
        
        self.client._make_request('POST', f'/guilds/{guild_id}/setrank',
                                json_data={
                                    'user_id': user_id,
                                    'group_id': group_id, 
                                    'rank_id': rank_id
                                })
    
    def set_user_rank_bulk(self, guild_id: str, rank_changes: List[SetRank]) -> None:
        """
        Set ranks for multiple users (batch operation)
        
        Args:
            guild_id (str): Discord guild ID
            rank_changes (List[SetRank]): List of rank change data
            
        Raises:
            ValidationError: Invalid parameters or empty list
            AuthenticationError: Invalid or expired token or insufficient permissions
            NotFoundError: Guild not found
        """
        guild_id = validate_discord_id(guild_id)
        
        if not rank_changes:
            raise ValidationError("Rank changes list cannot be empty")
        
        # Validate all rank changes
        validated_changes = []
        for change in rank_changes:
            validated_change = {
                'user_id': validate_roblox_id(change.user_id),
                'group_id': validate_group_id(change.group_id),
                'rank_id': validate_rank_id(change.rank_id)
            }
            validated_changes.append(validated_change)
        
        self.client._make_request('POST', f'/guilds/{guild_id}/setrank/bulk',
                                json_data={'changes': validated_changes})