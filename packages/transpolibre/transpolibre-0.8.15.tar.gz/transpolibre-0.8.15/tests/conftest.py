"""
Pytest configuration and fixtures for tests.
"""

import pytest
import sys
import os


@pytest.fixture(autouse=True)
def reset_test_state():
    """
    Reset test state before and after each test to ensure isolation.
    This fixture runs automatically for all tests.
    """
    # Store original state
    original_modules = set(sys.modules.keys())
    original_env = os.environ.copy()

    # Clear any cached module-level state
    modules_to_clear = [
        "transpolibre.main",
        "transpolibre.lib.trans_msg",
        "transpolibre.lib.trans_pofile",
        "transpolibre.lib.trans_local",
        "transpolibre.lib.trans_ollama",
        "transpolibre.lib.trans_list",
        "transpolibre.lib.parse_arguments",
        "transpolibre.lib.get_lang_name",
        "transpolibre.lib.update_pofile",
    ]

    for module_name in modules_to_clear:
        if module_name in sys.modules:
            # Reset any module-level variables
            if hasattr(sys.modules[module_name], "_gettext_func"):
                sys.modules[module_name]._gettext_func = None

    yield  # Run the test

    # Clean up after test
    # Remove any modules that were added during the test
    modules_to_remove = set(sys.modules.keys()) - original_modules
    for module_name in modules_to_remove:
        if module_name.startswith("transpolibre"):
            del sys.modules[module_name]

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def temp_po_file(tmp_path):
    """
    Create a temporary PO file for testing.
    """
    import polib

    po_file = tmp_path / "test.po"
    po = polib.POFile()
    po.metadata = {
        "Project-Id-Version": "1.0",
        "Language": "en",
        "Content-Type": "text/plain; charset=UTF-8",
    }

    # Add some test entries
    po.append(polib.POEntry(msgid="Hello World", msgstr=""))
    po.append(polib.POEntry(msgid="This is a test message", msgstr=""))
    po.append(polib.POEntry(msgid="Multi-line\nmessage\nhere", msgstr=""))
    po.append(
        polib.POEntry(
            msgid="Welcome to the application", msgstr="Bienvenido a la aplicación"
        )
    )

    po.save(str(po_file))
    return str(po_file)


@pytest.fixture
def temp_po_file_with_urls(tmp_path):
    """
    Create a temporary PO file with URL entries for testing.
    """
    import polib

    po_file = tmp_path / "test_urls.po"
    po = polib.POFile()
    po.metadata = {
        "Project-Id-Version": "1.0",
        "Language": "en",
        "Content-Type": "text/plain; charset=UTF-8",
    }

    # Add entries with URLs
    po.append(
        polib.POEntry(msgid="`Documentation <https://example.com/docs>`_", msgstr="")
    )
    po.append(
        polib.POEntry(msgid="Visit `our website <https://example.com>`_", msgstr="")
    )

    po.save(str(po_file))
    return str(po_file)


@pytest.fixture
def temp_po_file_with_emails(tmp_path):
    """
    Create a temporary PO file with email entries for testing.
    """
    import polib

    po_file = tmp_path / "test_emails.po"
    po = polib.POFile()
    po.metadata = {
        "Project-Id-Version": "1.0",
        "Language": "en",
        "Content-Type": "text/plain; charset=UTF-8",
    }

    # Add entries with emails
    po.append(polib.POEntry(msgid="Contact us at <support@example.com>", msgstr=""))
    po.append(polib.POEntry(msgid="Email <admin@test.org> for help", msgstr=""))

    po.save(str(po_file))
    return str(po_file)


@pytest.fixture
def malformed_po_file(tmp_path):
    """
    Create a malformed PO file for testing error handling.
    """
    po_file = tmp_path / "malformed.po"
    # Write invalid PO content
    with open(po_file, "w") as f:
        f.write("This is not a valid PO file\n")
        f.write("msgid without quotes\n")
        f.write("msgstr also without quotes\n")
    return str(po_file)


@pytest.fixture
def empty_po_file(tmp_path):
    """
    Create an empty PO file for testing.
    """
    import polib

    po_file = tmp_path / "empty.po"
    po = polib.POFile()
    po.metadata = {
        "Project-Id-Version": "1.0",
        "Language": "en",
        "Content-Type": "text/plain; charset=UTF-8",
    }
    # No entries added - empty file
    po.save(str(po_file))
    return str(po_file)


@pytest.fixture
def mock_env_variables(monkeypatch):
    """
    Mock environment variables for testing.
    """
    # Set test environment variables
    monkeypatch.setenv("LT_URL", "http://test.libretranslate.com")
    monkeypatch.setenv("LT_API_KEY", "test-api-key")
    yield
    # Cleanup happens automatically with monkeypatch
