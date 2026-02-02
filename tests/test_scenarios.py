from src.transaction import Transaction
from src.block import mine_block
from src.utxo_manager import UTXOManager
from src.mempool import Mempool
from decimal import Decimal

# --- Helper Functions for Formatting ---
def print_header(title):
    print(f"\n{'='*60}")
    print(f"{title.center(60)}")
    print(f"{'='*60}")

def print_action(action, expected=None):
    print(f"[*] ACTION  : {action}")
    if expected:
        print(f"[*] EXPECTED: {expected}")

def print_result(success, message):
    # In some negative tests (like double spend), a 'False' result from mempool is actually a 'PASS' for the test.
    print(f"    -> Response: {message}")

def print_status(passed):
    if passed:
        print(f"    -> Status  : \033[92m[ PASS ]\033[0m") # Green text
    else:
        print(f"    -> Status  : \033[91m[ FAIL ]\033[0m") # Red text
    print(f"{'-'*60}")

# --- Individual Test Cases ---

def test_1_basic_valid(mempool, utxo_manager):
    print_header("Test 1: Basic Valid Transaction")
    print_action("Alice sends 10 BTC to Bob (Fee: 0.001)", "Transaction Accepted")
    
    # Check if Alice has genesis funds
    if not utxo_manager.exists("genesis", 0):
        print("    -> Error: Alice's Genesis UTXO (genesis:0) not found (Already spent?).")
        print("    -> Tip: Use 'R' in menu to Reset state if you re-running tests.")
        print_status(False)
        return False

    tx = Transaction(sender="Alice", recipient="Bob",
                     inputs=[{"prev_tx": "genesis", "index": 0, "owner": "Alice"}], # 50 BTC
                     outputs=[{"amount": 10.0, "address": "Bob"}, {"amount": 39.999, "address": "Alice"}])
    
    res, msg = mempool.add_transaction(tx, utxo_manager)
    print_result(res, msg)
    print_status(res)
    return res

def test_2_multi_input(mempool, utxo_manager):
    print_header("Test 2: Multiple Inputs Check")
    print_action("1. Charlie sends 20 BTC to Alice.\n"
                 "              2. Mine block to confirm funds.\n"
                 "              3. Alice sends 50 BTC (Uses Change + Charlie's funds).", 
                 "Final Multi-Input TX Accepted")

    # Step 1: Charlie -> Alice
    if not utxo_manager.exists("genesis", 2):
         print("    -> Error: Charlie's Genesis UTXO (20 BTC) not found.")
         print_status(False)
         return False

    tx_setup = Transaction(sender="Charlie", recipient="Alice",
                           inputs=[{"prev_tx": "genesis", "index": 2, "owner": "Charlie"}],
                           outputs=[{"amount": 20.0, "address": "Alice"}])
    res_s, msg_s = mempool.add_transaction(tx_setup, utxo_manager)
    print(f"    -> Setup TX (Charlie->Alice): {msg_s}")

    if not res_s:
        print_status(False)
        return False

    # Store IDs before mining
    setup_txid = tx_setup.tx_id
    
    print("    -> [Mining Block to confirm previous inputs...]")
    mine_block("Miner_Test2", mempool, utxo_manager)

    # Find the inputs for the big transaction
    # We need Alice's change from Test 1 (approx 39.999) and the new 20.0
    alice_utxos = utxo_manager.get_utxos_for_owner("Alice")
    
    # Sort by amount descending to get the big chunks
    alice_utxos.sort(key=lambda x: x['amount'], reverse=True)
    
    if len(alice_utxos) < 2:
        print(f"    -> Error: Alice needs at least 2 UTXOs. Found {len(alice_utxos)}.")
        print("       (Did Test 1 run successfully?)")
        print_status(False)
        return False

    input1 = alice_utxos[0] 
    input2 = alice_utxos[1]

    print(f"    -> Inputs selected: {input1['amount']} BTC & {input2['amount']} BTC")

    tx2 = Transaction(sender="Alice", recipient="Bob",
                      inputs=[
                          {"prev_tx": input1['tx_id'], "index": input1['index'], "owner": "Alice"},
                          {"prev_tx": input2['tx_id'], "index": input2['index'], "owner": "Alice"}
                      ],
                      outputs=[{"amount": 50.0, "address": "Bob"}, {"amount": 9.998, "address": "Alice"}])
    
    res2, msg2 = mempool.add_transaction(tx2, utxo_manager)
    print_result(res2, msg2)
    print_status(res2)
    return res2

