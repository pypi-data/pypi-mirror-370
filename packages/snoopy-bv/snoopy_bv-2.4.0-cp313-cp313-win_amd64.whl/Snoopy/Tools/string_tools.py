def clean_comment_lines(lines):
    for il in range(len(lines)):
        l = lines[il]
        lines[il] = l[:l.find("#")].strip()


if __name__ == "__main__":
    lines = []
    lines.append("")
    lines.append("   This is not a comment")
    lines.append("  This is also not a comment  # but this one it is")
    lines.append(" #Full line is comment")
    lines.append("")
    lines.append("Another line #with comment #additional symbol")

    for l in lines:
        print(l)
    CleanCommentLines(lines)
    for l in lines:
        print(l)
