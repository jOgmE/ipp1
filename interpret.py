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
class Files:

    #Nested class for traversing through instructions
    #implemented jump for jumping jumpers
    class InstructionIterator:
        def __init__(self, xml_root):
            #initializing variables
            self.arr = [x for x in xml_root]
            self.length = len(self.arr)
            self.arr.sort(key=self.sort_key)
            self.last_instr = self.arr[self.length -1].attrib['order']

            #checking instr attributes
            for instr in self.arr:
                if(not 'opcode' in instr.attrib and not 'order' in instr.attrib \
                        and len(instr.attrib) != 2):
                    raise BadTag

            #checking negative order number
            #only the first because sorted array
            if(int(self.arr[0].attrib['order']) < 0):
                raise NegativeOrderNumber

            #checking duplicates
            if(len(self.arr) != len(set([x.attrib['order'] for x in self.arr]))):
                raise DuplicateError

            #checking missing 'instruction' attrib
            if(len([x for x in xml_root if x.tag != 'instruction']) != 0):
                raise BadTag 
            #run through the code and save every label and their order number
            #check for redefinition and syntax correctness
            check_label_arr = [label for label in self.arr if label.attrib['opcode'].lower() == "label"]
            if(len(check_label_arr) != len(set(check_label_arr))):
                raise BadTag

            for lab in check_label_arr:
                #element lvl
                for arg in lab:
                    #instr arg lvl
                    if(arg.tag != "arg1"):
                        raise InvalidOperand
                    if(arg.attrib['type'].lower() != "label"):
                        raise InvalidOperand
                    #check label syntax
                    if(Data.check(arg.text)[0] != 'label'):
                        raise InvalidOperand
                    #filling the dict with labels
                    Data.label_book.update({arg.text:lab.attrib['order']})

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

        def get_order_number(self):
            #function to get the current instrs order number
            #in the array
            return self.arr[self.i].attrib['order']
    
##continuation of the XmlFile class
    #def __init__(self, source_path, input_path):
    #opening the source
    source_path = args.source
    input_path = args.input

    if(source_path == 'stdin'):
        #sets stdin - etree can parse from stdin
        source_path = sys.stdin
    try:
        Files.xml = ET.parse(source_path)
        Files.xml_root = Files.xml.getroot()
        Files.instr_iter = Files.InstructionIterator(Files.xml_root)
    except:
        raise sys.exc_info()

    #checking header
    if(Files.root.attrib['language'].lower() != 'ippcode20'):
        raise WrongHeaderError

    #opening the input
    if(input_path == 'stdin'):
        #input_path remains stdin
        pass
    else:
        try:
            Files.input_file = open(source_path, 'r');
        except:
            raise sys.exc_info()

#generator for instruction arguments
    def get_arg(instr):
        for arg in instr:
            yield arg
#header attribs
    def get_header_attrib():
        return Files.root.attr
