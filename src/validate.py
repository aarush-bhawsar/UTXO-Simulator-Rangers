from decimal import Decimal

class Validator:
    @staticmethod
    def validate_transaction(transaction, utxo_manager, mempool):
        # Rule 4: Check for negative outputs
        for output in transaction.outputs:
            if Decimal(str(output['amount'])) < 0:
                return False, "Validation Error: Negative output amount detected."

        # Rule 2: Check for duplicate inputs within the same transaction
        input_keys = set()
        for tx_input in transaction.inputs:
            key = (tx_input['prev_tx'], tx_input['index'])
            if key in input_keys:
                return False, f"Validation Error: Duplicate input {key} in the same transaction."
            input_keys.add(key)

        # Initialize as Decimal to avoid floating point errors
        total_input_value = Decimal('0.0')
        
        # Rule 1 & 5: Validate inputs against UTXO Manager and Mempool
        for tx_input in transaction.inputs:
            prev_id = tx_input['prev_tx']
            idx = tx_input['index']
            
            if not utxo_manager.exists(prev_id, idx):
                return False, f"Validation Error: UTXO {prev_id}:{idx} does not exist or is already spent."
            
            if (prev_id, idx) in mempool.spent_utxos:
                return False, f"Validation Error: UTXO {prev_id}:{idx} is already being spent in the mempool."

            utxo_data = utxo_manager.utxo_set[(prev_id, idx)]
            # Convert stored amount to Decimal
            amount = Decimal(str(utxo_data["amount"]))
            total_input_value += amount

        # Rule 3: Ensure sufficient funds - Calculate output sum using Decimals
        total_output_value = sum(Decimal(str(output['amount'])) for output in transaction.outputs)
        
        if total_input_value < total_output_value:
            return False, f"Validation Error: Insufficient funds. Inputs ({total_input_value}) < Outputs ({total_output_value})."

        # Safe Decimal subtraction for exact fee calculation
        fee = total_input_value - total_output_value
        return True, f"Transaction valid! Fee: {fee} BTC"