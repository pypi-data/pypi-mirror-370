from datetime import date
from finessensual.persons import Person
from finessensual.expenditures import ExpenditureType, ExpenditurePhase
from finessensual.budget import BudgetItem

import re

class Project():
    def __init__( self,
                  name      : str,
                  number    : str,
                  simple    : str,
                  sheetname : str,
                  promotor  : Person,
                  copromotor: Person,
                  afdeling  : int,
                  eenheid   : str,
                  source    : str,
                  begindate : date,
                  enddate   : date,
                  
                 ):
        
        self.name       = re.sub( ':', '-', name )
        self.number     = number
        self.simple     = simple == 'Y'
        self.sheet      = sheetname
        self.promotor   = promotor
        self.copromotor = copromotor
        self.afdeling   = afdeling
        self.eenheid    = eenheid
        self.source     = source
        self.begindate  = begindate
        self.enddate    = enddate
        if simple == 'Y':
            self.budget = None
        else:
            self.budget     = {}
            for i in ExpenditureType:
                self.budget[i] = None

    def __repr__( self ) -> str:
        retval = f"""
        Projectnr  : {self.number}
        Projectname: {self.name}
        Begindate  : {self.begindate}
        Enddate    : {self.enddate}
        Promotor   : {self.promotor}
        Copromotor : {self.copromotor}
        Budgetcode : {self.budgetcode()}
        Source     : {self.source}
        Budget     :
        """
        if self.simple:
            retval += f"{self.budget}"
        else:
            retval += f"""
            - Salaries    : {self.budget[ExpenditureType.WEDDEN]}
            - Operational : {self.budget[ExpenditureType.WERKING]}
            - Equipment   : {self.budget[ExpenditureType.UITRUSTING]}
            - Overhead    : {self.budget[ExpenditureType.OVERHEAD]}
            - Reservations: {self.budget[ExpenditureType.RESERVATIES]}
            """
        return retval
    

    def blurb( self ) -> str:
        return self.number + ' ' + self.name;

    def sheetname( self ) -> str:
        return self.sheet
        
    def budgetcode( self ) -> str:
        return f"{self.afdeling}/{self.eenheid}/{self.number}"

    def register_budget( self,
                         type: ExpenditureType,
                         value: float ):
        if self.simple:
            self.budget = BudgetItem( value, 0, 0 )
        else:
            print( "Error: trying to register simple budget value into a typed project" )
            exit(1)

    def issimple( self ) -> bool:
        return self.simple
    
