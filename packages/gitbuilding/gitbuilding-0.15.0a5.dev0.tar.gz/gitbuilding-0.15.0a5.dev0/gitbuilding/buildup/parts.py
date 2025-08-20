'''
This submodule contains functionality to count parts used or created in buildup
documentation.
UsedPart is a child class of Part, it is used to track the usage of parts.
CreatedPart is a child class of Part, it is used to track parts that are made.

Part is defined in the basepart submodule
'''

import logging
from gitbuilding.buildup.basepart import Part
from gitbuilding.buildup.quantity import largest_quantity, zero_quantity, remaining_quantity
from gitbuilding.buildup.link import FromStepLink
from gitbuilding.buildup.buildup import proccess_buildup_snippet

_LOGGER = logging.getLogger('BuildUp')

class UsedPart(Part):
    """
    This class represents a particular part used in the documentation such as
    "M3x6mm Cap Head Screws". UsedPart is a child class of Part.
    It handles counting the quantity of the part used, its category, and notes
    about usage etc.
    """

    def __init__(self, link, config):
        self._config = config
        super().__init__(link)

    @property
    def from_step(self):
        """
        Boolean property for whether the used part is an output of a previous step,
        created with a fromstep link. See also made_earlier
        """
        for link in self._links:
            if isinstance(link, FromStepLink):
                return True
        return False

    @property
    def to_make(self):
        """
        Boolean property for whether the used part is to be made (i.e. set with a make link)
        """
        for link in self._links:
            if link.is_make:
                return True
        return False

    def made_earlier(self):
        """
        Boolean property for whether the used part is made earlier in the documentation
        this could be using a make link or a fromstep link.
        """
        if self.from_step:
            return True
        if self.to_make:
            return True
        return False

    @property
    def _all_categories(self):
        categories = []
        for link in self._links:
            if link.buildup_data.category is not None:
                categories.append(link.buildup_data.category)
        return categories

    @property
    def _all_totals(self):
        total_qtys = []
        for link in self._links:
            if link.buildup_data.total_qty is not None:
                total_qtys.append(link.buildup_data.total_qty)
        return total_qtys

    @property
    def category(self):
        """
        Read-only property: The category of the part.
        """
        categories = self._all_categories
        if len(categories) == 0:
            return self._config.default_category
        return categories[0]

    @property
    def qty(self):
        """
        Read-only property: The total quantity of this part used in references
        in the text. This differs from total_qty as total_qty can be set explicitly.
        If total_qty is not set then total_qty will be set equal to qty. If
        total_qty is set and doesn't match qty a warning will be logged.
        """

        all_qtys = self._all_qtys
        if len(all_qtys) > 0:
            if self._config.categories[self.category].reuse:
                qty = largest_quantity(all_qtys)
            else:
                qty = sum(all_qtys, zero_quantity())
        else:
            qty = None
        return qty

    def multiply_use(self, factor):
        if not self._config.categories[self.category].reuse:
            for link in self._links:
                link.buildup_data.qty = link.buildup_data.qty*factor

    @property
    def total_qty(self):
        """
        Read-only property: The total quantity of the part used in the
        partlist it is indexed in.
        """
        qty = self.qty
        total_qtys = self._all_totals
        if len(total_qtys) > 0:
            if self._config.categories[self.category].reuse:
                total_qty = largest_quantity(total_qtys)
            else:
                #Note totals can be defined on multiple pages so must be added.
                total_qty = sum(total_qtys, zero_quantity())
            if total_qty != qty:
                _LOGGER.warning('Total quantity for %s was explicity set as %s but only %s used',
                                self.name,
                                total_qty,
                                qty)
        else:
            total_qty = qty
        return total_qty

    @property
    def note(self):
        """
        Read-only property: this returns any notes defined for the part
        """
        return self.get_note(None, False)

    def get_note(self, url_translator, formatted=True, leading_dash=True):
        """
        Return the note, optionally can be formatted such as translating any links
        """
        note_txt = None
        n = 0
        for link in self._links:
            if link.buildup_data.note is not None:
                n += 1
                this_note = link.buildup_data.note
                if formatted:
                    this_note = proccess_buildup_snippet(this_note,
                                                         link.page,
                                                         url_translator)
                if note_txt is None:
                    note_txt = ''
                if n>1 or leading_dash:
                    note_txt += ' - ' + this_note
                else:
                    note_txt += this_note
        return note_txt


    def __str__(self):
        return (f"{self.name:}\n"
                f"uri:       {self.linklocation}\n"
                f"category:  {self.category}\n"
                f"Total Qty: {self.total_qty}\n"
                f"Qty Used:  {self.qty}\n")

    def combine(self, part):
        """
        Combines two copies of the same part. Combine is different from counting,
        combine is the operation when two lists are merged.
        """

        if not isinstance(part, Part):
            raise TypeError("A UsedPart object can only combine with another a Part object")
        if part != self:
            raise RuntimeError("Parts must have the same name to be combined")
        if isinstance(part, CreatedPart):
            raise RuntimeError("You can't combine a created part into part. You must combine"
                               " the other way around")
        if self.linklocation != part.linklocation:
            _LOGGER.warning('The part "%s" is defined on multiple pages with different URIs. '
                            ' This may cause an inconsistent bill of materials.' ,
                            self.name)
        if self.category != part.category:
            _LOGGER.warning('The part "%s" is defined on multiple pages with different '
                            'categories. This may cause an inconsistent bill of materials.',
                            self.name)
        if self.from_step != part.from_step:
            _LOGGER.warning('Whether the part "%s" is created in a previous step is '
                            'inconsistently defined between pages. Try setting all URLs'
                            'to "FromStep"',
                            self.name)
        self._links += part.get_links()

    def count(self, link):
        """
        Counts more of the same part on a page. This is not used when merging two
        lists of parts for merging lists see combine.
        """
        if link.is_output:
            _LOGGER.warning("Cannot define %s as an outout as it is already used as"
                            "a part on this page.", self.name)
        checks = [self._check_link_total,
                  self._check_link_category,
                  self._check_link_location]
        self._count(link, checks)

    def _check_link_total(self, link):
        if link.buildup_data.total_qty is not None:
            if len(self._all_totals) > 0:
                _LOGGER.warning('TotalQty multiply defined on this page for %s', self.name)
                # Dont add total quantity twice even if consistent as it will get double the
                # total
                link.buildup_data.total_qty = None

    def _check_link_category(self, link):
        if link.buildup_data.category is not None:
            if link.buildup_data.category not in self._config.categories:
                _LOGGER.warning("No valid category %s. You can define custom categories"
                                " in the config file.",
                                link.buildup_data.category)
                link.buildup_data.category = None
            else:
                cats = self._all_categories
                if len(set(cats)) == 1 and link.buildup_data.category != cats[0]:
                    # Only warn if categories are currently consistent
                    _LOGGER.warning('Category is inconsistently defined for %s', self.name)

    def bom_line(self, url_translator, no_links):
        '''
        Writes the markdown line for the bill of materials
        '''
        appended_class = ""
        total_qty = self.total_qty
        if total_qty is None:
            return ""
        qty_str = total_qty.formatted

        if self.location_undefined and not self.from_step:
            appended_class = '{: Class="missing"}'
        else:
            appended_class = '{: Class="bom"}'

        note = self.get_note(url_translator, formatted=True)
        if note is None:
            note_txt = ""
        else:
            note_txt = "  " + note

        if no_links:
            link = self.name
        else:
            link = f"[{self.name}]{appended_class}"
        return f"* {qty_str} {link} {note_txt}\n"

