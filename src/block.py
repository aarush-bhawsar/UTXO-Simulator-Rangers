import time
from transaction import Transaction

def mine_block(miner_address, mempool, utxo_manager, num_txs=3):
    """
    Simulates mining: updates UTXO set and creates a coinbase reward.
    """
    # Prioritize highest fee transactions
    selected_txs = mempool.get_top_transactions(num_txs, utxo_manager)
    
    if not selected_txs:
        print("Mempool empty, nothing to mine.")
        return False

    total_fees = 0.0
    print(f"Mining block with {len(selected_txs)} transactions...")

    for tx in selected_txs:
        input_sum = 0.0
        output_sum = 0.0
        
        # 1. Consume Inputs (Remove from UTXO set)
        for inp in tx.inputs:
            prev_id, prev_idx = inp['prev_tx'], inp['index']
            
            if utxo_manager.exists(prev_id, prev_idx):
                amt, _ = utxo_manager.utxo_set[(prev_id, prev_idx)]
                input_sum += amt
                utxo_manager.remove_utxo(prev_id, prev_idx)
            
            # Clean up mempool tracker
            if (prev_id, prev_idx) in mempool.spent_utxos:
                mempool.spent_utxos.remove((prev_id, prev_idx))

        # 2. Create Outputs (Add to UTXO set)
        for i, out in enumerate(tx.outputs):
            utxo_manager.add_utxo(tx.tx_id, i, out['amount'], out['address'])
            output_sum += out['amount']

        # Fee = Inputs - Outputs
        total_fees += (input_sum - output_sum)

    # 3. Create Coinbase TX (Miner Reward)
    coinbase_tx = Transaction(
        sender="SYSTEM",
        recipient=miner_address,
        inputs=[],
        outputs=[{"amount": total_fees, "address": miner_address}]
    )
    
    # Add coinbase output to UTXO set (index 0)
    utxo_manager.add_utxo(coinbase_tx.tx_id, 0, total_fees, miner_address)

    # 4. Remove mined txs from mempool
    for tx in selected_txs:
        mempool.remove_transaction(tx.tx_id)

    print(f"Block mined! Miner {miner_address} reward: {total_fees:.4f} BTC")
    return True