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
	var urlParams = new URLSearchParams(window.location.search);
	const initial_query = urlParams.get('q');
	if (!!initial_query) {
		searchbar.val(initial_query)
		submit_form(initial_query)
	}
	$(window).bind("popstate", function(e) {
		urlParams = new URLSearchParams(window.location.search);
		var new_query = urlParams.get('q');
		if (!!new_query) {
			searchbar.val(new_query)
			submit_form(new_query)
		}
	});

	const adCode = '<iframe data-aa="1549965" src="//acceptable.a-ads.com/1549965?size=Adaptive&background_color=eeeeee&text_color=111111&title_color=daa520&title_hover_color=daa520&link_color=b82f2f&link_hover_color=b82f2f" scrolling="no" style="border:0px; padding:0; width:100%; height:100%; overflow:hidden" allowtransparency="true"></iframe>'
	function showAds () {
		var cusid_ele = document.getElementsByClassName('ad')
		for (var i = 0; i < cusid_ele.length; ++i) {
			cusid_ele[i].innerHTML = adCode;
		}
	}

	function removeAds () {
		var cusid_ele = document.getElementsByClassName('ad')
		for (var i = 0; i < cusid_ele.length; ++i) {
			cusid_ele[i].remove()
		}
	}

	let hasPaid = false
	if (document.monetization) {
		document.monetization.addEventListener('monetizationstart', () => {
			hasPaid = true
			removeAds()
		})
	}

	if (!document.monetization) {
		showAds()
	} else {
		//setTimeout(() => {
		if (!hasPaid) {
			showAds()
		}
		//}, 3000)
	}

	// LOAD PARTICLES ANIMATION
	particlesJS.load('particles-js', 'particles_white.json');

	// DEFINE WHICH SECTION TO SHOW FIRST
	var section = "initial"

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

	if (annyang) {
		var commands = {
			'search for *query': function(query) {
				searchbar.val(query);
				submit_form(query);
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
		if (section == "summary") {
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
		} else if (section == "links") {
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
	function submit_form(input) {
		var date = new Date();
		var start_time = date.getTime();
		$("#welcome").fadeOut("fast");
		$(".hex").addClass("rotate");
		$("#links_list").empty()
		$("#links_description").empty()
		images.empty()
		videos.empty()
		maps.empty()
		summary.empty()
		counter = 0

		//$('#sidebar_show').addClass("blink_sidebar");

		$('#particles-js').fadeOut("slow");

		links_button.animate({
			color: "#9e3434"
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
		images_button.animate({
			color: "#1b1a1a"
		}, "fast");

		//scroll_element.getScrollElement().scrollTop = scroll_element.getScrollElement().scrollHeight;
		$.getJSON($SCRIPT_ROOT + '/_fetchSearxResults', {
			query: input
		}, function(data) {
			searx_response = data.result

			var current_page = 1
			summary_button.show();
			links_button.show();
			images_button.show();
			videos_button.show();
			maps_button.show();
			summary.fadeOut("fast");
			images.fadeOut("fast");
			videos.fadeOut("fast");
			maps.fadeOut("fast");
			links.fadeIn("fast");
			section = "links"
			changeSection();

			searx_response["urls"].reverse().forEach(function(url) {
				$("#links_list").prepend('<div class="url_item"><p class="link_paragraph"><span class="domain"><a href="' + url["url"] + '">' + url["header"] + '</a></span></p><p class="link_paragraph2"><span class="link"><a href="' + url["url"] + '">' + url["url"] + '</a></span></p><p class="body searchable">' + url["body"] + '<p></div>')
			});

			searx_response["images"].reverse().forEach(function(image) {
				images.prepend('<div class="grid-item"><a href=' + image["parentUrl"] + '><img class="image-item" src="' + image["url"] + '" alt="Not available"></a></div>')
			});

			searx_response["videos"].forEach(function(video) {
				videos.append('<div class="video_item"><div class="video_thumbnail"><a href="' + video["url"] + '"><img src="' + video["thumbnail"] + '" alt=""></a></div><div class="video_description"><p class="link_paragraph"><span class="domain"><a href="' + video["url"] + '">' + video["title"] + '</a></span></p><p class="link_paragraph2"><span class="link"><a href="' + video["url"] + '">' + video["url"] + '</a></span></p><p class="body searchable">' + video['length'] + ' | Uploaded by ' + video["author"] + ' on ' + video['date'] + '.<p></div></div>')
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

			var current_page = 1
			summary_button.show();
			links_button.show();
			images_button.show();
			videos_button.show();
			maps_button.show();
			summary.fadeOut("fast");
			images.fadeOut("fast");
			videos.fadeOut("fast");
			maps.fadeOut("fast");
			links.fadeIn("fast");
			section = "links"
			changeSection();
			if (response["map"] === "") {
				maps_button.hide();
			} else {
				maps_button.show();
			}
			
			if (searchbar.val() != response["corrected"]) {
				searchbar.val(response["corrected"])
				searchbar.animate({
					backgroundColor: "#9e3434"
				}, "fast");
				searchbar.animate({
					backgroundColor: "#2b2b2b"
				}, "fast");
			}
			//$('#chat .simplebar-content').append('<div class="blockline"><div class="container2"><span class="you">' + response["corrected"] + '</span></div></div>');

			response["images"].forEach(function(image) {
				images.append('<div class="grid-item"><a href=' + image["parentUrl"] + '><img class="image-item" src="' + image["url"] + '" alt="Not available"></a></div>')
			});

			$("#links_description").prepend('<div id="small_summary">' + response["small_summary"] + '</div>')
			response["urls"].forEach(function(url) {
				$("#links_list").append('<div class="url_item"><p class="link_paragraph"><span class="domain"><a href="' + url["url"] + '">' + url["header"] + '</a></span></p><p class="link_paragraph2"><span class="link"><a href="' + url["url"] + '">' + url["url"] + '</a></span></p><p class="body searchable">' + url["body"] + '<p></div>')
			});

			summary.text(response["answer"]);
			//$('#chat .simplebar-content').append('<div class="blockline"><div class="container"><span class="machine">' + response["reply"] + '</span></div></div>');

			//if (response["n_res"] === 0 || response["chatbot"] === 0) {
			//	chat.slideDown("slow")
			//}
			
			counter += 1
			if (counter == 2) {
				$(".hex").removeClass("rotate")
				var new_date = new Date();
				var end_time = new_date.getTime();
				$("#links_description").prepend('<p id="gathered">Gathered ' + $("#links_list .url_item").length + ' resources in ' + ((end_time - start_time)/1000) + 's</p>')
			}
		});

		const url = new URL(window.location)
		url.searchParams.set('q', input)
		window.history.pushState({}, '', url)

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
		section = "links"
		changeSection()
		summary.fadeOut("fast");
		images.fadeOut("fast");
		maps.fadeOut("fast");
		videos.fadeOut("fast");
		links.fadeIn("fast");
	})

	summary_button.click(function(e) {
		section = "summary"
		changeSection()
		links.fadeOut("fast");
		images.fadeOut("fast");
		maps.fadeOut("fast");
		videos.fadeOut("fast");
		summary.fadeIn("fast");
		if (summary.text().length == 0) {
			summary.text(response["answer"]);
		}
	})

	images_button.click(function(e) {
		section = "images"
		changeSection()
		summary.fadeOut("fast");
		links.fadeOut("fast");
		maps.fadeOut("fast");
		videos.fadeOut("fast");
		images.fadeIn("fast");
		//if (images.html().length == 0) {
			//response["images"].forEach(function(url) {
				//images.append('<div class="grid-item"><img class="image-item" src="' + url + '" alt="Not available"></div>')
			//});
		//}
	})

	videos_button.click(function(e) {
		section = "videos"
		changeSection()
		summary.fadeOut("fast");
		images.fadeOut("fast");
		maps.fadeOut("fast");
		links.fadeOut("fast");
		videos.fadeIn("fast");
	})

	maps_button.click(function(e) {
		section = "maps"
		changeSection()
		summary.fadeOut("fast");
		links.fadeOut("fast");
		images.fadeOut("fast");
		videos.fadeOut("fast");
		maps.show();
		maps.append(response["map"])
	})

	$('#load_more_items').click(function(e) {
		$(".hex").addClass("rotate");
		$.getJSON($SCRIPT_ROOT + '/_updateAnswer', {
			query: searchbar.val(),
			page: (current_page + 1)
		}, function(data) {
			$(".hex").removeClass("rotate")
			response = data.result
			console.log(searchbar.val(), (current_page + 1))
			console.log(response)
			response["urls"].forEach(function(url) {
				$('<div class="url_item"><p class="link_paragraph"><span class="domain"><a href="' + url["url"] + '">' + url["header"] + '</a></span></p><p class="link_paragraph2"><span class="link"><a href="' + url["url"] + '">' + url["url"] + '</a></span></p><p class="body searchable">' + url["body"] + '<p></div>').insertBefore("#load_more_items");
			});
			response["images"].forEach(function(image) {
				images.append('<div class="grid-item"><a href=' + image["parentUrl"] + '><img class="image-item" src="' + image["url"] + '" alt="Not available"></a></div>')
			});
			current_page = current_page + 1;
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
					changeSection();
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
		submit_form(searchbar.val());
	});
	searchbar.bind('keydown', function(e) {
		if (e.keyCode == 13) {
			e.preventDefault()
			submit_form(searchbar.val());
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
