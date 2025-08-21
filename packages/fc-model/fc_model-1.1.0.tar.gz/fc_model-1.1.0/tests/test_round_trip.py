import json, sys
from pathlib import Path
from typing import Any, List

from fc_model import FCModel

def deep_diff(a: Any, b: Any, path: str = "$") -> List[str]:
    diffs: List[str] = []

    if type(a) != type(b):
        diffs.append(f"{path}: type mismatch {type(a).__name__} != {type(b).__name__}")
        return diffs

    if isinstance(a, dict):
        a_keys = set(a.keys())
        b_keys = set(b.keys())
        only_a = a_keys - b_keys
        only_b = b_keys - a_keys
        for k in sorted(only_a):
            diffs.append(f"{path}.{k}: missing in second")
        for k in sorted(only_b):
            diffs.append(f"{path}.{k}: missing in first")
        for k in sorted(a_keys & b_keys):
            diffs.extend(deep_diff(a[k], b[k], f"{path}.{k}"))
        return diffs

    if isinstance(a, list):
        if len(a) != len(b):
            diffs.append(f"{path}: list length {len(a)} != {len(b)}")
        min_len = min(len(a), len(b))
        for i in range(min_len):
            diffs.extend(deep_diff(a[i], b[i], f"{path}[{i}]"))
        if len(a) > len(b):
            for i in range(min_len, len(a)):
                diffs.append(f"{path}[{i}]: extra in first: {repr(a[i])}")
        elif len(b) > len(a):
            for i in range(min_len, len(b)):
                diffs.append(f"{path}[{i}]: extra in second: {repr(b[i])}")
        return diffs

    if a != b:
        diffs.append(f"{path}: {repr(a)} != {repr(b)}")
    
    return diffs


def main() -> int:
    p = Path('data/ultracube.fc')
    out = p.with_name(p.stem + '_roundtrip.fc')
    report = p.with_name(p.stem + '_compare.txt')

    # Обновляем round-trip для актуальности
    m = FCModel(str(p))
    m.save(str(out))

    # Проверяем, что файл корректный JSON
    with open(out, 'r') as f:
        json.load(f)

    with open(p, 'r') as f1, open(out, 'r') as f2:
        src = json.load(f1)
        rtp = json.load(f2)

    diffs = deep_diff(src, rtp)

    with open(report, 'w') as rf:
        if not diffs:
            rf.write('OK: files are identical\n')
        else:
            rf.write('DIFFERENCES FOUND:\n')
            for line in diffs:
                rf.write(line + '\n')

    # Возвращаем код 0 если идентичны, иначе 1
    return 0 if not diffs else 1


if __name__ == '__main__':
    sys.exit(main())
