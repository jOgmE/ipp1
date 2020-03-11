<?php

#------------------------------------------------------------------------
#                           Global Variables
#------------------------------------------------------------------------
#directory where to look for the tests
$directory = "./";
#search not just in ^, but in his subdirs
$recur = 0;
#script file of the parser
$parser = "parse.php";
#script file of the interpret
$interpret = "interpret.py";
#mode sets what mode testing will happen
#0 - both
#1 - parse only
#2 - interpret only
$mode = 0;
$jexam_path = "/pub/courses/ipp/jexamxml/jexamxml";

$longopts = array(
    "help",
    "directory:",
    "parse-script:",
    "int-script:",
    "parse-only",
    "int-only",
    "jexamxml:",
    "recursive",
);

#------------------------------------------------------------------------
#                           DOING PROGRAM ARGUMENTS
#------------------------------------------------------------------------
$options = getopt("",$longopts);
if(array_key_exists('help', $options)){
    echo "help\n"; #TODO
    exit(0);
}
if(array_key_exists("directory", $options)){
    $directory = $options["directory"];
    if(!preg_match('/\/$/', $directory)){
        $directory = $directory.'/';
    }
}
if(array_key_exists("recursive", $options)){
    $recur = 1;
}
if(array_key_exists("parse-script", $options)){
    $parser = $options["parse-script"];
}
if(array_key_exists("int-script", $options)){
    $interpret = $options["int-script"];
}
if(array_key_exists("parse-only", $options)){
    if(array_key_exists("int-only", $options) or array_key_exists("int-script", $options)){
        echo "Wrong arguments - int-only and int-script can't be combined with mode parse-only";
        exit(1);
    }
    $mode = 1;
}
if(array_key_exists("int-only", $options)){
    if(array_key_exists("parse-only", $options) or array_key_exists("parse-script", $options)){
        echo "Wrong arguments - parse-only and parse-script can't be combined with mode int-only";
        exit(1);
    }
    $mode = 2;
}
if(array_key_exists("jexamxml=", $options)){
    $jexam_path = $options["jexamxml="];
}

#------------------------------------------------------------------------
#                           RUNNING PARSER TESTS
#------------------------------------------------------------------------
function test_parser($dir){
    global $recur;
    foreach(new DirectoryIterator($dir) as $file){
        if($file->isDot()) continue;
        if($recur and $file->isDir()) test_parser($dir.$file.'/');
        if(preg_match('/\.src$/', $file->getFilename())){
            $output = testing($dir.$file);
            echo $output;
        }
    }
}

function testing($file_name){
    global $parser;
    $command = escapeshellcmd($parser);
    $output; #throwaway
    $out = shell_exec('/usr/bin/php ' . $command . ' <' . $file_name, $output, $ret);
    if(!$ret){
        return $out;
    }
    return $ret;
}

test_parser($directory);

?>
