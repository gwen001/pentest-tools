<?php

$n_child = 0;
$max_child = 10;
$loop_sleep = 100000;
$t_process = [];
$t_signal_queue = [];

// http://stackoverflow.com/questions/16238510/pcntl-fork-results-in-defunct-parent-process
// Thousand Thanks!
function signal_handler( $signal, $pid=null, $status=null )
{
	global $n_child, $t_process, $t_signal_queue;
	
	// If no pid is provided, Let's wait to figure out which child process ended
	$pid = (int)$pid;
	if( !$pid ){
		$pid = pcntl_waitpid( -1, $status, WNOHANG );
	}
	
	// Get all exited children
	while( $pid > 0 )
	{
		if( $pid && isset($t_process[$pid]) ) {
			// I don't care about exit status right now.
			//  $exitCode = pcntl_wexitstatus($status);
			//  if($exitCode != 0){
			//      echo "$pid exited with status ".$exitCode."\n";
			//  }
			// Process is finished, so remove it from the list.
			$n_child--;
			unset( $t_process[$pid] );
		}
		elseif( $pid ) {
			// Job finished before the parent process could record it as launched.
			// Store it to handle when the parent process is ready
			$t_signal_queue[$pid] = $status;
		}
		
		$pid = pcntl_waitpid( -1, $status, WNOHANG );
	}
	
	return true;
}


posix_setsid();
declare( ticks=1 );
pcntl_signal( SIGCHLD, 'signal_handler' );

$ssl_enable = true;
$t_status_colors = [
	0   => 'light_grey',
	200 => 'light_green',
	301 => 'blue',
	302 => 'blue',
	307 => 'blue',
	400 => 'light_grey',
	401 => 'purple',
	403 => 'purple',
	410 => 'purple',
	404 => 'red',
	500 => 'light_grey',
	503 => 'light_grey',
];


include( 'Utils.php' );

$t_host = file( $_SERVER['argv'][1], FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES );
$t_request = file( $_SERVER['argv'][2], FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES );
$t_regexp = array_slice( $_SERVER['argv'], 3 );
/*
var_dump( $t_host );
var_dump( $t_request );
var_dump( $t_regexp );
*/
$n_request = 0;

foreach( $t_request as $r ) 
{
	foreach( $t_host as $h )
	{
		if( $n_child < $max_child )
		{
			$pid = pcntl_fork();
			
			if( $pid == -1 ) {
				// fork error
			} elseif( $pid ) {
				// father
				$n_request++;
				$n_child++;
				$t_process[$pid] = uniqid();
		        if( isset($t_signal_queue[$pid]) ){
		        	$signal_handler( SIGCHLD, $pid, $t_signal_queue[$pid] );
		        	unset( $t_signal_queue[$pid] );
		        }
			} else {
				// child process
				usleep( $loop_sleep );
				ob_start();
				$http_code = (int)go( $r, $h );
				$result = ob_get_contents();
				ob_end_clean();
				if( $http_code == 200 || $http_code=302 ) {
					echo $result;
				}
				unset( $http_code );
				exit( 0 );
			}
		}

		usleep( $loop_sleep );
	}
}

echo $n_request." requests performed!\n";


function go( $r, $h )
{
	global $t_regexp, $t_status_colors, $ssl_enable;
	
	$url = 'http'.($ssl_enable ? 's': '').'://'.$h.'/'.ltrim($r,'/');
	
	$c = curl_init();
	curl_setopt( $c, CURLOPT_URL, $url );
	curl_setopt( $c, CURLOPT_HEADER, false );
	curl_setopt( $c, CURLOPT_TIMEOUT, 3 );
	curl_setopt( $c, CURLOPT_FOLLOWLOCATION, false );
	curl_setopt( $c, CURLOPT_RETURNTRANSFER, true );
	curl_setopt( $c, CURLOPT_HTTPHEADER, ['User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0','Cookie: xxxxxxx'] );
	$result = curl_exec( $c );
	$t_info = curl_getinfo( $c );
	curl_close( $c );
	
	/*if( $t_info['http_code'] == 200 ) {
		echo $result;
	}*/
	
	echo $url."\n";
	echo 'HTTP Code: ';
	Utils::_print( $t_info['http_code'], $t_status_colors[ $t_info['http_code'] ] );
	echo ', Length: ';
	Utils::_print( strlen($result), 'yellow' );
	echo "\n";
	
	foreach( $t_regexp as $e )
	{
		$regexp = '#'.$e.'#i';
		$a = preg_match( $regexp, $result, $matches );
		
		if( $a ) {
			$color = 'green';
		} else {
			$color = 'light_grey';
		}
		
		Utils::_print( $e, $color );
		echo ' , ';
	}
	
	echo "\n";

	return $t_info['http_code'];
}

exit();

?>