import websockets
import webshocket
import pytest

HOST, PORT = "127.0.0.1", 5000


@pytest.mark.asyncio
async def test_simple_packet() -> None:
    payload = "This is Custom Packet"

    try:
        server = webshocket.WebSocketServer(HOST, PORT)
        await server.start()

        custom_packet = webshocket.Packet(
            data=payload,
            source=webshocket.PacketSource.CUSTOM,
            channel=None,
        )

        client = webshocket.WebSocketClient(f"ws://{HOST}:{PORT}")
        await client.connect()
        await client.send(custom_packet)

        connected_client = await server.accept()
        received_response = await connected_client.recv()

        assert received_response.data == payload
        assert received_response.source == webshocket.PacketSource.CUSTOM

    finally:
        await client.close()
        await server.close()


@pytest.mark.asyncio
async def test_packet_source() -> None:
    payload = "Sport News!"
    payload2 = "Global Announcement!"

    try:
        server = webshocket.WebSocketServer(HOST, PORT)
        await server.start()

        client = webshocket.WebSocketClient(f"ws://{HOST}:{PORT}")
        await client.connect()

        connected_client = await server.accept()
        connected_client.subscribe("sport")

        assert "sport" in connected_client.subscribed_channel

        await server.publish(
            "sport",
            payload,
        )
        received_packet = await client.recv()

        assert received_packet.data == payload
        assert received_packet.source == webshocket.PacketSource.CHANNEL

        await server.broadcast(payload2)
        received_packet = await client.recv()

        assert received_packet.data == payload2
        assert received_packet.source == webshocket.PacketSource.BROADCAST

    finally:
        await client.close()
        await server.close()


@pytest.mark.asyncio
async def test_send_other_datatype():
    try:
        server = webshocket.WebSocketServer(HOST, PORT)
        await server.start()

        client = webshocket.WebSocketClient(f"ws://{HOST}:{PORT}")
        await client.connect()

        connected_client = await server.accept()
        await connected_client.send({"hello": "world"})

        received_packet = await client.recv()
        assert received_packet.data == {"hello": "world"}

    finally:
        await client.close()
        await server.close()


@pytest.mark.asyncio
async def test_send_unserializeable_data():
    data_to_send = [
        {"hello", "world", "this", "is", "a", "set"},
        lambda: "Function type",
        webshocket.ClientConnection,  # Classes
    ]

    try:
        server = webshocket.WebSocketServer(HOST, PORT)
        await server.start()

        client = webshocket.WebSocketClient(f"ws://{HOST}:{PORT}")
        await client.connect()

        for item in data_to_send:
            with pytest.raises(TypeError):
                await client.send(item)

    finally:
        await client.close()
        await server.close()


@pytest.mark.asyncio
async def test_unknown_packet():
    try:
        server = webshocket.WebSocketServer(HOST, PORT)
        await server.start()

        client = await websockets.connect(f"ws://{HOST}:{PORT}")
        connected_client = await server.accept()
        await client.send("Raw String.")

        received_packet = await connected_client.recv()

        assert received_packet.data == "Raw String."
        assert received_packet.source == webshocket.PacketSource.UNKNOWN

    finally:
        await client.close()
        await server.close()
