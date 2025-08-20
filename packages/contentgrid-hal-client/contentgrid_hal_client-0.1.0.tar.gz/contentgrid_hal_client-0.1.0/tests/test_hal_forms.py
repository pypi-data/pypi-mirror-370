import pytest
from contentgrid_hal_client.hal_forms import (
    HALFormsMethod, 
    HALFormsPropertyType, 
    HALFormsProperty, 
    HALFormsTemplate,
    HALFormsOptions,
    HALFormsOptionsLink,
    HALFormsOptionsValueItem
)
class TestHALFormsOptionsValueItem:
    def test_create_with_value_only(self):
        """Test creating an options value item with only a value."""
        item = HALFormsOptionsValueItem(value="test")
        assert item.value == "test"
        assert item.prompt == "test"  # Prompt defaults to value
        
    def test_create_with_value_and_prompt(self):
        """Test creating an options value item with value and prompt."""
        item = HALFormsOptionsValueItem(value="test", prompt="Test Option")
        assert item.value == "test"
        assert item.prompt == "Test Option"
        
    def test_create_with_additional_fields(self):
        """Test creating an options value item with additional fields."""
        item = HALFormsOptionsValueItem(value="test", prompt="Test Option", group="Group A", order=1)
        assert item.value == "test"
        assert item.prompt == "Test Option"
        assert item.group == "Group A"
        assert item.order == 1
        
    def test_serialize_value_only(self):
        """Test serializing an options value item with only a value."""
        item = HALFormsOptionsValueItem(value="test")
        assert item.model_dump() == "test"
        
    def test_serialize_with_prompt(self):
        """Test serializing an options value item with a different prompt."""
        item = HALFormsOptionsValueItem(value="test", prompt="Test Option")
        serialized = item.model_dump()
        assert serialized == {"prompt": "Test Option", "value": "test"}
        
    def test_serialize_with_additional_fields(self):
        """Test serializing an options value item with additional fields."""
        item = HALFormsOptionsValueItem(value="test", prompt="Test Option", group="Group A", order=1)
        serialized = item.model_dump()
        assert serialized == {"prompt": "Test Option", "value": "test", "group": "Group A", "order": 1}
        
    def test_deserialize_string(self):
        """Test deserializing a string to an options value item."""
        item = HALFormsOptionsValueItem("test")
        assert item.value == "test"
        assert item.prompt == "test"
        
    def test_deserialize_dict(self):
        """Test deserializing a dictionary to an options value item."""
        data = {"value": "test", "prompt": "Test Option", "group": "Group A", "order": 1}
        item = HALFormsOptionsValueItem(**data)
        assert item.value == "test"
        assert item.prompt == "Test Option"
        assert item.group == "Group A"
        assert item.order == 1

class TestHALFormsOptionsLink:
    def test_create_with_required_fields(self):
        """Test creating an options link with only required fields."""
        link = HALFormsOptionsLink(href="http://api.example.org/options")
        assert link.href == "http://api.example.org/options"
        assert link.templated is False
        assert link.type == "application/json"
        
    def test_create_with_all_fields(self):
        """Test creating an options link with all fields."""
        link = HALFormsOptionsLink(
            href="http://api.example.org/options/{id}",
            templated=True,
            type="text/csv"
        )
        assert link.href == "http://api.example.org/options/{id}"
        assert link.templated is True
        assert link.type == "text/csv"
        
    def test_invalid_uri_template(self):
        """Test that an invalid URI template raises a ValueError."""
        with pytest.raises(ValueError):
            HALFormsOptionsLink(href="http://api.example.org/options/{", templated=True)
            
    def test_expand_template(self):
        """Test expanding a URI template."""
        link = HALFormsOptionsLink(href="http://api.example.org/options/{id}", templated=True)
        expanded = link.expand_template(id="123")
        assert expanded == "http://api.example.org/options/123"
        
    def test_expand_template_not_templated(self):
        """Test that expand_template returns the href when not templated."""
        link = HALFormsOptionsLink(href="http://api.example.org/options")
        expanded = link.expand_template(id="123")
        assert expanded == "http://api.example.org/options"
        
    def test_serialize(self):
        """Test serializing an options link."""
        link = HALFormsOptionsLink(
            href="http://api.example.org/options/{id}",
            templated=True,
            type="text/csv"
        )
        serialized = link.model_dump()
        assert serialized == {
            "href": "http://api.example.org/options/{id}",
            "templated": True,
            "type": "text/csv"
        }
        
    def test_deserialize(self):
        """Test deserializing an options link."""
        data = {
            "href": "http://api.example.org/options/{id}",
            "templated": True,
            "type": "text/csv"
        }
        link = HALFormsOptionsLink(**data)
        assert link.href == "http://api.example.org/options/{id}"
        assert link.templated is True
        assert link.type == "text/csv"

