import logging

from sys import argv, exit, stderr
from time import time

import subprocess
import shutil

from fuse import FUSE, Operations, LoggingMixIn
from stat import S_IFDIR, S_IFREG

def mimetype_to_filename(mimetype: str) -> str:
    return mimetype.replace('/','.',1).replace('+','.')

def filename_to_mimetype(filename: str) -> str:
    return filename.replace('.','/',1).replace('.','+')

class XClipFs(Operations):
    '''
    A simple SFTP filesystem. Requires paramiko: http://www.lag.net/paramiko/
    You need to be able to login to remote host without entering a password.
    '''

    def __init__(self, path='.'):
        self.xclip = shutil.which('xclip')
        self.root = path

    def getattr(self, path, fh=None):
        '''
        Returns a dictionary with keys identical to the stat C structure of
        stat(2).

        st_atime, st_mtime and st_ctime should be floats.

        NOTE: There is an incombatibility between Linux and Mac OS X
        concerning st_nlink of directories. Mac OS X counts all files inside
        the directory, while Linux counts only the subdirectories.
        '''

        if path == '/':
            return dict(st_mode=(S_IFDIR | 0o755), st_nlink=2)
        else:
            target = filename_to_mimetype(path[1:]) if "." in path else path[1:]
            args = [self.xclip, '-o', '-selection', 'clipboard', '-t', target]
            completed_proc = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=stderr
            )
            return dict(st_mode=(S_IFREG | 0o755), st_size=len(completed_proc.stdout))
        

    def read(self, path, size, offset, fh):
        target = filename_to_mimetype(path[1:]) if "." in path else path[1:]
        args = [self.xclip, '-o', '-selection', 'clipboard', '-t', target]
        completed_proc = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=stderr
        )
        return completed_proc.stdout[offset:offset+size]

    def readdir(self, path, fh):
        args = [self.xclip, '-o', '-selection', 'clipboard', '-t', 'TARGETS']
        completed_proc = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=stderr
        )
        return ['.', '..'] + [
                    mimetype_to_filename(name) if "/" in name else name
                    for name in completed_proc.stdout.decode('utf-8').splitlines()
        ]

if __name__ == '__main__':
    if len(argv) != 2:
        print('usage: %s <mountpoint>' % argv[0])
        exit(1)

    logging.basicConfig(level=logging.DEBUG)

    fuse = FUSE(XClipFs(), argv[1], foreground=True, nothreads=True)