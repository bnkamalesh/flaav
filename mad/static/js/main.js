var Slideshow = (function() {
	var container, options, slide_count=0, win, slides = [], current_indx = 0;
	var last_index = 0, slide_w = 0, auto_timer, nav_buttons, bt_prev, bt_next;
	var on_next_fns = [], on_prev_fns = [];


	function next(indx) {
		next_indx = current_indx + 1;
		if(typeof indx != "undefined")
			next_indx = indx;

		if(next_indx>last_index && options.cycle) {
			next_indx = 0;
		}


		if(next_indx <= last_index) {
			var c_text = slides[current_indx].find(".text");
			var n_text = slides[next_indx].find(".text");

			if(options.prev_next_buttons){
				bt_prev.removeClass("disabled");
			}

			if(options.delay_text) {
				n_text.css("opacity", 0);
				c_text.stop().velocity({"opacity": 0}, options.animation_time, function() {


				 slides[next_indx].stop().css("left", slide_w).velocity({"left": 0}, options.animation_time, function() {

				 	n_text.stop().velocity({"opacity": 1}, options.animation_time);

				 }).addClass("active");

				slides[current_indx].velocity({"left": -(slide_w+100)}, options.animation_time+50).removeClass("active");

				current_indx = next_indx;
				update_navbuttons();
				});
			}
			else {
				slides[next_indx].stop().css("left", slide_w).velocity({"left": 0}, options.animation_time).addClass("active");

				slides[current_indx].velocity({"left": -(slide_w+100)}, options.animation_time+50).removeClass("active");

				current_indx = next_indx;
				update_navbuttons();
			}

			if(next_indx==last_index) {
				if(options.prev_next_buttons && !options.cycle) {
					bt_next.addClass("disabled");
				}
			}
		}
		
	}

	function prev(indx) {
		next_indx = current_indx - 1;
		if(typeof indx != "undefined")
			next_indx = indx;

		if(next_indx<0 && options.cycle) {
			next_indx = last_index;
		}

		if(next_indx >= 0) {
			var c_text = slides[current_indx].find(".text");
			var n_text = slides[next_indx].find(".text");

			if(options.prev_next_buttons){
				bt_next.removeClass("disabled");
			}

			if(options.delay_text) {
				n_text.css("opacity", 0);
				c_text.stop().velocity({"opacity": 0}, options.animation_time, function() {

					slides[next_indx].stop().css("left", -slide_w).velocity({"left": 0}, options.animation_time, function() {

						n_text.velocity({"opacity": 1}, options.animation_time);

					}).addClass("active");
					slides[current_indx].stop().velocity({"left": (slide_w+10)}, options.animation_time+50).removeClass("active");

					current_indx = next_indx;
					update_navbuttons();
				});
			}
			else {
				slides[next_indx].stop().css("left", -slide_w).velocity({"left": 0}, options.animation_time).addClass("active");

				slides[current_indx].stop().velocity({"left": (slide_w+10)}, options.animation_time+50).removeClass("active");

				current_indx = next_indx;
				update_navbuttons();
			}

			if(next_indx==0) {
				if(options.prev_next_buttons && !options.cycle){
					bt_prev.addClass("disabled");
				}
			}
		}
		
	}

	function update_navbuttons() {
		if(options.navbuttons) {
			nav_buttons.find("a").removeClass("active");
			nav_buttons.find("li:eq("+current_indx+") a").addClass("active");
		}

		if(on_next_fns.length > 0) {
			for(var i=0; i<on_next_fns.length; i++) {
				on_next_fns[i].fname.call(on_next_fns[i].params);
			}
		}

		if(on_prev_fns.length > 0) {
			for(var i=0; i<on_prev_fns.length; i++) {
				on_prev_fns[i].fname.call(on_prev_fns[i].params);
			}
		}
	}

	function start_auto() {
		auto_timer = setInterval(function() {
			next();
		}, options.delay);

	}

	function stop_auto() {
		clearInterval(auto_timer);
	}

	return {
		init: function(cont, opts) {
			if(typeof cont!="undefined") {
				container = cont;
				win = $(window);

				if(typeof opts=="undefined")
					opts = {};

				options = {
					"slide": (typeof opts.slide!=="undefined") ? opts.slide : ".slide",
					"delay": (typeof opts.delay!=="undefined") ? parseInt(opts.delay) : 5000,
					"auto": (opts.auto===false) ? false : true,
					"hoverpause": (opts.hoverpause===false) ? false : true,
					"cycle": (opts.cycle===false) ? false : true,
					"animation_time": (typeof opts.animation_time!=="undefined") ? opts.animation_time : 500,
					"prev_next_buttons": (opts.prev_next_buttons===false) ? false : true,
					"navbuttons": (opts.navbuttons===false) ? false : true,
					"overlay": (opts.overlay===false) ? false : true,
					"use_win_height": (opts.use_win_height===true) ? true : false,
					"delay_text": (opts.delay_text===false) ? false : true
				};

				if(options.navbuttons===true) {
					nav_buttons = $('<ul class="noul navbuttons"></ul>');
				}

				slide_count = container.find(options.slide).length;
				last_index = slide_count - 1;

				slide_w = container.parent().outerWidth(true);
				container.find(options.slide).each(function() {
					slides.push($(this));
					$(this).css("left", slide_w);
					if(options.overlay===true) {
						$(this).append('<div class="overlay"> </div>');
					}

					if(options.navbuttons) {
						nav_buttons.append('<li><a href="#" data-index="'+(slides.length-1)+'" > </a></li>');
					}

				}).first().css("left", 0).addClass("active");

				if(options.prev_next_buttons===true) {
					bt_prev = $('<a href="#" class="prev"> </a>');
					bt_next = $('<a href="#" class="next"> </a>');
					container.append(bt_prev).append(bt_next);
					bt_next.click(function() {
						next(); return false; 
					});
					bt_prev.click(function() { 
						prev(); return false; 
					});

					if(!options.cycle){
						bt_prev.addClass("disabled");
					}
				}

				if(options.navbuttons) {
					nav_buttons.find("a").click(function() {
						indx = parseInt($(this).data("index"));
						if(indx > current_indx) {
							next(indx);
						}
						else if(indx < current_indx) {
							prev(indx);
						}
						return false;
					});
					nav_buttons.find("a").first().addClass("active");
					container.append(nav_buttons);
				}

				if(options.auto===true) {
					start_auto();
				}

				if(options.hoverpause===true && options.auto===true) {
					container.hover(function() {
						stop_auto();
					}, function() {

						start_auto();
					});
				}

				Flaav.add_on_rez_fns(Slideshow.on_resize);
			}
		},

		next: next,
		prev: prev,
		on_next: function(fn, params) {
			on_next_fns.push({"fname": fn, "params": params})
		},

		on_prev: function(fn, params) {
			on_prev_fns.push({"fname": fn, "params": params})
		},

		on_resize: function() {
			cont_h = container.parent().outerHeight(true);
			slide_w = container.parent().outerWidth(true);
			if(options.use_win_height) {
				slide_h = win.outerHeight(true);
			}
			else {
				slide_h =  (cont_h > 100)? cont_h : win.outerHeight(true);
			}

			container.css("min-height", slide_h);
			var txt, title;
			for(var i=0; i<slides.length; i++) {
				slides[i].css("height", slide_h);
				txt = slides[i].find("div.text");
				if(txt.length>0) {
					txt.css("margin-top", (slide_h - txt.outerHeight())/2 );
				}
			}
		}
	};
})();

