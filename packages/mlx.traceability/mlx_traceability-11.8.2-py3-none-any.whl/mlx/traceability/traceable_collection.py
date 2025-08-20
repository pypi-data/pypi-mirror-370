'''
Storage classes for collection of traceable items
'''
import json
import re
from operator import attrgetter
from pathlib import Path

from natsort import natsorted

from .traceability_exception import MultipleTraceabilityExceptions, TraceabilityException
from .traceable_item import TraceableItem


class TraceableCollection:
    '''
    Storage for a collection of TraceableItems
    '''

    NO_RELATION_STR = ''

    def __init__(self):
        '''Initializer for container of traceable items'''
        self.relations = {}
        self.items = {}
        self.relations_sorted = {}
        self._intermediate_nodes = []
        self.attributes_sort = {}

    def add_relation_pair(self, forward, reverse=NO_RELATION_STR):
        '''
        Add a relation pair to the collection

        Args:
            forward (str): Keyword for the forward relation
            reverse (str): Keyword for the reverse relation, or NO_RELATION_STR for external relations
        '''
        # Link forward to reverse relation
        self.relations[forward] = reverse
        # Link reverse to forward relation
        if reverse != self.NO_RELATION_STR:
            self.relations[reverse] = forward

    def get_reverse_relation(self, forward):
        '''
        Get the matching reverse relation

        Args:
            forward (str): Keyword for the forward relation
        Returns:
            str: Keyword for the matching reverse relation, or None
        '''
        if forward in self.relations:
            return self.relations[forward]
        return None

    def iter_relations(self):
        '''
        Iterate over available relations: naturally sorted

        Returns:
            Naturally sorted list over available relations in the collection
        '''
        if len(self.relations) != len(self.relations_sorted):
            self.relations_sorted = natsorted(self.relations)
        return self.relations_sorted

    def add_item(self, item):
        '''
        Add a TraceableItem to the list

        Args:
            item (TraceableItem): Traceable item to add
        '''
        # If the item already exists ...
        if item.identifier in self.items:
            olditem = self.items[item.identifier]
            # ... and it's not a placeholder, log an error
            if not olditem.is_placeholder:
                raise TraceabilityException('duplicating {itemid}'.format(itemid=item.identifier), item.docname)
            # ... otherwise, update the item with new content
            item.update(olditem)
        # add it
        self.items[item.identifier] = item

    def get_item(self, itemid):
        '''
        Get a TraceableItem from the list

        Args:
            itemid (str): Identification of traceable item to get
        Returns:
            TraceableItem/None: Object for traceable item; None if the item was not found
        '''
        return self.items.get(itemid)

    def iter_items(self):
        '''
        Iterate over items: naturally sorted identification

        Returns:
            Sorted iterator over identification of the items in the collection
        '''
        return natsorted(self.items)

    def has_item(self, itemid):
        '''
        Verify if a item with given id is in the collection

        Args:
            itemid (str): Identification of item to look for
        Returns:
            bool: True if the given itemid is in the collection, false otherwise
        '''
        return itemid in self.items

    def remove_items_from_document(self, docname):
        '''Remove all items that originate from the given document.

        Args:
            docname (str): Document name (without extension) to purge items for
        '''
        to_remove = [identifier for identifier, item in self.items.items()
                     if getattr(item, 'docname', None) == docname]
        if not to_remove:
            return
        to_remove_set = set(to_remove)
        # Remove the items themselves
        for identifier in to_remove:
            del self.items[identifier]
        # Remove any relations (explicit and implicit) pointing to the removed items from remaining items
        for item in self.items.values():
            for removed_id in to_remove_set:
                item.remove_targets(removed_id, explicit=True, implicit=True)

    def add_relation(self, source_id, relation, target_id):
        '''
        Add relation between two items

        The function adds the forward and the automatic reverse relation.

        Args:
            source_id (str): ID of the source item
            relation (str): Relation between source and target item
            target_id (str): ID of the target item
        '''
        # Add placeholder if source item is unknown
        if source_id not in self.items:
            src = TraceableItem(source_id, True)
            self.add_item(src)
        source = self.items[source_id]
        # Error if relation is unknown
        if relation not in self.relations:
            raise TraceabilityException('Relation {name} not known'.format(name=relation), source.docname)
        # Add forward relation
        source.add_target(relation, target_id)
        # When reverse relation exists, continue to create/adapt target-item
        reverse_relation = self.get_reverse_relation(relation)
        if reverse_relation:
            # Add placeholder if target item is unknown
            if target_id not in self.items:
                tgt = TraceableItem(target_id, True)
                self.add_item(tgt)
            # Add reverse relation to target-item
            self.items[target_id].add_target(reverse_relation, source_id, implicit=True)

    def add_attribute_sorting_rule(self, filter_regex, attributes):
        """ Configures how the attributes of matching items should be sorted.

        The attributes that are missing from the given list will be sorted alphabetically underneath. The items that
        already have their attributes sorted will be returned as a list; used to report a warning.

        Args:
            filter_regex (str): Regular expression used to match items to apply the attribute sorting to.
            attributes (list): List of attributes (str) in the order they should be sorted on.

        Returns:
            list: Items that already have the order of their attributes configured.
        """
        ignored_items = []
        item_ids = self.get_items(filter_regex)
        for item_id in item_ids:
            item = self.get_item(item_id)
            if item.attribute_order:
                ignored_items.append(item)
            else:
                item.attribute_order = attributes
        return ignored_items

    def add_intermediate_node(self, node):
        """ Adds an intermediate node """
        self._intermediate_nodes.append(node)

    def process_intermediate_nodes(self):
        """ Processes all intermediate nodes in order by calling its ``apply_effect`` """
        for node in sorted(self._intermediate_nodes, key=attrgetter('order')):
            node.apply_effect(self)

    def rebuild_implicit_relations(self):
        """Rebuild all implicit (reverse) relations from explicit ones.

        This is needed on incremental builds when some documents are re-read and others come from cache,
        so implicit reverse links on re-read items are restored based on the existing explicit links.
        """
        # Clear all current implicit relations
        for item in self.items.values():
            item.implicit_relations = {}

        # Recreate implicit relations from explicit relations
        for source_id, source in self.items.items():
            for relation, targets in source.explicit_relations.items():
                reverse_relation = self.get_reverse_relation(relation)
                if not reverse_relation:
                    continue
                for target_item in (self.items.get(target_id) for target_id in targets):
                    if not target_item:
                        continue
                    target_item.add_target(reverse_relation, source_id, implicit=True)

    def export(self, fname):
        '''
        Exports collection content. The target location of the json file gets created if it doesn't exist yet.

        Args:
            fname (str): Path to the json file to export
        '''
        Path(fname).parent.mkdir(parents=True, exist_ok=True)
        with open(fname, 'w') as outfile:
            data = []
            for itemid in self.iter_items():
                item = self.items[itemid]
                entry = item.to_dict()
                if entry:
                    data.append(entry)
            json.dump(data, outfile, indent=4, sort_keys=True)

    def self_test(self, notification_item_id, docname=None):
        '''
        Perform self test on collection content

        Args:
            notification_item_id (str/None): ID of the configured notification item, None if not configured.
            docname (str): Document on which to run the self test, None for all.
        '''
        errors = []
        notification_item = self.get_item(notification_item_id)
        # Having no valid relations, is invalid
        if not self.relations:
            raise TraceabilityException('No relations configured', 'configuration')
        # Validate each item
        for itemid, item in self.items.items():
            # Only for relevant items, filtered on document name
            if docname is not None and item.docname != docname and item.docname is not None:
                continue
            # Check if docname of notification item will be used
            if item.docname is None and notification_item:
                continue
            # On item level
            try:
                item.self_test()
            except TraceabilityException as err:
                errors.append(err)
            # targetted items shall exist, with automatic reverse relation
            for relation in self.relations:
                # Exception: no reverse relation (external links)
                rev_relation = self.get_reverse_relation(relation)
                if rev_relation == self.NO_RELATION_STR:
                    continue
                for tgt in item.yield_targets(relation):
                    # Target item exists?
                    if tgt not in self.items:
                        errors.append(TraceabilityException("{source} {relation} {target}, but {target} is not known"
                                                            .format(source=itemid,
                                                                    relation=relation,
                                                                    target=tgt),
                                                            item.docname))
                        continue
                    # Reverse relation exists?
                    target = self.get_item(tgt)
                    if itemid not in target.yield_targets(rev_relation):
                        errors.append(TraceabilityException("No automatic reverse relation: {source} {relation} "
                                                            "{target}".format(source=tgt,
                                                                              relation=rev_relation,
                                                                              target=itemid),
                                                            item.docname))
                    # Circular relation exists?
                    for target_of_target in target.yield_targets(relation):
                        if target_of_target in item.yield_targets(rev_relation):
                            errors.append(TraceabilityException(
                                "Circular relationship found: {src} {rel} {tgt} {rel} {nested} {rel} {src}"
                                .format(src=itemid, rel=relation, tgt=tgt, nested=target_of_target),
                                item.docname))
        if errors:
            raise MultipleTraceabilityExceptions(errors)

    def __str__(self):
        '''
        Convert object to string
        '''
        retval = 'Available relations:'
        for relation in self.relations:
            reverse = self.get_reverse_relation(relation)
            retval += '\t{forward}: {reverse}\n'.format(forward=relation, reverse=reverse)
        for itemid in self.items:
            retval += str(self.items[itemid])
        return retval

    def are_related(self, source_id, relations, target_id):
        '''
        Check if 2 items are related using a list of relationships

        Placeholders are excluded

        Args:
            source_id (str): id of the source item
            relations (list): list of relations, empty list for wildcard
            target_id (str): id of the target item
        Returns:
            bool: True if both items are related through the given relationships, false otherwise
        '''
        if source_id not in self.items:
            return False
        source = self.items[source_id]
        if not source or source.is_placeholder:
            return False
        if target_id not in self.items:
            return False
        target = self.items[target_id]
        if not target or target.is_placeholder:
            return False
        if not relations:
            relations = self.relations
        return self.items[source_id].is_related(relations, target_id)

    def get_items(self, regex, attributes=None, sortattributes=None, reverse=False, sort=True):
        '''
        Get all items that match a given regular expression

        Placeholders are excluded

        Args:
            regex (str/re.Pattern): Regex pattern or object to match the items in this collection against
            attributes (dict): Dictionary with attribute-regex pairs to match the items in this collection against
            sortattributes (list): List of attributes on which to sort the items alphabetically, or using a custom
                sort order if at least one attribute is in ``attributes_sort``
            reverse (bool): True for reverse sorting
            sort (bool): When sortattributes is falsy: True to enable natural sorting, False to disable sorting

        Returns:
            list: A sorted list of item-id's matching the given regex. Sorting is done naturally when sortattributes is
            unused.
        '''
        matches = []
        for itemid, item in self.items.items():
            if item.is_placeholder:
                continue
            if item.is_match(regex) and (not attributes or item.attributes_match(attributes)):
                matches.append(itemid)
        if sortattributes:
            for attr in sortattributes:
                if attr in self.attributes_sort:
                    sorted_func = self.attributes_sort[attr]
                    break
            else:
                sorted_func = sorted
            return sorted_func(matches, key=lambda itemid: self.get_item(itemid).get_attributes(sortattributes),
                               reverse=reverse)
        if sort:
            return natsorted(matches, reverse=reverse)
        return matches

    def get_item_objects(self, regex, attributes=None):
        ''' Get all items that match a given regular expression as TraceableItem instances.

        Placeholders are excluded.

        Args:
            regex (str): Regex to match the items in this collection against
            attributes (dict): Dictionary with attribute-regex pairs to match the items in this collection against

        Returns:
            generator: An iterable of items matching the given regex.
        '''
        for item in self.items.values():
            if item.is_placeholder:
                continue
            if item.is_match(regex) and (not attributes or item.attributes_match(attributes)):
                yield item

    def get_external_targets(self, regex, relation):
        ''' Get all external targets for a given external relation with the IDs of their linked internal items

        Args:
            regex (str/re.Pattern): Regex pattern or object to match the external target
            relation (str): External relation
        Returns:
            dict: Dictionary mapping external targets to the IDs of their linked internal items
        '''
        external_targets_to_item_ids = {}
        for item_id, item in self.items.items():
            for target in item.yield_targets(relation):
                try:
                    match = regex.match(target)
                except AttributeError:
                    match = re.match(regex, target)
                if not match:
                    continue
                external_targets_to_item_ids.setdefault(target, []).append(item_id)
        return external_targets_to_item_ids
