import enum
from typing import Any, Dict, List, Optional, Self, Union
from typing_extensions import Annotated
from pydantic import BaseModel, BeforeValidator, Field, model_serializer, model_validator
import uri_template

class HALFormsMethod(str, enum.Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    
class HALFormsPropertyType(str, enum.Enum):
    # Basic input types
    hidden = "hidden"
    text = "text"
    textarea = "textarea"
    search = "search"
    tel = "tel"
    url = "url"
    email = "email"
    password = "password"
    
    # Date and time inputs
    date = "date"
    month = "month"
    week = "week"
    time = "time"
    datetime = "datetime"
    datetime_local = "datetime-local"
    
    # Numeric inputs
    number = "number"
    range = "range"
    
    # Color picker
    color = "color"
    
    # Selection inputs
    checkbox = "checkbox"
    radio = "radio"
    
    # File inputs
    file = "file"
    
    # Button inputs
    button = "button"
    submit = "submit"
    reset = "reset"
    
    # Image input
    image = "image"
    
    # Selection lists (not strictly input types but related)
    select = "select"
    datalist = "datalist"
    
    # Non-standard but useful types
    dropdown = "dropdown"  # Custom type for dropdown menus

class HALFormsOptionsLink(BaseModel):
    href : str
    templated : bool = False
    type : str = "application/json"
    
    @model_validator(mode='after')
    def check_valid_uri_template(self) -> Self:
        if self.templated:
            if not uri_template.validate(template=self.href):
                raise ValueError(f"Invalid URI template: {self.href}")
        return self
    
    def expand_template(self, **kwargs) -> str:
        """
        Expand the URI template with the provided variables.
        
        Args:
            **kwargs: Variables to use for template expansion
            
        Returns:
            The expanded URI
        """
        if not self.templated:
            return self.href
        
        return str(uri_template.URITemplate(self.href).expand(**kwargs))

class HALFormsOptionsValueItem(BaseModel):
    value: str = Field(...)
    prompt: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow additional fields
    
    def __init__(self, value: Union[str, None] = None, **data):
        """
        Initialize with either a string value or keyword arguments.
        If first argument is a string, use it as the value.
        """
        if isinstance(value, str):
            data['value'] = value
            super().__init__(**data)
        elif value is None:
            super().__init__(**data)
        else:
            # value is provided as keyword argument in **data
            super().__init__(value=value, **data)
    
    @model_validator(mode='after')
    def set_prompt_default(self):
        if self.prompt is None:
            self.prompt = self.value
        return self

    @model_serializer
    def ser_model(self) -> str | dict[str, Any]:
        """
        Serialize to either a string (if simple case) or dictionary.
        This custom logic is needed because the HAL Forms spec allows
        both string and object representations for value items.
        """
        prompt = self.prompt or self.value  # Use value as prompt if prompt is None
        
        # Get extra fields (fields not defined in the model schema)
        extra_data = getattr(self, '__pydantic_extra__', {})
        
        # Return simple string if no extras and prompt equals value
        if not extra_data and prompt == self.value:
            return self.value
        
        # Return full object representation
        result = {"prompt": prompt, "value": self.value}
        result.update(extra_data)
        return result

def transform_inline_strings(inline_options : Optional[List[Any]]) -> Optional[List[Dict[str, Any]]]:
    # Convert inline options to a list of dictionaries if they are strings so they get serialized correctly.
    # If something random is submitted, validation will later fail.
    options = []
    if not inline_options:
        return None
    for opt in inline_options:
        if isinstance(opt, str):
            options.append({"value": opt, "prompt": opt})
        else:
            options.append(opt)
    return options

class HALFormsOptions(BaseModel):
    inline: Annotated[Optional[List[ HALFormsOptionsValueItem]], BeforeValidator(transform_inline_strings)] = None
    link: Optional[HALFormsOptionsLink] = None
    maxItems: Optional[int] = None
    minItems: Optional[int] = None
    promptField: str = "prompt"
    selectedValues: Optional[List[str]] = []
    valueField: str = "value"

def validate_type(value : str):
    if value not in HALFormsPropertyType._value2member_map_:
        return "text"
    return value
    
class HALFormsProperty(BaseModel):
    name: str
    type: Annotated[Optional[HALFormsPropertyType], BeforeValidator(validate_type)] = HALFormsPropertyType.text
    prompt: Optional[str] = None
    readOnly: Optional[bool] = None
    regex: Optional[str] = None
    required: Optional[bool] = None
    templated: Optional[bool] = None
    value: Optional[str] = None
    cols: Optional[int] = None
    max: Optional[int] = None
    maxLength: Optional[int] = None
    min: Optional[int] = None
    minLength: Optional[int] = None
    options: Optional[HALFormsOptions] = None
    placeholder: Optional[str] = None
    rows: Optional[int] = None
    step: Optional[int] = None
        

class HALFormsTemplate(BaseModel):
    method: HALFormsMethod
    contentType: Optional[str] = "application/json"
    properties: List[HALFormsProperty] = []
    target: Optional[str] = None
    title: Optional[str] = None