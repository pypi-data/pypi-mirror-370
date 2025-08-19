# iOS Bridge CLI

**Stream and control iOS simulators like a desktop app** - The macOS equivalent of `scrcpy` for iOS development.

iOS Bridge CLI lets you stream iOS simulator sessions to any device with a beautiful desktop interface. Perfect for cross-platform development teams, remote work, and testing iOS apps from Windows/Linux machines.

## What iOS Bridge CLI Does

🖥️ **Desktop Streaming** - View iOS simulators in a native desktop window  
🎮 **Touch & Keyboard Control** - Click, tap, type, and gesture naturally  
🌐 **Cross-Platform Client** - Stream from Mac to Windows, Linux, or other Macs  
📱 **Real Device Experience** - Full touch controls, home button, screenshots  
🚀 **Zero Configuration** - Works out of the box with automatic server management  
⚡ **High Performance** - WebRTC streaming with ultra-low latency

## Installation

```bash
pip install ios-bridge-cli
```

**Requirements**: macOS (for server), Python 3.8+, Xcode (for iOS simulators)

## Quick Start

### 1. Create and Stream an iOS Session

```bash
# Create an iPhone simulator
ios-bridge create "iPhone 15 Pro" "18.2" --wait

# Stream it to desktop
ios-bridge stream
```

That's it! A desktop window opens with your iOS simulator ready for interaction.

### 2. Cross-Platform Setup (Mac Server → Windows/Linux Client)

**On Mac (Server):**
```bash
# Start the server for remote access
ios-bridge start-server --host 0.0.0.0

# Create and get session ID
ios-bridge create "iPhone 15 Pro" "18.2" --wait
ios-bridge list  # Copy the session ID
```

**On Windows/Linux (Client with Full Features):**
```bash
# Connect to your Mac server
ios-bridge connect http://YOUR-MAC-IP:8000 --save

# Full session management capabilities
ios-bridge create "iPhone 15 Pro" "18.2" --wait  # Create sessions
ios-bridge list                                   # List all sessions
ios-bridge stream                                 # Stream (auto-detects session)
ios-bridge terminate <session-id>                # Terminate sessions
ios-bridge info <session-id>                     # Get session details
```

> **✨ Important**: Windows and Linux clients have **complete feature parity** with macOS when connected to a Mac server. You can create, manage, stream, and control iOS sessions exactly like on Mac - the only requirement is the initial server connection.

### 3. Web Interface (Browser Streaming)

```bash
# Stream in browser instead of desktop app
ios-bridge stream <session-id> --web-only

# Then open: http://localhost:8000/web/<session-id>
```

## Core Commands

### Session Management
```bash
# List available device types
ios-bridge devices

# Create new simulator session
ios-bridge create "iPhone 14 Pro" "16.0" --wait

# List active sessions
ios-bridge list

# Get session details
ios-bridge info <session-id>

# Terminate session
ios-bridge terminate <session-id>
```

### Streaming & Control
```bash
# Stream session (auto-detects if only one session)
ios-bridge stream

# Stream specific session
ios-bridge stream <session-id>

# Stream with quality settings
ios-bridge stream <session-id> --quality ultra --fullscreen

# Take screenshot
ios-bridge screenshot --output screenshot.png
```

### Server Management
```bash
# Start server (macOS only)
ios-bridge start-server

# Start server in background
ios-bridge start-server --background --port 9000

# Check server status
ios-bridge server-status

# Stop server
ios-bridge kill-server
```

### Remote Connection
```bash
# Connect to remote server and save
ios-bridge connect https://ios-bridge.company.com --save

# Test connection
ios-bridge server-status

# Use all commands with remote server
ios-bridge devices
ios-bridge create "iPhone 14" "18.2"
```

## Desktop Controls

- **Mouse**: Click and drag for touch input
- **Keyboard**: Type directly into the simulator
- **F1**: Home button
- **F2**: Screenshot  
- **F3**: Device info
- **F4**: Toggle keyboard
- **F11**: Toggle fullscreen
- **Ctrl+C**: Close and exit

## Platform Support

| Platform | Local Server | Remote Client | Desktop Streaming |
|----------|:------------:|:-------------:|:-----------------:|
| **macOS** | ✅ Full | ✅ Full | ✅ Native App |
| **Windows** | ❌ | ✅ Full | ✅ Native App |
| **Linux** | ❌ | ✅ Full | ✅ Native App |

*Local server requires macOS + Xcode for iOS simulator access*

## Advanced Usage

### Quality Settings
```bash
# Ultra quality (best for local network)
ios-bridge stream --quality ultra

# Low quality (best for slow connections)  
ios-bridge stream --quality low
```

### Server Options
```bash
# Custom server host/port
ios-bridge start-server --host 192.168.1.100 --port 9000

# Background server with custom settings
ios-bridge start-server --background --host 0.0.0.0 --port 8080
```

### Web Interface Features
- 🌐 No desktop app installation required
- 📱 Mobile-friendly interface
- 🔗 Shareable URLs for team collaboration
- 🚀 WebRTC streaming option

## How It Works

```
┌─────────────────┐    HTTP/WebSocket    ┌─────────────────┐    
│   iOS Bridge    │ ←──────────────────→ │  Desktop Client │    
│     Server      │                      │   (Windows/     │    
│                 │                      │   Linux/Mac)    │    
│ • iOS Simulator │                      │                 │    
│ • Session Mgmt  │                      │ • Video Stream  │    
│ • WebRTC/WS API │                      │ • Touch Input   │    
│   (macOS Only)  │                      │ • Native UI     │    
└─────────────────┘                      └─────────────────┘    
```

The server runs on macOS (where iOS simulators are available) and streams to desktop clients on any platform.

## Common Workflows

### iOS Development Team
1. **QA Team**: Run server on Mac mini, stream to Windows/Linux machines
2. **Remote Work**: Develop on Mac, test from anywhere with web interface  
3. **Team Reviews**: Share session URLs for collaborative testing

### Individual Developer
1. **Multi-Monitor Setup**: Stream simulator to second monitor
2. **Screen Recording**: Use desktop apps like OBS to record iOS interactions
3. **Cross-Platform Testing**: Test iOS app while working on Windows/Linux

## Troubleshooting

**"No sessions available"**
```bash
# Check if sessions exist
ios-bridge list

# Create a new session
ios-bridge create "iPhone 15 Pro" "18.2" --wait
```

**Connection errors**
```bash
# Check server status
ios-bridge server-status

# Restart server if needed
ios-bridge kill-server
ios-bridge start-server
```

**Desktop app won't start**
- Ensure server is running first: `ios-bridge start-server`
- Try web interface: `ios-bridge stream --web-only`
- Check for port conflicts: `ios-bridge start-server --port 9000`

## Development

For development documentation, see:
- [Desktop App Development Guide](ios_bridge_cli/electron_app/DEVELOPMENT.md)
- [CLI Development Setup](ios_bridge_cli/electron_app/DEV-COMMANDS.md)

### Quick Development Setup
```bash
# CLI development
git clone <repo-url>
cd ios-bridge-cli
pip install -e .

# Desktop app development  
cd ios_bridge_cli/electron_app
npm install
npm run dev
```

## License

MIT License - see LICENSE file for details

---

**Getting Started**: `pip install ios-bridge-cli && ios-bridge start-server && ios-bridge create "iPhone 15 Pro" "18.2" --wait && ios-bridge stream`