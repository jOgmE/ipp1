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
class Arguments:
    parser = argparse.ArgumentParser(description="IPP project, part interpret")
    parser.add_argument('--source', nargs='?', default="stdin", \
            help='vstupni soubor s XML reprezentaci zdrojoveho kodu')
    parser.add_argument('--input', nargs='?', default="stdin", \
            help='soubor se vstupy pro samotnou interpretaci zadaneho zdrojoveho kodu.')
    args = parser.parse_args()

    if(args.source == args.input or args.source == None or args.input == None):
        sys.exit(10);
    source = args.source
    inp = args.input

#----------------------------------------------------------------------------------------
#                                 ERROR HANDLING CLASSES
#----------------------------------------------------------------------------------------
class Err_31(Exception):
    pass
class Err_32(Exception):
    pass
class Err_52(Exception):
    pass
class Err_53(Exception):
    pass
class Err_54(Exception):
    pass
class Err_55(Exception):
    pass
class Err_56(Exception):
    pass
class Err_57(Exception):
    pass
class Err_58(Exception):
    pass

#----------------------------------------------------------------------------------------
#                           CHECKING DATA TYPES
#----------------------------------------------------------------------------------------
class Data:
    #label:order number
    label_book = {}
    #TODO
    def check(att):
        #no literal given
        if(att.text == None):
            return ['symb', 'string', '']
        #variable
        if(re.match('^(GF|TF|LF)@[a-zA-Z_$&%*!?\-]([a-zA-Z_$&%*!?\-\d])*$', att.text)):
            tmp = att.text.split("@") #frame, name
            #[var, frame, name]
            return ['var', tmp[0], tmp[1]]
        #type
        typ = att.attrib['type'].lower()
        if(typ == 'type' and re.fullmatch('(int|string|bool)', att.text)):
            return ['type', att.text]

        #label
        if(typ == 'label' and re.match('^[a-zA-Z_$&%*!?\-]([a-zA-Z_$&%*!?\-\d])*$', att.text)):
            #[label, name]
            return ['label', att.text]

        #symbol
        if((re.fullmatch('^nil$', att.text) and typ == 'nil') or \
                (re.fullmatch('^(true|false)$', att.text.lower()) and typ == 'bool') or \
                (re.fullmatch('^(\+|\-)*\d+$', att.text) and typ == 'int') or \
                (re.fullmatch('^([^\\#\s]|\\\d{3})*$', att.text) and typ == 'string')):
            #[symb, type, value]
            if(typ == 'string'):
                att.text = re.sub(r'\\\d{3}', lambda x: chr(int(x.group(0).lstrip(r'\\'))), att.text)
            return ['symb', typ, att.text]

        #nothign matched
        raise Err_32

    #searches for a given key in lowcase and returns the key what can be
    #case insensitive
    def get_dict_key(dictionary, lowcase_key):
        return [key for key in dictionary.keys() if key.lower() == lowcase_key]

    def get_lit_type(text):
        if(re.fullmatch('^nil$', text)):
            return 'nil'
        if(re.fullmatch('^(true|false)$', text.lower())):
            return 'bool'
        if(re.fullmatch('^(\+|\-)*\d+$', text)):
            return 'int'
        else:#if(re.fullmatch('^(\\\d{3}|[^#\\\s])*$', text)):
            return 'string'

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
            if(self.length == 0):
                sys.exit(0)
            self.arr.sort(key=self.sort_key)
            self.last_instr = int(self.arr[self.length -1].attrib['order'])

            #checking instr attributes
            for instr in self.arr:
                if(not 'opcode' in instr.attrib or not 'order' in instr.attrib):
                    raise Err_32

            #checking negative order number
            #only the first because sorted array
            if(int(self.arr[0].attrib['order']) < 1):
                raise Err_32

            #checking duplicates
            if(len(self.arr) != len(set([x.attrib['order'] for x in self.arr]))):
                raise Err_32

            #checking missing 'instruction' tag
            if(len([x for x in xml_root if x.tag != 'instruction']) != 0):
                raise Err_32 
            #run through the code and save every label and their order number
            #check for redefinition and syntax correctness
            check_label_arr = [label for label in self.arr if label.attrib['opcode'].lower() == "label"]
            if(len(check_label_arr) != len(set(check_label_arr))):
                raise Err_52

            for lab in check_label_arr:
                #element lvl
                for arg in lab:
                    #instr arg lvl
                    if(arg.tag != "arg1"):
                        raise Err_52
                    if(arg.attrib['type'].lower() != "label"):
                        raise Err_52
                    #check label syntax
                    if(Data.check(arg)[0] != 'label'):
                        raise Err_52
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
            if(int(instr_order) > self.last_instr):
                raise StopIteration
            try:
                for x in self.arr:
                    if(int(x.attrib['order']) == int(instr_order)):
                        self.i = self.arr.index(x)
            except:
                raise Err_32

        def sort_key(self, e):
            #function for sorting by the order number of the instr
            try:
                return int(e.attrib['order'])
            except: #keyerror or valueerror
                raise Err_32

        def get_next_order_number(self):
            #function to get the next instrs order number
            #in the array
            try:
                return int(self.arr[self.i].attrib['order'])
            except:
                #last instr called this method, go behind that number
                return int(self.arr[self.i-1].attrib['order'])+1
    
