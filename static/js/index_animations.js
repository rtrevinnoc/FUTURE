// Copyright (c) 2020 Roberto Treviño Cervantes

// This file is part of FUTURE (Powered by Monad).

// FUTURE is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// FUTURE is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with FUTURE.  If not, see <https://www.gnu.org/licenses/>.

$(function() {
	// DECLARE RELEVANT VARIABLES
	//var chat = $("#chat")
	//var scroll_element = new SimpleBar(chat[0]);
	var searchbar = $('#searchbar')
	var sidebar_menu = $("#sidebar_menu")
	var summary = $("#summary_content")
	var links = $("#links_content")
	var images = $("#images_content")
	var videos = $("#videos_content")
	var maps = $("#maps_content")
	var summary_button = $('#summary')
	var links_button = $('#links')
	var images_button = $('#images')
	var videos_button = $('#videos')
	var maps_button = $('#maps')
	
	// LOAD PARTICLES ANIMATION
	particlesJS.load('particles-js', 'particles_white.json');

	// DEFINE WHICH SECTION TO SHOW FIRST

	// HIDE ALL SECTIONS WITH NO INFORMATION
	//chat.hide();
	sidebar_menu.hide();
	summary.hide();
	links.hide();
	images.hide();
	videos.hide();
	maps.hide();

	// REMOVE ACCESS TO HIDDEN SECTIONS
	summary_button.hide();
	links_button.hide();
	images_button.hide();
	videos_button.hide();
	maps_button.hide();

	var urlParams = new URLSearchParams(window.location.search);
	const initial_query = urlParams.get('q');
	const initial_section = urlParams.get('section');
	if (!!initial_query) {
		searchbar.val(initial_query)

		$("#links_list").empty()
		$("#links_description").empty()
		$("#welcome").fadeOut("fast");
		$("images_list").empty()
		videos.empty()
		maps.empty()
		summary.empty()

		if (initial_section == 'links' || initial_section == '') {
			get_urls(initial_query)
		} else if (initial_section == "summary") {
			get_urls(initial_query)
		} else if (initial_section == "images") {
			get_images(initial_query)
		} else if (initial_section == "videos") {
			get_videos(initial_query)
		} else if (initial_section == "maps") {
			get_map(initial_query)
		}
	}
	$(window).bind("popstate", function(e) {
		urlParams = new URLSearchParams(window.location.search);
		var new_query = urlParams.get('q');
		if (!!new_query) {

			const url = new URL(window.location)
			url.searchParams.set('q', input)
			url.searchParams.set('section', 'links')
			window.history.pushState({}, '', url)

			$("#links_list").empty()
			$("#links_description").empty()
			$("#welcome").fadeOut("fast");
			$("images_list").empty()
			videos.empty()
			maps.empty()
			summary.empty()

			searchbar.val(new_query)
			get_urls(new_query)
		}
	});

	//const adCode = '<iframe data-aa="1549965" src="//ad.a-ads.com/1549965?size=320x50&background_color=eeeeee&text_color=111111&title_color=daa520&title_hover_color=daa520&link_color=b82f2f&link_hover_color=b82f2f" scrolling="no" style="width:320px; height:50px; border:0px; padding:0; overflow:hidden" allowtransparency="true"></iframe>'
	//function showAds () {
		//var cusid_ele = document.getElementsByClassName('ad')
		//for (var i = 0; i < cusid_ele.length; ++i) {
			//cusid_ele[i].innerHTML = adCode;
		//}
	//}

	//function removeAds () {
		//var cusid_ele = document.getElementsByClassName('ad')
		//for (var i = 0; i < cusid_ele.length; ++i) {
			//cusid_ele[i].remove()
		//}
	//}

	//let hasPaid = false
	//if (document.monetization) {
		//document.monetization.addEventListener('monetizationstart', () => {
			//hasPaid = true
			//removeAds()
		//})
	//}

	//if (!document.monetization) {
		//showAds()
	//} else {
		////setTimeout(() => {
		//if (!hasPaid) {
			//showAds()
		//}
		////}, 3000)
	//}


	if (annyang) {
		var commands = {
			'search for *query': function(query) {

				const url = new URL(window.location)
				url.searchParams.set('q', input)
				url.searchParams.set('section', 'links')
				window.history.pushState({}, '', url)
				
				$("#links_list").empty()
				$("#links_description").empty()
				$("#welcome").fadeOut("fast");
				$("images_list").empty()
				videos.empty()
				maps.empty()
				summary.empty()

				searchbar.val(query);
				get_urls(query);
			}
		};
		annyang.addCommands(commands);
		annyang.start();
	}

	searchbar.autocomplete({
		source: "/_autocomplete",
		minLength: 1
	});

	function changeSection() {
		$('#particles-js').fadeOut("slow");
		urlParams = new URLSearchParams(window.location.search);
		section = urlParams.get('section');
		summary_button.show();
		links_button.show();
		images_button.show();
		videos_button.show();
		maps_button.show();
		if (section == "summary") {
			links.fadeOut("fast");
			images.fadeOut("fast");
			maps.fadeOut("fast");
			videos.fadeOut("fast");
			summary.fadeIn("fast");
			$("body").animate({
				backgroundColor: "#505050"
			}, "slow");
			summary.animate({
				color: "#BABABA"
			}, "slow");
			summary_button.animate({
				color: "#9e3434"
			}, "fast");
			links_button.animate({
				color: "#1b1a1a"
			}, "fast");
			maps_button.animate({
				color: "#1b1a1a"
			}, "fast");
			images_button.animate({
				color: "#1b1a1a"
			}, "fast");
			videos_button.animate({
				color: "#1b1a1a"
			}, "fast");
		} else if (section == "links" || section == "") {
			summary.fadeOut("fast");
			images.fadeOut("fast");
			maps.fadeOut("fast");
			videos.fadeOut("fast");
			links.fadeIn("fast");
			$("body").animate({
				backgroundColor: "#EEEEEE"
			}, "slow");
			links.animate({
				color: "#1C1C1C"
			}, "slow");
			links_button.animate({
				color: "#9e3434"
			}, "fast");
			summary_button.animate({
				color: "#1b1a1a"
			}, "fast");
			maps_button.animate({
				color: "#1b1a1a"
			}, "fast");
			images_button.animate({
				color: "#1b1a1a"
			}, "fast");
			videos_button.animate({
				color: "#1b1a1a"
			}, "fast");
		} else if (section == "maps") {
			summary.fadeOut("fast");
			links.fadeOut("fast");
			images.fadeOut("fast");
			videos.fadeOut("fast");
			maps.show();
			$("body").animate({
				backgroundColor: "#EEEEEE"
			}, "slow");
			maps.animate({
				color: "#1C1C1C"
			}, "slow");
			maps_button.animate({
				color: "#9e3434"
			}, "fast");
			links_button.animate({
				color: "#1b1a1a"
			}, "fast");
			summary_button.animate({
				color: "#1b1a1a"
			}, "fast");
			videos_button.animate({
				color: "#1b1a1a"
			}, "fast");
			images_button.animate({
				color: "#1b1a1a"
			}, "fast");
		} else if (section == "images") {
			summary.fadeOut("fast");
			links.fadeOut("fast");
			maps.fadeOut("fast");
			videos.fadeOut("fast");
			images.fadeIn("fast");
			$("body").animate({
				backgroundColor: "#EEEEEE"
			}, "slow");
			images.animate({
				color: "#1C1C1C"
			}, "slow");
			images_button.animate({
				color: "#9e3434"
			}, "fast");
			links_button.animate({
				color: "#1b1a1a"
			}, "fast");
			summary_button.animate({
				color: "#1b1a1a"
			}, "fast");
			maps_button.animate({
				color: "#1b1a1a"
			}, "fast");
			videos_button.animate({
				color: "#1b1a1a"
			}, "fast");
		} else if (section == "videos") {
			summary.fadeOut("fast");
			images.fadeOut("fast");
			maps.fadeOut("fast");
			links.fadeOut("fast");
			videos.fadeIn("fast");
			$("body").animate({
				backgroundColor: "#EEEEEE"
			}, "slow");
			videos.animate({
				color: "#1C1C1C"
			}, "slow");
			videos_button.animate({
				color: "#9e3434"
			}, "fast");
			links_button.animate({
				color: "#1b1a1a"
			}, "fast");
			summary_button.animate({
				color: "#1b1a1a"
			}, "fast");
			maps_button.animate({
				color: "#1b1a1a"
			}, "fast");
			images_button.animate({
				color: "#1b1a1a"
			}, "fast");
		} else {
			$("body").animate({
				backgroundColor: "#EEEEEE"
			}, "slow");
		}
	}

	$('#sidebar_content').hide();
	//scroll_element.getScrollElement().scrollTop = scroll_element.getScrollElement().scrollHeight;
	function get_urls(input) {
		var date = new Date();
		var start_time = date.getTime();
		$(".hex").addClass("rotate");
		counter = 0
		current_links_page = 1

		$.getJSON($SCRIPT_ROOT + '/_fetchSearxResults', {
			query: input
		}, function(data) {
			searx_response = data.result

			searx_response["urls"].reverse().forEach(function(url) {
				$("#links_list").prepend('<div class="url_item"><p class="link_paragraph"><span class="domain"><a href="' + url["url"] + '">' + url["header"] + '</a></span></p><p class="link_paragraph2"><span class="link"><a href="' + url["url"] + '">' + url["url"] + '</a></span></p><p class="body searchable">' + url["body"] + '<p></div>')
			});

			counter += 1
			if (counter == 2) {
				$(".hex").removeClass("rotate")
				var new_date = new Date();
				var end_time = new_date.getTime();
				$("#links_description").prepend('<p id="gathered">Gathered ' + $("#links_list .url_item").length + ' resources in ' + ((end_time - start_time)/1000) + 's</p>')
			}
		})

		$.getJSON($SCRIPT_ROOT + '/_answer', {
			query: input
		}, function(data) {
			response = data.result

			if (searchbar.val() != response["corrected"]) {
				searchbar.val(response["corrected"])
				searchbar.animate({
					backgroundColor: "#9e3434"
				}, "fast");
				searchbar.animate({
					backgroundColor: "#2b2b2b"
				}, "fast");
			}

			$("#links_description").prepend('<div id="small_summary">' + response["small_summary"] + '</div>')
			response["urls"].forEach(function(url) {
				$("#links_list").append('<div class="url_item"><p class="link_paragraph"><span class="domain"><a href="' + url["url"] + '">' + url["header"] + '</a></span></p><p class="link_paragraph2"><span class="link"><a href="' + url["url"] + '">' + url["url"] + '</a></span></p><p class="body searchable">' + url["body"] + '<p></div>')
			});

			summary.text(response["answer"]);
			
			counter += 1
			if (counter == 2) {
				$(".hex").removeClass("rotate")
				var new_date = new Date();
				var end_time = new_date.getTime();
				$("#links_description").prepend('<p id="gathered">Gathered ' + $("#links_list .url_item").length + ' resources in ' + ((end_time - start_time)/1000) + 's</p>')
			}
		});

		current_query = input;
		changeSection();

		return false;
	};

	function get_images(input) {
		$(".hex").addClass("rotate");
		counter = 0
		current_images_page = 1

		$.getJSON($SCRIPT_ROOT + '/_fetchSearxImages', {
			query: input
		}, function(data) {
			searx_response = data.result

			searx_response["images"].reverse().forEach(function(image) {
				$("#images_list").prepend('<div class="grid-item"><a href=' + image["parentUrl"] + '><img class="image-item" src="/_retrieveImage?url=' + image["url"] + '" alt="Not available"></a></div>')
			});

			counter += 1
			if (counter == 2) {
				$(".hex").removeClass("rotate")
			}
		})

		$.getJSON($SCRIPT_ROOT + '/_answerImages', {
			query: input
		}, function(data) {
			response = data.result

			response["images"].forEach(function(image) {
				$("#images_list").append('<div class="grid-item"><a href=' + image["parentUrl"] + '><img class="image-item" src="/_retrieveImage?url=' + image["url"] + '" alt="Not available"></a></div>')
			});

			counter += 1
			if (counter == 2) {
				$(".hex").removeClass("rotate")
			}
		});

		current_query = input;
		changeSection();
		return false;
	};

	function get_videos(input) {
		$(".hex").addClass("rotate");

		$.getJSON($SCRIPT_ROOT + '/_fetchSearxVideos', {
			query: input
		}, function(data) {
			searx_response = data.result

			searx_response["videos"].forEach(function(video) {
				videos.append('<div class="video_item"><div class="video_thumbnail"><a href="' + video["url"] + '"><img src="/_retrieveImage?url=' + video["thumbnail"] + '" alt=""></a></div><div class="video_description"><p class="link_paragraph"><span class="domain"><a href="' + video["url"] + '">' + video["title"] + '</a></span></p><p class="link_paragraph2"><span class="link"><a href="' + video["url"] + '">' + video["url"] + '</a></span></p><p class="body searchable">' + video['length'] + ' | Uploaded by ' + video["author"] + ' on ' + video['date'] + '.<p></div></div>')
			});

			$(".hex").removeClass("rotate")
		})

		current_query = input;
		changeSection();
		return false;
	};

	function get_map(input) {
		$(".hex").addClass("rotate");

		$.getJSON($SCRIPT_ROOT + '/_answerMap', {
			query: input
		}, function(data) {
			response = data.result
			maps.append(response["map"])

			$(".hex").removeClass("rotate")
		})

		current_query = input;
		changeSection();
		return false;
	};

	searchbar.focus()

	//$('#eye').click(function(e) {
		//if (chat.is(':hidden')) {
			//chat.slideDown("slow")
			//if ($(window).height() <= 768 && $(window).width() <= 960) {
				//sidebar_menu.hide()
				//$('#sidebar_show_icon').attr("class", "ion-chevron-left")
			//}
		//} else {
			//chat.slideUp("slow")
		//}
	//});

	//$("#close_chat").click(function(e) {
		//chat.slideUp("slow")
	//})

	links_button.click(function(e) {
		const url = new URL(window.location)
		url.searchParams.set('section', 'links')
		window.history.pushState({}, '', url)
		changeSection();

		if ($("#links_list").html() == '') {
			get_urls(current_query)
		}
	})

	summary_button.click(function(e) {
		const url = new URL(window.location)
		url.searchParams.set('section', 'summary')
		window.history.pushState({}, '', url)
		changeSection();
		
		if (summary.text().length == 0) {
			get_urls(current_query)
		}
	})

	images_button.click(function(e) {
		const url = new URL(window.location)
		url.searchParams.set('section', 'images')
		window.history.pushState({}, '', url)
		changeSection();
		
		if (images.html() == '') {
			get_images(current_query)
		}
	})

	videos_button.click(function(e) {
		const url = new URL(window.location)
		url.searchParams.set('section', 'videos')
		window.history.pushState({}, '', url)
		changeSection();
		
		if (videos.html() == '') {
			get_videos(current_query)
		}
	})

	maps_button.click(function(e) {
		const url = new URL(window.location)
		url.searchParams.set('section', 'maps')
		window.history.pushState({}, '', url)
		changeSection();
		
		if (maps.html() == '') {
			get_map(current_query)
		}
	})

	$('#load_more_links').click(function(e) {
		$(".hex").addClass("rotate");
		$.getJSON($SCRIPT_ROOT + '/_updateAnswer', {
			query: current_query,
			page: (current_links_page + 1)
		}, function(data) {
			$(".hex").removeClass("rotate")
			response = data.result
			response["urls"].forEach(function(url) {
				$("#links_list").append('<div class="url_item"><p class="link_paragraph"><span class="domain"><a href="' + url["url"] + '">' + url["header"] + '</a></span></p><p class="link_paragraph2"><span class="link"><a href="' + url["url"] + '">' + url["url"] + '</a></span></p><p class="body searchable">' + url["body"] + '<p></div>');
			});
			current_links_page += 1;
		});
	});

	$('#load_more_images').click(function(e) {
		$(".hex").addClass("rotate");
		$.getJSON($SCRIPT_ROOT + '/_updateImages', {
			query: current_query,
			page: (current_images_page + 1)
		}, function(data) {
			$(".hex").removeClass("rotate")
			response = data.result
			response["images"].forEach(function(image) {
				$("#images_list").append('<div class="grid-item"><a href=' + image["parentUrl"] + '><img class="image-item" src="/_retrieveImage?url=' + image["url"] + '" alt="Not available"></a></div>')
			});
			current_images_page += 1;
		});
	});

	$('#sidebar_show').click(function(e) {
		toggle_sidebar()
	});

	var toggle_sidebar = function(e) {
		sidebar_menu.animate({
			width: 'toggle'
		});
		switch ($('#sidebar_show_icon').attr("class")) {
			case 'ion-chevron-left':
				//if ($(window).height() <= 768 && $(window).width() <= 960) {
					//chat.hide()
				//}
				$('#sidebar_show_icon').attr("class", "ion-chevron-right")
				$('#particles-js').animate({
					width: ($(window).width() - ($(window).width() / 4.1))
				}, function() {
					$("#particles-js").animate({
						opacity: 0.5
					});
					$("body").animate({
						backgroundColor: "#111111"
					}, "slow");
					pJSDom[0].pJS.particles.opacity.value = 0
					pJSDom[0].pJS.particles.line_linked.color = "#FFFFFF"
					pJSDom[0].pJS.particles.move.speed = 10
					pJSDom[0].pJS.fn.particlesRefresh()
				});
				$('#sidebar_content').fadeIn("slow")
				break;
			case "ion-chevron-right":
				$('#sidebar_content').fadeOut("fast", function() {
					$('#sidebar_show_icon').attr("class", "ion-chevron-left")
				})

				$('#particles-js').animate({
					width: $(window).width()
				}, function() {
					$("#particles-js").animate({
						opacity: 1
					});
					pJSDom[0].pJS.particles.opacity.value = 0
					pJSDom[0].pJS.particles.line_linked.color = "#000000"
					pJSDom[0].pJS.particles.move.speed = 3
					pJSDom[0].pJS.fn.particlesRefresh()
				});
				break;
		}
	}

	$('#sendbutton').bind('click', function(e) {
		e.preventDefault()

		const url = new URL(window.location)
		url.searchParams.set('q', searchbar.val())
		url.searchParams.set('section', 'links')
		window.history.pushState({}, '', url)

		$("#links_list").empty()
		$("#links_description").empty()
		$("#welcome").fadeOut("fast");
		$("images_list").empty()
		videos.empty()
		maps.empty()
		summary.empty()

		get_urls(searchbar.val());
	});
	searchbar.bind('keydown', function(e) {
		if (e.keyCode == 13) {
			e.preventDefault()

			const url = new URL(window.location)
			url.searchParams.set('q', searchbar.val())
			url.searchParams.set('section', 'links')
			window.history.pushState({}, '', url)

			$("#links_list").empty()
			$("#links_description").empty()
			$("#welcome").fadeOut("fast");
			$("images_list").empty()
			videos.empty()
			maps.empty()
			summary.empty()

			get_urls(searchbar.val());
		}
	});

	// Copyright (c) 2020 by Justin Windle (https://codepen.io/soulwire/pen/mErPAK)
	class TextScramble {
		constructor(el) {
			this.el = el
			this.chars = '!<>-_\\/[]{}—=+*^?#________'
			this.update = this.update.bind(this)
		}
		setText(newText) {
			const oldText = this.el.text()
			const length = Math.max(oldText.length, newText.length)
			const promise = new Promise((resolve) => this.resolve = resolve)
			this.queue = []
			for (let i = 0; i < length; i++) {
				const from = oldText[i] || ''
				const to = newText[i] || ''
				const start = Math.floor(Math.random() * 40)
				const end = start + Math.floor(Math.random() * 40)
				this.queue.push({
					from,
					to,
					start,
					end
				})
			}
			cancelAnimationFrame(this.frameRequest)
			this.frame = 0
			this.update()
			return promise
		}
		update() {
			let output = ''
			let complete = 0
			for (let i = 0, n = this.queue.length; i < n; i++) {
				let {
					from,
					to,
					start,
					end,
					char
				} = this.queue[i]
				if (this.frame >= end) {
					complete++
					output += to
				} else if (this.frame >= start) {
					if (!char || Math.random() < 0.28) {
						char = this.randomChar()
						this.queue[i].char = char
					}
					output += `<span class="dud">${char}</span>`
				} else {
					output += from
				}
			}
			this.el.html("SEARCH FOR <br>" + output)
			if (complete === this.queue.length) {
				this.resolve()
			} else {
				this.frameRequest = requestAnimationFrame(this.update)
				this.frame++
			}
		}
		randomChar() {
			return this.chars[Math.floor(Math.random() * this.chars.length)]
		}
	}

	const phrases = [
		'ARTS',
		'BLACK <br> HOLES',
		'FINANCE',
		'MATHEMATICS',
		'LITERATURE',
		'COMPUTING',
		'LEARNING',
		'UTOPIA',
		'HUMAN',
		'BRAIN',
		'BIOLOGY',
		'NUMBERS',
		'NATURE',
		'MONEY',
		'SKYSCRAPPERS',
		'MUSIC',
		'NETWORKS',
		'FASHION',
		'PROGRAMMING',
		'GAMING',
		'NEWS',
		'VACCINES',
		'PHILOSOPHY',
		'ETHICS',
		'SPACESHIPS',
		'ROCKETS',
		'SPACE',
		'ROBOTICS',
		'ARTIFICIAL <br> INTELLIGENCE',
		'PHYSICS',
		'SPACETIME',
		'RADIOACTIVE <br> DECAY',
		'GASTRONOMY',
		'ENTROPY',
		'TENSORS',
		'SCALARS',
		'MATRICES',
		'CRYPTOGRAPHY',
		'QUANTUM <br> COMPUTING',
		'SCIENCE'
	]

	const el = $('#godfvt')
	const fx = new TextScramble(el)

	function generateRandomInteger(min, max) {
		return Math.floor(min + Math.random() * (max + 1 - min))
	}

	const next = () => {
		fx.setText(phrases[generateRandomInteger(1, phrases.length - 1)]).then(() => {
			setTimeout(next, 3000)
		})
	}

	next()
});
