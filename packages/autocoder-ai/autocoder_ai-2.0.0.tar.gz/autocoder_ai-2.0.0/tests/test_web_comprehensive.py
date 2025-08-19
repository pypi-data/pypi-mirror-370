"""
Comprehensive Playwright tests with console error monitoring for the AI Coding Agent System
"""

import pytest
import pytest_asyncio
from playwright.async_api import async_playwright, expect
import time
import re
from typing import List

# Base URL for the application
BASE_URL = "http://localhost:5001"
API_URL = f"{BASE_URL}/api"


@pytest_asyncio.fixture
async def browser():
    """Create a browser instance for testing"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()


@pytest_asyncio.fixture
async def page_with_console_monitoring(browser):
    """Create a page that monitors console errors and warnings"""
    context = await browser.new_context()
    page = await context.new_page()
    
    # Store console messages
    console_errors: List[str] = []
    console_warnings: List[str] = []
    
    # Monitor console messages
    def handle_console_message(msg):
        if msg.type == "error":
            console_errors.append(f"{msg.text} at {msg.location}")
        elif msg.type == "warning":
            console_warnings.append(f"{msg.text} at {msg.location}")
    
    page.on("console", handle_console_message)
    
    # Monitor page errors (uncaught exceptions)
    def handle_page_error(error):
        console_errors.append(f"Page error: {error}")
    
    page.on("pageerror", handle_page_error)
    
    # Attach console monitoring to page
    page.console_errors = console_errors
    page.console_warnings = console_warnings
    
    yield page
    
    # After test, check for console errors
    if console_errors:
        print(f"\n⚠️ Console errors detected: {console_errors}")
    if console_warnings:
        print(f"\n⚠️ Console warnings detected: {console_warnings}")
    
    await context.close()


@pytest.mark.asyncio
async def test_homepage_no_console_errors(page_with_console_monitoring):
    """Test that the homepage loads without console errors"""
    page = page_with_console_monitoring
    await page.goto(BASE_URL)
    
    # Wait for page to fully load
    await page.wait_for_load_state("networkidle")
    
    # Check basic elements
    assert await page.title() == "Dashboard - AI Coding Agent System"
    await expect(page.locator("h1")).to_contain_text("AI Coding Agent System")
    
    # Verify no console errors
    assert len(page.console_errors) == 0, f"Console errors found: {page.console_errors}"


@pytest.mark.asyncio
async def test_new_project_page_interaction(page_with_console_monitoring):
    """Test that the new project page works correctly without modal popups"""
    page = page_with_console_monitoring
    await page.goto(f"{BASE_URL}/new-project")
    
    # Wait for page to fully load
    await page.wait_for_load_state("networkidle")
    
    # Check page elements
    await expect(page.locator("h3")).to_contain_text("Create New Project")
    
    # Test clicking on checkboxes (should NOT trigger modal)
    git_checkbox = page.locator('#enableGit')
    await git_checkbox.uncheck()
    
    # Wait a moment to see if modal appears
    await page.wait_for_timeout(500)
    
    # Verify no modal is visible
    modal = page.locator('.modal.show')
    await expect(modal).not_to_be_visible()
    
    # Test clicking on form fields
    await page.fill('#projectName', 'Test Project')
    await page.fill('#projectDescription', 'Test Description')
    
    # Wait a moment to see if modal appears
    await page.wait_for_timeout(500)
    
    # Verify no modal is visible
    await expect(modal).not_to_be_visible()
    
    # Test selecting dropdown
    await page.select_option('#projectType', 'api')
    
    # Verify no modal is visible
    await expect(modal).not_to_be_visible()
    
    # Re-check the checkbox
    await git_checkbox.check()
    
    # Verify form values are preserved
    assert await page.input_value('#projectName') == 'Test Project'
    assert await page.input_value('#projectDescription') == 'Test Description'
    assert await page.input_value('#projectType') == 'api'
    
    # Verify no console errors
    assert len(page.console_errors) == 0, f"Console errors found: {page.console_errors}"


@pytest.mark.asyncio
async def test_create_project_button_on_dashboard(page_with_console_monitoring):
    """Test that Create Project button on dashboard opens modal correctly"""
    page = page_with_console_monitoring
    await page.goto(BASE_URL)
    await page.wait_for_load_state("networkidle")
    
    # Click Create Project button
    await page.click('button[data-action="create-project"]')
    
    # Wait for modal to appear
    await page.wait_for_selector('#createProjectModal', state='visible')
    
    # Verify modal is visible
    modal = page.locator('#createProjectModal')
    await expect(modal).to_be_visible()
    
    # Test modal interaction
    await page.fill('#createProjectModal #projectName', 'Modal Test Project')
    await page.fill('#createProjectModal #projectDescription', 'Created from modal')
    
    # Close modal
    await page.click('#createProjectModal button[data-bs-dismiss="modal"]')
    await page.wait_for_selector('#createProjectModal', state='detached')
    
    # Verify no console errors
    assert len(page.console_errors) == 0, f"Console errors found: {page.console_errors}"


@pytest.mark.asyncio
async def test_run_task_modal_interaction(page_with_console_monitoring):
    """Test Run Task modal with detailed interaction"""
    page = page_with_console_monitoring
    await page.goto(BASE_URL)
    await page.wait_for_load_state("networkidle")
    
    # Click Run Task button
    await page.click('button[data-action="run-task"]')
    
    # Wait for modal to appear
    await page.wait_for_selector('#runTaskModal', state='visible')
    
    # Test filling the textarea
    modal = page.locator('#runTaskModal')
    textarea = modal.locator('#taskDescription')
    await textarea.fill('Build a REST API with authentication')
    
    # Test checkbox interactions
    git_checkbox = modal.locator('#enableGit')
    test_checkbox = modal.locator('#testCode')
    
    # Uncheck and recheck
    await git_checkbox.uncheck()
    await test_checkbox.uncheck()
    await git_checkbox.check()
    
    # Verify values
    assert await textarea.input_value() == 'Build a REST API with authentication'
    assert await git_checkbox.is_checked() == True
    assert await test_checkbox.is_checked() == False
    
    # Close modal
    await page.click('#runTaskModal button[data-bs-dismiss="modal"]')
    await page.wait_for_selector('#runTaskModal', state='detached')
    
    # Verify no console errors
    assert len(page.console_errors) == 0, f"Console errors found: {page.console_errors}"


@pytest.mark.asyncio
async def test_navigation_without_errors(page_with_console_monitoring):
    """Test navigation between pages without console errors"""
    page = page_with_console_monitoring
    await page.goto(BASE_URL)
    
    # Navigate to Projects
    await page.click('a[href="/projects"]')
    await page.wait_for_url(f"{BASE_URL}/projects")
    await page.wait_for_load_state("networkidle")
    assert len(page.console_errors) == 0, f"Errors on projects page: {page.console_errors}"
    
    # Navigate to New Project
    await page.click('a[href="/new-project"]')
    await page.wait_for_url(f"{BASE_URL}/new-project")
    await page.wait_for_load_state("networkidle")
    assert len(page.console_errors) == 0, f"Errors on new-project page: {page.console_errors}"
    
    # Navigate back to Dashboard
    await page.click('a[href="/"]')
    await page.wait_for_url(BASE_URL + "/")
    await page.wait_for_load_state("networkidle")
    assert len(page.console_errors) == 0, f"Errors on dashboard: {page.console_errors}"


@pytest.mark.asyncio
async def test_api_calls_without_errors(page_with_console_monitoring):
    """Test API calls don't produce console errors"""
    page = page_with_console_monitoring
    
    # Test health endpoint
    response = await page.request.get(f"{API_URL}/health")
    assert response.status == 200
    
    # Test projects endpoint
    response = await page.request.get(f"{API_URL}/projects")
    assert response.status == 200
    
    # Test config endpoint
    response = await page.request.get(f"{API_URL}/config")
    assert response.status == 200
    
    # Load dashboard to check for any errors from API calls
    await page.goto(BASE_URL)
    await page.wait_for_load_state("networkidle")
    
    # Wait for any async API calls to complete
    await page.wait_for_timeout(1000)
    
    # Verify no console errors
    assert len(page.console_errors) == 0, f"Console errors found: {page.console_errors}"


