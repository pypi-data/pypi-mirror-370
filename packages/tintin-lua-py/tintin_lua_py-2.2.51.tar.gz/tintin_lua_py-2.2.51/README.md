# TinTin++ with Lua and Python Support

An enhanced version of the popular TinTin++ MUD client with built-in support for Lua and Python scripting languages, providing powerful automation and customization capabilities for MUD gaming.

## Features

- **TinTin++ 2.02.50**: Latest version of the robust MUD client
- **Lua Scripting**: Full Lua language support for advanced scripting
- **Python Integration**: Python scripting capabilities for complex automation
- **Statically Linked**: Self-contained binary with no external dependencies
- **High Performance**: Optimized for speed and reliability
- **Cross-platform**: Works on Linux x86_64 systems

## Installation

### From PyPI (Recommended)

```bash
pip install tintin-lua-py
```

### System Installation (Alternative)

```bash
# Install system-wide
pip install --user tintin-lua-py
```

## Usage

After installation, you can run TinTin++ with:

```bash
tt++                 # Primary command
tintin-lua-py        # Alternative command
```

### Basic Examples

```bash
# Start TinTin++
tt++

# Connect to a MUD directly
tt++ mudserver.com 4000

# Run with a script file
tt++ -r myscript.tin

# Set window title
tt++ -t "My MUD Client"
```

### Scripting Examples

#### Lua Scripting
```lua
#lua {
    function greet(name)
        send("say Hello, " .. name .. "!")
    end
    
    greet("World")
}
```

#### Python Integration
```python
#python {
    import random
    
    def random_emote():
        emotes = ["smile", "laugh", "nod", "wave"]
        return random.choice(emotes)
    
    send(random_emote())
}
```

## Features in Detail

### Enhanced Scripting
- **Lua 5.x**: Full featured Lua interpreter built-in
- **Python API**: Direct Python script execution
- **Cross-language**: Lua and Python can interact with TinTin++ commands
- **Libraries**: Access to standard Lua and Python libraries

### TinTin++ Core Features
- **Aliases**: Create command shortcuts
- **Triggers**: Automatic responses to text patterns  
- **Variables**: Store and manipulate data
- **Mapping**: Visual representation of game areas
- **Logging**: Record gaming sessions
- **Macros**: Key binding and automation
- **Multi-session**: Connect to multiple MUDs simultaneously

## Command Line Options

```bash
tt++ [options] [host] [port]

Options:
  -r <file>     Read script file on startup
  -t <title>    Set window title
  -e <command>  Execute command on startup
  -h            Show help information
```

## Configuration

TinTin++ stores configuration in various ways:
- **Script files**: `.tin` files with commands and scripts
- **Session files**: Saved connection settings
- **Variable files**: Persistent variable storage

### Example Configuration
```bash
# Create a startup script
echo "#ses main mudserver.com 4000" > startup.tin
echo "#alias hi say Hello everyone!" >> startup.tin

# Run with startup script
tt++ -r startup.tin
```

## Compatibility

- **Operating System**: Linux (x86_64)
- **Python**: Compatible with system Python installations
- **Lua**: Built-in Lua interpreter (no external Lua required)
- **Terminal**: Works with any terminal emulator

## Performance

- **Memory Efficient**: Low memory footprint
- **Fast Execution**: Optimized for real-time MUD gaming
- **Stable**: Thoroughly tested for reliability
- **Scalable**: Handles multiple simultaneous connections

## License

GPL v2 - See included license files for details

## Support and Documentation

### Official TinTin++ Resources
- [TinTin++ Official Website](https://tintin.mudhalla.net/)
- [TinTin++ Manual](https://tintin.mudhalla.net/manual/)
- [Scripting Reference](https://tintin.mudhalla.net/scripts/)

### Community
- MUD gaming communities
- TinTin++ forums and discussion groups
- GitHub issues for this package

## Version History

### 2.02.50
- Latest TinTin++ features
- Enhanced Lua integration
- Improved Python scripting support
- Performance optimizations
- Bug fixes and stability improvements

## Contributing

1. Fork the repository
2. Create your feature branch  
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Building from Source

This package includes a pre-built binary, but you can also build from TinTin++ source:

```bash
# Get TinTin++ source
wget http://tintin.mudhalla.net/download/tintin-2.02.50.tar.gz
tar -xzf tintin-2.02.50.tar.gz

# Configure with Lua and Python
cd tintin-2.02.50/src
./configure --enable-lua --enable-python
make
```