class TestHALFormsOptions:
    def test_create_empty(self):
        """Test creating an empty options object."""
        options = HALFormsOptions()
        # assert options.inline == None
        # assert options.link is None
        assert options.maxItems is None
        assert options.minItems is None
        assert options.promptField == "prompt"
        assert options.selectedValues == []
        assert options.valueField == "value"
        
    def test_create_with_inline_strings(self):
        """Test creating options with inline string values."""
        options = HALFormsOptions(inline=["Option 1", "Option 2", "Option 3"])
        assert len(options.inline) == 3
        assert options.inline[0].value == "Option 1"
        assert options.inline[0].prompt == "Option 1"
        
    def test_create_with_inline_dicts(self):
        """Test creating options with inline dictionary values."""
        options = HALFormsOptions(inline=[
            {"value": "opt1", "prompt": "Option 1"},
            {"value": "opt2", "prompt": "Option 2"}
        ])
        assert len(options.inline) == 2
        assert options.inline[0].value == "opt1"
        assert options.inline[0].prompt == "Option 1"
        
    def test_create_with_link(self):
        """Test creating options with a link."""
        link = HALFormsOptionsLink(href="http://api.example.org/options")
        options = HALFormsOptions(link=link)
        assert options.link == link
        
    def test_create_with_all_parameters(self):
        """Test creating options with all parameters."""
        link = HALFormsOptionsLink(href="http://api.example.org/options")
        options = HALFormsOptions(
            inline=["Option 1", "Option 2"],
            link=link,
            maxItems=5,
            minItems=1,
            promptField="label",
            selectedValues=["Option 1"],
            valueField="code"
        )
        assert len(options.inline) == 2
        assert options.link == link
        assert options.maxItems == 5
        assert options.minItems == 1
        assert options.promptField == "label"
        assert options.selectedValues == ["Option 1"]
        assert options.valueField == "code"
        
    def test_inline_property(self):
        """Test the inline property returns serialized items."""
        options = HALFormsOptions(inline=[
            {"value": "opt1", "prompt": "Option 1"},
            {"value": "opt2", "prompt": "Option 2"}
        ])
        inline = options.inline
        assert len(inline) == 2
        assert inline[0].model_dump() == {"prompt": "Option 1", "value": "opt1"}
        assert inline[1].model_dump() == {"prompt": "Option 2", "value": "opt2"}
        
    def test_serialize_minimal(self):
        """Test serializing a minimal options object."""
        options = HALFormsOptions(**{})
        serialized = options.model_dump(exclude_unset=True)
        assert serialized == {}
        
    def test_serialize_with_inline(self):
        """Test serializing options with inline values."""
        options = HALFormsOptions(inline=["Option 1", "Option 2"])
        serialized = options.model_dump()
        assert "inline" in serialized
        assert serialized["inline"] == ["Option 1", "Option 2"]
        
    def test_serialize_with_all_fields(self):
        """Test serializing options with all fields."""
        link = HALFormsOptionsLink(href="http://api.example.org/options")
        options = HALFormsOptions(
            inline=["Option 1", "Option 2"],
            link=link,
            maxItems=5,
            minItems=1,
            promptField="label",
            selectedValues=["Option 1"],
            valueField="code"
        )
        serialized = options.model_dump()
        assert "inline" in serialized
        assert "link" in serialized
        assert serialized["maxItems"] == 5
        assert serialized["minItems"] == 1
        assert serialized["promptField"] == "label"
        assert serialized["selectedValues"] == ["Option 1"]
        assert serialized["valueField"] == "code"
        
    def test_deserialize(self):
        """Test deserializing options."""
        data = {
            "inline": [
                {"value": "opt1", "prompt": "Option 1"},
                {"value": "opt2", "prompt": "Option 2"}
            ],
            "link": {
                "href": "http://api.example.org/options",
                "templated": False,
                "type": "application/json"
            },
            "maxItems": 5,
            "minItems": 1,
            "promptField": "label",
            "selectedValues": ["opt1"],
            "valueField": "code"
        }
        options = HALFormsOptions(**data)
        assert len(options.inline) == 2
        assert options.link is not None
        assert options.link.href == "http://api.example.org/options"
        assert options.maxItems == 5
        assert options.minItems == 1
        assert options.promptField == "label"
        assert options.selectedValues == ["opt1"]
        assert options.valueField == "code"

