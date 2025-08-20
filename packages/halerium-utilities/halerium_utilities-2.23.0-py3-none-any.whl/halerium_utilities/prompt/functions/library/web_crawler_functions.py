import asyncio
import uuid
import logging
from datetime import datetime, timedelta
from pydantic.v1 import BaseModel, Field
from typing import Optional


class Scraper:

    def __init__(self) -> None:
        """
        Initialize a webscraper. This webscraper uses Selenium to load webpages and
        extract the page source. It uses BeautifulSoup to extract all links from
        the page source and prioritizes them using a language model.
        """
        self.driver = None
        self.last_activity_time = datetime.now() - timedelta(days=1)
        self.webdriver_lock = asyncio.Lock()

    async def start_webdriver(self) -> None:
        """
        Start a Selenium WebDriver instance asynchronously.
        """
        self.last_activity_time = datetime.now()
        async with self.webdriver_lock:
            if self.driver is None:
                await asyncio.to_thread(self._start_webdriver_sync)

    def _start_webdriver_sync(self) -> None:
        """
        Synchronous method to start a Selenium WebDriver instance

        Returns:
            webdriver.firefox.webdriver.WebDriver: Selenium WebDriver instance
        """
        from selenium import webdriver

        try:
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)
        except Exception as e:
            logging.error(f"Error starting WebDriver: {e}")
            return None
        else:
            self.driver = driver

    async def stop_webdriver(self):
        """
        Stop a Selenium WebDriver instance asynchronously
        """
        async with self.webdriver_lock:
            if self.driver is not None:
                await asyncio.to_thread(self._stop_webdriver_sync)

    def _stop_webdriver_sync(self):
        """
        Synchronous method to stop a Selenium WebDriver instance
        Args:
            driver (webdriver.firefox.webdriver.WebDriver): Selenium WebDriver instance
        """
        try:
            self.driver.close()
            self.driver.quit()
            self.driver = None
        except Exception as e:
            print(f"Error stopping WebDriver: {e}")
            return False
        else:
            return True

    async def get_source_from_url(self, url: str) -> str:
        """
        Get the page source of a webpage asynchronously.
        """
        return await asyncio.to_thread(self._get_source_from_url_sync, url)

    def _get_source_from_url_sync(self, url: str) -> str:
        """
        Synchronous method to get the page source of a webpage

        Args:
            url (str): URL of the webpage
            driver (webdriver.firefox.webdriver.WebDriver): Selenium WebDriver instance

        Returns:
            str: page source of the webpage
        """
        import time

        # load webpage
        self.driver.get(url)

        # scroll through whole page (catch lazy loading)
        prev_scroll_height = self.driver.execute_script(
            "return document.body.scrollHeight"
        )
        scroll_ops = 0
        while True:
            # scroll to bottom
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            scroll_ops += 1
            time.sleep(0.25)

            # calculate new scroll height and compare with last scroll height.
            curr_scroll_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )

            if curr_scroll_height == prev_scroll_height:
                break

            prev_scroll_height = curr_scroll_height

        return self.driver.current_url, self.driver.page_source

    async def get_links_from_source(self, url: str, source: str) -> list:
        """
        Get all links from a webpage source asynchronously.
        """
        return await asyncio.to_thread(self._get_links_from_source_sync, url, source)

    def _get_links_from_source_sync(self, url: str, source: str) -> list:
        """
        Synchronous method to get all links from a webpage source

        Args:
            url (str): the webpage url
            source (str): webpage source

        Returns:
            list: list of links
        """
        from bs4 import BeautifulSoup, SoupStrainer
        from urllib.parse import urljoin

        page_links = BeautifulSoup(source, "lxml", parse_only=SoupStrainer("a"))
        new_links = []
        for new_link in page_links:
            # filter out links without href attribute
            if new_link.has_attr("href"):
                new_link = urljoin(url, new_link.get("href").split("#")[0])

                # filter out links that are already visited or queued
                if self._is_same_domain(url, new_link):
                    new_links.append(new_link)

        return sorted(set(new_links))

    @staticmethod
    def _is_same_domain(base_url: str, url: str) -> bool:
        """
        Check if two URLs are from the same domain

        Args:
            base_url (str): base URL
            url (str): URL to check

        Returns:
            bool: True if the URLs are from the same domain, False otherwise
        """
        from urllib.parse import urlparse

        base_domain = urlparse(base_url).netloc
        domain = urlparse(url).netloc

        #return base_domain == domain
        return True

    def _tag_is_visible(self, element: 'PageElement') -> bool:
        """
        Filter out non-visible text elements

        Args:
            element (PageElement):  element to check for visibility

        Returns:
            bool: True if the element is visible, False otherwise
        """
        from bs4.element import Comment

        if element.parent.name in [
            "style",
            "script",
            "head",
            "title",
            "meta",
            "[document]",
        ]:
            return False

        if isinstance(element, Comment):
            return False

        return True

    async def get_text_from_source(self, source: str) -> str:
        """
        Get the text content from an HTML string asynchronously.
        """
        return await asyncio.to_thread(self._get_text_from_source_sync, source)

    def _get_text_from_source_sync(self, source: str) -> str:
        """
        Synchronous method to get the text content from an HTML string

        Args:
            source (str): the page html

        Returns:
            str: the website text
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(source, "lxml")
        text = soup.findAll(text=True)

        # remove non-visible text
        text = filter(self._tag_is_visible, text)

        # trim whitespaces and remove empty strings
        text = [t.strip() for t in text if t.strip()]

        # filter out short sentences and cookie messages
        n = 4
        text = [
            t
            for t in text
            if not len(t.split()) < n
            and not any(
                substring in t
                for substring in [
                    "Einwilligungsoptionen",
                    "Cookie",
                    "Privatsphäre",
                ]
            )
        ]

        return text

    async def scrape_site(self, url):
        """
        Scrape the site for text and links asynchronously.
        """
        from urllib.parse import urljoin, urlparse

        self.last_activity_time = datetime.now()

        url = urljoin(url, urlparse(url).path)
        loaded_url, source = await self.get_source_from_url(url)
        text = await self.get_text_from_source(source)
        links = await self.get_links_from_source(url, source)

        return {"url": loaded_url, "text": text, "links": links}

    async def delayed_shutdown(self, wait=60, n_retry=1):
        await asyncio.sleep(wait)
        if datetime.now() - self.last_activity_time >= timedelta(seconds=wait):
            await self.stop_webdriver()
        if (self.driver is not None) and n_retry > 0:
            asyncio.create_task(self.delayed_shutdown(wait=wait, n_retry=n_retry - 1))


scraper_pool = []


def set_up():
    import psutil

    global scraper_pool
    n_scrapers = (
            (
                    round(psutil.virtual_memory().total / (1024 ** 3))  # runner host RAM in GB
                    - 1  # take away 1 GB for host
            )
            * 1  # sessions per GB RAM
    )
    scraper_pool = [{"scraper": Scraper(),
                     "session": None} for _ in range(n_scrapers)]


def get_scraper(session):
    if not scraper_pool:
        set_up()

    for scr in scraper_pool:
        if scr["session"] is None:
            scr["session"] = session
            return scr["scraper"]
    return None


def free_scraper(session):
    for scr in scraper_pool:
        if scr["session"] == session:
            scr["session"] = None


class Arguments(BaseModel):
    url: str = Field(description="The URL of the page.")
    return_text: Optional[bool] = Field(description="If true return the webpage as text. The default is True.")
    return_links: Optional[bool] = Field(
        description="If true return internal links found on the page. The default is False.")


async def load_website(data: Arguments):
    url = data.get("url")
    return_text = data.get("return_text", True)
    return_links = data.get("return_links", False)

    session = str(uuid.uuid4())
    scraper = get_scraper(session)
    while scraper is None:
        scraper = get_scraper(session)
        await asyncio.sleep(2)

    try:
        # Start the WebDriver
        await scraper.start_webdriver()

        # Scrape the site
        result = await scraper.scrape_site(url)

        # Filter results based on the provided options
        if not return_text:
            del result["text"]
        if not return_links:
            del result["links"]

        return result
    finally:
        free_scraper(session)
        # Delay shutdown of WebDriver
        asyncio.create_task(scraper.delayed_shutdown())
