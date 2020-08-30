from typing import List
import re

args_regex = re.compile('"([^"]*)"|\'([^\']*)\'|([^ ]+)')


def sanitize_input(src: str) -> str:
    return re.sub(r'[^A-Za-z0-9 _]', "", src.lower().strip())


def parse_arguments(src: str) -> List[str]:
    def get_found_match(m: list) -> str:
        f = [g for g in m if len(g) > 0]
        if len(f) > 0:
            return f[0]
        return ""

    return [get_found_match(m) for m in args_regex.findall(src)]
