#!/usr/bin/python3
#Interpret for IPP
#project 2
#author: Norbert Pocs (xpocsn00)

import argparse
import sys
import xml.etree.ElementTree as ET
import re

#----------------------------------------------------------------------------------------
#                               PARSING ARGUMENTS
#----------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="IPP project, part interpret")
parser.add_argument('--source', nargs='?', default="stdin", \
        help='vstupni soubor s XML reprezentaci zdrojoveho kodu')
parser.add_argument('--input', nargs='?', default="stdin", \
        help='soubor se vstupy pro samotnou interpretaci zadaneho zdrojoveho kodu.')
args = parser.parse_args()

if(args.source == args.input or args.source == None or args.input == None):
    sys.exit(10);

#----------------------------------------------------------------------------------------
#                                 ERROR HANDLING CLASSES
#----------------------------------------------------------------------------------------
class DuplicateError(Exception):
    ###Raised when the array of instruments has a duplicate###
    pass
class NegativeOrderNumber(Exception):
    ###Raised when at least one of the instructions in the array has###
    ###negative order number###
    pass
class WrongHeaderError(Exception):
    ##Raised when the .out file has other language parameter than ippcode20, insensitive###
    pass
class BadTag(Exception):
    ###Raised when bad tag of the element. f.e. attrib among instructions###
    pass
class NotFound(Exception):
    ###Raised when an item not found in the array###
    pass
class FrameNotDefined(Exception):
    ###Raised when accessing non defined Mem frame###
    pass
class VarRedefinition(Exception):
    ###Raised when a redefinition of a var in a frame###
    pass
class VarNotDefined(Exception):
    ###Raised when the variable is not defined in the frame###
    pass
class InvalidOperand(Exception):
    ###Raised when the passed operand of the instr is bad###
    pass
class BadOperandType(Exception):
    ###Raised when an instruction has wrong operand types e.g. var,symb,lab###
    pass
class NonInicializedVar(Exception):
    ###Raised when trying to read from a noninicialized variable###
    pass

#----------------------------------------------------------------------------------------
#                            CLASS DEALING WITH THE INPUT FILES
#----------------------------------------------------------------------------------------
class XmlFile:

    #Nested class for traversing through instructions
    #implemented jump for jumping jumpers
    class InstructionIterator:
        def __init__(self, xml_root):
            #initializing variables
            self.arr = [x for x in xml_root]
            self.length = len(self.arr)
            self.arr.sort(key=self.sort_key)

            #checking negative order number
            if(int(self.arr[0].attrib['order']) < 0):
                raise NegativeOrderNumber

            #checking duplicates
            if(len(self.arr) != len(set([x.attrib['order'] for x in self.arr]))):
                raise DuplicateError

            #checking missing 'instruction' attrib
            if(len([x for x in xml_root if x.tag != 'instruction']) != 0):
                raise BadTag 

        def __iter__(self):
            #counter for the iteration through arr
            self.i = 0
            return self;

        def __next__(self):
            #get next element of the arr
            i = self.i
            
            #stop when reaching the size of the arr
            if(i == self.length):
                raise StopIteration

            self.i += 1
            return self.arr[i]

        def jump(self, instr_order):
            #setting the index iterator to the instruction pointed by
            try:
                self.i = self.arr.index(next(x for x in self.arr if int(x.attrib['order']) \
                        == instr_order))
            except:
                raise NotFound

        def sort_key(self, e):
            #function for sorting by the order number of the instr
            try:
                return e.attrib['order']
            except:
                raise sys.exc_info()
    
##continuation of the XmlFile class
    def __init__(self, source_path, input_path):
        #opening the source
        if(source_path == 'stdin'):
            self.source_file = sys.stdin
        else:
            try:
                self.xml = ET.parse(source_path)
                self.xml_root = self.xml.getroot()
                self.instr_iter = self.InstructionIterator(self.xml_root)
            except:
                raise sys.exc_info()

        #checking header
        if(self.root.attrib['language'].lower() != 'ippcode20'):
            raise WrongHeaderError

        #opening the input
        if(input_path == 'stdin'):
            self.input_file = sys.stdin
        else:
            try:
                self.input_file = open(source_path, 'r');
            except:
                raise sys.exc_info()

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

#----------------------------------------------------------------------------------------
#                           CHECKING DATA TYPES
#----------------------------------------------------------------------------------------
class Data:
    #TODO
    def check(smth):
        if(re.fullmach('/^(GF|TF|LF)@[a-zA-Z_$&%*!?\-]([a-zA-Z_$&%*!?\-\d])*$/', smth)):
            tmp = smth.split("@") #frame, name
            return ['var', tmp[0], tmp[1]]
        if(re.fullmach('/^[a-zA-Z_$&%*!?\-]([a-zA-Z_$&%*!?\-\d])*$/', smth)):
            return ['label', smth]
        if(re.fullmach('/^nil@nil$/', smth) or
                re.fullmach('/^bool@(true|false)$/', smth) or
                re.fullmach('/^int@(\+|\-)*\d+$/', smth) or
                re.fullmach('/^string@([^\\#\s]|\\\d{3})*$/', smth)):
            tmp = smth.split("@", 1)
            return ['symb', tmp[0], tmp[1]]
        #nothign matched
        raise InvalidOperand

