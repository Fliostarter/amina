import threading
import time
import hashlib
import json
from collections import deque

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = time.time()

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp
        }

class DAG:
    def __init__(self):
        self.transactions = deque()  # قائمة الانتظار للمعاملات
        self.lock = threading.Lock()

    def add_transaction(self, tx: Transaction):
        with self.lock:
            self.transactions.append(tx)

    def get_batch(self, max_count=1000):
        batch = []
        with self.lock:
            while self.transactions and len(batch) < max_count:
                batch.append(self.transactions.popleft())
        return batch

class Block:
    def __init__(self, index, previous_hash, transactions):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = [tx.to_dict() for tx in transactions]
        self.timestamp = time.time()
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "previous_hash": self.previous_hash,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self, premine_address, block_time=0.001, batch_size=1000):
        self.dag = DAG()
        self.chain = []
        self.block_time = block_time
        self.batch_size = batch_size
        self.lock = threading.Lock()
        self.create_genesis(premine_address)

    def create_genesis(self, premine_address):
        # البلوك الأولي (Genesis) بدون معاملات عادية لكن يمكن تخصيص premine
        genesis_tx = Transaction("GENESIS", premine_address, 1_000_000_000)  # كمّية premine
        self.dag.add_transaction(genesis_tx)
        batch = self.dag.get_batch(self.batch_size)
        genesis_block = Block(0, "0", batch)
        self.chain.append(genesis_block)

    def add_transaction(self, sender, receiver, amount):
        tx = Transaction(sender, receiver, amount)
        self.dag.add_transaction(tx)

    def aggregate_block(self):
        # يجلب دفعة من المعاملات من DAG ويولد بلوك تجميعي
        batch = self.dag.get_batch(self.batch_size)
        if not batch:
            return None
        with self.lock:
            previous_hash = self.chain[-1].hash
            block = Block(len(self.chain), previous_hash, batch)
            self.chain.append(block)
        return block

    def run_aggregator(self):
        while True:
            block = self.aggregate_block()
            time.sleep(self.block_time)