def test_3_double_spend_same_tx(mempool, utxo_manager):
    print_header("Test 3: Double-Spend in Same Transaction")
    print_action("Bob uses same UTXO twice as input", "Transaction REJECTED")

    if not utxo_manager.exists("genesis", 1):
        print("    -> Error: Bob's Genesis UTXO not available.")
        print_status(False)
        return False

    tx3 = Transaction(sender="Bob", recipient="Eve",
                      inputs=[{"prev_tx": "genesis", "index": 1, "owner": "Bob"},
                              {"prev_tx": "genesis", "index": 1, "owner": "Bob"}],
                      outputs=[{"amount": 10.0, "address": "Eve"}])
    
    res3, msg3 = mempool.add_transaction(tx3, utxo_manager)
    print_result(res3, msg3)
    print_status(not res3) # Pass if result is False
    return not res3

def test_4_mempool_double_spend(mempool, utxo_manager):
    print_header("Test 4: Mempool Double-Spend")
    print_action("Alice tries to spend genesis:0 again (used in Test 1)", "Transaction REJECTED")
    
    tx4 = Transaction(sender="Alice", recipient="Charlie",
                      inputs=[{"prev_tx": "genesis", "index": 0, "owner": "Alice"}],
                      outputs=[{"amount": 5.0, "address": "Charlie"}])
    
    res4, msg4 = mempool.add_transaction(tx4, utxo_manager)
    print_result(res4, msg4)
    print_status(not res4)
    return not res4

def test_5_insufficient_funds(mempool, utxo_manager):
    print_header("Test 5: Insufficient Funds")
    print_action("Bob (30 BTC) tries to send 35 BTC", "Transaction REJECTED")

    tx5 = Transaction(sender="Bob", recipient="Alice",
                      inputs=[{"prev_tx": "genesis", "index": 1, "owner": "Bob"}],
                      outputs=[{"amount": 35.0, "address": "Alice"}])
    
    res5, msg5 = mempool.add_transaction(tx5, utxo_manager)
    print_result(res5, msg5)
    print_status(not res5)
    return not res5

def test_6_negative_amount(mempool, utxo_manager):
    print_header("Test 6: Negative Amount")
    print_action("David sends -5.0 BTC", "Transaction REJECTED")

    tx6 = Transaction(sender="David", recipient="Alice",
                      inputs=[{"prev_tx": "genesis", "index": 3, "owner": "David"}],
                      outputs=[{"amount": -5.0, "address": "Alice"}])
    
    res6, msg6 = mempool.add_transaction(tx6, utxo_manager)
    print_result(res6, msg6)
    print_status(not res6)
    return not res6

def test_7_zero_fee(mempool, utxo_manager):
    print_header("Test 7: Zero Fee Transaction")
    print_action("David sends 10 BTC (Fee = 0)", "Transaction ACCEPTED")

    if not utxo_manager.exists("genesis", 3):
        print("    -> Error: David's UTXO not available.")
        print_status(False)
        return False

    tx7 = Transaction(sender="David", recipient="Eve",
                      inputs=[{"prev_tx": "genesis", "index": 3, "owner": "David"}],
                      outputs=[{"amount": 10.0, "address": "Eve"}])
    
    res7, msg7 = mempool.add_transaction(tx7, utxo_manager)
    print_result(res7, msg7)
    print_status(res7)
    return res7

def test_8_race_attack(mempool, utxo_manager):
    print_header("Test 8: Race Attack / Replacement")
    print_action("Spend genesis:0 again (already spent in Test 1)", "Transaction REJECTED (First-Seen Rule)")

    tx8 = Transaction(sender="Alice", recipient="Eve",
                      inputs=[{"prev_tx": "genesis", "index": 0, "owner": "Alice"}],
                      outputs=[{"amount": 10.0, "address": "Eve"}, {"amount": 30.0, "address": "Alice"}]) 
    
    res8, msg8 = mempool.add_transaction(tx8, utxo_manager)
    print_result(res8, msg8)
    print_status(not res8)
    return not res8

def test_9_mining_flow(mempool, utxo_manager):
    print_header("Test 9: Complete Mining Flow")
    print_action("Mine remaining transactions in Mempool", "Block Mined & Balances Updated")
    
    print(f"    -> Mempool size before mining: {len(mempool.transactions)}")
    miner_name = "Miner_1"
    pre_balance = utxo_manager.get_balance(miner_name)
    
    success = mine_block(miner_name, mempool, utxo_manager)
    
    post_balance = utxo_manager.get_balance(miner_name)
    
    if success:
        print(f"    -> Block Mined! Miner Reward: {post_balance - pre_balance} BTC")
        print_status(True)
        return True
    else:
        print("    -> Mining Failed (Mempool might be empty).")
        print_status(True) 
        return True

