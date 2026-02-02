from decimal import Decimal 

class UTXOManager:
    def __init__(self):
        # Store UTXOs as dictionary: (tx_id, index) -> {amount, owner}
        self.utxo_set = {}

    def add_utxo(self, tx_id: str, index: int, amount: float, owner: str):
        """
        Add a new UTXO to the set.
        """
        key = (tx_id, index)
        
        self.utxo_set[key] = {
            "amount": Decimal(str(amount)), 
            "owner": owner
        }

    def remove_utxo(self, tx_id: str, index: int):
        """
        Remove a UTXO (when spent).
        """
        key = (tx_id, index)
        if key in self.utxo_set:
            del self.utxo_set[key]
        
    def get_balance(self, owner: str) -> Decimal: 
        """
        Calculate total balance for an address.
        """
        balance = Decimal('0.0') 
        for utxo in self.utxo_set.values():
            if utxo["owner"] == owner:
                balance += utxo["amount"]
        return balance

    def exists(self, tx_id: str, index: int) -> bool:
        """
        Check if UTXO exists and is unspent.
        """
        return (tx_id, index) in self.utxo_set

    def get_utxos_for_owner(self, owner: str) -> list:
        """
        Get all UTXOs owned by an address.
        """
        owned_utxos = []
        for (tx_id, index), data in self.utxo_set.items():
            if data["owner"] == owner:
                utxo_info = {
                    "tx_id": tx_id,
                    "index": index,
                    "amount": data["amount"],
                    "owner": data["owner"]
                }
                owned_utxos.append(utxo_info)
        return owned_utxos