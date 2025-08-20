"""Module for the item directive"""
from docutils import nodes
from docutils.parsers.rst import directives
from pathlib import Path

from ..traceability_exception import report_warning, TraceabilityException
from ..traceable_base_directive import TraceableBaseDirective
from ..traceable_base_node import TraceableBaseNode
from ..traceable_item import TraceableItem
from ..callback_utils import call_callback_function


class Item(TraceableBaseNode):
    '''Documentation item'''
    _item = None

    def perform_replacement(self, app, collection):
        """
        Perform the node replacement
        Args:
            app: Sphinx's application object to use.
            collection (TraceableCollection): Collection for which to generate the nodes.
        """
        self._item = collection.get_item(self['id'])
        item_id = self._item.identifier
        top_node = self.create_top_node(item_id, app=app)
        dl_node = nodes.definition_list()
        if app.config.traceability_render_attributes_per_item:
            self._process_attributes(dl_node, app)
        if app.config.traceability_render_relationship_per_item:
            self._process_relationships(dl_node, app)
        if dl_node.children:
            top_node.append(dl_node)
        # Note: content should be displayed during read of RST file, as it contains other RST objects
        self.replace_self(top_node)
        call_callback_function(
            app.config.traceability_inspect_item,
            item_id,
            collection,
            app=app
        )

    def _process_attributes(self, dl_node, app):
        """ Processes all attributes for the given item and adds the list of attributes to the given definition list.

        Args:
            dl_node (nodes.definition_list): Definition list of the item.
            app: Sphinx's application object to use.
        """
        attributes = self._item.iter_attributes()
        if attributes:
            li_node = nodes.definition_list_item()
            dt_node = nodes.term()
            txt = nodes.Text('Attributes')
            dt_node.append(txt)
            li_node.append(dt_node)
            for attr in attributes:
                dd_node = nodes.definition()
                p_node = nodes.paragraph()
                link = self.make_attribute_ref(app, attr, self._item.get_attribute(attr))
                p_node.append(link)
                dd_node.append(p_node)
                li_node.append(dd_node)
            dl_node.append(li_node)

    def _process_relationships(self, *args):
        """ Processes all relationships of the item in natural order.

        All targets get naturally sorted per relationship.
        """
        for rel, targets in self._item.all_relations:
            if rel not in self['hidetype']:
                self._list_targets_for_relation(rel, targets, *args)

    def _list_targets_for_relation(self, relation, targets, dl_node, app):
        """ Add a list with all targets for a specific relation to the given definition list.

        Args:
            relation (str): Name of the relation.
            targets (iterable): Naturally sorted iterable of targets to other traceable item(s).
            dl_node (nodes.definition_list): Definition list of the item.
            app: Sphinx's application object to use.
        """
        li_node = nodes.definition_list_item()
        dt_node = nodes.term()
        if relation in app.config.traceability_relationship_to_string:
            relstr = app.config.traceability_relationship_to_string[relation]
        else:
            report_warning(f'Traceability: relation {relation} cannot be translated to string',
                           docname=self['document'], lineno=self['line'])
            relstr = relation
        dt_node.append(nodes.Text(relstr))
        li_node.append(dt_node)
        for target in targets:
            dd_node = nodes.definition()
            p_node = nodes.paragraph()
            if self.is_relation_external(relation):
                link = self.make_external_item_ref(app, target, relation)
            else:
                link = self.make_internal_item_ref(app, target)
            p_node.append(link)
            dd_node.append(p_node)
            li_node.append(dd_node)
        dl_node.append(li_node)


