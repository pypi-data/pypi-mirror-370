# -*- coding: utf-8 -*-

import os
from base64 import b64decode

import robot

from .keywordgroup import KeywordGroup, ignore_on_fail


class _ScreenshotKeywords(KeywordGroup):

    # Public

    def appium_get_element_screenshot(self, locator, timeout=20, filename=None):
        """
        Get a screenshot of element to base64
        If provide filename, saves a screenshot to a PNG image file.

        Parameters:
        -----------
        locator: Element locator
        timeout: timeout in second to find element
        filename : str
            - The full path you wish to save your screenshot to. This
            - should end with a `.png` extension.

        Example:
        --------
        >>> driver.get_screenshot_as_file("/Screenshots/foo.png")
        """

        element = self._invoke_original("appium_get_element", locator, timeout, False)

        if not element:
            self._info(f'Not found {locator}, return None')
            return None

        base64data = element.screenshot_as_base64

        if filename:
            if not str(filename).lower().endswith(".png"):
                self._info(
                    "name used for saved screenshot does not match file type. It should end with a `.png` extension")

            png = b64decode(base64data.encode("ascii"))
            try:
                with open(filename, "wb") as f:
                    f.write(png)
            except OSError:
                self._info(f'Fail to write screenshot file {filename}, return False')
                return False
            finally:
                del png
            return True

        return base64data

    @ignore_on_fail
    def appium_get_screenshot(self):
        return self._invoke_original("appium_capture_page_screenshot", None, False)

    def appium_capture_page_screenshot(self, filename=None, embed=True):
        try:
            return self._invoke_original("capture_page_screenshot", filename, embed)
        except Exception as err:
            self._info(err)
        return None

    def capture_page_screenshot(self, filename=None, embed=True):
        """Takes a screenshot of the current page and embeds it into the log.

        `filename` argument specifies the name of the file to write the
        screenshot into. If no `filename` is given, the screenshot will be
        embedded as Base64 image to the log.html. In this case no file is created in the filesystem.

        `embed` is True: the screenshot will be embedded to the log.html

        Warning: this behavior is new in 1.7. Previously if no filename was given
        the screenshots where stored as separate files named `appium-screenshot-<counter>.png`
        """
        if filename:
            path, link = self._get_screenshot_paths(filename)

            if hasattr(self._current_application(), 'get_screenshot_as_file'):
                self._current_application().get_screenshot_as_file(path)
            else:
                self._current_application().save_screenshot(path)

            # Image is shown on its own row and thus prev row is closed on purpose
            if embed:
                self._html('</td></tr><tr><td colspan="3"><a href="%s">'
                           '<img src="%s" width="800px"></a>' % (link, link))
            return path
        else:
            base64_screenshot = self._current_application().get_screenshot_as_base64()
            if embed:
                self._html('</td></tr><tr><td colspan="3">'
                           '<img src="data:image/png;base64, %s" width="800px">' % base64_screenshot)
            return None

    # Private

    def _get_screenshot_paths(self, filename):
        filename = filename.replace('/', os.sep)
        logdir = self._get_log_dir()
        path = os.path.join(logdir, filename)
        link = robot.utils.get_link_path(path, logdir)
        return path, link
