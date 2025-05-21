# utils/appwrite_sync.py
from appwrite.id import ID
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage
from django.conf import settings

client = Client()
client.set_endpoint("https://cloud.appwrite.io/v1")
client.set_project("67d090e90034dde1e899")
client.set_key("standard_13e1b9551affac5b1a4aa60e285409d819eea8e39f0992b02d0eb184c8e1513f3f1422e3b633406e0a5d08a3624b0e81e11a953da293854203f0f633056554225cb36cb3f07c3c16e4b782d2e97c6ede19cbe17dfcea6cb959d628c77fb6ede33870d645c0ab7b2cd95711ae12b23163f2c7fb73e4cad1b668d1973646734f13")

databases = Databases(client)
storage = Storage(client)

DATABASE_ID = "67d09163002ea9ef0c8b"


def sync_to_appwrite(collection_id, data, document_id=None):
    try:
        if document_id:
            return databases.update_document(
                database_id=DATABASE_ID,
                collection_id=collection_id,
                document_id=document_id,
                data=data
            )
        else:
            return databases.create_document(
                database_id=DATABASE_ID,
                collection_id=collection_id,
                document_id=ID.unique(),
                data=data
            )
    except Exception as e:
        print(f"[Appwrite Sync Error] {collection_id}: {str(e)}")
        return None


def upload_file_to_appwrite(file, bucket_id="67d1babc00201ad80d75"):
    try:
        result = storage.create_file(
            bucket_id=bucket_id,
            file_id=ID.unique(),
            file=file
        )
        return result["$id"]
    except Exception as e:
        print(f"[Appwrite Upload Error]: {e}")
        return None


def get_public_file_url(file_id, bucket_id="67d1babc00201ad80d75"):
    try:
        return storage.get_file_view(bucket_id, file_id)
    except Exception:
        return None
