"""
Pytest-compatible version of Playwright tests for the AI Coding Agent System web interface
"""

import pytest
import pytest_asyncio
from playwright.async_api import async_playwright, expect
import time
import re

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
async def page(browser):
    """Create a new page for each test"""
    context = await browser.new_context()
    page = await context.new_page()
    yield page
    await context.close()


@pytest.mark.asyncio
async def test_homepage_loads(page):
    """Test that the homepage loads successfully"""
    await page.goto(BASE_URL)
    
    # Check page title
    assert await page.title() == "Dashboard - AI Coding Agent System"
    
    # Check main elements are present
    await expect(page.locator("h1")).to_contain_text("AI Coding Agent System")
    await expect(page.locator(".navbar")).to_be_visible()


@pytest.mark.asyncio
async def test_navigation_links(page):
    """Test that all navigation links work"""
    await page.goto(BASE_URL)
    
    # Test Projects link
    await page.click('a[href="/projects"]')
    await page.wait_for_url(f"{BASE_URL}/projects")
    assert "Projects" in await page.title()
    
    # Test New Project link
    await page.click('a[href="/new-project"]')
    await page.wait_for_url(f"{BASE_URL}/new-project")
    assert "New Project" in await page.title()
    
    # Test Dashboard link
    await page.click('a[href="/"]')
    await page.wait_for_url(BASE_URL + "/")
    assert "Dashboard" in await page.title()


@pytest.mark.asyncio
async def test_create_project_modal(page):
    """Test that the create project modal works correctly"""
    await page.goto(BASE_URL)
    
    # Click Create Project button
    await page.click('button[data-action="create-project"]')
    
    # Wait for modal to appear
    await page.wait_for_selector('#createProjectModal', state='visible')
    
    # Check modal elements
    modal = page.locator('#createProjectModal')
    await expect(modal.locator('.modal-title')).to_contain_text("Create New Project")
    
    # Fill in the form
    await page.fill('#projectName', 'Test Project')
    await page.fill('#projectDescription', 'This is a test project description')
    
    # Verify inputs are working
    assert await page.input_value('#projectName') == 'Test Project'
    assert await page.input_value('#projectDescription') == 'This is a test project description'
    
    # Close modal
    await page.click('#createProjectModal button[data-bs-dismiss="modal"]')
    await page.wait_for_selector('#createProjectModal', state='detached')


@pytest.mark.asyncio
async def test_run_task_modal(page):
    """Test that the run task modal works correctly"""
    await page.goto(BASE_URL)
    
    # Click Run Task button
    await page.click('button[data-action="run-task"]')
    
    # Wait for modal to appear
    await page.wait_for_selector('#runTaskModal', state='visible')
    
    # Check modal elements
    modal = page.locator('#runTaskModal')
    await expect(modal.locator('.modal-title')).to_contain_text("Run New Task")
    
    # Fill in the form - use the modal-specific selector
    await modal.locator('#taskDescription').fill('Build a simple web server')
    
    # Verify input is working
    assert await modal.locator('#taskDescription').input_value() == 'Build a simple web server'
    
    # Check checkboxes
    git_checkbox = page.locator('#enableGit')
    test_checkbox = page.locator('#testCode')
    
    await expect(git_checkbox).to_be_checked()
    await expect(test_checkbox).to_be_checked()
    
    # Close modal
    await page.click('#runTaskModal button[data-bs-dismiss="modal"]')
    await page.wait_for_selector('#runTaskModal', state='detached')


@pytest.mark.asyncio
async def test_projects_page(page):
    """Test the projects list page"""
    await page.goto(f"{BASE_URL}/projects")
    
    # Check page elements
    await expect(page.locator("h1")).to_contain_text("All Projects")
    await expect(page.locator("#searchProjects")).to_be_visible()
    
    # Test search functionality
    await page.fill('#searchProjects', 'test')
    
    # Check Create Project button exists
    create_button = page.locator('button[data-action="create-project"]')
    await expect(create_button).to_be_visible()


