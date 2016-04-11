var FlaavDashboard = (function() {
	var animation_time = 500, sidebar;
	return {
		init: function() {
			sidebar =  $("#sidebar");
			page_dashboard();
			if(typeof MODULE === "string") {
				modules = MODULE.split(" ");
				for(var i=0; i<modules.length; i++) {
					switch(modules[i]) {
						case "dashboard-home":
							page_dashboard_home();
							break;
						case "media-add":
						case "media-edit":
							page_media_add();
							break;
						case "media-view":
							page_media_view();
							break;
						case "media-single-view":
							page_media_single_view();
							break;
						case "dashboard-plugins":
							page_dashboard_plugins();
							break;
						default:
							break;
					}
				}
			}
			//===
		}

	};

	// Set active submenu according to currentw window URL
	function set_active_submenu() {
		var window_url = window.location.pathname;
		sidebar.find(".sub-menu a").each(function() {
			var item = $(this);
			if(window_url.search(item.attr("href"))>=0 && item.attr("href")!="#" ) {
				item.closest("li").addClass("active").addClass(item.attr("class"));
				item.closest(".sub-menu").data("active", true).show();
			}
		});
	}
	// ===
	
	function get_activated_plugins(plugins_page) {
	// Get activated plugin list and populate Activated Plugin sub-menu
		var plugin_link_container = sidebar.find(".dashboard-plugins .sub-menu"), source = [];

		var directives = {
					"view": {
						href: function() {
							return this.url;
						},
						html: function(item) {
							return this.name;
						}
					},
					"settings": {
						href: function() {
							return this.url.replace("view", "settings");
						}
					}
		};

		if(plugins_page===true) {
			/* If calling from plugins_page, server request is not required to
			 re-populate the active plugins menu.
			*/
			$("#plugins .activated").each(function() {
				var item = $(this);
				source.push({"name": item.find(".name").text(), "url": item.find(".button.view").attr("href") });
			});
			plugin_link_container.render(source, directives=directives);
		}
		else {

			$.getJSON( "/dashboard?get=active-plugins", function(data) {
				plugin_link_container.render(data, directives=directives);
				set_active_submenu();
			});
		}
		set_active_submenu();
	} // get_activated_plugins
	//===

	function page_dashboard() {
		var header=$("#header"), footer = $("#footer"), sb_width = sidebar.outerWidth(true),
			main = $("#main"), win = $(window), logo = $("#logo"), body = $("body"), sb_children = sidebar.children("li");
		
		body.addClass("dashboard");

		sb_children.each(function() {
			var item = $(this);
			if(body.hasClass(item.attr("class")))
				item.addClass("active");
		});

		get_activated_plugins();
		set_active_submenu();

		// sub-menu
		sidebar.find(".sub-menu").each(function() {
			var sub = $(this);
			sub.closest("li").hover(function() {
				if(!sub.data("active"))
					sub.stop().slideDown(animation_time);
			}, function() {
				if(!sub.data("active"))
					sub.stop().slideUp(animation_time);
			});
		});
		// ===

		Flaav.add_on_rez_fns(function() {
			main.css("margin-left", sb_width).css("max-width", win.width() - sb_width);
		});

		// add icons to left menu
		$("#sidebar a").each(function() {
			if(!$(this).hasClass("view") && !$(this).hasClass("settings"))
				$(this).append($('<span class="icon"> </span>'));
		});
		// ===
	}// page_dashboard()

	function page_dashboard_home() {
		if(typeof media_stat !== "undefined") {
			var canvas = document.getElementById("media_stat").getContext("2d");
			for(i=0; i<media_stat.length; i++) {
				media_stat[i]["color"] = Flaav.get_color();
			}
			new Chart(canvas).PolarArea(media_stat);
		}

		// Load blog feed
		
		$.getJSON( "/dashboard?get=blog-feed", function( data ) {
			if(data.length > 0) {
				var blog_feeds = $('#blog_feed');
				var directives = {
						"link": {
							href: function () {
								return this.link;
							},
							html: function() {
								return "";
							}
						},
						"summary": {
								html: function() {
									return $('<textarea />').html(this.summary).text();
								}
						},
						"published": {
								text: function() {
									return moment.utc(new Date(this.published)).local().calendar();
								}
						}
					};
				data.shift(); // removing first element of the array. The blog title
				blog_feeds.render(data, directives=directives);

				var img, item, avatar;
				blog_feeds.find(".wp-post-image").each(function() {
					img = $(this); item = img.closest("li");
					avatar = $('<span class="avatar"> </span>');
					avatar.css("background-image", 'url("'+img.attr("src")+'")');
					img.remove();
					item.prepend(avatar);
				});
			}
		});
		// ===

		// Delete Search history
			$("#search_history").on("click", ".item .delete", function() {
				var del_link = $(this);
				$.getJSON(del_link.attr("href"), function( data ) {
					if(data.status=="success") {
						del_link.closest(".item").fadeOut(animation_time, function() { $(this).remove(); });
					}
					else {
						$('<span class="message">'+data.message+'</span>').insertAfter(del_link);
					}
				});
				return false;
			});
			// ===

		// Get search history
		var sh_cont = $("#search_history"), sh_title = sh_cont.find(".title").first(), sh_items = sh_cont.find(".items");
		sh_items.addClass("hidden");

		sh_title.append($('<span class="loading"> </span>'));
		$.getJSON( "/search?get=search-history", function( data ) {
			sh_title.find(".loading").remove();
			if(data.length==0) {
				$("<p>You don't have any saved searches.</p>").insertAfter(sh_title);
				return false;
			}

			var sh_num=1, directives = {
				"details": {
					value: function() {
						return JSON.stringify(this.details);
					}
				},
				"title": {
					href: function() {
						return "/search/results?search_id="+this.search_id;
					}
				},
				"created-on": {
					text: function() {
						return moment.utc(this.created_on).local().calendar();
					}
				},
				"delete": {
					href: function() {
						return "/search?delete="+this.search_id
					}
				},
				"view-results": {
					href: function() {
						return "/search/results?search_id="+this.search_id;
					}
				}
			};

			sh_items.render(data, directives);
			sh_items.removeClass("hidden");
			sh_items.find(".item").first().mouseenter();
		});
		// ===

		var details, details_cont = sh_cont.find(".details"), details_item, details_list = $('<ul class="noul"></ul>');
		var labels = {
			"market_goal": "Market Goal",
			"campaign_length": "Campaign Length",
			"select_markets": "Select markets",
			"budget": "Budget",
			"viewership_industry": "Viewership Industry",
			"conversion_rate": "Conversion Rate",
			"demography": "Demographies",
			"media_type": "Media type",
			"customer_type": "Customer type",
			"geography": "Geographies"
		};

		sh_items.on("mouseenter", ".item", function() {
			details = $(this).find(".details").val();
			if(details_cont.data("current")!=details) {
				details_cont.data("current", details);
				details = JSON.parse(details);
				details_list.html('');
				directives = {};
				for(key in details) {
					details_item = $('<li></li>').clone();
					if(details[key] instanceof Array) {
						details[key] = details[key].join(", ");
					}
					details_item.html(details[key]).addClass(key);
					details_list.append(details_item);
				}

				// details_list.render([details]);
				details_list.find("li").each(function() {
					item = $(this);
					if($.trim(item.text()).length==0)
						item.remove();
					else {
						key = $(this).attr("class");
						$(this).prepend("<label>"+labels[key]+": </label>");
					}
				});
				// details_list.append('<li><a href="'+$(this).find("a.title").attr("href")+'" class="button">view results</a></li>');
				details_cont.html(details_list);
			}
		});
	}// page_dashboard_home()

	function page_dashboard_plugins() {
		$("#main form.activate-form, #main form.deactivate-form").submit(function() {
			var form = $(this), item = form.closest(".item"), loading = item.find(".loading");
			loading.show();
			$.ajax({
				type: "POST",
				url: form.attr("action"),
				data: form.serialize(),
				dataType: "json",
				success: function(data) {
					loading.fadeOut(animation_time);
					if(data.status=="success") {
						item.removeClass("activated deactivated");
						if(form.hasClass("activate-form")) {
							item.addClass("activated");
						}
						else if(form.hasClass("deactivate-form")) {
							item.addClass("deactivated");
						}
						get_activated_plugins(plugins_page=true);
					}
				}
			});
			return false;
		});
	}// page_dashboard_plugins()
	
	function page_media_single_view() {
		$(".www a, .banner a").each(function() {
			var item = $(this), href= item.attr("href");
			if(href.indexOf("http") < 0)
				item.attr("href", "http://"+item.attr("href"));
		});
	}

	function page_media_view() {
		var filter_options = [], url = "/dashboard/media?filter=business&name=", business_names = [], item, b_name;
		if(window.location.href.indexOf("filter")==-1) {
			$("#media_items .media-item").each(function() {
				item = $(this);
				b_name = $.trim(item.find(".business-name").text());
				if($.inArray(b_name, business_names)<0) {
					business_names.push(b_name);
					filter_options.push({"b-name": b_name, "url": url+encodeURIComponent(b_name)});
				}
			});
			
			filter_options.sort(function(a, b) { return a["b-name"].localeCompare(b["b-name"]); });
			var directives = {
				"b-name": {
					value: function() { return this.url; }
				}
			};
			$("#filters").render(filter_options, directives);
			$("#filters").prop("selectedIndex", 0);
			$("#filters").change(function() {
				window.location = $(this).val();
			});
		}
		else {
			var loc = window.location.href;
			$(".filter-container").html("Showing all ad-packages from '"+decodeURIComponent(loc.substr(loc.indexOf("name=")+5, loc.indexOf("name=")+99))+"'.");
		}
	}// page_media_view()

	function page_media_add() {
		$.getJSON( "/dashboard/media?get=industries", function( data ) {
			Flaav.enable_autocomplete($(".autocomplete-industry"), data);
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

		$(".more-info").click(function() {
			var item = $(this);
			item.closest("li").find(".hidden.info").toggle(350);
			if(item.hasClass("active")) {
				item.removeClass("active");
				item.text("more info");
			}
			else {
				item.addClass("active");
				item.text("hide info");
			}
			return false;
		});

		$("#geography-1").click().click();

		// Show custom geo location textfield when "Other" is enabled
		
		if($("#media_type-7").is(":checked")) {
			$("#custom_media_type").fadeIn(animation_time);
		}

		$("#media_type-7").click(function() {
			if($(this).is(":checked")) {
				$("#custom_media_type").fadeIn(animation_time);
			}
			else {
				$("#custom_media_type").fadeOut(animation_time);
			}
		});
		// ===

		// Tooltip for info buttons
		$(".info").each(function() {
			var item = $(this);
			tttext.attach(item, {"message": item.find(".hidden").text() });
		});
		// ====
	}
})();


window.onload = function() {
	FlaavDashboard.init();
};