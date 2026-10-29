"""Превращает документ релиза дизайн-токенов в CSS-переменные.

Сохраняет двухслойность системы: базовые литералы и продуктовые алиасы на них.
"""
import json
import re
import sys

MODE = 'b2b-light'


def to_var(path: str) -> str:
    kebab = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '-', path)
    kebab = re.sub(r'(?<=[a-zA-Z])(?=\d[a-zA-Z])', '-', kebab)
    return re.sub(r'[^a-z0-9-]', '-', kebab.replace('.', '-').lower())


def to_value(value, is_number: bool) -> str:
    if isinstance(value, str) and value.startswith('{'):
        return f'var(--base-{to_var(value.strip("{}").replace("base-b2b.", ""))})'
    if is_number and isinstance(value, (int, float)):
        return f'{value:g}'
    return str(value)


def main(src: str, dst: str) -> None:
    document = json.load(open(src))
    base, product = [], []

    for token in document['tokens']:
        if token['collection'] == 'base-b2b':
            base.append((f'--base-{to_var(token["path"])}', to_value(token['$value'], False)))
        elif token['mode'] == MODE:
            product.append((f'--{to_var(token["path"])}', to_value(token['$value'], False)))

    lines = [
        '/* Сгенерировано из документа релиза дизайн-токенов. Не править руками. */',
        '/* tools/tokens-to-css.py doc.json css/design-tokens.css */',
        '',
        ':root {',
        f'\t/* base-b2b — литералы, {len(base)} токенов */',
    ]
    lines += [f'\t{name}: {value};' for name, value in sorted(base)]
    lines += ['', f'\t/* product / {MODE} — семантика, алиасы на base, {len(product)} токенов */']
    lines += [f'\t{name}: {value};' for name, value in sorted(product)]
    lines += ['}', '']

    open(dst, 'w').write('\n'.join(lines))
    print(f'  base: {len(base)} · product: {len(product)} → {dst}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
