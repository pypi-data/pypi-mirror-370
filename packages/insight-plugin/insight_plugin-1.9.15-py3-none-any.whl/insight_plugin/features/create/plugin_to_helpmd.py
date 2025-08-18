import os
from typing import Tuple, Callable

from insight_plugin.features.common.plugin_spec_util import (
    PluginSpecConstants,
    PluginComponent,
)
from insight_plugin.features.common.logging_util import BaseLoggingFeature
from insight_plugin.features.common.exceptions import InsightException
from insight_plugin.features.common.temp_file_util import SafeTempDirectory
from insight_plugin.features.create.help.connection_help import ConnectionHelp
from insight_plugin.features.create.help.components import ComponentHelp
from insight_plugin.features.create.help.input_output_helpers import InputOutputHelper
from insight_plugin.features.create.help.constants import HelpMappings, TableHeaders
from insight_plugin.features.create.help.help_util import HelpUtil
from mdutils.mdutils import MdUtils


class ConvertPluginToHelp(BaseLoggingFeature):
    def __init__(self, spec: dict, filepath: str):
        super().__init__()
        self.spec = spec
        self.filepath = filepath
        self.input_output_helper = InputOutputHelper(spec)
        self.component_help = ComponentHelp(spec, self.input_output_helper)
        self.connection_help = ConnectionHelp(spec, self.input_output_helper)
        self.convert_function = None

    def _convert_spec_to_markdown(self):
        SafeTempDirectory.execute_safe_dir(
            self._safe_build_markdown, self.filepath, overwrite=True
        )

    def _safe_build_markdown(self, temp_dir: str):
        temp_name = os.path.join(temp_dir, "help.md")
        md_file = MdUtils(file_name=temp_name)

        # This line ensures we don't get the 3 newlines at the top
        # of the help.md each time we refresh.
        HelpUtil.change_title_to_description(md_file)

        try:
            self.build_markdown(self.spec, md_file)
        except InsightException as error:
            self.logger.exception("Help generation threw an exception")
            raise error

        md_file.create_md_file()

    @classmethod
    def new_for_markdown(cls, spec: dict, filepath: str):
        instance = cls(spec, filepath)
        instance.convert_function = instance._convert_spec_to_markdown
        return instance

    def build_markdown(self, spec: dict, markdown_obj: MdUtils):
        """
        Add all the sections needed to the markdown file, and populate.
        Each function in here may only ADD to the markdown object, never subtract or edit a previous section
        :param markdown_obj: markdown object to add to and return
        :param spec: dictionary of the plugin
        :return: format string with components place holder where needed
        """

        # Not really markdown related but it's nice to bundle with the others
        self.check_if_not_in_spec("sdk")
        self.check_if_not_in_spec("connection_version")

        # Plugin Description
        self.build_markdown_meta_helper(
            PluginSpecConstants.PLUGIN_DESCRIPTION,
            ConvertPluginToHelp.add_text,
            1,
            markdown_obj,
        )

        # Key Features
        self.build_markdown_meta_helper(
            PluginSpecConstants.KEY_FEATURES,
            ConvertPluginToHelp.add_list,
            1,
            markdown_obj,
        )

        # Requirements
        self.build_markdown_meta_helper(
            PluginSpecConstants.REQUIREMENTS,
            ConvertPluginToHelp.add_list,
            1,
            markdown_obj,
        )

        # Supported Product Versions
        self.build_markdown_meta_helper(
            PluginSpecConstants.SUPPORTED_VERSIONS,
            ConvertPluginToHelp.add_list,
            1,
            markdown_obj,
        )

        # Documentation
        HelpUtil.make_header(markdown_obj, 1, "Documentation")

        # Connection
        markdown_obj = self.connection_help.convert_connection(spec, markdown_obj)

        # Components (actions, tasks, triggers)
        HelpUtil.make_header(markdown_obj, 2, "Technical Details")
        components = ComponentHelp.gather_components(spec)
        markdown_obj = self.component_help.convert_components(components, markdown_obj)

        # Custom types
        HelpUtil.make_header(markdown_obj, 3, "Custom Types")
        markdown_obj = ConvertPluginToHelp.add_any_custom_types(spec, markdown_obj)

        # Plugin-wide troubleshooting
        self.build_markdown_meta_helper(
            PluginSpecConstants.PLUGIN_TROUBLESHOOTING,
            ConvertPluginToHelp.add_list,
            2,
            markdown_obj,
        )

        # Version History
        self.build_markdown_meta_helper(
            PluginSpecConstants.VERSION_HISTORY,
            ConvertPluginToHelp.add_list,
            1,
            markdown_obj,
        )

        # Links
        self.build_markdown_meta_helper(
            PluginSpecConstants.LINKS, ConvertPluginToHelp.add_list, 1, markdown_obj
        )

        # References
        self.build_markdown_meta_helper(
            PluginSpecConstants.REFERENCES,
            ConvertPluginToHelp.add_list,
            2,
            markdown_obj,
        )

    def build_markdown_meta_helper(
        self, key: str, adder_func: Callable, header_level: int, markdown_obj: MdUtils
    ) -> MdUtils:
        if key != "description":
            HelpUtil.make_header(
                markdown_obj, header_level, HelpMappings.SECTION_TITLES[key]
            )
        if self.check_if_not_in_spec(key):
            article = HelpUtil.get_article(key)
            markdown_obj.new_line(
                f"This plugin does not contain {article} {HelpMappings.SECTION_TITLES[key].lower()}.",
                bold_italics_code="i",
            )
        else:
            markdown_obj = adder_func(self.spec, key, markdown_obj)
        return markdown_obj

    @staticmethod
    def add_any_custom_types(spec: dict, markdown_obj: MdUtils) -> MdUtils:
        """
        Add custom types to the markdown help file
        :param spec: complete plugin spec
        :param markdown_obj: markdown object to add any custom types to
        :return: markdown object with custom types added, or a statement saying there are no custom types
        """
        if PluginSpecConstants.TYPES in spec:
            for type_name, custom_type in spec[PluginSpecConstants.TYPES].items():
                markdown_obj = ConvertPluginToHelp.add_type(
                    type_name, custom_type, markdown_obj
                )
        else:
            markdown_obj.new_line(
                text="This plugin does not contain any custom output types.",
                bold_italics_code="i",
            )
        return markdown_obj

    @staticmethod
    def add_type(type_name: str, custom_type: dict, markdown_obj: MdUtils) -> MdUtils:
        """
        Add a type to the markdown file
        :param markdown_obj: markdown object to add this custom type to
        :param type_name: name of type (for table header)
        :param custom_type: custom type dictionary (for the table itself)
        :return: MDUtils markdown object with this type's header and table appended
        """
        markdown_obj.new_line(text=type_name, bold_italics_code="b")
        markdown_obj.write("\n")
        table_text = HelpUtil.get_new_table_text(
            custom_type, TableHeaders.CUSTOM_TYPE_HEADERS
        )
        markdown_obj.new_table(
            columns=len(TableHeaders.CUSTOM_TYPE_HEADERS),
            rows=len(custom_type) + 1,
            text=table_text,
            text_align="left",
        )
        return markdown_obj

    def add_troubleshooting(
        self, components: [Tuple[PluginComponent, dict]], markdown_obj: MdUtils
    ):
        # TODO - This doesn't work!! - I think we can just delete this / seems like its for connection/component specific troubleshooting which we dont do
        """
        Adds troubleshooting info for connections and components
        :param components: components in this spec
        :param markdown_obj: markdown object to add any troubleshooting to
        :return:
        """
        # check / add connection troubleshooting
        no_troubleshooting = ConnectionHelp.add_connection_troubleshooting(
            self.spec, markdown_obj
        )
        no_troubleshooting = ComponentHelp.add_component_troubleshooting(
            components, markdown_obj, no_troubleshooting
        )

        # if no troubleshooting added, make sure the "no troubleshooting" is added
        if no_troubleshooting:
            markdown_obj.new_line(
                f"There is no {PluginSpecConstants.PLUGIN_TROUBLESHOOTING} for this plugin.",
                bold_italics_code="i",
            )

    def check_if_not_in_spec(self, key: str) -> bool:
        """
        Log a warning if key does not exist in spec
        :param key: key in the spec we are trying to add
        :return: true if not in spec, false if in spec
        """
        if key not in self.spec:
            self.logger.warning(
                f"No {key} found in spec. Help.md generation will be missing {key}, please add to "
                f"{PluginSpecConstants.FILENAME}."
            )
            return True
        return False

    @staticmethod
    def add_list(
        spec: dict, key: PluginSpecConstants, markdown_obj: MdUtils
    ) -> MdUtils:
        """
        Add a list to a markdown object from the plugin spec with the specified key
        :param spec: plugin spec dictionary
        :param key: key we are making a list from
        :param markdown_obj: markdown object we are adding this markdown list to
        :return: markdown object with list added
        """
        section = spec.get(key)
        if section is not None and isinstance(section, list):
            try:
                markdown_obj.write("\n")
                for item in section[0:-1]:
                    markdown_obj.write(
                        ConvertPluginToHelp.bullet_string(str(item)) + "\n",
                        wrap_width=0,
                    )
                markdown_obj.write(
                    ConvertPluginToHelp.bullet_string(str(section[-1])), wrap_width=0
                )
            except IndexError:
                pass

        return markdown_obj

    @staticmethod
    def bullet_string(string: str) -> str:
        """
        Turn a string in to a markdown "bullet"
        :param string: string to pre-pend a bullet to
        :return: bulletized string
        """
        return "* " + string

    @staticmethod
    def add_text(
        spec: dict, key: PluginSpecConstants, markdown_obj: MdUtils
    ) -> MdUtils:
        """
        Add the text to a markdown object from the plugin spec with the specified key
        :param spec: plugin spec dictionary
        :param key: key we are taxing the text from
        :param markdown_obj: markdown object we are adding this markdown list to
        :return: markdown object with text added
        """
        section = spec.get(key)
        if section is not None:
            markdown_obj.write("\n" + section, wrap_width=0)
        return markdown_obj
