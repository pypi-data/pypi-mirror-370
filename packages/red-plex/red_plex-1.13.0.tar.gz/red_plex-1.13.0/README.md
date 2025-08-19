# red-plex

[![PyPI version](https://badge.fury.io/py/red-plex.svg)](https://badge.fury.io/py/red-plex)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A command-line tool and web interface for creating and updating Plex collections based on collages and bookmarks from Gazelle-based music trackers like **Redacted** ("RED") and **Orpheus Network** ("OPS"). 

red-plex bridges the gap between your curated music collections on private trackers and your personal Plex media server, automatically creating and maintaining Plex collections that mirror your tracker collages and bookmarks.

## Quick Start

1. **Install red-plex**: `pip install red-plex`
2. **Configure your API keys**: `red-plex config edit`
3. **Create your first collection**: 
   - **CLI**: `red-plex collages convert 12345 --site red`
   - **Web GUI**: `red-plex gui` (then visit http://127.0.0.1:8000)

## Web Interface

red-plex now includes a comprehensive web-based GUI for users who prefer a visual interface over command-line operations.

### Features

- **🌐 Dashboard**: Clean overview with feature cards and navigation
- **⚙️ Configuration Management**: View and edit all settings (API keys, Plex config, rate limits) through web forms
- **🎨 Collage Operations**: Convert new collages and view existing collections
- **🔖 Bookmark Operations**: Convert bookmarks from RED and OPS trackers
- **🏷️ Site Tags Operations**: Scan albums using album/artist names and create tag-based collections
- **🗄️ Database Management**: View statistics, update albums, reset tables
- **⚡ Real-time Updates**: Live status updates during long operations via WebSocket
- **📱 Mobile-Responsive**: Bootstrap-based design that works on all devices

### Usage

```bash
# Launch GUI server (default: http://127.0.0.1:8000)
red-plex gui

# Custom host/port
red-plex gui --host 0.0.0.0 --port 8080

# Debug mode with auto-reload
red-plex gui --debug
```

The web interface provides the same functionality as the CLI commands but with a user-friendly visual interface, real-time progress updates, and intuitive navigation.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Getting API Keys](#getting-api-keys)
- [Configuration](#configuration)
- [Web Interface](#web-interface)
- [Overview](#overview)
- [Features](#features)
- [Usage & Commands](#usage--commands)
  - [Configuration Commands](#configuration-commands)
  - [Collages](#collages)
  - [Upstream Sync](#upstream-sync)
  - [Bookmarks](#bookmarks)
  - [Site Tags](#site-tags)
  - [Remote Mappings](#remote-mappings)
  - [Fetch Mode (-fm)](#fetch-mode--fm)
  - [Database Commands](#database-commands)
- [Examples](#examples)
  - [Creating Collections](#creating-collections)
  - [Updating Collections](#updating-collections)
  - [Using Query Fetch Mode](#using-query-fetch-mode)
- [Configuration Details](#configuration-details)
- [Configuration Tips](#configuration-tips)
- [Troubleshooting](#troubleshooting)
- [Important Considerations](#important-considerations)
- [Contributing](#contributing)

---

## Prerequisites

- **Python 3.8 or higher**
- **Plex Media Server** with a configured music library
- **Active account** on RED and/or OPS with API access
- **Music library** organized in your Plex server

## Installation

### Using pip (recommended)

```bash
pip install red-plex
```

### Using pipx (isolated environment)

```bash
pipx install red-plex
```

### From source

```bash
git clone https://github.com/marceljungle/red-plex.git
cd red-plex
pip install -e .
```

## Getting API Keys

### For Redacted (RED)
1. Log into your RED account
2. Go to your profile settings
3. Navigate to "Access Settings" or "API"
4. Generate a new API key
5. **Keep this key secure and private**

### For Orpheus Network (OPS)
1. Log into your OPS account
2. Go to your user settings
3. Find the API section
4. Generate a new API key
5. **Keep this key secure and private**

## Configuration

After installation, you need to configure red-plex with your credentials:

```bash
# Open configuration file in your default editor
red-plex config edit
```

Edit the configuration file with your details:

```yaml
LOG_LEVEL: INFO
PLEX_URL: http://localhost:32400
PLEX_TOKEN: your_plex_token_here
SECTION_NAME: Music
RED:
  API_KEY: your_red_api_key_here
  BASE_URL: https://redacted.sh
  RATE_LIMIT:
    calls: 10
    seconds: 10
OPS:
  API_KEY: your_ops_api_key_here
  BASE_URL: https://orpheus.network
  RATE_LIMIT:
    calls: 4
    seconds: 15
```

### Getting Your Plex HTTPs URL

Visit: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token
Also visit: https://plex.tv/api/resources?includeHttps=1&X-Plex-Token={YOUR_TOKEN}

## Overview

- **Stores Data in SQLite**: Instead of CSV-based "caches," red-plex now stores albums, collages, and bookmarks in a lightweight SQLite database.
- **Collages & Bookmarks**: Fetch and manage torrent-based "collages" or personal "bookmarks" from Gazelle-based sites.
- **Plex Integration**: Compare the torrent group info with your Plex music library to create or update Plex collections.
- **Flexible Album Matching**: Match albums in Plex using either the original `torrent_name` (directory name) or a query-based approach (`Artist/Album`), ideal for organized libraries (e.g., Beets/Lidarr).
- **Incremental Updating**: Update previously created collections as new albums become available or site data changes.

## Features

- **Multi-Site**: Works with Redacted ("red") and Orpheus Network ("ops").
- **Web Interface**: Modern Flask-based GUI with Bootstrap styling and real-time updates.
- **Collections from Collages/Bookmarks**: Create or update entire Plex collections for each collage or bookmarked set.
- **Site Tags Mapping**: Map your Plex albums to site groups using album and artist names, then create collections based on specific tags.
- **Upstream Sync**: Push local Plex collection changes back to upstream collages on RED, enabling bidirectional synchronization between Plex collections and site collages.
- **Remote Mappings**: Core functionality that links Plex collections with site group IDs, enabling features like site tags and upstream sync.
- **Local SQLite Database**: All data (albums, collages, bookmarks, site mappings) is kept in one DB, no more CSV.
- **Two Fetch Modes**: Choose between `torrent_name` (default) for direct path matching or `query` for metadata-based searches in Plex.
- **Configurable Logging**: Choose between INFO, DEBUG, etc., in `config.yml`.
- **Rate Limiting**: Respects site rate limits and retries on errors.
- **Dual Interface**: Access all functionality via both command-line interface and web GUI.
- **Python 3.8+ Compatible**: Runs on modern Python versions with no external database dependencies.

## Usage & Commands

Type `red-plex --help` for detailed usage. Below is a summary of the main commands.

### Web Interface Commands

```bash
# Launch web GUI server
red-plex gui [--host HOST] [--port PORT] [--debug]

# Examples:
red-plex gui                           # Default: http://127.0.0.1:8000
red-plex gui --host 0.0.0.0            # Bind to all interfaces
red-plex gui --port 8080               # Custom port
red-plex gui --debug                   # Debug mode with auto-reload
```

### Configuration Commands

```bash
# Show current configuration (YAML)
red-plex config show

# Edit configuration in your default editor
red-plex config edit

# Reset configuration to default values
red-plex config reset
```

### Collages

```bash
# Create Plex collections for specific collage IDs
red-plex collages convert [COLLAGE_IDS] --site [red|ops] --fetch-mode [torrent_name|query]

# Update all collages in the database, re-checking the site data
red-plex collages update --fetch-mode [torrent_name|query]
```

### Upstream Sync

**⚠️ Important Prerequisites:**
- Only works with **RED** (Redacted) - OPS doesn't have the required API operations
- You must **own** the collages on the tracker site
- First **convert the collage** from the site using `red-plex collages convert` (even if the collage is empty)
- Run **remote mappings scan** to link Plex items with site group IDs: `red-plex db remote-mappings scan -s red`

**How it works:**
- Pushes local Plex collection changes back to upstream collages on RED
- Uses fuzzy string matching to find albums on the site (may cause occasional mismatches)
- Shows confirmation dialog with exactly what will be added before making changes
- **Never deletes** anything from upstream collages, only adds missing items
- If you update your Plex library, run a new remote-mappings scan to link new albums

```bash
# Sync all collections to upstream collages
red-plex collages update --push

# Sync specific collections to upstream collages  
red-plex collages update 12345 67890 --push

# Alternative flag name
red-plex collages update --update-upstream
```

**Scanning Process:**
- Can be cancelled anytime with **Ctrl+C** and resumed later
- Each mapping is saved to the database during scanning (no data loss)
- Scans latest added entries in Plex, so interrupted scans can continue from where they left off
- ⚠️ **Current limitation**: If you have many unmatched albums (e.g., 200 albums with no matches), they'll appear in the scan queue each time. This is being improved to ignore previously failed matches.

**Available in both CLI and Web Interface**

### Bookmarks

```bash
# Create Plex collections from your bookmarked releases
red-plex bookmarks convert --site [red|ops] --fetch-mode [torrent_name|query]

# Update all bookmarks in the database
red-plex bookmarks update --fetch-mode [torrent_name|query]
```

### Site Tags

```bash
# Create collections from albums matching specific tags
red-plex extras site-tags convert --tags [tag1,tag2,...] --collection-name [name]
```

### Remote Mappings

Remote mappings are the core functionality that links your Plex music library with site group IDs, enabling features like site tags and upstream sync.

```bash
# Scan albums and create remote mappings using album and artist names
red-plex db remote-mappings scan --site [red|ops] [--always-skip]

# Reset remote mappings (clears the relationship data)
red-plex db remote-mappings reset
```

**Scanning Features:**
- **Interruptible**: Can be cancelled with **Ctrl+C** at any time and resumed later
- **No data loss**: Each mapping is saved to database immediately during the scan
- **Incremental**: Processes latest Plex additions first, so you can resume interrupted scans
- **Fuzzy matching**: Uses string similarity to match Plex albums with site releases
- ⚠️ **Current limitation**: Albums with no matches will reappear in future scans (improvement planned)

### Fetch Mode (-fm)

The `--fetch-mode` (or `-fm`) option controls how red-plex locates albums in Plex:

#### For all commands (`collages convert`, `collages update`, `bookmarks convert`, `bookmarks update`):
- **torrent_name** (default): Searches for directories matching the torrent folder name
- **query**: Searches using `Artist` and `Album` metadata, ideal for organized libraries managed by tools like Beets or Lidarr

### Database Commands

```bash
# Show database location
red-plex db location

# Manage albums table
red-plex db albums reset        # Clear all album records
red-plex db albums update       # Pull fresh album info from Plex

# Manage collections table
red-plex db collections reset   # Clear the collage collections table

# Manage bookmarks table
red-plex db bookmarks reset     # Clear the bookmark collections table

# Manage remote mappings (core feature for site tags and upstream sync)
red-plex db remote-mappings scan --site [red|ops]  # Create Plex-to-site mappings
red-plex db remote-mappings reset                  # Clear remote mapping data
```

## Examples

### Creating Collections

```bash
# Single collage (Redacted), default mode
red-plex collages convert 12345 --site red

# Multiple collages (Orpheus), default mode
red-plex collages convert 1111 2222 3333 --site ops

# From bookmarks (RED or OPS), default mode
red-plex bookmarks convert --site red

# Remote mappings - scan albums and create mappings using album/artist names
red-plex db remote-mappings scan --site red

# Site tags - create collection from specific tags
red-plex extras site-tags convert --tags "electronic,ambient" --collection-name "Electronic Ambient"

# Upstream sync - push Plex collection changes back to RED collages (RED only)
red-plex collages update 12345 --push  # Sync specific collage
red-plex collages update --push         # Sync all collages
```

### Updating Collections

```bash
# Update all stored collages
red-plex collages update

# Update all stored bookmarks
red-plex bookmarks update

# Update albums from Plex
red-plex db albums update

# Sync collections to upstream collages (RED only)
red-plex collages update --push
```

### Using Query Fetch Mode

```bash
# Create a collection using query mode (for Beets/Lidarr organized libraries)
red-plex collages convert 12345 --site red --fetch-mode query

# Update all bookmarks using query mode
red-plex bookmarks update --site ops -fm query
```

### Complete Workflow Example

#### Command Line Interface
```bash
# 1. First time setup
red-plex config edit  # Add your API keys and Plex details

# 2. Update your local album database from Plex
red-plex db albums update

# 3. Create collections from specific collages
red-plex collages convert 12345 67890 --site red

# 4. Create collection from your bookmarks
red-plex bookmarks convert --site red

# 5. Scan albums for remote mappings (required for site tags and upstream sync)
red-plex db remote-mappings scan --site red

# 6. Create collections from specific tags
red-plex extras site-tags convert --tags "electronic,downtempo" --collection-name "Electronic Downtempo"

# 7. Sync collections back to upstream collages (RED only, requires ownership)
red-plex collages update --push

# 8. Later, update all collections with new releases
red-plex collages update
red-plex bookmarks update

# 9. If you add new music to Plex, re-scan for new mappings
red-plex db remote-mappings scan --site red
```

#### Web Interface
```bash
# 1. Launch the web interface
red-plex gui

# 2. Open http://127.0.0.1:8000 in your browser

# 3. Navigate to Configuration to add your API keys and Plex details

# 4. Use the Database page to update your local album database

# 5. Use the Collages page to convert specific collages

# 6. Use the Bookmarks page to convert your bookmarks

# 7. Use the Remote Mappings page to scan albums and create mappings

# 8. Use Site Tags to create collections from specific tags

# 9. Use the Collages page to sync collections to upstream (RED only)

# 10. Return to Database page later to update all collections
```

## Configuration Details

By default, configuration is stored in `~/.config/red-plex/config.yml`:

```yaml
LOG_LEVEL: INFO
OPS:
  API_KEY: your_ops_api_key_here
  BASE_URL: https://orpheus.network
  RATE_LIMIT:
    calls: 4
    seconds: 15
PLEX_TOKEN: your_plex_token_here
PLEX_URL: http://localhost:32400
RED:
  API_KEY: your_red_api_key_here
  BASE_URL: https://redacted.sh
  RATE_LIMIT:
    calls: 10
    seconds: 10
SECTION_NAME: Music
```

## Configuration Tips

- If HTTP fails, fetch an HTTPS URL:
  ```
  https://plex.tv/api/resources?includeHttps=1&X-Plex-Token={YOUR_TOKEN}
  ```
- Look for the `<Device>` node in the XML for a `uri`, use this `plex.direct` address.
- Use `DEBUG` log level for verbose debugging information
- Use `WARNING` log level for minimal output

## Troubleshooting

### Common Issues

#### Authentication Errors
- Verify your API keys are correct in `config.yml`
- Check that your Plex token is valid
- Ensure you have access to the sites you're trying to use

#### No Albums Found
- Run `red-plex db albums update` to refresh your Plex library
- Check that your Plex music library is properly configured
- Verify the `SECTION_NAME` in your config matches your Plex music library name

#### Rate Limiting Issues
- The tool respects site rate limits automatically
- If you encounter issues, try reducing the rate limit values in your config

#### Fetch Mode Issues
- Use `torrent_name` mode if your library structure matches torrent folder names
- Use `query` mode if you use Beets, Lidarr, or have renamed your music files
- Try both modes to see which works better for your library

#### Web Interface Issues
- **GUI won't start**: Ensure `gunicorn` and `eventlet` are installed: `pip install gunicorn eventlet`
- **Can't access GUI**: Check if the port is available and not blocked by firewall
- **GUI stuck on "Starting..."**: Check terminal logs for error messages
- **WebSocket connection failed**: Ensure your browser supports WebSockets and isn't blocking them

### Getting Help

1. Check the logs with `LOG_LEVEL: DEBUG` in your config
2. Verify your configuration with `red-plex config show`
3. Test your Plex connection by running `red-plex db albums update`
4. Open an issue on GitHub with detailed error messages

## Important Considerations

- **Album Matching Strategy**:
  - `torrent_name` (default): Matches albums by comparing torrent folder names with Plex directory paths
  - `query`: Uses artist and album metadata for matching, ideal for libraries organized by Beets, Lidarr, or other tools that rename files
- **Database Management**: All data is stored in `red_plex.db`. Use database reset commands (`db albums reset`, etc.) to clear specific tables when needed
- **Site Credentials**: Ensure your API keys are valid and have proper permissions
- **Rate Limiting**: The tool automatically respects site-specific rate limits to avoid being banned
- **Logging Levels**: 
  - `DEBUG`: Verbose output for troubleshooting
  - `INFO`: Standard information (default)
  - `WARNING`: Minimal output
- **Collection Updates**: When you run `collages update` or `bookmarks update`, new albums are added to existing Plex collections, but removed items from tracker collages are not automatically removed from Plex collections
- **Upstream Sync (RED Only)**: 
  - Only works with RED (Redacted) - OPS doesn't support the required API operations
  - You must own the collages you want to sync to
  - Convert collages from the site first, even if they're empty
  - Run `red-plex db remote-mappings scan --site red` to create the necessary mappings
  - Uses fuzzy string matching which may occasionally cause mismatches
  - Never deletes items from upstream collages, only adds missing ones
  - Can be interrupted with Ctrl+C and resumed later with no data loss
  - Re-scan after adding new music to your Plex library
- **Remote Mappings**: Core functionality that links Plex items with site group IDs. Required for both site tags and upstream sync features

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
git clone https://github.com/marceljungle/red-plex.git
cd red-plex
pip install -e .
```

---