##continuation of the XmlFile class
    #def __init__(self, source_path, input_path):
    #opening the source
    source_path = Arguments.source
    input_path = Arguments.inp

    if(source_path == 'stdin'):
        #sets stdin - etree can parse from stdin
        source_path = sys.stdin
    try:
        xml = ET.parse(source_path)
        xml_root = xml.getroot()
        instr_iter = InstructionIterator(xml_root)
    except FileNotFoundError:
        #file can't be opened
        sys.exit(11)
    except ET.ParseError:
        sys.exit(31)
    except Err_32:
        sys.exit(32)

    #checking header
    if(xml_root.attrib['language'].lower() != 'ippcode20'):
        sys.exit(32)

    #opening the input
    #input_path remains stdin if == stdin
    if(input_path != 'stdin'):
        try:
            input_file = open(input_path, 'r');
        except:
            sys.exit(11)

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
        if(f_type == "GF"):
            return v_key in Mem.gf
        if(f_type == "LF"):
            if(hasattr(Mem, 'lf')):
                return v_key in Mem.lf.top()
            raise Err_55
        if(f_type == "TF"):
            if(hasattr(Mem, 'tf')):
                return v_key in Mem.tf
            raise Err_55
    def create_local_frame():
        Mem.lf = Stack()
    def create_temp_frame():
        Mem.tf = {}
    def del_local_frame():
        del Mem.lf
    def del_temp_frame():
        del Mem.tf
    def push_tmp_to_loc():
        if(hasattr(Mem, "tf")):
            if(not hasattr(Mem, "lf")):
                Mem.create_local_frame()
            Mem.lf.push(Mem.tf)
        else:
            raise Err_55
    def pop_tmp_from_loc():
        if(hasattr(Mem, "lf")):
            Mem.tf = Mem.lf.pop()
            if(Mem.lf.size() == 0):
                Mem.del_local_frame()
        else:
            raise Err_55
    def declare_var(f_type, v_key):
        #global frame
        if(f_type == "GF"):
            if(Mem.in_frame("GF", v_key)):
                raise Err_52
            Mem.gf.update({v_key:['']})
        #local frame
        if(f_type == "LF"):
            if(hasattr(Mem, 'lf')):
                if(Mem.in_frame("LF", v_key)):
                    raise Err_52
                Mem.lf.top().update({v_key:['']})
            else:
                raise Err_55
        #temporary frame
        if(f_type == "TF"):
            if(hasattr(Mem, "tf")):
                if(Mem.in_frame("TF", v_key)):
                    raise Err_52
                Mem.tf.update({v_key:['']})
            else:
                raise Err_55

    def add_var(f_type, v_key, v_type, v_val):
        #global frame
        if(f_type == "GF"):
            if(Mem.in_frame("GF", v_key)):
                Mem.gf.update({v_key:[v_type, v_val]})
            else:
                raise Err_54
        #local frame
        if(f_type == "LF"):
            if(hasattr(Mem, 'lf')):
                if(Mem.in_frame("LF", v_key)):
                    Mem.lf.top().update({v_key:[v_type, v_val]})
                else:
                    raise Err_54
            else:
                raise Err_55
        #temporary frame
        if(f_type == "TF"):
            if(hasattr(Mem, "tf")):
                if(Mem.in_frame("TF", v_key)):
                    Mem.tf.update({v_key:[v_type, v_val]})
                else:
                    raise Err_54
            else:
                raise Err_55
    def get_var(f_type, v_key):
        if(Mem.in_frame(f_type, v_key)):
            #without error
            if(f_type == "GF"):
                ret = Mem.gf[v_key]
            elif(f_type == "LF"):
                ret = Mem.lf.top()[v_key]
            elif(f_type == "TF"):
                ret = Mem.tf[v_key]

            if(ret[0] == ''):
                raise Err_56
            return ret
        else:
            raise Err_54

