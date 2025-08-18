from insight_plugin.features.common.plugin_spec_util import (
    PluginSpecConstants,
    PluginSpecVersions,
)
from insight_plugin.features.common.logging_util import BaseLoggingFeature
from insight_plugin.features.create.help.constants import TableHeaders, HelpMappings
from insight_plugin.features.create.help.help_util import HelpUtil
from insight_plugin.features.create.help.input_output_helpers import InputOutputHelper

from mdutils.mdutils import MdUtils


class ConnectionHelp(BaseLoggingFeature):
    def __init__(self, spec: dict, input_output_helper: InputOutputHelper):
        super().__init__()
        self.spec = spec
        self.input_output_helper = input_output_helper

    def convert_connection(self, spec: dict, markdown_obj: MdUtils) -> MdUtils:
        """
        Converts connection plugin spec and adds to a markdown file passed in
        :param spec: complete plugin spec
        :param markdown_obj: markdown object to add connection help to
        :return:
        """
        # Connection Header: Setup
        markdown_obj.new_header(level=2, title="Setup")
        if PluginSpecConstants.CONNECTIONS in spec:
            markdown_obj.write(
                "\n" + "The connection configuration accepts the following parameters:"
            )
            version = spec.get(
                PluginSpecConstants.SPEC_VERSION, PluginSpecVersions.V2.value
            )
            if version == PluginSpecVersions.V3.value:
                spec_in = spec[PluginSpecConstants.CONNECTIONS].get(
                    PluginSpecConstants.INPUT, None
                )
                if spec_in is None:
                    self.logger.warning(
                        "Connection with empty input, please fill the input section"
                    )
                    return markdown_obj
            elif version == PluginSpecVersions.V2.value:
                spec_in = spec[PluginSpecConstants.CONNECTIONS]
            else:
                self.logger.error(
                    f"No {PluginSpecConstants.VERSION_HISTORY} in {PluginSpecConstants.FILENAME}."
                )
                return markdown_obj
            spec_in = HelpUtil.shallow_sort(spec_in)
            markdown_obj.new_line()
            markdown_obj.new_table(
                columns=len(TableHeaders.INPUT_HEADERS),
                rows=len(spec_in) + 1,
                text=HelpUtil.get_new_table_text(spec_in, TableHeaders.INPUT_HEADERS),
                text_align="left",
            )
            markdown_obj.write("\n" + HelpMappings.EXAMPLE_INPUT)
            markdown_obj.insert_code(self.input_output_helper.get_example(spec_in))
        else:
            markdown_obj.new_line(
                "This plugin does not contain a connection.", bold_italics_code="i"
            )

        return markdown_obj

    @staticmethod
    def add_connection_troubleshooting(spec: dict, markdown_obj: MdUtils) -> bool:
        """
        Add the connection troubleshooting section to the markdown object
        :param spec: complete plugin spec dictionary
        :param markdown_obj: markdown object to add any connection troubleshooting to
        :return: false if anything was added. True if nothing was added
        """
        no_troubleshooting = True
        if PluginSpecConstants.CONNECTIONS in spec:
            # Check if there is connection troubleshooting and that it is not None
            if (
                PluginSpecConstants.PLUGIN_TROUBLESHOOTING
                in spec[PluginSpecConstants.CONNECTIONS]
                and spec[PluginSpecConstants.CONNECTIONS][
                    PluginSpecConstants.PLUGIN_TROUBLESHOOTING
                ]
                is not None
            ):
                # add it
                no_troubleshooting = False
                markdown_obj.new_header(level=3, title="Connection Troubleshooting")
                markdown_obj.new_line(
                    spec[PluginSpecConstants.CONNECTIONS][
                        PluginSpecConstants.PLUGIN_TROUBLESHOOTING
                    ]
                )
        return no_troubleshooting
