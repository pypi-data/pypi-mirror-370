

class AbstractOperator:
    """
    Represents an abstract operator with a symbol and arity.
    Attributes:
        symbol (str): The symbol representing the operator.
        arity (int): The arity of the operator, indicating how many operands it takes.
    Methods:
        getSymbol() -> str: Returns the symbol of the operator.
        getArity() -> int: Returns the arity of the operator.
        setArity(arity: int) -> None: Sets the arity of the operator
        setSymbol(symbol: str) -> None: Sets the symbol of the operator.
    """
    
    def __init__(self,symbol,arity,preference=0) -> None:
        self.symbol = symbol
        self.arity = arity
        self.preference = preference 


    def getPreference(self) -> int:
        return self.preference
    

    def setPreference(self, preference: int) -> None:
        self.preference = preference

    
    def getArity(self) -> int:
        return self.arity
    

    def setArity(self,arity:int) -> None:
        self.arity = arity
    

    def getSymbol(self) -> str:
        return self.symbol
    

    def setSymbol(self,symbol:str) -> None:
        self.symbol = symbol


    def __str__(self) -> str:
        return f"AbstractOperator(symbol:{self.symbol}, arity:{self.arity}, preference:{self.preference})"
    

    def __repr__(self) -> str:        
        return self.__str__()
    

    def __eq__(self, other) -> bool:
        if not isinstance(other, AbstractOperator):
            return False
        return self.symbol == other.symbol and self.arity == other.arity