from validate import Validator

class Mempool:
    def __init__(self, max_size=50):
        self.transactions = [] 
        self.spent_utxos = set() # Tracks UTXOs referenced in mempool to prevent double-spends
        self.max_size = max_size

    def add_transaction(self, tx, utxo_manager):
        """Validates and adds a transaction to the mempool."""
        if len(self.transactions) >= self.max_size:
            self._evict_lowest_fee(utxo_manager)

        # Validate tx (checks signatures, balance, and mempool conflicts)
        is_valid, msg = Validator.validate_transaction(tx, utxo_manager, self)
        
        if not is_valid:
            return False, msg

        self.transactions.append(tx)
        
        # Mark inputs as 'pending spent'
        for inp in tx.inputs:
            key = (inp['prev_tx'], inp['index'])
            self.spent_utxos.add(key)
            
        return True, f"Added to mempool. {msg}"

    def remove_transaction(self, tx_id):
        """Removes a transaction from the pool (e.g., after mining)."""
        self.transactions = [t for t in self.transactions if t.tx_id != tx_id]

    def get_top_transactions(self, n, utxo_manager):
        """Returns top N transactions sorted by fee (descending)."""
        def calc_fee(tx):
            total_in = 0.0
            for inp in tx.inputs:
                if utxo_manager.exists(inp['prev_tx'], inp['index']):
                    val, _ = utxo_manager.utxo_set[(inp['prev_tx'], inp['index'])]
                    total_in += val
            
            total_out = sum(o['amount'] for o in tx.outputs)
            return total_in - total_out

        # Sort by fee desc
        sorted_txs = sorted(self.transactions, key=calc_fee, reverse=True)
        return sorted_txs[:n]

    def _evict_lowest_fee(self, utxo_manager):
        """Removes the lowest fee transaction when full."""
        if not self.transactions:
            return

        sorted_txs = self.get_top_transactions(len(self.transactions), utxo_manager)
        worst_tx = sorted_txs[-1] # Last one has lowest fee
        
        # Clean up spent_utxos tracker before removing
        for inp in worst_tx.inputs:
            key = (inp['prev_tx'], inp['index'])
            if key in self.spent_utxos:
                self.spent_utxos.remove(key)
                
        self.remove_transaction(worst_tx.tx_id)

    def clear(self):
        self.transactions = []
        self.spent_utxos = set()