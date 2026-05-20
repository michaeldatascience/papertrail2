from src.schemas import AADHAAR_CARD_SCHEMA
from src.schemas.base import DocumentType, SchemaRegistry


class TestAadhaarSchema:
    def test_document_type_exists(self):
        assert DocumentType.AADHAAR_CARD == "aadhaar_card"

    def test_schema_identity(self):
        assert AADHAAR_CARD_SCHEMA.name == "aadhaar_card"
        assert AADHAAR_CARD_SCHEMA.display_name == "Aadhaar Card"
        assert AADHAAR_CARD_SCHEMA.document_type == DocumentType.AADHAAR_CARD

    def test_required_fields(self):
        required = {f.name for f in AADHAAR_CARD_SCHEMA.get_required_fields()}
        assert "aadhaar_number" in required
        assert "full_name" in required

    def test_aadhaar_number_pattern(self):
        field = AADHAAR_CARD_SCHEMA.get_field("aadhaar_number")
        assert field is not None
        assert field.pattern == r"^\d{4}\s?\d{4}\s?\d{4}$"

    def test_registry_contains_schema(self):
        schema = SchemaRegistry().get("aadhaar_card")
        assert schema is not None
        assert schema.name == "aadhaar_card"

    def test_validate_valid_minimal_result(self):
        result = {
            "aadhaar_number": "1234 5678 9012",
            "full_name": "Ravi Kumar",
            "year_of_birth": "1990",
        }
        errors, warnings = AADHAAR_CARD_SCHEMA.validate_result(result)
        assert errors == []

    def test_validate_missing_required(self):
        errors, warnings = AADHAAR_CARD_SCHEMA.validate_result({"full_name": "Ravi Kumar"})
        assert any("Aadhaar Number" in e for e in errors)
