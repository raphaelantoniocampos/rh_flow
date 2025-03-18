from abc import ABC, abstractmethod

# import os
# import threading
import time
# from datetime import date, datetime
# from pathlib import Path

# from config import Config
from rich import print
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    MoveTargetOutOfBoundsException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BaseBrowser(ABC):
    MAX_TRIES = 30
    DELAY = 0.5
    IGNORED_EXCEPTIONS = (
        ElementClickInterceptedException,
        ElementNotInteractableException,
        MoveTargetOutOfBoundsException,
        NoSuchElementException,
        StaleElementReferenceException,
    )

    def __init__(self, url):
        self.driver = self._get_web_driver()
        self.driver.get(url)


    @abstractmethod
    def download_data(self):
        pass

    @abstractmethod
    def _login(self):
        pass

    @abstractmethod
    def _enter_username(self):
        pass

    @abstractmethod
    def _enter_password(self):
        pass

    def _get_web_driver(self, headless_mode: bool = True) -> webdriver.Firefox:
        options = webdriver.FirefoxOptions()
        if headless_mode:
            options.add_argument("-headless")
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", str(self.downloads_dir_path))

        driver = webdriver.Firefox(options=options)
        driver.implicitly_wait(self.DELAY)

        return driver

    def close_driver(self):
        self.driver.quit()

    def click_element(
        self,
        selector,
        selector_type=By.XPATH,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
        max_tries=MAX_TRIES,
    ):
        self._retry_func(
            lambda: self._click_element_helper(
                self.driver, selector, selector_type, delay, ignored_exceptions
            ),
            max_tries,
        )

    def _click_element_helper(
        self,
        selector,
        selector_type=By.XPATH,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
    ):
        WebDriverWait(self.driver, delay, ignored_exceptions=ignored_exceptions).until(
            EC.presence_of_element_located((selector_type, selector))
        ).click()

    def send_keys(
        self,
        selector,
        keys,
        selector_type=By.XPATH,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
        max_tries=MAX_TRIES,
    ):
        self._retry_func(
            lambda: self._send_keys_helper(
                self.driver, selector, keys, selector_type, delay, ignored_exceptions
            ),
            max_tries,
        )

    def _send_keys_helper(
        self,
        selector,
        keys,
        selector_type=By.XPATH,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
    ):
        WebDriverWait(self.driver, delay, ignored_exceptions=ignored_exceptions).until(
            EC.presence_of_element_located((selector_type, selector))
        ).send_keys(keys)

    def right_click_element(
        self,
        selector,
        selector_type=By.XPATH,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
        max_tries=MAX_TRIES,
    ):
        self._retry_func(
            lambda: self._right_click_element_helper(
                self.driver, selector, selector_type, delay, ignored_exceptions
            ),
            max_tries,
        )

    def _right_click_element_helper(
        self,
        selector,
        selector_type=By.XPATH,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
    ):
        ActionChains(self.driver).context_click(
            WebDriverWait(
                self.driver, delay, ignored_exceptions=ignored_exceptions
            ).until(EC.presence_of_element_located((selector_type, selector)))
        ).perform()

    def select_and_send_keys(
        self,
        selector,
        keys,
        selector_type=By.XPATH,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
        max_tries=MAX_TRIES,
    ):
        if isinstance(keys, list):
            for i, key in enumerate(keys):
                element_selector = f"({selector})[{i + 1}]"
                self._retry_func(
                    lambda: self._select_and_send_keys_helper(
                        self.driver,
                        element_selector,
                        key,
                        selector_type,
                        delay,
                        ignored_exceptions,
                    ),
                    max_tries,
                )
        else:
            self._retry_func(
                lambda: self._select_and_send_keys_helper(
                    self.driver,
                    selector,
                    keys,
                    selector_type,
                    delay,
                    ignored_exceptions,
                ),
                max_tries,
            )

    def _select_and_send_keys_helper(
        self,
        selector,
        keys,
        selector_type=By.XPATH,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
    ):
        ActionChains(self.driver).context_click(
            WebDriverWait(
                self.driver, delay, ignored_exceptions=ignored_exceptions
            ).until(EC.presence_of_element_located((selector_type, selector)))
        ).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(
            keys
        ).perform()

    def wait_desappear(
        self,
        selector,
        selector_type=By.XPATH,
        delay=30,
        ignored_exceptions=IGNORED_EXCEPTIONS,
        max_tries=10,
    ):
        return self._retry_func(
            lambda: self._wait_desappear_helper(
                self.driver, selector, selector_type, delay, ignored_exceptions
            ),
            max_tries,
        )

    def _wait_desappear_helper(
        self,
        selector,
        selector_type=By.XPATH,
        delay=30,
        ignored_exceptions=IGNORED_EXCEPTIONS,
    ):
        WebDriverWait(self.driver, delay).until(
            EC.invisibility_of_element_located((selector_type, selector))
        )

    def move_to_element(
        self,
        selector,
        selector_type=By.XPATH,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
        max_tries=MAX_TRIES,
    ):
        self._retry_func(
            lambda: self._move_to_element_helper(
                self.driver, selector, selector_type, delay, ignored_exceptions
            ),
            max_tries,
        )

    def _move_to_element_helper(
        self,
        selector,
        selector_type=By.XPATH,
        delay=DELAY,
        ignored_exceptions=IGNORED_EXCEPTIONS,
    ):
        ActionChains(self.driver).move_to_element(
            WebDriverWait(
                self.driver, delay, ignored_exceptions=ignored_exceptions
            ).until(EC.presence_of_element_located((selector_type, selector)))
        ).perform()

    def _retry_func(self, func, max_tries=MAX_TRIES):
        for i in range(max_tries):
            try:
                time.sleep(self.DELAY)
                return func()
            except Exception as e:
                time.sleep(self.DELAY)
                if i >= max_tries - 1:
                    print(e)
                    return
                    # raise e
