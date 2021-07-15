class CommissionScheme:
    def __init__(self,
                 scheme: str):
        self.name = scheme
        self.commission = 0

    def calculate_commission(self,
                             quantity: float,
                             price: float) -> float:
        min_com = 0.0
        trans_com = 0.0

        if self.name == 'avanza_medium':
            min_com = 69
            trans_com = quantity * price * 0.00069
            if min_com <= trans_com:
                return min_com
            else:
                return trans_com
        elif self.name == '':
            return 0.0
