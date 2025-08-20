from spryx_core import NOT_GIVEN, is_given
from spryx_http import SpryxAsyncClient


class Messages:
    def __init__(self, client: SpryxAsyncClient):
        self._client = client

    async def list_messages(
        self,
        organization_id: str,
        page: int = 1,
        limit: int = 10,
        order: str = "asc",
        contact_id: str = NOT_GIVEN,
        channel_id: str = NOT_GIVEN,
        sort_field: str = NOT_GIVEN,
    ) -> dict:
        """List all messages."""
        params = {"page": page, "limit": limit, "order": order}
        
        if is_given(contact_id):
            params["contact_id"] = contact_id
            
        if is_given(channel_id):
            params["channel_id"] = channel_id
            
        if is_given(sort_field):
            params["sort_field"] = sort_field

        return await self._client.get(
            "/v1/messages",
            params=params,
            headers={"x-organization-id": organization_id},
        )

    async def add_message_outgoing(
        self,
        organization_id: str,
        channel_id: str,
        contact_id: str,
        message: dict,
        reply_to: str = NOT_GIVEN,
    ) -> dict:
        """Add an outgoing message."""
        payload = {
            "channel_id": channel_id,
            "contact_id": contact_id,
            "message": message,
        }

        if is_given(reply_to):
            payload["reply_to"] = reply_to

        return await self._client.post(
            "/v1/messages/outgoing",
            json=payload,
            headers={"x-organization-id": organization_id},
        )

    async def mark_as_read(
        self,
        organization_id: str,
        message_id: str,
    ) -> dict:
        """Mark a message as read."""
        return await self._client.post(
            f"/v1/messages/{message_id}/read",
            headers={"x-organization-id": organization_id},
        ) 