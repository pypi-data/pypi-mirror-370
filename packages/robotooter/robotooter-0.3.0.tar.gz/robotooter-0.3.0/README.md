# RoboTooter

A Python framework for easily creating Mastodon bots with pluggable content generation and filtering capabilities.

## Features

- **Multiple Bot Types**: Currently supports Markov chain-based text generation
- **Plugin Architecture**: Extensible plugin system for adding new bot types and functionality
- **Flexible Filtering**: Extensible filter system for processing input text (Gutenberg, blank line removal, paragraph combining)
- **Mastodon Integration**: Built-in support for posting to Mastodon instances
- **CLI Interface**: Comprehensive command line interface for bot and plugin management
- **Configuration Management**: Simple bot configuration and data management

## Why?

I've built a few bots over the years, for fun. Recently I was reminded of a Twitter bot I wrote back in 2019 that
generated sentences from a Markov chain generator trained on the text of Conan the Barbarian stories. I decided to
reimplement it, this time for Mastodon.

I also wanted to be able to easily create other bots to do other things, and so built a simple plugin architecture.

## Examples

- **[Conan-o-matic](https://social.naughtybaptist.com/@conanomatic)** The original reason for this project. Yes, it's silly. I still find it funny.
- **[Chapter By Chapter](https://social.naughtybaptist.com/@chapterbychapter)]** Posts a chapter a day from Public Domain litereature. Victorian-era Netflix.

## Installation

### As a Package

```bash
# Create a virtual environment
$ python3 -m venv .venv
# Activtate it
$ . .venv/bin/activate
# Install via pip
$ pip install robotooter
```

### From Source
This project uses Poetry for dependency management. To install:

```bash
git clone ssh://git@codeberg.org/bfordham/robotooter.git
cd robotooter
poetry install
```

## Quick Start

1. **Configure the framework**:
   ```bash
   robotooter configure
   ```

2. **Create a new bot**:
   ```bash
   robotooter create
   ```

3. **Set up your bot's data** (for Markov bots, add a `sources.txt` file to the bot directory):
   ```bash
   robotooter --bot <bot-name> setup
   ```

4. **Authorize your bot with Mastodon**:
   ```bash
   robotooter --bot <bot-name> authorize
   ```

5. **Generate content locally**:
   ```bash
   robotooter --bot <bot-name> speak
   ```

6. **Post to Mastodon**:
   ```bash
   robotooter --bot <bot-name> toot
   ```

## Bot Types

### Markov Bot

The Markov bot generates text using Markov chains trained on source material. 

**Setup Requirements**:
- Create a `sources.txt` file in your bot's working directory
- Each line should contain a URL to a text file to use as training data
- Run `robotooter --bot <bot-name> setup` to download and process the sources

## Plugin Architecture

RoboTooter now supports a plugin system that allows you to extend the framework with custom bot types and functionality. Plugins inherit from the `BasePlugin` class and can define their own filters and bot implementations.

**Plugin Development**:
- Extend the `BasePlugin` class to create custom bot types
- Register plugins using `robotooter plugins register <plugin-name>`
- Remove plugins with `robotooter plugins remove <plugin-name>`

## CLI Commands

### General Commands
- `robotooter info` - Display information about the local setup
- `robotooter configure` - Initialize configuration
- `robotooter create` - Create a new bot
- `robotooter list` - List all configured bots
- `robotooter version` - Display the current version
- `robotooter help` - Display help information

### Bot-Specific Commands
- `robotooter --bot <name> setup` - Download and process bot training data
- `robotooter --bot <name> authorize [--force]` - Authorize bot with Mastodon
- `robotooter --bot <name> speak [--count N]` - Generate content locally
- `robotooter --bot <name> toot` - Generate and post content to Mastodon

### Plugin Management
- `robotooter plugins register <plugin-name>` - Register a new plugin
- `robotooter plugins remove <plugin-name>` - Remove a plugin
- `robotooter plugins help` - Display plugin management help

## Project Structure

```
src/robotooter/
   bots/                # Bot implementations
       base_bot.py      # Base bot class
       markov/          # Markov chain bot
   cli/                 # Command line interface
   filters/             # Text processing filters
   mastodon_manager.py  # Mastodon API integration
   models.py            # Data models
   util.py              # Utility functions
```

## Development

### Requirements

- Python 3.12+
- Poetry for dependency management

### Development Setup

```bash
poetry install --with dev
```

### Running Tests

```bash
poetry run pytest
```

### Code Quality

The project uses Ruff for linting and MyPy for type checking:

```bash
# Linting
./scripts/lint

# Type checking  
./scripts/type
```

## Dependencies

- **requests**: HTTP client for downloading source material
- **markovify**: Markov chain text generation
- **mastodon.py**: Mastodon API client
- **pydantic**: Data validation and settings management
- **jinja2**: Template engine

## Contributing

If you would like to add features, please feel free. If you use this yourself, [please let me know](https://infosec.exchange/@bfordham)!

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). See the [LICENSE](LICENSE) file for details.

The AGPL-3.0 is a copyleft license that requires anyone who distributes the code or runs it on a server to make the source code available under the same license terms.
