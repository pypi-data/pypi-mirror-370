from typing import Literal
import json
import copy
from insight_plugin.features.common.logging_util import BaseLoggingFeature
from insight_plugin.features.common.plugin_spec_util import (
    PluginSpecConstants,
    PluginComponent,
)
from insight_plugin.features.common.exceptions import InsightException
from insight_plugin.features.create.json_generation_util import BaseTypes, JsonGenerator
from insight_plugin.features.create.help.constants import HelpMappings, TableHeaders
from insight_plugin.features.create.help.help_util import HelpUtil
from mdutils.mdutils import MdUtils


class InputOutputHelper(BaseLoggingFeature):
    def __init__(self, spec: dict):
        super().__init__()
        self.spec = spec

    def convert_input_output_markdown(
        self,
        spec_in: dict,
        input_or_output: Literal["Input", "Output"],
        section_name: PluginComponent,
        markdown_obj: MdUtils,
    ) -> MdUtils:
        """
        Converts input in spec to the corresponding markdown string
        :param input_or_output: Input or Output
        :param markdown_obj: markdown object to append this section to
        :param spec_in: input spec dictionary for this input/output
        :param section_name: type of section we are inside
        :return: markdown object modified as needed
        """
        HelpUtil.make_header(markdown_obj, 5, input_or_output)
        # check if there is actually an input/output section
        if spec_in != {} and spec_in is not None and len(spec_in) > 0:
            self.create_table(spec_in, input_or_output, markdown_obj)
        else:
            # take singular (everything but the last "s") of section name because this is only for one component
            markdown_obj.new_line(
                f"This {section_name[:-1]} does not contain any {input_or_output.lower()}s.",
                bold_italics_code="i",
            )
        return markdown_obj

    def create_table(
        self,
        spec_in: dict,
        input_or_output: Literal["Input", "Output"],
        markdown_obj: MdUtils,
    ):
        """
        Creates a table in the markdown object for the inputs and outputs
        of each component respectively.
        Input & Output are separated because they have differing headers required to
        pass the validator checks
        :param spec_in: input spec dictionary for this input/output
        :param input_or_output: Input or Output
        :param markdown_obj: markdown object to append this section to
        :return: Markdown object with new table added.
        """
        table_headers = None
        help_mappings = None

        if input_or_output == "Input":
            table_headers = TableHeaders.INPUT_HEADERS
            help_mappings = HelpMappings.EXAMPLE_INPUT
        elif input_or_output == "Output":
            table_headers = TableHeaders.OUTPUT_HEADERS
            help_mappings = HelpMappings.EXAMPLE_OUTPUT

        markdown_obj.new_table(
            columns=len(table_headers),
            rows=len(spec_in) + 1,
            text=HelpUtil.get_new_table_text(spec_in, table_headers),
            text_align="left",
        )
        markdown_obj.new_line(help_mappings)
        markdown_obj.insert_code(self.get_example(spec_in))

    def get_example(self, section_spec: dict):
        """
        Take some example section (at time of writing: connection, input, or output) and create the example json
        :param section_spec: section to make an example of
        :return: example section filled in with "example" fields, or base example type if no example exists
        """

        priority_list = [
            PluginSpecConstants.DEFAULT,
            PluginSpecConstants.EXAMPLE,
            PluginSpecConstants.ENUM,
        ]

        # create copy of section spec in order not to manipulate the original plugin spec object
        temp_section_spec = copy.deepcopy(section_spec)

        for field in temp_section_spec:
            if PluginSpecConstants.TYPE not in temp_section_spec[field]:
                raise InsightException(
                    message=f"No type specified for the {field} field.",
                    troubleshooting=f"Please fill in the type for the {field} "
                    f"field in the plugin.spec.yaml file.",
                )
            else:
                # fill in with the proper type template
                type_example = self.get_type(
                    temp_section_spec[field][PluginSpecConstants.TYPE],
                    temp_section_spec[field],
                    [],
                    priority_list,
                )
                # One common example is JSON, which may contain extra " characters. This would confuse normal JSON
                # writers with output like "INPUT_FIELD": {\"KEY\": \"VALUE\"}. So here we just attempt conversion
                try:
                    type_example = json.loads(type_example)
                except json.JSONDecodeError:
                    # Do nothing, this is expected for many cases- just means there isn't json within a string hidden
                    pass
                except TypeError:
                    pass

                temp_section_spec[field] = type_example

        json_obj = JsonGenerator(temp_section_spec)
        return json_obj.generate_json()

    def get_type(
        self,
        type_str: str,
        curr_dict: dict,
        prev_types_discovered: [str],
        priority_list: [str],
    ):
        """
        Given a type in, produce the example for the helpmd file
        :param type_str: string representation of our current type
        :param curr_dict: if we have it yet, this is the dictionary of our current type
        :param prev_types_discovered: list of types we have already seen, to prevent infinite loops
        :param priority_list: list
        :return: type example (many possible types)
        """
        # Case to avoid infinite loops where types refer to each other
        if type_str in prev_types_discovered:
            return {}
        else:
            prev_types_discovered.append(type_str)

        # If we have an example (or default, enum) use that
        for possible_example in priority_list:
            if possible_example in curr_dict:
                test_val = curr_dict[possible_example]
                if test_val is not None:
                    return test_val

        # ok, so there is no example value. Is it (1) a base type? (2) An existing custom type? Or (3) a mistake?
        # Case 1: Base type
        if type_str in BaseTypes.base_types:
            # base type is so far up because we are already in the "custom types" section
            return BaseTypes.base_types[type_str]
        # Case 2: List of some other type
        elif len(type_str) >= 2 and type_str[0:2] == "[]":
            return [
                self.get_type(type_str[2:], {}, prev_types_discovered, priority_list)
            ]
        # Case 3: Custom type
        elif (
            PluginSpecConstants.TYPES in self.spec
            and type_str in self.spec[PluginSpecConstants.TYPES]
        ):
            template = {}
            # in some cases we might not have the current dictionary yet- resetting it won't hurt
            curr_dict = self.spec[PluginSpecConstants.TYPES][type_str]
            # Loop through each field of this custom type...
            for subkey, subtype in curr_dict.items():
                try:
                    type_title = subtype.get(PluginSpecConstants.TITLE, subkey)
                    if type_title is None:
                        # This occurs if the spec has a blank title: (leave the validators to sort)
                        type_title = subkey
                    type_inner_type = subtype[PluginSpecConstants.TYPE]
                except KeyError:
                    raise InsightException(
                        message=f"Type '{subtype}' must have both title and type as fields.",
                        troubleshooting=f"Add title and type to '{subtype}' type.",
                    )
                # ...and recurse further for those types
                template[type_title] = self.get_type(
                    type_inner_type, subtype, prev_types_discovered, priority_list
                )
            return template
        else:
            raise InsightException(
                message=f"Type '{type_str}' not found in the plugin.spec.yaml file and is not a base type.",
                troubleshooting="See https://docs.rapid7.com/insightconnect/plugin-spec/#base-types"
                " or add this type to the types section in the plugin.spec.yaml file.",
            )
