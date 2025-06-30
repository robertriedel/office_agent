import os
import tempfile

import notes_module


def test_search_notes(tmp_path):
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()
    # create two notes
    (notes_dir / "note_1.txt").write_text("meeting agenda")
    (notes_dir / "note_2.txt").write_text("shopping list")
    # temporarily patch NOTES_DIR
    old_dir = notes_module.NOTES_DIR
    notes_module.NOTES_DIR = str(notes_dir)
    try:
        results = notes_module.search_notes("meeting")
        assert len(results) == 1
        assert results[0].endswith("note_1.txt")
    finally:
        notes_module.NOTES_DIR = old_dir