var PageControls = (function() {
	var body, win, header, footer, pages = [], current_indx = 0, last_index = 0, options, scroller, page_counter;
	var pg_counter_timer;

	function set_current_page_indx() {
		var win_scroll_stop = win.scrollTop() + header.outerHeight(true);

		for(var i=1; i<=last_index; i++) {
			if((pages[i].offset().top-24) > win_scroll_stop) {
				current_indx = i-1;
				break;
			}
		}
	}

	function next(indx) {
		var next_indx = current_indx + 1;
		
		if(typeof indx != "undefined")
			next_indx = indx;

		if(options.cycle) {
			if(next_indx>last_index)
				next_indx = 0;
			else if(next_indx < 0)
				next_indx = last_index;
		}

		if(next_indx <= last_index && next_indx >= 0) {
			// pages[next_indx].velocity("scroll", {"duration": options.animation_time});
			$("html").stop().velocity("scroll", {"duration": options.animation_time, "offset": pages[next_indx].offset().top - header.outerHeight(true) });
			current_indx = next_indx;
			show_pagecntr();
		}
	}

	function show_pagecntr() {
		clearTimeout(pg_counter_timer);
		page_counter.find(".left").text(current_indx+1);
		page_counter.fadeIn(options.animation_time, function() {
			pg_counter_timer = setTimeout(function() {
				page_counter.fadeOut(options.animation_time);
			}, 1500);

		});
	}

	return {
		init: function(pgs, opts) {
			if(typeof pgs=="undefined")
				return;
			if(typeof opts=="undefined")
				opts = {};

			options = {
				"cycle": (opts.cycle === true)? true: false,
				"animation_time": opts.animation_time || 500,
				"fitwindow": (opts.fitwindow === false)? false: true
			};

			body = $("body");
			win = $(window);
			header = $("#header");
			footer = $("#footer");
			body.addClass("page-controlled");
			scroller = $("body, html");
			
			pgs.each(function() {
				$(this).data("page-num", $(this).index());
				pages.push($(this));
			});
			
			last_index = pages.length-1;

			if(last_index>0) {
				body.keydown(function(e) {
						switch(e.keyCode ? e.keyCode : e.which) {
							case 38: //up
							case 33:
								if(current_indx>0) {
									e.preventDefault();
									set_current_page_indx();
									next(current_indx-1);
									return false;
								}
								break;

							case 40: //down
							case 34:
								if(current_indx<last_index) {
									e.preventDefault();
									set_current_page_indx();
									next();
									return false;
								}
								break;
							default:
								break;
						}
						return;
				});
				page_counter = $('<span id="page_counter"><span class="left">1</span> / <span class="right">'+(last_index+1)+'</span></span>');
				body.append(page_counter);
				page_counter.hide();
			}

			Flaav.add_on_rez_fns(PageControls.on_resize);
		},

		next: next,
		on_resize: function() {
			if(options.fitwindow===true) {
				for(var i=0; i<pages.length; i++) {
					pages[i].css("min-height", win.outerHeight(true) - header.outerHeight(true));
				}
			}
		}
	};
})();

