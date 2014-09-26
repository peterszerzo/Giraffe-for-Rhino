$(document).ready(function() {

	var $sections = $(".section"),
		i, max = $sections.length,
		currentSection = 0,
		currentType = "home";

	function getCurrent() {

		return $("#" + currentType + "-" + currentSection);

	}

	function fadeInCurrent() {

		getCurrent().fadeIn();

	}

	function changeSection(newType, newSection) {

		getCurrent().hide();
		currentType = newType;
		currentSection = newSection;
		getCurrent().fadeIn();

	}

	$sections.hide();
	$(".tut-nav").hide();
	$(".doc-nav").hide();

	fadeInCurrent();

	$(".tut-nav, .doc-nav").click(function(event){

		event.preventDefault();

		var id = $(event.target).attr("id"),
			no = id.slice(-1),
			type = id.substr(0, id.indexOf('-'));

		changeSection(type, no);

	});

	$("#home").click(function(event) {

		event.preventDefault();

		changeSection("home", 0);
		$(".tut-nav").fadeOut();
		$(".doc-nav").fadeOut();

	});

	$("#doc").click(function(event) {

		event.preventDefault();

		changeSection("doc", 0);
		$(".doc-nav").fadeIn();
		$(".tut-nav").hide();

	});

	$("#tut").click(function(event) {

		event.preventDefault();

		changeSection("tut", 0);
		$(".tut-nav").fadeIn();
		$(".doc-nav").hide();

	});

});