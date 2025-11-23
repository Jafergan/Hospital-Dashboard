from pymongo import MongoClient
  # Correct specific error for connection issues

client = MongoClient("mongodb+srv://Projectdb:Project123@patient.bcjav.mongodb.net/patientsDB")

db = client['patientsDB']

patients = db['patients']

try:
    # Check MongoDB connection
    client.server_info()  # This will raise an exception if MongoDB is not reachable
    print("MongoDB connection verified.")
except Exception:
    print(f"Error verifying connection to MongoDB")
