"""IDE document surfaces with margin folding and selectable, read-only text."""
import json
import tkinter as tk
from tkinter import ttk, font
from document_model import reference_parts, json_spans, document_rows, default_folds
from vs_theme import COLORS, menu


class TextPane(ttk.Frame):
    def __init__(self, master, size=11, code=False):
        super().__init__(master, style='Editor.TFrame')
        self.size, self.code = size, code
        self.folds = {}
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        families = font.families(self)
        self.code_family = 'Cascadia Mono' if 'Cascadia Mono' in families else 'Consolas'
        self.family = self.code_family if code else 'Microsoft YaHei UI'
        self.reading_font = font.Font(self, family=self.family, size=size)
        self.number_font = font.Font(self, family=self.code_family, size=size)
        self.gutter = tk.Canvas(self, width=54, highlightthickness=0, borderwidth=0)
        self.gutter.grid(row=0, column=0, sticky='ns')
        self.text = tk.Text(self, width=1, height=1, wrap='none' if code else 'word',
                            font=self.reading_font, relief='flat', borderwidth=0, highlightthickness=0,
                            padx=10, pady=10, spacing1=1 if code else 2, spacing3=1 if code else 2,
                            state='disabled', cursor='xterm', undo=False)
        self.text.grid(row=0, column=1, sticky='nsew')
        self.vertical = ttk.Scrollbar(self, orient='vertical', command=self.text.yview)
        self.horizontal = ttk.Scrollbar(self, orient='horizontal', command=self.text.xview)
        self.vertical.grid(row=0, column=2, sticky='ns')
        self.horizontal.grid(row=1, column=0, columnspan=2, sticky='ew')
        self.text.configure(yscrollcommand=self.scrolled, xscrollcommand=self.horizontal.set)
        self.text.bind('<Configure>', lambda event: self.draw_margin())
        self.text.bind('<Expose>', lambda event: self.draw_margin())
        self.text.bind('<Control-a>', self.select_all)
        self.text.bind('<Button-3>', self.context_menu)
        self.apply_palette()

    def apply_palette(self):
        self.gutter.configure(bg=COLORS['editor'])
        self.text.configure(bg=COLORS['editor'], fg=COLORS['text'], insertbackground=COLORS['text'],
                            selectbackground=COLORS['selection'], selectforeground=COLORS['selected_text'])
        self.draw_margin()

    def scrolled(self, first, last):
        self.vertical.set(first, last)
        self.draw_margin()

    def draw_margin(self):
        if not hasattr(self, 'text'):
            return
        self.gutter.delete('all')
        digits = max(3, len(self.text.index('end-1c').split('.')[0]))
        margin = self.number_font.measure('0' * digits) + 30
        if int(self.gutter.cget('width')) != margin:
            self.gutter.configure(width=margin)
        number_x, fold_x = margin - 23, margin - 12
        index = self.text.index('@0,0')
        while True:
            geometry = self.text.dlineinfo(index)
            if geometry is None:
                break
            line = int(index.split('.')[0])
            y = geometry[1] + geometry[3] / 2
            self.gutter.create_text(number_x, y, text=str(line), anchor='e', fill=COLORS['muted'], font=self.number_font)
            if line in self.folds:
                path, collapsed = self.folds[line]
                tag = 'fold_' + str(line)
                self.gutter.create_rectangle(fold_x - 5, y - 5, fold_x + 5, y + 5, fill=COLORS['editor'], outline=COLORS['muted'], tags=(tag,))
                self.gutter.create_line(fold_x - 3, y, fold_x + 3, y, fill=COLORS['muted'], tags=(tag,))
                if collapsed:
                    self.gutter.create_line(fold_x, y - 3, fold_x, y + 3, fill=COLORS['muted'], tags=(tag,))
                self.gutter.tag_bind(tag, '<Button-1>', lambda event, p=path: self.toggle(p))
            index = self.text.index(f'{line + 1}.0')

    def set_size(self, size):
        self.size = size
        self.reading_font.configure(size=size)
        self.number_font.configure(size=size)
        for tag in self.text.tag_names():
            if tag.startswith('indent_'):
                depth = int(tag.split('_')[1])
                self.text.tag_configure(tag, lmargin2=self.reading_font.measure('    ' * depth))
        self.draw_margin()

    def set_text(self, text):
        self.folds.clear()
        self.text.configure(state='normal')
        self.text.delete('1.0', 'end')
        self.text.insert('1.0', text)
        self.text.configure(state='disabled')
        self.draw_margin()

    def select_all(self, event=None):
        self.text.tag_add('sel', '1.0', 'end-1c')
        return 'break'

    def copy_all(self):
        self.clipboard_clear()
        self.clipboard_append(self.text.get('1.0', 'end-1c'))

    def context_menu(self, event):
        popup = menu(self)
        popup.add_command(label='复制', command=lambda: self.text.event_generate('<<Copy>>'),
                          state='normal' if self.text.tag_ranges('sel') else 'disabled')
        popup.add_command(label='复制全文', command=self.copy_all)
        popup.add_separator()
        popup.add_command(label='全选', command=self.select_all, accelerator='Ctrl+A')
        try:
            popup.tk_popup(event.x_root, event.y_root)
        finally:
            popup.grab_release()

