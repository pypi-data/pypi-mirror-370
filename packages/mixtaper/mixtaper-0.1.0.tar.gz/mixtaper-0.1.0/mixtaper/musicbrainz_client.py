"""
MusicBrainz API client for genre and metadata lookup
"""

import time
from typing import List, Optional

import requests

from .config import AudioTrack


class MusicBrainzClient:
    """MusicBrainz API integration for genre lookup"""

    BASE_URL = "https://musicbrainz.org/ws/2"
    USER_AGENT = "MixtapeOrganizer/1.0 (https://github.com/user/mixtape-organizer)"
    RATE_LIMIT_DELAY = 1.0  # seconds between requests

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": self.USER_AGENT, "Accept": "application/json"}
        )
        self._last_request_time = 0

    def _rate_limit(self):
        """Ensure we don't exceed API rate limits"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - time_since_last)
        self._last_request_time = time.time()

    def search_artist(self, artist_name: str) -> Optional[str]:
        """Search for artist and return MBID"""
        self._rate_limit()

        try:
            params = {"query": f'artist:"{artist_name}"', "fmt": "json", "limit": 1}
            response = self.session.get(f"{self.BASE_URL}/artist", params=params)
            response.raise_for_status()

            data = response.json()
            if data.get("artists") and len(data["artists"]) > 0:
                return data["artists"][0]["id"]
            return None
        except Exception:
            return None

    def get_artist_genres(self, artist_mbid: str) -> List[str]:
        """Get genres for an artist by MBID, sorted by popularity (count)"""
        self._rate_limit()

        try:
            params = {"inc": "genres", "fmt": "json"}
            response = self.session.get(
                f"{self.BASE_URL}/artist/{artist_mbid}", params=params
            )
            response.raise_for_status()

            data = response.json()
            genres = []
            if "genres" in data:
                # Extract genres with counts, sort by count (descending)
                genre_items = []
                for genre in data["genres"]:
                    if "name" in genre:
                        count = genre.get("count", 0)
                        genre_items.append((genre["name"], count))

                # Sort by count descending, then alphabetically for ties
                genre_items.sort(key=lambda x: (-x[1], x[0]))
                genres = [name for name, count in genre_items]

            return genres
        except Exception:
            return []

    def search_recording(self, artist_name: str, title: str) -> Optional[str]:
        """Search for a recording by artist and title, return MBID"""
        self._rate_limit()

        try:
            # Clean up the search terms
            artist_clean = artist_name.strip().replace('"', '\\"')
            title_clean = title.strip().replace('"', '\\"')

            params = {
                "query": f'artist:"{artist_clean}" AND recording:"{title_clean}"',
                "fmt": "json",
                "limit": 1,
            }
            response = self.session.get(f"{self.BASE_URL}/recording", params=params)
            response.raise_for_status()

            data = response.json()
            if data.get("recordings") and len(data["recordings"]) > 0:
                return data["recordings"][0]["id"]
            return None
        except Exception:
            return None

    def get_recording_genres(self, recording_mbid: str) -> List[str]:
        """Get genres for a recording by MBID, sorted by popularity"""
        self._rate_limit()

        try:
            params = {"inc": "genres+artist-credits", "fmt": "json"}
            response = self.session.get(
                f"{self.BASE_URL}/recording/{recording_mbid}", params=params
            )
            response.raise_for_status()

            data = response.json()
            genres = []

            # First try to get genres from the recording itself
            if "genres" in data and data["genres"]:
                # Extract and sort recording genres by count
                genre_items = []
                for genre in data["genres"]:
                    if "name" in genre:
                        count = genre.get("count", 0)
                        genre_items.append((genre["name"], count))

                # Sort by count descending, then alphabetically
                genre_items.sort(key=lambda x: (-x[1], x[0]))
                genres = [name for name, count in genre_items]

            # If no recording genres, try to get from the artist
            if not genres and "artist-credit" in data and data["artist-credit"]:
                # Try to get artist MBID from the artist-credit directly
                if (
                    "artist" in data["artist-credit"][0]
                    and "id" in data["artist-credit"][0]["artist"]
                ):
                    artist_mbid = data["artist-credit"][0]["artist"]["id"]
                    genres = self.get_artist_genres(artist_mbid)
                else:
                    # Fallback to search
                    artist_name = data["artist-credit"][0]["name"]
                    artist_mbid = self.search_artist(artist_name)
                    if artist_mbid:
                        genres = self.get_artist_genres(artist_mbid)

            return genres
        except Exception:
            return []

    def lookup_track_genre(self, track: AudioTrack) -> Optional[str]:
        """Look up genre for a specific track"""
        if not track.artist or not track.title:
            return None

        # First try to find the specific recording
        recording_mbid = self.search_recording(track.artist, track.title)
        if recording_mbid:
            genres = self.get_recording_genres(recording_mbid)
            if genres:
                return genres[0]  # Return the first/primary genre

        # Fallback to artist lookup
        artist_mbid = self.search_artist(track.artist)
        if artist_mbid:
            genres = self.get_artist_genres(artist_mbid)
            if genres:
                return genres[0]

        return None

    def lookup_all_track_genres(self, tracks: List[AudioTrack]) -> None:
        """Look up genres for all tracks and update them in-place"""
        print(f"Looking up genres for {len(tracks)} tracks...")

        for i, track in enumerate(tracks):
            print(f"  [{i + 1}/{len(tracks)}] {track.artist} - {track.title}")

            genre = self.lookup_track_genre(track)
            if genre:
                track.genre = genre
                print(f"    Genre: {genre}")
            else:
                print("    Genre: Not found")

    def get_most_common_genre(self, tracks: List[AudioTrack]) -> str:
        """Get the most common genre from a list of tracks"""
        genre_counts = {}
        for track in tracks:
            if track.genre:
                genre_counts[track.genre] = genre_counts.get(track.genre, 0) + 1

        if not genre_counts:
            return "Various"

        # Return the most common genre
        return max(genre_counts, key=genre_counts.get)
