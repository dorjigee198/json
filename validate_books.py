import json
import jsonschema
from jsonschema import validate

# Load JSON
with open("books.json", "r", encoding="utf-8") as f:
    books_data = json.load(f)

# Load Schema
with open("books.schema.json", "r", encoding="utf-8") as f:
    books_schema = json.load(f)

# Validate
try:
    validate(instance=books_data, schema=books_schema)
    print("✅ books.json is valid according to books.schema.json")
except jsonschema.exceptions.ValidationError as e:
    print("❌ Validation error:", e.message)
