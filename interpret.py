#Interpret for IPP
#project 2
#author: Norbert Pocs (xpocsn00)

import argparse
import sys
import xml.etree.ElementTree as ET

#parsing arguments
parser = argparse.ArgumentParser(description="IPP project, part interpret")
parser.add_argument('--source', nargs='?', default="stdin", \
        help='vstupni soubor s XML reprezentaci zdrojoveho kodu')
parser.add_argument('--input', nargs='?', default="stdin", \
        help='soubor se vstupy pro samotnou interpretaci zadaneho zdrojoveho kodu.')
args = parser.parse_args()

#if(args.source == args.input or args.source == None or args.input == None):
#    sys.exit(10);

class Files:
    
    def __init__(self, source_path, input_path):
        #opening the files or setting them to stdin
        if(source_path == 'stdin'):
            self.source_file = sys.stdin
        else:
            try:
                self.xml = ET.parse(source_path)
                self.root = xml.getroot()
            except:
                raise sys.exc_info()

        if(input_path == 'stdin'):
            self.input_file = sys.stdin
        else:
            try:
                self.input_file = open(source_path, 'r');
            except:
                raise sys.exc_info()

#generator for instructions
    def get_instr(self):
        for instr in self.root:
            yield instr
#generator for instruction arguments
    def get_arg(self, instr):
        for arg in instr:
            yield arg
#header attribs
    def get_header_attrib(self):
        return self.root.attr
#header tag
    def get_header_tag(self):
        return self.root.tag
#accessing an elements tag
    def get_element_tag(elem):
        return elem.tag
#accessing an elements attrs
    def get_element_attr(elem):
        return elem.attr

##TODO write functions for INPUT

class Instr:
    instructions = {'move', 'createframe', 'pushframe', 'popframe', 'defvar', 'call', \
            'return', 'pushs', 'pops', 'add', 'sub', 'mul', 'idiv', 'lt', 'gt', 'eq', \
            'and', 'or', 'not', 'int2char', 'stri2int', 'read', 'write', 'concat', \
            'strlen', 'getchar', 'setchar', 'type', 'label', 'jump', 'jumpifeq', \
            'jumpifneq', 'exit', 'dprint', 'break'}
    # 1 function = 1 intruction
    # .
    # .
    # .
