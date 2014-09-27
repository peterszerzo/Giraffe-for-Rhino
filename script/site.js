$(document).ready(function() {

	// adding a prefix and a suffix to each member in a string list, and concatenate with a separator
	function solidConcat(stringList, prefix, suffix, separator) {

		var i, max = stringList.length,
			result = "";

		for (i = 0; i < max; i += 1) {

			result += prefix + stringList[i] + suffix;

			if (i !== max - 1) {

				result += separator;

			}

		}

		return result;

	}

	var Jumper = {

		types: [],

		type: "home",
		section: 0,

		getCurrent: function() {

			return $("#" + this.type + "-" + this.section);

		},

		fadeInCurrent: function() {

			this.getCurrent().fadeIn();

		},

		jump: function(newType, newSection) {

			this.getCurrent().hide();
			this.type = newType;
			this.section = newSection;
			this.getCurrent().fadeIn();

		},

		getIDs: function() {

			return solidConcat(this.types, "#", "", ", ");

		},

		getNavIDs: function() {

			return solidConcat(this.types, "#", "-nav", ", ");

		},

	};

	Jumper.types = ["home", "tut", "doc"];

	$(".section").hide();
	$(Jumper.getNavIDs()).hide();

	Jumper.fadeInCurrent();

	$(Jumper.getNavIDs()).click(function(event){

		var id, no, type;

		event.preventDefault();

		no = $(event.target).attr("data-ch");

		if (no) {

			id = $(this).attr("id");
			type = id.slice(0, id.indexOf('-'));

			Jumper.jump(type, no);

		}

	});

	$(Jumper.getIDs()).click(function() {

		var id;

		event.preventDefault();

		$(Jumper.getNavIDs()).hide();

		id = $(this).attr("id");

		Jumper.jump(id, 0);
		$("#" + id + "-nav").fadeIn();

	});

});