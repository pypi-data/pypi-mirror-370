from finessensual.expenditures import ExpenditureType, ExpenditurePhase, Expenditure

class CostItem():
    def __init__( self,
                  nature     : str,
                  opponent   : str,
                  date       : str,
                  value      : float,
                  description: str = '',
                 ):
        self.nature      = nature
        self.description = description
        self.opponent    = opponent or 'NN'
        self.value       = value
        self.date        = date

    def __repr__( self ) -> str:
        return " / ".join( [ self.date,
                             self.nature, self.description, self.opponent,
                             str(self.value),
                             self.description ] )
        
class SalaryCost(Expenditure):
    def __init__( self,
                  phase     : ExpenditurePhase,
                  personnr  : str,
                  date      : str,
                  fraction  : float,
                  projectnr : str,
                 ):
        super().__init__( ExpenditureType.WEDDEN,
                          phase )
        self.personnr  = personnr
        self.date      = date
        self.fraction  = fraction
        self.projectnr = projectnr
        self.items     = []

    def __repr__( self ) -> str:
        repr = " / ".join( [ str( self.projectnr ), self.personnr, self.date, str(self.fraction) ] ) + ' -> ' + str( self.totalcost() ) + "\n"
        for i in self.items:
            repr += '  ' + str(i) + '\n'
        return repr

    def additem( self,
                 nature  : str,
                 employee: int,
                 date    : str,
                 value   : float ) :
        self.items.append( CostItem( nature   = nature,
                                     opponent = employee,
                                     date     = date,
                                     value    = value ) )
    def totalcost( self ) -> float:
        cost = 0.0
        for i in self.items:
            cost += i.value
        return cost

    def overview( self ) -> str:
        overview = ''
        for item in self.items:
            overview += item.nature + ": " + f"{item.value:.2f}\n"
        return overview


            
class OperationCost(Expenditure):
    def __init__( self,
                  phase     : ExpenditurePhase,
                  projectnr : str,
                  batchnr   : str,
                  date      : str,
                  nature    : str,
                 ):
        super().__init__( ExpenditureType.WERKING,
                          phase )
        self.projectnr = projectnr
        self.batchnr   = batchnr
        self.date      = date
        self.items     = []
        self.nature    = nature
        
    def __repr__( self ) -> str:
        repr = " / ".join( [ self.projectnr, self.batchnr, self.date ] ) + ' -> ' + str( self.totalcost() ) + "\n"
        for i in self.items:
            repr += '  ' + str(i) + '\n'
        return repr

    def additem( self,
                 nature  : str,
                 opponent: str,
                 date    : str,
                 value   : float,
                 description: str,
                ) :
        self.items.append( CostItem( nature      = nature,
                                     opponent    = opponent,
                                     date        = date,
                                     value       = value,
                                     description = description ) )
    def totalcost( self ) -> float:
        cost = 0.0
        for i in self.items:
            cost += i.value
        return cost

    def overview( self ) -> str:
        overview = ''
        for item in self.items:
            overview += item.description + " // " + item.opponent + ": " + f"{item.value:.2f}\n----\n"
        return overview

class EquipmentCost(Expenditure):
    def __init__( self,
                  phase     : ExpenditurePhase,
                  projectnr : str,
                  batchnr   : str,
                  date      : str,
                  nature    : str,
                 ):
        super().__init__( ExpenditureType.UITRUSTING,
                          phase )
        self.projectnr = projectnr
        self.batchnr   = batchnr
        self.date      = date
        self.items     = []
        self.nature    = nature
        
    def __repr__( self ) -> str:
        repr = " / ".join( [ self.projectnr, self.batchnr, self.date ] ) + ' -> ' + str( self.totalcost() ) + "\n"
        for i in self.items:
            repr += '  ' + str(i) + '\n'
        return repr

    def additem( self,
                 nature  : str,
                 opponent: str,
                 date    : str,
                 value   : float,
                 description: str,
                ) :
        self.items.append( CostItem( nature      = nature,
                                     opponent    = opponent,
                                     date        = date,
                                     value       = value,
                                     description = description ) )
    def totalcost( self ) -> float:
        cost = 0.0
        for i in self.items:
            cost += i.value
        return cost

    def overview( self ) -> str:
        overview = ''
        for item in self.items:
            overview += item.description + " // " + item.opponent + ": " + f"{item.value:.2f}\n----\n"
        return overview
    
    
class OverheadCost(Expenditure):
    def __init__( self,
                  phase     : ExpenditurePhase,
                  projectnr : str,
                  batchnr   : str,
                  date      : str,
                 ):
        super().__init__( ExpenditureType.OVERHEAD,
                          phase )
        self.projectnr = projectnr
        self.batchnr   = batchnr
        self.date      = date
        self.items     = []
        
    def __repr__( self ) -> str:
        repr = " / ".join( [ self.projectnr, self.batchnr, self.date ] ) + ' -> ' + str( self.totalcost() ) + "\n"
        for i in self.items:
            repr += '  ' + str(i) + '\n'
        return repr

    def additem( self,
                 nature  : str,
                 opponent: str,
                 date    : str,
                 value   : float,
                ) :
        self.items.append( CostItem( nature      = nature,
                                     opponent    = opponent,
                                     date        = date,
                                     value       = value,
                                    ) )
    def totalcost( self ) -> float:
        cost = 0.0
        for i in self.items:
            cost += i.value
        return cost

    def overview( self ) -> str:
        overview = ''
        for item in self.items:
            overview += item.description + " // " + item.opponent + ": " + f"{item.value:.2f}\n----\n"
        return overview
    
