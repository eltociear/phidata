from typing import Optional, Union, Dict, List

from httpx import Response

from phi.api.api import api, invalid_response
from phi.api.routes import ApiRoutes
from phi.api.schemas.conversation import ConversationEventCreate, ConversationWorkspace, ConversationResponseSchema
from phi.cli.settings import phi_cli_settings
from phi.utils.log import logger


def log_conversation_event(
    conversation: ConversationEventCreate, workspace: ConversationWorkspace
) -> Optional[ConversationResponseSchema]:
    if not phi_cli_settings.api_enabled:
        return None

    logger.debug("--o-o-- Log conversation event")
    with api.Client() as api_client:
        try:
            r: Response = api_client.post(
                ApiRoutes.CONVERSATION_EVENT,
                json={
                    "event": conversation.model_dump(exclude_none=True),
                    "workspace": workspace.model_dump(exclude_none=True),
                },
            )
            if invalid_response(r):
                return None

            response_json: Union[Dict, List] = r.json()
            if response_json is None:
                return None

            conversation_response: ConversationResponseSchema = ConversationResponseSchema.model_validate(response_json)
            logger.debug(f"Conversation response: {conversation_response}")
            if conversation_response is not None:
                return conversation_response
        except Exception as e:
            logger.debug(f"Could not log conversation event: {e}")
    return None
