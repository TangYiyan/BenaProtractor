"""Text presentation data, independent of any GUI toolkit."""
from dataclasses import dataclass
import json
import re
import bena


def reference_parts(value, catalog, explicit=''):
    preferred = {}
    for target in str(explicit or '').split(','):
        entry = catalog.resolve(target.strip())
        if entry:
            preferred[entry.key] = entry
    pattern = re.compile(r'<([^<>\n]+)>')
    parts, offset = [], 0

    def append_plain(text):
        last = 0
        matches = catalog.key_pattern.finditer(text) if catalog.key_pattern else []
        for match in matches:
            if match.start() > last:
                parts.append((text[last:match.start()], None))
            entry = preferred.get(match.group()) or catalog.resolve(match.group())
            parts.append((match.group(), entry.target if entry else None))
            last = match.end()
        if last < len(text):
            parts.append((text[last:], None))

    value = str(value)
    for match in pattern.finditer(value):
        append_plain(value[offset:match.start()])
        key = match.group(1)
        entry = preferred.get(key) or catalog.resolve(key)
        label = entry.name if entry else bena.translate_buff_name(key)
        if entry is None and label != key:
            label = f'{label}（{key}）'
        parts.append((label, entry.target if entry else None))
        offset = match.end()
    append_plain(value[offset:])
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


def document_rows(document, collapsed=frozenset()):
    def visit(node, path=(), depth=0):
        if isinstance(node, list):
            for i, child in enumerate(node):
                yield from visit(child, path + (i,), depth)
        elif not isinstance(node, dict):
            yield DocumentRow(path, depth, str(node))
        elif node.get('main') is not None:
            children = node.get('children') or []
            foldable = bool(children or node.get('description') or node.get('true') or node.get('false'))
            role = 'heading' if depth == 0 else 'section' if children else 'body'
            yield DocumentRow(path, depth, str(node['main']), role, node.get('link', ''), foldable)
            if path not in collapsed:
                for key in ('description', 'true', 'false'):
                    if node.get(key):
                        yield DocumentRow(path + (key,), depth + 1, str(node[key]), 'description' if key == 'description' else 'condition')
                for i, child in enumerate(children):
                    yield from visit(child, path + (i,), depth + 1)
    return list(visit(document))


def default_folds(document):
    paths = set()
    def visit(node, path=()):
        if isinstance(node, dict):
            if node.get('style_closed'):
                paths.add(path)
            for i, child in enumerate(node.get('children') or []):
                visit(child, path + (i,))
        elif isinstance(node, list):
            for i, child in enumerate(node):
                visit(child, path + (i,))
    visit(document)
    return paths
