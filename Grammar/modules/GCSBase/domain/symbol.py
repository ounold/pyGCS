from ..domain.types.SymobolType import SymbolType


class Symbol:
    def __init__(self, value: str = None, symbol_type: SymbolType = None, index: int = None, *args):
        self.value = value
        self.symbol_type = symbol_type
        # Index added for performance improvement
        self.index = index

    def is_terminal(self):
        return self.symbol_type == SymbolType.ST_TERMINAL

    def is_non_terminal(self):
        return self.symbol_type == SymbolType.ST_NON_TERMINAL

    def is_start(self):
        return self.symbol_type == SymbolType.ST_START

    def is_universal(self):
        return self.symbol_type == SymbolType.ST_UNIVERSAL

    def json_str(self):
        json_value = dict()
        json_value['value'] = self.value
        json_value['index'] = self.index
        return json_value

    @staticmethod
    def from_dict(symbol):
        return Symbol(symbol['value'], None, symbol['index'])

    def __eq__(self, other):
        if type(self) is type(other):
            if self.symbol_type == SymbolType.ST_TERMINAL:
                return self.value == other.value
            else:
                #return self.index == other.index
                return (self.value, self.symbol_type) == (other.value, other.symbol_type)
        else:
            return False

    def __hash__(self) -> int:
        return hash((self.value, self.symbol_type))

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.value

