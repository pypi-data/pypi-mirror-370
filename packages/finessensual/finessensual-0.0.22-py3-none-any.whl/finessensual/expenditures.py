from enum import Enum

class ExpenditureType(Enum):
    WEDDEN       = 1
    WERKING      = 2
    UITRUSTING   = 3
    OVERHEAD     = 4
    RESERVATIES  = 5
    
class ExpenditurePhase(Enum):
    PLANNED = 1
    FIXED   = 2
    BOOKED  = 3
    OVERRULED = 4
    
class Expenditure():
    def __init__( self,
                  type: ExpenditureType,
                  phase: ExpenditurePhase ):
        self.type  = type
        self.phase = phase

phasetranslation = { 'P': ExpenditurePhase.PLANNED,
                     'F': ExpenditurePhase.FIXED,
                     'B': ExpenditurePhase.BOOKED,
                     'O': ExpenditurePhase.OVERRULED,
                    }
        
def expenditure_phase( c: str ) -> ExpenditurePhase:
    return phasetranslation[c[0]]

