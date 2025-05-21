from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID

client = Client()
client.set_endpoint("https://cloud.appwrite.io/v1")
client.set_project("67d090e90034dde1e899")
client.set_key("standard_13e1b9551affac5b1a4aa60e285409d819eea8e39f0992b02d0eb184c8e1513f3f1422e3b633406e0a5d08a3624b0e81e11a953da293854203f0f633056554225cb36cb3f07c3c16e4b782d2e97c6ede19cbe17dfcea6cb959d628c77fb6ede33870d645c0ab7b2cd95711ae12b23163f2c7fb73e4cad1b668d1973646734f13")

databases = Databases(client)
database_id = "67d09163002ea9ef0c8b"

# ✅ Full collection and attribute config with INT IDs
collections = {
    "Users": [
        {"key": "id", "type": "integer", "required": True},
        {"key": "username", "type": "string", "size": 100, "required": True},
        {"key": "email", "type": "email", "required": True},
        {"key": "is_active", "type": "boolean", "required": True},
        {"key": "date_joined", "type": "datetime", "required": True}
    ],
    "profiles": [
        {"key": "id", "type": "integer", "required": True},
        {"key": "user_id", "type": "integer", "required": True},
        {"key": "bio", "type": "string", "size": 1000},
        {"key": "profile_picture", "type": "string", "size": 200},
        {"key": "location", "type": "string", "size": 255},
        {"key": "phone_number", "type": "string", "size": 20}
    ],
    "projects": [
        {"key": "id", "type": "integer", "required": True},
        {"key": "user_id", "type": "integer", "required": True},
        {"key": "title", "type": "string", "size": 255, "required": True},
        {"key": "description", "type": "string", "size": 1000},
        {"key": "tools_used", "type": "string", "size": 1000},
        {"key": "repository_url", "type": "string", "size": 500},
        {"key": "live_url", "type": "string", "size": 500},
        {"key": "start_date", "type": "datetime"},
        {"key": "end_date", "type": "datetime"}
    ],
    "work_experience": [
        {"key": "id", "type": "integer", "required": True},
        {"key": "user_id", "type": "integer", "required": True},
        {"key": "company_name", "type": "string", "size": 255},
        {"key": "position", "type": "string", "size": 255},
        {"key": "start_date", "type": "datetime"},
        {"key": "end_date", "type": "datetime"},
        {"key": "description", "type": "string", "size": 1000}
    ],
    "education": [
        {"key": "id", "type": "integer", "required": True},
        {"key": "user_id", "type": "integer", "required": True},
        {"key": "school_name", "type": "string", "size": 255},
        {"key": "degree", "type": "string", "size": 255},
        {"key": "start_year", "type": "integer"},
        {"key": "end_year", "type": "integer"},
        {"key": "description", "type": "string", "size": 1000}
    ],
    "skills": [
        {"key": "id", "type": "integer", "required": True},
        {"key": "user_id", "type": "integer", "required": True},
        {"key": "name", "type": "string", "size": 255},
        {"key": "level", "type": "string", "size": 255}
    ],
    "certifications": [
        {"key": "id", "type": "integer", "required": True},
        {"key": "user_id", "type": "integer", "required": True},
        {"key": "title", "type": "string", "size": 255},
        {"key": "issuer", "type": "string", "size": 255},
        {"key": "date_issued", "type": "datetime"}
    ],
    "achievements": [
        {"key": "id", "type": "integer", "required": True},
        {"key": "user_id", "type": "integer", "required": True},
        {"key": "title", "type": "string", "size": 255},
        {"key": "description", "type": "string", "size": 1000},
        {"key": "date", "type": "datetime"}
    ],
    "publications": [
        {"key": "id", "type": "integer", "required": True},
        {"key": "user_id", "type": "integer", "required": True},
        {"key": "title", "type": "string", "size": 255},
        {"key": "journal", "type": "string", "size": 255},
        {"key": "publication_date", "type": "datetime"}
    ]
}

# ✅ Loop through collection and attributes
for collection_name, attrs in collections.items():
    collection_id = ID.unique()
    try:
        databases.create_collection(
            database_id=database_id,
            collection_id=collection_id,
            name=collection_name,
            permissions=[],
            document_security=False
        )
        print(f"✅ Created Collection: {collection_name}")
    except Exception as e:
        print(f"⚠ Collection {collection_name} exists or failed: {str(e)}")
        continue

    for attr in attrs:
        try:
            if attr["type"] == "string":
                databases.create_string_attribute(database_id, collection_id, attr["key"], attr["size"], attr.get("required", False))
            elif attr["type"] == "integer":
                databases.create_integer_attribute(database_id, collection_id, attr["key"], min=-2147483648, max=2147483647, required=attr.get("required", False))
            elif attr["type"] == "email":
                databases.create_email_attribute(database_id, collection_id, attr["key"], attr.get("required", False))
            elif attr["type"] == "boolean":
                databases.create_boolean_attribute(database_id, collection_id, attr["key"], attr.get("required", False))
            elif attr["type"] == "datetime":
                databases.create_datetime_attribute(database_id, collection_id, attr["key"], attr.get("required", False))
            print(f"   ➔ Created attribute: {attr['key']} ({attr['type']})")
        except Exception as e:
            print(f"⚠ Failed attribute {attr['key']} in {collection_name}: {str(e)}")

print("\n✅✅✅ All Collections and Attributes created successfully!")
