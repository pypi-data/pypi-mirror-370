# 🎵 Mixtaper

[![CI/CD Pipeline](https://github.com/ido50/mixtaper/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/ido50/mixtaper/actions/workflows/ci-cd.yml)
[![PyPI version](https://badge.fury.io/py/mixtaper.svg)](https://badge.fury.io/py/mixtaper)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

AI-powered mixtape creator that turns a directory of music files into a flowing
track sequence, suitable for a personal mixtape. Using advanced audio analysis
and machine learning, it arranges tracks based on musical characteristics like
tempo, key, energy, and rhythm to create flowing mixtapes.

## Features

- **🎵 Audio Analysis**: Extracts tempo, key, energy, brightness, and rhythm
  complexity from MP3, FLAC, WAV, M4A, and OGG files
- **🎯 Smart Ordering**: Uses weighted transition scoring to create optimal
  track sequences
- **🎨 AI Artwork**: Generate album artwork using OpenAI DALL-E based on musical
  analysis
- **📀 Multi-CD Support**: Automatically splits large collections across multiple
  CDs with natural break points
- **🏷️ Metadata Management**: Updates ID3v2/FLAC tags with album info, track
  numbers and ReplayGain
- **🎭 Genre Detection**: Looks up accurate genres using MusicBrainz database
- **⚡ Multithreaded**: Fast analysis using parallel processing
- **🖥️ Rich UI**: Beautiful command-line interface with progress indicators

## Rationale and Overview

This project was created using Claude Code. I wanted to quickly whip up something
that will formalize and automate how I created "mixtapes" for myself. I prefer
creating my own compilation albums versus creating playlist files (e.g. m3u).
I do so by creating a new subdirectory under my Music directory, dumping a dozen
or so pre-selected music files into it, ordering them, generating cover art with
an AI image generator, updating their ID3 tags and renaming them in the chosen
order. I mostly create mixtapes based on certain moods, so that I can quickly
choose a playlist based on what I want to hear. I find that music collection
managers that have "mood" as a filter work terribly.

The only problem is choosing a good order for the songs. It always takes too
long and I don't want every mixtape to turn into some ridiculous project. So I
created `mixtaper` to make this process quicker. I can now just dump the files
into a directory and let the program do everything for me:

1. Analyze the songs for things like tempo, key, energy, etc.
2. Choose an ordering for the songs that will "flow well" based on the analysis.
3. Generate cover art via OpenAI DALL-E (or select an existing
   `^(cover|front)\.(png|jpg)$` image in the directory).
4. Calculate ReplayGain values for the tracks individually and the album as a
   whole.
5. Set relevant ID3 tags for the files.
6. Rename the files with the format "<TRACK_NUMBER>. <ARTIST> - <TITLE>".

I also added support for multi-CD mixtapes. `mixtaper` will recommend a number of
CDs if it finds that the directory contains "more songs than common in albums",
and prefix the files with the disc number, so, "<DISC_NUMBER><TRACK_NUMBER>. <ARTIST> - <TITLE>".

This is an early release. I decided to let Claude Code implement this and see
how it goes. For now, it seems to work quite nicely. My biggest issue right now
is how to craft a good prompt for the cover art generation. The current prompt
generator isn't good, but prompts can be edited. The ordering `mixtaper` creates
could be better, but I'm fine with it for now. I can always tinker with the
parameters and re-run.

By default, `mixtaper` works interactively, asking you questions and also for
confirmation. You can pre-answer questions via command line flags, or opt for
completely automatic, non-interactive execution. Information later on.

## Installation

`mixtaper` is a command line utility written in Python and distributed via PyPI.
It is recommended to install it via a utility such as [pipx](https://github.com/pypa/pipx):

```sh
pipx install mixtaper
```

You can also install it directly through `pip`:

```sh
python3 -m pip install mixtaper
```

## Usage

### Basic Usage

```bash
# Interactive mode - prompts for configuration
mixtaper /path/to/music

# Automatic mode with smart defaults
mixtaper /path/to/music --auto

# Preview without making changes
mixtaper /path/to/music --dry-run
```

### Advanced Options

```bash
# Generate AI artwork (requires OpenAI API key)
export OPENAI_API_KEY="your-api-key"
mixtaper /path/to/music --ai-art

# Preset album information
mixtaper /path/to/music --title "My Mixtape" --artist "DJ Name" --year 2024

# Preselect number of CDs
mixtaper /path/to/music --num-cds 2

# Predefine AI artwork prompt
mixtaper /path/to/music --ai-art --ai-prompt "Abstract digital art with neon colors"

# Performance tuning
mixtaper /path/to/music --threads 8
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `--title` | Album title (default: directory name) |
| `--artist` | Album artist (default: Various Artists) |
| `--year` | Release year (default: current year) |
| `--num-cds` | Number of CDs to create (default: auto-suggest) |
| `--ai-art` | Generate AI artwork using DALL-E |
| `--ai-prompt` | Custom prompt for AI artwork generation |
| `--auto` | Automatic mode - no interactive prompts |
| `--dry-run` | Preview operations without making changes |
| `-y, --yes` | Automatically confirm all prompts |
| `--threads` | Number of analysis threads (default: 4) |

## How It Works

### 1. Audio Analysis
The tool analyzes each audio file to extract:
- **Tempo**: BPM detection for rhythmic continuity
- **Key**: Chromatic feature analysis for harmonic compatibility
- **Energy**: RMS levels for dynamic flow management
- **Brightness**: Spectral centroid for tonal continuity
- **Rhythm Complexity**: Onset density analysis

### 2. Track Optimization
Uses a weighted scoring algorithm for track transitions:
- Tempo similarity: 30%
- Key compatibility: 20%
- Energy flow: 25%
- Brightness continuity: 15%
- Rhythm complexity: 10%

### 3. Metadata Enhancement
- Reads existing Artist/Title from file metadata
- Looks up accurate genres via MusicBrainz API
- Updates all files with consistent album information
- Adds ReplayGain tags for volume normalization
- Embeds album artwork in file metadata

### 4. File Organization
- Renames files to format: "01. Artist - Title.ext"
- For multi-CD sets: "201. Artist - Title.ext" (CD 2, Track 1)
- Safe renaming with conflict resolution
- Preserves original files if errors occur

## Directory Structure

The project uses a modular architecture for maintainability:

```
mixtaper/
├── __init__.py           # Package exports
├── config.py             # Configuration and data classes
├── audio_analyzer.py     # Audio analysis using librosa
├── metadata_manager.py   # ID3v2/FLAC metadata handling
├── musicbrainz_client.py # MusicBrainz API integration
├── artwork_generator.py  # AI artwork generation
├── mixtape_optimizer.py  # Track ordering algorithms
├── tui.py               # Rich-based user interface
└── cli.py               # Command-line interface
```

## Development

### Running Tests

```bash
# Install development dependencies
uv sync --dev

# Run all tests
uv run python run_tests.py

# Or use pytest directly
uv run pytest tests/ -v
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .
```

### Testing with Sample Files

```bash
# Test with audio files
uv run mixtaper.py /path/to/test/audio/files

# Test AI artwork (requires OpenAI API key)
export OPENAI_API_KEY="your-api-key"
uv run mixtaper.py /path/to/music --ai-art --dry-run
```

## Requirements

### System Dependencies
- Python 3.8+
- FFmpeg (for audio format support)

### Python Dependencies
- **librosa**: Audio analysis and feature extraction
- **mutagen**: Audio metadata reading/writing
- **rich**: Beautiful command-line interface
- **numpy/scipy**: Numerical computations
- **openai**: AI artwork generation (optional)
- **requests**: HTTP client for API calls

### Optional
- **OpenAI API Key**: For AI artwork generation
- **MusicBrainz**: Free genre lookup (no API key required)

## Examples

### Example Output

```
╔══ Mixtaper ══╗
Processing: /music/Various Artists - 2024 - New Wave Mix

╔══ Audio Analysis ══╗
  [1/13] Analyzing: 04. The Cure - Boys Don't Cry.flac
  [2/13] Analyzing: 03. Don Henley - The Boys Of Summer.flac
  ...

╔══ Genre Lookup ══╗
  [1/13] The Cure - Boys Don't Cry
    Genre: alternative rock
  [2/13] Don Henley - The Boys Of Summer
    Genre: classic rock
  ...

╔══ Suggested Track Order ══╗
01. Crowded House - Don't Dream It's Over [alternative rock] (82 BPM, Energy: 0.17)
02. A-Ha - Take on Me [dance-pop] (85 BPM, Energy: 0.18)
03. Don Henley - The Boys Of Summer [classic rock] (89 BPM, Energy: 0.16)
...

✓ Mixtape organization complete!
  • 13 tracks processed
  • 1 CD created
  • Metadata and ReplayGain tags updated
  • Album artwork preserved
```

### Directory Structure Example

```
Various Artists - 2024 - New Wave Mix/
├── cover.jpg                                    # Album artwork
├── 01. Crowded House - Don't Dream It's Over.flac
├── 02. A-Ha - Take on Me.flac
├── 03. Don Henley - The Boys Of Summer.flac
└── ...
```

## License

Apache License 2.0 - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `uv run python run_tests.py`
5. Submit a pull request

## Support

- Report issues: [GitHub Issues](https://github.com/ido50/mixtaper/issues)
- Documentation: See `CLAUDE.md` for development details
- Examples: Check the `tests/` directory for usage examples
