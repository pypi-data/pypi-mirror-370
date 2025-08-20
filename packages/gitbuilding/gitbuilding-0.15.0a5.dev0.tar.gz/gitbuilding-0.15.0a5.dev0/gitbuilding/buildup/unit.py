"""
This sub-module deals with units and unit conversion. Unlike other more advanced
unit modules like `pint` this module only deals with physical quantities of length,
area, volume, and mass. It is built from the ground up to group units with similar
units for preffered conversions. UnitGroups are then related in a tree like definition
structure so conversions (hopefully) automatically choose an appropriate unit.
"""
from fractions import Fraction

class Unit:
    """
    This class defined a list of possible names for a unit. It containts no other
    information. The first name in the definition is the preffered name. This class
    registers as equal to any string equal to one of the unit's names. This means
    strings can always be used in place of a Unit object when using the funtions
    in UnitLibrary and UnitGroup.
    """

    def __init__(self, names, case_insensitive_names=None):
        self._names = names
        self._case_insensitive_names = case_insensitive_names
        if self._case_insensitive_names is None:
            self._case_insensitive_names = []
        self._check_names()

    @property
    def name(self):
        """
        Return the prefered name of this unit
        """
        return self._names[0]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Unit {self.name}>"

    def __eq__(self, string):
        if isinstance(string, str):
            return string in self._names or string.lower() in self._case_insensitive_names
        return NotImplemented

    def _check_names(self):
        if not isinstance(self._names, list):
            raise TypeError('`names` must be a list of strings')
        if not isinstance(self._case_insensitive_names, list):
            raise TypeError('`case_insensitive_names` must be a list of strings')
        for name in self._names:
            if not isinstance(name, str):
                raise TypeError('`names` must be a list of strings')
        for n, name in enumerate(self._case_insensitive_names):
            if not isinstance(name, str):
                raise TypeError('`case_insensitive_names` must be a list of strings')
            self._case_insensitive_names[n] = name.lower()

class UnitGroup:
    """
    A UnitGroup is a group of similar units such as a uL, mL, L, and the scalins between them.
    The inputs are, the base unit for the group, a list of tuples of the form (Unit, scale)
    where scale is the scaling from the unit to the base unit as an int, float, or Fraction
    Optional inputs parent_group and parent_scale should either both be set or neither should
    be set. The parent_group is another group of units of a more primary definition for the
    same quanity. The scale is between the base units of the two groups.
    """
    def __init__(self, base_unit, unit_scalings, parent_group=None, parent_scale=None):

        self._unit_scalings = unit_scalings
        self._unit_scalings.append((base_unit, 1))
        self._base_unit = base_unit
        self._units = [unit_scaling[0] for unit_scaling in self._unit_scalings]

        self._parent_group = parent_group
        if parent_group is None:
            self._parent_scale = None
        else:
            if not isinstance(parent_group, UnitGroup):
                raise TypeError('The parent_group of a UnitGroup must be a unit group')
            if not isinstance(parent_scale, (int, float, Fraction)):
                raise TypeError('The parent_scale of a UnitGroup must be an int, '
                                'str, or Fraction')
            self._parent_scale = parent_scale

    def __getitem__(self, ind):
        return self._units[ind]

    def __len__(self):
        return len(self._units)

    def index(self, other):
        """
        Works as index for a list but indexes the list of units
        """
        return self._units.index(other)

    def __repr__(self):
        return f"<UnitGroup-base={self.base_unit}>"

    def get_scale(self, other):
        """
        Returns the scale of the input unit relative to the base unit. The unit
        must be in this UnitGroup.
        """
        ind = self.index(other)
        return self._unit_scalings[ind][1]

    @property
    def base_unit(self):
        """
        Returns the base unit of this group
        """
        return self._base_unit

    @property
    def parent_group(self):
        """
        Returns the parent unit group of this group
        """
        return self._parent_group

    @property
    def unit_scalings(self):
        """
        Returns list of tuples of (Unit, scale) that describe all the units in
        this group
        """
        return self._unit_scalings

    @property
    def parent_scale(self):
        """
        Returns the scaling between the base unit of this group and the base unit
        of the parent groups base unit
        """
        return self._parent_scale

    @property
    def get_parent_list(self):
        """
        Returns a list of all UnitGroups that are parent to this group.
        The first in the list is the primary definition of the quanity (e.g. the mg,
        g, kg) group for mass, then all other groups in the definition chain upto
        and including this group.
        """
        if self._parent_group is None:
            return [self]
        parent_list = self._parent_group.get_parent_list
        parent_list.append(self)
        return parent_list

    def convertable(self, other):
        """
        Returns a boolean value stating whether units in this UnitGroup and and
        units in the input UnitGroup can be converted
        """
        return self.get_parent_list[0] == other.get_parent_list[0]

    def preffered_group(self, other):
        """
        The preffered unit group when combining units in the group and the input
        group. This is the colses common relative group in the definition chains
        of the groups.
        """
        own_list = self.get_parent_list
        other_list = other.get_parent_list

        shortest_len = min(len(own_list), len(other_list))
        n = 0
        while n < shortest_len and own_list[n] == other_list[n]:
            n += 1
        if n == 0:
            raise RuntimeError(f"UnitGroups {self} and {other} are not convertable")
        return own_list[n-1]

    def get_parent_group_scale(self, other):
        """
        Returns the scaling between this group and the input group. The input group
        must be a parent of this group.
        """
        plist = self.get_parent_list
        try:
            conv_path = plist[plist.index(other)+1:]
        except ValueError as err:
            raise RuntimeError(f"UnitGroups {other} is not a parent of {self}") from err
        scale = 1
        for group in conv_path:
            scale *= group.parent_scale
        return scale

