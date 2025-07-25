import tempfile
from pathlib import Path
from unittest.mock import Mock

from scdl.scdl import ArchiveManager


def test_archive_manager_init(tmp_path: Path) -> None:
    """Test ArchiveManager initialization creates necessary tables"""
    archive_path = tmp_path / "test_archive.json"
    
    with ArchiveManager(archive_path) as archive:
        assert archive.archive_path.exists()
        stats = archive.get_statistics()
        assert stats['total_tracks'] == 0
        assert stats['total_added'] == 0


def test_add_track_new(tmp_path: Path) -> None:
    """Test adding a new track to the archive"""
    archive_path = tmp_path / "test_archive.json"
    
    # Create mock track
    mock_track = Mock()
    mock_track.id = 123456
    mock_track.title = "Test Track"
    
    with ArchiveManager(archive_path) as archive:
        result = archive.add_track(mock_track, playlist="Test Playlist", removed=False)
        assert result is True  # New track added
        assert archive.is_track_downloaded(123456)


def test_add_track_existing(tmp_path: Path) -> None:
    """Test adding an existing track updates it"""
    archive_path = tmp_path / "test_archive.json"
    
    mock_track = Mock()
    mock_track.id = 123456
    mock_track.title = "Test Track"
    
    with ArchiveManager(archive_path) as archive:
        # Add track first time
        archive.add_track(mock_track, playlist="Playlist 1")
        # Add same track again
        result = archive.add_track(mock_track, playlist="Playlist 2")
        assert result is False  # Existing track updated
        
        track_info = archive.get_track_info(123456)
        assert track_info['playlist'] == "Playlist 2"


def test_check_for_removed_tracks(tmp_path: Path) -> None:
    """Test checking for removed tracks marks them as removed"""
    archive_path = tmp_path / "test_archive.json"
    
    mock_track1 = Mock()
    mock_track1.id = 111
    mock_track2 = Mock()
    mock_track2.id = 222
    
    with ArchiveManager(archive_path) as archive:
        # Add two tracks
        archive.add_track(mock_track1, playlist="Test Playlist", removed=False)
        archive.add_track(mock_track2, playlist="Test Playlist", removed=False)
        
        # Check with only one track present (simulate track 222 being removed)
        current_ids = {111}
        removed_tracks = archive.check_for_removed_tracks(current_ids, "Test Playlist")
        
        assert len(removed_tracks) == 1
        assert removed_tracks[0]['track_id'] == 222
        
        # Verify track 222 is now marked as removed
        track_info = archive.get_track_info(222)
        assert track_info['removed'] is True


def test_get_statistics(tmp_path: Path) -> None:
    """Test getting archive statistics"""
    archive_path = tmp_path / "test_archive.json"
    
    mock_track = Mock()
    mock_track.id = 123456
    
    with ArchiveManager(archive_path) as archive:
        # Initially empty
        stats = archive.get_statistics()
        assert stats['total_tracks'] == 0
        
        # Add a track
        archive.add_track(mock_track)
        stats = archive.get_statistics()
        assert stats['total_tracks'] == 1
        assert stats['total_added'] == 1
        assert stats['total_seen'] == 1