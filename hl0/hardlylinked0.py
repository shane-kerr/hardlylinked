"""
hardlyliked0.py

This is a program to save or restore hard links in a set of files or
directories.

This version does not actually do anything except create the
framework for the program, including:

* parsing arguments
* setting up logging
* invoking dummy functions
"""
import logging
import sys
import time

import docopt

SYNTAX = """
Save or restore hard links.

Usage:
  hardlylinked0 -s [-f firstlinks] [-e extralinks] <linkstore> <path>...
  hardlylinked0 -r <linkstore>
  hardlylinked0 (-h | --help)

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


def hard_links_restore(linkstore):
    """
    Restore hard links from a store.

    - linkstore, a file name holding the store with information needed
      to restore hard links
    """
    logging.debug("hard_links_restore(%r)", linkstore)


def main(argv):
    """
    Our main function, as invoked from the command line.

    - argv, the command-line arguments
    """
    # set up logging
    logging.Formatter.converter = time.gmtime
    logfmt = '%(asctime)s.%(msecs)d+0000 %(levelname)-7s - %(message)s'
    logging.basicConfig(level=logging.DEBUG,
                        filename='hardlylinked0.log', filemode='w',
                        format=logfmt, datefmt='%Y-%m-%dT%H:%M:%S')

    # parse our command line arguments
    arguments = docopt.docopt(SYNTAX, argv=argv[1:], version="0.0.0")

    # call the proper action based on our arguments
    if arguments['--restore']:
        hard_links_restore(arguments["<linkstore>"])
    else:
        hard_links_save(arguments["<path>"], arguments["<linkstore>"],
                        arguments["--first"], arguments["--extra"])


if __name__ == '__main__':
    main(sys.argv)
