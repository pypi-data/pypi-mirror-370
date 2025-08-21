<div align="center">

# gupsup

<em>A secure terminal-based chat application for real-time communication — right from your terminal.</em>

[![PyPI Downloads](https://static.pepy.tech/badge/gupsup)](https://pepy.tech/projects/gupsup)
[![PyPI version](https://img.shields.io/pypi/v/gupsup)](https://pypi.org/project/gupsup/)
[![Python version](https://img.shields.io/pypi/pyversions/gupsup)](https://pypi.org/project/gupsup/)

Learn more and explore detailed info at [gupsup-cli](https://gupsup-cli.vercel.app/)

Looking for the server? See [gupsup-server](https://github.com/iamRahul21/terminalchat-server)
</div>



## ⚡ Quick Start

```bash
pip install gupsup
gupsup
```

[![PyPI](https://img.shields.io/pypi/v/gupsup?label=Install%20from%20PyPI)](https://pypi.org/project/gupsup/)

That's it! Start chatting instantly.

## Features

- **Zero-friction setup** - Just run `gupsup` and start chatting
- **End-to-end encryption** - Messages are encrypted on your device and only readable by others with the same channel code
- **Secure channels** - Create private rooms with shareable codes  
- **Auto-reconnection** - Handles network issues gracefully
- **Cross-platform** - Works on Windows, macOS, Linux
- **No account required** - Anonymous secure communication

## Usage

```bash
# Install once
pip install gupsup

# Run anywhere
gupsup
```

### Example Session
```
gupsup - Secure Communication Channel
Channel code (or 'new' to create): new
Channel created: a4b2c1
Share code 'a4b2c1' with others to join
Username: qwerty

Establishing connection...
🟢 Connected to channel: a4b2c1
Commands: Type messages to send, 'quit' to exit

qwerty: Hello world!
mrrobot: Hey there!
qwerty: quit
Terminating session.
```

## How It Works

1. **Create or join** a secure channel with a 6-character code
2. **Share the code** with people you want to chat with
3. **Chat securely** - messages are only sent to your channel
4. **No persistence** - messages disappear when you disconnect

## Security & Privacy

- **End-to-end encryption** - Only clients with the same channel code and updated app can read your messages
- **Channel isolation** - Only people with your code can join
- **No message storage** - Everything is real-time only
- **No accounts** - Completely anonymous
- **Secure transport** - All communication encrypted in transit

## Development Install
```bash
# Client:
git clone https://github.com/iamRahul21/gupsup.git
cd gupsup
pip install -e .
gupsup

# Server (required to host your own backend):
git clone https://github.com/iamRahul21/gupsup-server.git
cd gupsup-server
pip install -r requirements.txt
python main.py
```

## Commands

- **Type normally** to send messages
- **`quit`** or **`exit`** to leave
- **Ctrl+C** to force quit
- **Enter without text** is ignored

## Troubleshooting

<details>
<summary><strong>Encrypted messages look garbled or cause errors in old clients?</strong></summary>

- Make sure all users are on the latest version of the app to support end-to-end encryption.

</details>

<details>
<summary><strong>Connection timeouts?</strong></summary>

- First connection may be slow (server waking up)
- Try again - should connect immediately
- Check internet connection

</details>

<details>
<summary><strong>Messages not appearing?</strong></summary>

- Ensure same channel code
- Check if others are actually connected
- Try creating a new channel

</details>

## 📦 Package Details

- **Package**: `gupsup` on PyPI
- **Command**: `gupsup` 
- **Python**: 3.8+ required
- **Dependencies**: Only `websockets>=11.0`
- **Size**: Ultra-lightweight

## Architecture

```
Terminal Client  ←→  WebSocket  ←→  FastAPI Server  ←→  Channel Manager
   (gupsup)         (see: https://github.com/iamRahul21/gupsup-server)
```

## Contributing

1. Fork on GitHub
2. Create feature branch
3. Test thoroughly  
4. Submit pull request

## 📄 License

MIT License - use freely, contribute back.

## Author

**[Rahul Deka](https://rahul-deka.vercel.app/)**

---

**Simple. Secure. Terminal-native.**