class UnitLibrary:
    """
    This class defines all Units and UnitGroups, it holds the list of all unit groups.
    The library can be used to check if units are convertable, the preffered unit for
    this conversion, and the scalings for the conversion. It can also be used to scale
    quantities to a more appropriate unit inside a UnitGroup.
    """

    def __init__(self):
        self.all_groups = []
        self._init_mass()
        self._init_lengths()
        self._init_areas()
        self._init_volumes()

    def _init_mass(self):
        microgramme = Unit(['μg', 'ug'],
                           ['microgramme', 'microgram', 'microgrammes', 'micrograms'])
        milligramme = Unit(['mg'],
                           ['milligramme', 'milligram', 'milligrammes', 'milligrams'])
        gramme = Unit(['g'],
                      ['gramme', 'gram', 'grammes', 'grams'])
        kilogramme = Unit(['kg'],
                          ['kilogramme', 'kilogram', 'kilorammes', 'kilograms'])
        tonne = Unit(['tonne', 'Mg'],
                     ['tonne', 'metric ton', 'megagramme', 'megagram',
                      'megarammes', 'megagrams'])

        # Note the use of g not kg as the base unit despite this not being the SI
        # definition. This is not important as when we convert between lists we
        # auto scale. It just means I don't have to remember to multiply by a factor
        # of 10^3!
        gramme_scales = [(microgramme, 1e-6),
                         (milligramme, 0.001),
                         (kilogramme, 1000),
                         (tonne, 1e6)]
        grammes = UnitGroup(gramme, gramme_scales)
        self.all_groups.append(grammes)

    def _init_lengths(self):
        metre = Unit(['m'], ['metre', 'meter', 'metres', 'meters'])
        millimetre = Unit(['mm'],
                          ['millimetre', 'millimeter', 'millimetres', 'millimeters'])
        kilometre = Unit(['km'],
                         ['kilometre', 'kilometer', 'kilometres', 'kilometers'])
        met_len_scales = [(millimetre, 1e-3),
                          (kilometre, 1e3)]
        metric_lengths = UnitGroup(metre, met_len_scales)
        self.all_groups.append(metric_lengths)

        centimetre = Unit(['cm'],
                          ['centimetre', 'centimeter', 'centimetres', 'centimeters'])
        secondary_metric_lengths = UnitGroup(centimetre, [], metric_lengths, 1e-2)
        self.all_groups.append(secondary_metric_lengths)

    def _init_areas(self):
        sq_metre = Unit(['m^2'], ['metre^2', 'meter^2', 'metres^2', 'meters^2'])
        sq_millimetre = Unit(['mm^2'],
                             ['millimetre^2', 'millimeter^2', 'millimetres^2', 'millimeters^2'])
        sq_kilometre = Unit(['km^2'],
                            ['kilometre^2', 'kilometer^2', 'kilometres^2', 'kilometers'])
        met_area_scales = [(sq_millimetre, 1e-6),
                           (sq_kilometre, 1e6)]
        metric_areas = UnitGroup(sq_metre, met_area_scales)
        self.all_groups.append(metric_areas)

        sq_centimetre = Unit(['cm^2'],
                             ['centimetre^2', 'centimeter^2', 'centimetres^2', 'centimeters^2'])
        secondary_metric_areas = UnitGroup(sq_centimetre, [], metric_areas, 1e-4)
        self.all_groups.append(secondary_metric_areas)

    def _init_volumes(self):
        microlitre = Unit(['μL', 'μl', 'uL', 'ul'],
                          ['microlitre', 'microliter', 'microlitres', 'microliters'])
        millilitre = Unit(['mL', 'ml'],
                          ['millilitre', 'milliliter', 'millilitres', 'milliliters'])
        litre = Unit(['L', 'l'],
                     ['litre', 'liter', 'litres', 'liters'])
        litre_scales = [(millilitre, 0.001),
                        (microlitre, 1e-6)]
        litres = UnitGroup(litre, litre_scales)
        self.all_groups.append(litres)

        metrescubed = Unit(['m^3'], ['metre^3', 'meter^3', 'metres^3', 'meters^3'])
        cubic_cm = Unit(['cm^3'],
                        ['centimetre^3', 'centimeter^3', 'centimetres^3', 'centimeters^3',
                         'cc'])
        cubic_mm = Unit(['mm^3'],
                        ['millimetre^3', 'millimeter^3', 'millimetres^3', 'millimeters^3'])
        met_vol_scales = [(cubic_cm, 1e-6),
                          (cubic_mm, 1e-9)]
        metric_volumes = UnitGroup(metrescubed, met_vol_scales, litres, 1000)
        self.all_groups.append(metric_volumes)

    def get_group(self, unit):
        """
        Returns the group that containts the input unit
        """
        for group in self.all_groups:
            if unit in group:
                return group
        return None

    def convertable(self, unit1, unit2):
        """
        Returns a boolean value which is true if unit1 can be converted to unit2 (and
        vise-versa)
        """
        unit_group1 = self.get_group(unit1)
        if unit_group1 is None:
            return False
        unit_group2 = self.get_group(unit2)
        if unit_group2 is None:
            return False
        return unit_group1.convertable(unit_group2)

    def unify_units(self, unit1, unit2):
        """
        Returns the scaling factors to convert quantities if unit1 and unit2
        into the preerred unit. The outputs are:
        unit1_scale: the scale to multiply quanity1 by to covert to the preffered unit
        unit2_scale: the scale to multiply quanity2 by to covert to the preffered unit
        preffered_unit: the preffered unit - note this is the base unit in the preffered
        group. The quanity may need to be scaled
        """
        if not self.convertable(unit1, unit2):
            raise RuntimeError(f'Cannot convert {unit1} into {unit2}')
        unit_group1 = self.get_group(unit1)
        unit_group2 = self.get_group(unit2)
        pref_group = unit_group1.preffered_group(unit_group2)
        group_scale1 = unit_group1.get_parent_group_scale(pref_group)
        group_scale2 = unit_group2.get_parent_group_scale(pref_group)
        unit1_basescale = unit_group1.get_scale(unit1)
        unit2_basescale = unit_group2.get_scale(unit2)
        unit1_scale = unit1_basescale*group_scale1
        unit2_scale = unit2_basescale*group_scale2
        return unit1_scale, unit2_scale, pref_group.base_unit

    def scale_quantity(self, value, unit):
        """
        Scales the quantiy described by the input value and unit. The output is
        an equivalent value and unit. The new unit is in the same UnitGroup.
        """
        unit_group = self.get_group(unit)
        if unit_group is None:
            raise RuntimeError('Unknown unit {unit} cannot be scaled')
        unit_scalings = unit_group.unit_scalings
        value_in_base = value*unit_group.get_scale(unit)
        values = [value_in_base/unit_scaling[1] for unit_scaling in unit_scalings]
        values_gt_1 = [value for value in values if value >= 1]
        if len(values_gt_1) > 0:
            value = min(values_gt_1)
        else:
            value = max(values)
        ind = values.index(value)
        unit = unit_scalings[ind][0]
        return value, unit
