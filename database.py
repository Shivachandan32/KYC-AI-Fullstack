# database.py
from pymongo import MongoClient
from datetime import datetime
import os

class Database:
    def __init__(self):
        try:
            self.client = MongoClient(os.getenv("MONGODB_URL"))
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client["kyc_ai"]
            self.collection = self.db["verifications"]
            self.connected = True
            print("✅ MongoDB connected successfully")
        except Exception as e:
            print(f"⚠️ MongoDB connection failed: {e}")
            print("⚠️ Running without database — results won't be saved")
            self.connected = False

    def save_verification(self, filename: str, file_type: str, result: dict, processing_time: float) -> str:
        if not self.connected:
            return "no-db"
        try:
            record = {
                "filename": filename,
                "file_type": file_type,
                "status": result["status"],
                "document_type": result["document_type"],
                "confidence": result["confidence"],
                "issues": result["issues"],
                "explanation": result["explanation"],
                "rules_applied": result["rules_applied"],
                "rag_used": result["rag_used"],
                "processing_time_seconds": round(processing_time, 2),
                "timestamp": datetime.utcnow()
            }
            inserted = self.collection.insert_one(record)
            print(f"💾 Saved to MongoDB: {inserted.inserted_id}")
            return str(inserted.inserted_id)
        except Exception as e:
            print(f"⚠️ Failed to save: {e}")
            return "save-failed"

    def get_dashboard_stats(self) -> dict:
        if not self.connected:
            return {
                "total": 0,
                "verified": 0,
                "flagged": 0,
                "avg_processing_time": 0,
                "confidence_breakdown": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
                "recent_verifications": [],
                "db_status": "disconnected"
            }
        try:
            total = self.collection.count_documents({})
            verified = self.collection.count_documents({"status": "VERIFIED"})
            flagged = self.collection.count_documents({"status": "FLAGGED"})

            pipeline = [
                {"$group": {"_id": None, "avg_time": {"$avg": "$processing_time_seconds"}}}
            ]
            avg_result = list(self.collection.aggregate(pipeline))
            avg_time = round(avg_result[0]["avg_time"], 2) if avg_result else 0

            high_conf = self.collection.count_documents({"confidence": "HIGH"})
            medium_conf = self.collection.count_documents({"confidence": "MEDIUM"})
            low_conf = self.collection.count_documents({"confidence": "LOW"})

            recent = list(self.collection.find(
                {},
                {"_id": 0, "filename": 1, "status": 1, "document_type": 1,
                 "confidence": 1, "timestamp": 1, "processing_time_seconds": 1}
            ).sort("timestamp", -1).limit(10))

            for r in recent:
                r["timestamp"] = r["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

            return {
                "total": total,
                "verified": verified,
                "flagged": flagged,
                "avg_processing_time": avg_time,
                "confidence_breakdown": {
                    "HIGH": high_conf,
                    "MEDIUM": medium_conf,
                    "LOW": low_conf
                },
                "recent_verifications": recent,
                "db_status": "connected"
            }
        except Exception as e:
            return {"error": str(e)}