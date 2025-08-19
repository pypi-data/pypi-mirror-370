from typing import Dict, List

from fastapi import WebSocket
from starlette.websockets import WebSocketState


class ConnectionManager:
    """
    Manages active WebSocket connections for a FastAPI application.

    This class provides methods to handle client connections and
    disconnections, send messages to individual clients, broadcast messages
    to all connected clients, and retrieve a list of currently connected users.
    """

    def __init__(self):
        """
        Initialize the connection manager with an empty dictionary of active
        connections.
        The dictionary maps client IDs to their respective WebSocket instances.
        """
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        """
        Accept a new WebSocket connection and register it.

        :param client_id: Unique identifier for the connecting client.
        :param websocket: The WebSocket connection object.
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        """
        Remove a WebSocket connection from the active connections.

        :param client_id: The ID of the client to disconnect.
        """
        self.active_connections.pop(client_id, None)

    async def send_personal_message(self, message: str, client_id: str):
        """
        Send a message to a specific connected client.

        :param message: The text message to send.
        :param client_id: The ID of the target client.
        """
        websocket = self.active_connections.get(client_id)
        if websocket:
            await websocket.send_text(message)

    async def broadcast(self, message: str):
        """
        Send a message to all currently connected clients.

        Only clients with an active WebSocket connection (`CONNECTED` state)
        will receive the message.
        Any exceptions during sending will be logged to stdout.

        :param message: The text message to broadcast.
        """
        for connection in self.active_connections.values():
            if connection.client_state == WebSocketState.CONNECTED:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    print(f"Error sending to client: {e}")
            else:
                print(f"Skipping client in state: {connection.client_state}")

    def get_connected_users(self) -> List[str]:
        """
        Get a list of all currently connected client IDs.

        :return: A list of client IDs.
        """
        return list(self.active_connections.keys())
