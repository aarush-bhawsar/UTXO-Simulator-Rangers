import sys
from src.utxo_manager import UTXOManager
from src.mempool import Mempool
from src.transaction import Transaction
from src.block import mine_block
from tests.test_scenarios import run_tests
from decimal import Decimal, getcontext
getcontext().prec = 28

def parse_amount(input_str):
    try:
        clean = input_str.upper().replace("BTC", "").strip()
        return Decimal(clean) 
    except:
        return None

def main():
    utxo_manager = UTXOManager()
    mempool = Mempool()

    # Initial Genesis State setup (Required for Assignment)
    utxo_manager.add_utxo("genesis", 0, 50.0, "Alice")
    utxo_manager.add_utxo("genesis", 1, 30.0, "Bob")
    utxo_manager.add_utxo("genesis", 2, 20.0, "Charlie")
    utxo_manager.add_utxo("genesis", 3, 10.0, "David")
    utxo_manager.add_utxo("genesis", 4, 5.0, "Eve")

    print("\n=== Bitcoin Transaction Simulator ===")
    print(f"Genesis UTXOs created for Alice, Bob, Charlie, David, and Eve.")

    while True:
        print("\n--- Main Menu ---")
        print("1. Create new transaction")
        print("2. View UTXO set (Unspent outputs)")
        print("3. View Mempool (Pending transactions)")
        print("4. Mine block")
        print("5. Run test scenarios")
        print("6. Exit")
        
        choice = input("\nSelect an option (1-6): ")

        if choice == '1':
            sender = input("Enter sender name: ")
            balance = utxo_manager.get_balance(sender)
            
            if balance <= 0:
                print(f"Error: {sender} has no available BTC.")
                continue
                
            print(f"Available balance: {balance} BTC")
            recipient = input("Enter recipient name: ")
            
            amount_input = input("Enter amount (e.g., 10.0 BTC): ")
            amount = parse_amount(amount_input)
            
            if amount is None or amount <= 0:
                print("Error: Invalid amount entered.")
                continue

            sender_utxos = utxo_manager.get_utxos_for_owner(sender)
            selected_utxo = sender_utxos[0]
            
            # --- START OF UPDATED FEE LOGIC ---
            utxo_amount = Decimal(str(selected_utxo['amount']))
            
            # Check how much is left after the transfer amount
            remainder = utxo_amount - amount
            
            # If remainder is zero or negative, we can't pay ANY fee
            if remainder <= 0:
                print(f"Error: Selected UTXO ({utxo_amount} BTC) is insufficient to pay amount + non-zero fee.")
                continue

            target_fee = Decimal('0.001')

            # If we have enough for the standard fee
            if remainder >= target_fee:
                change = remainder - target_fee
            # If we have less than 0.001 but more than 0, take all remainder as fee
            else:
                print(f"Warning: Insufficient funds for full 0.001 fee. Using available remainder ({remainder} BTC) as fee.")
                change = Decimal('0.0')
            # --- END OF UPDATED FEE LOGIC ---

            tx = Transaction(
                sender=sender,
                recipient=recipient,
                inputs=[{
                    "prev_tx": selected_utxo['tx_id'], 
                    "index": selected_utxo['index'], 
                    "owner": sender
                }],
                outputs=[
                    {"amount": amount, "address": recipient},
                    {"amount": change, "address": sender}
                ]
            )
            
            success, msg = mempool.add_transaction(tx, utxo_manager)
            print(msg)

        elif choice == '2':
            print("\n--- Current UTXO Set ---")
            if not utxo_manager.utxo_set:
                print("No UTXOs exist.")
            else:
                for (tx_id, idx), data in utxo_manager.utxo_set.items():
                    print(f"[{tx_id}:{idx}] Owner: {data['owner']} | Amount: {data['amount']} BTC")

        elif choice == '3':
            print("\n--- Current Mempool ---")
            if not mempool.transactions:
                print("Mempool is empty.")
            else:
                for tx in mempool.transactions:
                    print(f"ID: {tx.tx_id} | {tx.sender} -> {tx.recipient} | Amount: {tx.outputs[0]['amount']} BTC")

        elif choice == '4':
            miner = input("Enter miner name for reward: ")
            success = mine_block(miner, mempool, utxo_manager)
            if not success:
                print("Mining failed (likely empty mempool).")

        elif choice == '5':
            print("\n--- Test Suite ---")
            print("Enter Test Case Number (1-10) to run a specific test.")
            print("Enter -1 to run ALL tests.")
            t_choice = input("Choice: ")
            try:
                run_tests(utxo_manager, mempool, int(t_choice))
            except ValueError:
                print("Invalid input. Please enter a number.")

        elif choice == '6':
            print("Thankyou!")
            sys.exit()
        
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    main()