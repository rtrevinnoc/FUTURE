const OFFLINE_VERSION = 1;
const CACHE_NAME = 'FUTURE';
var CACHED_FILES = [
	'/offline.html',
	'/apple-touch-icon.png',
	'/favicon-32x32.png',
	'/favicon-16x16.png',
	'/site.webmanifest',
	'/safari-pinned-tab.svg',
	'/css/default/FONTS.css',
	'/css/default/OFFLINE.css',
	'/fonts/sourceSansPro/Light/SourceSansPro-Light.otf',
	'/fonts/sourceSansPro/Light/SourceSansPro-Light.otf.woff',
	'/fonts/sourceSansPro/Light/SourceSansPro-Light.ttf',
	'/fonts/sourceSansPro/Light/SourceSansPro-Light.ttf.woff2',
]

this.addEventListener('install', event => {
	event.waitUntil(
		caches.open(currentCache.offline).then(function(cache) {
			return cache.addAll(CACHED_FILES);
		})
	);
});

this.addEventListener('fetch', event => {
	// request.mode = navigate isn't supported in all browsers
	// so include a check for Accept: text/html header.
	if (event.request.mode === 'navigate' || (event.request.method === 'GET' && event.request.headers.get('accept').includes('text/html'))) {
		event.respondWith(
			fetch(event.request.url).catch(error => {
				// Return the offline page
				return caches.match('/offline.html');
			})
		);
	}
	else {
		// Respond with everything else if we can
		event.respondWith(caches.match(event.request)
			.then(function (response) {
				return response || fetch(event.request);
			})
		);
	}
});