class TestHALFormsProperty:
    def test_create_minimal(self):
        """Test creating a property with minimal attributes."""
        prop = HALFormsProperty(name="test")
        assert prop.name == "test"
        assert prop.type == HALFormsPropertyType.text
        
    def test_create_with_all_attributes(self):
        """Test creating a property with all attributes."""
        options = HALFormsOptions(inline=["Option 1", "Option 2"])
        prop = HALFormsProperty(
            name="test",
            type=HALFormsPropertyType.text,
            prompt="Test Property",
            readOnly=False,
            regex="^[a-z]+$",
            required=True,
            templated=False,
            value="default",
            cols=40,
            max=100,
            maxLength=50,
            min=0,
            minLength=3,
            options=options,
            placeholder="Enter text",
            rows=5,
            step=1
        )
        
        assert prop.name == "test"
        assert prop.type == HALFormsPropertyType.text
        assert prop.prompt == "Test Property"
        assert prop.readOnly is False
        assert prop.regex == "^[a-z]+$"
        assert prop.required is True
        assert prop.templated is False
        assert prop.value == "default"
        assert prop.cols == 40
        assert prop.max == 100
        assert prop.maxLength == 50
        assert prop.min == 0
        assert prop.minLength == 3
        assert prop.options == options
        assert prop.placeholder == "Enter text"
        assert prop.rows == 5
        assert prop.step == 1
        
    def test_serialize(self):
        """Test serializing a property."""
        options = HALFormsOptions(inline=["Option 1", "Option 2"])
        prop = HALFormsProperty(
            name="test",
            type=HALFormsPropertyType.text,
            prompt="Test Property",
            required=True,
            options=options
        )
        
        serialized = prop.model_dump()
        assert serialized["name"] == "test"
        assert serialized["type"] == "text"
        assert serialized["prompt"] == "Test Property"
        assert serialized["required"] is True
        assert "options" in serialized
        assert serialized["options"]["inline"] == ["Option 1", "Option 2"]
        
    def test_deserialize_minimal(self):
        """Test deserializing a minimal property."""
        data = {"name": "test"}
        prop = HALFormsProperty(**data)
        assert prop.name == "test"
        assert prop.type == HALFormsPropertyType.text  # Default type is text
        assert prop.prompt is None
        assert prop.required is None
        assert prop.options is None
        
    def test_deserialize_complete(self):
        """Test deserializing a complete property."""
        data = {
            "name": "test",
            "type": "select",
            "prompt": "Test Property",
            "readOnly": False,
            "regex": "^[a-z]+$",
            "required": True,
            "templated": False,
            "value": "default",
            "cols": 40,
            "max": 100,
            "maxLength": 50,
            "min": 0,
            "minLength": 3,
            "options": {
                "inline": ["Option 1", "Option 2"],
                "maxItems": 1
            },
            "placeholder": "Enter text",
            "rows": 5,
            "step": 1
        }
        
        prop = HALFormsProperty(**data)
        
        assert prop.name == "test"
        assert prop.type == HALFormsPropertyType.select
        assert prop.prompt == "Test Property"
        assert prop.readOnly is False
        assert prop.regex == "^[a-z]+$"
        assert prop.required is True
        assert prop.templated is False
        assert prop.value == "default"
        assert prop.cols == 40
        assert prop.max == 100
        assert prop.maxLength == 50
        assert prop.min == 0
        assert prop.minLength == 3
        assert prop.options is not None
        assert len(prop.options.inline) == 2
        assert prop.options.inline[1].value == "Option 2"
        assert prop.placeholder == "Enter text"
        assert prop.rows == 5
        assert prop.step == 1
        
    def test_deserialize_with_invalid_type(self):
        """Test deserializing a property with an invalid type."""
        data = {
            "name": "test",
            "type": "invalid_type"
        }
        
        prop = HALFormsProperty(**data)
        assert prop.name == "test"
        assert prop.type == HALFormsPropertyType.text  # Should default to text


