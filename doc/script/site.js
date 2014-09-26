$(document).ready(function() {

	var $sections = $(".section"),
		i, max = $sections.length,
		currentSection = 0;

	function changeSection(new_section) {

		$("#ch-" + currentSection).hide();
		currentSection = new_section;
		$("#ch-" + currentSection).fadeIn();

	}

	$sections.hide();
	$(".tutorialnav").hide();
	$(".docnav").hide();

	$(".tutorialnav").click(function(event){

		var no = $(event.target).attr("id").slice(-1);
		changeSection(no);

	});

	$("#ch-" + currentSection).fadeIn();

	$("#home").click(function() {

		changeSection(0);
		$(".tutorialnav").fadeOut();
		$(".docnav").fadeOut();

	});

	$("#doc").click(function() {

		changeSection(0);
		$(".docnav").fadeIn();
		$(".tutorialnav").hide();

	});

	$("#tutorial").click(function() {

		changeSection(1);
		$(".tutorialnav").fadeIn();
		$(".docnav").hide();

	});

});