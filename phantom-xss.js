
var system = require('system');
var args = system.args;
var page = require('webpage').create();
page.settings.userAgent = 'Mozilla/5.0 (X11; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0';

var ext_exclude = [
	'css',
	'ico','bmp','jpeg','jpg','gif','svg','png',
	'eot','ttf','woff','woff2',
	'doc','docx','eot','pdf','xls','xlsx',
	'avi','mp4','mpeg','mpg',
	'wav','wmv',
	'rar','tar','tgz','zip',
];
var n_ext_exclude = ext_exclude.length;

// var mime_exclude = [
// 	'application/epub+zip','application/java-archive','application/msword','application/ogg','application/pdf','application/rtf','application/typescript',
// 	'application/vnd.amazon.ebook','application/vnd.apple.installer+xml','application/vnd.ms-excel','application/vnd.ms-fontobject','application/vnd.visio',
// 	'application/x-7z-compressed','application/x-abiword','application/x-bzip','application/x-bzip2','application/x-csh','application/x-rar-compressed',
// 	'application/x-sh','application/x-shockwave-flash','application/x-tar','application/zip','audio/3gpp','audio/3gpp2','audio/aac','audio/midi','audio/ogg',
// 	'audio/wav','audio/wave','audio/webm','audio/x-pn-wav','audio/x-wav','font/otf','font/ttf','font/woff','font/woff2','image/apng','image/bmp','image/gif',
// 	'image/jpeg','image/png','image/svg+xml','image/tiff','image/webp','image/x-icon','text/calendar','text/css','text/csv','video/3gpp','video/3gpp2',
// 	'video/mpeg','video/ogg','video/webm','video/x-msvideo'
// ];
// var n_mime_exclude = mime_exclude.length;

String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

page.onResourceRequested = function(requestData, request) {
	var parser = document.createElement('a');
	parser.href = requestData['url'];

	for( var i=0 ; i<n_ext_exclude ; i++ ) {
		if( parser['pathname'].endsWith('.'+ext_exclude[i]) ) {
			console.log('The url of the request is matching EXTENSION ('+ext_exclude[i]+'). Aborting: ' + requestData['url']);
			request.abort();
		}
	}
	
	// console.log( 'CT: '+requestData.headers['Content-Type'] );
	// for( var i=0 ; i<n_mime_exclude ; i++ ) {
	// 	if( requestData.headers['Content-Type'] == mime_exclude[i] ) {
	// 		console.log('The url of the request is matching CONTENT TYPE ('+mime_exclude[i]+'). Aborting: ' + requestData['url']);
	// 		request.abort();
	// 	}
	// }
};

if( args.length < 3 || args.length > 6 ) {
	console.log( 'Usage: phantomjs xss.js <method> <url> [<post_params>] [<cookies> <domain>]');
	phantom.exit();
}

var method = atob( args[1] );
var url = atob( args[2] );

if( args.length > 3 ) {
	var post = atob( args[3] );
} else {
	var post = '';
}

phantom.clearCookies();
if( args.length >= 5 ) {
	var cookies = atob( args[4] ).split(';');
	var domain = atob( args[5] );
	for( var i=0 ; i<cookies.length ; i++ ) {
		c = cookies[i].trim().split( '=' );
		//console.log( c[0]+' -> '+c[1] );
		phantom.addCookie( {'name':c[0],'value':c[1],'domain':'.'+domain} );
	}
} else {
	var cookies = '';
	var domain = '';
}

/*console.log( '========== DEBUG PHANTOM ==========' );
console.log( 'METHOD= '+method );
console.log( 'URL= '+url );
console.log( 'POST= '+post );
console.log( 'COOKIES= '+cookies );
console.log( 'DOMAIN= '+domain );*/


////////////////////////////////////////////////////////////////////////////////
page.onAlert = function(str) {
    console.log('alert() called: '+str);
    phantom.exit();
};
page.onConfirm = function(str) {
    console.log('confirm() called: '+str);
    phantom.exit();
};
page.onPrompt = function(str) {
    console.log('prompt() called: '+str);
    phantom.exit();
};
////////////////////////////////////////////////////////////////////////////////


function run( page, method, url, post )
{
	console.log( 'Testing: '+url );
    page.open( url, method, post, function (status) {
    	//console.log("Status: " + status);
    	//page.render('poc.png');
    	/*console.log("Status: " + status);
		var cookies = page.cookies;
		console.log('Listing cookies:');
		for(var i in cookies) {
			console.log(cookies[i].name + '=' + cookies[i].value);
		}*/
		phantom.exit();
	});
}


setTimeout( run(page,method,url,post), 0 );

setTimeout(function() {
	phantom.exit();
}, 5000);
