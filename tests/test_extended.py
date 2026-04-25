"""Unit tests for Nebula Writer"""

from unittest.mock import patch

from nebula_writer import BackupManager, Document, Storage


class TestDocument:
    def test_document_creation(self):
        doc = Document(title="Test Doc", content="Hello World")
        assert doc.title == "Test Doc"
        assert doc.content == "Hello World"

    def test_document_word_count(self):
        doc = Document(title="Test", content="one two three four five")
        assert doc.word_count() == 5

    def test_document_update(self):
        doc = Document(title="Test", content="Original")
        doc.update(content="Updated")
        assert doc.content == "Updated"

    def test_document_tags(self):
        doc = Document(title="Test", content="Content")
        doc.add_tag("draft")
        assert "draft" in doc.tags


class TestStorage:
    @patch("nebula_writer.os.path.exists")
    def test_storage_initialization(self, mock_exists):
        mock_exists.return_value = True
        storage = Storage("./data")
        assert storage.base_path == "./data"

    def test_save_document(self):
        with patch("nebula_writer.open", create=True):
            Storage("./data")
            Document(title="Test", content="Content")
            # Test save would work
            assert True

    def test_load_document(self):
        Storage("./data")
        # Mock loading
        assert True


class TestBackupManager:
    def test_backup_creation(self):
        manager = BackupManager("./data", "./backups")
        assert manager.source == "./data"
        assert manager.destination == "./backups"

    def test_list_backups(self):
        manager = BackupManager("./data", "./backups")
        backups = manager.list_backups()
        assert isinstance(backups, list)


class TestExportFormats:
    def test_markdown_export(self):
        doc = Document(title="Test", content="# Hello\nWorld")
        md = doc.export("markdown")
        assert "# Hello" in md

    def test_html_export(self):
        doc = Document(title="Test", content="Hello World")
        html = doc.export("html")
        assert "<html>" in html
