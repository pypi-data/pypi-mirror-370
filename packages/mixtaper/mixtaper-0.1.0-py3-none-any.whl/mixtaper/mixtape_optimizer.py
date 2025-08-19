"""
Mixtape optimization and track ordering algorithms
"""

import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List

from .config import AudioTrack


class MixtapeOptimizer:
    """Handles track ordering optimization for mixtapes"""

    # Weights for transition scoring
    TEMPO_WEIGHT = 0.30
    KEY_WEIGHT = 0.20
    ENERGY_WEIGHT = 0.25
    BRIGHTNESS_WEIGHT = 0.15
    RHYTHM_WEIGHT = 0.10

    def __init__(self):
        pass

    def calculate_transition_score(
        self, track1: AudioTrack, track2: AudioTrack
    ) -> float:
        """Calculate how well two tracks transition into each other"""
        # Tempo similarity (closer tempos = higher score)
        tempo_diff = abs(track1.tempo - track2.tempo)
        tempo_score = max(0, 1 - tempo_diff / 60)  # Normalize by 60 BPM

        # Key compatibility (circle of fifths)
        key_diff = min(abs(track1.key - track2.key), 12 - abs(track1.key - track2.key))
        key_score = max(0, 1 - key_diff / 6)  # Normalize by 6 semitones

        # Energy flow (should be gradual)
        energy_diff = abs(track1.energy - track2.energy)
        energy_score = max(0, 1 - energy_diff / 0.5)  # Normalize by 0.5

        # Brightness continuity
        brightness_diff = abs(track1.brightness - track2.brightness)
        brightness_score = max(0, 1 - brightness_diff / 2000)  # Normalize by 2000 Hz

        # Rhythm complexity similarity
        rhythm_diff = abs(track1.rhythm_complexity - track2.rhythm_complexity)
        rhythm_score = max(0, 1 - rhythm_diff / 5)  # Normalize by 5 onsets/sec

        # Weighted combination
        total_score = (
            tempo_score * self.TEMPO_WEIGHT
            + key_score * self.KEY_WEIGHT
            + energy_score * self.ENERGY_WEIGHT
            + brightness_score * self.BRIGHTNESS_WEIGHT
            + rhythm_score * self.RHYTHM_WEIGHT
        )

        return total_score

    def find_optimal_order(self, tracks: List[AudioTrack]) -> List[int]:
        """Find optimal track ordering using greedy algorithm"""
        if len(tracks) <= 1:
            return list(range(len(tracks)))

        # Start with the track that has median energy (good starting point)
        energies = [track.energy for track in tracks]
        median_energy = sorted(energies)[len(energies) // 2]

        start_idx = min(
            range(len(tracks)), key=lambda i: abs(tracks[i].energy - median_energy)
        )

        order = [start_idx]
        remaining = set(range(len(tracks))) - {start_idx}

        # Greedy selection: always pick the best next track
        while remaining:
            current_track = tracks[order[-1]]

            best_score = -1
            best_idx = None

            for idx in remaining:
                score = self.calculate_transition_score(current_track, tracks[idx])
                if score > best_score:
                    best_score = score
                    best_idx = idx

            if best_idx is not None:
                order.append(best_idx)
                remaining.remove(best_idx)

        return order

    def split_tracks_across_cds(
        self, tracks: List[AudioTrack], optimal_order: List[int], num_cds: int
    ) -> List[List[int]]:
        """Split tracks across multiple CDs while maintaining good flow"""
        if num_cds <= 1:
            return [optimal_order]

        total_tracks = len(optimal_order)
        base_tracks_per_cd = total_tracks // num_cds
        extra_tracks = total_tracks % num_cds

        cd_orders = []
        start_idx = 0

        for cd_num in range(num_cds):
            # Determine how many tracks for this CD
            tracks_for_cd = base_tracks_per_cd + (1 if cd_num < extra_tracks else 0)
            end_idx = start_idx + tracks_for_cd

            cd_tracks = optimal_order[start_idx:end_idx]

            # Try to find natural breaking points based on energy
            if cd_num < num_cds - 1 and end_idx < len(optimal_order):
                # Look for a good transition point within ±2 tracks
                current_energy = tracks[optimal_order[end_idx - 1]].energy
                next_energy = tracks[optimal_order[end_idx]].energy

                best_break = end_idx
                best_energy_diff = abs(current_energy - next_energy)

                for offset in range(-2, 3):
                    test_idx = end_idx + offset
                    if start_idx < test_idx < len(optimal_order):
                        test_current = tracks[optimal_order[test_idx - 1]].energy
                        test_next = tracks[optimal_order[test_idx]].energy
                        energy_diff = abs(test_current - test_next)

                        if energy_diff > best_energy_diff:  # Bigger gap = better break
                            best_energy_diff = energy_diff
                            best_break = test_idx

                # Adjust the split if we found a better break point
                if best_break != end_idx:
                    end_idx = best_break
                    cd_tracks = optimal_order[start_idx:end_idx]

            cd_orders.append(cd_tracks)
            start_idx = end_idx

        return cd_orders

    def suggest_num_cds(self, num_tracks: int) -> int:
        """Suggest optimal number of CDs based on track count"""
        if num_tracks <= 18:
            return 1
        elif num_tracks <= 36:
            return 2
        elif num_tracks <= 54:
            return 3
        else:
            return math.ceil(num_tracks / 18)

    def analyze_track_flow(
        self, tracks: List[AudioTrack], order: List[int]
    ) -> Dict[str, float]:
        """Analyze the flow quality of a track ordering"""
        if len(order) <= 1:
            return {"average_transition_score": 1.0, "total_score": 1.0}

        transition_scores = []

        for i in range(len(order) - 1):
            score = self.calculate_transition_score(
                tracks[order[i]], tracks[order[i + 1]]
            )
            transition_scores.append(score)

        avg_score = sum(transition_scores) / len(transition_scores)
        total_score = sum(transition_scores)

        return {
            "average_transition_score": avg_score,
            "total_score": total_score,
            "transition_scores": transition_scores,
        }

    def optimize_with_multithreading(
        self, tracks: List[AudioTrack], max_workers: int = 4
    ) -> List[int]:
        """Optimize track order using multiple threads for larger collections"""
        if len(tracks) <= 20:
            # For smaller collections, single-threaded is fine
            return self.find_optimal_order(tracks)

        # For larger collections, try multiple starting points
        num_attempts = min(max_workers, len(tracks))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []

            # Try different starting points
            for i in range(num_attempts):
                future = executor.submit(self._optimize_from_start_point, tracks, i)
                futures.append(future)

            best_order = None
            best_score = -1

            for future in as_completed(futures):
                order = future.result()
                flow_analysis = self.analyze_track_flow(tracks, order)
                score = flow_analysis["total_score"]

                if score > best_score:
                    best_score = score
                    best_order = order

        return best_order or list(range(len(tracks)))

    def _optimize_from_start_point(
        self, tracks: List[AudioTrack], start_idx: int
    ) -> List[int]:
        """Optimize starting from a specific track index"""
        if not tracks:
            return []

        start_idx = start_idx % len(tracks)
        order = [start_idx]
        remaining = set(range(len(tracks))) - {start_idx}

        while remaining:
            current_track = tracks[order[-1]]

            best_score = -1
            best_idx = None

            for idx in remaining:
                score = self.calculate_transition_score(current_track, tracks[idx])
                if score > best_score:
                    best_score = score
                    best_idx = idx

            if best_idx is not None:
                order.append(best_idx)
                remaining.remove(best_idx)

        return order
