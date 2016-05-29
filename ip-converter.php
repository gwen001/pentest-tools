<?php

function _echo( $str ) {
    global $prefix, $suffix;
    echo $prefix.$str.$suffix."\n";
}

function _ip2long( $ip ) {
    $tmp = explode( '.', $ip );
    $tmp = array_reverse( $tmp );
    $cnt = count( $tmp );
    $long = 0;
    
    for( $i=0,$n=0 ; $i<$cnt ; $i++,$n+=2 ) {
        $long += $tmp[$i] * pow(16,$n);
    }
        
    return $long;
}

function overflow( $n ) {
    return $n+256;
}

function usage( $err=null ) {
  echo 'Usage: '.$_SERVER['argv'][0]." <ip address> [<prefix>] [<suffix>]\n";
  if( $err ) {
    echo 'Error: '.$err."\n";
  }
  exit();
}

if( $_SERVER['argc'] < 2 || $_SERVER['argc'] > 4 ) {
  usage();
}

if( $_SERVER['argc'] > 2 ) {
    $prefix = $_SERVER['argv'][2];
} else {
    $prefix = '';
}
if( $_SERVER['argc'] > 3 ) {
    $suffix = $_SERVER['argv'][3];
} else {
    $suffix = '';
}

$ip = $_SERVER['argv'][1];
$t_ip = explode( '.', $ip );
//var_dump( $t_ip );
$t_overflow = array_map( "overflow", $t_ip );
//var_dump( $t_overflow );
$overflow = implode( '.', $t_overflow );

// dotted decimal
_echo( $ip );
// dotted decimal with overflow
_echo( $overflow );
// dotless decimal
_echo( _ip2long( $ip ) );
// dotless decimal with overflow
_echo( _ip2long( $overflow ) );
// dotted hexadecimal
_echo( strtoupper( sprintf("0x%02x.0x%02x.0x%02x.0x%02x", $t_ip[0], $t_ip[1], $t_ip[2], $t_ip[3]) ) );
// dotless hexadecimal
_echo( strtoupper( sprintf("0x%02x%02x%02x%02x", $t_ip[0], $t_ip[1], $t_ip[2], $t_ip[3]) ) );
// dotless hexadecimal with overflow
_echo( strtoupper( sprintf("0x%02x%02x%02x%02x", $t_overflow[0], $t_overflow[1], $t_overflow[2], $t_overflow[3]) ) );
// dotted octal
_echo( strtoupper( sprintf("%04o.%04o.%04o.%04o", $t_ip[0], $t_ip[1], $t_ip[2], $t_ip[3]) ) );
// dotted octal with padding
_echo( strtoupper( sprintf("%04o.%05o.%06o.%07o", $t_ip[0], $t_ip[1], $t_ip[2], $t_ip[3]) ) );
// mix - padded octal+decimal+hex+octal
_echo( strtoupper( sprintf("%09o.%d.0x%02x.%04o", $t_ip[0], $t_ip[1], $t_ip[2], $t_ip[3]) ) );
// mix - octal+hex+2 bytes wide dotless decimal
_echo( strtoupper( sprintf("%04o.0x%02x.%d", $t_ip[0], $t_ip[1], _ip2long($t_ip[2].'.'.$t_ip[3])) ) );
// IPv4 compatible address
_echo( '[::'.$ip.']' );
// IPv4 mapped address
_echo( '[::ffff:'.$ip.']' );

exit();

?>