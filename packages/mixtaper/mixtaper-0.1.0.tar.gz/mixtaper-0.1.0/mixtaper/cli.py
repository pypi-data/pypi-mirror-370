"""
Command-line interface for the mixtape organizer
"""

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List

from rich.console import Console
from rich.prompt import Confirm

from .artwork_generator import ArtworkGenerator
from .audio_analyzer import AudioAnalyzer
from .config import AlbumConfig, AudioTrack
from .metadata_manager import MetadataManager
from .mixtape_optimizer import MixtapeOptimizer
from .musicbrainz_client import MusicBrainzClient
from .tui import MixtapeTUI

console = Console()


class MixtapeOrganizer:
    """Main orchestrator for the mixtape organization process"""

    def __init__(self):
        self.audio_analyzer = AudioAnalyzer()
        self.metadata_manager = MetadataManager()
        self.musicbrainz_client = MusicBrainzClient()
        self.artwork_generator = ArtworkGenerator()
        self.mixtape_optimizer = MixtapeOptimizer()
        self.tui = MixtapeTUI()

    def analyze_files_multithreaded(
        self, file_paths: List[Path], max_workers: int = 4
    ) -> List[AudioTrack]:
        """Analyze audio files using multiple threads"""
        tracks = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            self.tui.show_progress_header("Audio Analysis")

            # Submit all analysis tasks
            future_to_path = {
                executor.submit(self.audio_analyzer.analyze_audio_features, path): path
                for path in file_paths
            }

            # Collect results as they complete
            for i, future in enumerate(as_completed(future_to_path), 1):
                try:
                    track = future.result()
                    if track:
                        tracks.append(track)
                        self.tui.show_track_analysis_progress(
                            i, len(file_paths), track.filename
                        )
                except Exception as e:
                    path = future_to_path[future]
                    self.tui.show_error(f"Failed to analyze {path.name}: {e}")

        return tracks

    def process_directory(self, directory: Path, config: AlbumConfig) -> bool:
        """Process a complete directory of audio files"""
        try:
            # Find audio files
            audio_files = self.audio_analyzer.find_audio_files(directory)
            if not audio_files:
                self.tui.show_error("No supported audio files found")
                return False

            console.print(f"Found {len(audio_files)} audio files")

            # Analyze audio files
            tracks = self.analyze_files_multithreaded(audio_files)
            if not tracks:
                self.tui.show_error("No audio files could be analyzed")
                return False

            # Look up genres
            self.tui.show_progress_header("Genre Lookup")
            self.musicbrainz_client.lookup_all_track_genres(tracks)

            # Optimize track order
            optimal_order = self.mixtape_optimizer.find_optimal_order(tracks)

            # Split across CDs if needed
            if config.num_cds > 1:
                track_orders = self.mixtape_optimizer.split_tracks_across_cds(
                    tracks, optimal_order, config.num_cds
                )
            else:
                track_orders = [optimal_order]

            # Display results
            self.tui.display_track_order(tracks, track_orders, config.num_cds)

            # Handle artwork
            album_info = {
                "album": config.title,
                "album_artist": config.album_artist,
                "year": config.year,
            }

            artwork_data = None
            if config.use_ai_art:
                # Generate AI prompt based on analysis
                ai_prompt = self.artwork_generator.generate_ai_prompt(
                    album_info, tracks
                )

                # Allow user to edit prompt in interactive mode
                if not config.auto_mode:
                    ai_prompt = self.tui.get_ai_prompt_input(ai_prompt)
                elif config.ai_prompt:
                    # Use custom prompt from command line
                    ai_prompt = config.ai_prompt

                # Generate AI artwork
                self.tui.show_info("Generating AI artwork...")
                artwork_data = self.artwork_generator.generate_ai_artwork(
                    album_info, tracks, ai_prompt
                )

                if artwork_data:
                    # Save the artwork
                    self.artwork_generator.save_artwork(directory, artwork_data)
                    self.tui.show_success("AI artwork generated")
                else:
                    self.tui.show_error("AI artwork generation failed")
                    # Fall back to existing cover
                    artwork_data = self.artwork_generator.find_existing_cover(directory)
                    if artwork_data:
                        self.tui.show_info("Using existing cover image")
            else:
                # Use existing cover if available
                artwork_data = self.artwork_generator.find_existing_cover(directory)
                if artwork_data:
                    self.tui.show_success("Using existing cover image")

            # Update metadata and rename files
            success = self.metadata_manager.batch_update_and_rename(
                tracks, track_orders, album_info, artwork_data
            )

            if success:
                self.tui.show_success("Mixtape crafted successfully!")
                console.print(f"  • {len(tracks)} tracks processed")
                console.print(
                    f"  • {config.num_cds} CD{'s' if config.num_cds > 1 else ''} created"
                )
                console.print("  • Metadata and ReplayGain tags updated")
                if artwork_data:
                    mode = "generated" if config.use_ai_art else "preserved"
                    console.print(f"  • Album artwork {mode}")
                return True
            else:
                self.tui.show_error("Failed to complete file operations")
                return False

        except Exception as e:
            self.tui.show_error(f"Processing failed: {e}")
            return False


