"""Denylist management endpoint handlers"""

from typing import List, Optional
from ..models import Denylist, DenylistCreate, DenylistKind
from ..utils import validate_discord_id, validate_roblox_id, validate_group_id
from ..exceptions import ValidationError

class DenylistEndpoints:
    """Handles denylist management API endpoints"""
    
    def __init__(self, client):
        self.client = client
    
    def get_denylists(self, guild_id: str) -> List[Denylist]:
        """
        Get all denylists for a guild
        
        Args:
            guild_id (str): Discord guild ID
            
        Returns:
            List[Denylist]: List of denylist entries
            
        Raises:
            ValidationError: Invalid guild ID
            AuthenticationError: Invalid or expired token
            NotFoundError: Guild not found
        """
        guild_id = validate_discord_id(guild_id)
        
        data = self.client._make_request('GET', f'/guilds/{guild_id}/blacklists')
        return [Denylist(kind=DenylistKind(item['kind']), **item) for item in data]
    
    def create_denylist(self, guild_id: str, denylist: DenylistCreate) -> None:
        """
        Create a new denylist entry
        
        Args:
            guild_id (str): Discord guild ID
            denylist (DenylistCreate): Denylist data
            
        Raises:
            ValidationError: Invalid parameters or missing required fields
            AuthenticationError: Invalid or expired token
            NotFoundError: Guild not found
        """
        guild_id = validate_discord_id(guild_id)
        
        # Validate denylist data
        if not denylist.reason or not denylist.reason.strip():
            raise ValidationError("Denylist reason cannot be empty")
        
        data = {
            'reason': denylist.reason.strip(),
            'kind': denylist.kind.value
        }
        
        if denylist.kind == DenylistKind.USER:
            if not denylist.user_id:
                raise ValidationError("user_id is required for USER denylist entries")
            data['user_id'] = validate_roblox_id(denylist.user_id)
            
        elif denylist.kind == DenylistKind.GROUP:
            if denylist.group_id:
                data['group_id'] = validate_group_id(denylist.group_id)
            if denylist.code:
                data['code'] = denylist.code.strip()
            
            if not denylist.group_id and not denylist.code:
                raise ValidationError("Either group_id or code is required for GROUP denylist entries")
        
        self.client._make_request('POST', f'/guilds/{guild_id}/denylists', json_data=data)
    
    def delete_denylists(self, guild_id: str, denylist_ids: List[int]) -> None:
        """
        Delete denylist entries by IDs
        
        Args:
            guild_id (str): Discord guild ID
            denylist_ids (List[int]): List of denylist IDs to delete
            
        Raises:
            ValidationError: Invalid parameters or empty ID list
            AuthenticationError: Invalid or expired token
            NotFoundError: Guild or denylist entries not found
        """
        guild_id = validate_discord_id(guild_id)
        
        if not denylist_ids:
            raise ValidationError("Denylist IDs list cannot be empty")
        
        # Validate all IDs are positive integers
        validated_ids = []
        for denylist_id in denylist_ids:
            if not isinstance(denylist_id, int) or denylist_id <= 0:
                raise ValidationError(f"Invalid denylist ID: {denylist_id}")
            validated_ids.append(denylist_id)
        
        self.client._make_request('DELETE', f'/guilds/{guild_id}/denylists', 
                                json_data={'id': validated_ids})
