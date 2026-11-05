import sys, zipfile, lxml.etree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
p = sys.argv[1]
z = zipfile.ZipFile(p)
root = ET.fromstring(z.read('word/document.xml'))
body = root.find(W + 'body')


def txt(el):
    return ''.join(t.text or '' for t in el.iter(W + 't'))


i = 0
out = []
for el in body:
    if el.tag == W + 'p':
        ps = el.find(W + 'pPr/' + W + 'pStyle')
        st = ps.get(W + 'val') if ps is not None else 'Normal'
        img = len(list(el.iter(W + 'drawing')))
        out.append(f"[{i}]{{{st}}}{'[IMG]' if img else ''} {txt(el)}")
        i += 1
    elif el.tag == W + 'tbl':
        rows = []
        for tr in el.findall(W + 'tr'):
            cells = [txt(tc).strip() for tc in tr.findall(W + 'tc')]
            rows.append(' | '.join(cells))
        out.append(f"[{i}]<TABLE {len(rows)} rows>\n    " + "\n    ".join(rows))
        i += 1

with open(sys.argv[2], 'w', encoding='utf8') as f:
    f.write('\n'.join(out))
print('blocks:', i)
