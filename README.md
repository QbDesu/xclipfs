# xclipfs

Mounts the X11/XFIXES clipboard as a fuse filesystem. Very much WIP, very bad performance, proof of concept. When running the targeted directory contains virtual files containing the clipboard contents. There is one file for each selection target (~mimetype) in the current clipboard.

## Usage

```sh
python ./main.py /path/to/mount/point
```

## Requirements

* xclip
* [fusepy](https://pypi.org/project/fusepy/)