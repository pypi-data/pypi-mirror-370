"""
WebSocket endpoints for real-time messaging and notifications.

This module provides WebSocket routes for chat message exchange and
user connection tracking. Authentication is required for both endpoints
via a query parameter token.

Routes:

- `/messages`: WebSocket for real-time chat messaging.
- `/notifications`: WebSocket for real-time notifications.
- `/connected_users`: HTTP endpoint to retrieve the list of connected clients.

"""

import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from ..configuration import MANAGER
from ..descriptors import MessageType
from ..middleware.auth_websocket import WebSocketAuthMiddleware
from ..models import Message
from ..models.schemas import NotificationSchema, MessageSchema

ws_router = APIRouter()
websocket_auth = WebSocketAuthMiddleware()


@ws_router.websocket("/messages")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    """
    WebSocket endpoint for real-time chat messaging.

    Clients must authenticate using a token passed as a query parameter.
    Once connected, messages are broadcasted to all users and stored in the
    database.

    :param websocket: WebSocket connection instance.
    :param token: Authentication token passed as a query parameter.
    """
    client_id = websocket_auth.is_auth(token)
    if client_id == '':
        return websocket_auth.unauthorised(websocket)

    client_id = client_id['sub'][:9] + f"{uuid.uuid4().hex[:4]}"
    await MANAGER.connect(client_id, websocket)

    msg_ = MessageSchema(user_id=client_id)
    msg_.connection_msg()
    await MANAGER.broadcast(msg_.to_json())

    try:
        while True:
            data = await websocket.receive_text()
            message_data = MessageSchema.parse_raw(data)

            if message_data.mtype == MessageType.MESSAGE.value:
                message_data.user_id = (
                    message_data.user_id if message_data.user_id != "null"
                    else client_id
                )
                Message.create(
                    user_id=message_data.user_id,
                    content=message_data.content
                )
                await MANAGER.broadcast(message_data.to_json())
    except WebSocketDisconnect:
        MANAGER.disconnect(client_id)
        msg_ = MessageSchema(user_id=client_id)
        msg_.disconnection_msg()
        await MANAGER.broadcast(msg_.to_json())


@ws_router.get("/connected_users")
async def get_connected_users():
    """
    Retrieve the list of currently connected WebSocket client IDs.

    :return: Dictionary containing a list of connected user IDs.
    """
    users = MANAGER.get_connected_users()
    return {"connected_users": users}


@ws_router.websocket("/notifications")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    """
    WebSocket endpoint for receiving real-time notifications.

    Clients must authenticate using a token passed as a query parameter.
    The connection is registered with a combination of client ID and IP:port.
    Incoming messages are parsed as notifications.

    :param websocket: WebSocket connection instance.
    :param token: Authentication token passed as a query parameter.
    """
    client_id = websocket_auth.is_auth(token)
    if client_id == '':
        return websocket_auth.unauthorised(websocket)

    ipp_ = websocket.client.host + str(websocket.client.port)
    name_connection = client_id + ipp_
    await MANAGER.connect(name_connection, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message_data = NotificationSchema.parse_raw(data)
            print(message_data)
            # Uncomment below to publish to RabbitMQ exchange
            # await RABBITMQ_MANAGER.publish_message_to_exchange(
            #     EXCHANGE_NAME, message_data.json())
    except WebSocketDisconnect:
        MANAGER.disconnect(name_connection)
