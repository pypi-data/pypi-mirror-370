# hockey_scraper/src/core/utils.py
# Utility functions for the hockey scraper project
# This file contains functions for data manipulation and fetching JSON data.
# Example functions include:
#
import asyncio
import requests
import json
from typing import Union
import pandas as pd
import polars as pl
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright


def fetch_json(url: str) -> dict:
    """Fetch JSON data from a URL synchronously."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch {url}: Status {response.status_code}")


def fetch_html(url, timeout=10000):
    """Fetch HTML content from a URL using Playwright in headless mode."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=timeout, wait_until="networkidle")
            html = page.content()
        except PlaywrightTimeoutError as e:
            print(f"Timeout while loading {url}: {e}")
            html = None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            html = None
        finally:
            browser.close()
        return html


async def fetch_html_async(url, timeout=10000):
    """Fetch HTML content from a URL using async Playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=timeout, wait_until="networkidle")
            html = await page.content()
        except PlaywrightTimeoutError as e:
            print(f"Timeout while loading {url}: {e}")
            html = None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            html = None
        finally:
            await browser.close()
        return html


def fetch_html_smart(url, timeout=10000):
    """
    Smart HTML fetching that detects async context and handles appropriately.

    - In sync context: Returns HTML content directly
    - In async context: Raises helpful error with instructions

    Args:
        url (str): URL to fetch
        timeout (int): Timeout in milliseconds

    Returns:
        str: HTML content

    Raises:
        RuntimeError: If called in async context (with helpful message)
    """
    try:
        # Check if we're in an async context
        asyncio.get_running_loop()
        raise RuntimeError(
            f"fetch_html_smart() cannot be used in async context (like Jupyter). "
            f"Use 'await fetch_html_async(\"{url}\")' instead."
        )
    except RuntimeError as e:
        if "no running event loop" in str(e):
            # Safe to use sync Playwright
            return fetch_html(url, timeout)
        else:
            # We're in an async context, re-raise with helpful message
            raise e


def run_async_safe(coro):
    """
    Safely run an async coroutine, detecting if we're already in an event loop.

    Args:
        coro: Async coroutine to run

    Returns:
        Result of the coroutine

    Raises:
        RuntimeError: If called from within an async context
    """
    try:
        # Check if we're in an async context
        asyncio.get_running_loop()
        raise RuntimeError(
            "Cannot use run_async_safe() in async context. " "Use 'await' directly instead."
        )
    except RuntimeError as e:
        if "no running event loop" in str(e):
            # Safe to use asyncio.run
            return asyncio.run(coro)
        else:
            # We're in an async context
            raise e
