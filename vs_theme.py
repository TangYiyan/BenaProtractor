"""Light/dark Visual Studio 2022 inspired palettes and application controls."""
import sys
import tkinter as tk
from tkinter import ttk, font

THEMES = {
    'light': {
        'bg': '#f5f5f5', 'panel': '#eeeeF2', 'editor': '#ffffff',
        'border': '#cccedb', 'text': '#1e1e1e', 'muted': '#6d6d6d',
        'accent': '#007acc', 'blue': '#0066bf', 'purple': '#6f42a1',
        'orange': '#a31515', 'green': '#098658', 'red': '#c42b1c',
        'hover': '#dfe7f3', 'selection': '#c9def5', 'selected_text': '#1e1e1e',
        'status': '#007acc', 'field': '#ffffff', 'button': '#f5f5f5', 'scroll': '#b6b6bd',
        'key': '#0451a5', 'string': '#a31515', 'number': '#098658', 'keyword': '#0000ff',
        'type': '#267f99', 'bracket0': '#5b5b5b', 'bracket1': '#795e26', 'bracket2': '#6f42a1',
    },
    'dark': {
        'bg': '#252526', 'panel': '#2d2d30', 'editor': '#1e1e1e',
        'border': '#3f3f46', 'text': '#dcdcdc', 'muted': '#a6a6a6',
        'accent': '#007acc', 'blue': '#80bfff', 'purple': '#c586c0',
        'orange': '#ce9178', 'green': '#b5cea8', 'red': '#f48771',
        'hover': '#3e3e40', 'selection': '#094771', 'selected_text': '#ffffff',
        'status': '#007acc', 'field': '#333337', 'button': '#333337', 'scroll': '#686868',
        'key': '#9cdcfe', 'string': '#ce9178', 'number': '#b5cea8', 'keyword': '#569cd6',
        'type': '#4ec9b0', 'bracket0': '#dcdcdc', 'bracket1': '#d7ba7d', 'bracket2': '#c586c0',
    },
}
COLORS = dict(THEMES['light'])


