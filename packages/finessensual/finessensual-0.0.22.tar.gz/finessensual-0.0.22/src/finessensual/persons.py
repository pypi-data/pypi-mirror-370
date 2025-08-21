import re
from datetime import date

class Person():
    def __init__( self,
                  number: int,
                  name: str,
                  carreerstart: date,
                  carreerend: date,
                 ):
        self.name = name
        self.number = number
        self.start = carreerstart
        self.end = carreerend

    # this one still needs to be finished (and was never used)
    def seniority( self,
                   on: date ):
        delta = on - carreerstart;
        return delta

    def __repr__( self ):
        return f"{self.number}\t{self.name}\n"
        

def parse_person( description: str ) -> tuple[int,str]:
    match = re.search( r'(.+)\s+\(([^)]+)\)', description )
    return ( match.group(2), match.group(1) )


