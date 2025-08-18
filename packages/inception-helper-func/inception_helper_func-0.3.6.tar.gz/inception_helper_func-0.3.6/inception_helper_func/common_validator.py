import re
from pydantic import BaseModel, EmailStr, BeforeValidator
from enum import Enum
from typing import Literal, Annotated, List, Dict

class PhotoDType(BaseModel):
    id: str
    key: str
    filename: str
    unique_filename: str
    url: str
    content_type: str
    extension: str
    size: str = "100KB"
    thumbnail_url: str = ""
    thumbnail_key: str = ""
    thumbnail_filename: str = ""

class AttachmentDType(BaseModel):
    id: str
    key: str
    filename: str
    unique_filename: str
    url: str
    content_type: str
    extension: str
    size: str = "100KB"
    thumbnail_url: str = ""
    thumbnail_key: str = ""
    thumbnail_filename: str = ""

class ReferenceLinkDType(BaseModel):
    link: str
    name: str = ""

def strip_and_lower(v: object) -> str:
    return str(v).strip().lower()


EmailApiDType = Annotated[
    EmailStr,
    BeforeValidator(strip_and_lower),
]

class CommonSchemaDType(BaseModel):
    id: str
    name: str


class BusinessProfileDType(BaseModel):
    id: str
    profile_name: str
    business_name: str
    logo: PhotoDType

class CoordinatesDType(BaseModel):
    lat: float = 0.0
    lng: float = 0.0
    accuracy: str = ""


class AddressComponentDType(BaseModel):
    long_name: str = ""
    short_name: str = ""
    types: list[str] = []


class AddressDType(BaseModel):
    formatted: str = ""
    components: dict[str, str] = {}


class ViewportDType(BaseModel):
    northeast: CoordinatesDType
    southwest: CoordinatesDType


class GoogleDataDType(BaseModel):
    place_id: str = ""
    viewport: ViewportDType


class MetadataDType(BaseModel):
    source: Literal["browser_geolocation", "google_maps", "manual_entry", "gps_location"]
    retrieved_at: str = ""


class LocationDataDType(BaseModel):
    coordinates: CoordinatesDType
    address: AddressDType
    google_data: GoogleDataDType
    metadata: MetadataDType


class UnitDType(BaseModel):
    id: str = ""
    name: str = ""
    symbol: str = ""
    code: str = ""
    group: CommonSchemaDType | None = None

class DimensionDType(BaseModel):
    length: float = 0
    width: float = 0
    height_or_thickness: float = 0
    # heat_number: use for coil/sheet/etc. A heat number is a unique identifier assigned to a batch of metal produced in a single furnace (or "heat") 
    # during a melting process in steel or metal manufacturing. The heat number allows traceability
    heat_number: str = ""
    unit: UnitDType

class WeightDType(BaseModel):
    value: float = 0
    unit: UnitDType

class MaterialDType(BaseModel):
    id: str
    name: str
    image_url: str = ""

class BrandDType(BaseModel):
    id: str
    name: str
    image_url: str = ""

class CategoryDType(BaseModel):
    id: str
    name: str
    slug: str = ""
    image_url: str = ""

class SubCategoryDType(BaseModel):
    id: str
    name: str
    category_id: str
    slug: str = ""
    image_url: str = ""

class ManufacturerDType(BaseModel):
    id: str
    name: str
    image_url: str = ""

class ManagerDType(BaseModel):
    account_num: str
    full_name: str
    email: EmailApiDType
    photo: PhotoDType | None = None
    role: CommonSchemaDType


class CountryDType(BaseModel):
    id: str = ""
    iso_code_2: str = ""
    iso_code_3: str = ""
    name: str = ""
    zip_code: str = ""
    zip_code_raw: str = ""
    phone_num_start_with_zero: bool = False
    flag_url: str = ""


class CityTownDType(BaseModel):
    id: str = ""
    name: str = ""
    country_iso_code: str = ""


