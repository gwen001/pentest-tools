#!/usr/bin/php
<?php

function isIp( $str )
{
	return preg_match( '/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\z/', trim($str) );
}

function ip2bin( $ip )
{
	$bin = '';
	$tmp = explode( '.', $ip );
	foreach( $tmp as $t ) {
		$bin .= sprintf( '%08d', decbin($t) );
	}
	return $bin;
}

function bin2ip( $bin )
{
	return long2ip( bindec($bin) );
}

function subnet( $ip, $netmask )
{
	$b_ip = ip2bin($ip);
	//echo 'ADDRESS= '.$ip.' -> '.$b_ip."\n";
	$b_netmask = str_pad( str_pad('', $netmask, 1), 32, 0, STR_PAD_RIGHT );
	//echo 'NETMASK= '.$netmask.' -> '.$b_netmask."\n";
	$b_wildcard = str_pad( str_pad('', $netmask, 0), 32, 1, STR_PAD_RIGHT );
	$wildcard = bin2ip($b_wildcard);
	//echo 'WILDCARD= '.$wildcard.' -> '.$b_wildcard."\n";
	$b_network = $b_ip & $b_netmask;
	$network = bin2ip($b_network);
	//echo 'NETWORK= '.$network.' -> '.$b_network."\n";
	$b_broadcast = str_pad( substr($b_ip, 0, $netmask), 32, 1, STR_PAD_RIGHT );
	$broadcast = bin2ip( $b_broadcast );
	//echo 'BROADCAST= '.$broadcast.' -> '.$b_broadcast."\n";
	$b_min_host = str_pad( substr($b_network, 0, $netmask), 32, 0, STR_PAD_RIGHT );
	$min_host = bin2ip( $b_min_host );
	//echo 'MIN_HOST= '.$min_host.' -> '.$b_min_host."\n";
	$b_max_host = str_pad( substr($b_network, 0, $netmask), 32, 1, STR_PAD_RIGHT );
	$max_host = bin2ip( $b_max_host );
	//echo 'MAX_HOST= '.$max_host.' -> '.$b_max_host."\n";
	
	return [$min_host,$max_host];
}

function usage( $err=null ) {
	echo "Usage: php ".$_SERVER['argv'][0]." <start ip> <end ip> [<step>] || php ".$_SERVER['argv'][0]." <ip/mask> [<step>]\n";
	if( $err ) {
		echo 'Error: '.$err."!\n";
	}
	exit();
}



if( $_SERVER['argc'] < 2 || $_SERVER['argc'] > 4 ) {
	usage();
}

$mask = null;


if( strstr($_SERVER['argv'][1],'/') )
{
	if( $_SERVER['argc'] < 2 || $_SERVER['argc'] > 3 ) {
		usage();
	}
	
	list($start,$mask) = explode( '/', $_SERVER['argv'][1] );
	$mask = (int)$mask;
	$step = isset($_SERVER['argv'][2]) ? (int)$_SERVER['argv'][2] : 1;
	list($start,$end) = subnet( $start, $mask );
	$start = ip2long( $start );
	$end = ip2long( $end );
}
else
{
	if( $_SERVER['argc'] < 3 || $_SERVER['argc'] > 4 ) {
		usage();
	}
	
	if( !isIp($_SERVER['argv'][1]) ) {
		usage($_SERVER['argv'][1].' is not a valid ip address');
	}
	
	if( !isIp($_SERVER['argv'][2]) ) {
		usage($_SERVER['argv'][2].' is not a valid ip address');
	}
	
	$reverse = false;
	$start = ip2long( $_SERVER['argv'][1] );
	$end = ip2long( $_SERVER['argv'][2] );
	$step = isset($_SERVER['argv'][3]) ? (int)$_SERVER['argv'][3] : 1;
}

$t_ip = range( $start, $end, $step );
array_walk( $t_ip, create_function('&$v', '$v=long2ip($v);') );
echo implode( "\n", $t_ip )."\n";

exit();

?>