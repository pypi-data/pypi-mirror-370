from insight_plugin.features.common.logging_util import BaseLoggingFeature
from insight_plugin.features.common.plugin_spec_util import (
    PluginSpecConstants,
    PluginComponent,
)
from typing import Tuple, List
from insight_plugin.features.create.help.constants import HelpMappings
from insight_plugin.features.create.help.help_util import HelpUtil
from insight_plugin.features.create.help.input_output_helpers import InputOutputHelper
from mdutils.mdutils import MdUtils


class ComponentHelp(BaseLoggingFeature):
    def __init__(self, spec: dict, input_output_helper: InputOutputHelper):
        super().__init__()
        self.spec = spec
        self.input_output_helper = input_output_helper

    @staticmethod
    def gather_components(spec: dict) -> [Tuple[PluginComponent, dict]]:
        """
        Go through the plugin spec and collect all existing components (actions, tasks, triggers)
        :param spec: complete plugin spec
        :return: List of tuples (PluginComponent, dict) where dict is dict of that component type (e.g. all actions)
        """
        components = []

        ComponentHelp.get_component(spec, PluginSpecConstants.ACTIONS, components)
        ComponentHelp.get_component(spec, PluginSpecConstants.TRIGGERS, components)
        ComponentHelp.get_component(spec, PluginSpecConstants.TASKS, components)

        return components

    @staticmethod
    def get_component(
        spec: dict,
        component_type: PluginComponent,
        components: [Tuple[PluginComponent, dict]],
    ):
        """
        Helper function for less code duplication. Gets individual component dict from spec if it exists
        :param spec: complete plugin spec
        :param component_type: component to look for and add
        :param components: list of components so far
        :return: list of all component types, filled in with applicable components or empty dict
        """
        if component_type in spec:
            actions = spec[component_type]
            components.append((component_type, actions))
        else:
            components.append((component_type, {}))

    @staticmethod
    def add_component_troubleshooting(
        components: List[Tuple[PluginComponent, dict]],
        markdown_obj: MdUtils,
        troubleshooting_added: bool,
    ) -> bool:
        """
        Add component troubleshooting to the markdown object
        :param components: plugin components
        :param markdown_obj: markdown object to add any connection troubleshooting to
        :param troubleshooting_added: boolean if we have already added some troubleshooting
        :return: true if troubleshooting_added was true and we didn't add any help, false otherwise
        """
        # check / add component troubleshooting
        for component_tuple in components:
            # Don't want to bother checking blank components (though removing this wouldn't break anything right now)
            component_items = component_tuple[1]
            if component_items != {}:
                # Loop through each component
                for component_name, component in component_items.items():
                    # Check if this component has specific troubleshooting associated with it
                    if (
                        PluginSpecConstants.PLUGIN_TROUBLESHOOTING in component
                        and component[PluginSpecConstants.PLUGIN_TROUBLESHOOTING]
                        is not None
                    ):
                        # add it
                        troubleshooting_added = False
                        markdown_obj.new_header(
                            level=3,
                            title=component.get(
                                PluginSpecConstants.TITLE, component_name
                            ),
                        )
                        markdown_obj.new_line(
                            component[PluginSpecConstants.PLUGIN_TROUBLESHOOTING]
                        )
        return troubleshooting_added

    def convert_components(
        self, components: [Tuple[PluginComponent, dict]], markdown_obj: MdUtils
    ):
        """
        Convert all components to markdown format and add them to running markdown file
        :param components: Tuple with title PluginComponent and value dictionary. E.G. "Action" and all action in spec
        :param markdown_obj: Markdown obj to add the components to
        :return: None
        """
        for component in components:
            component_type = component[0]
            component_contents = component[1]
            if component_contents == {}:
                # empty section (aka no actions or triggers or...). Lets just handle that here
                markdown_obj.new_header(
                    level=3, title=HelpMappings.SECTION_TITLES[component_type]
                )
                # These should all be plural (actionS) so no need for extra helper function
                markdown_obj.new_line(
                    f"This plugin does not contain any {component_type.lower()}.",
                    bold_italics_code="i",
                )
            else:
                markdown_obj = self.convert_component_markdown(
                    component_type, component_contents, markdown_obj
                )
        return markdown_obj

    def convert_component_markdown(
        self, section_name: PluginComponent, section_spec: dict, markdown_obj: MdUtils
    ) -> MdUtils:
        """
        Converts a component to its markdown string
        :param markdown_obj: markdown object to add component to
        :param section_name: component type that identifies what we are working on
        :param section_spec: spec that needs to be converted to markdown
        :return: markdown string for the component
        """
        markdown_obj.new_header(
            level=3, title=HelpMappings.SECTION_TITLES[section_name]
        )
        section_spec = HelpUtil.shallow_sort(section_spec)

        for component_name, individual_component in section_spec.items():
            # try to use the title. Statistically, this should work for all of them (in theory)
            if PluginSpecConstants.TITLE not in individual_component:
                title = component_name
                self.logger.warning(
                    f"{section_name} {component_name} does not have a title"
                )
            else:
                title = individual_component[PluginSpecConstants.TITLE]
            HelpUtil.make_header(markdown_obj, 4, title)
            # same here- all current plugin components currently have descriptions

            description_start = f"this {section_name[:-1]} is used to"

            if (
                description_start
                in individual_component.get(PluginSpecConstants.DESCRIPTION).lower()
            ):
                markdown_obj.new_line(
                    individual_component.get(PluginSpecConstants.DESCRIPTION, "")
                )

            else:
                markdown_obj.write(
                    "\n"
                    + f"This {section_name[:-1]} is used to "
                    + individual_component.get(PluginSpecConstants.DESCRIPTION, "")[
                        0
                    ].lower()
                    + individual_component.get(PluginSpecConstants.DESCRIPTION, "")[1:]
                )

            # add component specific "help" if it exists
            if PluginSpecConstants.HELP in individual_component:
                markdown_obj.new_line(individual_component[PluginSpecConstants.HELP])

            # Add input if it exists
            markdown_obj = self.input_output_helper.convert_input_output_markdown(
                individual_component.get(PluginSpecConstants.INPUT, {}),
                "Input",
                section_name,
                markdown_obj,
            )

            # Add output if it exists
            markdown_obj = self.input_output_helper.convert_input_output_markdown(
                individual_component.get(PluginSpecConstants.OUTPUT, {}),
                "Output",
                section_name,
                markdown_obj,
            )
        return markdown_obj