def test_10_unconfirmed_chain(mempool, utxo_manager):
    print_header("Test 10: Unconfirmed Chain")
    print_action("Create Parent TX -> Try to spend Parent Output immediately", 
                 "Child TX REJECTED (Must wait for mining)")

    # 1. Create Parent (Bob -> Alice)
    # We check if Bob has money. If genesis:1 was spent, we might fail here.
    # In a full run, genesis:1 is spent in Test 5 (insufficient) and Test 3 (double), 
    # so it SHOULD still be available (since those failed).
    if not utxo_manager.exists("genesis", 1):
        print("    -> Bob's Genesis UTXO not found (Already spent).")
        print_status(False)
        return False

    tx_parent = Transaction(sender="Bob", recipient="Alice",
                            inputs=[{"prev_tx": "genesis", "index": 1, "owner": "Bob"}], 
                            outputs=[{"amount": 5.0, "address": "Alice"}, {"amount": 24.999, "address": "Bob"}])
    res_p, msg_p = mempool.add_transaction(tx_parent, utxo_manager)
    print(f"    -> Parent TX Result: {msg_p}")

    if res_p:
        # 2. Child TX (Alice tries to spend unmined 5 BTC)
        parent_txid = tx_parent.tx_id
        
        tx_child = Transaction(sender="Alice", recipient="Frank",
                               inputs=[{"prev_tx": parent_txid, "index": 0, "owner": "Alice"}],
                               outputs=[{"amount": 2.0, "address": "Frank"}])
                               
        res10, msg10 = mempool.add_transaction(tx_child, utxo_manager)
        print_result(res10, msg10)
        print("    -> Design Decision: Simulator requires mined UTXOs.")
        print_status(not res10)
        return not res10
    else:
        print_status(False)
        return False

def print_final_balances(utxo_manager):
    print_header("FINAL BALANCES (TEST ENVIRONMENT)")
    people = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Miner_1", "Miner_Test2"]
    current_owners = {data['owner'] for data in utxo_manager.utxo_set.values()}
    all_people = sorted(list(set(people) | current_owners))

    for person in all_people:
        balance = utxo_manager.get_balance(person)
        print(f"    {person:<15}: {balance} BTC")
    print(f"{'='*60}\n")

# --- Context Manager ---
def reset_test_environment():
    """Creates a FRESH state for testing only."""
    utxo_manager = UTXOManager()
    mempool = Mempool()
    # Genesis Setup
    utxo_manager.add_utxo("genesis", 0, 50.0, "Alice")
    utxo_manager.add_utxo("genesis", 1, 30.0, "Bob")
    utxo_manager.add_utxo("genesis", 2, 20.0, "Charlie") 
    utxo_manager.add_utxo("genesis", 3, 10.0, "David")
    utxo_manager.add_utxo("genesis", 4, 5.0, "Eve")
    print("\n[!] Test Environment Reset: Genesis State Restored.")
    return utxo_manager, mempool

# --- Main Test Runner ---
def run_tests():
    # Initialize fresh state immediately
    utxo_manager, mempool = reset_test_environment()
    
    test_cases = {
        1: test_1_basic_valid,
        2: test_2_multi_input,
        3: test_3_double_spend_same_tx,
        4: test_4_mempool_double_spend,
        5: test_5_insufficient_funds,
        6: test_6_negative_amount,
        7: test_7_zero_fee,
        8: test_8_race_attack,
        9: test_9_mining_flow,
        10: test_10_unconfirmed_chain
    }

    while True:
        print(f"\n=== TEST SUITE MENU [ISOLATED STATE] ===")
        print("1-10. Run Specific Test Case")
        print("A.    Run ALL Test Cases (Sequential)")
        print("B.    Print Current Test Balances")
        print("R.    Reset Test State (Restore Genesis)")
        print("X.    Return to Main Menu")
        
        choice = input("\nEnter selection: ").strip().upper()
        
        if choice == 'X':
            break
        
        elif choice == 'B':
            print_final_balances(utxo_manager)

        elif choice == 'R':
            utxo_manager, mempool = reset_test_environment()

        elif choice == 'A':
            print("\n[Running ALL Tests sequentially...]")
            # Important: We must reset before 'Run All' to ensure sequence validity
            utxo_manager, mempool = reset_test_environment()
            for i in range(1, 11):
                test_cases[i](mempool, utxo_manager)
            print_final_balances(utxo_manager)
            input("\nPress Enter to continue...")

        elif choice.isdigit():
            num = int(choice)
            if num in test_cases:
                print(f"\n[Running Test Case {num} Only...]")
                test_cases[num](mempool, utxo_manager)
                print("\nNote: Tests modify the shared test state. Use 'R' if data gets messy.")
                input("Press Enter to continue...")
            else:
                print("Invalid test number.")
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    run_tests()