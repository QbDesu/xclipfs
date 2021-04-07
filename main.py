import asyncio
import logging
import os

from sys import argv, exit, stderr
from time import time

import selections

from fuse import FUSE, Operations, LoggingMixIn, c_stat
from stat import S_IFDIR, S_IFREG

def mimetype_to_filename(mimetype: str) -> str:
    return mimetype.replace('/','.',1).replace('+','.')

def filename_to_mimetype(filename: str) -> str:
    return filename.replace('.','/',1).replace('.','+')

class XClipFs(Operations):
    '''
    A simple X11/XFIXES clipboard filesystem.
    '''

    def __init__(self, path='.'):
        self.root = path

    async def get_attr_for_target(self, target: str) -> c_stat:
        selection, e, stderr = await selections.get_selection(selections.CLIPBOARD, target)
        return dict(st_mode=(S_IFREG | 0o755), st_size=len(selection))

    def getattr(self, path, fh=None):
        if path == '/':
            return dict(st_mode=(S_IFDIR | 0o755), st_nlink=2)
        else:
            target = filename_to_mimetype(os.path.basename(path))
            return asyncio.run(self.get_attr_for_target(target))
        

    def read(self, path, size, offset, fh):
        target = filename_to_mimetype(path[1:]) if "." in path else path[1:]
        selection, *_ = asyncio.run(selections.get_selection(selections.CLIPBOARD, target))
        return selection[offset:offset+size]

    async def directory(self, targets):
        return [(
                    mimetype_to_filename(target.decode('utf-8')),
                    await self.get_attr_for_target(target),
                    0
                )
                for target in targets]

    def readdir(self, path, fh):
        selection, *_ = asyncio.run(selections.get_selection(selections.CLIPBOARD, selections.TARGETS))
        return ['.', '..'] + asyncio.run(self.directory(selection.splitlines()))

if __name__ == '__main__':
    if len(argv) != 2:
        print('usage: %s <mountpoint>' % argv[0])
        exit(1)

    logging.basicConfig(level=logging.INFO)

    fuse = FUSE(XClipFs(), argv[1], foreground=True, nothreads=True)