# 原始伪代码界面
class SourceView(TextPane):
    def __init__(self, master, size=11):
        super().__init__(master, size=size, code=True)

    def apply_palette(self):
        super().apply_palette()
        for kind in ('key', 'string', 'number', 'keyword', 'type', 'bracket0', 'bracket1', 'bracket2'):
            self.text.tag_configure(kind, foreground=COLORS[kind])

    def show(self, data):
        content = json.dumps(data, ensure_ascii=False, indent=4)
        self.set_text(content)
        for start, end, kind in json_spans(content):
            self.text.tag_add(kind, f'1.0+{start}c', f'1.0+{end}c')
        self.text.yview_moveto(0)
        self.text.xview_moveto(0)

# 伪代码中文翻译界面
class TranslationView(TextPane):
    def __init__(self, master, navigate, size=11):
        self.navigate = navigate
        self.document = None
        self.catalog = None
        self.collapsed = set()
        self.links = {}
        super().__init__(master, size=size)
        self.text.bind('<Motion>', self.hover_link)
        self.text.bind('<ButtonRelease-1>', self.activate_link)

    def apply_palette(self):
        super().apply_palette()
        for role, color in {'heading': COLORS['keyword'], 'section': COLORS['type'], 'condition': COLORS['purple'],
                            'description': COLORS['muted'], 'body': COLORS['text']}.items():
            self.text.tag_configure(role, foreground=color)
        for tag in self.links:
            self.text.tag_configure(tag, foreground=COLORS['blue'], underline=True)

    def show(self, document, catalog):
        self.document, self.catalog = document, catalog
        self.collapsed = default_folds(document)
        self.render()
        self.text.yview_moveto(0)

    def render(self):
        if self.document is None or self.catalog is None:
            return
        for tag in self.links:
            self.text.tag_delete(tag)
        self.links.clear()
        self.set_text('')
        self.text.configure(state='normal')
        for row in document_rows(self.document, self.collapsed):
            line = int(self.text.index('end-1c').split('.')[0])
            if row.foldable:
                self.folds[line] = (row.path, row.path in self.collapsed)
            indent = f'indent_{row.depth}'
            self.text.tag_configure(indent, lmargin2=self.reading_font.measure('    ' * row.depth))
            self.text.insert('end', '    ' * row.depth, (indent,))
            used = set()
            for label, target in reference_parts(row.text, self.catalog, row.explicit):
                tags = (row.role, indent)
                if target:
                    tag = f'reference_{len(self.links)}'
                    self.links[tag] = target
                    self.text.tag_configure(tag, foreground=COLORS['blue'], underline=True)
                    tags += (tag,)
                    used.add(target)
                self.text.insert('end', label, tags)
            for target in str(row.explicit or '').split(','):
                target = target.strip()
                entry = self.catalog.resolve(target)
                destination = entry.target if entry else target if target.startswith('prts.') else None
                if destination and destination not in used:
                    tag = f'reference_{len(self.links)}'
                    self.links[tag] = destination
                    self.text.tag_configure(tag, foreground=COLORS['blue'], underline=True)
                    self.text.insert('end', '  [' + (entry.name if entry else 'PRTS') + ']', (tag, indent))
                    used.add(destination)
            self.text.insert('end', '\n')
        self.text.configure(state='disabled')
        self.draw_margin()

    def target_at(self, event):
        index = self.text.index(f'@{event.x},{event.y}')
        return next((self.links[tag] for tag in self.text.tag_names(index) if tag in self.links), None)

    def hover_link(self, event):
        self.text.configure(cursor='hand2' if self.target_at(event) else 'xterm')

    def activate_link(self, event):
        target = self.target_at(event)
        if target and not self.text.tag_ranges('sel'):
            self.follow(target)
            return 'break'

    def follow(self, target):
        self.navigate(target)
        return 'break'

    def toggle(self, path):
        self.collapsed.symmetric_difference_update({path})
        position = self.text.yview()[0]
        self.render()
        self.text.yview_moveto(position)

    def expand_all(self, collapse=False):
        self.collapsed = {row.path for row in document_rows(self.document) if row.foldable and row.path} if collapse else set()
        self.render()

    def full_text(self):
        if self.document is None:
            return self.text.get('1.0', 'end-1c')
        return '\n'.join('    ' * row.depth + ''.join(text for text, _ in reference_parts(row.text, self.catalog, row.explicit))
                         for row in document_rows(self.document))

    def copy_all(self):
        self.clipboard_clear()
        self.clipboard_append(self.full_text())
