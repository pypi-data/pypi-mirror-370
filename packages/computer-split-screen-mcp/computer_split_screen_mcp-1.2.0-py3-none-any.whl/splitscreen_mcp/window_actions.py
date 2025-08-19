import platform
import subprocess
import time
import math

_WINDOWS_IMPORTS_AVAILABLE = False
if platform.system() == 'Windows':
    try:
        import ctypes
        from ctypes import wintypes
        import win32con
        import win32gui
        import win32api
        _WINDOWS_IMPORTS_AVAILABLE = True
    except ImportError:
        pass

# ===== DWM (via Visible Frame Bounds) =====
if _WINDOWS_IMPORTS_AVAILABLE:
    DWMWA_EXTENDED_FRAME_BOUNDS = 9
    _dwmapi = ctypes.windll.dwmapi

    class RECT(ctypes.Structure):
        _fields_ = [('left', ctypes.c_long),
                    ('top', ctypes.c_long),
                    ('right', ctypes.c_long),
                    ('bottom', ctypes.c_long)]


def execute_os(mac_command, win_command):

    os_name = platform.system()

    if os_name == 'Darwin':
        return mac_command
    elif os_name == 'Windows': 
        return win_command
    else:
        print("Unsupported Operating System (Not MacOS or Windows)")
        return False


def check_fullscreen_mac() -> bool:

    script = r'''
    try
      tell application "System Events"
        set frontProc to first application process whose frontmost is true
        tell frontProc
          -- Prefer the actually focused window
          set targetWin to missing value
          try
            set targetWin to value of attribute "AXFocusedWindow"
          end try
          -- Fall back to a standard window, then any window
          if targetWin is missing value then
            set stdWins to every window whose subrole is "AXStandardWindow"
            if stdWins is not {} then set targetWin to item 1 of stdWins
          end if
          if targetWin is missing value then
            if (count of windows) > 0 then set targetWin to window 1
          end if

          if targetWin is missing value then return false

          if exists attribute "AXFullScreen" of targetWin then
            return (value of attribute "AXFullScreen" of targetWin)
          else
            return false
          end if
        end tell
      end tell
    on error
      return false
    end try
    '''

    try:
        r = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, check=True) 
        return r.stdout.strip().lower() == 'true' # Fullscreen = True, Otherwise = False
    except subprocess.CalledProcessError:
        return False


def exit_fullscreen_mac():

    script = '''
    tell application "System Events"
        key code 3 using {command down, control down}
    end tell
    '''

    subprocess.run(['osascript', '-e', script], check=True) # Exit Fullscreen via (CMD + CTRL + F)
    return True


def check_exit_fullscreen_win(hwnd):
    """Restore if Window is Maximized so it can be Resized/Moved."""
    placement = win32gui.GetWindowPlacement(hwnd)
    if placement[1] == win32con.SW_SHOWMAXIMIZED:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)


def set_dpi_aware_win():
    """Ensure Coordinates Match Physical Pixels on High-DPI Displays."""
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def get_effective_dimension_win(hwnd):
    """(L, T, R, B) for the Monitor Containing hwnd, Excluding Taskbar."""
    monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    mi = win32api.GetMonitorInfo(monitor)  # Keys: "Monitor" & "Work"
    return mi['Work']


def get_visible_frame_win(hwnd):
    """
    (L, T, R, B) of the Visible Window Frame (Excludes Drop Shadow).
    Falls back to GetWindowRect if DWM Call Fails.
    """
    rect = RECT()
    hr = _dwmapi.DwmGetWindowAttribute(
        wintypes.HWND(hwnd),
        ctypes.c_uint(DWMWA_EXTENDED_FRAME_BOUNDS),
        ctypes.byref(rect),
        ctypes.sizeof(rect),
    )
    if hr == 0:
        return rect.left, rect.top, rect.right, rect.bottom
    return win32gui.GetWindowRect(hwnd)


def apply_effective_bounds_win(hwnd, target_ltrb):
    """
    Move/Resize so the Visible Frame Aligns with the Target Rect.
    1) Set Outer Bounds Roughly, 2) Measure Insets, 3) Correct.
    """
    L, T, R, B = target_ltrb
    W = max(1, R - L)
    H = max(1, B - T)

    win32gui.SetWindowPos(
        hwnd, 0, L, T, W, H,
        win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
    )

    visL, visT, visR, visB = get_visible_frame_win(hwnd)
    outL, outT, outR, outB = win32gui.GetWindowRect(hwnd)

    inset_left   = visL - outL
    inset_top    = visT - outT
    inset_right  = outR - visR
    inset_bottom = outB - visB

    corrL = L - inset_left
    corrT = T - inset_top
    corrW = W + inset_left + inset_right
    corrH = H + inset_top + inset_bottom

    corrL = int(round(corrL))
    corrT = int(round(corrT))
    corrW = max(1, int(round(corrW)))
    corrH = max(1, int(round(corrH)))

    win32gui.SetWindowPos(
        hwnd, 0, corrL, corrT, corrW, corrH,
        win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
    )


def apply_window_fraction_win(rx, ry, rw, rh):
    """
    Snap the Foreground Window to a Rectangle Expressed as Fractions
    of the Monitor Work Area: (rx, ry, rw, rh) in [0..1].
    """
    set_dpi_aware_win()
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd or not win32gui.IsWindowVisible(hwnd):
        raise RuntimeError("No visible foreground window found.")

    check_exit_fullscreen_win(hwnd)

    waL, waT, waR, waB = get_effective_dimension_win(hwnd)
    waW = waR - waL
    waH = waB - waT

    L = waL + int(math.floor(waW * rx))
    T = waT + int(math.floor(waH * ry))
    R = waL + int(math.floor(waW * (rx + rw)))
    B = waT + int(math.floor(waH * (ry + rh)))

    R = max(R, L + 1)
    B = max(B, T + 1)

    apply_effective_bounds_win(hwnd, (L, T, R, B))


# Tool 01 - Minimise Window
def minimise_window():
    run = execute_os(minimise_window_mac, minimise_window_win)
    return run()


