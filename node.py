import threading
from dag_blockchain import Blockchain

class Node:
    def __init__(self, name, premine_address, block_time=0.001, batch_size=1000):
        self.name = name
        self.blockchain = Blockchain(premine_address, block_time, batch_size)
        self.peers = set()

    def add_peer(self, peer_url):
        self.peers.add(peer_url)

    def start(self):
        # بدء تجميع الكتل في thread منفصل
        t = threading.Thread(target=self.blockchain.run_aggregator)
        t.daemon = True
        t.start()

    def broadcast_block(self, block):
        # يمكن إضافة كود لبث البلوك للأقران (HTTP POST)
        pass