#header tag
    def get_header_tag():
        return Files.root.tag
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
    #label:order number
    label_book = {}
    #TODO
    def check(att):
        #variable
        if(re.fullmach('/^(GF|TF|LF)@[a-zA-Z_$&%*!?\-]([a-zA-Z_$&%*!?\-\d])*$/', att.text)):
            tmp = att.text.split("@") #frame, name
            #[var, frame, name]
            return ['var', tmp[0], tmp[1]]

        #label
        if(re.fullmach('/^[a-zA-Z_$&%*!?\-]([a-zA-Z_$&%*!?\-\d])*$/', att.text)):
            #[label, name]
            return ['label', att.text]

        #symbol
        typ = att.attrib['type'].lower()
        if((re.fullmach('/^nil$/', att.text) and typ == 'nil') or \
                (re.fullmach('/^(true|false)$/', att.text) and typ == 'bool') or \
                (re.fullmach('/^(\+|\-)*\d+$/', att.text) and typ == 'int') or \
                (re.fullmach('/^([^\\#\s]|\\\d{3})*$/', att.text) and typ == 'string')):
            #[symb, type, value]
            return ['symb', typ, att.text]

        #type
        if(typ == 'type' and re.fullmatch('/(int|string|bool)/', att.text)):
            return ['type', att.text]
        #nothign matched
        raise InvalidOperand

    #searches for a given key in lowcase and returns the key what can be
    #case insensitive
    def get_dict_key(dictionary, lowcase_key):
        return [key for key in dictionary.keys() if key.lower() == lowcase_key]

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

    def in_frame(f_type, v_key):
        #f_type can be gf,lf or tf
        if(f_type == "gf"):
            return v_key in Mem.gf
        if(f_type == "lf"):
            if(hasattrib(Mem, 'lf')):
                return v_key in Mem.lf.top()
            raise FrameNotDefined
        if(f_type == "tf"):
            if(hasattrib(Mem, 'tf')):
                return v_key in Mem.tf
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
            Mem.lf.push(tf)
        else:
            raise FrameNotDefined
    def pop_tmp_from_loc():
        if(hasattrib(Mem, "lf")):
            Mem.tf = Mem.lf.pop()
    def declare_var(f_type, v_key):
        #global frame
        if(f_type == "gf"):
            if(in_frame("gf", v_key)):
                raise VarRedefinition
            Mem.gf.update({v_key, []})
        #local frame
        if(f_type == "lf"):
            if(hasattrib(Mem, 'lf')):
                if(in_frame("lf", v_key)):
                    raise VarRedefinition
                Mem.lf.top().update({v_key, []})
            else:
                raise FrameNotDefined
        #temporary frame
        if(f_type == "tf"):
            if(hasattrib(Mem, "tf")):
                if(in_frame("tf", v_key)):
                    raise VarRedefinition
                Mem.tf.update({v_key, []})
            else:
                raise FrameNotDefined

    def add_var(f_type, v_key, v_type, v_val):
        #global frame
        if(f_type == "gf"):
            if(in_frame("gf", v_key)):
                Mem.gf.update({v_key:[v_type, v_val]})
            else:
                raise VarNotDefined
        #local frame
        if(f_type == "lf"):
            if(hasattrib(Mem, 'lf')):
                if(in_frame("lf", v_key)):
                    Mem.lf.top().update({v_key:[v_type, v_val]})
                else:
                    raise VarNotDefined
            else:
                raise FrameNotDefined
        #temporary frame
        if(f_type == "tf"):
            if(hasattrib(Mem, "tf")):
                if(in_frame("tf", v_key)):
                    Mem.tf.update({v_key:[v_type, v_val]})
                else:
                    raise VarNotDefined
            else:
                raise FrameNotDefined
    def get_var(f_type, v_key):
        try:
            if(in_frame(f_type, v_key)):
                #without error
                if(f_type == "gf"):
                    return Mem.gf[v_key]
                if(f_type == "lf"):
                    return Mem.lf.top()[v_key]
                if(f_type == "tf"):
                    return Mem.tf[v_key]
            else:
                raise VarNotFound
        except FrameNotDefined:
            raise FrameNotDefined