#----------------------------------------------------------------------------------------
#                             CLASS HANDLING INSTRUCTIONS
#----------------------------------------------------------------------------------------
class Instr:
    instr_var_symb = ('MOVE', 'INT2CHAR', 'STRLEN', 'TYPE', 'NOT')
    instr_empty = ('CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', 'BREAK')
    instr_var = ('DEFVAR', 'POPS')
    instr_lab = ('CALL', 'LABEL', 'JUMP')
    instr_symb = ('PUSHS', 'WRITE', 'EXIT', 'DPRINT')
    instr_var_symb_symb = ('ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR', \
                            'STRI2INT', 'CONCAT', 'GETCHAR', 'SETCHAR')
    instr_var_typ = ('READ')
    instr_lab_symb_symb = ('JUMPIFEQ', 'JUMPIFNEQ')

    def get_symb_symb(symbol):
        if(symbol[0] == 'symb'):
            return symbol
        val = Mem.get_var(symbol[1], symbol[2])
        try:
            return ['symb', val[0], val[1]]
        except IndexError:
            return ['symb', val[0], '']

    def move(operands):
        #read the oprnd arr
        variable = operands[0]
        symbol = operands[1]
        if(variable[0] == 'var'):
            if(symbol[0] == 'symb'):
                Mem.add_var(variable[1], variable[2], symbol[1], symbol[2])
            elif(symbol[0] == 'var'):
                ret = Mem.get_var(symbol[1], symbol[2])
                if(ret == []):
                    raise Err_56
                Mem.add_var(variable[1], variable[2], ret[0], ret[1])
            else:
                raise Err_53
        else:
            raise Err_53
    
    def createframe(operands):
        Mem.create_temp_frame()

    def pushframe(operands):
        Mem.push_tmp_to_loc()
        Mem.del_temp_frame()

    def popframe(operands):
        Mem.pop_tmp_from_loc()
    
    def defvar(operands):
        variable = operands[0]
        #check var correctness

        if(variable[0] != 'var'):
            raise Err_53
        #checking var name existence in the given frame
        if(Mem.in_frame(variable[1], variable[2])):
            raise Err_52
        #variable declaration
        Mem.declare_var(variable[1], variable[2])

    def call(operands):
        label = operands[0]
        #check TODO last_instr > order number
        #saving the next instr number after the call
        Mem.call_stack.push(Files.instr_iter.get_next_order_number())
        try:
            Files.instr_iter.jump(Data.label_book[label[1]])
        except KeyError:
            raise Err_52

    def in_return(operands):
        if(Mem.call_stack.is_empty()):
            raise Err_56
        Files.instr_iter.jump(Mem.call_stack.pop())

    def pushs(operands):
        symbol = operands[0]
        Mem.data_stack.push(symbol)

    def pops(operands):
        f_type = operands[0][1]
        v_key = operands[0][2]
        if(Mem.data_stack.is_empty()):
            raise Err_56
        var = Instr.get_symb_symb(Mem.data_stack.pop())
        Mem.add_var(f_type, v_key, var[1], var[2])

    #6.4.3
    def aritmetic(operands, operation):
        var = operands[0]
        symb1 = Instr.get_symb_symb(operands[1])
        symb2 = Instr.get_symb_symb(operands[2])
        if(symb1[1] == 'int' and symb2[1] == 'int'):
            Mem.add_var(var[1], var[2], 'int', str(operation(int(symb1[2]), int(symb2[2]))))
        else:
            raise Err_53

    def add(operands):
        Instr.aritmetic(operands, lambda x, y : x+y)

    def sub(operands):
        Instr.aritmetic(operands, lambda x, y : x-y)

    def mul(operands):
        Instr.aritmetic(operands, lambda x, y : x*y)

    def idiv(operands):
        if(Instr.get_symb_symb(operands[2])[2] == '0'):
            raise Err_57
        Instr.aritmetic(operands, lambda x, y : x//y)

    def relational(operands,  operator):
        var = operands[0]
        symb1 = Instr.get_symb_symb(operands[1])
        symb2 = Instr.get_symb_symb(operands[2])

        if(symb1[1] == symb2[1]):
            if(symb1[1] == 'int'):
                symb1[2] = int(symb1[2])
            if(symb2[1] == 'int'):
                symb2[2] = int(symb2[2])
            Mem.add_var(var[1], var[2], 'bool', \
                    'true' if operator(symb1[2], symb2[2]) else 'false')
        else:
            raise Err_53

    def lt(operands):
        Instr.relational(operands, lambda x,y : x < y)

    def gt(operands):
        Instr.relational(operands, lambda x,y : x > y)

    def eq(operands):
        try:
            Instr.relational(operands, lambda x,y : x == y)
        except Err_53:
            var = operands[0]
            symb1 = Instr.get_symb_symb(operands[1])
            symb2 = Instr.get_symb_symb(operands[2])
            if(symb1[1] == 'nil' or symb2[1] == 'nil'):
                Mem.add_var(var[1], var[2], 'bool', 'true' if symb1[2] == symb2[2] else 'false')
            else:
                raise Err_53

    def in_and(operands):
        var = operands[0]
        symb1 = Instr.get_symb_symb(operands[1])
        symb2 = Instr.get_symb_symb(operands[2])

        if(symb1[1] == 'bool' and symb2[1] == 'bool'):
            Mem.add_var(var[1], var[2], 'bool', \
                    'true' if symb1[2] == 'true' and symb2[2] == 'true' else 'false')
        else:
            raise Err_53

    def in_or(operands):
        var = operands[0]
        symb1 = Instr.get_symb_symb(operands[1])
        symb2 = Instr.get_symb_symb(operands[2])

        if(symb1[1] == 'bool' and symb2[1] == 'bool'):
            Mem.add_var(var[1], var[2], 'bool', \
                    'false' if symb1[2] == 'false' and symb2[2] == 'false' else 'true')
        else:
            raise Err_53

    def in_not(operands):
        var = operands[0]
        symb = Instr.get_symb_symb(operands[1])

        if(symb[1] == 'bool'):
            Mem.add_var(var[1], var[2], 'bool', 'true' if symb[2] == 'false' else 'false')
    
    def int2char(operands):
        var = operands[0]
        symb = Instr.get_symb_symb(operands[1])
        if(symb[1] != 'int'):
            raise Err_53
        try:
            Mem.add_var(var[1], var[2], 'string', chr(int(symb[2])))
        except ValueError:
            raise Err_58

    def stri2int(operands):
        var = operands[0]
        symb1 = Instr.get_symb_symb(operands[1])
        symb2 = Instr.get_symb_symb(operands[2])

        if(symb1[1] != 'string' or symb2[1] != 'int'):
            raise Err_53
        try:
            Mem.add_var(var[1], var[2], 'int', str(ord(symb1[2][int(symb2[2])])))
        except IndexError:
            raise Err_58

    #6.4.4
    def read(operands):
        var = operands[0]
        typ = operands[1]

        if(Files.input_path == 'stdin'):
            try:
                inp = input()
            except EOFError:
                typ[1] = 'nil'
                inp = 'nil'
        else:
            inp = Files.input_file.readline()
            if(len(inp) == 0):
                #EOF
                typ[1] = 'nil'
                inp = 'nil'
            inp = inp.rstrip('\n')
        #V pripade chybneho nebo
        #chybejiciho vstupu bude do promenne ⟨var⟩ ulozena hodnota nil@nil.
        if(typ[1] == 'bool'):
            Mem.add_var(var[1], var[2], typ[1], 'true' if inp.lower() == 'true' else 'false')
        else:
            Mem.add_var(var[1], var[2], typ[1], inp)
            #rewriting the var if error
            if(Data.get_lit_type(inp) != typ[1]):
                Mem.add_var(var[1], var[2], 'nil', 'nil')

    def write(operands):
        symb = Instr.get_symb_symb(operands[0])
        if(symb[1] == 'nil'):
            print('', end='')
        else:
            print(symb[2], end='')

    #6.4.5
    def concat(operands):
        var = operands[0]
        symb1 = Instr.get_symb_symb(operands[1])
        symb2 = Instr.get_symb_symb(operands[2])

        if(symb1[1] != 'string' or symb2[1] != 'string'):
            raise Err_53
        Mem.add_var(var[1], var[2], 'string', symb1[2] + symb2[2])

    def strlen(operands):
        var = operands[0]
        symb = Instr.get_symb_symb(operands[1])

        Mem.add_var(var[1], var[2], 'int', len(symb[2]))

    def getchar(operands):
        var = operands[0]
        symb1 = Instr.get_symb_symb(operands[1])
        symb2 = Instr.get_symb_symb(operands[2])

        if(symb1[1] != 'string' or symb2[1] != 'int'):
            raise Err_53
        try:
            Mem.add_var(var[1], var[2], 'string', symb1[2][int(symb2[2])])
        except IndexError:
            raise Err_58

    def setchar(operands):
        var = operands[0]
        symb1 = Instr.get_symb_symb(operands[1])
        symb2 = Instr.get_symb_symb(operands[2])

        s = Mem.get_var(var[1], var[2])
        if(s[0] != 'string' or symb1[1] != 'int' or symb2[1] != 'string'):
            raise Err_53
        try:
            #turning string to list to change the char
            s = list(s[1])
            s[int(symb1[2])] = symb2[2][0]
            s = "".join(s)
            Mem.add_var(var[1], var[2], 'string', s)
        except IndexError:
            raise Err_58

    #6.4.6
    def in_type(operands):
        var = operands[0]
        try:
            symb = Instr.get_symb_symb(operands[1])
        except Err_56:
            #the variable is not inicialized
            symb = ['symb', '']
        Mem.add_var(var[1], var[2], 'string', symb[1])

    #6.4.7
    def label(operands):
        #functinality already done in the file traversing
        #process
        pass

    def jump(operands):
        lab = operands[0]
        try:
            Files.instr_iter.jump(Data.label_book[lab[1]])
        except KeyError:
            raise Err_52

    def jumpifeqneq(operands, operation):
        symb1 = Instr.get_symb_symb(operands[1])
        symb2 = Instr.get_symb_symb(operands[2])
        if(symb1[1] == symb2[1] or (symb1[1] == 'nil' or symb2[1] == 'nil')):
            if(operation(symb1[2], symb2[2])):
                try:
                    Files.instr_iter.jump(Data.label_book[operands[0][1]])
                except KeyError:
                    raise Err_52
        else:
            raise Err_53

    def jumpifeq(operands):
        Instr.jumpifeqneq(operands, lambda x,y : x == y)

    def jumpifneq(operands):
        Instr.jumpifeqneq(operands, lambda x,y : x != y)

    def in_exit(operands):
        symb = Instr.get_symb_symb(operands[0])
        if(symb[1] == 'int'):
            if((int(symb[2]) >= 0 and int(symb[2]) <= 49)):
                sys.exit(int(symb[2]))
            else:
                raise Err_57
        else:
            raise Err_53
    #6.4.8
    def dprint(operands):
        symb = Instr.get_symb_symb(operands[0])
        print(symb[1] + '@' + symb[2], file=sys.stderr)

    def in_break(operands):
        #do i want to implement this?
        pass

    instructions = {'MOVE':move, 'CREATEFRAME':createframe, \
            'PUSHFRAME':pushframe, 'POPFRAME':popframe, 'DEFVAR':defvar, \
            'CALL':call, 'RETURN':in_return, 'PUSHS':pushs, \
            'POPS':pops, 'ADD':add, 'SUB':sub, 'MUL':mul, \
            'IDIV':idiv, 'LT':lt, 'GT':gt, 'EQ':eq, \
            'AND':in_and, 'OR':in_or, 'NOT':in_not, \
            'INT2CHAR':int2char, 'STRI2INT':stri2int, 'READ':read, \
            'WRITE':write, 'CONCAT':concat, 'STRLEN':strlen, \
            'GETCHAR':getchar, 'SETCHAR':setchar, 'TYPE':in_type, \
            'LABEL':label, 'JUMP':jump, 'JUMPIFEQ':jumpifeq, \
            'JUMPIFNEQ':jumpifneq, 'EXIT':in_exit, 'DPRINT':dprint, \
            'BREAK':in_break}

#----------------------------------------------------------------------------------------
#                                   INTERPRET
#----------------------------------------------------------------------------------------
class Interpret:
    for instr in Files.instr_iter:
        code = instr.attrib['opcode'].upper() #case insensitive
        arg_arr = [] #instructin operands
        #load all the operands into the arr
        arg1 = False
        arg2 = False
        arg3 = False
        for a in instr:
            try:
                #checking attrib tag correctness
                if(a.tag == 'arg1' and not arg1):
                    arg1 = Data.check(a)
                    arg_arr.append(arg1)
                elif(a.tag == 'arg2' and not arg2):
                    arg2 = Data.check(a)
                elif(a.tag == 'arg3' and not arg3):
                    arg3 = Data.check(a)
                else:
                    raise Err_32
            except Err_32:
                sys.exit(32)
        #checking attrib tag order completion
        if(arg2):
            if(arg1):
                arg_arr.append(arg2)
            else:
                sys.exit(32)
        if(arg3):
            if(arg2):
                arg_arr.append(arg3)
            else:
                sys.exit(32)

        try:
            #calling instructions
            if code in Instr.instr_var_symb:
                if(len(arg_arr) != 2):
                    raise Err_32 #??
                if(arg_arr[0][0] != 'var' and (arg_arr[1][0] != 'var' or arg_arr[1][0] != 'symb')):
                    raise Err_53
            elif code in Instr.instr_empty:
                if(len(arg_arr) != 0):
                    raise Err_32
            elif code in Instr.instr_var:
                if(len(arg_arr) != 1):
                    raise Err_32
                if(arg_arr[0][0] != 'var'):
                    raise Err_53
            elif code in Instr.instr_lab:
                if(len(arg_arr) != 1):
                    raise Err_32
                if(arg_arr[0][0] != 'label'):
                    raise Err_53
            elif code in Instr.instr_symb:
                if(len(arg_arr) != 1):
                    raise Err_32
                if(arg_arr[0][0] != 'symb' and arg_arr[0][0] != 'var'):
                    raise Err_53
            elif code in Instr.instr_var_symb_symb:
                if(len(arg_arr) != 3):
                    raise Err_32
                if(arg_arr[0][0] != 'var' and (arg_arr[1][0] != 'var' or arg_arr[1][0] != 'symb') \
                        and (arg_arr[2][0] != 'var' or arg_arr[2][0] != 'symb')):
                    raise Err_53
            elif code in Instr.instr_var_typ:
                if(len(arg_arr) != 2):
                    raise Err_32
                if(arg_arr[0][0] != 'var' and arg_arr[1][0] != 'type'):
                    raise Err_53
            elif code in Instr.instr_lab_symb_symb:
                if(len(arg_arr) != 3):
                    raise Err_32
                if(arg_arr[0][0] != 'label' and \
                        (arg_arr[1][0] != 'var' or arg_arr[1][0] != 'symb')):
                    raise Err_53
            else:
                raise Err_32

            #calling the function of the instruction
            Instr.instructions[code](arg_arr)
        except Err_32:
            sys.exit(32)
        except Err_52:
            sys.exit(52)
        except Err_53:
            sys.exit(53)
        except Err_54:
            sys.exit(54)
        except Err_55:
            sys.exit(55)
        except Err_56:
            sys.exit(56)
        except Err_57:
            sys.exit(57)
        except Err_58:
            sys.exit(58)
        except StopIteration:
            break

    sys.exit(0);

#----------------------------------------------------------------------------------------
#                               TESTING/MAIN PART
#----------------------------------------------------------------------------------------
#f = XmlFile(args.source, args.input)