class TestHALFormsTemplate:
    def test_create_minimal(self):
        """Test creating a template with minimal attributes."""
        template = HALFormsTemplate(method=HALFormsMethod.GET)
        assert template.method == HALFormsMethod.GET
        assert template.contentType == "application/json"
        assert template.properties == []
        assert template.target is None
        assert template.title is None
        
    def test_create_complete(self):
        """Test creating a template with all attributes."""
        properties = [
            HALFormsProperty(name="prop1", type=HALFormsPropertyType.text),
            HALFormsProperty(name="prop2", type=HALFormsPropertyType.number)
        ]
        
        template = HALFormsTemplate(
            method=HALFormsMethod.POST,
            contentType="application/x-www-form-urlencoded",
            properties=properties,
            target="http://api.example.org/submit",
            title="Test Template"
        )
        
        assert template.method == HALFormsMethod.POST
        assert template.contentType == "application/x-www-form-urlencoded"
        assert len(template.properties) == 2
        assert template.target == "http://api.example.org/submit"
        assert template.title == "Test Template"
        
    def test_serialize_minimal(self):
        """Test serializing a minimal template."""
        template = HALFormsTemplate(method=HALFormsMethod.GET)
        serialized = template.model_dump(exclude_unset=True)
        
        assert serialized["method"] == "GET"
        assert "target" not in serialized
        assert "title" not in serialized
        
    def test_serialize_complete(self):
        """Test serializing a complete template."""
        properties = [
            HALFormsProperty(name="prop1", type=HALFormsPropertyType.text),
            HALFormsProperty(name="prop2", type=HALFormsPropertyType.number, options=HALFormsOptions(
                inline=["Option 1", "Option 2"]
            ))
        ]
        
        template = HALFormsTemplate(
            method=HALFormsMethod.POST,
            contentType="application/x-www-form-urlencoded",
            properties=properties,
            target="http://api.example.org/submit",
            title="Test Template"
        )
        
        serialized = template.model_dump()
        
        assert serialized["method"] == "POST"
        assert serialized["contentType"] == "application/x-www-form-urlencoded"
        assert len(serialized["properties"]) == 2
        assert serialized["properties"][0]["name"] == "prop1"
        assert serialized["properties"][1]["name"] == "prop2"
        assert "options" in serialized["properties"][1]
        assert serialized["target"] == "http://api.example.org/submit"
        assert serialized["title"] == "Test Template"
        
    def test_deserialize_minimal(self):
        """Test deserializing a minimal template."""
        data = {
            "method": "GET"
        }
        
        template = HALFormsTemplate(**data)
        
        assert template.method == HALFormsMethod.GET
        assert template.contentType == "application/json"
        assert template.properties == []
        assert template.target is None
        assert template.title is None
        
    def test_deserialize_complete(self):
        """Test deserializing a complete template."""
        data = {
            "method": "POST",
            "contentType": "application/x-www-form-urlencoded",
            "properties": [
                {
                    "name": "prop1",
                    "type": "text"
                },
                {
                    "name": "prop2",
                    "type": "number",
                    "options": {
                        "inline": ["Option 1", "Option 2"]
                    }
                }
            ],
            "target": "http://api.example.org/submit",
            "title": "Test Template"
        }
        
        template = HALFormsTemplate(**data)
        
        assert template.method == HALFormsMethod.POST
        assert template.contentType == "application/x-www-form-urlencoded"
        assert len(template.properties) == 2
        assert template.properties[0].name == "prop1"
        assert template.properties[1].name == "prop2"
        assert template.properties[1].options is not None
        assert template.target == "http://api.example.org/submit"
        assert template.title == "Test Template"
        
    def test_deserialize_with_options_link(self):
        """Test deserialization with options link."""
        data = {
            "method": "GET",
            "properties": [
                {
                    "name": "category",
                    "type": "select",
                    "options": {
                        "link": {
                            "href": "http://api.example.org/categories",
                            "templated": False,
                            "type": "application/json"
                        }
                    }
                }
            ]
        }
        
        template = HALFormsTemplate(**data)
        
        assert template.method == HALFormsMethod.GET
        assert len(template.properties) == 1
        assert template.properties[0].name == "category"
        assert template.properties[0].type == HALFormsPropertyType.select
        assert template.properties[0].options is not None
        assert template.properties[0].options.link is not None
        assert template.properties[0].options.link.href == "http://api.example.org/categories"
        assert template.properties[0].options.link.templated is False
        assert template.properties[0].options.link.type == "application/json"
    
    def test_deserialize_with_templated_options_link(self):
        """Test deserialization with templated options link."""
        data = {
            "method": "GET",
            "properties": [
                {
                    "name": "item",
                    "type": "select",
                    "options": {
                        "link": {
                            "href": "http://api.example.org/items/{category}",
                            "templated": True
                        }
                    }
                }
            ]
        }
        
        template = HALFormsTemplate(**data)
        
        assert template.method == HALFormsMethod.GET
        assert len(template.properties) == 1
        assert template.properties[0].name == "item"
        assert template.properties[0].type == HALFormsPropertyType.select
        assert template.properties[0].options is not None
        assert template.properties[0].options.link is not None
        assert template.properties[0].options.link.href == "http://api.example.org/items/{category}"
        assert template.properties[0].options.link.templated is True
        
        # Test template expansion
        expanded_url = template.properties[0].options.link.expand_template(category="books")
        assert expanded_url == "http://api.example.org/items/books"
    
    def test_deserialize_with_complex_inline_options(self):
        """Test deserialization with complex inline options (objects with prompt/value pairs)."""
        data = {
            "method": "POST",
            "properties": [
                {
                    "name": "status",
                    "type": "select",
                    "options": {
                        "inline": [
                            {"prompt": "Active", "value": "active"},
                            {"prompt": "Pending", "value": "pending"},
                            {"prompt": "Closed", "value": "closed", "description": "No longer available"}
                        ],
                        "selectedValues": ["active"]
                    }
                }
            ]
        }
        
        template = HALFormsTemplate(**data)
        
        assert template.method == HALFormsMethod.POST
        assert len(template.properties) == 1
        assert template.properties[0].name == "status"
        assert template.properties[0].type == HALFormsPropertyType.select
        assert template.properties[0].options is not None
        
        # Check inline options
        assert len(template.properties[0].options.inline) == 3
        assert template.properties[0].options.inline[0].prompt == "Active"
        assert template.properties[0].options.inline[0].value == "active"
        assert template.properties[0].options.inline[1].prompt == "Pending"
        assert template.properties[0].options.inline[1].value == "pending"
        assert template.properties[0].options.inline[2].prompt == "Closed"
        assert template.properties[0].options.inline[2].value == "closed"
        assert template.properties[0].options.inline[2].description == "No longer available"
        
        # Check selected values
        assert template.properties[0].options.selectedValues == ["active"]
    
    def test_deserialize_with_mixed_inline_options(self):
        """Test deserialization with mixed inline options (strings and objects)."""
        data = {
            "method": "PUT",
            "properties": [
                {
                    "name": "priority",
                    "type": "select",
                    "options": {
                        "inline": [
                            "low",
                            {"prompt": "Medium Priority", "value": "medium"},
                            "high"
                        ]
                    }
                }
            ]
        }
        
        template = HALFormsTemplate(**data)
        
        assert template.method == HALFormsMethod.PUT
        assert len(template.properties) == 1
        assert template.properties[0].name == "priority"
        assert template.properties[0].type == HALFormsPropertyType.select
        assert template.properties[0].options is not None
        
        # Check inline options
        assert len(template.properties[0].options.inline) == 3
        assert template.properties[0].options.inline[0].value == "low"
        assert template.properties[0].options.inline[0].prompt == "low"  # Same as value for string items
        assert template.properties[0].options.inline[1].value == "medium"
        assert template.properties[0].options.inline[1].prompt == "Medium Priority"
        assert template.properties[0].options.inline[2].value == "high"
        assert template.properties[0].options.inline[2].prompt == "high"
    
    def test_deserialize_with_options_configuration(self):
        """Test deserialization with options configuration parameters."""
        data = {
            "method": "POST",
            "properties": [
                {
                    "name": "tags",
                    "type": "select",
                    "options": {
                        "inline": ["tag1", "tag2", "tag3", "tag4"],
                        "minItems": 1,
                        "maxItems": 3,
                        "promptField": "label",
                        "valueField": "id"
                    }
                }
            ]
        }
        
        template = HALFormsTemplate(**data)
        
        assert template.method == HALFormsMethod.POST
        assert len(template.properties) == 1
        assert template.properties[0].name == "tags"
        assert template.properties[0].type == HALFormsPropertyType.select
        assert template.properties[0].options is not None
        
        # Check options configuration
        assert template.properties[0].options.minItems == 1
        assert template.properties[0].options.maxItems == 3
        assert template.properties[0].options.promptField == "label"
        assert template.properties[0].options.valueField == "id"
        assert len(template.properties[0].options.inline) == 4
    
    def test_deserialize_with_property_validation_attributes(self):
        """Test deserialization with property validation attributes."""
        data = {
            "method": "POST",
            "properties": [
                {
                    "name": "username",
                    "type": "text",
                    "required": True,
                    "minLength": 3,
                    "maxLength": 20,
                    "regex": "^[a-zA-Z0-9_]+$",
                    "placeholder": "Enter username"
                },
                {
                    "name": "age",
                    "type": "number",
                    "min": 18,
                    "max": 100,
                    "step": 1
                }
            ]
        }
        
        template = HALFormsTemplate(**data)
        
        assert template.method == HALFormsMethod.POST
        assert len(template.properties) == 2
        
        # Check first property validation attributes
        assert template.properties[0].name == "username"
        assert template.properties[0].type == HALFormsPropertyType.text
        assert template.properties[0].required is True
        assert template.properties[0].minLength == 3
        assert template.properties[0].maxLength == 20
        assert template.properties[0].regex == "^[a-zA-Z0-9_]+$"
        assert template.properties[0].placeholder == "Enter username"
        
        # Check second property validation attributes
        assert template.properties[1].name == "age"
        assert template.properties[1].type == HALFormsPropertyType.number
        assert template.properties[1].min == 18
        assert template.properties[1].max == 100
        assert template.properties[1].step == 1
    
    def test_deserialize_with_textarea_attributes(self):
        """Test deserialization with textarea-specific attributes."""
        data = {
            "method": "POST",
            "properties": [
                {
                    "name": "description",
                    "type": "textarea",
                    "rows": 5,
                    "cols": 40,
                    "value": "Default description"
                }
            ]
        }
        
        template = HALFormsTemplate(**data)
        
        assert template.method == HALFormsMethod.POST
        assert len(template.properties) == 1
        assert template.properties[0].name == "description"
        assert template.properties[0].type == HALFormsPropertyType.textarea
        assert template.properties[0].rows == 5
        assert template.properties[0].cols == 40
        assert template.properties[0].value == "Default description"
    
    def test_deserialize_with_multiple_property_types(self):
        """Test deserialization with multiple property types."""
        data = {
            "method": "POST",
            "properties": [
                {"name": "title", "type": "text"},
                {"name": "description", "type": "textarea"},
                {"name": "category", "type": "select"},
                {"name": "priority", "type": "range", "min": 1, "max": 5},
                {"name": "dueDate", "type": "date"},
                {"name": "notify", "type": "checkbox"},
                {"name": "color", "type": "color"},
                {"name": "attachment", "type": "file"}
            ]
        }
        
        template = HALFormsTemplate(**data)
        
        assert template.method == HALFormsMethod.POST
        assert len(template.properties) == 8
        
        # Check property types
        assert template.properties[0].type == HALFormsPropertyType.text
        assert template.properties[1].type == HALFormsPropertyType.textarea
        assert template.properties[2].type == HALFormsPropertyType.select
        assert template.properties[3].type == HALFormsPropertyType.range
        assert template.properties[4].type == HALFormsPropertyType.date
        assert template.properties[5].type == HALFormsPropertyType.checkbox
        assert template.properties[6].type == HALFormsPropertyType.color
        assert template.properties[7].type == HALFormsPropertyType.file


