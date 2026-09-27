"""Load and validate a closed, explicit tool authorization matrix."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
KNOWN = {'math.add', 'text.upper', 'files.read', 'shell.run_script', 'network.fetch'}


def load(path=None):
    data = json.loads((path or ROOT / 'config/tool-authorization.yaml').read_text(encoding='utf-8'))
    if data.get('version') != 1 or not isinstance(data.get('tools'), list):
        raise ValueError('Invalid tool matrix version or missing tools')
    tools = {}
    for item in data['tools']:
        if (set(item) != {'name', 'status', 'risk', 'requires_confirmation', 'description'} or
                item['name'] not in KNOWN or item['name'] in tools or
                item['status'] not in ('allow', 'blocked') or
                type(item['requires_confirmation']) is not bool or
                not isinstance(item['description'], str) or not item['description']):
            raise ValueError('Invalid, duplicate or unknown tool matrix entry')
        tools[item['name']] = item
    if set(tools) != KNOWN or any(tools[name]['status'] != 'blocked' for name in ('network.fetch', 'shell.run_script')):
        raise ValueError('Matrix must explicitly block all unimplemented network/shell tools')
    return tools
