<?php

function _hash( $array, $glue='' )
{
	global $t_algo;

	$str = implode( $glue, $array );

	foreach( $t_algo as $a ) {
		echo strtoupper($a).': '.$str."\n";
		echo 'HASH: '.hash( $a, $str )."\n";
	}
}


function computePermutations( &$array, &$results, $start_i=0 )
{
	if ($start_i == sizeof($array)-1) {
		array_push($results, $array);
	}
	for ($i = $start_i; $i<sizeof($array); $i++) {
		//Swap array value at $i and $start_i
		$t = $array[$i];
		$array[$i] = $array[$start_i];
		$array[$start_i] = $t;

		//Recurse
		computePermutations($array, $results, $start_i+1);

		//Restore old order
		$t = $array[$i];
		$array[$i] = $array[$start_i];
		$array[$start_i] = $t;
	}
}

//var_dump($_SERVER['argv']);
$t_params = array_slice( $_SERVER['argv'], 1 );
//var_dump($t_params);
//var_dump($_SERVER['argv']);
$t_test = array();
computePermutations( $t_params, $t_test );
print_r( $t_test );
exit();
$cnt = count( $t_test );
//$t_glue = array( '', ',', ';', ':', '/', '|', '||', '.', '=', '@' );
$t_glue = array( ',', ';', ':', '|', '||' );
//$t_algo = array( 'md2','md4','md5','sha1','sha256','sha384','sha512','ripemd128','ripemd160','ripemd256','ripemd320','whirlpool','tiger128,3','tiger160,3','tiger192,3','tiger128,4','tiger160,4','tiger192,4','snefru','gost','adler32','crc32','crc32b','haval128,3','haval160,3','haval192,3','haval224,3','haval256,3','haval128,4','haval160,4','haval192,4','haval224,4','haval256,4','haval128,5','haval160,5','haval192,5','haval224,5','haval256,5' );
$t_algo = array( 'sha1' );

for( $i=0 ; $i<$cnt ; $i++ )
{
	$c = count( $t_test[$i] );

	for( $j=1 ; $j<$c ; $j++ )
	{
		$t_test[] = array_slice( $t_test[$i], $j );
	}
}
//var_dump( $t_test );


foreach( $t_test as $t )
{
	if( count($t) == 1 ) {
		_hash( $t );
	} else {
		foreach ($t_glue as $g) {
			_hash($t, $g);
		}
	}
}


exit();

?>