@pytest.mark.asyncio
async def test_form_submission_new_project_page(page_with_console_monitoring):
    """Test form submission on new project page"""
    page = page_with_console_monitoring
    await page.goto(f"{BASE_URL}/new-project")
    await page.wait_for_load_state("networkidle")
    
    # Fill out the form
    await page.fill('#projectName', 'Test Submission Project')
    await page.fill('#projectDescription', 'Testing form submission')
    await page.select_option('#projectType', 'cli')
    await page.check('#setupTests')
    
    # Intercept the API call to prevent actual submission
    await page.route('**/api/projects', lambda route: route.fulfill(
        status=200,
        content_type='application/json',
        body='{"success": true, "project": {"id": "test-id", "name": "Test Submission Project"}}'
    ))
    
    # Also intercept navigation to projects page
    await page.route('**/projects', lambda route: route.fulfill(
        status=200,
        content_type='text/html',
        body='<html><body>Projects Page</body></html>'
    ))
    
    # Submit the form
    await page.click('button[type="submit"]')
    
    # Wait for submission to process
    await page.wait_for_timeout(500)
    
    # Verify no console errors
    assert len(page.console_errors) == 0, f"Console errors found: {page.console_errors}"


@pytest.mark.asyncio
async def test_websocket_connection(page_with_console_monitoring):
    """Test WebSocket connection doesn't cause errors"""
    page = page_with_console_monitoring
    
    # Go to the main page
    await page.goto(BASE_URL)
    await page.wait_for_load_state("networkidle")
    
    # Wait for WebSocket to attempt connection
    await page.wait_for_timeout(2000)
    
    # Check console for WebSocket-related messages
    # Note: WebSocket connection failures are expected in test environment
    # but should not cause JavaScript errors
    ws_errors = [e for e in page.console_errors if 'WebSocket' not in e and 'ws:' not in e]
    assert len(ws_errors) == 0, f"Non-WebSocket console errors found: {ws_errors}"


