"""
Test fixtures for pydantic_variants library.

This module contains various Pydantic model fixtures covering different features:
- Basic models with different field types
- Models with validation and constraints
- Generic models with TypeVar
- Models with forward references requiring rebuild
- Models with computed fields and private attributes
- Models with custom configurations
- Nested models and complex hierarchies
"""

from __future__ import annotations

import pytest
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum, IntEnum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Literal, Generic, TypeVar, ForwardRef, Annotated, ClassVar, Set, Tuple, FrozenSet
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    computed_field,
    PrivateAttr,
    validator,
    root_validator,
    field_validator,
    model_validator,
    EmailStr,
    HttpUrl,
    IPvAnyAddress,
    Json,
    SecretStr,
    PositiveInt,
    NegativeInt,
    NonNegativeInt,
    NonPositiveInt,
    PositiveFloat,
    NegativeFloat,
    NonNegativeFloat,
    NonPositiveFloat,
    StrictInt,
    StrictFloat,
    StrictStr,
    StrictBool,
    conint,
    confloat,
    constr,
    conlist,
    conset,
    conbytes,
    ByteSize,
    create_model,
)


# Enums for testing
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


# Generic TypeVars
T = TypeVar("T")
U = TypeVar("U", bound=BaseModel)
NumericType = TypeVar("NumericType", int, float, Decimal)


@pytest.fixture
def basic_user_model():
    """Simple user model with basic field types."""

    class User(BaseModel):
        id: int
        name: str
        email: str
        age: Optional[int] = None
        is_active: bool = True
        created_at: datetime

    return User


@pytest.fixture
def model_with_various_types():
    """Model with many different field types for comprehensive testing."""

    class VariousTypes(BaseModel):
        # Basic types
        string_field: str
        int_field: int
        float_field: float
        bool_field: bool
        bytes_field: bytes

        # Optional and Union types
        optional_str: Optional[str] = None
        union_field: Union[str, int, None] = None
        literal_field: Literal["option1", "option2", "option3"] = "option1"

        # Collections
        list_field: List[str] = []
        dict_field: Dict[str, Any] = {}
        set_field: Set[int] = set()
        tuple_field: Tuple[str, int, bool] = ("", 0, False)
        frozenset_field: FrozenSet[str] = frozenset()

        # Special types
        uuid_field: UUID = Field(default_factory=uuid4)
        path_field: Path = Path(".")
        decimal_field: Decimal = Decimal("0.00")
        date_field: date = Field(default_factory=date.today)
        time_field: time = time(12, 0)
        datetime_field: datetime = Field(default_factory=datetime.now)

        # Pydantic special types
        email_field: EmailStr = "test@example.com"
        url_field: HttpUrl = "https://example.com"
        ip_field: IPvAnyAddress = "192.168.1.1"
        json_field: Json[Dict[str, Any]] = {}

        # Constrained types
        positive_int: PositiveInt = 1
        negative_float: NegativeFloat = -1.0
        bytesize_field: ByteSize = "1MB"

        # Strict types
        strict_int: StrictInt = 42
        strict_str: StrictStr = "strict"
        strict_bool: StrictBool = True

        # Enum
        role: UserRole = UserRole.USER
        priority: Priority = Priority.MEDIUM

        # Annotated field with metadata
        annotated_field: Annotated[str, Field(description="Metadata example")] = "annotated"

    return VariousTypes


@pytest.fixture
def model_with_computed_fields():
    """Model with computed fields and private attributes."""

    class ModelWithComputed(BaseModel):
        first_name: str
        last_name: str
        birth_year: int

        # Private attributes
        _cache: Dict[str, Any] = PrivateAttr(default_factory=dict)
        _internal_id: str = PrivateAttr(default_factory=lambda: str(uuid4()))

        @computed_field
        @property
        def full_name(self) -> str:
            return f"{self.first_name} {self.last_name}"

        @computed_field
        @property
        def age(self) -> int:
            current_year = datetime.now().year
            return current_year - self.birth_year

        @computed_field
        @property
        def initials(self) -> str:
            return f"{self.first_name[0]}.{self.last_name[0]}."

    return ModelWithComputed


