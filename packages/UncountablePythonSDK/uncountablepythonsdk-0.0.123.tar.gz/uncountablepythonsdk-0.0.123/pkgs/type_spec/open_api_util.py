from abc import ABC, abstractmethod
from enum import StrEnum

from pkgs.serialization_util import JsonValue


class OpenAPIType(ABC):
    description: str | None = None
    nullable: bool = False
    default: JsonValue

    def __init__(
        self,
        description: str | None = None,
        nullable: bool = False,
        default: JsonValue = None,
    ) -> None:
        self.description = description
        self.nullable = nullable
        self.default = default

    @abstractmethod
    def asdict(self) -> dict[str, object]:
        pass

    def add_addl_info(self, emitted: dict[str, object]) -> dict[str, object]:
        if self.description is not None:
            emitted["description"] = self.description
        if self.nullable:
            emitted["nullable"] = self.nullable
        if self.default is not None:
            emitted["default"] = self.default
        return emitted


class OpenAPIRefType(OpenAPIType):
    source: str

    def __init__(
        self, source: str, description: str | None = None, nullable: bool = False
    ) -> None:
        self.source = source
        super().__init__(description=description, nullable=nullable)

    def asdict(self) -> dict[str, object]:
        # TODO: use parents description and nullable
        return {"$ref": self.source}


class OpenAPIPrimitive(StrEnum):
    string = "string"
    boolean = "boolean"
    integer = "integer"
    number = "number"


class OpenAPIPrimitiveType(OpenAPIType):
    base_type: OpenAPIPrimitive

    def __init__(
        self,
        base_type: OpenAPIPrimitive,
        description: str | None = None,
        nullable: bool = False,
    ) -> None:
        self.base_type = base_type
        super().__init__(description=description, nullable=nullable)

    @property
    def value(self) -> str:
        return self.base_type.value

    def asdict(self) -> dict[str, object]:
        # TODO: use parents description and nullable
        return {"type": self.value}


def OpenAPIStringT() -> OpenAPIPrimitiveType:
    return OpenAPIPrimitiveType(base_type=OpenAPIPrimitive.string)


def OpenAPIBooleanT() -> OpenAPIPrimitiveType:
    return OpenAPIPrimitiveType(base_type=OpenAPIPrimitive.boolean)


def OpenAPIIntegerT() -> OpenAPIPrimitiveType:
    return OpenAPIPrimitiveType(base_type=OpenAPIPrimitive.integer)


def OpenAPINumberT() -> OpenAPIPrimitiveType:
    return OpenAPIPrimitiveType(base_type=OpenAPIPrimitive.number)


class OpenAPIEmptyType(OpenAPIType):
    def __init__(self, description: str | None = None, nullable: bool = False) -> None:
        super().__init__(description=description, nullable=nullable)

    def asdict(self) -> dict[str, object]:
        return self.add_addl_info({})


class OpenAPIEnumType(OpenAPIType):
    """
    represents OpenAPIs type: "string"; with enum set to the corresponding
    options
    """

    base_type: OpenAPIPrimitiveType = OpenAPIStringT()
    options: list[str]

    def __init__(
        self, options: list[str], description: str | None = None, nullable: bool = False
    ) -> None:
        self.options = options
        super().__init__(description=description, nullable=nullable)

    def asdict(self) -> dict[str, object]:
        return self.add_addl_info({
            "type": self.base_type.value,
            "enum": self.options,
        })


class OpenAPIArrayType(OpenAPIType):
    """
    represents OpenAPIs type: "array"
    """

    base_types: list[OpenAPIType]

    def __init__(
        self,
        base_types: OpenAPIType | list[OpenAPIType],
        description: str | None = None,
        nullable: bool = False,
    ) -> None:
        if not isinstance(base_types, list):
            base_types = [base_types]
        self.base_types = base_types
        super().__init__(description=description, nullable=nullable)

    def asdict(self) -> dict[str, object]:
        items = [base_type.asdict() for base_type in self.base_types]
        return self.add_addl_info({
            "type": "array",
            "items": items[0] if len(items) == 1 else items,
        })


class OpenAPIFreeFormObjectType(OpenAPIType):
    def __init__(self, description: str | None = None, nullable: bool = False) -> None:
        super().__init__(description=description, nullable=nullable)

    def asdict(self) -> dict[str, object]:
        return self.add_addl_info({"type": "object"})


class OpenAPIObjectType(OpenAPIType):
    """
    represents OpenAPIs type: "object"
    """

    properties: dict[str, OpenAPIType]

    def __init__(
        self,
        properties: dict[str, OpenAPIType],
        description: str | None = None,
        nullable: bool = False,
        *,
        property_desc: dict[str, str] | None = None,
    ) -> None:
        self.properties = properties
        if property_desc is None:
            self.property_desc = {}
        else:
            self.property_desc = property_desc
        super().__init__(description=description, nullable=nullable)

    def _emit_property_desc(self, property_name: str) -> dict[str, str]:
        desc = self.property_desc.get(property_name)
        if desc is None or desc.strip() == "":
            return {}

        return {"description": desc}

    def _emit_property(
        self, property_name: str, property_type: OpenAPIType
    ) -> dict[str, object]:
        property_info = {
            **property_type.asdict(),
        }
        property_description = self._emit_property_desc(property_name)
        if "$ref" in property_info and "description" in property_description:
            return {"allOf": [property_info, property_description]}

        return property_info | property_description

    def asdict(self) -> dict[str, object]:
        return self.add_addl_info({
            "type": "object",
            "required": [
                property_name
                for property_name, property_type in self.properties.items()
                if not property_type.nullable
            ],
            "properties": {
                property_name: self._emit_property(property_name, property_type)
                for property_name, property_type in self.properties.items()
            },
        })


class OpenAPIUnionType(OpenAPIType):
    """
    represents OpenAPIs type: "oneOf"
    """

    base_types: list[OpenAPIType]

    def __init__(
        self,
        base_types: list[OpenAPIType],
        description: str | None = None,
        nullable: bool = False,
        discriminator: str | None = None,
        discriminator_map: dict[str, OpenAPIRefType] | None = None,
    ) -> None:
        self.base_types = base_types
        self._discriminator = discriminator
        self._discriminator_map = discriminator_map
        super().__init__(description=description, nullable=nullable)

    def asdict(self) -> dict[str, object]:
        # TODO: use parents description and nullable
        return {
            "oneOf": [base_type.asdict() for base_type in self.base_types],
            "discriminator": {
                "propertyName": self._discriminator,
                "mapping": {
                    discriminator_value: base_type.source
                    for discriminator_value, base_type in self._discriminator_map.items()
                },
            }
            if self._discriminator is not None and self._discriminator_map is not None
            else None,
        }


class OpenAPIIntersectionType(OpenAPIType):
    """
    represents OpenAPIs type: "allOf"
    """

    base_types: list[OpenAPIType]

    def __init__(
        self,
        base_types: list[OpenAPIType],
        description: str | None = None,
        nullable: bool = False,
    ) -> None:
        self.base_types = base_types
        super().__init__(description=description, nullable=nullable)

    def asdict(self) -> dict[str, object]:
        # TODO: use parents description and nullable
        return {"allOf": [base_type.asdict() for base_type in self.base_types]}
