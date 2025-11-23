from flask import Flask, render_template, request, jsonify
from db_config import patients  # MongoDB collection
import uuid  # For generating unique patient IDs

# Initialize Flask app
app = Flask(__name__)

# -------------------------------
# Home Route (UI for Registration)
# -------------------------------
@app.route('/')
def home():
    return render_template('index.html')  # HTML form

# -------------------------------
# Register a New Patient
# -------------------------------
@app.route('/register', methods=['POST'])
def register_patient():
    try:
        # Collect form data and generate a unique patient ID
        data = {
            "patient_id": str(uuid.uuid4()),  # Unique ID
            "name": request.form.get('name'),
            "aadhaar": request.form.get('aadhaar'),
            "age": request.form.get('age'),
            "gender": request.form.get('gender'),
            "status": request.form.get('status'),  # inpatient or outpatient
            "ward": request.form.get('ward')       # Ward name
        }

        # Insert patient data into MongoDB
        patients.insert_one(data)
        return jsonify({"message": f"Patient Registered! Unique ID: {data['patient_id']}"}), 201
    except Exception as err:
        return jsonify({"error": "Failed to connect to MongoDB Atlas", "details": str(err)}), 500

# -------------------------------
# Get All Patients
# -------------------------------
@app.route('/patients', methods=['GET'])
def get_patients():
    try:
        data = list(patients.find({}, {"_id": 0}))  # Exclude MongoDB ObjectId
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": "Failed to connect to MongoDB Atlas", "details": str(e)}), 500

# -------------------------------
# Get Specific Patient by ID
# -------------------------------
@app.route('/patients/<string:patient_id>', methods=['GET'])
def get_patient(patient_id):
    try:
        patient = patients.find_one({"patient_id": patient_id}, {"_id": 0})
        if patient:
            return jsonify(patient), 200
        return jsonify({"error": "Patient not found"}), 404
    except Exception as e:
        return jsonify({"error": "Failed to connect to MongoDB Atlas", "details": str(e)}), 500

# -------------------------------
# Update Patient Details
# -------------------------------
@app.route('/patients/<string:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    try:
        data = request.get_json()
        result = patients.update_one({"patient_id": patient_id}, {"$set": data})
        if result.matched_count > 0:
            return jsonify({"message": "Patient record updated successfully"}), 200
        return jsonify({"error": "Patient not found"}), 404
    except Exception as e:
        return jsonify({"error": "Failed to connect to MongoDB Atlas", "details": str(e)}), 500

# -------------------------------
# Delete Patient
# -------------------------------
@app.route('/patients/<string:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    try:
        result = patients.delete_one({"patient_id": patient_id})
        if result.deleted_count > 0:
            return jsonify({"message": "Patient record deleted successfully"}), 200
        return jsonify({"error": "Patient not found"}), 404
    except Exception as e:
        return jsonify({"error": "Failed to connect to MongoDB Atlas", "details": str(e)}), 500

# -------------------------------
# Dashboard Route (In/Out/Ward Stats)
# -------------------------------
@app.route('/dashboard')
def dashboard():
    try:
        data = list(patients.find({}, {"_id": 0}))
        total = len(data)
        inpatients = len([p for p in data if p.get("status") == "inpatient"])
        outpatients = len([p for p in data if p.get("status") == "outpatient"])

        ward_counts = {}
        for p in data:
            ward = p.get("ward", "Unassigned")
            ward_counts[ward] = ward_counts.get(ward, 0) + 1

        return render_template("dashboard.html",
                               total=total,
                               inpatients=inpatients,
                               outpatients=outpatients,
                               wards=ward_counts)
    except Exception as e:
        return f"Error loading dashboard: {e}"


# -------------------------------
# Run Flask app
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
