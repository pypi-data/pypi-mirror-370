import asyncio
import websockets
import json
import sys
import os
import base64
from typing import Optional
import logging
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

try:
    from .config import Config
except ImportError:
    from config import Config

logging.basicConfig(level=getattr(logging, Config.get_log_level()))
logger = logging.getLogger(__name__)

class TerminalChatClient:
    def derive_key(self, passphrase: str) -> bytes:
        # Use a static salt for simplicity; for real security, use a random salt and share it
        salt = b'gupsup-static-salt'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
            backend=default_backend()
        )
        return kdf.derive(passphrase.encode())

    def encrypt_message(self, plaintext: str) -> str:
        key = self.derive_key(self.channel_code)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, plaintext.encode(), None)
        return base64.b64encode(nonce + ct).decode()

    def decrypt_message(self, ciphertext_b64: str) -> Optional[str]:
        try:
            key = self.derive_key(self.channel_code)
            aesgcm = AESGCM(key)
            data = base64.b64decode(ciphertext_b64)
            nonce, ct = data[:12], data[12:]
            pt = aesgcm.decrypt(nonce, ct, None)
            return pt.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None
    def __init__(self):
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.username: str = ""
        self.channel_code: str = ""
        self.server_uri: str = ""
        self.is_connected: bool = False
        self.reconnect_attempts: int = 0
        self.max_reconnect_attempts: int = Config.get_max_reconnect_attempts()
        self.websocket_config = Config.get_websocket_config()
    
    def get_server_config(self) -> str:
        """Get server configuration from environment or user input"""
        default_server = Config.get_server_address()
        
        print("gupsup - Secure Communication Channel")
        return default_server
    
    def get_channel_code(self) -> str:
        """Get or generate channel code"""
        choice = input("Channel code (or 'new' to create): ").strip()
        if choice.lower() == "new":
            import random, string
            code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            print(f"Channel created: {code}")
            print(f"Share code '{code}' with others to join")
            return code
        else:
            return choice
    
    def get_username(self) -> str:
        """Get username from user"""
        while True:
            username = input("Username: ").strip()
            if username:
                return username
            print("Username required. Try again.")
    
    def build_websocket_uri(self, server: str, code: str) -> str:
        """Build WebSocket URI based on server address"""
        if server.startswith("localhost") or server.startswith("127.0.0.1"):
            return f"ws://{server}/ws/{code}"
        else:
            return f"wss://{server}/ws/{code}"
    
    async def connect(self) -> bool:
        """Establish WebSocket connection with retry logic"""
        try:
            print("Establishing connection...")
            print("Note: Initial connection may take longer if server is sleeping")
            
            self.websocket = await websockets.connect(
                self.server_uri,
                **self.websocket_config
            )
            self.is_connected = True
            self.reconnect_attempts = 0
            print(f"🟢 Connected to channel: {self.channel_code}")
            print("Commands: Type messages to send, 'quit' to exit\n")
            return True
        except asyncio.TimeoutError:
            print(f"🔴 Connection timeout - server may be starting up")
            print("Retry recommended - server should be ready now")
            return False
        except Exception as e:
            print(f"🔴 Connection failed: {e}")
            return False
    
    async def reconnect(self) -> bool:
        """Attempt to reconnect to the server"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print(f"🔴 Max reconnection attempts reached ({self.max_reconnect_attempts}). Aborting.")
            return False
        
        self.reconnect_attempts += 1
        print(f"Reconnecting... (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
        
        delay = min(2 ** self.reconnect_attempts, 30) 
        await asyncio.sleep(delay)
        return await self.connect()
    
    async def receive_messages(self):
        """Handle incoming messages (decrypt)"""
        while self.is_connected:
            try:
                if self.websocket:
                    message = await self.websocket.recv()
                    plaintext = self.decrypt_message(message)
                    if plaintext is None:
                        continue
                    if plaintext.startswith(f"{self.username}: "):
                        continue
                    print(f"\r{plaintext}")
                    print(f"{self.username}: ", end="", flush=True)
            except websockets.exceptions.ConnectionClosedError:
                if self.is_connected:
                    print("\nConnection lost. Reconnecting...")
                    self.is_connected = False
                    if await self.reconnect():
                        continue
                    else:
                        break
            except websockets.exceptions.ConnectionClosedOK:
                self.is_connected = False
                break
            except Exception as e:
                if self.is_connected: 
                    logger.error(f"Error receiving message: {e}")
                break
    
    async def send_messages(self):
        """Handle outgoing messages (encrypt)"""
        while self.is_connected:
            try:
                prompt = f"{self.username}: "
                message = await asyncio.get_event_loop().run_in_executor(None, input, prompt)
                if message.lower() in ['quit', 'exit', '/quit', '/exit']:
                    print("Terminating session.")
                    self.is_connected = False
                    break
                if message.strip():
                    if self.websocket:
                        formatted_message = f"{self.username}: {message}"
                        encrypted = self.encrypt_message(formatted_message)
                        await self.websocket.send(encrypted)
            except KeyboardInterrupt:
                print("\nSession interrupted.")
                self.is_connected = False
                break
            except Exception as e:
                print(f"🔴 Error sending message: {e}")
                break
    
    async def chat(self):
        """Main chat loop"""
        try:
            await asyncio.gather(
                self.receive_messages(),
                self.send_messages()
            )
        except KeyboardInterrupt:
            print("\nSession terminated.")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources"""
        self.is_connected = False
        if self.websocket:
            try:
                await self.websocket.close()
            except:
                pass

def run_client():
    """Main entry point for the terminal chat client"""
    client = TerminalChatClient()
    
    try:
        server = client.get_server_config()
        client.channel_code = client.get_channel_code()
        client.username = client.get_username()
        client.server_uri = client.build_websocket_uri(server, client.channel_code)
        
        async def connect_with_retry():
            max_initial_attempts = 2
            for attempt in range(max_initial_attempts):
                if await client.connect():
                    return True
                elif attempt < max_initial_attempts - 1:
                    print(f"Retrying connection... (attempt {attempt + 2}/{max_initial_attempts})")
                    await asyncio.sleep(3)
            return False
        
        async def main():
            if not await connect_with_retry():
                print("🔴 Connection failed after multiple attempts.")
                print("Check network connection and retry.")
                return
            await client.chat()
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\nExiting.")
    except Exception as e:
        print(f"🔴 System error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_client()