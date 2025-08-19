"""
Text User Interface components for interactive configuration
"""

from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from .config import AlbumConfig

console = Console()


class MixtapeTUI:
    """Rich-based Text User Interface for mixtape configuration"""

    def __init__(self):
        self.console = console

    def get_album_configuration(
        self, directory: Path, suggested_cds: int, has_existing_cover: bool
    ) -> AlbumConfig:
        """Interactive album configuration"""
        config = AlbumConfig()

        self.console.print("\n[bold cyan]╔══ Album Configuration ══╗[/bold cyan]")

        # Album title
        default_title = directory.name.replace("_", " ").replace("-", " ").title()
        config.title = Prompt.ask("[cyan]Album title[/cyan]", default=default_title)

        # Album artist
        config.album_artist = Prompt.ask(
            "[cyan]Album artist[/cyan]", default="Various Artists"
        )

        # Year
        config.year = Prompt.ask("[cyan]Release year[/cyan]", default=config.year)

        # Number of CDs
        if suggested_cds > 1:
            self.console.print(f"[yellow]Suggested: {suggested_cds} CDs[/yellow]")

        config.num_cds = IntPrompt.ask(
            "[cyan]Number of CDs[/cyan]", default=suggested_cds, show_default=True
        )

        # Artwork options
        self.console.print("\n[bold cyan]Artwork Options:[/bold cyan]")

        if has_existing_cover:
            self.console.print("[green]✓ Existing cover image found[/green]")
            config.use_ai_art = Confirm.ask(
                "[cyan]Generate new AI artwork instead?[/cyan]", default=False
            )
        else:
            self.console.print("[yellow]No existing cover image found[/yellow]")
            config.use_ai_art = Confirm.ask(
                "[cyan]Generate AI artwork?[/cyan]", default=True
            )

        return config

    def get_ai_prompt_input(self, generated_prompt: str) -> str:
        """Allow user to edit the AI prompt"""
        import os
        import subprocess
        import tempfile

        self.console.print("\n[bold cyan]AI Artwork Prompt:[/bold cyan]")
        self.console.print(f"[dim]{generated_prompt}[/dim]")

        self.console.print("\n[dim]Editing options:[/dim]")
        self.console.print(
            "[dim]  y = Edit inline (with arrow keys if readline available)[/dim]"
        )
        self.console.print("[dim]  n = Use as-is[/dim]")
        self.console.print("[dim]  editor = Open in external editor ($EDITOR)[/dim]")

        edit_choice = Prompt.ask(
            "\n[cyan]Edit this prompt?[/cyan]",
            choices=["y", "n", "editor"],
            default="n",
            show_choices=True,
            show_default=True,
        )

        if edit_choice == "n":
            return generated_prompt
        elif edit_choice == "editor":
            # Use external editor for advanced editing
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w+", suffix=".txt", delete=False
                ) as f:
                    f.write(generated_prompt)
                    temp_file = f.name

                # Get editor from environment or use sensible default
                editor = os.environ.get("EDITOR", "nano")

                self.console.print(
                    f"[cyan]Opening {editor} for prompt editing...[/cyan]"
                )
                subprocess.run([editor, temp_file])

                # Read back the edited content
                with open(temp_file) as f:
                    edited_prompt = f.read().strip()

                # Clean up
                os.unlink(temp_file)

                if edited_prompt:
                    return edited_prompt
                else:
                    self.console.print("[yellow]Empty prompt, using original[/yellow]")
                    return generated_prompt

            except Exception as e:
                self.console.print(f"[red]Editor failed: {e}[/red]")
                self.console.print("[yellow]Falling back to simple input[/yellow]")
                return self._simple_prompt_edit(generated_prompt)
        else:
            # Simple inline editing
            return self._simple_prompt_edit(generated_prompt)

    def _simple_prompt_edit(self, generated_prompt: str) -> str:
        """Simple prompt editing with readline support"""
        try:
            # Try to enable readline for better editing
            import readline

            readline.set_startup_hook(lambda: readline.insert_text(generated_prompt))
        except ImportError:
            pass

        self.console.print(
            "\n[cyan]Edit the prompt (use arrow keys if available):[/cyan]"
        )

        try:
            edited_prompt = input("> ").strip()
            if edited_prompt:
                return edited_prompt
            else:
                self.console.print("[yellow]Empty prompt, using original[/yellow]")
                return generated_prompt
        except (EOFError, KeyboardInterrupt):
            self.console.print("[yellow]Edit cancelled, using original prompt[/yellow]")
            return generated_prompt
        finally:
            try:
                readline.set_startup_hook()  # Clear the hook
            except (NameError, AttributeError):
                pass

    def show_final_confirmation(self, config: AlbumConfig, num_tracks: int) -> bool:
        """Show final confirmation before processing"""
        self.console.print("\n[bold cyan]╔══ Final Confirmation ══╗[/bold cyan]")

        # Create summary table
        table = Table(show_header=False, box=None)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Album Title:", config.title)
        table.add_row("Album Artist:", config.album_artist)
        table.add_row("Year:", config.year)
        table.add_row("Number of CDs:", str(config.num_cds))
        table.add_row("Total Tracks:", str(num_tracks))

        if config.use_ai_art:
            artwork_text = "Generate AI artwork"
            if config.ai_prompt:
                artwork_text += " (custom prompt)"
        else:
            artwork_text = "Use existing cover or none"

        table.add_row("Artwork:", artwork_text)

        self.console.print(table)

        return Confirm.ask("\n[cyan]Proceed with file operations?[/cyan]", default=True)

    def show_progress_header(self, title: str):
        """Show a progress section header"""
        self.console.print(f"\n[bold cyan]╔══ {title} ══╗[/bold cyan]")

    def show_track_analysis_progress(self, current: int, total: int, filename: str):
        """Show track analysis progress"""
        progress = f"[{current}/{total}]"
        self.console.print(f"[cyan]{progress:>8}[/cyan] Analyzing: {filename}")

    def show_genre_lookup_progress(
        self, current: int, total: int, artist: str, title: str
    ):
        """Show genre lookup progress"""
        progress = f"[{current}/{total}]"
        self.console.print(f"[cyan]{progress:>8}[/cyan] {artist} - {title}")

    def display_track_order(self, tracks, track_orders, num_cds: int):
        """Display the suggested track order"""
        self.console.print("\n[bold cyan]╔══ Suggested Track Order ══╗[/bold cyan]")

        for cd_num, track_indices in enumerate(track_orders, 1):
            if num_cds > 1:
                self.console.print(f"\n[bold yellow]CD {cd_num}:[/bold yellow]")

            for track_pos, track_idx in enumerate(track_indices, 1):
                track = tracks[track_idx]

                # Format track number
                if num_cds > 1:
                    track_num = f"{cd_num}{track_pos:02d}"
                else:
                    track_num = f"{track_pos:02d}"

                # Format track info
                artist = track.artist or "Unknown Artist"
                title = track.title or Path(track.file_path).stem

                # Add genre if available
                genre_text = f" [{track.genre}]" if track.genre else ""

                # Format tempo and energy info
                info_text = f"({track.tempo:.0f} BPM, Energy: {track.energy:.2f})"

                self.console.print(
                    f"[white]{track_num}.[/white] [green]{artist}[/green] - "
                    f"[yellow]{title}[/yellow][dim]{genre_text}[/dim] [dim]{info_text}[/dim]"
                )

    def show_error(self, message: str):
        """Display an error message"""
        self.console.print(f"[red]Error: {message}[/red]")

    def show_warning(self, message: str):
        """Display a warning message"""
        self.console.print(f"[yellow]Warning: {message}[/yellow]")

    def show_success(self, message: str):
        """Display a success message"""
        self.console.print(f"[green]✓ {message}[/green]")

    def show_info(self, message: str):
        """Display an info message"""
        self.console.print(f"[cyan]{message}[/cyan]")
