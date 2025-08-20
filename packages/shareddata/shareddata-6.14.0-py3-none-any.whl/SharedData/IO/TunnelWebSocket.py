import asyncio
import websockets
import argparse

def get_args():
    """
    Parses command-line arguments for configuring a WebSocket tunnel.
    
    Returns:
        argparse.Namespace: An object containing the parsed arguments:
            - local_host (str): Local host address (default: '127.0.0.1')
            - local_port (int): Local port number (default: 2222)
            - remote_uri (str): Remote WebSocket URI (required)
    """
    parser = argparse.ArgumentParser(description="Websocket tunnel configuration")
    parser.add_argument('--local_host', type=str, default='127.0.0.1', help="Local host address")
    parser.add_argument('--local_port', type=int, default=2222, help="Local port number")
    parser.add_argument('--remote_uri', type=str, required=True, help="Remote WebSocket URI wss://")

    return parser.parse_args()

# Configuration
args = get_args()
LOCAL_HOST = args.local_host
LOCAL_PORT = args.local_port
REMOTE_URI = args.remote_uri

async def forward_data(websocket, reader, writer):
    """
    Asynchronously forwards data received from a websocket to a stream writer.
    
    Continuously reads messages from the given websocket and writes them to the provided stream writer. Ensures that the writer is properly drained after each write. Handles exceptions by printing an error message and guarantees that the writer is closed and awaited upon completion or error.
    
    Args:
        websocket: An asynchronous websocket connection to read messages from.
        reader: An asynchronous stream reader (not used in this function but included for interface consistency).
        writer: An asynchronous stream writer to forward messages to.
    """
    try:
        async for message in websocket:
            writer.write(message)
            await writer.drain()
    except Exception as e:
        print(f"Error in forward_data: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def forward_socket_to_websocket(reader, websocket):
    """
    Asynchronously reads data from a socket-like stream reader and forwards it to a WebSocket.
    
    Continuously reads up to 4096 bytes from the provided `reader`. If data is received, it is sent to the specified `websocket`. The loop terminates when no more data is available from the reader. Any exceptions encountered during reading or sending are caught and logged.
    
    Args:
        reader: An asynchronous stream reader with a `read` method.
        websocket: An asynchronous WebSocket connection with a `send` method.
    """
    try:
        while True:
            data = await reader.read(4096)
            if not data:
                break
            await websocket.send(data)
    except Exception as e:
        print(f"Error in forward_socket_to_websocket: {e}")

async def handle_client(reader, writer):
    """
    Handles a client connection by establishing a WebSocket connection to a remote server and forwarding data bidirectionally between the client socket and the WebSocket.
    
    Parameters:
        reader (asyncio.StreamReader): The stream reader for the client socket.
        writer (asyncio.StreamWriter): The stream writer for the client socket.
    
    This coroutine creates two asynchronous tasks to forward data from the client socket to the WebSocket and from the WebSocket back to the client socket concurrently. It ensures proper cleanup by closing the client socket writer upon completion or in case of an error.
    
    Exceptions are caught and logged to the console.
    """
    try:
        async with websockets.connect(REMOTE_URI) as websocket:
            # Create tasks for bidirectional data forwarding
            to_server = asyncio.create_task(forward_socket_to_websocket(reader, websocket))
            to_client = asyncio.create_task(forward_data(websocket, reader, writer))

            await asyncio.gather(to_server, to_client)
    except Exception as e:
        print(f"Error in handle_client: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    """
    Starts an asynchronous TCP server that listens on a specified local host and port.
    
    The server uses the `handle_client` coroutine to handle incoming client connections.
    Once started, it prints a message indicating the address it is listening on and runs indefinitely,
    serving clients asynchronously.
    
    Requires the `asyncio` module and predefined `LOCAL_HOST`, `LOCAL_PORT`, and `handle_client`.
    """
    server = await asyncio.start_server(handle_client, LOCAL_HOST, LOCAL_PORT)
    async with server:
        print(f"Listening on {LOCAL_HOST}:{LOCAL_PORT}...")
        await server.serve_forever()

# Run the main function when the script is executed
if __name__ == "__main__":
    asyncio.run(main())