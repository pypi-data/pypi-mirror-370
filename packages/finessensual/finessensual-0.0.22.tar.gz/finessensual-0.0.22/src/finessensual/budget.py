class BudgetItem():
    def __init__( self,
                  total  : float,
                  fixed  : float,
                  booked : float,
                 ):
        self.total   = total
        self.fixed   = fixed
        self.booked  = booked
        self.planned = 0.0

    
    def remaining( self ):
        return self.total - self.fixed - self.booked - self.planned
    
    def __repr__( self ) -> str:
        return f"T = {self.total: >10,.2f} / P = {self.planned: >10,.2f} / F = {self.fixed: >10,.2f} / B = {self.booked: >10,.2f} / R = {self.remaining(): >10,.2f}"

    def overview( self ):
        return ( self.total, self.planned, self.fixed, self.booked, self.remaining() )

    @staticmethod
    def oraclelabels():
        return ( 'Total', 'Planned', 'Fixed', 'Booked', 'Remaining' )

    @staticmethod
    def planninglabels():
        return ( 'Planned', 'Fixed', 'Booked', 'Overruled', 'Remaining' )
