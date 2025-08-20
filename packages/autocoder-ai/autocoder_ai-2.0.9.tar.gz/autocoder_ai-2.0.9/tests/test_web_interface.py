"""
Comprehensive Playwright tests for the AI Coding Agent System web interface
"""

import pytest
import pytest_asyncio
import asyncio
from playwright.async_api import async_playwright, expect
import json
import time
import re

# Base URL for the application
BASE_URL = "http://localhost:5001"
API_URL = f"{BASE_URL}/api"

class TestWebInterface:
    """Test suite for the web interface"""
    
    @pytest_asyncio.fixture(scope="class")
    async def browser_context(self):
        """Create a browser context for testing"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            yield context
            await browser.close()
    
    @pytest.mark.asyncio
    async def test_homepage_loads(self, browser_context):
        """Test that the homepage loads successfully"""
        page = await browser_context.new_page()
        await page.goto(BASE_URL)
        
        # Check page title
        assert await page.title() == "Dashboard - AI Coding Agent System"
        
        # Check main elements are present
        await expect(page.locator("h1")).to_contain_text("AI Coding Agent System")
        await expect(page.locator(".navbar")).to_be_visible()
        
        await page.close()
    
    @pytest.mark.asyncio
    async def test_navigation_links(self, browser_context):
        """Test that all navigation links work"""
        page = await browser_context.new_page()
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
        
        await page.close()
    
    @pytest.mark.asyncio
    async def test_create_project_modal(self, browser_context):
        """Test that the create project modal works correctly"""
        page = await browser_context.new_page()
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
        
        await page.close()
    
    @pytest.mark.asyncio
    async def test_run_task_modal(self, browser_context):
        """Test that the run task modal works correctly"""
        page = await browser_context.new_page()
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
        
        await page.close()
    
    @pytest.mark.asyncio
    async def test_projects_page(self, browser_context):
        """Test the projects list page"""
        page = await browser_context.new_page()
        await page.goto(f"{BASE_URL}/projects")
        
        # Check page elements
        await expect(page.locator("h1")).to_contain_text("All Projects")
        await expect(page.locator("#searchProjects")).to_be_visible()
        
        # Test search functionality
        await page.fill('#searchProjects', 'test')
        
        # Check Create Project button exists
        create_button = page.locator('button[data-action="create-project"]')
        await expect(create_button).to_be_visible()
        
        await page.close()
    
    @pytest.mark.asyncio
    async def test_new_project_page(self, browser_context):
        """Test the new project creation page"""
        page = await browser_context.new_page()
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
        
        await page.close()
    
    @pytest.mark.asyncio
    async def test_api_health_check(self, browser_context):
        """Test that the API health endpoint is working"""
        page = await browser_context.new_page()
        
        response = await page.request.get(f"{API_URL}/health")
        assert response.status == 200
        
        data = await response.json()
        assert data['status'] == 'healthy'
        
        await page.close()
    
    @pytest.mark.asyncio
    async def test_api_projects_endpoint(self, browser_context):
        """Test the projects API endpoint"""
        page = await browser_context.new_page()
        
        response = await page.request.get(f"{API_URL}/projects")
        assert response.status == 200
        
        data = await response.json()
        assert 'success' in data
        assert 'projects' in data
        assert isinstance(data['projects'], list)
        
        await page.close()
    
    @pytest.mark.asyncio
    async def test_create_project_api(self, browser_context):
        """Test creating a project via API"""
        page = await browser_context.new_page()
        
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
        
        await page.close()
    
    @pytest.mark.asyncio
    async def test_settings_modal(self, browser_context):
        """Test that the settings modal opens and has correct tabs"""
        page = await browser_context.new_page()
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
        
        await page.close()
    
    @pytest.mark.asyncio
    async def test_quick_stats_display(self, browser_context):
        """Test that quick stats are displayed on the dashboard"""
        page = await browser_context.new_page()
        await page.goto(BASE_URL)
        
        # Check for stats cards
        await expect(page.locator('#totalProjects')).to_be_visible()
        await expect(page.locator('#activeSessions')).to_be_visible()
        await expect(page.locator('#completedTasks')).to_be_visible()
        
        await page.close()
    
    @pytest.mark.asyncio
    async def test_responsive_design(self, browser_context):
        """Test that the interface is responsive"""
        page = await browser_context.new_page()
        
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
        
        await page.close()


async def run_tests():
    """Run all tests"""
    print("Starting Playwright tests for AI Coding Agent System...")
    print(f"Testing URL: {BASE_URL}")
    
    test_instance = TestWebInterface()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        tests = [
            ("Homepage loads", test_instance.test_homepage_loads),
            ("Navigation links", test_instance.test_navigation_links),
            ("Create project modal", test_instance.test_create_project_modal),
            ("Run task modal", test_instance.test_run_task_modal),
            ("Projects page", test_instance.test_projects_page),
            ("New project page", test_instance.test_new_project_page),
            ("API health check", test_instance.test_api_health_check),
            ("API projects endpoint", test_instance.test_api_projects_endpoint),
            ("Create project API", test_instance.test_create_project_api),
            ("Settings modal", test_instance.test_settings_modal),
            ("Quick stats display", test_instance.test_quick_stats_display),
            ("Responsive design", test_instance.test_responsive_design),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                print(f"Running: {test_name}...", end=" ")
                await test_func(context)
                print("✅ PASSED")
                passed += 1
            except Exception as e:
                print(f"❌ FAILED: {str(e)}")
                failed += 1
        
        await browser.close()
        
        print("\n" + "="*50)
        print(f"Test Results: {passed} passed, {failed} failed")
        print("="*50)
        
        return failed == 0


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(run_tests())
    exit(0 if success else 1)
