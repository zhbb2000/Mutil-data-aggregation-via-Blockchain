# 📦 Mutil-data-aggregation-via-Blockchain

A **privacy-preserving secure multi-party computation framework** for verifiable and efficient multidimensional data aggregation over blockchain.

This project provides an end-to-end protocol and evaluation tools for **privacy-preserving data aggregation** using **homomorphic encryption**, **Pedersen commitment**, and **batch ECDSA verification**, with **blockchain-based verifiability** and **fog computing optimization**.

---

## 📁 Project Structure

| File/Folder         | Description                                                                                 |
|---------------------|---------------------------------------------------------------------------------------------|
| `ECDSA_pedersen.sol` | Solidity smart contract for **batch ECDSA verification** and **Pedersen commitment checking**. |
| `fuc_test.py`        | Simulates a **complete aggregation protocol flow**, including encryption, signature, and verification. |
| `gas_cost.py`        | Tests the **gas consumption** of on-chain activities using the deployed smart contract.    |
| `time_cost_DP.py`    | Simulates the **off-chain computation cost** of the **Data Provider (DP)**.               |
| `time_cos_FN.py`     | Simulates the **off-chain computation cost** of the **Fog Node (FN)**.                    |
| `utils/`             | Utility scripts and helper functions used throughout the project.                          |
| `README.md`          | This file, providing an overview and usage instructions.                                   |

---

## ⚙️ Blockchain Simulation Environment

- This project uses **Ganache** to simulate an Ethereum-compatible blockchain environment for contract deployment and testing.

---

## 🧪 Features

- 🔒 **Privacy-preserving data aggregation** using Paillier homomorphic encryption and Pedersen commitments  
- ✅ **Verifiable result correctness** through on-chain smart contract validation  
- ⚡ **Low-latency fog computing architecture** for local aggregation  
- ⛽ **Gas cost profiling** for evaluating blockchain resource consumption  
- ⏱️ **Off-chain performance evaluation** for both data providers and fog nodes

---

# Run a full test of the aggregation protocol
python fuc_test.py

# Test DP-side computation time
python time_cost_DP.py

# Test FN-side computation time
python time_cos_FN.py

# Test on-chain gas usage
python gas_cost.py