var Flaav = ( function() {
	// Class to handle all app specific js
	var body, doc, win, animation_time=500, colorindx=-1, colors = ["#2574A9", "#E74C3C","#00B16A", "#FFECDB", "#F9BF3B", "#674172", "#95A5A6"];
	var on_rez_fns = [], on_window_load_fns = [], bound_resize = false, header, header_h, wrap, footer;
	
// red: #E74C3C
// pink:#FFECDB
// purple:#674172
// blue:#34495E
// green:#00B16A
// yellow/orange:#F9BF3B
// gray:#95A5A6

	function page_home_onresize() {
		$(".page-home .about .right").height($(".page-home .about .left").outerHeight(false));

		// set height of tallest toolbox to all
		var tbox_h = 0, t_cont = $(".page-home ul.tools");
		t_cont.children("li").css("height", "auto"); // resetting height before calculating
		t_cont.children("li").each(function() {
			var item = $(this), h = parseInt(item.height());
			if(tbox_h < h)
				tbox_h = h;
		});
		t_cont.children("li").height(tbox_h);

		var ptop = (win.outerHeight(true) - t_cont.outerHeight(true) )/2;
		if(ptop > 0) {
			t_cont.closest("section.page").css("padding-top", ptop).css("padding-bottom", ptop);
		}

	}// page_home_onresize

	function page_home() {
		PageControls.init($("#main section.page"));
		Slideshow.init($("#slideshow"), {"delay": 9000});
		PageControls.next(0);
		$(".find-more.tools").click(function() {
			// $("body,html").velocity({"scrollTop": $("body.page-controlled section.page.tools").offset().top - header.outerHeight(true)}, animation_time);

			// $("body.page-controlled section.page.tools").velocity("scroll", {"duration": animation_time});
			PageControls.next(1);
			return false;
		});
		Flaav.add_on_rez_fns(page_home_onresize);
	}// page_home()

	function page_services_onresize() {
		var item;
		$("#main section.page").each(function() {
			item = $(this), txt = item.find(".text");
			txt.css("padding-top", (item.outerHeight() - txt.outerHeight())/4);
			
			$(this).find(".thumb").each(function() {
				$(this).css("height", item.outerHeight(false));
			});
		});
	}
	
	function page_services() {
		PageControls.init($("#main section.page"));

		$("#topnav .services li a").click(function() {
			var id = $.trim($(this).attr("href").split("#")[1]), el = $("#"+id);
			if(el.length > 0) {
				PageControls.next(el.data("page-num"));
			}
			return false;
		});

		Flaav.add_on_rez_fns(page_services_onresize);
	}

	function page_about() {
		PageControls.init($("#main section.page"));
	}

	function page_contact() {
		var hf = $("#verify_human");
		$("#verify_human_chk").change(function() {
			if($(this).is(":checked")) {
				hf.val($(this).val());
			}
			else{
				hf.val("");
			}
		});
	}

	function page_user_login() {
		var login_form = $("section.login"), reg_form = $("section.register");
		$("#show_register").click(function() {
			login_form.slideUp(animation_time, function() {
				reg_form.slideDown(animation_time);
			});
			return false;
		});

		$("#show_login").click(function() {
			reg_form.slideUp(animation_time, function() {
				login_form.slideDown(animation_time);
			});
			return false;
		});
	}// page_user_login()

	function page_search_filters() {

		$.getJSON( "/dashboard/media?get=industries", function( data ) {
			Flaav.enable_autocomplete($("#viewership_industry"), data);
		});

		$.getJSON( "/dashboard/media?get=geographies", function( data ) {
			Flaav.enable_autocomplete($("#select_markets"), data);
		});

		// Categories Demographoes
		$("#demography li").each(function() {
			var item = $(this), inp = item.find("input");
			if(inp.val().indexOf("Group#")>=0) {
				inp.remove();
				item.html($("<h4></h4>").append(item.find("label").text().replace("Group#", "")));
				item.addClass("title");
			}
		});
		// ===

		// slider
		var convslider = $("#conversion_rate_slider"), options = $('<ul class="slider-labels noul"><li class="label"></li></ul>'), data =[];
		var c_rate = $("#conversion_rate");
		c_rate.hide();
		convslider.slider({
			stop: function( e, ui ) {
				// select_options.prop('selectedIndex', ui.value);
				c_rate.val(ui.value);
			},

			max: 7,
			min: 0.5,
			step: 0.1,
			value: parseFloat(c_rate.val())
		});
		// ==

		// Geography filter
		var hidden_container = $("#geography").siblings(".hidden");
		$("#geography-1").change(function() {
			if($(this).is(":checked")) {
				hidden_container.fadeIn(200);
			}
			else {
				hidden_container.fadeOut(200);
			}
		});
		// ===

		if ($("#sidebar").length == 0) {
			$("body").addClass("front");
		}

	}// page_search_filters()

	function page_search_results() {
		var container = $("#media_items"), count= 1;
		
		tttext.attach($("#save_search .button"), {"message": "You can save up to <strong>8</strong> <i>recent</i> searches."})
		// saving search
		var ssform =$("#save_search"), msg_cont = ssform.find(".message");
		ssform.submit(function() {
			msg_cont.removeClass("success failed error");
			msg_cont.hide();
			$.ajax({
				type: "POST",
				url: "",
				data: ssform.serialize(),
				dataType: "json",
				success: function(data) {
					msg_cont.addClass(data.status);
					msg_cont.stop().fadeOut(animation_time, function() { 
						msg_cont.html(data.message).fadeIn(animation_time);
					});
				}
				});
			return false;
		});
		// ===

		// reducing description length
		var text;
		container.find(".description").each(function() {
			text = $(this).text();
			$(this).data("description", text);
			tttext.attach($(this), {"message": $(this).data("description")});

			// strip down description
			if(text.length > 90) {
				$(this).text( text.substring(0, 86) + "...") ;
			}
			//==
		});
		// ====
		container.find("li.media-item:eq(0)").prepend('<span class="medal" data-message="This is your best choice">1</span>').addClass("ranked");
		container.find("li.media-item:eq(1)").prepend('<span class="medal" data-message="This is your 2nd best choice">2</span>').addClass("ranked");
		container.find("li.media-item:eq(2)").prepend('<span class="medal" data-message="This is your 3rd best choice">3</span>').addClass("ranked");

		container.find(".medal").each(function() {
			tttext.attach($(this).closest(".media-item"), {"message": $(this).data("message")});
		});

	}// page_search_results()

	return {
		init: function() {
			body = $("body"); 
			doc = $(document); 
			win = $(window);
			header = $("#header");
			footer = $("#footer");
			header_h = header.outerHeight(false);
			wrap = $("#wrap");
			main = $("#main");

			this.on_resize();

			$(".currency").addClass("usd").html("$");

			// Setting default configurations for moment.js
			moment.lang("en", {
				calendar : {
					lastDay : "[Yesterday at] LT",
					sameDay : "LT",
					nextDay : "[Tomorrow at] LT",
					lastWeek : "[last] dddd [at] LT",
					nextWeek : "dddd [at] LT",
					sameElse : "L"
				},

				"longDateFormat": {
					LT: "h:mm A",
					L: "DD/MM/YYYY",
					l: "D/M/YYYY",
					LL: "Do MMMM YYYY",
					ll: "D MMM YYYY",
					LLL: "Do MMMM YYYY LT",
					lll: "D MMM YYYY LT",
					LLLL: "dddd, Do MMMM YYYY LT",
					llll: "ddd, D MMM YYYY LT"
				}
			});
			// ===

			tttext.init({"position": "top", "offset": 8, "duration": 150});

			//Change timestamps to local time
			var utc_time;
			$(".time").each(function() {
				utc_time = $(this).text();
				$(this).text(moment.utc(utc_time).local().calendar());
			});
			// ===

			// Adjust header on scroll
			function win_scroll_stop() {
				if( win.scrollTop() >= header_h) {
					header.addClass("minimized");
				}
				else if(header.hasClass("minimized")) {
					header.removeClass("minimized");
				}
			}
			var scroll_timer;
			win.scroll(function() {
				clearTimeout(scroll_timer);
				scroll_timer = setTimeout(function() {
					win_scroll_stop();
				}, 50);

			});
			// ===

			// Call page specific functions
			if(typeof MODULE === "string") {
				modules = MODULE.split(" ");
				for(var i=0; i<modules.length; i++) {
					switch($.trim(modules[i])) {
						case "page-home":
							page_home();
							break;
						case "page-services":
							page_services();
							break;
						case "page-about":
							page_about();
							break;
						case "page-contact":
							page_contact();
							break;
						case "page-user-login":
							page_user_login();
							break;
						case "search-filters":
							page_search_filters();
							break;
						case "search-results":
							page_search_results();
							break;
						default:
							break;
					}
				}
			}
			//===

			// Mini menu
			var mm = $("#mini_menu");
			mm.click(function() {
				if(mm.hasClass("active")) {
					mm.removeClass("active");
					$("#topnav .horizontal-menu").slideUp(animation_time);
				}
				else{
					mm.addClass("active");
					$("#topnav .horizontal-menu").slideDown(animation_time);
				}
				return false;
			});
			// ===

			// Sub menu
			$("#topnav .sub-menu").hover(function() { $(this).addClass("active"); }, function() { $(this).removeClass("active"); });

			$("#topnav li").hover(function() {
				$(this).find(".sub-menu").slideDown(200);
			}, function() {

				var sub = $(this).find(".sub-menu");
				setTimeout(function() {
					if(!sub.hasClass("active")) {
						sub.slideUp(200);
					}
				}, 200);


			});
			// ===

			Flaav.on_window_load();
		}, // init()

		enable_autocomplete: function(container, ac_source) {
			container.autocomplete({
		        minLength: 1,
		        source: function (request, response) {
		            var term = request.term;

		            // substring of new string (only when a comma is in string)
		            if (term.indexOf(', ') > 0) {
		                var index = term.lastIndexOf(', ');
		                term = term.substring(index + 2);
		            }

		            // regex to match string entered with start of suggestion strings
		            var re = $.ui.autocomplete.escapeRegex(term);
		            var matcher = new RegExp('^' + re, 'i');
		            var regex_validated_array = $.grep(ac_source, function (item, index) {
		                return matcher.test(item);
		            });

		            // pass array `regex_validated_array ` to the response and 
		            // `extractLast()` which takes care of the comma separation
		            response($.ui.autocomplete.filter(regex_validated_array, extractLast(term)));
		        },

		        focus: function () {
		        	return false;
		        },

		        select: function (event, ui) {
		            var terms = split(this.value);
		            terms.pop();
		            terms.push(ui.item.value);
		            terms.push('');
		            this.value = terms.join(', ');
		            return false;
		        }
		    });

		    function split(val) { return val.split(/,\s*/); }
		    function extractLast(term) { return split(term).pop(); }
		}, // enable_autocomplete

		get_color: function(indx) {
			colorindx = (colorindx+1) % colors.length;
			if(typeof indx==="undefined")
				indx = colorindx;
			return colors[indx];
		}, // get_color

		on_resize: function() {
			if(bound_resize===false) {
				win.resize(function() {
					if(on_rez_fns.length > 0) {
						for(var i=0; i<on_rez_fns.length; i++) {
							on_rez_fns[i].fname.call(on_rez_fns[i].params);
						}
					}
					header_h = header.outerHeight(true);

					main.css("min-height", win.outerHeight(true) - (header_h+footer.outerHeight(true)) );
					// nav menu
					if(win.outerWidth() >= 900) {
						$("#mini_menu").removeClass("active");
						$("#topnav .horizontal-menu").show();
					}
					// ===
				}).resize();
				bound_resize = true;
			}
			else {
				win.resize();
			}
		},

		add_on_rez_fns: function(fn, params) {
			on_rez_fns.push({"fname": fn, "params": params})
			Flaav.on_resize();
		},

		add_on_windowload_fns: function(fn, params) {
			on_window_load_fns.push({"fname": fn, "params": params});
		},

		on_window_load: function() {
			$(window).load(function() {
				if(on_window_load_fns.length > 0) {
					for(var i=0; i<on_window_load_fns.length; i++ ) {
						on_window_load_fns[i].fname.call(on_window_load_fns[i].params);
					}
				}

				//lazy load images
				var img, lazy_imgs = $(".lazy-load"), img_set = {}, win_height = win.outerHeight(true) - 100, 

						keys =[], cur_scr=0, i, indx, offset_top, loaded = [];

				lazy_imgs.each(function() {
					img = $(this);
					offset_top = parseInt(img.offset().top);
					if(img_set.hasOwnProperty(offset_top)) {
						img_set[offset_top].push(img);
					}
					else {
						img_set[offset_top] = [img];
					}
					keys.push(offset_top);
				});

				keys.sort(function(a, b) { return a-b; });

				doc.scroll(function() {
					cur_scr = doc.scrollTop() + win_height;
					for(i in keys) {
						indx = keys[i];
						if(indx < cur_scr && indx > doc.scrollTop() && ($.inArray(indx, loaded)===-1)) {
							loaded.push(indx);
							for(j in img_set[indx])
								img_set[indx][j].attr("src", img_set[indx][j].data("src"));
						}

						if(indx > cur_scr)
							break;
					}
				}).scroll();
				// ===
			});
		}
	};

})(); // Flaav

$(document).ready(function() {
	Flaav.init($);
});