class TestIntegration:
    def test_full_hal_forms_document(self):
        """Test a complete HAL-FORMS document serialization and deserialization."""
        # Create a complete HAL-FORMS document
        options = HALFormsOptions(
            inline=[
                HALFormsOptionsValueItem(value="true", prompt="Yes"),
                HALFormsOptionsValueItem(value="false", prompt="No")
            ],
            selectedValues=["false"]
        )
        
        properties = [
            HALFormsProperty(
                name="title", 
                type=HALFormsPropertyType.text,
                prompt="Title",
                required=True,
                value=""
            ),
            HALFormsProperty(
                name="completed",
                type=HALFormsPropertyType.checkbox,
                prompt="Completed",
                required=False,
                value="false",
                options=options
            )
        ]
        
        template = HALFormsTemplate(
            method=HALFormsMethod.POST,
            contentType="application/json",
            properties=properties,
            title="Create"
        )
        
        # Serialize the template
        serialized = template.model_dump()
        
        # Verify the serialized document
        assert serialized["method"] == "POST"
        assert serialized["contentType"] == "application/json"
        assert serialized["title"] == "Create"
        assert len(serialized["properties"]) == 2
        
        # Verify the first property
        assert serialized["properties"][0]["name"] == "title"
        assert serialized["properties"][0]["type"] == "text"
        assert serialized["properties"][0]["prompt"] == "Title"
        assert serialized["properties"][0]["required"] is True
        assert serialized["properties"][0]["value"] == ""
        
        # Verify the second property
        assert serialized["properties"][1]["name"] == "completed"
        assert serialized["properties"][1]["type"] == "checkbox"
        assert serialized["properties"][1]["prompt"] == "Completed"
        assert serialized["properties"][1]["required"] is False
        assert serialized["properties"][1]["value"] == "false"
        
        # Verify the options in the second property
        assert "options" in serialized["properties"][1]
        assert "inline" in serialized["properties"][1]["options"]
        assert len(serialized["properties"][1]["options"]["inline"]) == 2
        assert serialized["properties"][1]["options"]["selectedValues"] == ["false"]
        
        # Deserialize back to a template
        deserialized = HALFormsTemplate(**serialized)
        
        # Verify the deserialized template
        assert deserialized.method == HALFormsMethod.POST
        assert deserialized.contentType == "application/json"
        assert deserialized.title == "Create"
        assert len(deserialized.properties) == 2
        
        # Verify the first property
        assert deserialized.properties[0].name == "title"
        assert deserialized.properties[0].type == HALFormsPropertyType.text
        assert deserialized.properties[0].prompt == "Title"
        assert deserialized.properties[0].required is True
        assert deserialized.properties[0].value == ""
        
        # Verify the second property
        assert deserialized.properties[1].name == "completed"
        assert deserialized.properties[1].type == HALFormsPropertyType.checkbox
        assert deserialized.properties[1].prompt == "Completed"
        assert deserialized.properties[1].required is False
        assert deserialized.properties[1].value == "false"
        
        # Verify the options in the second property
        assert deserialized.properties[1].options is not None
        assert len(deserialized.properties[1].options.inline) == 2
        assert deserialized.properties[1].options.selectedValues == ["false"]
        
    def test_options_link_expansion(self):
        """Test expanding a templated options link."""
        # Create an options object with a templated link
        link = HALFormsOptionsLink(
            href="http://api.example.org/options/{category}/{id}",
            templated=True
        )
        
        options = HALFormsOptions(link=link)
        
        # Create a property with the options
        prop = HALFormsProperty(
            name="item",
            type=HALFormsPropertyType.select,
            options=options
        )
        
        # Serialize the property
        serialized = prop.model_dump()
        
        # Verify the serialized property
        assert serialized["name"] == "item"
        assert serialized["type"] == "select"
        assert "options" in serialized
        assert "link" in serialized["options"]
        assert serialized["options"]["link"]["href"] == "http://api.example.org/options/{category}/{id}"
        assert serialized["options"]["link"]["templated"] is True
        
        # Deserialize back to a property
        deserialized = HALFormsProperty(**serialized)
        
        # Verify the deserialized property
        assert deserialized.name == "item"
        assert deserialized.type == HALFormsPropertyType.select
        assert deserialized.options is not None
        assert deserialized.options.link is not None
        assert deserialized.options.link.href == "http://api.example.org/options/{category}/{id}"
        assert deserialized.options.link.templated is True
        
        # Expand the template
        expanded = deserialized.options.link.expand_template(category="products", id="123")
        assert expanded == "http://api.example.org/options/products/123"


