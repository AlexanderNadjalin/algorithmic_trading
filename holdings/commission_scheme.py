class CommissionScheme:
    def __init__(self,
                 scheme: str):
        self.name = scheme
        self.commission = 0

    def calculate_commission(self,
                             quantity: float,
                             price: float) -> float:
        # Avanza.se
        if self.name == 'avanza_mini':
            min_com = 1.0
            trans_com = quantity * price * 0.0025
            if quantity * price < 400.0:
                return min_com
            else:
                return trans_com
        elif self.name == 'avanza_small':
            min_com = 39.0
            trans_com = quantity * price * 0.0015
            if quantity * price < 26000.0:
                return min_com
            else:
                return trans_com
        elif self.name == 'avanza_medium':
            min_com = 69.0
            trans_com = quantity * price * 0.00069
            if quantity * price < 100000.0:
                return min_com
            else:
                return trans_com
        elif self.name == 'avanza_fast':
            return 99.0
        # No commission
        else:
            return 0.0
