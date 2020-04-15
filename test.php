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
$jexam_path = "/pub/courses/ipp/jexamxml/jexamxml.jar";

$pass = 0;
$fail = 0;

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
    echo "usage:\nphp7.4 test.php [--directory=dirpath] [--parse-script=script]
             [--int-script=script] [--parse-only] [--int-only] [--jexamxml=script]
             [--recursive]\n";
    exit(0);
}
if(array_key_exists("directory", $options)){
    $directory = $options["directory"];
    if(!file_exists($directory)){
        exit(11);
    }
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
if(array_key_exists("jexamxml", $options)){
    $jexam_path = $options["jexamxml"];
}

#checking files existence
if(!file_exists($parser)){
    exit(11);
}
if(!file_exists($interpret)){
    exit(11);
}
if(!file_exists($jexam_path)){
    exit(11);
}

#function to run parser
#return an array where (xml_output, return_code)
function run_par($file_name){
    global $parser;
    $command = escapeshellcmd($parser);
    $output = '';
    $rc = 0;
    $out = exec("php7.4 ". $command . " <" . $file_name . " 2> /dev/null", $output, $rc);
    $out = implode("\n", $output) . "\n";
    if($rc != 0){
        return array('',$rc);
    }
    return array($out, 0);
}

#function to run interpret
#return an array where (xml_output, return_code)
function run_inter($src, $in){
    global $interpret;
    $command = escapeshellcmd($interpret);
    $output = '';
    $rc = 0;
    $out = exec("python3.8 ". $command ." --source=".$src." --input=".$in, $output, $rc);
    $out = implode("\n", $output);
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
    $out = shell_exec("diff -w " . $file1 . ' ' . $file2);
    return empty($out);
}
function check_xml_difference($file1, $file2){
    global $jexam_path;
    $out = shell_exec("java -jar ". $jexam_path ." ". $file1." ".$file2." | grep 'are identical'");
    return !empty($out);
}

function test($dir){
    global $recur;
    global $mode;
    global $pass;
    global $fail;
    $passed = true;

    #html
    $table = "<table><tr><th id=dir>".$dir."</th><th id=state>Parser</th><th id=state>Interpret</th></tr>";
    $rec_table = "";

    #iterating through files in the directory
    #if global variable is set, then going recursive
    foreach(new DirectoryIterator($dir) as $file){
        #skipping dot dirs
        if($file->isDot()) continue;
        #going recursive - first match dir
        if($recur and $file->isDir()) $rec_table = $rec_table.test($dir.$file.'/');
        #testing .src files
        if(preg_match('/\.src$/', $file->getFilename())){
            $plain_file_name = preg_replace('/\.src$/', '', $file->getPathname());

            #checking existence of .in and .out
            if(!file_exists($plain_file_name.'.out')){
                $gen_file = fopen($plain_file_name.'.out', 'w');
                if(!$gen_file){
                    exit(12);
                }
                fclose($gen_file);
            }
            if(!file_exists($plain_file_name.'.in')){
                $gen_file = fopen($plain_file_name.'.in', 'w');
                if(!$gen_file){
                    exit(12);
                }
                fclose($gen_file);
            }
            if(!file_exists($plain_file_name.'.rc')){
                $gen_file = fopen($plain_file_name.'.rc', 'w');
                if(!$gen_file){
                    exit(12);
                }
                fwrite($gen_file, 0);
                fclose($gen_file);
            }

            #parser and both
            if($mode < 2){
                $output = run_par($plain_file_name.'.src');
            }else if($mode == 2){
                $output = run_inter($plain_file_name.".src", $plain_file_name.".in");
            }

            ## GENERATING TMP FILES FOR COMPARISION
            #return code file
            $rc_file = fopen($plain_file_name . '.tmprc', "w");
            if(!$rc_file){
                exit(12);
            }
            fwrite($rc_file, intval($output[1])."\n");
            fclose($rc_file);
            $passed = check_difference($plain_file_name.'.rc', $plain_file_name.'.tmprc');

            #checking out file only when RC is 0
            if($output[1] == 0){
                #output file
                $xml_file = fopen($plain_file_name . '.tmpout', "w");
                if(!$xml_file){
                    exit(12);
                }
                fwrite($xml_file, $output[0]);
                fclose($xml_file);
                
                #runnning interpret when BOTH
                if($mode == 0){
                    $output = run_inter($plain_file_name.".tmpout", $plain_file_name.".in");
                    #return code file
                    $rc_file = fopen($plain_file_name . '.tmprc', "w");
                    if(!$rc_file){
                        exit(12);
                    }
                    fwrite($rc_file, intval($output[1])."\n");
                    fclose($rc_file);
                    $passed = check_difference($plain_file_name.'.rc', $plain_file_name.'.tmprc');

                    if($output[1] == 0){
                        #writing output file again
                        $xml_file = fopen($plain_file_name . '.tmpout', "w");
                        if(!$xml_file){
                            exit(12);
                        }
                        fwrite($xml_file, $output[0]);
                        fclose($xml_file);
                    }
                }

                if($output[1] == 0){
                    if($mode != 1){
                        $passed = check_difference($plain_file_name.'.out', $plain_file_name.'.tmpout');
                    }else{
                        $passed = check_xml_difference($plain_file_name.'.out', $plain_file_name.'.tmpout');
                    }
                }
            }

            ## DELETING THE TMP FILES
            #shell_exec(sprintf("rm -f %s/*.tmprc %s/*.tmpout", $file->getPath(), $file->getPath()));

            #counting the results
            if($passed){
                $pass += 1;
            }else{
                $fail += 1;
            }

            #generating html output (and saving for later usage)
            $table = $table."<tr><td>".$file->getFilename()."</td>";
            if($mode == 0){
                if($passed){
                    $table = $table."<td id=pass>PASSED</td><td id=pass>PASSED</td></tr>";
                }else{
                    $table = $table."<td id=fail>FAILED</td><td id=fail>FAILED</td></tr>";
                }
            }
            elseif($mode == 1){
                if($passed){
                    $table = $table."<td id=pass>PASSED</td><td>-</td></tr>";
                }else{
                    $table = $table."<td id=fail>FAILED</td><td>-</td></tr>";
                }
            }
            elseif($mode == 2){
                if($passed){
                    $table = $table."<td>-</td><td id=pass>PASSED</td></tr>";
                }else{
                    $table = $table."<td>-</td><td id=fail>FAILED</td></tr>";
                }
            }
            #command line printout
            #printf("Testing %s >>> %s\n", $plain_file_name, $passed ? "Passed" : "Failed");
        }
    }

    #when dir has only dirs = no test output
    if($table == "<table><tr><th id=dir>".$dir."</th><th id=state>Parser</th><th id=state>Interpret</th></tr>"){
        return $rec_table;
    }
    #new tests were added to the output
    return $rec_table.$table."</table>";
}

$html_tables = test($directory);

$html_page = "
<!DOCTYPE html>
<head>
    <title>IPP projekt</title>
<style>
table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
    text-align: center;
    padding: 5px;
}
table{
    margin: auto;
    width: 80%;
    background: rgba(255,255,255,0.08);
    border-radius: 10px;
    margin-bottom: 1%;
}
th, td {
    position:relative;
    padding-left: 15px;
    padding-right: 15px;
    color: rgba(255,255,255,0.7);
}
th{
    font-weight:bold;
    border-bottom-width:medium;
    background:rgba(255,255,255,0.09);
}
td{
    border-bottom-width:thin;
}
#pass{
    font-weight: bold;
    opacity: 90%;
    color: #3BD16F;
}
#fail{
    font-weight: bold;
    opacity: 90%;
    color: #DB3A34;
}
#dir{
    position:relative;
    width:60%;
}
#state{
    position:relative;
    width:20%;
}
body{
    background: #121212;
}
</style>
</head>

<body>
    <h1 style=\"text-align:center;padding:2%;color:white;opacity:80%;\"><span style=\"margin-right:5%\">Total tests: ".strval($fail+$pass)."</span>
        <span style=\"margin-right:5%\">Passed: <span id=pass>".strval($pass)."</span></span>
        <span style=\"margin-right:5%\">Failed: <span id=fail>".strval($fail)."</span></span>
    </h1>
".$html_tables."</body>";

echo $html_page;

?>
