class RhinoInput():
    
    def __init__(self, s):
        
        self.string = s.strip()

    def get_no(self):

        i1 = self.string.find("[")
        i2 = self.string.find("{")

        if ((i1 == -1) and (i2 == -1)):

            return int(self.string)

        if ((i1 == -1) or (i2 == -1)):

            j = max(i1, i2)

        else:

            j = min(i1, i2)

        no_string = self.string[0:j].strip()

        return int(no_string)

    def get_prop(self):

        i1 = self.string.find("[")
        i2 = self.string.find("]")

        if ((i1 != -1) and (i2 != -1) and (i2 > i1)):

            return self.string[(i1 + 1):(i2)].strip()

        return ""

    def get_name(self):

        i1 = self.string.find("{")
        i2 = self.string.find("}")

        if ((i1 != -1) and (i2 != -1) and (i2 > i1)):
            
            return self.string[(i1 + 1):(i2)].strip()

        return ""