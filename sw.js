importScripts('/cache-polyfill.js');


self.addEventListener('install', function(e) {
	e.waitUntil(
		caches.open('airhorner').then(function(cache) {
			return cache.addAll([
				'templates/index.html',
				'static/css/default/FONTS.css',
				'static/css/default/INDEX.css',
				'static/js/jquery-3.5.1.min.js',
				'static/js/jquery-ui.min.js',
				'static/js/simplebar.js',
				'static/css/simplebar.css',
				'static/css/ionicons.min.css',
				'static/js/particles.js',
				'static/js/index_animations.js'
			]);
		})
	);
});
