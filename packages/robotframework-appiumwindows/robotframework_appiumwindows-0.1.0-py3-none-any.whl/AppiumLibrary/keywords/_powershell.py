# -*- coding: utf-8 -*-

import base64
import math
import os
from pathlib import Path

from appium.webdriver.mobilecommand import MobileCommand as Command
from robot.libraries.BuiltIn import BuiltIn
from selenium.common import InvalidArgumentException

from AppiumLibrary import utils
from AppiumLibrary.locators import ElementFinder
from .keywordgroup import KeywordGroup

SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts"))


class _PowershellKeywords(KeywordGroup):
    def __init__(self):
        self._element_finder = ElementFinder()
        self._bi = BuiltIn()

    # Public, element lookups
    # Powershell command, need appium server allow shell, eg: appium --relaxed-security

    def appium_ps_click(
            self,
            locator=None,
            x=0,
            y=0,
            button='left',
            **kwargs
    ):
        """
        Click using PowerShell-level mouse simulation.

        Supports:
          - Absolute coordinates or element-based location via locator
          - Optional offsets (absolute or 'center')
          - Custom mouse button

        kwargs:
            - offset: sets both x/y offset globally (overrides individual)
            - x_offset / y_offset

        @param locator:
        @param x:
        @param y:
        @param button:
            'left'           - single left click
            'right'          - single right click
            'middle'         - single middle click
            'double'         - double left click
            'triple'         - triple left click
            'right-double'   - double right click

        """
        self._info(f"Appium Ps Click")

        if locator:
            rect = self.get_element_rect(locator)
            x, y = self._parse_location(rect, kwargs, 'x_offset', 'y_offset')
            root = self._current_application().get_window_rect()
            self._info(f"[DEBUG] App window rect: {root}")
            x, y = x + root['x'], y + root['y']

        self._info(f"[CLICK] {button.upper()} Button: ({x},{y}))")

        ps_command = self._generate_click_command(x, y, button)
        self._info(f"ps_command: \n{ps_command}")

        self.appium_execute_powershell_command(ps_command)

    def appium_ps_sendkeys(self, text: str):
        """
        SendKeys can found at: https://learn.microsoft.com/en-us/dotnet/api/system.windows.forms.sendkeys?view=windowsdesktop-10.0

        To specify that any combination of SHIFT, CTRL, and ALT should be held down while several other keys are pressed,
        enclose the code for those keys in parentheses. For example, to specify to hold down SHIFT while E and C are pressed,
        use "+(EC)". To specify to hold down SHIFT while E is pressed, followed by C without SHIFT, use "+EC".

        To specify repeating keys, use the form {key number}. You must put a space between key and number.
        For example, {LEFT 42} means press the LEFT ARROW key 42 times; {h 10} means press H 10 times.

        @param text: text to sendkeys
        eg1: text = 123qwe{TAB}iop{ENTER}+a~ABC~
        eg2: text = "{+}" ({%}) ({^})
        eg3: text = This is test{LEFT}{BACKSPACE}x
        eg4: text = 123qwe{BACKSPACE 3}{TAB}{ENTER}
        @return:
        """
        self._info(f"Appium Ps Sendkeys: {text}")
        text = text.replace('"', '""')

        ps_command = (
            f'Add-Type -AssemblyName System.Windows.Forms;'
            f'[System.Windows.Forms.SendKeys]::SendWait("{text}")'
        )
        self._info(f'command: {ps_command}')

        self.appium_execute_powershell_command(ps_command)

    def appium_ps_drag_and_drop(
            self,
            start_locator=None,
            end_locator=None,
            x_start=0,
            y_start=0,
            x_end=0,
            y_end=0,
            button='left',
            **kwargs
    ):
        """
        Drag and drop using PowerShell-level mouse simulation.

        Supports:
          - Absolute coordinates or element-based location via start_locator/end_locator
          - Optional offsets (absolute or 'center')
          - Custom mouse button (left/right/mid)
          - Drag duration (default 0.5 seconds)

        kwargs:
            - offset: sets both x/y offset globally (overrides individual)
            - x_start_offset / y_start_offset
            - x_end_offset / y_end_offset
            - duration_sec: total drag time in seconds (default 0.5)
        """
        self._info(f"Appium Ps Drag And Drop")
        # Get actual coordinates from locators (if any)
        if start_locator:
            start_rect = self.get_element_rect(start_locator)
            x_start, y_start = self._parse_location(start_rect, kwargs, 'x_start_offset', 'y_start_offset')

        if end_locator:
            end_rect = self.get_element_rect(end_locator)
            x_end, y_end = self._parse_location(end_rect, kwargs, 'x_end_offset', 'y_end_offset')

        # Normalize against window position
        root = self._current_application().get_window_rect()
        self._info(f"[DEBUG] App window rect: {root}")

        x_start, y_start = x_start + root['x'], y_start + root['y']
        x_end, y_end = x_end + root['x'], y_end + root['y']

        self._info(f"[DRAG] {button.upper()} Button: From ({x_start},{y_start}) → ({x_end},{y_end})")

        # Get drag duration
        duration_sec = float(kwargs.get('duration_sec', 0.5))
        ps_command = self._generate_drag_command(x_start, y_start, x_end, y_end, button, duration_sec)
        self._info(f"ps_command: \n{ps_command}")

        # Execute PowerShell command
        self.appium_execute_powershell_command(ps_command)

    def appium_execute_powershell_command(self, command, handle_exception=False):
        """
        Executes a PowerShell command using Appium's execute_script method.

        Note:
            PowerShell command execution must be allowed on the Appium server.
            For this, Appium must be started with the `--relaxed-security` flag:
                appium --relaxed-security

        Args:
            command (str): The PowerShell command to be executed.
            handle_exception (bool): If True, return the exception object on error. Otherwise, return None.

        Returns:
            str | dict | Exception: The result of the execution or the exception object.

        Raises:
            Exception: If handle_exception is False and an error occurs.
        """
        try:
            driver = self._current_application()
            result = driver.execute_script("powerShell", {"command": command})
            return result
        except Exception as exc:
            if handle_exception:
                return exc
            raise

    def appium_execute_powershell_script(self, ps_script=None, file_path=None, handle_exception=False):
        """
        Executes a PowerShell script using Appium's execute_script method.

        Note:
            PowerShell command execution must be allowed on the Appium server.
            For this, Appium must be started with the `--relaxed-security` flag:
                appium --relaxed-security

        Args:
            ps_script (str): The full PowerShell script to be executed.
            file_path (str): The file ps1 to be executed.
            handle_exception (bool): If True, return the exception object on failure. If False, return None on failure.

        Returns:
            str | dict | Exception: The result of the script execution or the exception object.

        Raises:
            Exception: If handle_exception is False and an error occurs.
        """
        try:
            if file_path:
                self._info(f'file_path: {file_path}')
                ps_script = utils.read_file(file_path)
            self._info(f"ps_script: \n{ps_script}")
            driver = self._current_application()
            result = driver.execute_script("powerShell", {"script": ps_script})
            return result
        except Exception as exc:
            if handle_exception:
                return exc
            raise

    def appium_pull_file(self, path: str, save_path: str = None) -> str:
        """Retrieves the file at `path`.

        Powershell command must be allowed. eg: appium --relaxed-security

        Args:
            path: the path to the file on the device, eg: c:/users/user1/desktop/screenshot_file.png
            save_path: path to save, eg: /Users/user1/desktop/screenshot.png

        Returns:
            The file's contents encoded as Base64.
        """

        # base64data = self._current_application().pull_file(path)
        base64data = self._current_application().execute(Command.PULL_FILE, {'path': path})['value']

        if save_path:
            with open(save_path, "wb") as file:
                file.write(base64.b64decode(base64data))

        return base64data

    def appium_pull_folder(self, path: str, save_path_as_zip: str = '') -> str:
        """Retrieves a folder at `path`.

        Powershell command must be allowed. eg: appium --relaxed-security

        Args:
            path: the path to the folder on the device. eg: c:/users/user1/desktop/folder1
            save_path_as_zip: zip file. eg: /Users/user1/desktop/file.zip

        Returns:
            The folder's contents zipped and encoded as Base64.
        """
        # base64data = self._current_application().pull_folder(path)
        base64data = self._current_application().execute(Command.PULL_FOLDER, {'path': path})['value']

        if save_path_as_zip:
            with open(save_path_as_zip, "wb") as file:
                file.write(base64.b64decode(base64data))

        return base64data

    def appium_push_file(self, destination_path: str, source_path: str = None, base64data: str = None):
        """Puts the data from the file at `source_path`, encoded as Base64, in the file specified as `path`.

        Specify either `base64data` or `source_path`, if both specified default to `source_path`

        Powershell command must be allowed. eg: appium --relaxed-security

        Args:
            destination_path: the location on the device/simulator where the local file contents should be saved.
            eg: c:/users/user1/desktop/screenshot_file.png
            base64data: file contents, encoded as Base64, to be written
            to the file on the device/simulator. Eg: iVBORw0KGgoAAAANSUh...
            source_path: local file path for the file to be loaded on device. Eg: /Users/user1/desktop/source_file.png

        Returns:
            base64data
        """
        if source_path is None and base64data is None:
            raise InvalidArgumentException('Must either pass base64 data or a local file path')

        if source_path is not None:
            try:
                with open(source_path, 'rb') as f:
                    file_data = f.read()
            except IOError as e:
                message = f'source_path "{source_path}" could not be found. Are you sure the file exists?'
                raise InvalidArgumentException(message) from e
            base64data = base64.b64encode(file_data).decode('utf-8')

        # result = self._current_application().push_file(destination_path, base64data, source_path)

        self._current_application().execute(Command.PUSH_FILE, {'path': destination_path, 'data': base64data})

        return base64data

    def appium_transfer_file(self, file_path, remote_path):
        """
        Streams a binary file, base64-encodes it chunk by chunk,
        and sends it directly to a remote machine via PowerShell commands.

        Powershell command must be allowed. eg: appium --relaxed-security

        file_path: source file path, eg: c:/users/user1/desktop/screenshot_file.png
        remote_path: destination path, eg: c:/users/user1/download/screenshot_file.png
        """
        file_path = Path(file_path)
        remote_path = str(remote_path)
        remote_b64_path = remote_path + ".b64.tmp"
        chunk_size = 6000  # chunk size in raw bytes (will expand when base64 encoded)

        # 1. Ensure remote parent directory exists
        remote_directory = str(Path(remote_path).parent)
        mkdir_cmd = f'New-Item -Path "{remote_directory}" -ItemType Directory -Force'
        self.execute_script("powerShell", command=mkdir_cmd)
        self._info(f"Ensured remote directory: {remote_directory}")

        # 2. Open and stream file, encoding and sending each chunk
        with open(file_path, "rb") as f:
            chunk_index = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                chunk_b64 = base64.b64encode(chunk).decode('utf-8')
                escaped_chunk = chunk_b64.replace("`", "``").replace('"', '`"')
                ps = f'Add-Content -Path "{remote_b64_path}" -Value "{escaped_chunk}"'
                self.execute_script("powerShell", command=ps)
                chunk_index += 1
                self._info(f"Sent chunk {chunk_index}")

        # 3. Decode and write binary file on remote side
        decode_script = (
            f'[IO.File]::WriteAllBytes("{remote_path}";'
            f'[Convert]::FromBase64String((Get-Content "{remote_b64_path}" -Raw)))'
        )
        self.execute_script("powerShell", command=decode_script)
        self._info(f"File written to: {remote_path}")

        # 4. Optional cleanup
        cleanup_script = f'Remove-Item "{remote_b64_path}" -ErrorAction SilentlyContinue'
        self.execute_script("powerShell", command=cleanup_script)
        self._info("Cleaned up temporary base64 file.")

    def appium_split_and_push_file(self, source_path: str, remote_path: str, chunk_size_mb: int = 20):
        """
        Splits a binary file into chunks, pushes each to a remote machine via Appium,
        then executes a PowerShell script remotely to recombine and clean up chunk files.

        Powershell command must be allowed. eg: appium --relaxed-security

        Parameters:
            source_path (str): Local path to the binary file.
            remote_path (str): Full remote file path to create from recombination.
            chunk_size_mb (int): Size of each chunk in MB (default: 20MB).
        """
        chunk_size = chunk_size_mb * 1024 * 1024
        file_size = os.path.getsize(source_path)

        file_name = os.path.basename(source_path)
        remote_dir = os.path.dirname(remote_path)
        total_chunks = math.ceil(file_size / chunk_size)
        # chunk_index_digits = max(4, len(str(total_chunks - 1)))  # at least 4 digits
        chunk_index_digits = len(str(total_chunks - 1))

        self._info(f"Splitting '{file_name}' ({file_size} bytes) into {total_chunks} chunks of {chunk_size_mb}MB each")

        # Step 1: Split and push chunks
        with open(source_path, "rb") as f:
            for index in range(total_chunks):
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                b64_chunk = base64.b64encode(chunk).decode("utf-8")
                chunk_suffix = f"{index:0{chunk_index_digits}d}"
                remote_chunk_path = os.path.join(remote_dir, f"{file_name}.part{chunk_suffix}")

                self.appium_push_file(destination_path=remote_chunk_path, base64data=b64_chunk)
                self._info(f"Pushed chunk {chunk_suffix} to {remote_chunk_path}")

        # Step 2: Build PowerShell recombine script
        escaped_dir = remote_dir.replace("'", "''")
        escaped_out = remote_path.replace("'", "''")
        escaped_base = file_name.replace("'", "''")
        pad_format = f"D{chunk_index_digits}"

        ps_script_lines = [
            f"$out = [System.IO.File]::OpenWrite('{escaped_out}')",
            "$out.SetLength(0)",
            f"for ($i = 0; $i -lt {total_chunks}; $i++) {{",
            f"    $chunkName = '{escaped_base}.part' + $i.ToString('{pad_format}')",
            f"    $chunkPath = Join-Path '{escaped_dir}' $chunkName",
            '    if (-not (Test-Path $chunkPath)) { throw "Missing chunk: $chunkPath" }',
            "    $in = [System.IO.File]::OpenRead($chunkPath)",
            "    $buffer = New-Object byte[] (1MB)",
            "    while (($n = $in.Read($buffer, 0, $buffer.Length)) -gt 0) {",
            "        $out.Write($buffer, 0, $n)",
            "    }",
            "    $in.Close()",
            "}",
            "$out.Close()",
            f"for ($i = 0; $i -lt {total_chunks}; $i++) {{",
            f"    $chunkName = '{escaped_base}.part' + $i.ToString('{pad_format}')",
            f"    $chunkPath = Join-Path '{escaped_dir}' $chunkName",
            "    Remove-Item -Path $chunkPath -Force -ErrorAction SilentlyContinue",
            "}",
            f"Write-Output 'Combine and cleanup complete: {escaped_out}'"
        ]

        ps_script = "\n".join(ps_script_lines)

        # Step 3: Execute recombine script remotely
        self._info("Combining chunks and cleaning up on remote machine...")
        result = self.appium_execute_powershell_script(ps_script)
        self._info(f"Remote PowerShell result: {result}")
        return escaped_out

    # Private

    def _parse_location(self, rect, kwargs, x_offset_key, y_offset_key):
        """Parse offset inside a rect."""
        offset = kwargs.get('offset')
        x_offset = offset if offset is not None else kwargs.get(x_offset_key, 'center')
        y_offset = offset if offset is not None else kwargs.get(y_offset_key, 'center')

        x = rect['x'] + (rect['width'] // 2 if x_offset == 'center' else int(x_offset))
        y = rect['y'] + (rect['height'] // 2 if y_offset == 'center' else int(y_offset))
        return x, y

    def _generate_click_command(self, x, y, button='left'):
        """
        Generate a PowerShell command to click at the given coordinates.

        https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-mouse_event

        @param x: X coordinate
        @param y: Y coordinate
        @param button:
            'left'           - single left click
            'right'          - single right click
            'middle'         - single middle click
            'double'         - double left click
            'triple'         - triple left click
            'right-double'   - double right click
        @return: PowerShell one-liner as string
        """
        button = button.lower()

        # Mouse event codes
        left_code = 6  # MOUSEEVENTF_LEFTDOWN | MOUSEEVENTF_LEFTUP
        right_code = 24  # MOUSEEVENTF_RIGHTDOWN | MOUSEEVENTF_RIGHTUP
        middle_code = 40  # MOUSEEVENTF_MIDDLEDOWN | MOUSEEVENTF_MIDDLEUP

        # Define all buttons
        click_events = {
            'left': f'[M]::mouse_event({left_code},0,0,0,[UIntPtr]::Zero);',
            'right': f'[M]::mouse_event({right_code},0,0,0,[UIntPtr]::Zero);',
            'middle': f'[M]::mouse_event({middle_code},0,0,0,[UIntPtr]::Zero);',
            'double': (
                f'[M]::mouse_event({left_code},0,0,0,[UIntPtr]::Zero);'
                f'Start-Sleep -m 100;'
                f'[M]::mouse_event({left_code},0,0,0,[UIntPtr]::Zero);'
            ),
            'triple': (
                f'[M]::mouse_event({left_code},0,0,0,[UIntPtr]::Zero);'
                f'Start-Sleep -m 100;'
                f'[M]::mouse_event({left_code},0,0,0,[UIntPtr]::Zero);'
                f'Start-Sleep -m 100;'
                f'[M]::mouse_event({left_code},0,0,0,[UIntPtr]::Zero);'
            ),
            'right-double': (
                f'[M]::mouse_event({right_code},0,0,0,[UIntPtr]::Zero);'
                f'Start-Sleep -m 100;'
                f'[M]::mouse_event({right_code},0,0,0,[UIntPtr]::Zero);'
            )
        }

        if button not in click_events:
            valid = ', '.join(click_events.keys())
            raise ValueError(f"button must be one of: {valid}")

        event_code = click_events[button]

        ps_cmd = (
            'if (-not ("M" -as [type])) {'
            "Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;"
            'public class M{'
            '[DllImport("user32.dll")]public static extern bool SetCursorPos(int x,int y);'
            '[DllImport("user32.dll")]public static extern void mouse_event(uint f,uint dx,uint dy,uint d,UIntPtr i);}'
            "'|Out-Null;};"
            f'[M]::SetCursorPos({x},{y});Start-Sleep -m 300;'
            f'{event_code}'
        )

        return ps_cmd

    def _generate_drag_command(self, x_start, y_start, x_end, y_end, button='left', duration_sec=0.5):
        """
        https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-mouse_event

        Generate a PowerShell command to simulate mouse drag from (x_start, y_start) to (x_end, y_end)
        over the given duration in seconds.

        @param x_start: Start X coordinate
        @param y_start: Start Y coordinate
        @param x_end: End X coordinate
        @param y_end: End Y coordinate
        @param button: 'left' or 'right'
        @param duration_sec: Total drag duration in seconds
        @return: PowerShell command string
        """
        button = button.lower()
        button_codes = {
            'left': (0x0002, 0x0004),  # MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP
            'right': (0x0008, 0x0010),  # MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP
            'middle': (0x0020, 0x0040),  # MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP
        }

        if button not in button_codes:
            raise ValueError("button must be 'left', 'right', or 'middle'")

        down_code, up_code = button_codes[button]

        delay_ms = 50
        steps = round((float(duration_sec) * 1000) / delay_ms)
        dx = x_end - x_start
        dy = y_end - y_start

        ps_cmd = (
            'if (-not ("M" -as [type])) {'
            "Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;"
            'public class M{'
            '[DllImport("user32.dll")]public static extern bool SetCursorPos(int x,int y);'
            '[DllImport("user32.dll")]public static extern void mouse_event(uint f,uint dx,uint dy,uint d,UIntPtr i);}'
            "'|Out-Null;};"
            f'[M]::SetCursorPos({x_start},{y_start})|Out-Null; Start-Sleep -m 300;'
            f'[M]::mouse_event({down_code},0,0,0,[UIntPtr]::Zero); Start-Sleep -m 300;'
            f'for ($i=1; $i -le {steps}; $i++){{'
            f'$x={x_start}+[math]::Round({dx}*$i/{steps});'
            f'$y={y_start}+[math]::Round({dy}*$i/{steps});'
            f'[M]::SetCursorPos($x,$y)|Out-Null; Start-Sleep -m {delay_ms};'
            '};'
            f'[M]::SetCursorPos({x_end},{y_end})|Out-Null; Start-Sleep -m 300;'
            f'[M]::mouse_event({up_code},0,0,0,[UIntPtr]::Zero);'
        )

        return ps_cmd

    def _generate_keyboard_command(self, sequences):
        raise Exception('Not Implement yet')

    def _script_path(self, name):
        return os.path.join(SCRIPTS_DIR, name)
