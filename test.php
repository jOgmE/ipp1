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
    $passed = true;
    #iterating through files in the directory
    #if global variable is set, then going recursive
    foreach(new DirectoryIterator($dir) as $file){
        #skipping dot dirs
        if($file->isDot()) continue;
        #going recursive - first match dir
        if($recur and $file->isDir()) test_parser($dir.$file.'/');
        #testing .src files
        if(preg_match('/\.src$/', $file->getFilename())){
            $output = testing($dir.$file);
            $plain_file_name = preg_replace('/\.src$/', '', $file->getPathname());

            ## GENERATING TMP FILES FOR COMPARISION
            #return code file
            $rc_file = fopen($plain_file_name . '.tmprc', "w");
            fwrite($rc_file, intval($output[1]));
            fclose($rc_file);
            $passed = check_difference($plain_file_name.'.rc', $plain_file_name.'.tmprc');

            #checking out file only when RC is 0
            if($output[1] == 0){
                #output file
                $xml_file = fopen($plain_file_name . '.tmpout', "w");
                fwrite($xml_file, $output[0]);
                fclose($xml_file);
                $passed = check_difference($plain_file_name.'.out', $plain_file_name.'.tmpout');
            }

            ## DELETING THE TMP FILES
            shell_exec(sprintf("rm -f %s/*.tmprc %s/*.tmpout", $file->getPath(), $file->getPath()));

            #printing out the results
            printf("Testing %s >>> %s\n", $plain_file_name, $passed ? "Passed" : "Failed");
        }
    }
}

#function to test parser
#return an array where (xml_output, return_code)
function testing($file_name){
    global $parser;
    $command = escapeshellcmd($parser);
    $output = '';
    $rc = 0;
    $out = exec("/usr/bin/php ". $command . " <" . $file_name . " 2> /dev/null", $output, $rc);
    $out = implode("\n", $output) . "\n";
    if($rc != 0){
        return array('',$rc);
    }
    return array($out, 0);
}

#the function test the difference between two files
#returns:
#  false - NOT identical files
#  true  - identical files
function check_difference($file1, $file2){
    $out = shell_exec("diff " . $file1 . ' ' . $file2);
    return empty($out);
}

test_parser($directory);

?>