class StateProvinceDType(BaseModel):
    id: str = ""
    country_iso_code: str = ""
    name: str = ""


class WarehouseDType(BaseModel):
    id: str
    name: str

class ManufacturerDType(BaseModel):
    id: str
    name: str
    logo: PhotoDType

class ColorDType(BaseModel):
    id: str
    name: str
    code: str

    
class BrandDType(BaseModel):
    id: str
    name: str
    logo: PhotoDType

 
class ShelveDType(BaseModel):
    id: str
    name: str


class CurrencyDType(BaseModel):
    id: str
    country_iso_code: str
    currency_iso_code: str
    name: str
    symbol: str
    flag_url: str = ""


class CurrencyLocaleDType(BaseModel):
    id: str
    locale: str
    language: str
    currency: str
    symbol: str
    symbol_first: bool

class DateFormatDType(BaseModel):
    id: str
    name: str
    format: str
    py_date_fmt: str
    py_datetime_zone_fmt: str
    js_date_fmt: str
    js_datetime_zone_fmt: str



class TimeFormatDType(BaseModel):
    id: str
    name: str
    py_time_fmt: str
    py_time_fmt_zone: str
    js_time_fmt: str
    js_time_fmt_zone: str


class TimeZoneDType(BaseModel):
    id: str
    iso_code: str
    name: str
    utc_offset_hh_mm: str
    utc_dst_offset_hh_mm: str



class SystemOfMeasurementDType(BaseModel):
    id: str
    name: str
    symbol: str
    system: str
    description: str = "Length unit"


class PreparerTermDType(BaseModel):
    id: str
    name: str


class EstimateDocumentTitleDType(BaseModel):
    id: str
    name: str


class InvoiceDocumentTitleDType(BaseModel):
    id: str
    name: str


class BillFrequencyDType(BaseModel):
    id: str
    name: str
    unit: str
    num_of_days: int = 0



class DueDateDType(BaseModel):
    id: str
    name: str
    num_of_days: int = 0


class TemplateDType(BaseModel):
    id: str
    key: str
    name: str
    type: str
    flag_url: str = ""



class ClientCommunicationOptionsDType(BaseModel):
    whatsapp: bool = True
    email: bool = True
    sms: bool = False
    phone_call: bool = True


class ClientDType(BaseModel):
    id: str
    full_name: str
    first_name: str
    last_name: str
    primary_email: EmailApiDType
    secondary_email: EmailApiDType = ""
    primary_phone_number: str
    secondary_phone_number: str = ""
    whatsapp_number: str = ""
    photo: PhotoDType
    communication_options: ClientCommunicationOptionsDType



class CompanyDType(BaseModel):
    id: str
    company_name: str
    logo: PhotoDType



class VendorDType(BaseModel):
    id: str
    vendor_name: str
    logo: PhotoDType




class IconDType(BaseModel):
    key: str  #  "fa-solid fa-user"
    name: str  #  "User"
    url: str  # "https://fontawesome.com/icons/user?s=solid"
    use_url: bool = False


class AppType(str, Enum):
    INTERNAL = "InternalServices"
    EXTERNAL = "ExternalIntegrations"


class AuthType(str, Enum):
    OAUTH2 = "OAuth2"
    API_KEY = "APIKey"
    BASIC_AUTH = "BasicAuth"
    JWT = "JWT"

class AppDType(BaseModel):
    id: str
    name: str
    short_name: str
    logo: PhotoDType
    icon: IconDType
    type: AppType

class DepartmentDType(BaseModel):
    id: str
    name: str


class TeamDType(BaseModel):
    id: str
    name: str

    
class ChartOfAccountsDType(BaseModel):
    account_number: int
    name: str
    main_chart_of_account_type_id: str
    sub_chart_of_account_type_id: str


class DocumentAttachementDType(BaseModel):
    type: CommonSchemaDType
    data: AttachmentDType | ReferenceLinkDType
    
    
    
    
