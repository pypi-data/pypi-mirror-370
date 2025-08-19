# LumeTT - Multi-platform TinTin++ MUD Client

LumeTT is a sophisticated wrapper around TinTin++ that provides an enhanced MUD (Multi-User Dungeon) gaming experience with a scalable GUI and pre-configured settings.

## Features

- **Enhanced TinTin++ Integration**: Seamless wrapper around the powerful TinTin++ MUD client
- **Pre-configured Setup**: Ready-to-use configuration files and scripts
- **User-friendly**: Automatic setup and configuration management
- **Scalable GUI**: Optimized interface for different screen sizes
- **Cross-platform**: Works on any Linux distribution

## Installation

### From PyPI (Recommended)

```bash
pip install lumett
```

### Prerequisites

You'll need TinTin++ installed on your system:

```bash
# Ubuntu/Debian
sudo apt install tintin++

# Or install the enhanced version with Lua/Python support
pip install tintin-lua-py
```

## Usage

After installation, simply run:

```bash
lumett
```

On first run, LumeTT will:
1. Create a configuration directory in `~/.lumett`
2. Copy all necessary configuration files
3. Launch TinTin++ with the LumeTT configuration

## Configuration

LumeTT stores its configuration in `~/.lumett/`. You can customize:

- **Connection settings**: Modify MUD server connections
- **Scripting**: Add your own TinTin++ scripts
- **UI settings**: Customize colors, layouts, and more
- **Library files**: Extend functionality with additional modules

## Command Line Options

LumeTT accepts all standard TinTin++ command line options:

```bash
lumett [tintin++ options]
lumett -h                    # Show TinTin++ help
lumett mudserver.com 4000    # Connect directly to a MUD
```

## Directory Structure

```
~/.lumett/
├── lib/
│   ├── init.tin         # Main initialization script
│   ├── colors.tin       # Color definitions
│   └── filesystem.tin   # File system utilities
├── LICENSE              # License information
└── README.txt          # Additional documentation
```

## Requirements

- Python 3.6 or higher
- TinTin++ (automatically detected)
- Linux operating system

## License

GPL v2 - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For issues and support:
- Create an issue on GitHub
- Check the TinTin++ documentation for advanced usage

## Changelog

### 2.0.5
- Initial PyPI release
- Automatic configuration setup
- Enhanced TinTin++ integration
- Cross-platform compatibility improvements
