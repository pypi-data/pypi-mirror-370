"""Module for the attribute-link directive"""
from docutils.parsers.rst import directives

from ..traceability_exception import TraceabilityException, report_warning
from ..traceable_base_directive import TraceableBaseDirective
from ..traceable_base_node import TraceableBaseNode


class AttributeLink(TraceableBaseNode):
    """Node that adds one or more attributes to one or more items."""
    order = 3

    def perform_replacement(self, app, collection):
        """ The AttributeLink node has no final representation, so it is removed from the tree.

        Args:
            app: Sphinx application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        self.replace_self([])

    def apply_effect(self, collection):
        """ Processes the attribute-link items, which shall be done before converting anything to docutils.

        Args:
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        filtered_items = collection.get_item_objects(self['filter'])
        for attribute, value in self['filter-attributes'].items():
            for item in filtered_items:
                if not self['nooverwrite'] or not item.get_attribute(attribute):
                    try:
                        item.add_attribute(attribute, value)
                    except TraceabilityException as err:
                        report_warning(err, self['document'], self['line'])


class AttributeLinkDirective(TraceableBaseDirective):
    """ Directive to add attributes to items outside of the items' definition.

    The node will be responsible for applying the configuration to the Item. First, all directives must be parsed.

    Syntax::

      .. attribute-link::
         :filter: regex
         :<<attribute>>: attribute_value
         :nooverwrite:
    """
    # Options
    option_spec = {
        'filter': directives.unchanged,
        'nooverwrite': directives.flag,
    }
    # Content disallowed
    has_content = False

    def run(self):
        """ Processes the contents of the directive. Just store the configuration. """
        env = self.state.document.settings.env

        node = AttributeLink('')
        node['document'] = env.docname
        node['line'] = self.lineno

        self.process_options(
            node,
            {
                'filter': {'default': r"\S+", 'is_pattern': True},
            },
        )
        self.add_found_attributes(node)
        self.check_option_presence(node, 'nooverwrite')

        env.traceability_collection.add_intermediate_node(node)
        return [node]
