"""
Audio analysis module for extracting musical features from audio files
"""

import warnings
from pathlib import Path
from typing import List, Optional

import librosa
import numpy as np
from mutagen import File as MutagenFile

from .config import AudioTrack


class AudioAnalyzer:
    """Handles audio file analysis using librosa"""

    SUPPORTED_FORMATS = {".mp3", ".flac", ".wav", ".m4a", ".ogg"}

    def __init__(self):
        # Suppress specific warnings that don't affect functionality
        warnings.filterwarnings("ignore", category=UserWarning, module="librosa")

    def find_audio_files(self, directory: Path) -> List[Path]:
        """Find all supported audio files in directory"""
        audio_files = []
        for file_path in directory.rglob("*"):
            if (
                file_path.is_file()
                and file_path.suffix.lower() in self.SUPPORTED_FORMATS
            ):
                audio_files.append(file_path)
        return sorted(audio_files)

    def extract_metadata(self, file_path: Path) -> tuple[str, str]:
        """Extract artist and title from audio file metadata"""
        try:
            audio_file = MutagenFile(file_path, easy=True)
            if audio_file is None:
                return "", ""

            artist = ""
            title = ""

            # Try to get artist and title
            if hasattr(audio_file, "get"):
                artist_list = audio_file.get("artist", [])
                title_list = audio_file.get("title", [])

                if artist_list:
                    artist = str(artist_list[0])
                if title_list:
                    title = str(title_list[0])

            return artist, title

        except Exception:
            return "", ""

    def analyze_audio_features(self, file_path: Path) -> Optional[AudioTrack]:
        """Analyze audio file and extract musical features"""
        try:
            # Load audio file with error handling for different sample rates
            try:
                # First try with default parameters
                y, sr = librosa.load(file_path, sr=None)
            except Exception:
                # If that fails, force a standard sample rate
                y, sr = librosa.load(file_path, sr=22050)

            # Ensure we have valid audio data
            if len(y) == 0:
                return None

            # Extract metadata
            artist, title = self.extract_metadata(file_path)

            # Calculate duration
            duration = librosa.get_duration(y=y, sr=sr)

            # Tempo analysis
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            if np.isscalar(tempo):
                tempo = float(tempo)
            else:
                tempo = float(tempo[0]) if len(tempo) > 0 else 120.0

            # Key analysis using chromagram
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            key = int(np.argmax(np.mean(chroma, axis=1)))

            # Energy analysis (RMS)
            rms = librosa.feature.rms(y=y)
            energy = float(np.mean(rms))

            # Brightness (spectral centroid)
            # Adjust parameters for high sample rates to avoid warnings
            n_fft = min(2048, len(y))
            hop_length = n_fft // 4

            spectral_centroid = librosa.feature.spectral_centroid(
                y=y, sr=sr, n_fft=n_fft, hop_length=hop_length
            )
            brightness = float(np.mean(spectral_centroid))

            # Rhythm complexity (onset density)
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hop_length)
            rhythm_complexity = len(onset_frames) / duration if duration > 0 else 0.0

            # ReplayGain calculation (simple RMS-based approximation)
            rms_db = 20 * np.log10(np.maximum(np.sqrt(np.mean(y**2)), 1e-10))
            replaygain_track_gain = -(rms_db + 14.0)  # Target -14 dBFS

            return AudioTrack(
                file_path=str(file_path),
                artist=artist,
                title=title,
                tempo=tempo,
                key=key,
                energy=energy,
                brightness=brightness,
                rhythm_complexity=rhythm_complexity,
                replaygain_track_gain=replaygain_track_gain,
                duration=duration,
            )

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None

    def batch_analyze(self, file_paths: List[Path]) -> List[AudioTrack]:
        """Analyze multiple audio files sequentially"""
        tracks = []
        for file_path in file_paths:
            track = self.analyze_audio_features(file_path)
            if track:
                tracks.append(track)
        return tracks
