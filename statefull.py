from flask import Flask, request, jsonify
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['claims_management']
policyholders_collection = db['policyholders']
policies_collection = db['policies']
claims_collection = db['claims']

# Flask Application
app = Flask(__name__)

# Create Policyholder
@app.route('/policyholders', methods=['POST'])
def create_policyholder():
    data = request.json
    if policyholders_collection.find_one({"policyholder_id": data['policyholder_id']}):
        return jsonify({"error": "Policyholder already exists"}), 400
    policyholders_collection.insert_one({
        "policyholder_id": data['policyholder_id'],
        "name": data['name']
    })
    return jsonify({"message": "Policyholder created successfully"}), 201

# Read Policyholder
@app.route('/policyholders/<policyholder_id>', methods=['GET'])
def read_policyholder(policyholder_id):
    policyholder = policyholders_collection.find_one({"policyholder_id": policyholder_id})
    if policyholder:
        return jsonify({
            "policyholder_id": policyholder['policyholder_id'],
            "name": policyholder['name']
        }), 200
    return jsonify({"error": "Policyholder not found"}), 404

# Read All Policyholders
@app.route('/policyholders', methods=['GET'])
def get_all_policyholders():
    policyholders = policyholders_collection.find()
    return jsonify([{
        "policyholder_id": policyholder['policyholder_id'],
        "name": policyholder['name']
    } for policyholder in policyholders]), 200

# Create Policy
@app.route('/policies', methods=['POST'])
def create_policy():
    data = request.json
    if policies_collection.find_one({"policy_id": data['policy_id']}):
        return jsonify({"error": "Policy already exists"}), 400
    if not policyholders_collection.find_one({"policyholder_id": data['policyholder_id']}):
        return jsonify({"error": "Policyholder does not exist"}), 400
    if data['policy_amount'] > 50000:
        return jsonify({"error": "Policy amount cannot exceed 50000"}), 400
    policies_collection.insert_one({
        "policy_id": data['policy_id'],
        "policyholder_id": data['policyholder_id'],
        "policy_amount": data['policy_amount']
    })
    return jsonify({"message": "Policy created successfully"}), 201

# Read Policy
@app.route('/policies/<policy_id>', methods=['GET'])
def read_policy(policy_id):
    policy = policies_collection.find_one({"policy_id": policy_id})
    if policy:
        return jsonify({
            "policy_id": policy['policy_id'],
            "policyholder_id": policy['policyholder_id'],
            "policy_amount": policy['policy_amount']
        }), 200
    return jsonify({"error": "Policy not found"}), 404

# Read All Policies
@app.route('/policies', methods=['GET'])
def get_all_policies():
    policies = policies_collection.find()
    return jsonify([{
        "policy_id": policy['policy_id'],
        "policyholder_id": policy['policyholder_id'],
        "policy_amount": policy['policy_amount']
    } for policy in policies]), 200

# Create Claim
@app.route('/claims', methods=['POST'])
def create_claim():
    data = request.json
    if claims_collection.find_one({"claim_id": data['claim_id']}):
        return jsonify({"error": "Claim already exists"}), 400
    policy = policies_collection.find_one({"policy_id": data['policy_id']})
    if not policy:
        return jsonify({"error": "Policy does not exist"}), 400
    if data['amount'] > policy['policy_amount']:
        return jsonify({"error": "Claim amount exceeds policy amount"}), 400
    claims_collection.insert_one({
        "claim_id": data['claim_id'],
        "policy_id": data['policy_id'],
        "amount": data['amount'],
        "status": "Pending"
    })
    return jsonify({"message": "Claim created successfully"}), 201

# Read Claim
@app.route('/claims/<claim_id>', methods=['GET'])
def read_claim(claim_id):
    claim = claims_collection.find_one({"claim_id": claim_id})
    if claim:
        return jsonify({
            "claim_id": claim['claim_id'],
            "policy_id": claim['policy_id'],
            "amount": claim['amount'],
            "status": claim['status']
        }), 200
    return jsonify({"error": "Claim not found"}), 404

# Read All Claims
@app.route('/claims', methods=['GET'])
def get_all_claims():
    claims = claims_collection.find()
    return jsonify([{
        "claim_id": claim['claim_id'],
        "policy_id": claim['policy_id'],
        "amount": claim['amount'],
        "status": claim['status']
    } for claim in claims]), 200

# Update Claim Status
@app.route('/claims/<claim_id>/status', methods=['PUT'])
def update_claim_status(claim_id):
    data = request.json
    if claims_collection.find_one({"claim_id": claim_id}):
        if data['status'] not in ["Pending", "Approved", "Rejected"]:
            return jsonify({"error": "Invalid status"}), 400
        claims_collection.update_one({"claim_id": claim_id}, {"$set": {"status": data['status']}})
        return jsonify({"message": "Claim status updated successfully"}), 200
    return jsonify({"error": "Claim does not exist"}), 404

# Delete Claim
@app.route('/claims/<claim_id>', methods=['DELETE'])
def delete_claim(claim_id):
    if claims_collection.find_one({"claim_id": claim_id}):
        claims_collection.delete_one({"claim_id": claim_id})
        return jsonify({"message": "Claim deleted successfully"}), 200
    return jsonify({"error": "Claim does not exist"}), 404

if __name__ == '__main__':
    app.run(debug=True)

'''
1. Documentation Detailing the Choice of the Database System and Reasoning
Choice of Database: MongoDB

Reasoning:

a) Flexibility: MongoDB is a NoSQL database that uses a document-oriented data model. 
This provides flexibility in handling semi-structured data, which is ideal for our use case where policy and claim data may evolve over time.
b) Scalability: MongoDB is designed for horizontal scalability. 
As the amount of data grows, MongoDB can be distributed across multiple servers, making it suitable for applications with increasing data loads.
c) Ease of Use: MongoDB is developer-friendly with JSON-like documents, which makes it easy to understand and use. 
The MongoDB Compass GUI further simplifies database management.
Community and Support: MongoDB has a large community and extensive documentation, which makes troubleshooting and learning about new features easier.
4) Schema-less Nature: MongoDB allows for a schema-less structure, enabling rapid iteration and changes to data models without requiring extensive migrations.

2. Designed Database Schema and Migration Scripts

For this Claims Management System, we have three primary collections: policyholders, policies, and claims.
Migration Scripts: For MongoDB, migration scripts are often not as formalized as in relational databases, given the schema-less nature. 

4. Evidence of Proper Error Handling and Data Validation

Duplicate Check: Before creating a policyholder, policy, or claim, the application checks if the entity already exists and returns an error if it does.
Policyholder Existence: When creating a policy, it checks if the associated policyholder exists.
Claim Amount Validation: When creating a claim, it checks if the claim amount exceeds the policy amount and returns an error if it does.
Policy Amount Validation: When creating a policy, it ensures that the policy amount does not exceed 50,000.
Invalid Status Check: When updating a claim's status, it validates that the status is either "Pending", "Approved", or "Rejected".
'''

#mongod --dbpath ~/data/db