#!/usr/bin/env python
# Automatically correct common errors in PO files for gettext, like
# missing or extraneous interpunction at the end of the message.


def unquote(text):
    while text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    return text


def fix_message(msgid, msgstr):
    if not (msgid and msgstr):
        return msgstr
    for char in '.?!:':
        if msgstr.endswith(char) and not msgid.endswith(char):
            msgstr = msgstr.rstrip(char)
    for char in '.?!:':
        if msgid.endswith(char) and not msgstr.endswith(char):
            msgstr += char
    # if msgid[0].isupper() and msgstr[0].islower():
    #     msgstr = msgstr[0].upper() + msgstr[1:]
    # if msgid[0].islower() and msgstr[0].isupper():
    #     msgstr = msgstr[0].lower() + msgstr[1:]
    return msgstr


def format_file(filename):
    msgid = msgstr = None
    for line in file(filename):
        if line.startswith('#'):
            yield line
        elif line.startswith('msgid '):
            msgid = unquote(line[len('msgid'):].strip())
            yield 'msgid "%s"\n' % msgid
        elif line.startswith('msgstr '):
            msgstr = unquote(line[len('msgstr'):].strip())
            msgstr = fix_message(msgid, msgstr)
            yield 'msgstr "%s"\n' % msgstr
        else:
            yield line


if __name__ == '__main__':
    import sys
    for filename in sys.argv[1:]:
        if filename.startswith('locale/'):
            lang = filename.split('/')[1][:2]
            if lang in 'ja ru zh ar el'.split():
                print "ignoring", filename
                continue
        lines = list(format_file(filename))
        file(filename, 'w').write(''.join(lines))
