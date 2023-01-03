import logging

from altparse import AltSourceManager, Parser, altsource_from_file

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

sourcesData = [
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "https://apps.altstore.io"},
        "ids": ["com.rileytestut.Delta.Beta"],
    },
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "https://apps.litritt.com"},
        "ids": ["com.SideStore.SideStore"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "Wh0ba", "repo_name": "XPatcher"},
        "ids": ["com.wh0ba.xpatcher"]
    }
]

def header_remover(filename: str, header: str):
    with open(filename, 'r+') as f: 
        content = f.readlines()
        f.seek(0)
        f.writelines(content[header.count('\n')+1:])
        f.truncate()
        
def header_prepender(filename: str, header: str):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(header.rstrip('\r\n') + '\n' + content)
        f.truncate()

src = altsource_from_file("_includes/source.json")
mgr = AltSourceManager(src, sourcesData)
try:
    mgr.update()
    mgr.save(prettify=True)
except Exception as err:
    logging.error(f"Unable to update {mgr.src.name}.")
    logging.error(f"{type(err).__name__}: {str(err)}")
        