#----------------------------------------------------------------------------------------
#                             CLASS HANDLING INSTRUCTIONS
#----------------------------------------------------------------------------------------
class Instr:
    instructions = {'MOVE':Instr.move, 'CREATEFRAME':Instr.createframe, \
            'PUSHFRAME':Instr.pushframe, 'POPFRAME':Instr.popframe, 'DEFVAR':Instr.defvar, \
            'CALL':Instr.call, 'RETURN':Instr.ret, 'PUSHS', 'POPS', 'ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', \
            'AND', 'OR', 'NOT', 'INT2CHAR', 'STRI2INT', 'READ', 'WRITE', 'CONCAT', \
            'STRLEN', 'GETCHAR', 'SETCHAR', 'TYPE', 'LABEL', 'JUMP', 'JUMPIFEQ', \
            'JUMPIFNEQ', 'EXIT', 'DPRINT', 'BREAK'}

    instr_var_symb = ('MOVE', 'INT2CHAR', 'STRLEN', 'TYPE', 'NOT')
    instr_empty = ('CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', 'BREAK')
    instr_var = ('DEFVAR', 'POPS')
    instr_lab = ('CALL', 'LABEL', 'JUMP')
    instr_symb = ('PUSHS', 'WRITE', 'EXIT', 'DPRINT')
    instr_var_symb_symb = ('ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR' \
                            'STRI2INT', 'CONCAT', 'GETCHAR', 'SETCHAR')
    instr_var_typ = ('READ')
    instr_lab_symb = ('JUMPIFEQ', 'JUMPIFNEQ')

    def move(operands):
        #read the oprnd arr
        variable = operands[0]
        symbol = operands[1]
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
            except VarNotDefined: # Do I need these? is bubbling implicit?
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
        Mem.pop_tmp_from_loc()
    
    def defvar(operands):
        variable = operands[0]
        #check var correctness
        try:
            ret = Data.check(variable)
        except InvalidOperand:
            raise InvalidOperand

        if(ret[0] != 'var'):
            raise InvalidOperand
        #checking var name existence in the given frame
        if(Mem.in_frame(ret[1], ret[2])):
            raise VarRedefinition
        #variable declaration
        Mem.declare_var(ret[1], ret[2])

    def call(operands):
        label = operands[0]
        #check TODO last_instr > order number
        #saving the next instr number after the call
        Mem.call_stack.push(Files.instr_iter.get_order_number() + 1)
        try:
            Files.instr_iterator.jump(Data.label_book[label])
        except:
            #not found
            raise InvalidOperand

    def ret():
        if(Mem.call_stack.size() < 1):
            pass #raise error
        Files.instr_iterator.jump(Mem.call_stack.pop())

    # 1 function = 1 intruction
    # .
    # .
    # .

#----------------------------------------------------------------------------------------
#                                   INTERPRET
#----------------------------------------------------------------------------------------
class Interpret:
    for instr in Files.instr_iter:
        code = instr.attrib['opcode'].upper() #case insensitive
        arg_arr = [] #instructin operands
        #load all the operands into the arr
        for a in instr:
            try:
                arg_arr.append(Data.check(a.text))
            except:
                pass

        #calling instructions
        if code in Instr.instr_var_symb:
            if(len(arg_arr) != 2):
                pass #raise error
            if(arg_arr[0][0] != 'var' and (arg_arr[1][0] != 'var' or arg_arr[1][0] != 'symb')):
                pass #raise error
        elif code in Instr.instr_empty:
            if(len(arg_arr) != 0):
                pass
        elif code in Instr.instr_var:
            if(len(arg_arr) != 1):
                pass
            if(arg_arr[0][0] != 'var'):
                pass
        elif code in Instr.instr_lab:
            if(len(arg_arr) != 1):
                pass
            if(arg_arr[0][0] != 'label'):
                pass
        elif code in Instr.instr_symb:
            if(len(arg_arr) != 1):
                pass
            if(arg_arr[0][0] != 'symb'):
                pass
        elif code in Instr.instr_var_symb_symb:
            if(len(arg_arr) != 3):
                pass
            if(arg_arr[0][0] != 'var' and (arg_arr[1][0] != 'var' or arg_arr[1][0] != 'symb') \
                    and (arg_arr[2][0] != 'var' or arg_arr[2][0] != 'symb')):
                pass
        elif code in Instr.instr_var_typ:
            if(len(arg_arr) != 2):
                pass
            if(arg_arr[0][0] != 'var' and arg_arr[1][0] != 'type'):
                pass
        elif code in Instr.instr_lab_symb:
            if(len(arg_arr) != 2):
                pass
            if(arg_arr[0][0] != 'label' and \
                    (arg_arr[1][0] != 'var' or arg_arr[1][0] != 'symb')):
                pass
        else:
            pass

        #calling the function of the instruction
        Instr.instructions[code](arg_arr)

#----------------------------------------------------------------------------------------
#                               TESTING/MAIN PART
#----------------------------------------------------------------------------------------
#f = XmlFile(args.source, args.input)
