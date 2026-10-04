# FOLC-V3 Enhanced Orbic Shell

An interactive tmux-powered terminal interface for accessing the Orbic Speed native host.

## 🚀 Features

### Enhanced Terminal Experience
- **Beautiful UI** - Color-coded messages, ASCII banner, status indicators
- **tmux Integration** - Professional terminal multiplexer with custom config
- **Mouse Support** - Click to navigate, scroll through history
- **50k Line Buffer** - Extensive scrollback history
- **Vi Keybindings** - Efficient keyboard navigation

### Smart Operations
- **Dependency Checking** - Validates all requirements before launch
- **Connection Testing** - Ensures native host is responsive
- **Automatic Port Forwarding** - Sets up ADB forwarding automatically
- **Graceful Fallback** - Falls back to basic shell if tmux unavailable
- **Session Persistence** - Detach and reattach without losing work

## 📋 Usage

### Basic Launch
```bash
./orbic_shell.sh
```

This will:
1. Check dependencies (tmux, adb, netcat)
2. Set up ADB port forwarding
3. Test native host connection
4. Launch interactive tmux session

### Session Management
```bash
# List all active sessions
./orbic_shell_manager.sh list

# Attach to a detached session
./orbic_shell_manager.sh attach folc_orbic_1234567890

# Kill a specific session
./orbic_shell_manager.sh kill folc_orbic_1234567890

# Kill all sessions
./orbic_shell_manager.sh kill-all
```

## ⌨️ Keyboard Shortcuts

### tmux Commands (Prefix: Ctrl+B)
- `Ctrl+B then D` - Detach from session (keeps running in background)
- `Ctrl+B then [` - Enter scroll/copy mode (use arrows/PgUp/PgDn, press `q` to exit)
- `Ctrl+B then ?` - Show all tmux keybindings
- `Ctrl+B then :` - Enter tmux command mode

### In Scroll Mode
- `Arrow Keys` - Navigate line by line
- `PgUp/PgDn` - Navigate page by page
- `/` - Search forward
- `?` - Search backward
- `q` - Exit scroll mode

### Shell Commands
- `exit` - Close the native host connection
- Standard bash commands work as expected

## 🎨 Status Indicators

- 🔴 **RED** - Errors and failures
- 🟢 **GREEN** - Success and confirmations
- 🟡 **YELLOW** - Warnings and tips
- 🔵 **BLUE** - Informational messages
- 🟣 **PURPLE** - Action indicators
- 🔷 **CYAN** - Decorative elements and banners

## 🔧 Configuration

### Device Settings
Edit `orbic_shell.sh` to change:
```bash
DEVICE="e830926d"    # ADB device ID
PORT=9999            # Native host port
```

### tmux Customization
The script auto-generates a custom tmux config with:
- Custom status bar (shows time, date, session name)
- Colored pane borders
- Mouse support enabled
- Vi keybindings
- 50k line history buffer

You can modify these in the `create_tmux_config()` function.

## 🐛 Troubleshooting

### "Device not found"
- Run `adb devices` to see available devices
- Update the `DEVICE` variable in `orbic_shell.sh`

### "Cannot connect to native host"
- Ensure the native host daemon is running on the device
- Check that port forwarding is working: `adb -s e830926d forward --list`

### "Missing dependencies"
Install required packages:
```bash
apt-get install tmux adb netcat-openbsd
```

### Session Won't Detach
- Make sure you press `Ctrl+B` THEN `D` (not simultaneously)
- Wait a moment between the two keypresses

## 📊 Comparison: Old vs New

| Feature | Old Script | New Script |
|---------|-----------|------------|
| Interface | Raw netcat | tmux with custom UI |
| Colors | None | Full color support |
| Scrollback | Terminal default (~1k lines) | 50k lines |
| Mouse | No | Yes |
| Session persistence | No | Yes (detach/reattach) |
| Error handling | Minimal | Comprehensive |
| Help text | None | Built-in reference |
| Connection test | No | Yes |
| Dependency check | No | Yes |

## 💡 Tips

1. **Detach Instead of Exit** - Use `Ctrl+B D` to keep your session running while you work on other tasks
2. **Use Scroll Mode** - Press `Ctrl+B [` to browse command history and copy text
3. **Multiple Sessions** - You can run multiple instances and switch between them
4. **Mouse Scrolling** - Just scroll with your mouse to view history (easier than keyboard scrolling)
5. **Save Important Sessions** - Note the session name when you launch, so you can reattach later

## 🔐 Security Note

This shell provides root access to the native host. Use responsibly and ensure proper authentication/authorization in production environments.
