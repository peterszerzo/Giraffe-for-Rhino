class RhinoInput():


    def __init__(self, s):
        
        self.string = s.strip()


    def has_number(self):

        return self.get_before("[", "{").strip().isdigit()


    def get_before(self, char1, char2):

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

        i1 = self.string.find(char1)
        i2 = self.string.find(char2)

        if ((i1 != -1) and (i2 != -1) and (i2 > i1)):

            return self.string[(i1 + 1):(i2)]

        return ""


    def get_no(self):

        if (self.has_number()):

            return int(self.get_before("[", "{").strip())

        return -1        


    def get_prop(self):

        between_square_brackets = self.get_between("[", "]").strip()

        if (self.has_number()):

            return between_square_brackets

        elif (between_square_brackets == ""):

            return self.get_before("{", "{").strip()

        return between_square_brackets


    def get_name(self):

        return self.get_between("{", "}").strip()