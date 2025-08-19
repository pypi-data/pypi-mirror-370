"""
Tests for configuration classes
"""

from datetime import datetime

from mixtaper.config import AlbumConfig, AudioTrack


class TestAlbumConfig:
    """Test AlbumConfig dataclass"""

    def test_default_values(self):
        """Test default configuration values"""
        config = AlbumConfig()

        assert config.title == ""
        assert config.album_artist == "Various Artists"
        assert config.year == str(datetime.now().year)
        assert config.num_cds == 1
        assert config.use_ai_art is False
        assert config.ai_prompt is None
        assert config.auto_mode is False

    def test_custom_values(self):
        """Test configuration with custom values"""
        config = AlbumConfig(
            title="Test Album",
            album_artist="Test Artist",
            year="2023",
            num_cds=2,
            use_ai_art=True,
            ai_prompt="Custom prompt",
            auto_mode=True,
        )

        assert config.title == "Test Album"
        assert config.album_artist == "Test Artist"
        assert config.year == "2023"
        assert config.num_cds == 2
        assert config.use_ai_art is True
        assert config.ai_prompt == "Custom prompt"
        assert config.auto_mode is True


class TestAudioTrack:
    """Test AudioTrack dataclass"""

    def test_default_values(self):
        """Test default track values"""
        track = AudioTrack(file_path="/path/to/song.mp3")

        assert track.file_path == "/path/to/song.mp3"
        assert track.artist == ""
        assert track.title == ""
        assert track.genre == ""
        assert track.tempo == 0.0
        assert track.key == 0
        assert track.energy == 0.0
        assert track.brightness == 0.0
        assert track.rhythm_complexity == 0.0
        assert track.replaygain_track_gain == 0.0
        assert track.duration == 0.0

    def test_filename_property(self):
        """Test filename extraction from path"""
        track = AudioTrack(file_path="/path/to/test_song.mp3")
        assert track.filename == "test_song.mp3"

        track = AudioTrack(file_path="song.flac")
        assert track.filename == "song.flac"

    def test_str_representation(self):
        """Test string representation"""
        # With artist and title
        track = AudioTrack(
            file_path="/path/to/song.mp3", artist="Test Artist", title="Test Song"
        )
        assert str(track) == "Test Artist - Test Song"

        # Without artist and title
        track = AudioTrack(file_path="/path/to/song.mp3")
        assert str(track) == "song.mp3"

        # With only artist
        track = AudioTrack(file_path="/path/to/song.mp3", artist="Test Artist")
        assert str(track) == "song.mp3"

    def test_full_track_data(self):
        """Test track with complete data"""
        track = AudioTrack(
            file_path="/music/artist - song.mp3",
            artist="The Artist",
            title="Great Song",
            genre="Rock",
            tempo=120.5,
            key=7,
            energy=0.75,
            brightness=1500.0,
            rhythm_complexity=3.2,
            replaygain_track_gain=-12.5,
            duration=180.0,
        )

        assert track.artist == "The Artist"
        assert track.title == "Great Song"
        assert track.genre == "Rock"
        assert track.tempo == 120.5
        assert track.key == 7
        assert track.energy == 0.75
        assert track.brightness == 1500.0
        assert track.rhythm_complexity == 3.2
        assert track.replaygain_track_gain == -12.5
        assert track.duration == 180.0
        assert track.filename == "artist - song.mp3"
        assert str(track) == "The Artist - Great Song"
