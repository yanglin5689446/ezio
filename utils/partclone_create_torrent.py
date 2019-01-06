#!/usr/bin/env python

'''
This script can generate `torrent` from partclone torrent helper
You need to install `python-libtorrent` in ubnutu or debian like
`apt install python-libtorrent`
It will install `libtorrent-rasterbar` for depend

cat torrent.info | ./partclone_create_torrent.py \ 
-p sda1 -c CloneZilla -f ./btzone/image/sda1/sda1.torrent

When torrent is created, you should use `transmission-edit`
to edit the info such as `tracker` or `private`
'''

import libtorrent as lt
import sys
import os
import re
from argparse import ArgumentParser
from argparse import RawTextHelpFormatter

# parse args
parser = ArgumentParser(
        description='''input torrent.info from stdin
example: cat torrent.info | ./partclone_create_torrent.py \ 
-p sda1 -c CloneZilla -f ./btzone/image/sda1/sda1.torrent''',
        formatter_class=RawTextHelpFormatter)
parser.add_argument("-p", "--partition-name", help="Partition name of this torrent", dest="partition_name", required=True)
parser.add_argument("-f", "--file", help="Output torrent path and filename", dest="filename", required=True)
parser.add_argument("-c", "--creator", help="Creator of this torrent", dest="creator", required=True)

args = parser.parse_args()
partition_name = args.partition_name
creator_name = args.creator
filename = args.filename

data = sys.stdin.read()

# collect sha1
piece_hash = re.findall(r'^sha1: (.*)$', data, re.M)

# collect offset and length
offset = re.findall(r'^offset: (.*)$', data, re.M)
length = re.findall(r'^length: (.*)$', data, re.M)

fs = lt.file_storage()
fs.set_piece_length(16 * 1024 * 1024) # 16MiB

for o, l in zip(offset, length):
    fs.add_file(partition_name + "/" + o, int(l, 16))

torrent = lt.create_torrent(fs, 16 * 1024 * 1024, flags=0)
torrent.set_creator(creator_name)

for index, h in enumerate(piece_hash):
    torrent.set_hash(index, h.decode('hex'))

with open(filename, 'wb') as f:
    f.write(lt.bencode(torrent.generate()))
