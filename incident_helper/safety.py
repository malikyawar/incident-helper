import re
from typing import Tuple

DANGEROUS_PATTERNS = {
    'destructive_delete': r'rm\s+(-rf|-fr|-r\s+-f|-f\s+-r)\s+(/|/\*|~|\$HOME)',
    'disk_operations': r'dd\s+.*of=/dev/|mkfs|fdisk',
    'fork_bomb': r':\(\)\{.*:\|:&\};:',
    'system_overwrites': r'>\s*/dev/sd[a-z]|>\s*/dev/nvme',
}

def check_command_safety(command: str) -> Tuple[bool, str]:
    """Returns (is_safe, warning_message)"""
    for name, pattern in DANGEROUS_PATTERNS.items():
        if re.search(pattern, command, re.IGNORECASE):
            return False, f"⚠️  Potentially destructive command detected ({name})"
    return True, ""
