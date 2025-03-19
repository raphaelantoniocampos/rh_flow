from .browsers.core_browser import CoreBrowser
from .browsers.ahgora_browser import AhgoraBrowser
from .browsers.fiorilli_browser import FiorilliBrowser

class BrowserFactory:
    @staticmethod
    def create_browser(browser_type: str, *args, **kwargs) -> CoreBrowser:
        """
        Factory method to create a browser instance based on the type.

        :param browser_type: Type of browser to create (e.g., "ahgora", "fiorilli").
        :param args: Arguments to pass to the browser constructor.
        :param kwargs: Keyword arguments to pass to the browser constructor.
        :return: An instance of the specified browser.
        """
        if browser_type.lower() == "ahgora":
            return AhgoraBrowser(*args, **kwargs)
        elif browser_type.lower() == "fiorilli":
            return FiorilliBrowser(*args, **kwargs)
        else:
            raise ValueError(f"Unsupported browser type: {browser_type}")