#----------------------------------------------------------------------------------------
#                               CLASS FOR STACK
#----------------------------------------------------------------------------------------
class Stack:
    def __init__(self):
        self.items = []
    def push(self, item):
        self.items.append(item)
    def pop(self):
        return self.items.pop()
    def is_empty(self):
        return self.items == []
    def size(self):
        return len(self.items)
    def top(self):
        return self.items[len(self.items)-1]

#----------------------------------------------------------------------------------------
#                               CLASS FOR MEMORY
#----------------------------------------------------------------------------------------
class Mem:
    #variables
    gf = {}
    #lf = Stack()
    #tf = {}
    data_stack = Stack()
    call_stack = Stack()
    program_counter = 0

    def in_frame(f_type, v_key):
        #f_type can be gf,lf or tf
        if(f_type == "gf"):
            return v_key in gf
        if(f_type == "lf"):
            if(hasattrib(Mem, 'lf')):
                return v_key in lf.top()
            raise FrameNotDefined
        if(f_type == "tf"):
            if(hasattrib(Mem, 'tf')):
                return v_key in tf
            raise FrameNotDefined
    def create_local_frame():
        Mem.lf = Stack()
    def create_temp_frame():
        Mem.tf = {}
    def del_local_frame():
        del Mem.lf
    def del_temp_frame():
        del Mem.tf
    def push_tmp_to_loc():
        if(hasattrib(Mem, "lf") and hasattrib(Mem, "tf")):
            lf.push(tf)
        else:
            raise FrameNotDefined
    def create_var(f_type, v_key):
        #global frame
        if(f_type == "gf"):
            if(in_frame("gf", v_key)):
                raise VarRedefinition
            gf.update({v_key, []})
        #local frame
        if(f_type == "lf"):
            if(hasattrib(Mem, 'lf')):
                if(in_frame("lf", v_key)):
                    raise VarRedefinition
                lf.top().update({v_key, []})
            else:
                raise FrameNotDefined
        #temporary frame
        if(f_type == "tf"):
            if(hasattrib(Mem, "tf")):
                if(in_frame("tf", v_key)):
                    raise VarRedefinition
                tf.update({v_key, []})
            else:
                raise FrameNotDefined

    def add_var(f_type, v_key, v_type, v_val):
        #global frame
        if(f_type == "gf"):
            if(in_frame("gf", v_key)):
                gf.update({v_key:[v_type, v_val]})
            else:
                raise VarNotDefined
        #local frame
        if(f_type == "lf"):
            if(hasattrib(Mem, 'lf')):
                if(in_frame("lf", v_key)):
                    lf.top().update({v_key:[v_type, v_val]})
                else:
                    raise VarNotDefined
            else:
                raise FrameNotDefined
        #temporary frame
        if(f_type == "tf"):
            if(hasattrib(Mem, "tf")):
                if(in_frame("tf", v_key)):
                    tf.update({v_key:[v_type, v_val]})
                else:
                    raise VarNotDefined
            else:
                raise FrameNotDefined
    def get_var(f_type, v_key):
        try:
            if(in_frame(f_type, v_key)):
                #without error
                if(f_type == "gf"):
                    return gf[v_key]
                if(f_type == "lf"):
                    return lf.top()[v_key]
                if(f_type == "tf"):
                    return tf[v_key]
            else:
                raise VarNotFound
        except FrameNotDefined:
            raise FrameNotDefined

#----------------------------------------------------------------------------------------
#                             CLASS HANDLING INSTRUCTIONS
#----------------------------------------------------------------------------------------
class Instr:
    instructions = {'MOVE', 'CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'DEFVAR', 'CALL', \
            'RETURN', 'PUSHS', 'POPS', 'ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', \
            'AND', 'OR', 'NOT', 'INT2CHAR', 'STRI2INT', 'READ', 'WRITE', 'CONCAT', \
            'STRLEN', 'GETCHAR', 'SETCHAR', 'TYPE', 'LABEL', 'JUMP', 'JUMPIFEQ', \
            'JUMPIFNEQ', 'EXIT', 'DPRINT', 'BREAK'}
    def valid_instr(instr):
        return instr in instructions

    def move(var, symb):
        try:
            variable = Data.check(var)
            symbol = Data.check(symb)
        except InvalidOperand:
            raise InvalidOperand
        if(variable[0] == 'var'):
            try:
                if(symbol[0] == 'symb'):
                    Mem.add_var(variable[1], variable[2], symbol[1], symbol[2])
                elif(symbol[0] == 'var'):
                    ret = Mem.get_var(symbol[1], symbol[2])
                    if(ret == []):
                        raise NonInicializedVar
                    Mem.add_var(variable[1], variable[2], typ, val)
                else:
                    raise BadOperandType
            except VarNotDefined:
                raise VarNotDefined
            except FrameNotDefined:
                raise FrameNotDefined
            except NonInicializedVar:
                raise NonInicializedVar
        else:
            raise BadOperandType
    
    def createframe():
        Mem.create_temp_frame()

    def pushframe():
        try:
            Mem.push_tmp_to_loc()
            Mem.del_temp_frame()
        except FrameNotDefined:
            raise FrameNotDefined

    def popframe():
        pass
    # 1 function = 1 intruction
    # .
    # .
    # .

#----------------------------------------------------------------------------------------
#                               TESTING/MAIN PART
#----------------------------------------------------------------------------------------
f = XmlFile(args.source, args.input)
