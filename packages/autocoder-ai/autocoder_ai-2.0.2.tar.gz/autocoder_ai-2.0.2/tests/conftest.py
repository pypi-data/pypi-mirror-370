"""
Pytest configuration for test suite
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Check if playwright is available
try:
    import playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip tests based on available dependencies"""
    
    # List of test files that require playwright
    playwright_test_files = [
        'test_playwright_ui.py',
        'test_web_interface.py',
        'test_web_interface_pytest.py',
        'test_web_comprehensive.py'
    ]
    
    skip_playwright = pytest.mark.skip(reason="Playwright not available in this environment")
    
    for item in items:
        # Skip playwright tests if playwright is not available
        if not PLAYWRIGHT_AVAILABLE:
            test_file = Path(item.fspath).name
            if test_file in playwright_test_files:
                item.add_marker(skip_playwright)