def install_theme(root, name='light', ui_size=10):
    COLORS.update(THEMES[name])
    p = COLORS
    style = ttk.Style(root)
    if 'bena_vs2022' not in style.theme_names():
        style.theme_create('bena_vs2022', parent='clam')
    style.theme_use('bena_vs2022')
    ui_font = font.nametofont('TkDefaultFont')
    ui_font.configure(family='Microsoft YaHei UI', size=ui_size)
    font.nametofont('TkMenuFont').configure(family='Microsoft YaHei UI', size=ui_size)
    font.nametofont('TkTextFont').configure(family='Microsoft YaHei UI', size=ui_size)
    row_height = max(24, ui_font.metrics('linespace') + 6)
    style.configure('.', background=p['bg'], foreground=p['text'], bordercolor=p['border'],
                    lightcolor=p['border'], darkcolor=p['border'], focuscolor=p['accent'], font=('Microsoft YaHei UI', ui_size))
    style.configure('TFrame', background=p['bg'])
    style.configure('Chrome.TFrame', background=p['panel'])
    style.configure('Editor.TFrame', background=p['editor'])
    style.configure('TLabel', padding=0, background=p['bg'], foreground=p['text'])
    style.configure('Chrome.TLabel', background=p['panel'])
    style.configure('Muted.TLabel', foreground=p['muted'])
    style.configure('Dock.TLabel', background=p['panel'], font=('Microsoft YaHei UI', ui_size, 'bold'), padding=(8, 4))
    style.configure('TButton', padding=(9, 3), background=p['button'], borderwidth=1, relief='flat')
    style.map('TButton', background=[('pressed', p['selection']), ('active', p['hover'])],
              foreground=[('disabled', p['muted'])], bordercolor=[('focus', p['accent'])])
    style.configure('Tool.TButton', padding=(6, 3), background=p['panel'], borderwidth=0)
    style.configure('Primary.TButton', background=p['accent'], foreground='white', bordercolor=p['accent'])
    style.map('Primary.TButton', background=[('active', '#1c97ea'), ('pressed', '#005a9e')])
    style.configure('TEntry', fieldbackground=p['field'], foreground=p['text'], insertcolor=p['text'], padding=(6, 3))
    style.configure('TCombobox', fieldbackground=p['field'], foreground=p['text'], padding=(5, 3), arrowsize=12)
    style.map('TCombobox', fieldbackground=[('readonly', p['field'])], foreground=[('readonly', p['text'])],
              selectbackground=[('readonly', p['field'])], selectforeground=[('readonly', p['text'])])
    style.configure('TSpinbox', fieldbackground=p['field'], foreground=p['text'], padding=(5, 3), arrowsize=11)
    style.configure('TCheckbutton', padding=(0, 4), indicatorbackground=p['field'])
    style.map('TCheckbutton', background=[('active', p['bg'])], indicatorbackground=[('selected', p['accent'])])
    style.configure('TNotebook', background=p['panel'], borderwidth=0, tabmargins=0)
    style.configure('TNotebook.Tab', background=p['panel'], foreground=p['muted'], padding=(13, 6),
                    borderwidth=0, lightcolor=p['panel'], darkcolor=p['panel'])
    style.map('TNotebook.Tab', background=[('selected', p['editor']), ('active', p['hover'])],
              foreground=[('disabled', p['muted']), ('selected', p['text'])], padding=[('selected', (13, 6))],
              lightcolor=[('selected', p['accent'])], darkcolor=[('selected', p['accent'])])
    style.configure('Treeview', background=p['bg'], fieldbackground=p['bg'], foreground=p['text'], rowheight=row_height, borderwidth=0, indent=16)
    style.map('Treeview', background=[('selected', p['selection'])], foreground=[('selected', p['selected_text'])])
    style.configure('Treeview.Heading', background=p['panel'], foreground=p['text'], relief='flat', padding=(6, 4))
    style.configure('TPanedwindow', background=p['panel'], sashwidth=4)
    style.configure('TSeparator', background=p['border'])
    for orientation in ('Horizontal', 'Vertical'):
        control = orientation + '.TScrollbar'
        style.layout(control, [(f'{orientation}.Scrollbar.trough', {'sticky': 'nswe', 'children': [
            (f'{orientation}.Scrollbar.thumb', {'sticky': 'nswe', 'expand': 1})]})])
        style.configure(control, background=p['scroll'], troughcolor=p['bg'], borderwidth=0, arrowsize=11,
                        lightcolor=p['scroll'], darkcolor=p['scroll'])
        style.map(control, background=[('active', p['muted']), ('!active', p['scroll'])])
    style.configure('Horizontal.TProgressbar', background=p['accent'], troughcolor=p['panel'],
                    lightcolor=p['accent'], darkcolor=p['accent'], borderwidth=0, thickness=2)
    root.option_add('*TCombobox*Listbox.background', p['field'])
    root.option_add('*TCombobox*Listbox.foreground', p['text'])
    root.option_add('*TCombobox*Listbox.selectBackground', p['selection'])
    root.option_add('*TCombobox*Listbox.font', 'TkTextFont')
    root.configure(bg=p['panel'])
    style_titlebar(root, name)
    return style


def style_titlebar(window, theme):
    if sys.platform != 'win32':
        return
    try:
        import ctypes
        from ctypes import wintypes
        window.update_idletasks()
        user32, dwm = ctypes.windll.user32, ctypes.windll.dwmapi
        user32.GetParent.argtypes = [wintypes.HWND]
        user32.GetParent.restype = wintypes.HWND
        dwm.DwmSetWindowAttribute.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
        handle = user32.GetParent(window.winfo_id())
        enabled = ctypes.c_int(theme == 'dark')
        dwm.DwmSetWindowAttribute(handle, 20, ctypes.byref(enabled), ctypes.sizeof(enabled))
    except (AttributeError, OSError, tk.TclError):
        pass


def menu(master):
    return tk.Menu(master, tearoff=False, background=COLORS['panel'], foreground=COLORS['text'],
                   activebackground=COLORS['selection'], activeforeground=COLORS['selected_text'], borderwidth=1, relief='flat')
