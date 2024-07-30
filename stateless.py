from flask import Flask, request, jsonify

# Define Data Structures
class Claim:
    def __init__(self, claim_id, policy_id, amount, status):
        self.claim_id = claim_id
        self.policy_id = policy_id
        self.amount = amount
        self.status = status

class Policyholder:
    def __init__(self, policyholder_id, name):
        self.policyholder_id = policyholder_id
        self.name = name

class Policy:
    def __init__(self, policy_id, policyholder_id, policy_amount):
        self.policy_id = policy_id
        self.policyholder_id = policyholder_id
        self.policy_amount = policy_amount

# Claims Management System Class
class ClaimsManagementSystem:
    def __init__(self):
        self.claims = {}
        self.policies = {}
        self.policyholders = {}
        self.max_policy_amount = 50000  # Set maximum policy amount

    # Create Policyholder
    def create_policyholder(self, policyholder_id, name):
        if policyholder_id in self.policyholders:
            raise ValueError("Policyholder already exists")
        self.policyholders[policyholder_id] = Policyholder(policyholder_id, name)

    # Create Policy
    def create_policy(self, policy_id, policyholder_id, policy_amount):
        if policy_id in self.policies:
            raise ValueError("Policy already exists")
        if policyholder_id not in self.policyholders:
            raise ValueError("Policyholder does not exist")
        if policy_amount > self.max_policy_amount:
            raise ValueError(f"Policy amount cannot exceed {self.max_policy_amount}")
        self.policies[policy_id] = Policy(policy_id, policyholder_id, policy_amount)

    # Create Claim
    def create_claim(self, claim_id, policy_id, amount):
        if claim_id in self.claims:
            raise ValueError("Claim already exists")
        if policy_id not in self.policies:
            raise ValueError("Policy does not exist")
        policy = self.policies[policy_id]
        if amount > policy.policy_amount:
            raise ValueError("Claim amount exceeds policy amount")
        self.claims[claim_id] = Claim(claim_id, policy_id, amount, "Pending")

    # Read Policyholder
    def read_policyholder(self, policyholder_id):
        return vars(self.policyholders.get(policyholder_id, None))

    # Read Policy
    def read_policy(self, policy_id):
        return vars(self.policies.get(policy_id, None))

    # Read Claim
    def read_claim(self, claim_id):
        return vars(self.claims.get(claim_id, None))

    # Read All Policies
    def read_all_policies(self):
        return [vars(policy) for policy in self.policies.values()]

    # Update Claim Status
    def update_claim_status(self, claim_id, status):
        if claim_id not in self.claims:
            raise ValueError("Claim does not exist")
        if status not in ["Pending", "Approved", "Rejected"]:
            raise ValueError("Invalid status")
        self.claims[claim_id].status = status

    # Delete Claim
    def delete_claim(self, claim_id):
        if claim_id not in self.claims:
            raise ValueError("Claim does not exist")
        del self.claims[claim_id]

# Flask Application
app = Flask(__name__)
cms = ClaimsManagementSystem()

