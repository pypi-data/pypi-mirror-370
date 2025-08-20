'''
Storage classes for traceable item
'''

import re

from natsort import natsorted

from .traceability_exception import TraceabilityException
from .traceable_base_class import TraceableBaseClass


class TraceableItem(TraceableBaseClass):
    '''
    Storage for a traceable documentation item
    '''

    STRING_TEMPLATE = 'Item {identification}\n'

    defined_attributes = {}

    def __init__(self, item_id, placeholder=False, **kwargs):
        ''' Initializes a new traceable item

        Args:
            item_id (str): Item identifier.
            placeholder (bool): Internal use only.
        '''
        super().__init__(item_id, **kwargs)
        self.explicit_relations = {}
        self.implicit_relations = {}
        self.attributes = {}
        self.attribute_order = []
        self._is_placeholder = placeholder

    def update(self, other):
        ''' Updates item with other object. Stores the sum of both objects.

        Args:
            other (TraceableItem): Other TraceableItem which is the source for the update.
        '''
        super(TraceableItem, self).update(other)
        self._add_relations(self.explicit_relations, other.explicit_relations)
        self._add_relations(self.implicit_relations, other.implicit_relations)
        # Remainder of fields: update if they improve the quality of the item
        for attr in other.attributes:
            self.add_attribute(attr, other.attributes[attr], False)
        if not other.is_placeholder:
            self._is_placeholder = False

    @property
    def is_placeholder(self):
        ''' bool: True if this item is a placeholder; False otherwise '''
        return self._is_placeholder

    @property
    def all_relations(self):
        ''' generator: Yields a relationship and the corresponding targets, both naturally sorted. '''
        for relation in natsorted({**self.explicit_relations, **self.implicit_relations}):
            targets = set()
            if relation in self.explicit_relations:
                targets.update(self.explicit_relations[relation])
            if relation in self.implicit_relations:
                targets.update(self.implicit_relations[relation])
            if targets:
                yield relation, natsorted(targets)

    @staticmethod
    def _add_relations(relations_of_self, relations_of_other):
        ''' Adds all relations from other item to own relations.

        Args:
            relations_of_self (dict): Dictionary used to add relations to.
            relations_of_other (dict): Dictionary used to fetch relations from.
        '''
        for relation in relations_of_other:
            if relation not in relations_of_self:
                relations_of_self[relation] = []
            relations_of_self[relation].extend(relations_of_other[relation])

    def is_linked(self, relationships, target_regex):
        ''' Checks if item is linked with any of the forwards relationships to a target matching the regex pattern

        Args:
            relationships (iterable): Forward relationships (str)
            target_regex (str/re.Pattern): Regular expression pattern or object

        Returns:
            bool: True if linked; False otherwise
        '''
        for rel in relationships:
            for target in self.yield_targets(rel):
                try:
                    match = target_regex.match(target)
                except AttributeError:
                    match = re.match(target_regex, target)
                if match:
                    return True
        return False

    def add_target(self, relation, target, implicit=False):
        ''' Adds a relation to another traceable item.

        Note: using this API, the automatic reverse relation is not created. Adding the relation
        through the TraceableItemCollection class performs the adding of automatic reverse
        relations.

        Args:
            relation (str): Name of the relation.
            target (str): Item identification of the targeted traceable item.
            implicit (bool): If True, an explicitly expressed relation is added here. If false, an implicite
                             (e.g. automatic reverse) relation is added here.
        '''
        # When target is the item itself, it is an error: no circular relationships
        if self.identifier == target:
            raise TraceabilityException('circular relationship {src} {rel} {tgt}'.format(src=self.identifier,
                                                                                         rel=relation,
                                                                                         tgt=target),
                                        self.docname)
        # When relation is already explicit, we shouldn't add. It is an error.
        if relation in self.explicit_relations and target in self.explicit_relations[relation]:
            raise TraceabilityException('duplicating {src} {rel} {tgt}'.format(src=self.identifier,
                                                                               rel=relation,
                                                                               tgt=target),
                                        self.docname)
        # When relation is already implicit, we shouldn't add. When relation-to-add is explicit, it should move
        # from implicit to explicit.
        elif relation in self.implicit_relations and target in self.implicit_relations[relation]:
            if implicit is False:
                self._remove_target(self.implicit_relations, relation, target)
                self._add_target(self.explicit_relations, relation, target)
        # Otherwise it is a new relation, and we add to the selected database
        else:
            database = self.implicit_relations if implicit else self.explicit_relations
            self._add_target(database, relation, target)

    @staticmethod
    def _add_target(database, relation, target):
        ''' Adds a relation to another traceable item.

        Args:
            database (dict): Dictionary to add the relation to.
            relation (str): Name of the relation.
            target (str): Item identification of the targeted traceable item.
        '''
        if relation not in database:
            database[relation] = []
        if target not in database[relation]:
            database[relation].append(target)

    @staticmethod
    def _remove_target(database, relation, target):
        ''' Deletes a relation to another traceable item.

        Args:
            relation (str): Name of the relation.
            target (str): Item identification of the targeted traceable item.
            database (dict): Dictionary to remove the relation from.
        '''
        if relation in database:
            if target in database[relation]:
                database[relation].remove(target)

    def remove_targets(self, target_id, explicit=False, implicit=True, relations=set()):
        ''' Removes any relation to given target item.

        Args:
            target_id (str): Identification of the target items to remove.
            explicit (bool): If True, explicitly expressed relations to given target are removed.
            implicit (bool): If True, implicitly expressed relations to given target are removed.
            relations (set): Set of relations to remove; empty to take all into account.
        '''
        source_databases = []
        if explicit:
            source_databases.append(self.explicit_relations)
        if implicit:
            source_databases.append(self.implicit_relations)
        for database in source_databases:
            for relation in database:
                if target_id in database[relation] and (not relations or relation in relations):
                    database[relation].remove(target_id)

    def iter_targets(self, relation, explicit=True, implicit=True, sort=True):
        ''' Gets a list of targets to other traceable item(s), naturally sorted by default.

        Args:
            relation (str): Name of the relation.
            explicit (bool): If True, explicitly expressed relations are included in the returned list.
            implicit (bool): If True, implicitly expressed relations are included in the returned list.
            sort (bool): True if the relations should be sorted naturally, False if no sorting is needed

        Returns:
            list: List of targets to other traceable item(s), naturally sorted by default
        '''
        targets = []
        if explicit and relation in self.explicit_relations:
            targets.extend(self.explicit_relations[relation])
        if implicit and relation in self.implicit_relations:
            targets.extend(self.implicit_relations[relation])
        if sort:
            return natsorted(targets)
        return targets

    def yield_targets(self, *relations, explicit=True, implicit=True):
        ''' Gets an iterable of targets to other traceable items.

        Args:
            relations (iter[str]): One or more names of relations.
            explicit (bool): If True, explicitly expressed relations are included.
            implicit (bool): If True, implicitly expressed relations are included.

        Returns:
            generator: Targets to other traceable items, unsorted
        '''
        for relation in relations:
            if explicit and relation in self.explicit_relations:
                for target in self.explicit_relations[relation]:
                    yield target
            if implicit and relation in self.implicit_relations:
                for target in self.implicit_relations[relation]:
                    yield target

    def yield_targets_sorted(self, *args, **kwargs):
        ''' Gets an iterable of targets to other traceable items, with natural sorting applied. '''
        gen = self.yield_targets(*args, **kwargs)
        return natsorted(gen)

    def iter_relations(self, sort=True):
        ''' Iterates over available relations: naturally sorted by default.

        Args:
            sort (bool): True if the relations should be sorted naturally, False if no sorting is needed

        Returns:
            list: List containing available relations in the item, naturally sorted by default
        '''
        relations = list(self.explicit_relations) + list(self.implicit_relations)
        if sort:
            return natsorted(relations)
        return relations

    @staticmethod
    def define_attribute(attr):
        ''' Defines an attribute that can be assigned to traceable items.

        Args:
            attr (TraceableAttribute): Attribute to be assigned.
        '''
        TraceableItem.defined_attributes[attr.identifier] = attr

    def add_attribute(self, attr, value, overwrite=True):
        ''' Adds an attribute key-value pair to the traceable item.

        Note:
            The given attribute value is compared against defined attribute possibilities. An exception is thrown when
            the attribute value doesn't match the defined regex.

        Args:
            attr (str): Name of the attribute.
            value (str): Value of the attribute.
            overwrite (bool): Overwrite existing attribute value, if any.
        '''
        if not attr or value is None or attr not in TraceableItem.defined_attributes:
            raise TraceabilityException('item {item} has invalid attribute ({attr}={value})'
                                        .format(item=self.identifier, attr=attr, value=value),
                                        self.docname)
        if not TraceableItem.defined_attributes[attr].can_accept(value):
            raise TraceabilityException('item {item} attribute does not match defined attributes ({attr}={value})'
                                        .format(item=self.identifier, attr=attr, value=value),
                                        self.docname)
        if overwrite or attr not in self.attributes:
            self.attributes[attr] = value

    def remove_attribute(self, attr):
        ''' Removes an attribute key-value pair from the traceable item.

        Args:
            attr (str): Name of the attribute.
        '''
        if not attr:
            raise TraceabilityException('item {item}: cannot remove invalid attribute {attr}'
                                        .format(item=self.identifier, attr=attr),
                                        self.docname)
        del self.attributes[attr]

    def get_attribute(self, attr):
        ''' Gets the value of an attribute from the traceable item.

        Args:
            attr (str): Name of the attribute.
        Returns:
            str: Value matching the given attribute key, or '' if attribute does not exist.
        '''
        return self.attributes.get(attr, '')

    def get_attributes(self, attrs):
        ''' Gets the values of a list of attributes from the traceable item.

        Args:
            attr (list): List of names of the attribute
        Returns:
            list: List of values of the given attributes, '' is used as value for each attribute that does not exist
        '''
        return [self.get_attribute(attr) for attr in attrs]

    def iter_attributes(self):
        ''' Iterates over available attributes.

        Sorted as configured by an attribute-sort directive, with the remaining attributes naturally sorted.

        Returns:
            list: Sorted list containing available attributes in the item.
        '''
        sorted_attributes = [attr for attr in self.attribute_order if attr in self.attributes]
        sorted_attributes.extend(natsorted(set(self.attributes).difference(set(self.attribute_order))))
        return sorted_attributes

    def __str__(self, explicit=True, implicit=True):
        ''' Converts object to string.

        Args:
            explicit (bool)

        Returns:
            str: String representation of the item.
        '''
        retval = TraceableItem.STRING_TEMPLATE.format(identification=self.identifier)
        retval += '\tPlaceholder: {placeholder}\n'.format(placeholder=self.is_placeholder)
        for attribute in self.attributes:
            retval += '\tAttribute {attribute} = {value}\n'.format(attribute=attribute,
                                                                   value=self.attributes[attribute])
        if explicit:
            retval += self._relations_to_str(self.explicit_relations, 'Explicit')
        if implicit:
            retval += self._relations_to_str(self.implicit_relations, 'Implicit')
        return retval

    @staticmethod
    def _relations_to_str(relations, description):
        ''' Returns the string represtentation of the given relations.

        Args:
            relations (dict): Dictionary of relations.
            description (str): Description of the kind of relations.
        '''
        retval = ''
        for relation in relations:
            retval += '\t{text} {relation}\n'.format(text=description, relation=relation)
            for tgtid in relations[relation]:
                retval += '\t\t{target}\n'.format(target=tgtid)
        return retval

    def is_match(self, regex):
        ''' Checks if the item matches a given regular expression.

        Args:
            regex (str/re.Pattern): Regular expression pattern or object to match the given item against.

        Returns:
            bool: True if the given regex matches the item identification.
        '''
        if regex == '':
            return True
        try:
            return regex.match(self.identifier)
        except AttributeError:
            return re.match(regex, self.identifier)

    def attributes_match(self, attributes):
        ''' Checks if item matches a given set of attributes.

        Args:
            attributes (dict): Dictionary with attribute-regex pairs to match the given item against.

        Returns:
            bool: True if the given attributes match the item attributes.
        '''
        for attr, regex in attributes.items():
            if attr not in self.attributes:
                return False
            if regex == '':
                continue
            attribute_value = self.attributes[attr]
            try:
                if not regex.match(attribute_value):
                    return False
            except AttributeError:
                if not re.match(regex, attribute_value):
                    return False
        return True

    def is_related(self, relations, target_id):
        ''' Checks if a given item is related using a list of relationships.

        Args:
            relations (list): List of relations.
            target_id (str): Identifier of the target item.

        Returns:
            bool: True if given item is related through the given relationships, False otherwise.
        '''
        for relation in relations:
            if target_id in self.yield_targets(relation, explicit=True, implicit=True):
                return True
        return False

    def has_relations(self, relations):
        ''' Checks if the item has every relationship in given list.

        Args:
            relations (list): List of relations.

        Returns:
            bool: True if the item has every relationship in given list of list is empty, False otherwise.
        '''
        return set(relations).issubset(self.iter_relations(sort=False))

    def to_dict(self):
        ''' Exports item to a dictionary.

        Returns:
            dict: Dictionary representation of the object.
        '''
        data = {}
        if not self.is_placeholder:
            data = super(TraceableItem, self).to_dict()
            data['attributes'] = self.attributes
            data['targets'] = {}
            for relation in self.iter_relations():
                tgts = self.iter_targets(relation)
                if tgts:
                    data['targets'][relation] = tgts
        return data

    def self_test(self):
        ''' Performs self-test on collection content.

        Raises:
            TraceabilityException: Item is not defined.
            TraceabilityException: Item has an invalid attribute value.
            TraceabilityException: Duplicate target found for item.
        '''
        super().self_test()
        # Item should not be a placeholder
        if self.is_placeholder:
            raise TraceabilityException('item {item} is not defined'.format(item=self.identifier), self.docname)
        # Item's attributes should be valid, empty string is allowed
        for attribute in self.iter_attributes():
            value = self.attributes[attribute]
            if value is None or not TraceableItem.defined_attributes[attribute].can_accept(value):
                raise TraceabilityException('item {item} has invalid attribute value for {attribute}'
                                            .format(item=self.identifier, attribute=attribute))
        # Targets should have no duplicates
        for relation in self.iter_relations(sort=False):
            tgts = self.iter_targets(relation, sort=False)
            cnt_duplicate = len(tgts) - len(set(tgts))
            if cnt_duplicate:
                raise TraceabilityException('{cnt} duplicate target(s) found for {item} {relation})'
                                            .format(cnt=cnt_duplicate, item=self.identifier, relation=relation),
                                            self.docname)
