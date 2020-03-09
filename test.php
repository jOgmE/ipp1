<?php
$longopts = array(
    "help",
    "directory=:",
    "parse-script:",
    "int-script=:",
    "parse-only",
    "int-only",
    "jexamxml=:",
);

$options = getopt("",$longopts);
var_dump($options);
?>
