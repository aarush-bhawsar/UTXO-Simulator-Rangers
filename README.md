# UTXO Simulator - Rangers

## Team Information
**Team Name:** Rangers

**Members:**
* Patil Rajwardhan Umesh (240001051)
* Veer Doria (240041039)
* Samay Mulchandani (240001062)
* Aarush Bhawsar (240001002)

## Project Overview
This project is a simplified Bitcoin Transaction and UTXO Simulator implemented in Python. It simulates the core logic of Bitcoin's transaction lifecycle, including UTXO management, transaction validation, mempool operations, and block mining. The simulator runs locally and focuses on the logical implementation of the UTXO model and double-spending prevention.

## Design Explanation
The simulator is built around the following key components:

1. **UTXO Manager:** Acts as the single source of truth for the simulator. It manages the set of unspent transaction outputs (UTXOs) and tracks ownership and balances.
2. **Mempool:** A waiting area for unconfirmed transactions. It enforces conflict detection to prevent double-spending before transactions are mined.
3. **Transaction Validator:** Enforces Bitcoin's protocol rules, ensuring inputs exist, signatures (simulated) match owners, and input sums equal or exceed output sums.
4. **Miner:** Simulates the mining process by selecting transactions from the mempool, collecting fees, and permanently updating the UTXO set.

## Dependencies and Installation
This project is built using **Python 3.8+**.

* **External Libraries:** None. This project uses only Python's standard libraries.
* **Installation:** No specific installation is required beyond having Python installed on your system.

## Instructions to Run
Follow these steps to execute the simulator:

1. Clone this repository or download the source code.
2. Navigate to the project root directory in your terminal.
3. Run the main program using the following command:

   ```bash
   python src/main.py
