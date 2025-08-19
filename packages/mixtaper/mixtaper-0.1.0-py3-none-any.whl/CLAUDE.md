# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mixtaper is an AI-powered mixtape creator that analyzes audio files (MP3, FLAC, WAV, M4A, OGG) and crafts optimal track sequences based on musical features like tempo, key, energy, and rhythm complexity. It handles ID3v2/FLAC metadata tagging and AI-generated album artwork via DALL-E.

## Development Commands

### Setup and Installation
```bash
# Install dependencies using uv
uv sync

# Alternative: manual installation
pip install librosa mutagen numpy scipy rich
```

### Running the Tool
```bash
# Using uv (recommended)
uv run mixtaper.py [directory]

# Direct Python execution
python mixtaper.py [directory]
./mixtaper.py [directory]  # if executable

# Install as package and use command
uv pip install -e .
mixtaper [directory]
```

### Development
```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Run with development dependencies
uv sync --dev
```

### Testing
```bash
# Run unit tests
uv sync --dev
uv run python run_tests.py

# Alternative: run pytest directly
uv run pytest tests/ -v

# Test with sample audio files in a directory
uv run mixtaper.py /path/to/test/audio/files

# Test AI artwork generation (requires OPENAI_API_KEY)
export OPENAI_API_KEY="your-api-key"
uv run mixtaper.py --ai-art --dry-run
```

## Architecture

The project is now organized into a modular package structure for better testability and maintainability:

### Package Structure
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

### Core Components

- **AudioAnalyzer** (`audio_analyzer.py`): Handles audio file analysis using librosa
  - Extracts tempo, key, energy, brightness, rhythm complexity
  - Uses mutagen for metadata extraction
  - Supports multiple audio formats
  - Multithreaded analysis capability

- **MixtapeOptimizer** (`mixtape_optimizer.py`): Track ordering optimization
  - Transition scoring algorithm
  - Greedy optimization starting from median-energy track
  - Multi-CD splitting with natural break points
  - Flow analysis and quality metrics

- **MetadataManager** (`metadata_manager.py`): File metadata operations
  - ID3v2 and FLAC tag management
  - Safe file renaming with conflict resolution
  - ReplayGain tag integration
  - Batch processing capabilities

- **MusicBrainzClient** (`musicbrainz_client.py`): Genre lookup service
  - Song-specific genre detection
  - Rate-limited API access
  - Frequency analysis for common genres

- **ArtworkGenerator** (`artwork_generator.py`): Album artwork handling
  - AI generation via OpenAI DALL-E
  - Smart prompt generation based on musical analysis
  - Existing cover detection and management

- **MixtapeTUI** (`tui.py`): Interactive user interface
  - Rich-based configuration prompts
  - Progress display and feedback
  - Final confirmation workflow

### Audio Analysis Features

- **Tempo**: BPM detection for rhythmic continuity
- **Key**: Chromatic feature analysis for harmonic compatibility
- **Energy**: RMS levels for dynamic flow management
- **Brightness**: Spectral centroid for tonal continuity
- **Rhythm Complexity**: Onset density analysis

### Ordering Algorithm

Uses weighted scoring for track transitions:
- Tempo similarity: 30%
- Key compatibility: 20% 
- Energy flow: 25%
- Brightness continuity: 15%
- Rhythm complexity: 10%

Greedy optimization starting from median-energy track.

## Key Dependencies

- **librosa**: Core audio analysis library
- **mutagen**: Metadata extraction/writing for audio files (ID3v2, FLAC)
- **rich**: CLI formatting and user interaction
- **numpy/scipy**: Numerical computations
- **pillow**: Image generation for album artwork
- **openai**: AI artwork generation via DALL-E API
- **requests**: HTTP client for downloading AI-generated images

## File Operations

The tool performs comprehensive file processing:

### Metadata Handling
- Reads existing Artist/Title from ID3v2 (MP3) or FLAC metadata
- Updates all files with album information (Album, Album Artist, Year, Track Number)
- Clears existing tags for consistency
- Supports both ID3v2.4 and FLAC formats

### Album Artwork
- **Existing covers**: Searches for cover.jpg, cover.png, front.jpg, front.png
- **AI generation**: Uses OpenAI DALL-E with smart prompts based on musical analysis
- **Simple generation**: Creates custom artwork if no cover found (600x600 JPEG)
- **Flexible options**: CLI flags for --ai-art, --ai-prompt, --force-ai
- **Metadata integration**: Adds artwork to ID3v2 APIC tags (MP3) or FLAC Picture blocks
- **Smart prompts**: Analyzes tempo, energy, and mood to generate contextual AI prompts

### Safe File Renaming
1. Updates metadata and artwork first
2. Creates temporary filenames to avoid conflicts  
3. Renames to format: "01. Artist - Title.ext"
4. Cleans invalid filename characters
5. Rolls back on errors