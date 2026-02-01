import time
import random

def generate_tx_id(sender, recipient):
    """Generates a unique transaction ID including sender and recipient names."""
    timestamp = int(time.time())
    rand_salt = random.randint(1000, 9999)
    return f"tx_{sender}_to_{recipient}_{timestamp}_{rand_salt}"

class Transaction:
    def __init__(self, sender, recipient, inputs, outputs):
        """
        sender: str (e.g., 'Alice')
        recipient: str (e.g., 'Bob')
        inputs: list of dicts {'prev_tx': str, 'index': int, 'owner': str}
        outputs: list of dicts {'amount': float, 'address': str}
        """

        self.tx_id = generate_tx_id(sender, recipient)
        self.inputs = inputs
        self.outputs = outputs

    def to_dict(self):
        return {
            "tx_id": self.tx_id,
            "inputs": self.inputs,
            "outputs": self.outputs
        }