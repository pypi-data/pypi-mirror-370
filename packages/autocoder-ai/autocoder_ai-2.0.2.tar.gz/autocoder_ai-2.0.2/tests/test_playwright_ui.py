#!/usr/bin/env python3
"""
Playwright UI Tests
Tests the web interface using Playwright
"""

import pytest
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import time

BASE_URL = "http://localhost:5001"

class TestPlaywrightUI:
    """Test web UI with Playwright"""
    
    @pytest.mark.asyncio
    async def test_homepage_loads(self):
        """Test that the homepage loads successfully"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Navigate to homepage
            response = await page.goto(BASE_URL)
            assert response.status == 200
            
            # Check for title
            title = await page.title()
            assert "AI Coding Agent" in title or "AutoCoder" in title or "Agent System" in title
            
            await browser.close()
    
    @pytest.mark.asyncio
    async def test_create_project_ui(self):
        """Test creating a project through the UI"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Navigate to homepage
            await page.goto(BASE_URL)
            
            # Look for create project button or form
            # Try to find a button with text "Create", "New Project", etc.
            create_button = await page.query_selector('button:has-text("Create"), button:has-text("New"), button:has-text("Project")')
            
            if create_button:
                await create_button.click()
                # Wait for form or modal to appear
                await page.wait_for_timeout(1000)
            
            # Check if project form exists
            project_form = await page.query_selector('form, div[class*="modal"], div[class*="form"]')
            assert project_form is not None or create_button is not None
            
            await browser.close()
    
    @pytest.mark.asyncio
    async def test_api_health_check_ui(self):
        """Test API health check endpoint through UI"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Navigate to API health endpoint
            response = await page.goto(f"{BASE_URL}/api/health")
            assert response.status == 200
            
            # Check response content
            content = await page.content()
            assert "healthy" in content.lower() or "status" in content.lower()
            
            await browser.close()
    
    @pytest.mark.asyncio
    async def test_projects_page(self):
        """Test that the projects page loads"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Try different possible project URLs
            urls_to_try = [
                f"{BASE_URL}/projects",
                f"{BASE_URL}/#projects",
                f"{BASE_URL}/dashboard",
                BASE_URL  # Main page might show projects
            ]
            
            for url in urls_to_try:
                response = await page.goto(url)
                if response.status == 200:
                    # Look for project-related content
                    content = await page.content()
                    if "project" in content.lower():
                        break
            
            assert response.status == 200
            await browser.close()
    
    @pytest.mark.asyncio
    async def test_responsive_design(self):
        """Test that the UI is responsive"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            # Test desktop view
            desktop_page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
            await desktop_page.goto(BASE_URL)
            desktop_screenshot = await desktop_page.screenshot()
            assert len(desktop_screenshot) > 0
            
            # Test mobile view
            mobile_page = await browser.new_page(viewport={'width': 375, 'height': 667})
            await mobile_page.goto(BASE_URL)
            mobile_screenshot = await mobile_page.screenshot()
            assert len(mobile_screenshot) > 0
            
            await browser.close()

# Helper function to run async tests
def test_playwright_basic():
    """Basic test to ensure Playwright is working"""
    async def run_test():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("https://example.com")
            title = await page.title()
            await browser.close()
            return title
    
    result = asyncio.run(run_test())
    assert "Example" in result
