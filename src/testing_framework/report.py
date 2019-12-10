from typing import Iterable

def gen_content_block(s: str) -> str:
    return f"""<div>{s}</div>"""

def report(content: Iterable[str]) -> str:
    result = f"""
<!DOCTYPE html>
<html>
  <body>
    { "".join(gen_content_block(s) for s in content) }
  </body>
</html>
"""
    return result