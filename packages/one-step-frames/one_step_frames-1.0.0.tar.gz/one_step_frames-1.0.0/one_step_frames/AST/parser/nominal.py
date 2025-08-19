import string
import re


class Nominal():
    def __init__(self) -> None:
        self._availableLetters = [letter for letter in string.ascii_lowercase if letter != 'i']
        self._lastLetter = 0
        self._nominals = {}


    def createMapping(self,formula:str)->dict[str,str]:
        nominals = set(self._getNominals(formula))

        for i in nominals:
            self._addNominal(i)
        
        return self._nominals
    
    def _getNominals(self,string:str)->list[str]:
        matches = re.findall(r"\b[uwv](?:_\d+)?\b", string)
        return matches
    
    def reset(self):
        self._lastLetter = 0
        self._nominals = {}

    def _addNominal(self,newNominal:str)->None:
        returnedLetter = self._availableLetters[self._lastLetter]
        self._lastLetter+=1

        if (newNominal in self._nominals.keys()):
            raise KeyError("Key already exists")
        
        self._nominals[newNominal]=returnedLetter
    
    def getMapping(self):
        return self._nominals