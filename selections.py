import subprocess
import shutil
import os

PRIMARY = 'PRIMARY'
SECONDARY = 'SECONDARY'
CLIPBOARD = 'CLIPBOARD'

TARGETS = 'TARGETS'

class XclipInitializationExeption(Exception):
    pass

class SelectionRetrivalException(Exception):
    pass

_xclip_path = os.environ['XCLIP_PATH'] if 'XCLIP_PATH' in os.environ else shutil.which('xclip')
if not _xclip_path:
    raise XclipInitializationExeption('xclip executable was not found')

async def get_selection(selection: str, target:str = TARGETS) -> tuple[bytes,int,bytes]:
    args = [_xclip_path, '-o', '-selection', selection, '-t', target]
    completed_proc = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    print(type(completed_proc.stdout))
    return completed_proc.stdout, completed_proc.returncode, completed_proc.stderr