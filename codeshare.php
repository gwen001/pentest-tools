#!/usr/bin/php
<?php

include( 'Utils.php' );

$n_child = 0;
$loop_sleep = 100;
$t_process = [];
$t_signal_queue = [];
$_thread_test_host = 5;
$_thread_test_url = 10;

$options = '';
$options .= 's:'; // string to search
$options .= 't:'; // threads
$t_options = getopt( $options );
//var_dump($t_options);
if( !count($t_options) ) {
	usage();
}

if( isset($t_options['s']) ) {
	$_string = $t_options['s'];
} else {
	usage( 'string to search is missing' );
}

if( isset($t_options['t']) ) {
	$_threads = $t_options['t'];
} else {
    $_threads = 10;
}
$max_child = $_threads;

posix_setsid();
declare( ticks=1 );
pcntl_signal( SIGCHLD, 'signal_handler' );

sleep( 1 );

test_ids( $_string );


function output( $txt, $color=null )
{
	if( $color ) {
		Utils::_print( $txt, $color );
	} else {
		echo $txt;
	}
}


function create_ids( $q )
{
    $len_id = 6;
    $t_ids = [];
    $t_alphabet = 'abcdefghijklmnupqrstovwxyzABCDEFGHIJKLMNOPRSTUVWXYZ0123456789';
    $l = strlen($t_alphabet) - 1;
    
    for( $i=0 ; $i<$q ; $i++ ) {
        $id = '';
        for( $j=0 ; $j<$len_id ; $j++ ) {
            $id .= $t_alphabet [ rand(0,$l) ];
        }
        $t_ids[] = $id;
    }

    return $t_ids;
}


function test_single( $_string )
{
    $id = create_ids( 1 );
    $url = 'https://codeshare.io/'.$id[0];
    //echo $url."\n";
    //exit();
    
    $c = curl_init();
	curl_setopt( $c, CURLOPT_URL, $url );
	curl_setopt( $c, CURLOPT_CONNECTTIMEOUT, 3 );
	//curl_setopt( $c, CURLOPT_SSL_VERIFYPEER, false );
	curl_setopt( $c, CURLOPT_USERAGENT, 'Mozilla/5.0 (X11; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/60.0' );
	curl_setopt( $c, CURLOPT_RETURNTRANSFER, true );
	$datas = curl_exec( $c );
	$t_infos = curl_getinfo( $c );
	//var_dump( $datas );
    //var_dump($t_infos);
	//exit();

    $url = $url ." (".strlen($datas).")\n";
    
	/*if( $t_infos['http_code'] != 200 ) {
    //output( $url, 'light_grey' );
        ;
    } else if( stristr($datas,$_string) === false ) {
        //output( $url, 'white' );
        ;
    } else {
        output( $url, 'light_green' );
    }*/

    if( stristr($datas,$_string) !== false ) {
        output( $url, 'light_green' );
        ;
    } elseif( strlen($datas) > 38950 ) {
        output( $url, 'white' );
        ;
    } else {
        //output( $url, 'light_grey' );
        ;
    }
}


function test_ids( $_string )
{
	global $n_child, $max_child, $t_process, $t_signal_queue;

	//for( $i=0 ; $i<10 ; $i++ )
	for( $i=0 ; 1 ; $i++ )
	{
		if( $n_child < $max_child )
		{
			$pid = pcntl_fork();
			
			if( $pid == -1 ) {
				// fork error
			} elseif( $pid ) {
				// father
				$n_child++;
				$t_process[$pid] = uniqid();
		        if( isset($t_signal_queue[$pid]) ){
		        	signal_handler( SIGCHLD, $pid, $t_signal_queue[$pid] );
		        	unset( $t_signal_queue[$pid] );
		        }
			} else {
				// child process
				test_single( $_string );
				exit( 0 );
			}
		}

		usleep( 5000 );
	}
	
	while( $n_child ) {
		// surely leave the loop please :)
		sleep( 1 );
	}
}


// http://stackoverflow.com/questions/16238510/pcntl-fork-results-in-defunct-parent-process
// Thousand Thanks!
function signal_handler( $signal, $pid=null, $status=null )
{
	global $t_process, $n_child, $t_signal_queue;

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


function usage( $err=null ) {
	echo "Usage: php codeshare.php -s <string> -t <threads>\n\n";
	echo "Options:\n";
	echo "\t-s\tstring to search\n";
	echo "\t-t\tthreads, default 10\n";
	echo "\nRecommended: php codeshare.php -s api_key -t 50";
	echo "\n";
	if( $err ) {
		echo 'Error: '.$err."!\n";
	}
	exit();
}
