
const puppeteer = require('puppeteer');
var args = process.argv.slice(2);

if( args.length < 2 || args.length > 5 ) {
	console.log( 'Usage: node xss.js <method> <url> [<post_params>] [<cookies> <domain>]');
	process.exit();
}

var method = Buffer.from(args[0], 'base64').toString()
var url = Buffer.from(args[1], 'base64').toString()

if( args.length > 3 ) {
	var post = Buffer.from(args[2], 'base64').toString()
} else {
	var post = '';
}

if( args.length >= 5 && args[3].length ) {
	var cookies = Buffer.from(args[3], 'base64').toString().split(';');
  var domain = Buffer.from(args[4], 'base64').toString()
  var t_cookies = []
  
	for( var i=0 ; i<cookies.length ; i++ ) {
		c = cookies[i].trim().split( '=' );
        t_cookies[i] = { 'domain':domain, 'name':c[0], 'value':c[1] }
	}
} else {
	var t_cookies = [];
	var domain = '';
}

// console.log(method)
// console.log(url)
// console.log(post)
// console.log(t_cookies)
// console.log(domain)

setTimeout( run, 0, url, method, post, t_cookies );

setTimeout(function() {
    process.exit();
}, 5000);


function run( url, method, post, t_cookies )
{
    const options = {
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-accelerated-2d-canvas',
          '--no-first-run',
          '--no-zygote',
          '--single-process', // <- this one doesn't works in Windows
          '--disable-gpu'
        ],
        headless: true
      };

    puppeteer.launch(options).then(async browser => {
    const page = await browser.newPage();
    // await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/60.0');
    
    if( t_cookies.length ) {
      for( i=0 ; i<t_cookies.length ; i++ ) {
        await page.setCookie( t_cookies[i] );
      }
    }

    if( post.length ) {
        await page.setRequestInterception( true );
        page.on('request', interceptedRequest => {
            interceptedRequest.continue({
                method: 'POST',
                postData: post,
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            });
        });
    }

    page.on('dialog', async dialog => {
        console.log('dialog() called: '+dialog.message());
        // await page.close()
        // await browser.close();
        process.exit();
    });

    await page.goto( url );
    // debug
    // console.log( await page.content() )
    await page.close()
    await browser.close();
    process.exit();
  });
}
