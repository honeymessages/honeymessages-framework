/*
* This software uses open-source projects:
* Fingerprint2 https://github.com/fingerprintjs/fingerprintjs
* MurmurHash3 by Karan Lyons (https://github.com/karanlyons/murmurHash3.js)
*/

var FINGERPRINTJS_VERSION = "3.4.1";
var FINGERPRINTJS_ENDPOINT = "fingerprint/";

/**
 * Sends the fingerprint and additional data to an API endpoint.
 */
function reportFingerprintJs(results) {
	function getCookie(a) {
		var b = document.cookie.match('(^|;)\\s*' + a + '\\s*=\\s*([^;]+)');
		return b ? b.pop() : '';
	}

	let components = []
	components.push({"fingerprintjs_version": FINGERPRINTJS_VERSION}); // version of fingerprint JS
	components.push({"visited_url": window.location.href}); // the url that issued the fingerprint
	components.push({"visitor_id": results.visitorId}); // the id ("hash") of the collected data
	components.push({"components": {...results.components}});

	// prepare xhr
	let xhr = new XMLHttpRequest();
	let url = window.location.pathname;
	url = url.endsWith("/") ? url : url + "/";
	xhr.open("POST", url + FINGERPRINTJS_ENDPOINT, true);

	// set csrf header
	xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));

	// send XHR to API endpoint
	xhr.send(JSON.stringify(components));
}

(function run_fingerprintjs() {
	FingerprintJS.load().then(fp => {
		fp.get().then(results => {
			// Handle the result of FingerprintJS
			reportFingerprintJs(results);
		})
	});
})();
