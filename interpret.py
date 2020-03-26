#Interpret for IPP
#project 2
#author: Norbert Pocs (xpocsn00)

import argparse
import sys
import xml.etree.ElementTree as ET

#parsing arguments
parser = argparse.ArgumentParser(description="IPP project, part interpret")
parser.add_argument('--source', nargs='?', default="stdin", \
        help='vstupní soubor s XML reprezentací zdrojového kódu')
parser.add_argument('--input', nargs='?', default="stdin", \
        help='soubor se vstupy pro samotnou interpretaci zadaného zdrojového kódu.')
args = parser.parse_args()

if(args.source == args.input or args.source == None or args.input == None):
    sys.exit(10);


