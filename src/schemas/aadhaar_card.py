"""
Aadhaar card schema for document extraction.

Defines a schema for extracting key identity and address fields from
Indian Aadhaar cards / Aadhaar letters issued by UIDAI.
"""

from src.schemas.base import DocumentSchema, DocumentType, SchemaRegistry
from src.schemas.field_types import FieldDefinition, FieldType


IDENTITY_FIELDS = [
    FieldDefinition(
        name="aadhaar_number",
        display_name="Aadhaar Number",
        field_type=FieldType.MEMBER_ID,
        description="12-digit Aadhaar number printed on the card or letter",
        required=True,
        location_hint="Front side - prominent numeric identifier, often grouped as 4-4-4 digits",
        pattern=r"^\d{4}\s?\d{4}\s?\d{4}$",
        examples=["1234 5678 9012", "123456789012"],
    ),
    FieldDefinition(
        name="virtual_id",
        display_name="Virtual ID",
        field_type=FieldType.MEMBER_ID,
        description="16-digit Aadhaar Virtual ID if present",
        required=False,
        location_hint="May appear on newer Aadhaar print formats or supporting letter",
        pattern=r"^\d{4}\s?\d{4}\s?\d{4}\s?\d{4}$",
        examples=["1234 5678 9012 3456", "1234567890123456"],
    ),
]


PERSON_FIELDS = [
    FieldDefinition(
        name="full_name",
        display_name="Full Name",
        field_type=FieldType.NAME,
        description="Name of the Aadhaar holder",
        required=True,
        location_hint="Front side - below the Aadhaar heading / above DOB or YOB",
        examples=["Ravi Kumar", "Anita Sharma"],
    ),
    FieldDefinition(
        name="date_of_birth",
        display_name="Date of Birth",
        field_type=FieldType.DATE,
        description="Full date of birth when explicitly printed",
        required=False,
        location_hint="Front side - next to DOB label",
        examples=["01/01/1990", "1990-01-01"],
    ),
    FieldDefinition(
        name="year_of_birth",
        display_name="Year of Birth",
        field_type=FieldType.STRING,
        description="Year of birth when only YOB is shown instead of full DOB",
        required=False,
        location_hint="Front side - next to YOB label",
        pattern=r"^\d{4}$",
        examples=["1990", "2001"],
    ),
    FieldDefinition(
        name="gender",
        display_name="Gender",
        field_type=FieldType.STRING,
        description="Gender of the Aadhaar holder",
        required=False,
        location_hint="Front side - near DOB / YOB",
        allowed_values=["Male", "Female", "Other", "M", "F"],
        examples=["Male", "Female"],
    ),
]


ADDRESS_FIELDS = [
    FieldDefinition(
        name="care_of",
        display_name="Care Of",
        field_type=FieldType.STRING,
        description="C/O, S/O, D/O or W/O line if present in the address block",
        required=False,
        location_hint="Back side or lower section of Aadhaar letter - above address body",
        examples=["S/O Rajesh Kumar", "C/O Anita Devi"],
    ),
    FieldDefinition(
        name="address",
        display_name="Address",
        field_type=FieldType.ADDRESS,
        description="Residential address of the Aadhaar holder",
        required=False,
        location_hint="Back side or lower section - address block",
    ),
    FieldDefinition(
        name="postal_pin_code",
        display_name="Postal PIN Code",
        field_type=FieldType.STRING,
        description="6-digit Indian postal PIN code if visible",
        required=False,
        location_hint="End of address block",
        pattern=r"^\d{6}$",
        examples=["400614", "110001"],
    ),
    FieldDefinition(
        name="state_or_ut",
        display_name="State / UT",
        field_type=FieldType.STRING,
        description="Indian state or union territory if separable from the address",
        required=False,
        location_hint="Address block",
        examples=["Maharashtra", "Delhi", "Karnataka"],
    ),
]


CONTACT_FIELDS = [
    FieldDefinition(
        name="mobile_number",
        display_name="Mobile Number",
        field_type=FieldType.PHONE,
        description="Registered mobile number if printed or partially masked",
        required=False,
        location_hint="Supporting Aadhaar letter or QR-related section",
        examples=["+91 9876543210", "9876543210"],
    ),
]


AADHAAR_CARD_SCHEMA = DocumentSchema(
    name="aadhaar_card",
    display_name="Aadhaar Card",
    document_type=DocumentType.AADHAAR_CARD,
    description="Indian Aadhaar identity card / Aadhaar letter issued by UIDAI.",
    version="1.0.0",
    fields=IDENTITY_FIELDS + PERSON_FIELDS + ADDRESS_FIELDS + CONTACT_FIELDS,
    required_sections=["identity", "holder_details"],
    classification_hints=[
        "Aadhaar",
        "Government of India",
        "Unique Identification Authority of India",
        "UIDAI",
        "DOB",
        "YOB",
        "Male",
        "Female",
        "Address",
    ],
    extraction_prompt_template=(
        "Extract Aadhaar card fields exactly as printed. "
        "If the document shows YOB only, populate year_of_birth and leave date_of_birth null. "
        "If the document shows a full DOB, populate date_of_birth. "
        "Do not invent values not visible on the card or letter."
    ),
)


SchemaRegistry().register(AADHAAR_CARD_SCHEMA)
