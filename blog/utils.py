symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяії",
           u"abvgdeejzijklmnoprstufhzcss_y_euaii")


def transliterate(text):
    if text[0] in symbols[1]:
        return False
    tr = {ord(a): ord(b) for a, b in zip(*symbols)}
    return text.translate(tr)
