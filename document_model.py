"""Text presentation data, independent of any GUI toolkit."""
from dataclasses import dataclass
import json
import re

REFERENCE_PATTERN = re.compile(r'<([^<>\n]*)>')


def reference_parts(value, catalog, explicit=''):
    """Resolve declared references; leave unknown text and prose unchanged."""
    preferred = {}
    for target in str(explicit or '').split(','):
        entry = catalog.resolve(target.strip())
        if entry:
            preferred[entry.key] = entry
    parts = []
    value = str(value)

    def plain(start, end):
        offset = start
        if catalog.key_pattern:
            for match in catalog.key_pattern.finditer(value, start, end):
                if match.start() > offset:
                    parts.append((value[offset:match.start()], None))
                key = match.group()
                entry = preferred.get(key) or catalog.resolve(key)
                # Bare IDs gain a link, but never replace the author's wording.
                parts.append((key, entry.target if entry and entry.key == key else None))
                offset = match.end()
        if offset < end:
            parts.append((value[offset:end], None))

    offset = 0
    for match in REFERENCE_PATTERN.finditer(value):
        plain(offset, match.start())
        key = match.group(1)
        if '|' in key:
            category, key = key.split('|', 1)
            entry = catalog.resolve(key, category=category)
        else:
            entry = preferred.get(key) or catalog.resolve(key)
            # Untyped Chinese names may be ordinary game prose, not Buff IDs.
            if entry and entry.key != key:
                entry = None
        parts.append((entry.name, entry.target) if entry else (match.group(), None))
        offset = match.end()
    plain(offset, len(value))
    return parts


TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|\b(?:true|false|null)\b|[{}\[\]]')
COLON = re.compile(r'\s*:')


def json_spans(source):
    nesting = 0
    for match in TOKEN.finditer(source):
        token = match.group()
        if token.startswith('"'):
            kind = 'key' if COLON.match(source, match.end()) else 'type' if token.startswith('"Torappu.') else 'string'
        elif token in ('true', 'false', 'null'):
            kind = 'keyword'
        elif token in '{}[]':
            nesting = max(0, nesting - int(token in '}]'))
            kind = f'bracket{nesting % 3}'
            nesting += int(token in '{[')
        else:
            kind = 'number'
        yield match.start(), match.end(), kind


@dataclass
class DocumentRow:
    path: tuple
    depth: int
    text: str
    role: str = 'body'
    explicit: str = ''
    foldable: bool = False

# 文档嵌套解析
def document_rows(document, collapsed=frozenset()):
    def visit(part, path=(), depth=0):
        if isinstance(part, list):
            for i, child in enumerate(part):
                yield from visit(child, path + (i,), depth)
        elif not isinstance(part, dict):
            yield DocumentRow(path, depth, str(part))
        else:
            # 正文
            children = part.get('children') or []
            foldable = bool(children or part.get('description'))
            role = 'heading' if depth == 0 else 'section' if children else 'body'
            if part.get('main'):
                yield DocumentRow(path, depth, str(part['main']), role, part.get('link', ''), foldable)
            if not part.get("last_one"):
                if part.get('true') :
                    yield DocumentRow(path, depth, "若"+str(part['true'])+"，则继续执行后续节点", 'condition', part.get('link', ''), foldable)
                elif part.get('false'):
                    yield DocumentRow(path, depth, "若"+str(part['false'])+"，则停止执行后续节点", 'condition', part.get('link', ''), foldable)

            # 子部分
            if path not in collapsed:
                if part.get('description'):
                    yield DocumentRow(path + ('description',), depth + 1, str(part['description']), 'description')
                for i, child in enumerate(children):
                    yield from visit(child, path + (i,), depth + 1)
    return list(visit(document))


def default_folds(document):
    paths = set()
    def visit(part, path=()):
        if isinstance(part, dict):
            if part.get('style_closed'):
                paths.add(path)
            for i, child in enumerate(part.get('children') or []):
                visit(child, path + (i,))
        elif isinstance(part, list):
            for i, child in enumerate(part):
                visit(child, path + (i,))
    visit(document)
    return paths
