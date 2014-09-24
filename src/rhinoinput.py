##
# RhinoInput module.
# A RhinoInput string is structured in the following formats:
# - format 1: *number* [ *property* ] { *name* }
# - format 2: *property* { *name* }
# Format 2 should be used if no number is present - Rhino will not allow layer names to start with a square bracket.
##

class RhinoInput():


    def __init__(self, s):

        """Initialize string."""
        
        self.string = s.strip()


    def has_number(self):

        """Returns True if input a number is specified."""

        return self.get_before("[", "{").strip().isdigit()


    def get_before(self, char1, char2):

        """Returns string before two characters."""

        i1 = self.string.find(char1)
        i2 = self.string.find(char2)

        if ((i1 == -1) and (i2 == -1)):

            return self.string

        if ((i1 == -1) or (i2 == -1)):

            j = max(i1, i2)

        else:

            j = min(i1, i2)

        return self.string[0:j]


    def get_between(self, char1, char2):

        """Returns string between two characters."""

        i1 = self.string.find(char1)
        i2 = self.string.find(char2)

        if ((i1 != -1) and (i2 != -1) and (i2 > i1)):

            return self.string[(i1 + 1):(i2)]

        return ""


    def get_no(self):

        """Returns number."""

        if (self.has_number()):

            return int(self.get_before("[", "{").strip())

        return -1        


    def get_prop(self):

        """Returns property."""

        between_square_brackets = self.get_between("[", "]").strip()

        if (self.has_number()):

            return between_square_brackets

        elif (between_square_brackets == ""):

            return self.get_before("{", "{").strip()

        return between_square_brackets


    def get_name(self):

        """Returns name."""

        return self.get_between("{", "}").strip()