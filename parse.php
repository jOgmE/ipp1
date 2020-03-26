<?php

$line_counter = 0;

/* Function what checks program arguments
 */
function check_arguments(){
    global $argc, $argv;
    //arguments
    if($argc == 2){
        if($argv[1] == "--help"){
            echo "Skript typu filtr načte ze standardního vstupu zdrojový kód v IPP-code20, zkontroluje lexikální a syntaktickou správnost kódu a vypíše na standardnívýstup XML reprezentaci programu dle specifikace. Tento skript bude pracovat s těmito parametry:\n--help vypise tuto spravu\n"; //TODO
            exit(0);
        }else{
            fprintf(STDERR, "Wrong argument given\n");
            exit(10);
        }
    }elseif($argc == 1){}else{
            fprintf(STDERR, "Too much arguments given\n");
            exit(10);
    }
}

/* Checks the first line and
 * returns a non first line split by
 * ws in an arr
 */
function loadLine(){
    global $line_counter;
    global $output;

    if(feof(STDIN)){
        return fgets(STDIN);
        //exit(0);
    }
    $line = fgets(STDIN);

    //deleting comments
    $comment = preg_split('/#/', trim($line));
    if(strlen($comment[0]) == 0){
        return loadLine();
    }
    //counter for checking starting '.ippcode20'
    $line_counter = $line_counter +1;
    //split into array
    $line = trim($comment[0]);
    $arr = preg_split('/(\s+)/',$line);

    //checking first line correctness
    if($line_counter == 1){
        $ipp_code = strtolower($arr[0]);
        if(!preg_match('/.ippcode20/',$ipp_code)){
            //error
            fprintf(STDERR, "chybná nebo chybějící hlavička ve zdrojovém kódu zapsaném v IPPcode20\n");
            exit(21);
        }
        $output->write_program();
        return loadLine();
    }else{
        return $arr;
    }
}

/* Checking syntax/lex of the line
 * arg line > array of words in the line
 */
function parse($line){
    global $output;
    global $line_counter;

    $instr = strtolower($line[0]);
    
    //Decide what function is on the line
    //and do the proper checking
    //then write it to the xml
    switch($instr){
        case "move":
        case "int2char":
        case "strlen":
        case "type":
        case "not":
            if(count($line) == 3 && check_variable_name($line[1]) && check_symbol_name($line[2])){
                $output->write_instr($line_counter-1, strtoupper($instr));
                $output->write_arg(1,"var",$line[1]);
                if(check_variable_name($line[2])){
                    $output->write_arg(2,"var",$line[2]);
                }else{
                    $output->write_arg(2, preg_replace('/@\S*$/', "",$line[2]), htmlspecialchars(preg_replace('/^(string|int|bool|nil)@/', "", $line[2])));
                }
                $output->end_element(); //end of instruction
                break;
            }
            err_23(); //exit
        case "createframe":
        case "pushframe":
        case "popframe":
        case "return":
        case "break":
            if(count($line) == 1){
                $output->write_instr($line_counter-1, strtoupper($instr));
                $output->end_element();
                break;
            }
            err_23(); //exit
        case "defvar":
        case "pops":
            if(count($line) == 2 && check_variable_name($line[1])){
                $output->write_instr($line_counter-1, strtoupper($instr));
                $output->write_arg(1,"var",$line[1]);
                $output->end_element(); //end of instruction
                break;
            }
            err_23(); //exit
        case "call":
        case "label":
        case "jump":
            if(count($line) == 2 && check_label_name($line[1])){
                $output->write_instr($line_counter-1, strtoupper($instr));
                $output->write_arg(1,"label",$line[1]);
                $output->end_element(); //end of instruction
                break;
            }
            err_23(); //exit
        case "pushs":
        case "write":
        case "exit":
        case "dprint":
            if(count($line) == 2 && check_symbol_name($line[1])){
                $output->write_instr($line_counter-1, strtoupper($instr));
                if(check_variable_name($line[1])){
                    $output->write_arg(1,"var",$line[1]);
                }else{
                    $output->write_arg(1, preg_replace('/@\S*$/', "",$line[1]), htmlspecialchars(preg_replace('/^(string|int|bool|nil)@/', "", $line[1])));
                }
                $output->end_element(); //end of instruction
                break;
            }
            err_23(); //exit
        case "add":
        case "sub":
        case "mul":
        case "idiv":
        case "lt":
        case "gt":
        case "eq":
        case "and":
        case "or":
        case "stri2int":
        case "concat":
        case "getchar":
        case "setchar":
            if(count($line) == 4 && check_variable_name($line[1]) && check_symbol_name($line[2]) && check_symbol_name($line[3])){
                $output->write_instr($line_counter-1, strtoupper($instr));
                $output->write_arg(1,"var",$line[1]);
                if(check_variable_name($line[2])){
                    $output->write_arg(2,"var",$line[2]);
                }else{
                    $output->write_arg(2, preg_replace('/@\S*$/', "",$line[2]), htmlspecialchars(preg_replace('/^(string|int|bool|nil)@/', "", $line[2])));
                }
                if(check_variable_name($line[3])){
                    $output->write_arg(3,"var",$line[3]);
                }else{
                    $output->write_arg(3, preg_replace('/@\S*$/', "",$line[3]), htmlspecialchars(preg_replace('/^(string|int|bool|nil)@/', "", $line[3])));
                }
                $output->end_element(); //end of instruction
                break;
            }
            err_23(); //exit
        case "read":
            if(count($line) == 3 && check_variable_name($line[1]) && check_type($line[2])){
                $output->write_instr($line_counter-1, strtoupper($instr));
                $output->write_arg(1,"var",$line[1]);
                $output->write_arg(2,$line[2],"");
                $output->end_element(); //end of instruction
                break;
            }
            err_23(); //exit
        case "jumpifeq":
        case "jumpifneq":
            if(count($line) == 4 && check_label_name($line[1]) && check_symbol_name($line[2]) && check_symbol_name($line[3])){
                $output->write_instr($line_counter-1, strtoupper($instr));
                $output->write_arg(1,"label",$line[1]);
                if(check_variable_name($line[2])){
                    $output->write_arg(2,"var",$line[2]);
                }else{
                    $output->write_arg(2, preg_replace('/@\S*$/', "",$line[2]), htmlspecialchars(preg_replace('/^(string|int|bool|nil)@/', "", $line[2])));
                }
                if(check_variable_name($line[3])){
                    $output->write_arg(3,"var",$line[3]);
                }else{
                    $output->write_arg(3, preg_replace('/@\S*$/', "",$line[3]), htmlspecialchars(preg_replace('/^(string|int|bool|nil)@/', "", $line[3])));
                }
                $output->end_element(); //end of instruction
                break;
            }
            err_23(); //exit
        default:
            //couldn't parse the instruction
            err_22(); //exit
            break;
    }
    return 0;
}

