
var system = require('system');
var args = system.args;
//console.log(args.length);
var page = require('webpage').create();
page.settings.userAgent = 'Mozilla/5.0 (X11; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0';

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
};
page.onPrompt = function(str) {
    console.log('prompt() called: '+str);
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
}, 30000);
