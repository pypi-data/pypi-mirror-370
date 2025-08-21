import psutil
import win32gui
import win32con
import win32process
import win32api

# 마지막 모니터의 작업 영역 (작업표시줄 제외)
def get_last_monitor_work_area():
    monitors = win32api.EnumDisplayMonitors()
    last_monitor = monitors[-1][0]
    info = win32api.GetMonitorInfo(last_monitor)
    return info['Work']  # (left, top, right, bottom)

# 마지막 모니터의 전체 해상도 (작업표시줄 포함)
def get_last_monitor_resolution():
    monitors = win32api.EnumDisplayMonitors()
    last_monitor = monitors[-1][0]
    info = win32api.GetMonitorInfo(last_monitor)
    mon_left, mon_top, mon_right, mon_bottom = info['Monitor']
    return mon_right - mon_left, mon_bottom - mon_top

# 실제 표시되는 콘솔 창의 HWND 반환
def get_real_visible_hwnd_by_pid(pid):
    hwnds = []
    def callback(hwnd, hwnds):
        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        if found_pid == pid and win32gui.IsWindowVisible(hwnd):
            if class_name == "PseudoConsoleWindow":
                parent = win32gui.GetParent(hwnd)
                if parent and win32gui.IsWindowVisible(parent):
                    hwnds.append(parent)
            else:
                hwnds.append(hwnd)
        return True
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else None

# 창 위치 이동 (프레임 보정 포함)
def set_window_pos(hwnd, x, y, width, height, is_4k=False):
    if hwnd and win32gui.IsWindow(hwnd):
        # 마진 조정
        if is_4k:
            horizontal_margin = -12
            vertical_margin = -14
        else:
            horizontal_margin = -6
            vertical_margin = -8

        x += horizontal_margin
        y += vertical_margin
        width -= horizontal_margin * 2
        height -= vertical_margin

        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetWindowPos(hwnd, None, x, y, width, height,
                              win32con.SWP_NOZORDER | win32con.SWP_SHOWWINDOW)

# 전체 정렬 로직
def adjust_windows_by_recent_procs():
    # 작업 가능한 영역 (창 위치 기준)
    left, top, right, bottom = get_last_monitor_work_area()
    screen_w = right - left
    screen_h = bottom - top

    # 전체 해상도 기준 4K 판별
    mon_w, mon_h = get_last_monitor_resolution()
    is_4k = mon_w * mon_h >= 8000000
    is_portrait = screen_h > screen_w

    left_w = screen_w // 2
    right_w = screen_w - left_w
    top_h = screen_h // 2
    bottom_h = screen_h - top_h

    # 위치 설정
    if is_4k:
        if is_portrait:
            positions = [
                (left, top, screen_w, top_h),
                (left, top, left_w, top_h),
                (left + left_w, top, right_w, top_h),
                (left, top + top_h, screen_w, bottom_h),
                (left, top + top_h, left_w, bottom_h),
                (left + left_w, top + top_h, right_w, bottom_h),
            ]
        else:
            positions = [
                (left, top, left_w, screen_h),
                (left, top, left_w, top_h),
                (left, top + top_h, left_w, bottom_h),
                (left + left_w, top, right_w, screen_h),
                (left + left_w, top, right_w, top_h),
                (left + left_w, top + top_h, right_w, bottom_h),
            ]
    else:
        positions = [
                (left, top, left_w, screen_h),
                (left, top, left_w, top_h),
                (left, top + top_h, left_w, bottom_h),
                (left + left_w, top, right_w, screen_h),
                (left + left_w, top, right_w, top_h),
                (left + left_w, top + top_h, right_w, bottom_h),
        ]

    # 현재 Python을 실행한 cmd.exe 제외
    parent_pid = psutil.Process().ppid()

    procs = [
        p for p in psutil.process_iter(['pid', 'name', 'create_time'])
        if p.info['name'] == 'cmd.exe' and p.info['pid'] != parent_pid
    ]

    procs.sort(key=lambda p: p.info['create_time'], reverse=True)
    selected_procs = procs[:6]
    selected_procs.reverse()

    for i, proc in enumerate(selected_procs):
        hwnd = get_real_visible_hwnd_by_pid(proc.info['pid'])
        if hwnd:
            x, y, w, h = positions[i]
            print(f"[INFO] Moving PID {proc.info['pid']} to ({x}, {y}, {w}, {h})")
            set_window_pos(hwnd, x, y, w, h, is_4k=is_4k)
        else:
            print(f"[WARN] No visible HWND found for PID {proc.info['pid']}")

# 실행
if __name__ == "__main__":
    adjust_windows_by_recent_procs()