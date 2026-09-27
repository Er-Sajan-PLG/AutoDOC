"""Closed tool dispatcher: never executes a shell command or opens a socket."""
from pathlib import Path
from .policy import ROOT, load
from .tools.calculator import add
from .tools.text_utils import uppercase
from .tools.filesystem import read


def run(name, *args, data_root=None):
    policy = load()
    if name not in policy:
        raise ValueError(f'DENIED {name}: unknown tool')
    tool = policy[name]
    if tool['status'] != 'allow':
        raise PermissionError(f'DENIED {name}: blocked by policy')
    if tool['requires_confirmation']:
        raise PermissionError(f'DENIED {name}: human confirmation required; no approval system exists')
    handlers = {'math.add': add, 'text.upper': uppercase,
                'files.read': lambda filename: read(Path(data_root or ROOT / 'data'), filename)}
    return handlers[name](*args)


if __name__ == '__main__':
    print('math.add(2,3) =', run('math.add', 2, 3))
    try:
        run('network.fetch', 'https://example.invalid')
    except PermissionError as exc:
        print(exc)
