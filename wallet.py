import uuid

class Wallet:
    def __init__(self):
        self.address = str(uuid.uuid4())
        self.balance = 0

    def __repr__(self):
        return f"Wallet<{self.address}>"