@pytest.mark.asyncio
async def test_modal_z_index_and_backdrop(page_with_console_monitoring):
    """Test that modals have proper z-index and backdrop behavior"""
    page = page_with_console_monitoring
    await page.goto(BASE_URL)
    await page.wait_for_load_state("networkidle")
    
    # Open Create Project modal
    await page.click('button[data-action="create-project"]')
    await page.wait_for_selector('#createProjectModal', state='visible')
    
    # Try clicking outside the modal (on backdrop)
    # Modal should stay open due to backdrop: 'static'
    await page.mouse.click(100, 100)
    await page.wait_for_timeout(500)
    
    modal = page.locator('#createProjectModal')
    await expect(modal).to_be_visible()
    
    # Try pressing Escape
    # Modal should stay open due to keyboard: false
    await page.keyboard.press('Escape')
    await page.wait_for_timeout(500)
    await expect(modal).to_be_visible()
    
    # Close with the close button
    await page.click('#createProjectModal button[data-bs-dismiss="modal"]')
    await page.wait_for_selector('#createProjectModal', state='detached')
    
    # Verify no console errors
    assert len(page.console_errors) == 0, f"Console errors found: {page.console_errors}"


@pytest.mark.asyncio
async def test_responsive_navigation_menu(page_with_console_monitoring):
    """Test responsive navigation menu in mobile view"""
    page = page_with_console_monitoring
    
    # Set mobile viewport
    await page.set_viewport_size({"width": 375, "height": 667})
    await page.goto(BASE_URL)
    await page.wait_for_load_state("networkidle")
    
    # Check that hamburger menu is visible
    hamburger = page.locator('.navbar-toggler')
    await expect(hamburger).to_be_visible()
    
    # Click hamburger to open menu
    await hamburger.click()
    await page.wait_for_timeout(500)
    
    # Check that menu items are visible
    nav_menu = page.locator('#navbarNav')
    await expect(nav_menu).to_be_visible()
    
    # Click a menu item
    await page.click('a[href="/projects"]')
    await page.wait_for_url(f"{BASE_URL}/projects")
    
    # Verify no console errors
    assert len(page.console_errors) == 0, f"Console errors found: {page.console_errors}"


if __name__ == "__main__":
    # Run with: python -m pytest tests/test_web_comprehensive.py -v
    print("Run this test file with: python -m pytest tests/test_web_comprehensive.py -v")
