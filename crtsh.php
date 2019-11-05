#!/usr/bin/php
<?php

function isSubdomain( $str )
{
	$str = strtolower( $str );

	if( preg_match('/[^0-9a-z_\-\.]/',$str) || preg_match('/[^0-9a-z]/',$str[0]) || preg_match('/[^a-z]/',$str[strlen($str)-1]) || substr_count($str,'.')<2 ) {
		return false;
	} else {
		return true;
	}
}


function extractDomain( $host )
{
	$tmp = explode( '.', $host );
	$cnt = count( $tmp );

	$domain = $tmp[$cnt-1];

	for( $i=$cnt-2 ; $i>=0 ; $i-- ) {
		$domain = $tmp[$i].'.'.$domain;
		if( strlen($tmp[$i]) > 3 ) {
			break;
		}
	}

	return $domain;
}


function usage( $err=null ) {
  echo 'Usage: '.$_SERVER['argv'][0]." <domain>\n";
  if( $err ) {
    echo 'Error: '.$err."\n";
  }
  exit();
}

if( $_SERVER['argc'] != 2 ) {
  usage();
}

$t_host = [];
$domain = $_SERVER['argv'][1];
$src = 'https://crt.sh/?q=%25.'.$domain;
$html = file_get_contents( $src );
//echo $html;

$doc = new DOMDocument();
$doc->preserveWhiteSpace = false;
@$doc->loadHTML( $html );

$xpath = new DOMXPath( $doc );
$table = $xpath->query( '//table' );
//var_dump($table->length);

if( $table->length >= 3 )
{
	$row = $xpath->query( 'tr', $table[2] );
	//var_dump( $row->length );
	
	foreach( $row as $r ) {
		$column = $xpath->query( 'td', $r );
		//var_dump( $column->length );
		if( $column->length == 6 ) {
			$h = str_replace( '*.', '', trim($column[4]->nodeValue) );
			if( isSubdomain($h) && extractDomain($h) == $domain ) {
				$t_host[] = $h;
			}
		}
	}
}

if( count($t_host) )
{
	$t_host = array_unique( $t_host );
	sort( $t_host );
	
	foreach( $t_host as $h ) {
		echo $h."\n";
	}
}

exit( 0 );

?>