class TestHALFormsExamples:
    """Test examples from the HAL-FORMS specification."""
    
    def test_simple_hal_forms_document(self):
        """Test the simple HAL-FORMS document example from the spec."""
        # Create the document as described in the spec
        properties = [
            HALFormsProperty(
                name="title", 
                required=True, 
                value="", 
                prompt="Title", 
                regex="", 
                templated=False
            ),
            HALFormsProperty(
                name="completed", 
                required=False, 
                value="false", 
                prompt="Completed", 
                regex=""
            )
        ]
        
        template = HALFormsTemplate(
            method=HALFormsMethod.POST,
            contentType="application/json",
            properties=properties,
            title="Create"
        )
        
        # Serialize the template
        serialized = template.model_dump()
        
        # Verify it matches the expected structure
        assert serialized["title"] == "Create"
        assert serialized["method"] == "POST"
        assert serialized["contentType"] == "application/json"
        assert len(serialized["properties"]) == 2
        
        # Check first property
        assert serialized["properties"][0]["name"] == "title"
        assert serialized["properties"][0]["required"] is True
        assert serialized["properties"][0]["value"] == ""
        assert serialized["properties"][0]["prompt"] == "Title"
        
        # Check second property
        assert serialized["properties"][1]["name"] == "completed"
        assert serialized["properties"][1]["required"] is False
        assert serialized["properties"][1]["value"] == "false"
        assert serialized["properties"][1]["prompt"] == "Completed"
        
    def test_options_inline_array_of_values(self):
        """Test the simple inline array of values example from the spec."""
        # Create options with inline values
        options = HALFormsOptions(
            inline=["FedEx", "UPS", "DHL"],
            selectedValues=["FedEx"]
        )
        
        # Create property with options
        prop = HALFormsProperty(
            name="shipping",
            prompt="Select Shipping Method",
            options=options
        )
        
        # Serialize the property
        serialized = prop.model_dump()
        
        # Verify it matches the expected structure
        assert serialized["name"] == "shipping"
        assert serialized["prompt"] == "Select Shipping Method"
        assert "options" in serialized
        assert "inline" in serialized["options"]
        assert serialized["options"]["inline"] == ["FedEx", "UPS", "DHL"]
        assert serialized["options"]["selectedValues"] == ["FedEx"]
        