import sys
import os

# Add the app directory to the path so we can import services
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.services.firebase_service import db, bucket
    
    if db is not None:
        print("✅ Successfully connected to Firestore!")
        # Try a quick read to verify permissions
        collections = db.collections()
        print("✅ Firestore read permissions verified.")
    else:
        print("❌ Firestore (db) is None. Initialization failed.")
        
    if bucket is not None:
        print(f"✅ Successfully connected to Cloud Storage Bucket: {bucket.name}")
    else:
        print("❌ Cloud Storage Bucket is None. Initialization failed.")
        
except Exception as e:
    print(f"❌ Error testing Firebase connection: {e}")
