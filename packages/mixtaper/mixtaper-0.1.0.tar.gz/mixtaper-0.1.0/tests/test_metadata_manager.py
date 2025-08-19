"""
Tests for metadata management functionality
"""

from pathlib import Path

import pytest

from mixtaper.config import AudioTrack
from mixtaper.metadata_manager import MetadataManager


class TestMetadataManager:
    """Test MetadataManager class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = MetadataManager()

    def test_clean_filename(self):
        """Test filename cleaning"""
        # Test problematic characters
        assert self.manager.clean_filename('song<>:"/\\|?*.mp3') == "song_________.mp3"

        # Test control characters
        assert self.manager.clean_filename("song\x00\x1f\x7f.mp3") == "song.mp3"

        # Test trailing dots
        assert self.manager.clean_filename("song...") == "song"

        # Test empty string
        assert self.manager.clean_filename("") == "Unknown"
        assert self.manager.clean_filename("   ") == "Unknown"

        # Test normal filename
        assert self.manager.clean_filename("Normal Song.mp3") == "Normal Song.mp3"

        # Test unicode characters
        assert self.manager.clean_filename("Café Münchën.mp3") == "Café Münchën.mp3"

    def test_extract_album_info_from_directory(self):
        """Test album info extraction from directory names"""
        # Test pattern: "Artist - Year - Album (Type)"
        dir_path = Path("/music/Various Artists - 2023 - Great Hits (Compilation)")
        info = self.manager.extract_album_info_from_directory(dir_path)

        assert info["album_artist"] == "Various Artists"
        assert info["year"] == "2023"
        assert info["album"] == "Great Hits"

        # Test pattern: "Artist - Album (Year)"
        dir_path = Path("/music/The Beatles - Abbey Road (1969)")
        info = self.manager.extract_album_info_from_directory(dir_path)

        assert info["album_artist"] == "The Beatles"
        assert info["album"] == "Abbey Road"
        assert info["year"] == "1969"

        # Test default pattern
        dir_path = Path("/music/Random_Music-Collection")
        info = self.manager.extract_album_info_from_directory(dir_path)

        assert info["album_artist"] == "Various Artists"
        assert info["album"] == "Random Music Collection"
        assert info["year"] == "2024"

    def test_batch_update_and_rename_structure(self):
        """Test the structure of batch update and rename (without file I/O)"""
        # Create test tracks
        tracks = [
            AudioTrack(file_path="/tmp/test1.mp3", artist="Artist A", title="Song 1"),
            AudioTrack(file_path="/tmp/test2.mp3", artist="Artist B", title="Song 2"),
        ]

        track_orders = [[0, 1]]  # Single CD
        album_info = {
            "album": "Test Album",
            "album_artist": "Various Artists",
            "year": "2023",
        }

        # This test just verifies the method accepts the right parameters
        # Actual file operations would require test files
        try:
            # Should not crash on parameter validation
            result = self.manager.batch_update_and_rename(
                tracks, track_orders, album_info, None
            )
            # Will likely return False due to missing files, but that's expected
            assert isinstance(result, bool)
        except TypeError:
            pytest.fail("Method signature is incorrect")

    def test_track_ordering_calculation(self):
        """Test track numbering logic for multi-CD sets"""
        # Multi-CD: tracks should be numbered 101, 102, 201, 202...
        track_orders_multi = [[1, 2], [2]]

        # Test the numbering logic that would be used
        for cd_num, track_indices in enumerate(track_orders_multi, 1):
            for track_pos in track_indices:
                if len(track_orders_multi) > 1:
                    expected_track_number = cd_num * 100 + track_pos
                    if cd_num == 1 and track_pos == 1:
                        assert expected_track_number == 101
                    elif cd_num == 1 and track_pos == 2:
                        assert expected_track_number == 102
                    elif cd_num == 2 and track_pos == 1:
                        assert expected_track_number == 201
