"""
Tests for mixtape optimization algorithms
"""

from mixtaper.config import AudioTrack
from mixtaper.mixtape_optimizer import MixtapeOptimizer


class TestMixtapeOptimizer:
    """Test MixtapeOptimizer class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.optimizer = MixtapeOptimizer()

        # Create test tracks with different characteristics
        self.tracks = [
            AudioTrack(
                file_path="/music/track1.mp3",
                artist="Artist A",
                title="Song 1",
                tempo=120.0,
                key=0,
                energy=0.5,
                brightness=1000.0,
                rhythm_complexity=2.0,
            ),
            AudioTrack(
                file_path="/music/track2.mp3",
                artist="Artist B",
                title="Song 2",
                tempo=125.0,
                key=1,
                energy=0.6,
                brightness=1100.0,
                rhythm_complexity=2.2,
            ),
            AudioTrack(
                file_path="/music/track3.mp3",
                artist="Artist C",
                title="Song 3",
                tempo=110.0,
                key=11,
                energy=0.3,
                brightness=900.0,
                rhythm_complexity=1.8,
            ),
            AudioTrack(
                file_path="/music/track4.mp3",
                artist="Artist D",
                title="Song 4",
                tempo=130.0,
                key=2,
                energy=0.8,
                brightness=1200.0,
                rhythm_complexity=2.5,
            ),
        ]

    def test_calculate_transition_score(self):
        """Test transition score calculation"""
        track1 = self.tracks[0]
        track2 = self.tracks[1]

        score = self.optimizer.calculate_transition_score(track1, track2)

        # Score should be between 0 and 1
        assert 0.0 <= score <= 1.0

        # Score should be higher for similar tracks
        track1_copy = AudioTrack(
            file_path="/music/copy.mp3",
            tempo=track1.tempo,
            key=track1.key,
            energy=track1.energy,
            brightness=track1.brightness,
            rhythm_complexity=track1.rhythm_complexity,
        )

        similar_score = self.optimizer.calculate_transition_score(track1, track1_copy)
        assert similar_score > score

    def test_find_optimal_order_empty(self):
        """Test optimal order with empty track list"""
        order = self.optimizer.find_optimal_order([])
        assert order == []

    def test_find_optimal_order_single_track(self):
        """Test optimal order with single track"""
        order = self.optimizer.find_optimal_order([self.tracks[0]])
        assert order == [0]

    def test_find_optimal_order_multiple_tracks(self):
        """Test optimal order with multiple tracks"""
        order = self.optimizer.find_optimal_order(self.tracks)

        # Should return all track indices
        assert len(order) == len(self.tracks)
        assert set(order) == set(range(len(self.tracks)))

        # Should be a valid ordering (no duplicates)
        assert len(set(order)) == len(order)

    def test_suggest_num_cds(self):
        """Test CD number suggestions"""
        assert self.optimizer.suggest_num_cds(10) == 1
        assert self.optimizer.suggest_num_cds(18) == 1
        assert self.optimizer.suggest_num_cds(20) == 2
        assert self.optimizer.suggest_num_cds(36) == 2
        assert self.optimizer.suggest_num_cds(40) == 3
        assert self.optimizer.suggest_num_cds(72) == 4

    def test_split_tracks_across_cds_single(self):
        """Test splitting tracks across single CD"""
        order = list(range(len(self.tracks)))
        cd_orders = self.optimizer.split_tracks_across_cds(self.tracks, order, 1)

        assert len(cd_orders) == 1
        assert cd_orders[0] == order

    def test_split_tracks_across_cds_multiple(self):
        """Test splitting tracks across multiple CDs"""
        order = list(range(len(self.tracks)))
        cd_orders = self.optimizer.split_tracks_across_cds(self.tracks, order, 2)

        assert len(cd_orders) == 2

        # All tracks should be included
        all_tracks = []
        for cd_order in cd_orders:
            all_tracks.extend(cd_order)
        assert set(all_tracks) == set(order)

        # Each CD should have tracks
        for cd_order in cd_orders:
            assert len(cd_order) > 0

    def test_analyze_track_flow(self):
        """Test track flow analysis"""
        order = [0, 1, 2, 3]
        analysis = self.optimizer.analyze_track_flow(self.tracks, order)

        assert "average_transition_score" in analysis
        assert "total_score" in analysis
        assert "transition_scores" in analysis

        assert 0.0 <= analysis["average_transition_score"] <= 1.0
        assert analysis["total_score"] >= 0.0
        assert len(analysis["transition_scores"]) == len(order) - 1

    def test_analyze_track_flow_single_track(self):
        """Test flow analysis with single track"""
        analysis = self.optimizer.analyze_track_flow(self.tracks, [0])

        assert analysis["average_transition_score"] == 1.0
        assert analysis["total_score"] == 1.0