def create_argument_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Analyze audio files and create optimized mixtapes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mixtape /path/to/music                    # Interactive mode
  mixtape /path/to/music --auto             # Automatic mode with defaults
  mixtape /path/to/music --ai-art           # Generate AI artwork
  mixtape /path/to/music --num-cds 2        # Split across 2 CDs
  mixtape /path/to/music --dry-run          # Preview without changes
        """,
    )

    parser.add_argument(
        "directory", type=str, help="Directory containing audio files to organize"
    )

    # Album configuration
    parser.add_argument(
        "--title", type=str, help="Album title (default: directory name)"
    )

    parser.add_argument(
        "--artist", type=str, help="Album artist (default: Various Artists)"
    )

    parser.add_argument("--year", type=str, help="Release year (default: current year)")

    parser.add_argument(
        "--num-cds",
        type=int,
        help="Number of CDs to split across (default: auto-suggest)",
    )

    # Artwork options
    parser.add_argument(
        "--ai-art", action="store_true", help="Generate AI artwork using DALL-E"
    )

    parser.add_argument(
        "--ai-prompt", type=str, help="Custom prompt for AI artwork generation"
    )

    # Operation modes
    parser.add_argument(
        "--auto", action="store_true", help="Automatic mode - no interactive prompts"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview operations without making changes",
    )

    parser.add_argument(
        "-y", "--yes", action="store_true", help="Automatically confirm all prompts"
    )

    # Performance options
    parser.add_argument(
        "--threads",
        type=int,
        default=4,
        help="Number of threads for analysis (default: 4)",
    )

    return parser


def main():
    """Main entry point for the mixtape organizer"""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Validate directory
    directory = Path(args.directory).resolve()
    if not directory.exists():
        console.print(f"[red]Error: Directory '{directory}' does not exist[/red]")
        sys.exit(1)

    if not directory.is_dir():
        console.print(f"[red]Error: '{directory}' is not a directory[/red]")
        sys.exit(1)

    # Initialize components
    organizer = MixtapeOrganizer()

    # Display header
    console.print("\n[bold cyan]╔══ Mixtaper ══╗[/bold cyan]")
    console.print(f"[cyan]Processing: {directory}[/cyan]")

    # Configuration phase
    config = AlbumConfig()

    # Determine if we're in interactive mode
    has_manual_config = any(
        [args.title, args.artist, args.year, args.num_cds is not None, args.ai_art]
    )
    interactive_mode = not (args.auto or args.yes or args.dry_run or has_manual_config)

    if interactive_mode:
        # Interactive configuration
        audio_files = organizer.audio_analyzer.find_audio_files(directory)
        suggested_cds = organizer.mixtape_optimizer.suggest_num_cds(len(audio_files))
        has_existing_cover = (
            organizer.artwork_generator.find_existing_cover(directory) is not None
        )

        config = organizer.tui.get_album_configuration(
            directory, suggested_cds, has_existing_cover
        )
    else:
        # Non-interactive configuration
        metadata = organizer.metadata_manager.extract_album_info_from_directory(
            directory
        )

        config.title = args.title or metadata.get("album", directory.name)
        config.album_artist = args.artist or metadata.get(
            "album_artist", "Various Artists"
        )
        config.year = args.year or metadata.get("year", config.year)
        config.use_ai_art = args.ai_art
        config.ai_prompt = args.ai_prompt
        config.auto_mode = args.auto or args.yes

        if args.num_cds:
            config.num_cds = args.num_cds
        else:
            audio_files = organizer.audio_analyzer.find_audio_files(directory)
            config.num_cds = organizer.mixtape_optimizer.suggest_num_cds(
                len(audio_files)
            )

    # Dry run check
    if args.dry_run:
        console.print("\n[yellow]Dry run mode - no files will be modified[/yellow]")
        # TODO: Implement dry run preview
        return

    # Final confirmation for interactive mode
    if interactive_mode:
        audio_files = organizer.audio_analyzer.find_audio_files(directory)
        if not organizer.tui.show_final_confirmation(config, len(audio_files)):
            console.print("[yellow]Operation cancelled[/yellow]")
            return
    elif not config.auto_mode:
        if not Confirm.ask("Proceed with these settings?", default=True):
            console.print("[yellow]Operation cancelled[/yellow]")
            return

    # Process the directory
    success = organizer.process_directory(directory, config)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
