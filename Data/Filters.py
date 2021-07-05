
class Filter:

    AND = "AND"
    OR = "OR"

    def __init__(self, logical_sign = AND):
        self.logical_sign = logical_sign
        self.statement = ""


class EqualFilter(Filter):
    def __init__(self, value, label, logical_sign=Filter.AND):
        super().__init__(logical_sign)
        self.statement = "%s = %s" % (label, value)