class ItemDirective(TraceableBaseDirective):
    """
    Directive to declare items and their traceability relationships.

    Syntax::

      .. item:: item_id [item_caption]
         :<<relationship>>:  other_item_id ...
         :<<attribute>>: attribute_value
         ...
         :nocaptions:

         [item_content]

    When run, for each item, two nodes will be returned:

    * A target node
    * A custom node with id + caption, to be replaced with relationship links
    * A node containing the content of the item

    Also ``traceability_collection`` storage is filled with item information

    """
    # Required argument: id
    required_arguments = 1
    # Optional argument: caption (whitespace allowed)
    optional_arguments = 1
    # Options: the typical ones plus every relationship (and reverse)
    # defined in env.config.traceability_relationships
    option_spec = {
        'class': directives.class_option,
        'nocaptions': directives.flag,
        'hidetype': directives.unchanged,
    }
    # Content allowed
    has_content = True

    def run(self):
        """ Processes the contents of the directive. """
        env = self.state.document.settings.env
        app = env.app

        target_id = self.arguments[0]

        item_node = Item('')
        item_node['document'] = env.docname
        item_node['line'] = self.lineno
        item_node['id'] = target_id
        item_node['classes'].append('collapsible_links')  # traceability.js adds the arrowhead button
        if app.config.traceability_collapse_links:
            item_node['classes'].append('collapse')
        if 'class' in self.options:
            item_node['classes'].extend(self.options.get('class'))
        self.process_options(
            item_node,
            {
                'hidetype': {'default': []},
            },
        )
        item = self._store_item_info(target_id, env)
        if item is None:
            return []

        self.check_relationships(item_node['hidetype'], env)

        # Custom callback for modifying items
        call_callback_function(
            app.config.traceability_callback_per_item,
            target_id,
            env.traceability_collection,
            app=app
        )
        item.clear_state()  # avoid access to the state machine after this point

        self.check_caption_flags(item_node, app.config.traceability_item_no_captions)

        return [item.node, item_node, item.content_node]

    def _store_item_info(self, target_id, env):
        """ Stores item info and adds TraceableItem to the collection.

        If an item with the same identifier already exists, a warning will be reported and this item info is ignored.

        Args:
            target_id (str): Item identifier.
            env (sphinx.environment.BuildEnvironment): Sphinx's build environment.

        Returns:
            TraceableItem/None: Instantiated TraceableItem; or None if an item with the same identifier already exists
        """
        target_node = nodes.target('', '', ids=[target_id])
        item = TraceableItem(target_id, directive=self)
        doc_path_str, lineno = self.get_source_info()
        doc_path = Path(doc_path_str)
        if doc_path.is_absolute():
            doc_path = doc_path.relative_to(env.srcdir)
        item.set_location(doc_path, lineno)
        item.node = target_node
        item.caption = self.caption
        item.content = self.content
        try:
            env.traceability_collection.add_item(item)
        except TraceabilityException as err:
            report_warning(err, env.docname, self.lineno)
            return None

        self._add_attributes(item, env.docname)

        # Add found relationships to item. All relationship data is a string of
        # item ids separated by space. It is split in a list of item ids.
        for rel in set(env.traceability_collection.relations) & set(self.options):
            self._warn_if_comma_separated(rel, env.docname)
            related_ids = self.options[rel].split()
            self._add_relation_to_ids(rel, target_id, related_ids, env)

        return item

    def _add_relation_to_ids(self, relation, source_id, related_ids, env):
        """ Adds the given relation between the source id and all related ids.

        Both the forward and the automatic reverse relation are added.

        Args:
            relation (str): Name of the given relation.
            source_id (str): ID of the source item.
            related_ids (list): List of target item IDs.
            env (sphinx.environment.BuildEnvironment): Sphinx's build environment.
        """
        for related_id in related_ids:
            try:
                env.traceability_collection.add_relation(source_id, relation, related_id)
            except TraceabilityException as err:
                report_warning(err, env.docname, self.lineno)

    def _add_attributes(self, item, docname):
        """ Adds all specified attributes to the item. Attribute data is a single string.

        A warning is reported when an attribute's value doesn't match the attribute's regex.

        Args:
            item (TraceableItem): Item to add the attributes to.
            docname (str): Document name.
        """
        for attribute in set(TraceableItem.defined_attributes) & set(self.options) - self.conflicting_options:
            try:
                item.add_attribute(attribute, self.options[attribute])
            except TraceabilityException as err:
                report_warning(err, docname, self.lineno)
