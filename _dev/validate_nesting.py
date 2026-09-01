import re
import sys

def validate_div_nesting(html_content, label=""):
    """Stack-based validator that catches actual mismatched nesting, not just
    total open/close counts (which can coincidentally match despite real bugs)."""
    # Strip script blocks and comments first
    content = re.sub(r'<script>.*?</script>', '', html_content, flags=re.DOTALL)
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

    stack = []
    errors = []
    for m in re.finditer(r'<(/?)div\b[^>]*>', content):
        is_close = m.group(1) == '/'
        line_num = content[:m.start()].count('\n') + 1
        if is_close:
            if not stack:
                errors.append(f"Line {line_num}: closing </div> with empty stack (extra close)")
            else:
                stack.pop()
        else:
            stack.append(line_num)
    if stack:
        errors.append(f"Unclosed <div> tags opened at lines: {stack}")

    if errors:
        print(f"[{label}] NESTING ERRORS FOUND:")
        for e in errors:
            print("  -", e)
        return False
    else:
        print(f"[{label}] Nesting OK - all divs properly matched")
        return True

if __name__ == '__main__':
    path = sys.argv[1]
    with open(path, encoding='utf-8') as fh:
        content = fh.read()
    validate_div_nesting(content, path)