def minimise_window_mac():

    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
        end tell
        tell application frontApp
            activate
        end tell
        tell application "System Events"
            tell process frontApp
                set frontWindow to window 1
                set value of attribute "AXMinimized" of frontWindow to true
            end tell
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error Minimising Window: {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def minimise_window_win():

    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        result = ctypes.windll.user32.ShowWindow(hwnd, 6)

        if result:
            return True
        else:
            print("Failed to Minimise Window")
            return False
 
    except Exception as e:
        print(f"Error Minimising Window: {e}")
        return False


# Tool 02 - Maximise Window
def maximise_window():
    run = execute_os(maximise_window_mac, maximise_window_win)
    return run()


def maximise_window_mac():
    """
    Maximize the focused window to the visible frame of the *current* display,
    robust across multi-monitor setups (any arrangement, Dock/Menu Bar, Spaces).
    """
    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions

        -- Global union max Y across all displays (for AX/AppKit Y conversion)
        on unionMaxY()
          set maxY to 0
          set screens to current application's NSScreen's screens()
          repeat with s in screens
            set f to s's frame()
            set yMax to (current application's NSMaxY(f)) as integer
            if yMax > maxY then set maxY to yMax
          end repeat
          return maxY
        end unionMaxY

        -- Pick the NSScreen containing a global point (px,py)
        on screenForPoint(px, py)
          set screens to current application's NSScreen's screens()
          set chosen to current application's NSScreen's mainScreen()
          repeat with s in screens
            set f to s's frame()
            set fx to (current application's NSMinX(f)) as integer
            set fy to (current application's NSMinY(f)) as integer
            set fw to (current application's NSWidth(f)) as integer
            set fh to (current application's NSHeight(f)) as integer
            if (px ≥ fx and px ≤ fx + fw and py ≥ fy and py ≤ fy + fh) then
              set chosen to s
              exit repeat
            end if
          end repeat
          return chosen
        end screenForPoint

        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            -- Resolve a usable target window
            set targetWin to missing value
            try
              set targetWin to value of attribute "AXFocusedWindow" of frontProc
            end try
            if targetWin is missing value then
              set stdWins to every window of frontProc whose subrole is "AXStandardWindow"
              if stdWins is not {} then set targetWin to item 1 of stdWins
            end if
            if targetWin is missing value then
              if (count of windows of frontProc) > 0 then set targetWin to window 1 of frontProc
            end if
            if targetWin is missing value then error "No usable window."

            -- AX geometry (global, top-left origin)
            set {wx, wy} to value of attribute "AXPosition" of targetWin
            set {ww, wh} to value of attribute "AXSize" of targetWin
            set cx to wx + (ww / 2)
            set cy to wy + (wh / 2)

            -- Choose the *actual* screen containing the window center (global coords)
            set scr to my screenForPoint(cx, cy)

            -- Visible frame on that screen (global AppKit coords, bottom-left origin)
            set vFrame to scr's visibleFrame()
            set vX to (current application's NSMinX(vFrame)) as integer
            set vY to (current application's NSMinY(vFrame)) as integer
            set vW to (current application's NSWidth(vFrame)) as integer
            set vH to (current application's NSHeight(vFrame)) as integer

            -- Convert AppKit -> AX Y using GLOBAL union height
            set globalMaxY to my unionMaxY()
            set axYTop to globalMaxY - (vY + vH)

            -- Resize/move if allowed
            set canResize to true
            try
              set canResize to (value of attribute "AXResizable" of targetWin)
            end try
            if canResize then
              set position of targetWin to {vX, axYTop}
              set size of targetWin to {vW, vH}
            end if

          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error Maximising Window: {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def maximise_window_win():
    """Put the Foreground Window into the OS 'Maximize/Bordered Fullscreen' State (Bordered, Taskbar Visible)."""
    set_dpi_aware_win()
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd or not win32gui.IsWindowVisible(hwnd):
        raise RuntimeError("No visible foreground window found.")
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)


# Tool 03 - Fullscreen Window
def fullscreen_window():
    run = execute_os(fullscreen_window_mac, fullscreen_window_win)
    return run()


def fullscreen_window_mac():

    try:
        script = '''
        tell application "System Events"
            tell process (name of first application process whose frontmost is true)
                set frontWindow to window 1
                set value of attribute "AXFullScreen" of frontWindow to true
            end tell
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error to Fullscreen Window: {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def fullscreen_window_win():
    """Put the Foreground Window into the OS 'Maximize/Bordered Fullscreen' State (Bordered, Taskbar Visible)."""
    set_dpi_aware_win()
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd or not win32gui.IsWindowVisible(hwnd):
        raise RuntimeError("No visible foreground window found.")
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)


# Tool 04 - Left 1/2 Screen
def left_half_window():
    run = execute_os(left_half_window_mac, left_half_window_win)
    return run()


def left_half_window_mac():
    """
    Move the focused window to the left half of the *current* display,
    robust across multi-monitor setups (any arrangement, Dock/Menu bar, Spaces).
    """
    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions

        on unionMaxY()
          set maxY to 0
          set screens to current application's NSScreen's screens()
          repeat with s in screens
            set f to s's frame()
            set yMax to (current application's NSMaxY(f)) as integer
            if yMax > maxY then set maxY to yMax
          end repeat
          return maxY
        end unionMaxY

        on screenForPoint(px, py)
          set screens to current application's NSScreen's screens()
          set chosen to current application's NSScreen's mainScreen()
          repeat with s in screens
            set f to s's frame()
            set fx to (current application's NSMinX(f)) as integer
            set fy to (current application's NSMinY(f)) as integer
            set fw to (current application's NSWidth(f)) as integer
            set fh to (current application's NSHeight(f)) as integer
            if (px ≥ fx and px ≤ fx + fw and py ≥ fy and py ≤ fy + fh) then
              set chosen to s
              exit repeat
            end if
          end repeat
          return chosen
        end screenForPoint

        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            -- Resolve a usable target window
            set targetWin to missing value
            try
              set targetWin to value of attribute "AXFocusedWindow" of frontProc
            end try
            if targetWin is missing value then
              set stdWins to every window of frontProc whose subrole is "AXStandardWindow"
              if stdWins is not {} then set targetWin to item 1 of stdWins
            end if
            if targetWin is missing value then
              if (count of windows of frontProc) > 0 then set targetWin to window 1 of frontProc
            end if
            if targetWin is missing value then error "No usable window."

            -- AX geometry (global, top-left origin)
            set {wx, wy} to value of attribute "AXPosition" of targetWin
            set {ww, wh} to value of attribute "AXSize" of targetWin
            set cx to wx + (ww / 2)
            set cy to wy + (wh / 2)

            -- Choose the *actual* screen containing the window center (global coords)
            set scr to my screenForPoint(cx, cy)

            -- Visible frame on that screen (global AppKit coords, bottom-left origin)
            set vFrame to scr's visibleFrame()
            set vX to (current application's NSMinX(vFrame)) as integer
            set vY to (current application's NSMinY(vFrame)) as integer
            set vW to (current application's NSWidth(vFrame)) as integer
            set vH to (current application's NSHeight(vFrame)) as integer

            -- Convert AppKit -> AX Y using GLOBAL union height
            set globalMaxY to my unionMaxY()
            set axYTop to globalMaxY - (vY + vH)

            -- Left HALF sizing (integer division avoids banker's rounding quirks)
            set halfW to (vW div 2)

            -- Resize/move if allowed
            set canResize to true
            try
              set canResize to (value of attribute "AXResizable" of targetWin)
            end try
            if canResize then
              set position of targetWin to {vX, axYTop}
              set size of targetWin to {halfW, vH}
            end if

          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (left half): {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def left_half_window_win():
    apply_window_fraction_win(0.0, 0.0, 0.5, 1.0)


# Tool 05 - Right 1/2 Screen
def right_half_window():
    run = execute_os(right_half_window_mac, right_half_window_win)
    return run()


def right_half_window_mac():
    """
    Move the focused window to the right half of the *current* display,
    robust across multi-monitor setups (any arrangement, Dock/Menu bar, Spaces).
    """
    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions

        on unionMaxY()
          set maxY to 0
          set screens to current application's NSScreen's screens()
          repeat with s in screens
            set f to s's frame()
            set yMax to (current application's NSMaxY(f)) as integer
            if yMax > maxY then set maxY to yMax
          end repeat
          return maxY
        end unionMaxY

        on screenForPoint(px, py)
          set screens to current application's NSScreen's screens()
          set chosen to current application's NSScreen's mainScreen()
          repeat with s in screens
            set f to s's frame()
            set fx to (current application's NSMinX(f)) as integer
            set fy to (current application's NSMinY(f)) as integer
            set fw to (current application's NSWidth(f)) as integer
            set fh to (current application's NSHeight(f)) as integer
            if (px ≥ fx and px ≤ fx + fw and py ≥ fy and py ≤ fy + fh) then
              set chosen to s
              exit repeat
            end if
          end repeat
          return chosen
        end screenForPoint

        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            -- Resolve a usable target window
            set targetWin to missing value
            try
              set targetWin to value of attribute "AXFocusedWindow" of frontProc
            end try
            if targetWin is missing value then
              set stdWins to every window of frontProc whose subrole is "AXStandardWindow"
              if stdWins is not {} then set targetWin to item 1 of stdWins
            end if
            if targetWin is missing value then
              if (count of windows of frontProc) > 0 then set targetWin to window 1 of frontProc
            end if
            if targetWin is missing value then error "No usable window."

            -- AX geometry (global, top-left origin)
            set {wx, wy} to value of attribute "AXPosition" of targetWin
            set {ww, wh} to value of attribute "AXSize" of targetWin
            set cx to wx + (ww / 2)
            set cy to wy + (wh / 2)

            -- Choose the *actual* screen containing the window center (global coords)
            set scr to my screenForPoint(cx, cy)

            -- Visible frame on that screen (global AppKit coords, bottom-left origin)
            set vFrame to scr's visibleFrame()
            set vX to (current application's NSMinX(vFrame)) as integer
            set vY to (current application's NSMinY(vFrame)) as integer
            set vW to (current application's NSWidth(vFrame)) as integer
            set vH to (current application's NSHeight(vFrame)) as integer

            -- Convert AppKit -> AX Y using GLOBAL union height
            set globalMaxY to my unionMaxY()
            set axYTop to globalMaxY - (vY + vH)

            -- Right HALF sizing (integer division avoids banker's rounding quirks)
            set halfW to (vW div 2)

            -- Resize/move if allowed
            set canResize to true
            try
              set canResize to (value of attribute "AXResizable" of targetWin)
            end try
            if canResize then
              set position of targetWin to {vX + halfW, axYTop}
              set size of targetWin to {vW - halfW, vH}
            end if

          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (right half): {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def right_half_window_win():
    apply_window_fraction_win(0.5, 0.0, 0.5, 1.0)


# Tool 06 - Left 1/3 Screen
def left_third_window():
    run = execute_os(left_third_window_mac, left_third_window_win)
    return run()


def left_third_window_mac():
    """
    Move the focused window to the left third of the *current* display,
    robust across multi-monitor setups (any arrangement, Dock/Menu bar, Spaces).
    """
    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)
        
    try:
        script = r'''
        use framework "AppKit"
        use scripting additions

        on unionMaxY()
          set maxY to 0
          set screens to current application's NSScreen's screens()
          repeat with s in screens
            set f to s's frame()
            set yMax to (current application's NSMaxY(f)) as integer
            if yMax > maxY then set maxY to yMax
          end repeat
          return maxY
        end unionMaxY

        on screenForPoint(px, py)
          set screens to current application's NSScreen's screens()
          set chosen to current application's NSScreen's mainScreen()
          repeat with s in screens
            set f to s's frame()
            set fx to (current application's NSMinX(f)) as integer
            set fy to (current application's NSMinY(f)) as integer
            set fw to (current application's NSWidth(f)) as integer
            set fh to (current application's NSHeight(f)) as integer
            if (px ≥ fx and px ≤ fx + fw and py ≥ fy and py ≤ fy + fh) then
              set chosen to s
              exit repeat
            end if
          end repeat
          return chosen
        end screenForPoint

        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            -- Resolve a usable target window
            set targetWin to missing value
            try
              set targetWin to value of attribute "AXFocusedWindow" of frontProc
            end try
            if targetWin is missing value then
              set stdWins to every window of frontProc whose subrole is "AXStandardWindow"
              if stdWins is not {} then set targetWin to item 1 of stdWins
            end if
            if targetWin is missing value then
              if (count of windows of frontProc) > 0 then set targetWin to window 1 of frontProc
            end if
            if targetWin is missing value then error "No usable window."

            -- AX geometry (global, top-left origin)
            set {wx, wy} to value of attribute "AXPosition" of targetWin
            set {ww, wh} to value of attribute "AXSize" of targetWin
            set cx to wx + (ww / 2)
            set cy to wy + (wh / 2)

            -- Choose the *actual* screen containing the window center (global coords)
            set scr to my screenForPoint(cx, cy)

            -- Visible frame on that screen (global AppKit coords, bottom-left origin)
            set vFrame to scr's visibleFrame()
            set vX to (current application's NSMinX(vFrame)) as integer
            set vY to (current application's NSMinY(vFrame)) as integer
            set vW to (current application's NSWidth(vFrame)) as integer
            set vH to (current application's NSHeight(vFrame)) as integer

            -- Convert AppKit -> AX Y using GLOBAL union height
            set globalMaxY to my unionMaxY()
            set axYTop to globalMaxY - (vY + vH)

            -- Left THIRD sizing (rounded so thirds tile perfectly)
            set b0 to round (vW * 0.0 / 3.0)
            set b1 to round (vW * 1.0 / 3.0)
            set x0 to vX + b0
            set x1 to vX + b1
            set sliceW to (x1 - x0)

            -- Resize/move if allowed
            set canResize to true
            try
              set canResize to (value of attribute "AXResizable" of targetWin)
            end try
            if canResize then
              set position of targetWin to {x0, axYTop}
              set size of targetWin to {sliceW, vH}
            end if

          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (left third): {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def left_third_window_win():
    apply_window_fraction_win(0.0, 0.0, 1.0/3.0, 1.0)


# Tool 07 - Middle 1/3 Screen
def middle_third_window():
    run = execute_os(middle_third_window_mac, middle_third_window_win)
    return run()


def middle_third_window_mac():
    """
    Move the focused window to the middle third of the *current* display,
    robust across multi-monitor setups (any arrangement, Dock/Menu bar, Spaces).
    """
    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions

        on unionMaxY()
          set maxY to 0
          set screens to current application's NSScreen's screens()
          repeat with s in screens
            set f to s's frame()
            set yMax to (current application's NSMaxY(f)) as integer
            if yMax > maxY then set maxY to yMax
          end repeat
          return maxY
        end unionMaxY

        on screenForPoint(px, py)
          set screens to current application's NSScreen's screens()
          set chosen to current application's NSScreen's mainScreen()
          repeat with s in screens
            set f to s's frame()
            set fx to (current application's NSMinX(f)) as integer
            set fy to (current application's NSMinY(f)) as integer
            set fw to (current application's NSWidth(f)) as integer
            set fh to (current application's NSHeight(f)) as integer
            if (px ≥ fx and px ≤ fx + fw and py ≥ fy and py ≤ fy + fh) then
              set chosen to s
              exit repeat
            end if
          end repeat
          return chosen
        end screenForPoint

        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            -- Resolve a usable target window
            set targetWin to missing value
            try
              set targetWin to value of attribute "AXFocusedWindow" of frontProc
            end try
            if targetWin is missing value then
              set stdWins to every window of frontProc whose subrole is "AXStandardWindow"
              if stdWins is not {} then set targetWin to item 1 of stdWins
            end if
            if targetWin is missing value then
              if (count of windows of frontProc) > 0 then set targetWin to window 1 of frontProc
            end if
            if targetWin is missing value then error "No usable window."

            -- AX geometry (global, top-left origin)
            set {wx, wy} to value of attribute "AXPosition" of targetWin
            set {ww, wh} to value of attribute "AXSize" of targetWin
            set cx to wx + (ww / 2)
            set cy to wy + (wh / 2)

            -- Choose the *actual* screen containing the window center (global coords)
            set scr to my screenForPoint(cx, cy)

            -- Visible frame on that screen (global AppKit coords, bottom-left origin)
            set vFrame to scr's visibleFrame()
            set vX to (current application's NSMinX(vFrame)) as integer
            set vY to (current application's NSMinY(vFrame)) as integer
            set vW to (current application's NSWidth(vFrame)) as integer
            set vH to (current application's NSHeight(vFrame)) as integer

            -- Convert AppKit -> AX Y using GLOBAL union height
            set globalMaxY to my unionMaxY()
            set axYTop to globalMaxY - (vY + vH)

            -- Middle THIRD sizing (rounded so thirds tile perfectly)
            set b1 to round (vW * 1.0 / 3.0)
            set b2 to round (vW * 2.0 / 3.0)
            set x0 to vX + b1
            set x1 to vX + b2
            set sliceW to (x1 - x0)

            -- Resize/move if allowed
            set canResize to true
            try
              set canResize to (value of attribute "AXResizable" of targetWin)
            end try
            if canResize then
              set position of targetWin to {x0, axYTop}
              set size of targetWin to {sliceW, vH}
            end if

          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (middle third): {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def middle_third_window_win():
    apply_window_fraction_win(1.0/3.0, 0.0, 1.0/3.0, 1.0)


# Tool 08 - Right 1/3 Screen
def right_third_window():
    run = execute_os(right_third_window_mac, right_third_window_win)
    return run()


def right_third_window_mac():
    """
    Move the focused window to the right third of the *current* display,
    robust across multi-monitor setups (any arrangement, Dock/Menu bar, Spaces).
    """
    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions

        on unionMaxY()
          set maxY to 0
          set screens to current application's NSScreen's screens()
          repeat with s in screens
            set f to s's frame()
            set yMax to (current application's NSMaxY(f)) as integer
            if yMax > maxY then set maxY to yMax
          end repeat
          return maxY
        end unionMaxY

        on screenForPoint(px, py)
          set screens to current application's NSScreen's screens()
          set chosen to current application's NSScreen's mainScreen()
          repeat with s in screens
            set f to s's frame()
            set fx to (current application's NSMinX(f)) as integer
            set fy to (current application's NSMinY(f)) as integer
            set fw to (current application's NSWidth(f)) as integer
            set fh to (current application's NSHeight(f)) as integer
            if (px ≥ fx and px ≤ fx + fw and py ≥ fy and py ≤ fy + fh) then
              set chosen to s
              exit repeat
            end if
          end repeat
          return chosen
        end screenForPoint

        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            -- Resolve a usable target window
            set targetWin to missing value
            try
              set targetWin to value of attribute "AXFocusedWindow" of frontProc
            end try
            if targetWin is missing value then
              set stdWins to every window of frontProc whose subrole is "AXStandardWindow"
              if stdWins is not {} then set targetWin to item 1 of stdWins
            end if
            if targetWin is missing value then
              if (count of windows of frontProc) > 0 then set targetWin to window 1 of frontProc
            end if
            if targetWin is missing value then error "No usable window."

            -- AX geometry (global, top-left origin)
            set {wx, wy} to value of attribute "AXPosition" of targetWin
            set {ww, wh} to value of attribute "AXSize" of targetWin
            set cx to wx + (ww / 2)
            set cy to wy + (wh / 2)

            -- Choose the *actual* screen containing the window center (global coords)
            set scr to my screenForPoint(cx, cy)

            -- Visible frame on that screen (global AppKit coords, bottom-left origin)
            set vFrame to scr's visibleFrame()
            set vX to (current application's NSMinX(vFrame)) as integer
            set vY to (current application's NSMinY(vFrame)) as integer
            set vW to (current application's NSWidth(vFrame)) as integer
            set vH to (current application's NSHeight(vFrame)) as integer

            -- Convert AppKit -> AX Y using GLOBAL union height
            set globalMaxY to my unionMaxY()
            set axYTop to globalMaxY - (vY + vH)

            -- Right THIRD sizing (rounded so thirds tile perfectly)
            set b2 to round (vW * 2.0 / 3.0)
            set x0 to vX + b2
            set x1 to vX + vW
            set sliceW to (x1 - x0)

            -- Resize/move if allowed
            set canResize to true
            try
              set canResize to (value of attribute "AXResizable" of targetWin)
            end try
            if canResize then
              set position of targetWin to {x0, axYTop}
              set size of targetWin to {sliceW, vH}
            end if

          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (right third): {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def right_third_window_win():
    apply_window_fraction_win(2.0/3.0, 0.0, 1.0/3.0, 1.0)


# Tool 09 - Top 1/2 Screen
def top_half_window():
    run = execute_os(top_half_window_mac, top_half_window_win)
    return run()


def top_half_window_mac():
    """
    Move the focused window to the top half of the *current* display,
    robust across multi-monitor setups (any arrangement, Dock/Menu bar, Spaces).
    """
    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions

        on unionMaxY()
          set maxY to 0
          set screens to current application's NSScreen's screens()
          repeat with s in screens
            set f to s's frame()
            set yMax to (current application's NSMaxY(f)) as integer
            if yMax > maxY then set maxY to yMax
          end repeat
          return maxY
        end unionMaxY

        on screenForPoint(px, py)
          set screens to current application's NSScreen's screens()
          set chosen to current application's NSScreen's mainScreen()
          repeat with s in screens
            set f to s's frame()
            set fx to (current application's NSMinX(f)) as integer
            set fy to (current application's NSMinY(f)) as integer
            set fw to (current application's NSWidth(f)) as integer
            set fh to (current application's NSHeight(f)) as integer
            if (px ≥ fx and px ≤ fx + fw and py ≥ fy and py ≤ fy + fh) then
              set chosen to s
              exit repeat
            end if
          end repeat
          return chosen
        end screenForPoint

        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            -- Resolve a usable target window
            set targetWin to missing value
            try
              set targetWin to value of attribute "AXFocusedWindow" of frontProc
            end try
            if targetWin is missing value then
              set stdWins to every window of frontProc whose subrole is "AXStandardWindow"
              if stdWins is not {} then set targetWin to item 1 of stdWins
            end if
            if targetWin is missing value then
              if (count of windows of frontProc) > 0 then set targetWin to window 1 of frontProc
            end if
            if targetWin is missing value then error "No usable window."

            -- AX geometry (global, top-left origin)
            set {wx, wy} to value of attribute "AXPosition" of targetWin
            set {ww, wh} to value of attribute "AXSize" of targetWin
            set cx to wx + (ww / 2)
            set cy to wy + (wh / 2)

            -- Choose the *actual* screen containing the window center (global coords)
            set scr to my screenForPoint(cx, cy)

            -- Visible frame on that screen (global AppKit coords, bottom-left origin)
            set vFrame to scr's visibleFrame()
            set vX to (current application's NSMinX(vFrame)) as integer
            set vY to (current application's NSMinY(vFrame)) as integer
            set vW to (current application's NSWidth(vFrame)) as integer
            set vH to (current application's NSHeight(vFrame)) as integer

            -- Convert AppKit -> AX Y using GLOBAL union height
            set globalMaxY to my unionMaxY()
            set axYTop to globalMaxY - (vY + vH)

            -- Top HALF sizing (integer division avoids banker's rounding quirks)
            set halfH to (vH div 2)

            -- Resize/move if allowed
            set canResize to true
            try
              set canResize to (value of attribute "AXResizable" of targetWin)
            end try
            if canResize then
              set position of targetWin to {vX, axYTop}
              set size of targetWin to {vW, halfH}
            end if

          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error Resizing Window via Top Half: {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def top_half_window_win():
    apply_window_fraction_win(0.0, 0.0, 1.0, 0.5)


# Tool 10 - Bottom 1/2 Screen
def bottom_half_window():
    run = execute_os(bottom_half_window_mac, bottom_half_window_win)
    return run()


def bottom_half_window_mac():
    """
    Move the focused window to the bottom half of the *current* display,
    robust across multi-monitor setups (any arrangement, Dock/Menu bar, Spaces).
    """
    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions

        on unionMaxY()
          set maxY to 0
          repeat with s in (current application's NSScreen's screens())
            set f to s's frame()
            set yMax to (current application's NSMaxY(f)) as integer
            if yMax > maxY then set maxY to yMax
          end repeat
          return maxY
        end unionMaxY

        on screenForPoint(px, py)
          set chosen to current application's NSScreen's mainScreen()
          repeat with s in (current application's NSScreen's screens())
            set f to s's frame()
            set fx to (current application's NSMinX(f)) as integer
            set fy to (current application's NSMinY(f)) as integer
            set fw to (current application's NSWidth(f)) as integer
            set fh to (current application's NSHeight(f)) as integer
            if (px ≥ fx and px < fx + fw and py ≥ fy and py < fy + fh) then
              set chosen to s
              exit repeat
            end if
          end repeat
          return chosen
        end screenForPoint

        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            -- small settle after potential fullscreen exit
            delay 0.06

            -- resolve target window
            set targetWin to missing value
            try
              set targetWin to value of attribute "AXFocusedWindow" of frontProc
            end try
            if targetWin is missing value then
              set stdWins to every window of frontProc whose subrole is "AXStandardWindow"
              if stdWins is not {} then set targetWin to item 1 of stdWins
            end if
            if targetWin is missing value then
              if (count of windows of frontProc) > 0 then set targetWin to window 1 of frontProc
            end if
            if targetWin is missing value then error "No usable window."

            -- window center in AX (global, top-left origin)
            set {wx, wy} to value of attribute "AXPosition" of targetWin
            set {ww, wh} to value of attribute "AXSize" of targetWin
            set cx to wx + (ww / 2)
            set cyTop to wy + (wh / 2)

            -- convert center Y to AppKit bottom-left using GLOBAL union height
            set gMaxY to my unionMaxY()
            set cyBottom to gMaxY - cyTop

            -- pick screen containing window center (global coords)
            set scr to my screenForPoint(cx, cyBottom)

            -- visible frame (global AppKit coords)
            set v1 to scr's visibleFrame()
            delay 0.02
            set v2 to scr's visibleFrame()
            if ((current application's NSEqualRects(v1, v2)) as boolean) is false then set v1 to v2

            set vX to (current application's NSMinX(v1)) as integer
            set vY to (current application's NSMinY(v1)) as integer
            set vW to (current application's NSWidth(v1)) as integer
            set vH to (current application's NSHeight(v1)) as integer

            -- convert AppKit -> AX Y using GLOBAL union height
            set axTopY to gMaxY - (vY + vH)

            -- bottom half geometry (integer math)
            set halfH to (vH div 2)
            set newY to axTopY + halfH
            set newH to vH - halfH

            -- apply
            set canResize to true
            try
              set canResize to (value of attribute "AXResizable" of targetWin)
            end try
            if canResize then
              set position of targetWin to {vX, newY}
              set size of targetWin to {vW, newH}
            end if

          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript','-e',script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (bottom half): {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def bottom_half_window_win():
    apply_window_fraction_win(0.0, 0.5, 1.0, 0.5)


# Tool 11 - Top Left 1/4 Screen
def top_left_quadrant_window():
    run = execute_os(top_left_quadrant_window_mac, top_left_quadrant_window_win)
    return run()


def top_left_quadrant_window_mac():
    """
    Move the focused window to the top-left quadrant of the *current* display,
    robust across multi-monitor setups (any arrangement, Dock/Menu bar, Spaces).
    """
    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions

        on unionMaxY()
          set maxY to 0
          set screens to current application's NSScreen's screens()
          repeat with s in screens
            set f to s's frame()
            set yMax to (current application's NSMaxY(f)) as integer
            if yMax > maxY then set maxY to yMax
          end repeat
          return maxY
        end unionMaxY

        on screenForPoint(px, py)
          set screens to current application's NSScreen's screens()
          set chosen to current application's NSScreen's mainScreen()
          repeat with s in screens
            set f to s's frame()
            set fx to (current application's NSMinX(f)) as integer
            set fy to (current application's NSMinY(f)) as integer
            set fw to (current application's NSWidth(f)) as integer
            set fh to (current application's NSHeight(f)) as integer
            if (px ≥ fx and px ≤ fx + fw and py ≥ fy and py ≤ fy + fh) then
              set chosen to s
              exit repeat
            end if
          end repeat
          return chosen
        end screenForPoint

        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            -- Resolve a usable target window
            set targetWin to missing value
            try
              set targetWin to value of attribute "AXFocusedWindow" of frontProc
            end try
            if targetWin is missing value then
              set stdWins to every window of frontProc whose subrole is "AXStandardWindow"
              if stdWins is not {} then set targetWin to item 1 of stdWins
            end if
            if targetWin is missing value then
              if (count of windows of frontProc) > 0 then set targetWin to window 1 of frontProc
            end if
            if targetWin is missing value then error "No usable window."

            -- AX geometry (global, top-left origin)
            set {wx, wy} to value of attribute "AXPosition" of targetWin
            set {ww, wh} to value of attribute "AXSize" of targetWin
            set cx to wx + (ww / 2)
            set cy to wy + (wh / 2)

            -- Choose the *actual* screen containing the window center (global coords)
            set scr to my screenForPoint(cx, cy)

            -- Visible frame on that screen (global AppKit coords, bottom-left origin)
            set vFrame to scr's visibleFrame()
            set vX to (current application's NSMinX(vFrame)) as integer
            set vY to (current application's NSMinY(vFrame)) as integer
            set vW to (current application's NSWidth(vFrame)) as integer
            set vH to (current application's NSHeight(vFrame)) as integer

            -- Convert AppKit -> AX Y using GLOBAL union height
            set globalMaxY to my unionMaxY()
            set axYTop to globalMaxY - (vY + vH)

            -- Top-left QUADRANT sizing (integer division avoids banker's rounding quirks)
            set halfW to (vW div 2)
            set halfH to (vH div 2)

            -- Resize/move if allowed
            set canResize to true
            try
              set canResize to (value of attribute "AXResizable" of targetWin)
            end try
            if canResize then
              set position of targetWin to {vX, axYTop}
              set size of targetWin to {halfW, halfH}
            end if

          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (top-left quadrant): {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def top_left_quadrant_window_win():
    apply_window_fraction_win(0.0, 0.0, 0.5, 0.5)


# Tool 12 - Top Right 1/4 Screen
def top_right_quadrant_window():
    run = execute_os(top_right_quadrant_window_mac, top_right_quadrant_window_win)
    return run()


def top_right_quadrant_window_mac():
    """
    Move the focused window to the top-right quadrant of the *current* display,
    robust across multi-monitor setups (any arrangement, Dock/Menu bar, Spaces).
    """
    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)
    try:
        script = r'''
        use framework "AppKit"
        use scripting additions

        on unionMaxY()
          set maxY to 0
          set screens to current application's NSScreen's screens()
          repeat with s in screens
            set f to s's frame()
            set yMax to (current application's NSMaxY(f)) as integer
            if yMax > maxY then set maxY to yMax
          end repeat
          return maxY
        end unionMaxY

        on screenForPoint(px, py)
          set screens to current application's NSScreen's screens()
          set chosen to current application's NSScreen's mainScreen()
          repeat with s in screens
            set f to s's frame()
            set fx to (current application's NSMinX(f)) as integer
            set fy to (current application's NSMinY(f)) as integer
            set fw to (current application's NSWidth(f)) as integer
            set fh to (current application's NSHeight(f)) as integer
            if (px ≥ fx and px ≤ fx + fw and py ≥ fy and py ≤ fy + fh) then
              set chosen to s
              exit repeat
            end if
          end repeat
          return chosen
        end screenForPoint

        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            -- Resolve a usable target window
            set targetWin to missing value
            try
              set targetWin to value of attribute "AXFocusedWindow" of frontProc
            end try
            if targetWin is missing value then
              set stdWins to every window of frontProc whose subrole is "AXStandardWindow"
              if stdWins is not {} then set targetWin to item 1 of stdWins
            end if
            if targetWin is missing value then
              if (count of windows of frontProc) > 0 then set targetWin to window 1 of frontProc
            end if
            if targetWin is missing value then error "No usable window."

            -- AX geometry (global, top-left origin)
            set {wx, wy} to value of attribute "AXPosition" of targetWin
            set {ww, wh} to value of attribute "AXSize" of targetWin
            set cx to wx + (ww / 2)
            set cy to wy + (wh / 2)

            -- Choose the *actual* screen containing the window center (global coords)
            set scr to my screenForPoint(cx, cy)

            -- Visible frame on that screen (global AppKit coords, bottom-left origin)
            set vFrame to scr's visibleFrame()
            set vX to (current application's NSMinX(vFrame)) as integer
            set vY to (current application's NSMinY(vFrame)) as integer
            set vW to (current application's NSWidth(vFrame)) as integer
            set vH to (current application's NSHeight(vFrame)) as integer

            -- Convert AppKit -> AX Y using GLOBAL union height
            set globalMaxY to my unionMaxY()
            set axYTop to globalMaxY - (vY + vH)

            -- Top-right QUADRANT sizing (integer division avoids banker's rounding quirks)
            set halfW to (vW div 2)
            set halfH to (vH div 2)

            -- Resize/move if allowed
            set canResize to true
            try
              set canResize to (value of attribute "AXResizable" of targetWin)
            end try
            if canResize then
              set position of targetWin to {vX + halfW, axYTop}
              set size of targetWin to {vW - halfW, halfH}
            end if

          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (top-right quadrant): {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def top_right_quadrant_window_win():
    apply_window_fraction_win(0.5, 0.0, 0.5, 0.5)


# Tool 13 - Bottom Left 1/4 Screen
def bottom_left_quadrant_window():
    run = execute_os(bottom_left_quadrant_window_mac, bottom_left_quadrant_window_win)
    return run()


def bottom_left_quadrant_window_mac():
    """
    Move the focused window to the bottom-left quadrant of the *current* display,
    robust across multi-monitor setups (any arrangement, Dock/Menu bar, Spaces).
    """
    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions

        -- Global union max Y across all displays (for robust AX/AppKit Y conversion)
        on unionMaxY()
          set maxY to 0
          repeat with s in (current application's NSScreen's screens())
            set f to s's frame()
            set yMax to (current application's NSMaxY(f)) as integer
            if yMax > maxY then set maxY to yMax
          end repeat
          return maxY
        end unionMaxY

        -- Return the NSScreen that contains a point (px, py) in Cocoa (global bottom-left) coords
        on screenForPoint(px, py)
          set chosen to current application's NSScreen's mainScreen()
          repeat with sc in (current application's NSScreen's screens())
            set fr to sc's frame()
            set sx to (current application's NSMinX(fr)) as integer
            set sy to (current application's NSMinY(fr)) as integer
            set sw to (current application's NSWidth(fr)) as integer
            set sh to (current application's NSHeight(fr)) as integer
            if (px ≥ sx and px < sx + sw and py ≥ sy and py < sy + sh) then
              set chosen to sc
              exit repeat
            end if
          end repeat
          return chosen
        end screenForPoint

        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            -- Small settle to avoid stale visibleFrame after state changes
            delay 0.06

            -- Choose the window (focused -> standard -> window 1)
            set targetWin to missing value
            try
              set targetWin to value of attribute "AXFocusedWindow" of frontProc
            end try
            if targetWin is missing value then
              set stdWins to every window of frontProc whose subrole is "AXStandardWindow"
              if stdWins is not {} then set targetWin to item 1 of stdWins
            end if
            if targetWin is missing value then
              if (count of windows of frontProc) > 0 then set targetWin to window 1 of frontProc
            end if
            if targetWin is missing value then error number -128

            -- Window center (AX coords = global top-left origin)
            set {wx, wy} to value of attribute "AXPosition" of targetWin
            set {ww, wh} to value of attribute "AXSize" of targetWin
            set cx_top to (wx + ww / 2)
            set cy_top to (wy + wh / 2)

            -- Convert that center Y to Cocoa bottom-left using the GLOBAL union height
            set gMaxY to my unionMaxY()
            set cy_bottom to (gMaxY - cy_top)

            -- Pick the screen containing that point (global coords)
            set sc to my screenForPoint(cx_top, cy_bottom)

            -- Read visibleFrame; re-read once for stability
            set v1 to sc's visibleFrame()
            delay 0.02
            set v2 to sc's visibleFrame()
            if ((current application's NSEqualRects(v1, v2)) as boolean) is false then set v1 to v2

            -- Extract rects (Cocoa bottom-left), then convert Y to AX top-left using GLOBAL union height
            set visX to (current application's NSMinX(v1)) as integer
            set visW to (current application's NSWidth(v1)) as integer
            set visYBottom to (current application's NSMinY(v1)) as integer
            set visH to (current application's NSHeight(v1)) as integer

            set axTopY to gMaxY - (visYBottom + visH)

            -- Bottom-left quadrant target (integer division avoids banker's rounding)
            set halfW to (visW div 2)
            set halfH to (visH div 2)
            set xTarget to visX
            set yTarget to (axTopY + halfH)
            set wTarget to halfW
            set hTarget to (visH - halfH)

            -- Clamp so the bottom never crosses the visible bottom (tiny guard)
            set guard to 4
            set visibleBottomTopY to (axTopY + visH)
            set maxH to (visibleBottomTopY - yTarget - guard)
            if hTarget > maxH then set hTarget to maxH
            if hTarget < 100 then set hTarget to 100

            -- Apply
            set canResize to true
            try
              set canResize to (value of attribute "AXResizable" of targetWin)
            end try
            if canResize then
              set position of targetWin to {xTarget, yTarget}
              set size of targetWin to {wTarget, hTarget}
            end if

          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (bottom-left quadrant): {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def bottom_left_quadrant_window_win():
    apply_window_fraction_win(0.0, 0.5, 0.5, 0.5)


# Tool 14 - Bottom Right 1/4 Screen
def bottom_right_quadrant_window():
    run = execute_os(bottom_right_quadrant_window_mac, bottom_right_quadrant_window_win)
    return run()


def bottom_right_quadrant_window_mac():
    """
    Move the focused window to the bottom-right quadrant of the *current* display,
    robust across multi-monitor setups (any arrangement, Dock/Menu bar, Spaces).
    """
    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions

        -- Global union max Y across all displays (for robust AX/AppKit Y conversion)
        on unionMaxY()
          set maxY to 0
          repeat with s in (current application's NSScreen's screens())
            set f to s's frame()
            set yMax to (current application's NSMaxY(f)) as integer
            if yMax > maxY then set maxY to yMax
          end repeat
          return maxY
        end unionMaxY

        -- Return the NSScreen that contains a point (px, py) in Cocoa (global bottom-left) coords
        on screenForPoint(px, py)
          set chosen to current application's NSScreen's mainScreen()
          repeat with sc in (current application's NSScreen's screens())
            set fr to sc's frame()
            set sx to (current application's NSMinX(fr)) as integer
            set sy to (current application's NSMinY(fr)) as integer
            set sw to (current application's NSWidth(fr)) as integer
            set sh to (current application's NSHeight(fr)) as integer
            if (px ≥ sx and px < sx + sw and py ≥ sy and py < sy + sh) then
              set chosen to sc
              exit repeat
            end if
          end repeat
          return chosen
        end screenForPoint

        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            -- Settle to avoid stale visibleFrame after state changes
            delay 0.06

            -- Pick target window (focused -> standard -> any)
            set targetWin to missing value
            try
              set targetWin to value of attribute "AXFocusedWindow" of frontProc
            end try
            if targetWin is missing value then
              set stdWins to every window of frontProc whose subrole is "AXStandardWindow"
              if stdWins is not {} then set targetWin to item 1 of stdWins
            end if
            if targetWin is missing value then
              if (count of windows of frontProc) > 0 then set targetWin to window 1 of frontProc
            end if
            if targetWin is missing value then error number -128

            -- Window center (AX uses global top-left origin)
            set {wx, wy} to value of attribute "AXPosition" of targetWin
            set {ww, wh} to value of attribute "AXSize" of targetWin
            set cx_top to (wx + ww / 2)
            set cy_top to (wy + wh / 2)

            -- Convert center Y to Cocoa bottom-left using GLOBAL union height
            set gMaxY to my unionMaxY()
            set cy_bottom to (gMaxY - cy_top)

            -- Choose the screen containing that point (global coords)
            set sc to my screenForPoint(cx_top, cy_bottom)

            -- Read visibleFrame; re-read once for stability
            set v1 to sc's visibleFrame()
            delay 0.02
            set v2 to sc's visibleFrame()
            if ((current application's NSEqualRects(v1, v2)) as boolean) is false then set v1 to v2

            -- Extract rects (Cocoa bottom-left), then convert Y to AX top-left with GLOBAL union height
            set visX to (current application's NSMinX(v1)) as integer
            set visW to (current application's NSWidth(v1)) as integer
            set visYBottom to (current application's NSMinY(v1)) as integer
            set visH to (current application's NSHeight(v1)) as integer

            set axTopY to gMaxY - (visYBottom + visH)

            -- Bottom-right quadrant (integer division avoids banker's rounding)
            set halfW to (visW div 2)
            set halfH to (visH div 2)
            set xTarget to (visX + halfW)
            set yTarget to (axTopY + halfH)
            set wTarget to (visW - halfW)
            set hTarget to (visH - halfH)

            -- Guards & clamps (prevent overshoot of visible right/bottom)
            set guardBottom to 4
            set guardRight to 2
            set visibleRightX to (visX + visW)
            set visibleBottomTopY to (axTopY + visH)

            set maxW to (visibleRightX - xTarget - guardRight)
            if wTarget > maxW then set wTarget to maxW
            if wTarget < 100 then set wTarget to 100

            set maxH to (visibleBottomTopY - yTarget - guardBottom)
            if hTarget > maxH then set hTarget to maxH
            if hTarget < 100 then set hTarget to 100

            -- Apply
            set canResize to true
            try
              set canResize to (value of attribute "AXResizable" of targetWin)
            end try
            if canResize then
              set position of targetWin to {xTarget, yTarget}
              set size of targetWin to {wTarget, hTarget}
            end if

          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (bottom-right quadrant): {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def bottom_right_quadrant_window_win():
    apply_window_fraction_win(0.5, 0.5, 0.5, 0.5)


# Tool 15 - Left 2/3 Screen
def left_two_thirds_window():
    run = execute_os(left_two_thirds_window_mac, left_two_thirds_window_win)
    return run()


def left_two_thirds_window_mac():
    """
    Move the focused window to the left two-thirds of the *current* display,
    robust across multi-monitor setups (any arrangement, Dock/Menu bar, Spaces).
    """
    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions

        on unionMaxY()
          set maxY to 0
          set screens to current application's NSScreen's screens()
          repeat with s in screens
            set f to s's frame()
            set yMax to (current application's NSMaxY(f)) as integer
            if yMax > maxY then set maxY to yMax
          end repeat
          return maxY
        end unionMaxY

        on screenForPoint(px, py)
          set screens to current application's NSScreen's screens()
          set chosen to current application's NSScreen's mainScreen()
          repeat with s in screens
            set f to s's frame()
            set fx to (current application's NSMinX(f)) as integer
            set fy to (current application's NSMinY(f)) as integer
            set fw to (current application's NSWidth(f)) as integer
            set fh to (current application's NSHeight(f)) as integer
            if (px ≥ fx and px ≤ fx + fw and py ≥ fy and py ≤ fy + fh) then
              set chosen to s
              exit repeat
            end if
          end repeat
          return chosen
        end screenForPoint

        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            -- Resolve a usable target window
            set targetWin to missing value
            try
              set targetWin to value of attribute "AXFocusedWindow" of frontProc
            end try
            if targetWin is missing value then
              set stdWins to every window of frontProc whose subrole is "AXStandardWindow"
              if stdWins is not {} then set targetWin to item 1 of stdWins
            end if
            if targetWin is missing value then
              if (count of windows of frontProc) > 0 then set targetWin to window 1 of frontProc
            end if
            if targetWin is missing value then error "No usable window."

            -- AX geometry (global, top-left origin)
            set {wx, wy} to value of attribute "AXPosition" of targetWin
            set {ww, wh} to value of attribute "AXSize" of targetWin
            set cx to wx + (ww / 2)
            set cy to wy + (wh / 2)

            -- Choose the *actual* screen containing the window center (global coords)
            set scr to my screenForPoint(cx, cy)

            -- Visible frame on that screen (global AppKit coords, bottom-left origin)
            set vFrame to scr's visibleFrame()
            set vX to (current application's NSMinX(vFrame)) as integer
            set vY to (current application's NSMinY(vFrame)) as integer
            set vW to (current application's NSWidth(vFrame)) as integer
            set vH to (current application's NSHeight(vFrame)) as integer

            -- Convert AppKit -> AX Y using GLOBAL union height
            set globalMaxY to my unionMaxY()
            set axYTop to globalMaxY - (vY + vH)

            -- Left TWO-THIRDS sizing (rounded so thirds tile perfectly)
            set b2 to round (vW * 2.0 / 3.0)
            set x0 to vX
            set x1 to vX + b2
            set sliceW to (x1 - x0)

            -- Resize/move if allowed
            set canResize to true
            try
              set canResize to (value of attribute "AXResizable" of targetWin)
            end try
            if canResize then
              set position of targetWin to {x0, axYTop}
              set size of targetWin to {sliceW, vH}
            end if

          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript','-e',script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (left 2/3): {e}"); return False
    except Exception as e:
        print(f"Unexpected Error: {e}"); return False


def left_two_thirds_window_win():
    apply_window_fraction_win(0.0, 0.0, 2.0/3.0, 1.0)


# Tool 16 - Right 2/3 Screen
def right_two_thirds_window():
    run = execute_os(right_two_thirds_window_mac, right_two_thirds_window_win)
    return run()


def right_two_thirds_window_mac():
    """
    Move the focused window to the right two-thirds of the *current* display,
    robust across multi-monitor setups (any arrangement, Dock/Menu bar, Spaces).
    """
    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)
    try:
        script = r'''
        use framework "AppKit"
        use scripting additions

        on unionMaxY()
          set maxY to 0
          set screens to current application's NSScreen's screens()
          repeat with s in screens
            set f to s's frame()
            set yMax to (current application's NSMaxY(f)) as integer
            if yMax > maxY then set maxY to yMax
          end repeat
          return maxY
        end unionMaxY

        on screenForPoint(px, py)
          set screens to current application's NSScreen's screens()
          set chosen to current application's NSScreen's mainScreen()
          repeat with s in screens
            set f to s's frame()
            set fx to (current application's NSMinX(f)) as integer
            set fy to (current application's NSMinY(f)) as integer
            set fw to (current application's NSWidth(f)) as integer
            set fh to (current application's NSHeight(f)) as integer
            if (px ≥ fx and px ≤ fx + fw and py ≥ fy and py ≤ fy + fh) then
              set chosen to s
              exit repeat
            end if
          end repeat
          return chosen
        end screenForPoint

        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            -- Resolve a usable target window
            set targetWin to missing value
            try
              set targetWin to value of attribute "AXFocusedWindow" of frontProc
            end try
            if targetWin is missing value then
              set stdWins to every window of frontProc whose subrole is "AXStandardWindow"
              if stdWins is not {} then set targetWin to item 1 of stdWins
            end if
            if targetWin is missing value then
              if (count of windows of frontProc) > 0 then set targetWin to window 1 of frontProc
            end if
            if targetWin is missing value then error "No usable window."

            -- AX geometry (global, top-left origin)
            set {wx, wy} to value of attribute "AXPosition" of targetWin
            set {ww, wh} to value of attribute "AXSize" of targetWin
            set cx to wx + (ww / 2)
            set cy to wy + (wh / 2)

            -- Choose the *actual* screen containing the window center (global coords)
            set scr to my screenForPoint(cx, cy)

            -- Visible frame on that screen (global AppKit coords, bottom-left origin)
            set vFrame to scr's visibleFrame()
            set vX to (current application's NSMinX(vFrame)) as integer
            set vY to (current application's NSMinY(vFrame)) as integer
            set vW to (current application's NSWidth(vFrame)) as integer
            set vH to (current application's NSHeight(vFrame)) as integer

            -- Convert AppKit -> AX Y using GLOBAL union height
            set globalMaxY to my unionMaxY()
            set axYTop to globalMaxY - (vY + vH)

            -- Right TWO-THIRDS sizing (rounded so thirds tile perfectly)
            set b1 to round (vW * 1.0 / 3.0)
            set x0 to vX + b1
            set x1 to vX + vW
            set sliceW to (x1 - x0)

            -- Resize/move if allowed
            set canResize to true
            try
              set canResize to (value of attribute "AXResizable" of targetWin)
            end try
            if canResize then
              set position of targetWin to {x0, axYTop}
              set size of targetWin to {sliceW, vH}
            end if

          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript','-e',script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (right 2/3): {e}"); return False
    except Exception as e:
        print(f"Unexpected Error: {e}"); return False


def right_two_thirds_window_win():
    apply_window_fraction_win(1.0/3.0, 0.0, 2.0/3.0, 1.0)
