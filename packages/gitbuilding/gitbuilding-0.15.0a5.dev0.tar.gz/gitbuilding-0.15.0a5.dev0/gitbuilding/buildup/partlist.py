'''
This submodule contains functionality to handle lists of parts in the BuildUp
documentation.
'''

import logging
from gitbuilding.buildup.basepart import Part
from gitbuilding.buildup.parts import UsedPart
from gitbuilding.buildup.parts import CreatedPart

_LOGGER = logging.getLogger('BuildUp')
class PartList:
    """
    PartLists are lists of Part objects. They have functions that allow them to
    safely add parts and to be merged.
    """

    def __init__(self, config):

        self._parts = []
        self._config = config

    def __getitem__(self, ind):
        return self._parts[ind]

    def __setitem__(self, ind, part):
        if not isinstance(part, Part):
            raise TypeError("Can only store Part objects in a PartList")
        self._parts[ind] = part

    def __len__(self):
        return len(self._parts)

    def _append(self, part):
        """
        Appends a new part into the list, this function is used by count_link
        if no matching part exists.
        """

        if not isinstance(part, Part):
            raise TypeError("Can only append Part objects to a PartList")

        self._parts.append(part)

    def index(self, part):
        """
        Works as index for a list but uses the __eq__ method of Part objects
        in the part list
        """
        return self._parts.index(part)

    def getpart(self, part):
        """
        Returns the part object from the list that matches input "part"
        uses the __eq__ method of Parts, so this input could be a Part
        object or a string
        """
        if part in self._parts:
            return self._parts[self.index(part)]
        return None

    @property
    def used_parts(self):
        """
        Only the parts that are used not the ones that were created.
        """
        return [part for part in self._parts if isinstance(part, UsedPart)]

    def merge(self, inputlist, multiply_by=None):
        """
        Merges in another partlist
        """
        if not isinstance(inputlist, PartList):
            raise TypeError("Can only merge a PartList to another PartList")
        for part in inputlist:
            part = part.replicate()
            if multiply_by is not None:
                part.multiply_use(multiply_by)
            matching_part = self.getpart(part)
            if matching_part is None:
                self._append(part)
            else:
                if isinstance(matching_part, UsedPart) and isinstance(part, CreatedPart):
                    part.combine(matching_part)
                    # swap the parts in the list to put the created one first
                    self._parts[self.index(matching_part)] = part
                    # Warn is the part was created by from_step link
                    if matching_part.from_step:
                        _LOGGER.warning("The part %s is defined as an output after "
                                        "it is already used.",
                                        matching_part.name)
                else:
                    matching_part.combine(part)

    def count_link(self, link):
        """
        Takes the information from a link and stores it in the coresponding UsedPart
        object so the information is counted when the bill of materials is created
        If it a matching doesn't exist, one is created.
        """

        part = self.getpart(link)
        if part is None:
            if link.is_output:
                self._append(CreatedPart(link))
            else:
                self._append(UsedPart(link, self._config))
        else:
            part.count(link)

    def link_refs_md(self, url_translator, excludelist=None):
        """
        Returns the markdown link reference for each part. All links are translated
        with the url_translator. Parts can be excluded using the excludelist.
        """
        linktext = ""

        if excludelist is None:
            excludelist = []

        for part in self.used_parts:
            if part not in excludelist:
                linktext += f"{part.link_ref_md(url_translator)}\n"
        return linktext

    def bom_md(self, title, url_translator, divide=True, exclude_refs=None, intro=None, no_links=False):
        """
        Creates the bill of materials in markdown format.
        Can set whether it also includes the link references for each
        part, and whether they are divided by categories

        The `divide` argument means the bill of materials will have headings
        for each of the part categories when set to `True` (the default).
        """
        sorted_parts = sorted(self.used_parts)
        bom_text = ""
        if title != "":
            bom_text += f"{title}\n\n"
        if intro is not None:
            bom_text += intro
            bom_text += "\n\n"
        # Loop through parts and put quantities and names in md
        if divide:
            for category in self._config.categories:
                catname = self._config.categories[category].display_name
                first = True
                for part in sorted_parts:
                    if part.category == category:
                        if first:
                            first = False
                            bom_text += f"\n\n### {catname} \n\n"

                        bom_text += part.bom_line(url_translator, no_links)
        else:
            for part in sorted_parts:
                bom_text += part.bom_line(url_translator, no_links)
        if not no_links:
            bom_text += self.link_refs_md(url_translator, exclude_refs)
        bom_text += "\n\n"
        return bom_text

    def bom_csv(self, doc):
        """
        Outputs a bill of materials in character-separated values format.
        Tab-separated is the only option for now.
        """
        sorted_parts = sorted(self.used_parts)
        entries = []
        max_products = 0
        for part in sorted_parts:
            part_data = part.get_part_data(doc)
            entries.append((part, part_data))
            if part_data is not None:
                num_products = len(part_data.product_list)
                if num_products > max_products:
                    max_products = num_products

        csv = ""
        headings = ["Name in documentation", "Category", "Qty", "Full Name", "Notes"]
        for n in range(max_products):
            headings += [f"Supplier {n+1}", "Part No", "Link"]
        csv += "\t".join(headings)
        csv += "\n"

        for part, part_data in entries:
            #somewhat ugly double list comprehension to flatten the list of tuples into a flat list
            if part_data is None:
                flat_products = []
                part_data_name = ""
            else:
                flat_products = [item for product in part_data.product_list for item in product]
                part_data_name = part_data.name
            part_note = part.get_note(None, False, False)
            if part_note is None:
                part_note = ''
            #calculate extra columns to pad row
            extra_cols = 3*max_products - len(flat_products)
            part_data_csv = [part.name,
                             str(part.category),
                             str(part.qty),
                             part_data_name,
                             part_note]
            row = part_data_csv + flat_products + ['']*extra_cols
            csv += "\t".join(row)
            csv += "\n"
        return csv

class GlobalPartList(PartList):
    """
    The global partlist is only used listing all parts ever used. As such
    it doesn't need created parts. The total quantities are meaningless
    """

    def merge(self, inputlist, _=None):
        """
        Merges in another partlist
        """
        if not isinstance(inputlist, PartList):
            raise TypeError("Can only merge a PartList to another PartList")
        for part in inputlist:
            #for the global list we are only checking the used parts.
            if isinstance(part, UsedPart):
                matching_part = self.getpart(part)
                if matching_part is None:
                    self._append(part.replicate())
                else:
                    matching_part.combine(part)