class CreatedPart(Part):
    """
    This is the class items that are created in BuildUp documentation.
    CreatedParts are created using "output". This class isn't called "Output" as this
    may get confused with the output documentation.
    """

    def __init__(self, link):
        self._used = None
        super().__init__(link)

    def count(self, link):
        """
        Counts more of the same parts baordson a page..
        """
        if len(self._links) == 0:
            self._links.append(link)
        else:
            if link.is_output:
                _LOGGER.warning('Attempting to redefine the output %s. Outputs can'
                                ' be defined multiple times only if the pages'
                                ' that define them are not steps of the same page.',
                                self.name)
            else:
                _LOGGER.warning('Using an output on the same page it is defined is'
                                'not supported. It is something that may be allowed'
                                'as BuildUp evolves.')

    def combine(self, part):
        """
        Combine is used when merging part lists as a CreatedPart combine represents use of
        the part
        """
        if not isinstance(part, Part):
            raise TypeError("A CreatedPart object can only combine with another a Part object")
        if part != self:
            raise RuntimeError("Parts must have the same name to be combined")
        if isinstance(part, CreatedPart):
            _LOGGER.warning("The part %s is alread defined as an output",
                            self.name)
            return
        if not part.made_earlier:
            _LOGGER.warning('The part %s is alread defined as an output. To use this part change '
                            'the link url to "FromStep"',
                            self.name)
            #Not returing here, may cause some weird link, but should count correctly.
        if self._used is None:
            self._used = part.replicate()
        else:
            self._used.combine(part)
        #Calculate remaining to warn if more are used than created.
        self._calculate_remaining()

    @property
    def qty_created(self):
        """
        The total quantity of the output that was created. For the quantity that
        remains after use see `qty`
        """
        all_qtys = self._all_qtys
        if len(all_qtys) == 1:
            return all_qtys[0]
        return zero_quantity()

    def _calculate_remaining(self):
        try:
            return remaining_quantity(self.qty_created, self._used.qty)
        except ValueError:
            _LOGGER.warning('A greater number of %s were used (%s) than created (%s)',
                            self.name,
                            self._used.qty,
                            self.qty_created)
        return zero_quantity()

    @property
    def qty(self):
        """
        The quantity that remains after use. For the total quantity created see
        `qty_created`
        """
        return self._calculate_remaining()
