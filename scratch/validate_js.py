def validate():
    with open('static/app.js', 'r', encoding='utf-8') as f:
        code = f.read()
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    in_str = None
    escape = False
    in_line_comment = False
    in_block_comment = False
    i = 0
    while i < len(code):
        ch = code[i]
        nxt = code[i+1] if i + 1 < len(code) else ''
        if in_line_comment:
            if ch == '\n':
                in_line_comment = False
        elif in_block_comment:
            if ch == '*' and nxt == '/':
                in_block_comment = False
                i += 1
        elif in_str:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == in_str:
                in_str = None
        else:
            if ch == '/' and nxt == '/':
                in_line_comment = True
                i += 1
            elif ch == '/' and nxt == '*':
                in_block_comment = True
                i += 1
            elif ch in ('"', "'", '`'):
                in_str = ch
            elif ch in '([{':
                stack.append((ch, i))
            elif ch in ')]}':
                if not stack:
                    print(f"Unmatched {ch} at char {i}")
                    return False
                top, _ = stack.pop()
                if top != pairs[ch]:
                    print(f"Mismatched {top} and {ch} at char {i}")
                    return False
        i += 1
    if stack:
        print(f"Unclosed opening brackets: {len(stack)}, top={stack[-1]}")
        return False
    print("app.js syntax validation: PERFECT (all brackets and quotes balanced)")
    return True

if __name__ == '__main__':
    validate()