@pytest.mark.asyncio
async def test_new_project_page(page):
    """Test the new project creation page"""
    await page.goto(f"{BASE_URL}/new-project")
    
    # Check page elements
    await expect(page.locator("h3")).to_contain_text("Create New Project")
    
    # Test form elements
    await page.fill('#projectName', 'New Test Project')
    await page.fill('#projectDescription', 'Description for new test project')
    await page.select_option('#projectType', 'webapp')
    
    # Verify form values
    assert await page.input_value('#projectName') == 'New Test Project'
    assert await page.input_value('#projectDescription') == 'Description for new test project'
    assert await page.input_value('#projectType') == 'webapp'
    
    # Check checkboxes
    await expect(page.locator('#enableGit')).to_be_checked()
    await expect(page.locator('#createReadme')).to_be_checked()


@pytest.mark.asyncio
async def test_api_health_check(page):
    """Test that the API health endpoint is working"""
    response = await page.request.get(f"{API_URL}/health")
    assert response.status == 200
    
    data = await response.json()
    assert data['status'] == 'healthy'


@pytest.mark.asyncio
async def test_api_projects_endpoint(page):
    """Test the projects API endpoint"""
    response = await page.request.get(f"{API_URL}/projects")
    assert response.status == 200
    
    data = await response.json()
    assert 'success' in data
    assert 'projects' in data
    assert isinstance(data['projects'], list)


@pytest.mark.asyncio
async def test_create_project_api(page):
    """Test creating a project via API"""
    project_data = {
        "name": f"Test Project {time.time()}",
        "description": "Created via Playwright test"
    }
    
    response = await page.request.post(
        f"{API_URL}/projects",
        data=project_data
    )
    
    assert response.status == 200
    data = await response.json()
    assert data['success'] == True
    assert 'project' in data
    assert data['project']['name'] == project_data['name']


@pytest.mark.asyncio
async def test_settings_modal(page):
    """Test that the settings modal opens and has correct tabs"""
    await page.goto(BASE_URL)
    
    # Look for settings button in the UI
    # Since it might be in a dropdown or menu, let's trigger it via JavaScript
    await page.evaluate('() => { if(window.app) window.app.showSettingsModal(); }')
    
    # Wait for settings modal
    await page.wait_for_selector('.modal.show', timeout=5000)
    
    # Check tabs are present
    modal = page.locator('.modal.show')
    await expect(modal.locator('#general-tab')).to_be_visible()
    await expect(modal.locator('#providers-tab')).to_be_visible()
    await expect(modal.locator('#agents-tab')).to_be_visible()
    await expect(modal.locator('#templates-tab')).to_be_visible()
    
    # Test tab switching
    await page.click('#providers-tab')
    await expect(page.locator('#providers')).to_have_class(re.compile("active"))
    
    await page.click('#agents-tab')
    await expect(page.locator('#agents')).to_have_class(re.compile("active"))


@pytest.mark.asyncio
async def test_quick_stats_display(page):
    """Test that quick stats are displayed on the dashboard"""
    await page.goto(BASE_URL)
    
    # Check for stats cards
    await expect(page.locator('#totalProjects')).to_be_visible()
    await expect(page.locator('#activeSessions')).to_be_visible()
    await expect(page.locator('#completedTasks')).to_be_visible()


@pytest.mark.asyncio
async def test_responsive_design(page):
    """Test that the interface is responsive"""
    # Test desktop view
    await page.set_viewport_size({"width": 1920, "height": 1080})
    await page.goto(BASE_URL)
    await expect(page.locator('.navbar')).to_be_visible()
    
    # Test tablet view
    await page.set_viewport_size({"width": 768, "height": 1024})
    await page.goto(BASE_URL)
    await expect(page.locator('.navbar')).to_be_visible()
    
    # Test mobile view
    await page.set_viewport_size({"width": 375, "height": 667})
    await page.goto(BASE_URL)
    await expect(page.locator('.navbar-toggler')).to_be_visible()
