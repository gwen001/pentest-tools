<?php

class Utils
{
	const TMP_DIR = '/tmp/';
	const T_SHELL_COLORS = array(
		'nc' => '0',
		'black' => '0;30',
		'red' => '0;31',
		'green' => '0;32',
		'orange' => '0;33',
		'blue' => '0;34',
		'purple' => '0;35',
		'cyan' => '0;36',
		'light_grey' => '0;37',
		'dark_grey' => '1;30',
		'light_red' => '1;31',
		'light_green' => '1;32',
		'yellow' => '1;33',
		'light_blue' => '1;34',
		'light_purple' => '1;35',
		'light_cyan' => '1;36',
		'white' => '1;37',
	);


	public static function help( $error='' )
	{
		if( is_file(__DIR__.'/README.md') ) {
			$help = file_get_contents( __DIR__.'/README.md' )."\n";
			preg_match_all( '#```(.*)```#s', $help, $matches );
			if( count($matches[1]) ) {
				echo trim($matches[1][0])."\n\n";
			}
		} else {
			echo "No help found!\n";
		}

		if( $error ) {
			echo "Error: ".$error."!\n";
		}

		exit();
	}


	public static function isIp( $str ) {
		return filter_var( $str, FILTER_VALIDATE_IP );
	}


	public static function isEmail( $str )
	{
		return filter_var( $str, FILTER_VALIDATE_EMAIL );
	}


	public static function _print( $str, $color )
	{
		echo "\033[".self::T_SHELL_COLORS[$color]."m".$str."\033[0m";
	}
	public static function _println( $str, $color )
	{
		self::_print( $str, $color );
		echo "\n";
	}


	public static function _array_search( $array, $search, $ignore_case=true )
	{
		if( $ignore_case ) {
			$f = 'stristr';
		} else {
			$f = 'strstr';
		}

		if( !is_array($search) ) {
			$search = array( $search );
		}

		foreach( $array as $k=>$v ) {
			foreach( $search as $str ) {
				if( $f($v, $str) ) {
					return $k;
				}
			}
		}

		return false;
	}


	public static function isDomain( $str )
	{
		$str = strtolower( $str );

		if( preg_match('/[^0-9a-z_\-\.]/',$str) || preg_match('/[^0-9a-z]/',$str[0]) || preg_match('/[^a-z]/',$str[strlen($str)-1]) || substr_count($str,'.')>2 || substr_count($str,'.')<=0 ) {
			return false;
		} else {
			return true;
		}
	}


	public static function isSubdomain( $str )
	{
		$str = strtolower( $str );

		if( preg_match('/[^0-9a-z_\-\.]/',$str) || preg_match('/[^0-9a-z]/',$str[0]) || preg_match('/[^a-z]/',$str[strlen($str)-1]) || substr_count($str,'.')<2 ) {
			return false;
		} else {
			return true;
		}
	}


	public static function extractDomain( $host )
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


	public static function cleanOutput( $str )
	{
		$str = preg_replace( '#\[[0-9;]{1,4}m#', '', $str );

		return $str;
	}


	public static function _exec( $cmd )
	{
		$output = '';

		while( @ob_end_flush() );

		$proc = popen( $cmd, 'r' );
		while( !feof($proc) ) {
			$line = fread( $proc, 4096 );
			echo $line;
			$output .= $line;
			@flush();
		}

		return $output;
	}
}
