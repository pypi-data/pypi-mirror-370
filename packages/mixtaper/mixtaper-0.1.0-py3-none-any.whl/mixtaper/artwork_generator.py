"""
AI artwork generation using OpenAI DALL-E
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

import requests

from .config import AudioTrack

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ArtworkGenerator:
    """Handles album artwork generation and management"""

    COVER_FILENAMES = ["cover.jpg", "cover.png", "front.jpg", "front.png"]

    def __init__(self):
        self.openai_client = None
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.openai_client = OpenAI()

    def find_existing_cover(self, directory: Path) -> Optional[bytes]:
        """Find existing cover image in directory"""
        for filename in self.COVER_FILENAMES:
            cover_path = directory / filename
            if cover_path.exists():
                try:
                    with open(cover_path, "rb") as f:
                        return f.read()
                except Exception:
                    continue
        return None

    def generate_ai_prompt(
        self, album_info: Dict[str, str], tracks: List[AudioTrack]
    ) -> str:
        """Generate AI prompt based on album and track analysis"""
        if not tracks:
            return f"Album cover for '{album_info.get('album', 'Unknown Album')}'"

        # Analyze musical characteristics
        avg_tempo = sum(track.tempo for track in tracks) / len(tracks)
        avg_energy = sum(track.energy for track in tracks) / len(tracks)

        # Get most common genre
        genre_counts = {}
        for track in tracks:
            if track.genre:
                genre_counts[track.genre] = genre_counts.get(track.genre, 0) + 1

        primary_genre = (
            "music" if not genre_counts else max(genre_counts, key=genre_counts.get)
        )

        # Build descriptive prompt
        album_title = album_info.get("album", "Unknown Album")

        # Tempo-based mood
        if avg_tempo < 90:
            tempo_mood = "calm, meditative"
        elif avg_tempo < 120:
            tempo_mood = "relaxed, steady"
        elif avg_tempo < 140:
            tempo_mood = "energetic, upbeat"
        else:
            tempo_mood = "high-energy, intense"

        # Energy-based atmosphere
        if avg_energy < 0.1:
            energy_mood = "peaceful, serene"
        elif avg_energy < 0.3:
            energy_mood = "gentle, flowing"
        elif avg_energy < 0.5:
            energy_mood = "vibrant, lively"
        else:
            energy_mood = "powerful, dynamic"

        # Genre-specific imagery
        genre_imagery = {
            "rock": "mountain landscapes, stormy skies, rugged terrain",
            "punk": "urban landscapes, graffiti, raw cityscapes",
            "country": "rural landscapes, farmlands, open roads",
            "folk": "forests, acoustic instruments, natural settings",
            "electronic": "futuristic landscapes, neon lights, digital worlds",
            "jazz": "night scenes, smoky atmospheres, urban sophistication",
            "classical": "orchestral halls, elegant architecture, timeless beauty",
            "blues": "crossroads, vintage scenes, soulful environments",
            "hip hop": "urban environments, street art, modern cityscapes",
            "pop": "colorful scenes, modern life, accessible imagery",
        }

        genre_desc = genre_imagery.get(
            primary_genre.lower(), "beautiful natural landscapes"
        )

        prompt = (
            f"Create album cover art for '{album_title}', a {primary_genre} album. "
            f"The music is {tempo_mood} and {energy_mood}. "
            f"Feature {genre_desc}. "
            f"Create a photorealistic nature scene or real-world landscape that captures the mood. "
            f"No text, logos, or album packaging. Focus on natural beauty, landscapes, and real environments. "
            f"High quality, artistic composition suitable for album artwork."
        )

        return prompt

    def generate_ai_artwork(
        self,
        album_info: Dict[str, str],
        tracks: List[AudioTrack],
        custom_prompt: Optional[str] = None,
    ) -> Optional[bytes]:
        """Generate artwork using OpenAI DALL-E"""
        if not self.openai_client:
            return None

        try:
            prompt = custom_prompt or self.generate_ai_prompt(album_info, tracks)

            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url

            # Download the image
            img_response = requests.get(image_url)
            img_response.raise_for_status()

            return img_response.content

        except Exception as e:
            print(f"AI artwork generation failed: {e}")
            return None

    def save_artwork(
        self, directory: Path, artwork_data: bytes, filename: Optional[str] = None
    ) -> Optional[Path]:
        """Save artwork to directory"""
        try:
            if not filename:
                # Determine format from data
                if artwork_data.startswith(b"\x89PNG"):
                    filename = "cover.png"
                else:
                    filename = "cover.jpg"

            artwork_path = directory / filename
            with open(artwork_path, "wb") as f:
                f.write(artwork_data)

            return artwork_path

        except Exception as e:
            print(f"Error saving artwork: {e}")
            return None

    def get_artwork_for_album(
        self,
        directory: Path,
        album_info: Dict[str, str],
        tracks: List[AudioTrack],
        use_ai: bool = False,
        custom_prompt: Optional[str] = None,
    ) -> Optional[bytes]:
        """Get artwork for album - either existing or AI-generated"""
        # First check for existing cover
        existing_artwork = self.find_existing_cover(directory)

        if use_ai:
            # Generate AI artwork
            ai_artwork = self.generate_ai_artwork(album_info, tracks, custom_prompt)
            if ai_artwork:
                # Save the AI artwork
                self.save_artwork(directory, ai_artwork)
                return ai_artwork
            elif existing_artwork:
                print("AI generation failed, using existing cover")
                return existing_artwork
        else:
            # Use existing artwork if available
            if existing_artwork:
                return existing_artwork

        return None
