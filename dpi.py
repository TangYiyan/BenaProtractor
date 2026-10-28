"""Windows下的DPI设置策略，通过SetProcessDpiAwareness实现，默认采用96DPI方案，临时解决方案"""
import ctypes
import sys


def enable_dpi_awareness():
    """在Tk创建前进行系统DPI适应"""
    if sys.platform != 'win32':
        return
    try:
        set_awareness = ctypes.windll.shcore.SetProcessDpiAwareness
        set_awareness.argtypes = [ctypes.c_int]
        set_awareness.restype = ctypes.c_long
        # PROCESS_SYSTEM_DPI_AWARE. 后续版本再改为采用manifest声明dpi的方式来实现自适应
        # 传入值为1时启用系统DPI感知。此应用不会根据 DPI 变化进行缩放。它会查询一次 DPI，并在应用的整个生命周期内使用该值
        set_awareness(1)
    except (AttributeError, OSError):
        # Windows versions without shcore expose the system-aware API in user32.
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


class DpiScale:
    """对显示逻辑中通过固定像素量规定的显示内容进行缩放调整"""
    def __init__(self, widget):
        self.factor = round(widget.winfo_fpixels('1i')) / 96

    def __call__(self, *values):
        scaled = tuple(round(value * self.factor) for value in values)
        return scaled[0] if len(scaled) == 1 else scaled
