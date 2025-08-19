"""
Configuration classes for the mixtape organizer
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AlbumConfig:
    """Configuration for album metadata and processing options"""

    title: str = ""
    album_artist: str = "Various Artists"
    year: str = ""
    num_cds: int = 1
    use_ai_art: bool = False
    ai_prompt: Optional[str] = None
    auto_mode: bool = False

    def __post_init__(self):
        if not self.year:
            self.year = str(datetime.now().year)


@dataclass
class AudioTrack:
    """Represents an analyzed audio track with metadata and features"""

    file_path: str
    artist: str = ""
    title: str = ""
    genre: str = ""
    tempo: float = 0.0
    key: int = 0
    energy: float = 0.0
    brightness: float = 0.0
    rhythm_complexity: float = 0.0
    replaygain_track_gain: float = 0.0
    duration: float = 0.0

    @property
    def filename(self) -> str:
        """Get the filename without path"""
        return self.file_path.split("/")[-1]

    def __str__(self) -> str:
        return (
            f"{self.artist} - {self.title}"
            if self.artist and self.title
            else self.filename
        )
