"""
Mixtape Organizer - A modular audio analysis and mixtape creation tool
"""

from .artwork_generator import ArtworkGenerator
from .audio_analyzer import AudioAnalyzer
from .config import AlbumConfig
from .metadata_manager import MetadataManager
from .mixtape_optimizer import MixtapeOptimizer
from .musicbrainz_client import MusicBrainzClient
from .tui import MixtapeTUI

__version__ = "0.1.0"
__all__ = [
    "AudioAnalyzer",
    "MetadataManager",
    "MusicBrainzClient",
    "ArtworkGenerator",
    "MixtapeOptimizer",
    "AlbumConfig",
    "MixtapeTUI",
]