@pytest.fixture
def model_with_validators():
    """Model with custom validators."""

    class ModelWithValidators(BaseModel):
        name: str
        email: str
        password: str
        confirm_password: str

        @field_validator("name")
        @classmethod
        def validate_name(cls, v):
            if not v.strip():
                raise ValueError("Name cannot be empty")
            return v.title()

        @field_validator("email")
        @classmethod
        def validate_email(cls, v):
            if "@" not in v:
                raise ValueError("Invalid email format")
            return v.lower()

        @model_validator(mode="after")
        def validate_passwords_match(self):
            if self.password != self.confirm_password:
                raise ValueError("Passwords do not match")
            return self

    return ModelWithValidators


@pytest.fixture
def generic_models():
    """Generic models with TypeVar."""

    class Container(BaseModel, Generic[T]):
        items: List[T]
        count: int = Field(default=0)
        metadata: Dict[str, Any] = {}

        @computed_field
        @property
        def item_count(self) -> int:
            return len(self.items)

    class Response(BaseModel, Generic[T]):
        data: T
        success: bool = True
        message: Optional[str] = None
        timestamp: datetime = Field(default_factory=datetime.now)

    class NumericContainer(BaseModel, Generic[NumericType]):
        value: NumericType
        min_val: NumericType
        max_val: NumericType

        @model_validator(mode="after")
        def validate_range(self):
            if not (self.min_val <= self.value <= self.max_val):
                raise ValueError("Value must be between min_val and max_val")
            return self

    return Container, Response, NumericContainer


@pytest.fixture
def nested_models():
    """Nested model hierarchy."""

    class Address(BaseModel):
        street: str
        city: str
        state: str
        zip_code: str = Field(pattern=r"^\d{5}(-\d{4})?$")
        country: str = "USA"

    class ContactInfo(BaseModel):
        email: EmailStr
        phone: Optional[str] = Field(None, pattern=r"^\+?1?-?\(?\d{3}\)?-?\d{3}-?\d{4}$")
        address: Address

    class Profile(BaseModel):
        bio: Optional[str] = None
        website: Optional[HttpUrl] = None
        avatar_url: Optional[HttpUrl] = None
        social_links: Dict[str, HttpUrl] = {}

    class User(BaseModel):
        id: UUID = Field(default_factory=uuid4)
        username: str = Field(min_length=3, max_length=50)
        contact: ContactInfo
        profile: Optional[Profile] = None
        tags: List[str] = []
        roles: Set[UserRole] = {UserRole.USER}
        created_at: datetime = Field(default_factory=datetime.now)
        updated_at: Optional[datetime] = None

        # Class variable
        _version: ClassVar[str] = "1.0.0"

    return User, ContactInfo, Address, Profile


@pytest.fixture
def models_with_forward_refs():
    """Models with forward references that need rebuilding."""

    class User(BaseModel):
        id: int
        name: str
        posts: List["Post"] = []  # Forward reference
        profile: Optional[UserProfile] = None  # Forward reference

    class Post(BaseModel):
        id: int
        title: str
        content: str
        author: User  # Circular reference
        tags: List["Tag"] = []  # Forward reference
        created_at: datetime = Field(default_factory=datetime.now)

    class Tag(BaseModel):
        id: int
        name: str
        posts: List[Post] = []  # Circular reference

    class UserProfile(BaseModel):
        user_id: int
        bio: Optional[str] = None
        user: User  # Back reference

    # These models need to be rebuilt due to forward references
    return User, Post, Tag, UserProfile


@pytest.fixture
def models_with_configs():
    """Models with different configuration options."""

    class StrictModel(BaseModel):
        model_config = ConfigDict(strict=True, extra="forbid", frozen=True, validate_assignment=True)

        id: StrictInt
        name: StrictStr
        active: StrictBool

    class FlexibleModel(BaseModel):
        model_config = ConfigDict(extra="allow", str_strip_whitespace=True, validate_default=True, from_attributes=True)

        name: str
        value: Optional[Any] = None

    class AliasModel(BaseModel):
        model_config = ConfigDict(populate_by_name=True)

        user_id: int = Field(alias="userId")
        full_name: str = Field(alias="fullName")
        email_address: EmailStr = Field(alias="emailAddress")

    return StrictModel, FlexibleModel, AliasModel


