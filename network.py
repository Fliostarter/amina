from flask import Flask, request, jsonify, render_template
from node import Node
from dag_blockchain import Transaction
import threading
import requests
import config

app = Flask(__name__)
node = Node("Node1", config.PREMINE_ADDRESS, config.BLOCK_TIME, config.BATCH_SIZE)
node.start()

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    data = request.get_json()
    sender = data.get("sender")
    receiver = data.get("receiver")
    amount = data.get("amount")
    node.blockchain.add_transaction(sender, receiver, amount)
    return jsonify({"message": "Transaction added"}), 201

@app.route('/mine', methods=['GET'])
def mine():
    # مجرد تشغيل التجميع، البلوك يتم إنشاؤه تلقائيًا
    return jsonify({"message": "Aggregator running"}), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    chain_data = []
    for block in node.blockchain.chain:
        chain_data.append({
            "index": block.index,
            "previous_hash": block.previous_hash,
            "transactions": block.transactions,
            "timestamp": block.timestamp,
            "hash": block.hash
        })
    return jsonify({"length": len(chain_data), "chain": chain_data})

@app.route('/dashboard')
def dashboard():
    # حساب تقريب لـ TPS: عدد المعاملات في آخر كتلة ÷ وقت البلوك
    if len(node.blockchain.chain) < 2:
        tps = 0
    else:
        last = node.blockchain.chain[-1]
        prev = node.blockchain.chain[-2]
        tx_count = len(last.transactions)
        elapsed = last.timestamp - prev.timestamp
        tps = tx_count / elapsed if elapsed > 0 else tx_count
    return render_template('dashboard.html',
                           num_blocks=len(node.blockchain.chain),
                           last_tx_count=len(node.blockchain.chain[-1].transactions),
                           tps=round(tps, 2))

@app.route('/peers/add', methods=['POST'])
def add_peer():
    data = request.get_json()
    address = data.get("address")
    node.add_peer(address)
    return jsonify({"message": "Peer added"}), 201

if __name__ == "__main__":
    app.run(port=5000)