@app.route('/policyholders', methods=['POST'])
def create_policyholder():
    data = request.json
    try:
        cms.create_policyholder(data['policyholder_id'], data['name'])
        return jsonify({"message": "Policyholder created successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/policyholders/<policyholder_id>', methods=['GET'])
def read_policyholder(policyholder_id):
    policyholder = cms.read_policyholder(policyholder_id)
    if policyholder:
        return jsonify(policyholder), 200
    return jsonify({"error": "Policyholder not found"}), 404

@app.route('/policies', methods=['POST'])
def create_policy():
    data = request.json
    try:
        cms.create_policy(data['policy_id'], data['policyholder_id'], data['policy_amount'])
        return jsonify({"message": "Policy created successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/policies/<policy_id>', methods=['GET'])
def read_policy(policy_id):
    policy = cms.read_policy(policy_id)
    if policy:
        return jsonify(policy), 200
    return jsonify({"error": "Policy not found"}), 404

@app.route('/policies', methods=['GET'])
def get_all_policies():
    policies = cms.read_all_policies()
    return jsonify(policies), 200

@app.route('/claims', methods=['POST'])
def create_claim():
    data = request.json
    try:
        cms.create_claim(data['claim_id'], data['policy_id'], data['amount'])
        return jsonify({"message": "Claim created successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/claims/<claim_id>', methods=['GET'])
def read_claim(claim_id):
    claim = cms.read_claim(claim_id)
    if claim:
        return jsonify(claim), 200
    return jsonify({"error": "Claim not found"}), 404

@app.route('/claims/<claim_id>/status', methods=['PUT'])
def update_claim_status(claim_id):
    data = request.json
    try:
        cms.update_claim_status(claim_id, data['status'])
        return jsonify({"message": "Claim status updated successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/claims/<claim_id>', methods=['DELETE'])
def delete_claim(claim_id):
    try:
        cms.delete_claim(claim_id)
        return jsonify({"message": "Claim deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)


'''
1. Low-Level Design (LLD)

 a. Understanding

The Claims Management System is designed to manage policies, policyholders, and claims. 
It involves operations such as creating, reading, updating, and deleting records, with specific validations to ensure data integrity. 

Key entities include:
- Policyholder: Represents an individual who holds a policy.
- Policy: Represents an insurance policy linked to a policyholder, with a maximum allowable policy amount.
- Claim: Represents a claim made against a policy, with a status indicating its progress.

 b. Implementation Approach

1. Data Structures:
   - Use Python classes to represent entities: `Policyholder`, `Policy`, and `Claim`.
   - In-memory dictionaries for storing instances of these entities keyed by their unique identifiers.

2. CRUD Operations:
   - Implement CRUD operations for each entity.
   - Utilize Flask to expose these operations as RESTful API endpoints.

3. Validation Rules:
   - Ensure unique identifiers for policyholders, policies, and claims.
   - Limit policy amounts to a maximum value.
   - Restrict claims to not exceed the associated policy's amount.

4. Business Logic:
   - A claim must be associated with an existing policy.
   - Claims status can be updated to "Pending", "Approved", or "Rejected".

 c. Test Cases

1. Policyholder Tests:
   - Create a policyholder and ensure it's stored correctly.
   - Retrieve a policyholder by ID.
   - Handle attempts to create duplicate policyholders.

2. Policy Tests:
   - Create a policy with a valid amount and ensure it's stored correctly.
   - Validate error handling for policies exceeding the maximum amount.
   - Retrieve policies and ensure correct information is returned.

3. Claim Tests:
   - Create a claim for an existing policy.
   - Validate error handling for claims exceeding the policy amount.
   - Update claim status and ensure changes are correctly reflected.

2. LLD Needs to be Created Before Initiating Development

See above

3. Suite of Functions Representing CRUD Operations

The code provided previously contains CRUD functions for policyholders, policies, and claims. 
These functions are encapsulated in the `ClaimsManagementSystem` class and exposed via Flask endpoints.

4. Validation Rules and Business Logic Implementations

Validation and business rules are implemented within the CRUD operations:
- Policy amounts are validated against a maximum threshold.
- Claim amounts are checked against the policy amount.
- Unique constraints are enforced for IDs.

5. Postman Collection

You can create a Postman collection by following these steps:

1. Create a New Collection:
   - Name it `Claims Management System`.

2. Add Requests:
   - POST /policyholders: Add a request to create a policyholder.
   - GET /policyholders/{policyholder_id}: Add a request to retrieve a policyholder by ID.
   - POST /policies: Add a request to create a policy.
   - GET /policies/{policy_id}: Add a request to retrieve a policy by ID.
   - GET /policies: Add a request to list all policies.
   - POST /claims: Add a request to create a claim.
   - GET /claims/{claim_id}: Add a request to retrieve a claim by ID.
   - PUT /claims/{claim_id}/status: Add a request to update a claim status.
   - DELETE /claims/{claim_id}: Add a request to delete a claim.

6. Demonstration of Application Functionalities

To be shown
'''