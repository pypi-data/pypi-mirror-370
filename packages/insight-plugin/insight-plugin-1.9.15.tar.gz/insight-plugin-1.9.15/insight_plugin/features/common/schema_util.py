from typing import Tuple, Dict, Union, Any
from insight_plugin.features.common.plugin_spec_util import PluginSpecConstants
from insight_plugin.features.common.exceptions import InsightException
from insight_plugin.features.common.logging_util import BaseLoggingFeature


class SchemaConstants:
    """
    Constants that are part of the JSON schema specification
    Documentation: https://json-schema.org/understanding-json-schema/
    """

    ARRAY = "array"
    TYPE = "type"
    TYPE_ARRAY = "[]"
    ITEMS = "items"
    TITLE = "title"
    ORDER = "order"
    PROPERTIES = "properties"
    REF = "$ref"
    DEFAULT = "default"
    REQUIRED = "required"
    DEFINITIONS = "definitions"
    REF_DEF = "#/definitions/"


class SchemaUtil:
    # Primitive types are the basic building blocks with which all other types must be constructed.
    PRIMITIVE_TYPES = {
        "boolean": "boolean",
        "bool": "boolean",  # not technically in the spec but here for backwards compatibility
        "integer": "integer",
        "number": "number",  # not technically in the spec but here for backwards compatibility
        "int": "integer",
        "float": "number",
        "string": "string",
        "date": {"type": "string", "format": "date-time", "displayType": "date"},
        "bytes": {"type": "string", "format": "bytes", "displayType": "bytes"},
        "object": "object",
    }
    # Base types are hardcoded custom type definitions
    # that are universally usable like primitive types as part of the plugin runtime.
    # Documentation for base AND primitive types: https://docs.rapid7.com/insightconnect/plugin-spec#base-types
    BASE_TYPES = {
        "file": {
            "id": "file",
            "type": "object",
            "title": "File",
            "description": "File Object",
            "properties": {
                "filename": {
                    "type": "string",
                    "title": "Filename",
                    "description": "Name of file",
                },
                "content": {
                    "type": "string",
                    "format": "bytes",
                    "title": "Content",
                    "description": "File contents",
                },
            },
        },
        "password": {
            "type": "string",
            "format": "password",
            "displayType": "password",
        },
        "python": {"type": "string", "format": "python", "displayType": "python"},
        "credential_username_password": {
            "id": "credential_username_password",
            "title": "Credential: Username and Password",
            "description": "A username and password combination",
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "title": "Username",
                    "description": "The username to log in with",
                    "order": 1,
                },
                "password": {
                    "type": "string",
                    "title": "Password",
                    "description": "The password",
                    "format": "password",
                    "displayType": "password",
                    "order": 2,
                },
            },
            "required": ["username", "password"],
        },
        "credential_asymmetric_key": {
            "id": "credential_asymmetric_key",
            "type": "object",
            "title": "Credential: Asymmetric key",
            "description": "A shared key",
            "required": ["privateKey"],
            "properties": {
                "privateKey": {
                    "type": "string",
                    "title": "Private Key",
                    "description": "The private key",
                    "format": "password",
                    "displayType": "password",
                }
            },
        },
        "credential_token": {
            "id": "credential_token",
            "type": "object",
            "title": "Credential: Token",
            "description": "A pair of a token, and an optional domain",
            "required": ["token"],
            "properties": {
                "domain": {
                    "type": "string",
                    "title": "Domain",
                    "description": "The domain for the token",
                    "order": 1,
                },
                "token": {
                    "type": "string",
                    "title": "Token",
                    "description": "The shared token",
                    "format": "password",
                    "displayType": "password",
                    "order": 2,
                },
            },
        },
        "credential_secret_key": {
            "id": "credential_secret_key",
            "type": "object",
            "title": "Credential: Secret Key",
            "description": "A shared secret key",
            "required": ["secretKey"],
            "properties": {
                "secretKey": {
                    "type": "string",
                    "title": "Secret Key",
                    "description": "The shared secret key",
                    "format": "password",
                    "displayType": "password",
                }
            },
        },
    }

    @staticmethod
    def generate_json_schema(section: dict, spec: dict, task: bool = False) -> dict:
        """
        Build this section of the schema (input or output), just the dictionary.
        Inner functions will complete the specified wrapping headers / templating as needed.
        """
        if section is None or len(section) == 0:
            return {}
        built_schema = SchemaUtil.build_inner(section, spec, task)
        return built_schema

    @staticmethod
    def build_inner(input_output_spec: dict, spec: dict, task: bool) -> dict:
        """
        Create a JSON schema object complete with headers and required / definitions sections.
        Initiates the build method on the properties section that may contain recursive type definitions.
        :param task:
        :param input_output_spec: Either the input or output subset spec of a plugin component (e.g. trigger or task)
        :param spec: The plugin spec dictionary
        :return: JSON schema object with complete custom type definitions and required parameters, alphabetically sorted
        """
        outer_object = {
            PluginSpecConstants.TYPE: "object",
            PluginSpecConstants.TITLE: "Variables",
            SchemaConstants.PROPERTIES: {},
            SchemaConstants.REQUIRED: [],
            SchemaConstants.DEFINITIONS: {},
        }
        properties, required = SchemaUtil.recurse_build(
            input_output_spec,
            outer_object[SchemaConstants.PROPERTIES],
            outer_object[SchemaConstants.DEFINITIONS],
            spec,
        )

        if not task:
            outer_object[SchemaConstants.PROPERTIES] = properties
        else:
            outer_object = SchemaUtil._build_task_schema(outer_object, properties)

        # The recursive method returned properties with complete definitions, array formatting, and sort order
        if len(required) > 0:
            outer_object[SchemaConstants.REQUIRED] = required
        else:
            del outer_object[SchemaConstants.REQUIRED]
        return outer_object

    @staticmethod
    def _build_task_schema(
        outer_object: Dict[str, Union[str, Dict[str, Any], list]],
        properties: Dict[str, Dict[str, Union[str, int, Dict[str, Any]]]],
    ):
        """
        A helper function to build the schema for tasks output.

        :param outer_object: The outer object dict to be inserted into the schema.
        :type: Dict[str, Union[str, Dict[str, Any], list]]

        :param properties: The built out properties dict.
        :type: Dict[str, Dict[str, Union[str, int, Dict[str, Any]]]]

        :return:
        """
        PROPERTIES = "properties"

        first_key = list(properties.keys())[0]
        # Fill in all the details we need for successful task obj
        outer_object[SchemaConstants.TYPE] = SchemaConstants.ARRAY
        outer_object[SchemaConstants.TITLE] = properties.get(first_key, {}).get(
            "title", {}
        )
        outer_object[PluginSpecConstants.DESCRIPTION] = properties.get(
            first_key, {}
        ).get("description", {})
        items = {}
        outer_object[PluginSpecConstants.ITEMS] = items

        # We remove then add these 2 fields to move them to the back of the object since dict are sorted
        # by insertion order.
        outer_object[SchemaConstants.REQUIRED] = outer_object.pop(
            SchemaConstants.REQUIRED
        )

        outer_object[SchemaConstants.DEFINITIONS] = outer_object.pop(
            SchemaConstants.DEFINITIONS
        )

        # Delete the properties field
        if PROPERTIES in outer_object:
            del outer_object[PROPERTIES]

        return outer_object

    # Until this method is broken up, we need to ignore Pylint warnings about excessive statements and branches.
    # pylint: disable=too-many-statements,too-many-branches
    @staticmethod  # noqa: MC0001
    def recurse_build(
        current_section: dict, parent_object: dict, definitions: dict, spec
    ) -> Tuple[dict, list]:
        """
        Build the properties section of the JSON schema object. This method may recurse on custom type definitions
        that contain their own properties sections.
        :param current_section: Dict to be parsed into JSON schema, may be plugin spec subset, or custom type spec dict
        :param parent_object: Recursively built JSON schema object, may be properties section, or custom type definition
        :param definitions: Recursively built custom type definitions object
        :param spec: The plugin spec dictionary
        :return: A JSON schema properties section with complete custom type definitions, and list of required parameters
        """
        # Using a logger here because it's a tough function and could use some help from env.
        logger_ = BaseLoggingFeature("SchemaBuilder")
        logger_ = logger_.logger
        order = 1
        required = []
        # At the top recursion level, key is the name of each property and items is that property's definition.
        # In recursion, key is the ID of each parameter of a custom type, and items is that parameter's definition.
        for key, items in current_section.items():
            parent_object[key] = {}
            current_type = None
            # If this parameter is an array, it will have an items object to define the array contents.
            # In this loop, we will build the items object before we should assign it to the schema in the key sequence.
            # We use this variable to store the items map after defining it but before adding it to the parent_object.
            # current_items must be initialized with the items key to remain compatible with the try_add() method.
            array_items = {SchemaConstants.ITEMS: {}}
            try:
                # We require that each property has a type value.
                current_type = items[PluginSpecConstants.TYPE]
            except KeyError:
                raise InsightException(
                    message=f"No type in {key}",
                    troubleshooting=f'Please add "type" to {key} in plugin.spec.yaml',
                )
            # If this property is a primitive type, then we do not need to add it to the definitions section.
            if current_type in SchemaUtil.PRIMITIVE_TYPES:
                # Primitive type definitions are only either strings or dicts.
                if isinstance(SchemaUtil.PRIMITIVE_TYPES[current_type], str):
                    # If this type definition is a string, we simply assign the value to the type property.
                    parent_object[key][
                        PluginSpecConstants.TYPE
                    ] = SchemaUtil.PRIMITIVE_TYPES[current_type]
                # This parameter's primitive type is one defined as a dict object with multiple properties.
                elif isinstance(SchemaUtil.PRIMITIVE_TYPES[current_type], dict):
                    # Add each property of this primitive type's dict definition to the current parameter schema.
                    for primitive_key in SchemaUtil.PRIMITIVE_TYPES[current_type]:
                        # Dict-defined primitive type properties have primitive_keys type, displayType, and format.
                        parent_object[key][primitive_key] = SchemaUtil.PRIMITIVE_TYPES[
                            current_type
                        ][primitive_key]
            # Base types are non-primitive, so we must define them, but their definitions are statically specified.
            elif current_type in SchemaUtil.BASE_TYPES:
                # Add a type definition reference instead of a type string.
                parent_object[key][
                    SchemaConstants.REF
                ] = f"{SchemaConstants.REF_DEF}{current_type}"
                # Have we not yet added this base type definition to this schema?
                if current_type not in definitions:
                    # We have not yet added this base type definition, we get its static definition now.
                    definitions[current_type] = SchemaUtil.BASE_TYPES[current_type]
            # This key may be a custom type or an array. Check that this type is defined in the original plugin spec.
            elif (
                PluginSpecConstants.TYPES in spec
                and current_type in spec[PluginSpecConstants.TYPES]
            ):
                # The current key is a custom type.
                # Add a type definition reference instead of a type string.
                parent_object[key][
                    SchemaConstants.REF
                ] = f"{SchemaConstants.REF_DEF}{current_type}"
                # Have we not yet added this custom type definition to the schema?
                if current_type not in definitions:
                    # We have not yet defined this custom type, prepare to recurse.
                    # Instantiate the nested schema with attributes like those set at the top level in build_inner().
                    # Custom type definitions are objects which all start with type = "object" and title set to its name
                    definitions[current_type] = {}
                    definitions[current_type][SchemaConstants.TYPE] = "object"
                    definitions[current_type][SchemaConstants.TITLE] = current_type
                    definitions[current_type][SchemaConstants.PROPERTIES] = {}
                    # The parent in this recurse is the properties object of the current custom type's definition.
                    new_parent = definitions[current_type][SchemaConstants.PROPERTIES]
                    # Recurse with the current_section scope narrowed to the current type definition spec
                    _, new_parent_required = SchemaUtil.recurse_build(
                        spec[PluginSpecConstants.TYPES][current_type],
                        new_parent,
                        definitions,
                        spec,
                    )
                    # Bubble up required parameters found in recurse to the top level list we ultimately return.
                    if len(new_parent_required) > 0:
                        definitions[current_type][
                            SchemaConstants.REQUIRED
                        ] = new_parent_required
            # In the case that this type is an array of another type:
            # must have at least 1 character of the type after the brackets (hence the +1 below)
            elif len(current_type) >= len(
                SchemaConstants.TYPE_ARRAY
            ) + 1 and current_type.startswith(SchemaConstants.TYPE_ARRAY):
                # The current key is an array.
                # Set the type string to array.
                parent_object[key][PluginSpecConstants.TYPE] = SchemaConstants.ARRAY
                # Set a convenience variable for this array items type definition
                current_item = array_items[SchemaConstants.ITEMS]
                # Remove the [] array indicator and extract the parameter array contents type.
                final_type = current_type[len(SchemaConstants.TYPE_ARRAY) :]
                # Is this parameter an array of a primitive type?
                if final_type in SchemaUtil.PRIMITIVE_TYPES:
                    # Is this an array of strings?
                    if isinstance(SchemaUtil.PRIMITIVE_TYPES[final_type], str):
                        # Set this array's items: type value to string.
                        current_item[
                            PluginSpecConstants.TYPE
                        ] = SchemaUtil.PRIMITIVE_TYPES[final_type]
                    # Is this an array of dict objects?
                    elif isinstance(SchemaUtil.PRIMITIVE_TYPES[final_type], dict):
                        for primitive_key in SchemaUtil.PRIMITIVE_TYPES[final_type]:
                            current_item[primitive_key] = SchemaUtil.PRIMITIVE_TYPES[
                                final_type
                            ][primitive_key]
                # Is this parameter an array of a base type?
                elif final_type in SchemaUtil.BASE_TYPES:
                    # Non-primitive types use $ref instead of type, here we set the definition reference.
                    current_item[
                        SchemaConstants.REF
                    ] = f"{SchemaConstants.REF_DEF}{final_type}"
                    # Non-primitive types must be defined in the schema, here we get this base type definition.
                    if final_type not in definitions:
                        definitions[final_type] = SchemaUtil.BASE_TYPES[final_type]
                # Is this parameter an array of a custom type defined in the plugin spec?
                elif (
                    PluginSpecConstants.TYPES in spec
                    and final_type in spec[PluginSpecConstants.TYPES]
                ):
                    # Non-primitive types use $ref instead of type, here we set the definition reference.
                    current_item[
                        SchemaConstants.REF
                    ] = f"{SchemaConstants.REF_DEF}{final_type}"
                    # Have we not yet added this custom type definition to the schema?
                    if final_type not in definitions:
                        # We have not yet defined this custom type, prepare to recurse.
                        # Instantiate the nested schema with attributes like those set at the top level in build_inner()
                        # Custom type definitions are objects which all start with type = "object" and title = its name
                        definitions[final_type] = {}
                        definitions[final_type][SchemaConstants.TYPE] = "object"
                        definitions[final_type][SchemaConstants.TITLE] = final_type
                        definitions[final_type][SchemaConstants.PROPERTIES] = {}
                        # The parent in this recurse is the properties object of the current custom type's definition.
                        new_parent = definitions[final_type][SchemaConstants.PROPERTIES]
                        # Recurse with the current_section scope narrowed to the current custom type definition spec
                        _, new_parent_required = SchemaUtil.recurse_build(
                            spec[PluginSpecConstants.TYPES][final_type],
                            new_parent,
                            definitions,
                            spec,
                        )
                        # Bubble up required parameters found in recurse to the top level list we ultimately return.
                        if len(new_parent_required) > 0:
                            definitions[final_type][
                                SchemaConstants.REQUIRED
                            ] = new_parent_required
                else:
                    # This type of array is not defined.
                    # Is this a legacy array type setting that we no longer support?
                    if final_type in ("array", " tag"):
                        # TODO: REMOVE THESE IF TECH DEBT TICKETS CLOSED
                        logger_.warning(
                            f"Invalid type {final_type} in the plugin.spec.yaml within {items}"
                        )
                    # Is this a matrix/multidimensional array that the platform does not support?
                    elif len(final_type) >= len(
                        SchemaConstants.TYPE_ARRAY
                    ) and final_type.startswith(SchemaConstants.TYPE_ARRAY):
                        logger_.warning(
                            "Nested types currently not fully supported in InsightConnect product"
                        )
                    # This array type is simply invalid.
                    else:
                        raise InsightException(
                            message=f"Invalid array type in plugin.spec.yaml file within {items}",
                            troubleshooting="Type must be one of the types listed at "
                            "https://docs.rapid7.com/insightconnect/plugin-spec/#base-types"
                            " or a defined custom type",
                        )
            # The order in which parameter properties are added is fixed in this sequence.
            # Set the current parameter title if one exists.
            SchemaUtil.try_add(PluginSpecConstants.TITLE, items, parent_object[key])
            # Set the current parameter description if one exists.
            SchemaUtil.try_add(
                PluginSpecConstants.DESCRIPTION, items, parent_object[key]
            )
            # Set the current parameter default if one exists.
            SchemaUtil.try_add(PluginSpecConstants.DEFAULT, items, parent_object[key])
            # Set placeholder
            SchemaUtil.try_add(
                PluginSpecConstants.PLACEHOLDER, items, parent_object[key]
            )
            # Set tooltip
            SchemaUtil.try_add(PluginSpecConstants.TOOLTIP, items, parent_object[key])
            # If the current parameter is an array (it has items contents), set the items object dict.
            if array_items[SchemaConstants.ITEMS]:
                SchemaUtil.try_add(
                    SchemaConstants.ITEMS, array_items, parent_object[key]
                )
            # Set the current parameter enums if a list of strings exists.
            SchemaUtil.try_add(PluginSpecConstants.ENUM, items, parent_object[key])
            # Set the current parameter order as it appears in current_section.
            parent_object[key][SchemaConstants.ORDER] = order
            order += 1
            # Add this parameter to the required list if required is true.
            if (
                PluginSpecConstants.REQUIRED in items
                and items[PluginSpecConstants.REQUIRED]
            ):
                required.append(key)
        # Sort the parent_object (at the top recurse level this would be properties).
        parent_object = {
            key: parent_object[key] for key in sorted(parent_object.keys())
        }
        # Sort the required object.
        required = sorted(required)
        return parent_object, required

    @staticmethod
    def try_add(key: str, src: dict, dest: dict, throw_error: bool = False):
        """Attempt to add the value of key from src dictionary to dest dictionary. May throw error if not found."""
        if key in src:
            dest[key] = src[key]
        elif throw_error:
            raise InsightException(
                message=f"Key {key} missing from {src}",
                troubleshooting="Please add the required key",
            )
