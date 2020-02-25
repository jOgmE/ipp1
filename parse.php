<?php

$line_counter = 0;

function check_arguments(){
    //arguments
    if($argc == 2){
        if($argv[1] == "--help"){
            echo "put help here"; //TODO
            exit(0);
        }else{
            fprintf(STDERR, "put error here\n");
            exit(10);
        }
    }elseif($argc ==1){}else{
            fprintf(STDERR, "put error here\n");
            exit(10);
    }
}

/* Checks the first line and
 * returns a non first line split by
 * ws in an arr
 */
function loadLine(){
    global $line_counter;

    $line = fgets(STDIN);
    if(feof(STDIN)){
        exit(0);
    }

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
        return loadLine();
    }else{
        return $arr;
    }
}

/* Checking syntax/lex of the line
 * arg line > array of words in the line
 */
function parse($line){
    $instr = strtolower($line[0]);
    //testing
    var_dump($instr);
    switch($instr){
        case "move":
        case "int2char":
        case "strlen":
        case "type":
            if(count($line) == 3 && check_variable_name($line[1]) && check_symbol_name($line[2])){
                break;
            }
            err_23(); //exit
        case "createframe":
        case "pushframe":
        case "popframe":
        case "return":
        case "break":
            if(count($line) == 1){
                break;
            }
            err_23(); //exit
        case "defvar":
        case "pops":
            if(count($line) == 2 && check_variable_name($line[1])){
                break;
            }
            err_23(); //exit
        case "call":
        case "label":
        case "jump":
            if(count($line) == 2 && check_label_name($line[1])){
                break;
            }
            err_23(); //exit
        case "pushs":
        case "write":
        case "exit":
        case "dprint":
            if(count($line) == 2 && check_symbol_name($line[1])){
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
        case "not":
        case "stri2int":
        case "concat":
        case "getchar":
        case "setchar":
            if(count($line) == 4 && check_variable_name($line[1]) && check_symbol_name($line[2]) && check_symbol_name($line[3])){
                break;
            }
            err_23(); //exit
        case "read":
            if(count($line) == 3 && check_variable_name($line[1]) && check_type($line[2])){
                break;
            }
            err_23(); //exit
        case "jumpifeq":
        case "jumpifneq":
            if(count($line) == 4 && check_label_name($line[1]) && check_symbol_name($line[2]) && check_symbol_name($line[3])){
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

//pls rewrite his while and the ending with eof
while(1){
    parse(loadLine());
}

?>
