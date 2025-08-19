import re


class Nominal:
    """A class to manage nominals for modal logic."""
    def __init__(self):
        self.nominal_dict = {
            "w": {},
            "v": {},
            "u": {}
        }
    
    def get_nominal(self, name: str) -> str:
        """Returns a fresh nominal based on the name and value."""
        if name not in self.nominal_dict:
            raise ValueError(f"Invalid nominal name: {name}")
        
        temp_dict = self.nominal_dict[name]
        new_nom = f"{name}_{len(temp_dict)}"
        temp_dict[new_nom] = True
        return new_nom
    
    def pop_nominal(self,name:str):
        """Pops the last nominal(last generated) for a nominal string

        Args:
            name (str): nominal to pop

        Raises:
            ValueError: Invalid nominal name
        """
        if name not in self.nominal_dict:
            raise ValueError(f"Invalid nominal name: {name}")
        
        temp_dict = self.nominal_dict[name]

        if (len(temp_dict)==0):
            return
        
        pop_nom = f"{name}_{len(temp_dict)-1}"
        temp_dict.pop(pop_nom)

    def __str__(self):
        return f"Nominal(nominal_dict={self.nominal_dict})"



def checkNominal(string:str):
    return bool(re.fullmatch(r"\b[uwv](?:_\d+)?\b",string))


def getNominals(string:str):
    matches = re.findall(r"\b[uwv](?:_\d+)?\b", string)
    return matches