@pytest.fixture
def complex_hierarchy():
    """Complex nested model hierarchy for advanced testing."""

    class Permission(BaseModel):
        id: int
        name: str
        resource: str
        action: str

    class Role(BaseModel):
        id: int
        name: str
        permissions: List[Permission] = []

    class Department(BaseModel):
        id: int
        name: str
        manager_id: Optional[int] = None

    class Employee(BaseModel):
        id: int
        employee_id: str = Field(pattern=r"^EMP\d{6}$")
        first_name: str
        last_name: str
        email: EmailStr
        department: Department
        roles: List[Role] = []
        manager: Optional[Employee] = None  # Self-reference
        direct_reports: List[Employee] = []  # Self-reference
        salary: Optional[Decimal] = Field(None, decimal_places=2)
        hire_date: date
        is_active: bool = True

        @computed_field
        @property
        def full_name(self) -> str:
            return f"{self.first_name} {self.last_name}"

    class Company(BaseModel):
        id: int
        name: str
        employees: List[Employee] = []
        departments: List[Department] = []

    return Company, Employee, Department, Role, Permission


@pytest.fixture
def dynamic_models():
    """Dynamically created models for testing create_model functionality."""
    # Simple dynamic model
    DynamicUser = create_model(
        "DynamicUser", id=(int, ...), name=(str, ...), email=(str, Field(default="user@example.com")), age=(Optional[int], None)
    )

    # Dynamic model with complex fields
    DynamicProduct = create_model(
        "DynamicProduct",
        __config__=ConfigDict(extra="forbid"),
        id=(UUID, Field(default_factory=uuid4)),
        name=(str, Field(min_length=1, max_length=100)),
        price=(Decimal, Field(decimal_places=2, gt=0)),
        categories=(List[str], []),
        metadata=(Dict[str, Any], {}),
        created_at=(datetime, Field(default_factory=datetime.now)),
    )

    return DynamicUser, DynamicProduct


@pytest.fixture
def rebuild_models(models_with_forward_refs):
    """Rebuild models with forward references."""
    User, Post, Tag, UserProfile = models_with_forward_refs

    # Rebuild all models to resolve forward references
    User.model_rebuild()
    Post.model_rebuild()
    Tag.model_rebuild()
    UserProfile.model_rebuild()

    return User, Post, Tag, UserProfile


@pytest.fixture
def all_test_models(
    basic_user_model,
    user_with_constraints,
    model_with_various_types,
    model_with_computed_fields,
    model_with_validators,
    generic_models,
    nested_models,
    models_with_configs,
    complex_hierarchy,
    dynamic_models,
    rebuild_models,
):
    """Collection of all test models for comprehensive testing."""
    Container, Response, NumericContainer = generic_models
    User, ContactInfo, Address, Profile = nested_models
    StrictModel, FlexibleModel, AliasModel = models_with_configs
    Company, Employee, Department, Role, Permission = complex_hierarchy
    DynamicUser, DynamicProduct = dynamic_models
    UserWithForwardRefs, Post, Tag, UserProfile = rebuild_models

    return {
        "basic_user": basic_user_model,
        "user_constrained": user_with_constraints,
        "various_types": model_with_various_types,
        "computed_fields": model_with_computed_fields,
        "validators": model_with_validators,
        "generic_container": Container,
        "generic_response": Response,
        "numeric_container": NumericContainer,
        "nested_user": User,
        "contact_info": ContactInfo,
        "address": Address,
        "profile": Profile,
        "strict_model": StrictModel,
        "flexible_model": FlexibleModel,
        "alias_model": AliasModel,
        "company": Company,
        "employee": Employee,
        "department": Department,
        "role": Role,
        "permission": Permission,
        "dynamic_user": DynamicUser,
        "dynamic_product": DynamicProduct,
        "user_forward_refs": UserWithForwardRefs,
        "post": Post,
        "tag": Tag,
        "user_profile": UserProfile,
    }


# Sample data fixtures for testing
@pytest.fixture
def sample_user_data():
    """Sample data for user models."""
    return {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 30, "is_active": True, "created_at": datetime.now()}


@pytest.fixture
def sample_nested_data():
    """Sample nested data for complex models."""
    return {
        "id": str(uuid4()),
        "username": "johndoe",
        "contact": {
            "email": "john@example.com",
            "phone": "+1-555-123-4567",
            "address": {"street": "123 Main St", "city": "Anytown", "state": "CA", "zip_code": "12345", "country": "USA"},
        },
        "profile": {
            "bio": "Software developer",
            "website": "https://johndoe.dev",
            "social_links": {"github": "https://github.com/johndoe", "linkedin": "https://linkedin.com/in/johndoe"},
        },
        "tags": ["developer", "python", "fastapi"],
        "roles": ["user"],
    }
