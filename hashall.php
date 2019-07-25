<?php

$str = $_SERVER['argv'][1];

$t_algo = [
  'md2','md4','md5','sha1','sha256','sha384','sha512',
  'ripemd128','ripemd160','ripemd256','ripemd320',
  'whirlpool',
  'tiger128,3','tiger160,3','tiger192,3','tiger128,4','tiger160,4','tiger192,4',
  'snefru','gost','adler32','crc32','crc32b',
  'haval128,3','haval160,3','haval192,3','haval224,3','haval256,3','haval128,4','haval160,4','haval192,4',
  'haval224,4','haval256,4','haval128,5','haval160,5','haval192,5','haval224,5','haval256,5'
];

foreach( $t_algo as $a ) {
  echo $a." -> ".hash( $a, $str )."\n";
}

?>