/* Returns 1 on succ
 * and 0 on failure
 */
function check_literal($name){
    if(preg_match('/^nil@nil$/', $name)){   //nil
        return 1;
    }else if(preg_match('/^bool@(true|false)$/', $name)){   //bool
        return 1;
    }else if(preg_match('/^int@(\+|\-)*\d+$/', $name)){  //int
        return 1;
    }else if(preg_match('/^string@([^\\#\s]|\\\d{3})*$/', $name)){  //string
        return 1;
    }else{  //error
        return 0;
    }
}

/* Returns 1 on succ
 * and 0 on failure
 */
function check_variable_name($name){
    return preg_match('/^(GF|TF|LF)@[a-zA-Z_$&%*!?\-]([a-zA-Z_$&%*!?\-\d])*$/',$name);
}

/* Returns 1 on succ
 * and 0 on failure
 */
function check_symbol_name($name){
    return check_variable_name($name) || check_literal($name);
}

/* Returns 1 on succ
 * and 0 on failure
 */
function check_label_name($name){
    return preg_match('/^[a-zA-Z_$&%*!?\-]([a-zA-Z_$&%*!?\-\d])*$/',$name);
}

function check_type($name){
    $name = strtolower($name);
    return preg_match('/^(int|string|bool)$/', $name);
}

function err_22(){
    fprintf(STDERR, "neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode20\n");
    exit(22);
}
function err_23(){
    fprintf(STDERR, "jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode20\n");
    exit(23);
}

/*-----------------------------------------------------------------------------------
 *                      --  part    XML --
 *-----------------------------------------------------------------------------------
 */

class Output_xml{
    private $xw;
    private $res;

    //constructor of the class
    public function __construct(){
        $this->xw = xmlwriter_open_memory();
        xmlwriter_set_indent($this->xw, 1);
        $this->res = xmlwriter_set_indent_string($this->xw, '    ');

        xmlwriter_start_document($this->xw, '1.0', 'UTF-8');
    }

    function content($text){
        xmlwriter_text($this->xw, $text);
    }
    function start_element($name){
        xmlwriter_start_element($this->xw, $name);
    }
    function start_attr($name){
        xmlwriter_start_attribute($this->xw, $name);
    }
    function end_attr(){
        xmlwriter_end_attribute($this->xw);
    }
    function end_element(){
        xmlwriter_end_element($this->xw);
    }
    function end_doc(){
        xmlwriter_end_document($this->xw);
    }
    public function write_xml_to_output(){
        echo xmlwriter_output_memory($this->xw);
    }

    //NOT ENDED tags
    function write_instr($id, $code){
        $this->start_element("instruction");
        $this->start_attr("order");
        $this->content($id);
        $this->end_attr();
        $this->start_attr("opcode");
        $this->content($code);
        $this->end_attr();
    }
    function write_program(){
        $this->start_element("program");
        $this->start_attr("language");
        $this->content("IPPcode20");
        $this->end_attr();
    }
    //ENDED tag
    function write_arg($num, $type, $text){
        $this->start_element("arg".$num);
        $this->start_attr("type");
        $this->content($type);
        $this->end_attr();
        if(strlen($text) != 0){
            $this->content($text);
        }
        $this->end_element();
    }
}

/*-----------------------------------------------------------------------------------
 *                      --  part    MAIN --
 *-----------------------------------------------------------------------------------
 */

check_arguments();

$output = new Output_xml;

//pls rewrite his while and the ending with eof
while(($line = loadLine()) !== false){
    parse($line);
}


//ending program tag
$output->end_element();
//ending xml document
$output->end_doc();
//write xml to output
$output->write_xml_to_output();

?>
