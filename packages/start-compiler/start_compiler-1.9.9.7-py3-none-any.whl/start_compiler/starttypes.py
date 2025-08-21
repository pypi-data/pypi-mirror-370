import copy

class StartError(Exception):
    lineNumber = 0

class start:
    def copy(self, other):
        for attr_name, attr_value in vars(self).items():
            vars(other)[attr_name] = copy.deepcopy(attr_value)

    def clone(self):
        return copy.deepcopy(self)

    def to_key(self):
        if isinstance(self, text):
            return str(self.value)
        if isinstance(self, number):
            return str(int(self.value))
        key = ""
        for attr_name, attr_value in vars(self).items():
            key += attr_value.to_key()

        return key

    def toStr(self):
        if type(self) == start:
            return "null"

        if isinstance(self, number) or isinstance(self, text):
            return str(self.value)

        result = ""
        for attr_name, attr_value in vars(self).items():
            if isinstance(attr_value, start):
                result += attr_value.toStr()
        return result

    def toStrStructured(self):
        if type(self) == start:
            return "null"

        if isinstance(self, number) or isinstance(self, text):
            return str(self.value)

        result = ""
        for attr_name, attr_value in vars(self).items():
            if isinstance(attr_value, start):
                result += "[" + attr_value.toStrStructured() + "],"

        return result[0:-1]

    def __repr__(self):
        return type(self).__name__

    def __bool__(self):
        return bool(self.value)

class number(start):
    def __init__(self, value=0):
        # check for start objects
        if isinstance(value, start):
            if hasattr(value, "value"):
                value = value.value
            elif type(value) is start:
                raise StartError("null pointer exception. You forgot to instantiate the object.")
            else:
                raise StartError(f"{value} is not a number or python floatable type")

        # check if it can be converted to a start number
        try:
            self.value = int(value) if float(value).is_integer() else float(value)
        except (ValueError, TypeError):
            raise StartError(f"{value} is not a number or python floatable type")

class text(start):
    def __init__(self, value=''):
        # check for start objects
        if isinstance(value, start):
            if hasattr(value, "value"):
                value = value.value
            elif type(value) is start:
                raise StartError("null pointer exception. You forgot to instantiate the object.")
            else:
                raise StartError(f"{value} is not a text or python string type")

        # check if it can be converted to a start text, should always work
        try:
            self.value = str(value)
        except (ValueError, TypeError):
            raise StartError(f"{value} is not a text, number or python stringable type")