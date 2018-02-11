"""
hardlyliked1.py

This is a program to save or restore hard links in a set of files or
directories.

This version implemets the basic functionality.
"""
import logging
import os
import stat
import string
import sys
import time

import docopt

SYNTAX = """
Save or restore hard links.

Usage:
  hardlylinked1 -s [-f firstlinks] [-e extralinks] <linkstore> <path>...
  hardlylinked1 -r <linkstore>
  hardlylinked1 (-h | --help)

Options:
  -h --help                Show this screen.
  -s --save                Save link information.
  -f --first firstlinks    File to store name of first use of each inode.
  -e --extra extralinks    File to store name of additional use of each inode.
  -r --restore             Restore link information.

Arguments:
  linkstore                File storing link information.
  path                     Directory or file to check for hard links.
"""


# Make a set containing the values that we will NOT escape in filenames.
PRINTABLE_SET = set([ord(c) for c in string.printable])
WHITESPACE_SET = set([ord(c) for c in string.whitespace])
NONESC_SET = PRINTABLE_SET - WHITESPACE_SET - set([b'\\'])


def escape_filename(filename):
    """
    Escape any characters from the file name given that may cause
    problems.

    - filename, the name to escape

    In principle, we only need to escape backslash ('\\') and
    newline ('\n'), since those are the characters that will have
    meaning for us when we unescape a filename. However, we choose to
    also escape anything that is not-printable because that can make
    visual inspection of the file by hand difficult. We also escape
    whitespace characters for the same reason (for example, it is
    impossible to tell whether you have a file name with a tab or with
    spaces just by looking at it).
    """
    esc_bytes = bytearray()
    for byte in filename:
        if byte in NONESC_SET:
            esc_bytes.append(byte)
        else:
            esc_bytes.extend(b'\\x%02X' % byte)
    return bytes(esc_bytes)


def unescape_filename(filename):
    """
    Convert a file name previously escaped with escape_filename() to
    the original version.

    - filename, the name to unescape
    """
    unesc_bytes = bytearray()
    ofs = 0
    while ofs < len(filename):
        if filename[ofs] == ord('\\'):
            unesc_bytes.append(int(filename[ofs+2:ofs+4], 16))
            ofs += 4
        else:
            unesc_bytes.append(filename[ofs])
            ofs += 1
    return bytes(unesc_bytes)


# pylint: disable=R0903
class HardLinksState:
    """
    This class contains the information that we use to output
    information about whether files and directories are hard links
    or not.

    Initialize with:
    - linkstore, a file name to store information about hard links in
    - firstlinks, a file name to store name of first use of each inode
    - extralinks, a file name to store name of additional use of each inode
    """
    def __init__(self, linkstore, firstlinks, extralinks):
        self.inodes = {}
        self.store_fp = open(linkstore, 'wb')
        if firstlinks:
            self.first_fp = open(firstlinks, 'wb')
        else:
            self.first_fp = None
        if extralinks:
            self.extra_fp = open(extralinks, 'wb')
        else:
            self.extra_fp = None

    def record_file(self, filename, inode):
        """
        Record information about the given file.

        - filename, the name of the file to record
        - inode, the inode number of the file

        This function will check if the inode has already been seen.
        If not, then it gets handled as the first occurrence of that
        inode. If so, then it is an extra occurrence and will be
        handled as such.
        """
        if inode in self.inodes:
            # found a hard link
            self.store_fp.write(escape_filename(self.inodes[inode]) + b'\n')
            self.store_fp.write(escape_filename(filename) + b'\n')
            if self.extra_fp:
                self.extra_fp.write(filename + b'\n')
        else:
            # not a hard link
            self.inodes[inode] = filename
            if self.first_fp:
                self.first_fp.write(filename + b'\n')


def hard_links_save(files, linkstore, firstlinks, extralinks):
    """
    Save hard links to a store.

    - files, a list of file or directory names to check for hard links
    - linkstore, a file name to store information about hard links in
    - firstlinks, a file name to store name of first use of each inode
    - extralinks, a file name to store name of additional use of each inode
    """
    logging.debug("hard_links_save(%r, %r, %r, %r)",
                  files, linkstore, firstlinks, extralinks)

    state = HardLinksState(linkstore, firstlinks, extralinks)
    for path in [f.encode() for f in files]:
        st_path = os.lstat(path)
        if stat.S_ISDIR(st_path.st_mode):
            for dirpath, dirnames, filenames in os.walk(path):
                for name in dirnames + filenames:
                    fullname = dirpath + b'/' + name
                    state.record_file(fullname, os.lstat(fullname).st_ino)
        else:
            state.record_file(fullname, st_path.st_ino)


def hard_links_restore(linkstore):
    """
    Restore hard links from a store.

    - linkstore, a file name holding the store with information needed
      to restore hard links
    """
    logging.debug("hard_links_restore(%r)", linkstore)
    with open(linkstore, 'rb') as store_fp:
        while True:
            first_esc_fname = store_fp.readline()
            if first_esc_fname == b'':
                break
            extra_esc_fname = store_fp.readline()
            first_fname = unescape_filename(first_esc_fname[:-1])
            extra_fname = unescape_filename(extra_esc_fname[:-1])
            os.link(first_fname, extra_fname)


def main(argv):
    """
    Our main function, as invoked from the command line.

    - argv, the command-line arguments
    """
    # set up logging
    logging.Formatter.converter = time.gmtime
    logfmt = '%(asctime)s.%(msecs)d+0000 %(levelname)-7s - %(message)s'
    logging.basicConfig(level=logging.DEBUG,
                        filename='hardlylinked1.log', filemode='w',
                        format=logfmt, datefmt='%Y-%m-%dT%H:%M:%S')

    # parse our command line arguments
    arguments = docopt.docopt(SYNTAX, argv=argv[1:], version="0.1.0")

    # call the proper action based on our arguments
    if arguments['--restore']:
        hard_links_restore(arguments["<linkstore>"])
    else:
        hard_links_save(arguments["<path>"], arguments["<linkstore>"],
                        arguments["--first"], arguments["--extra"])


if __name__ == '__main__':
    main(sys.argv)
