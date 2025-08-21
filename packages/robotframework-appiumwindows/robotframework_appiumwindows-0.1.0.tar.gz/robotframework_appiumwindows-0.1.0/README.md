# Robot Framework AppiumLibrary Compatible with NovaWindows Driver

---

## Overview
This library extends [AppiumLibrary](https://github.com/serhatbolsu/robotframework-appiumlibrary) to provide compatibility with the **NovaWindows Driver** for Appium 2.x.  

It allows you to automate Windows desktop applications using **Robot Framework** with minimal setup.  

---

> **Note**
>
> - NovaWindows Driver currently uses a **PowerShell session** as its back-end.  
>   - No Developer Mode required  
>   - No extra dependencies required  
> - A future update is planned to move to a **.NET-based backend** for:  
>   - Improved reliability  
>   - Better error handling  
>   - More feature support beyond PowerShell limitations  
>
> Reference: [AutomateThePlanet/appium-novawindows-driver](https://github.com/AutomateThePlanet/appium-novawindows-driver)

---

## Installation

### 1. On the **Test Runner (local machine)**

Install the Robot Framework library:

```bash
pip install robotframework-appiumwindows
```

> This is the only requirement on the machine where you run Robot Framework tests.  
> No need to install Node.js or Appium here.

---

### 2. On the **Target Machine (remote machine under test)**

This is where the Appium server and NovaWindows driver must be installed.

1. Install **Node.js**  
   [Download Node.js](https://nodejs.org/en/download)  

2. Install **Appium** globally:  
   ```bash
   npm install -g appium
   ```

3. Install **NovaWindows Driver**:  
   ```bash
   appium driver install --source=npm appium-novawindows-driver
   ```

4. Start the Appium server:  
   ```bash
   appium --relaxed-security
   ```
   (use `--relaxed-security` if you plan to execute PowerShell commands)

---

## Example Test

```robot
*** Settings ***
Library    AppiumLibrary

Test Setup       Open Root Session
Test Teardown    Appium Close All Applications


*** Test Cases ***
Type To Notepad
    [Documentation]    Launch Notepad, type text, and close without saving
    Appium Execute Powershell Command    Start-Process "notepad"
    Appium Input    class=Notepad    This is example{enter 3}Close without save
    Appium Click    //Window[@ClassName='Notepad']//Button[@Name='Close']
    Appium Click    name=Don't Save


*** Keywords ***
Open Root Session
    ${parameters}=    Create Dictionary
    ...    remote_url=http://<TARGET_MACHINE_IP>:4723
    ...    platformName=Windows
    ...    appium:app=Root
    ...    appium:automationName=NovaWindows
    ...    appium:newCommandTimeout=30
    Open Application    &{parameters}
```

---

## Architecture

```text
+--------------------------+         +----------------------------+
|  Test Runner (Local PC)  |         |  Target Machine (Windows)  |
|--------------------------|         |----------------------------|
| - Robot Framework        |         | - Node.js                  |
| - robotframework-        |  --->   | - Appium 2.x               |
|   appium-windows (pip)   |         | - NovaWindows Driver       |
+--------------------------+         +----------------------------+
```

---

## References

- [Appium](https://appium.io/)  
- [Robot Framework](https://robotframework.org/)  
- [AppiumLibrary](https://github.com/serhatbolsu/robotframework-appiumlibrary)  
- [NovaWindows Driver](https://github.com/AutomateThePlanet/appium-novawindows-driver)  

---