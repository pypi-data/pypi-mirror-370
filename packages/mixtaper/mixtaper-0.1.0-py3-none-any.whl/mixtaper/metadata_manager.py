"""
Metadata management for audio files (ID3v2, FLAC tags, ReplayGain)
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

from mutagen import File as MutagenFile
from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, TALB, TCON, TDRC, TIT2, TPE1, TPE2, TPOS, TRCK, TXXX

from .config import AudioTrack


class MetadataManager:
    """Handles metadata operations for audio files"""

    def __init__(self):
        pass

    def clean_filename(self, filename: str) -> str:
        """Clean filename for safe file operations"""
        # Remove or replace problematic characters
        cleaned = re.sub(r'[<>:"/\\|?*]', "_", filename)
        cleaned = re.sub(
            r"[\x00-\x1f\x7f-\x9f]", "", cleaned
        )  # Remove control characters
        cleaned = re.sub(r"\.+$", "", cleaned)  # Remove trailing dots
        cleaned = cleaned.strip()

        # Ensure it's not empty
        if not cleaned:
            cleaned = "Unknown"

        return cleaned

    def update_metadata(
        self,
        track: AudioTrack,
        album_info: Dict[str, str],
        track_number: int,
        disc_number: int = 1,
        artwork_data: Optional[bytes] = None,
    ) -> bool:
        """Update metadata for a single track"""
        try:
            file_path = Path(track.file_path)
            audio_file = MutagenFile(file_path)

            if audio_file is None:
                return False

            # Determine file type and update accordingly
            if file_path.suffix.lower() == ".flac":
                return self._update_flac_metadata(
                    audio_file,
                    track,
                    album_info,
                    track_number,
                    disc_number,
                    artwork_data,
                )
            else:
                return self._update_id3_metadata(
                    audio_file,
                    track,
                    album_info,
                    track_number,
                    disc_number,
                    artwork_data,
                )

        except Exception as e:
            print(f"Error updating metadata for {track.file_path}: {e}")
            return False

    def _update_flac_metadata(
        self,
        flac_file: FLAC,
        track: AudioTrack,
        album_info: Dict[str, str],
        track_number: int,
        disc_number: int,
        artwork_data: Optional[bytes],
    ) -> bool:
        """Update FLAC metadata"""
        try:
            # Clear existing tags
            flac_file.clear()

            # Set basic metadata
            flac_file["TITLE"] = track.title or Path(track.file_path).stem
            flac_file["ARTIST"] = track.artist or "Unknown Artist"
            flac_file["ALBUM"] = album_info.get("album", "Unknown Album")
            flac_file["ALBUMARTIST"] = album_info.get("album_artist", "Various Artists")
            flac_file["DATE"] = album_info.get("year", "2024")
            flac_file["TRACKNUMBER"] = str(track_number)

            if disc_number > 1:
                flac_file["DISCNUMBER"] = str(disc_number)

            if track.genre:
                flac_file["GENRE"] = track.genre

            # Add ReplayGain
            flac_file["REPLAYGAIN_TRACK_GAIN"] = f"{track.replaygain_track_gain:.2f} dB"

            # Add artwork if provided
            if artwork_data:
                picture = Picture()
                picture.data = artwork_data
                picture.type = 3  # Cover (front)
                picture.mime = (
                    "image/png" if artwork_data.startswith(b"\x89PNG") else "image/jpeg"
                )
                picture.width = 600
                picture.height = 600
                picture.depth = 24
                flac_file.add_picture(picture)

            flac_file.save()
            return True

        except Exception as e:
            print(f"Error updating FLAC metadata: {e}")
            return False

    def _update_id3_metadata(
        self,
        audio_file,
        track: AudioTrack,
        album_info: Dict[str, str],
        track_number: int,
        disc_number: int,
        artwork_data: Optional[bytes],
    ) -> bool:
        """Update ID3v2 metadata"""
        try:
            # Ensure we have ID3 tags
            if not hasattr(audio_file, "tags") or audio_file.tags is None:
                audio_file.add_tags()

            tags = audio_file.tags

            # Clear existing tags
            tags.clear()

            # Set basic metadata
            tags.add(TIT2(encoding=3, text=track.title or Path(track.file_path).stem))
            tags.add(TPE1(encoding=3, text=track.artist or "Unknown Artist"))
            tags.add(TALB(encoding=3, text=album_info.get("album", "Unknown Album")))
            tags.add(
                TPE2(encoding=3, text=album_info.get("album_artist", "Various Artists"))
            )
            tags.add(TDRC(encoding=3, text=album_info.get("year", "2024")))
            tags.add(TRCK(encoding=3, text=str(track_number)))

            if disc_number > 1:
                tags.add(TPOS(encoding=3, text=str(disc_number)))

            if track.genre:
                tags.add(TCON(encoding=3, text=track.genre))

            # Add ReplayGain
            tags.add(
                TXXX(
                    encoding=3,
                    desc="REPLAYGAIN_TRACK_GAIN",
                    text=f"{track.replaygain_track_gain:.2f} dB",
                )
            )

            # Add artwork if provided
            if artwork_data:
                mime_type = (
                    "image/png" if artwork_data.startswith(b"\x89PNG") else "image/jpeg"
                )
                tags.add(
                    APIC(
                        encoding=3,
                        mime=mime_type,
                        type=3,  # Cover (front)
                        desc="Cover",
                        data=artwork_data,
                    )
                )

            audio_file.save()
            return True

        except Exception as e:
            print(f"Error updating ID3 metadata: {e}")
            return False

    def rename_file(self, track: AudioTrack, new_name: str) -> Optional[str]:
        """Rename file and return new path"""
        try:
            old_path = Path(track.file_path)
            new_path = old_path.parent / f"{new_name}{old_path.suffix}"

            # Check if target already exists
            if new_path.exists() and new_path != old_path:
                # Create temporary name to avoid conflicts
                temp_path = old_path.parent / f"temp_{new_name}{old_path.suffix}"
                old_path.rename(temp_path)
                temp_path.rename(new_path)
            else:
                old_path.rename(new_path)

            return str(new_path)

        except Exception as e:
            print(f"Error renaming {track.file_path}: {e}")
            return None

    def batch_update_and_rename(
        self,
        tracks: List[AudioTrack],
        track_orders: List[List[int]],
        album_info: Dict[str, str],
        artwork_data: Optional[bytes] = None,
    ) -> bool:
        """Update metadata and rename files for all tracks"""
        try:
            num_cds = len(track_orders)

            for cd_num, track_indices in enumerate(track_orders, 1):
                for track_pos, track_idx in enumerate(track_indices, 1):
                    track = tracks[track_idx]

                    # Calculate track number for multi-CD sets
                    if num_cds > 1:
                        track_number = (
                            cd_num * 100 + track_pos
                        )  # e.g., 201 for CD 2, track 1
                        disc_number = cd_num
                    else:
                        track_number = track_pos
                        disc_number = 1

                    # Update metadata first
                    success = self.update_metadata(
                        track, album_info, track_number, disc_number, artwork_data
                    )

                    if not success:
                        print(f"Failed to update metadata for {track.filename}")
                        continue

                    # Generate new filename
                    artist = track.artist or "Unknown Artist"
                    title = track.title or Path(track.file_path).stem

                    if num_cds > 1:
                        filename = f"{track_number:03d}. {artist} - {title}"
                    else:
                        filename = f"{track_pos:02d}. {artist} - {title}"

                    filename = self.clean_filename(filename)

                    # Rename file
                    new_path = self.rename_file(track, filename)
                    if new_path:
                        track.file_path = new_path
                        print(f"✓ {filename}")
                    else:
                        print(f"✗ Failed to rename {track.filename}")

            return True

        except Exception as e:
            print(f"Error in batch update and rename: {e}")
            return False

    def extract_album_info_from_directory(self, directory: Path) -> Dict[str, str]:
        """Extract album info from directory name using common patterns"""
        dir_name = directory.name

        # Pattern: "Artist - Year - Album (Type)"
        match = re.match(
            r"(.+?)\s*-\s*(\d{4})\s*-\s*(.+?)(?:\s*\([^)]+\))?\s*$", dir_name
        )
        if match:
            return {
                "album_artist": match.group(1).strip(),
                "year": match.group(2),
                "album": match.group(3).strip(),
            }

        # Pattern: "Artist - Album (Year)"
        match = re.match(r"(.+?)\s*-\s*(.+?)\s*\((\d{4})\)\s*$", dir_name)
        if match:
            return {
                "album_artist": match.group(1).strip(),
                "album": match.group(2).strip(),
                "year": match.group(3),
            }

        # Default: use directory name as album
        return {
            "album_artist": "Various Artists",
            "album": dir_name.replace("_", " ").replace("-", " ").title(),
            "year": "2024",
        }
