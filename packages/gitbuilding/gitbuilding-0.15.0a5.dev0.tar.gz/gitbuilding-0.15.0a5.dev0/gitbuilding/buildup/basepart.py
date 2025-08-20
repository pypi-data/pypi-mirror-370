'''
This submodule contains functionality to handle parts in the BuildUp documentation.
'''
from copy import copy, deepcopy
from dataclasses import dataclass, make_dataclass
import logging
from marshmallow import Schema, fields, post_load, ValidationError
from gitbuilding.buildup.link import BaseLink, LibraryLink, create_link_object
from gitbuilding.buildup.quantity import zero_quantity

_LOGGER = logging.getLogger('BuildUp')
class Part:
    """
    A part is anything that can be counted in the documentation. This includes
    components and tools that are used (UsedParts). And other parts created in
    a page (CreatedPart).
    """

    def __init__(self, link):
        self._name = link.linktext
        #Storing all links and calculate parts like the category on the fly.
        self._links = []
        self.count(link)

    def replicate(self):
        """
        Returns a replica of this part.
        """
        # pylint: disable=protected-access
        replica = copy(self)
        # This deepcopy is potentially an issue for fromstep links getting
        # resolved. It needs to be a deepcopy based on how multiplying pages
        # is handled by make links. If real issues arise some refactoring will be
        # needed
        replica._links = [deepcopy(link) for link in self._links]
        return replica

    @property
    def _all_locations(self):
        locations = []
        for link in self._links:
            if not link.location_undefined:
                locations.append(link.link_rel_to_root)
        return locations

    @property
    def original_link_obj(self):
        """
        Return the link object originally used to create this part
        """
        for link in self._links:
            if not link.location_undefined:
                return link
        return self._links[0]

    def link_needed_on_page(self, page):
        """
        The link location (uri) that must be specified on the input page
        to link to this item.
        `page` should be a string for the pages' path relative to root, the path should
        already be deduplicated.
        """
        return self.original_link_obj.link_needed_on_page(page)

    def get_part_data(self, doc):
        """
        Return the part data for the part. Requires the documentation object so
        it can scan libraries and pages to ge this data
        """
        link_obj = self.original_link_obj

        if isinstance(link_obj, LibraryLink):
            return doc.libs.get_part_data(*link_obj.library_location)

        page = doc.get_page_by_path(self.linklocation)
        if page is None:
            return None
        return page.part_data

    @property
    def _all_alttexts(self):
        alttexts = []
        for link in self._links:
            if link.alttext != '':
                alttexts.append(link.alttext)
        return alttexts

    @property
    def _all_qtys(self):
        qtys = []
        for link in self._links:
            if link.buildup_data.qty is not None:
                qtys.append(link.buildup_data.qty)
        return qtys

    @property
    def name(self):
        """
        Read-only property: The name of the part. This is equivalent to
        the text of the link in the build up.
        """
        return self._name

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
            qty = sum(all_qtys, zero_quantity())
        else:
            qty = None
        return qty

    def multiply_use(self, factor):
        for link in self._links:
            link.buildup_data.qty = link.buildup_data.qty*factor

    def get_links(self):
        """
        Returns the list of links that define this part
        """
        return self._links

    @property
    def linklocation(self):
        """
        Read-only property: The URL for the part relative to the root of the
        directory
        """
        locations = self._all_locations
        if len(locations) > 0:
            return locations[0]
        return ''

    @property
    def alttext(self):
        """
        Read-only property: The alttext for the part
        """
        alttexts = self._all_alttexts
        if len(alttexts) > 0:
            return ' '.join(alttexts)
        return ''

    @property
    def location_undefined(self):
        """
        Boolean read-only property True if no URL is defined.
        """
        return self.linklocation == ''

    @property
    def link_obj(self):
        """
        The part's link as a Link object
        """
        link_dict = {"fullmatch": None,
                     "overridetext": None,
                     "linktext": self.name,
                     "linklocation": self.linklocation,
                     "alttext": self.alttext,
                     "buildup_data": None}
        #make a link object relative to root
        return create_link_object(link_dict, 'index.md')

    def link_ref_md(self, url_translator):
        """
        Returns the markdown link reference for this part.
        """

        return self.link_obj.link_ref_md(url_translator)

    def __eq__(self, obj):
        """
        Two parts are considered equal if their names match. This allows use of
        inbuilt methods such as "in" and "index". A string or link will also compare
        to the part name.
        """

        if isinstance(obj, str):
            return self.name.lower() == obj.lower()
        if isinstance(obj, BaseLink):
            return self.name.lower() == obj.linktext.lower()
        if isinstance(obj, Part):
            return self.name.lower() == obj.name.lower()
        return NotImplemented

    def __lt__(self, obj):
        """
        Implemented to allow sorting of parts by name
        """

        if isinstance(obj, str):
            return self.name.lower() < obj.lower()
        if isinstance(obj, Part):
            return self.name.lower() < obj.name.lower()
        return NotImplemented

    def count(self, link):
        """
        Counts more of the same parts on a page..
        """
        checks = [self._check_link_location]
        self._count(link, checks)


    def _count(self, link, checks):
        if not isinstance(link, BaseLink):
            raise TypeError('Part.count expects a Link object')
        if link.linktext != self:
            raise ValueError(f'Cannot count the link as the linktext "{link.linktext}"'
                             f'does not equal the partname "{self.name}"')
        for check in checks:
            check(link)
        self._links.append(link)

    def _check_link_location(self, link):
        if not link.location_undefined:
            locations = self._all_locations
            if len(locations) > 0 and link.link_rel_to_root != locations[0]:
                _LOGGER.warning('Location multiply defined on this page for %s', self.name)

class _LaxStrFeild(fields.Str):
    """
    The is a subclass of field.Str that coerces float and integer objects into
    strings rather than warning
    """

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, float):
            value = str(value)
        elif isinstance(value, int):
            value = str(value)
        return super()._deserialize(value, attr, data, **kwargs)

class _SuppliersField(fields.Dict):
    """
    _SuppliersField is used by marshmallow to serialise and de-serialise
    the data from all suppliers.
    """

    def __init__(self, **kwargs):
        kwargs['keys'] = fields.Str()
        kwargs['values'] = _ProductsField()
        super().__init__(**kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        processed_dict = super()._deserialize(value, attr, data, **kwargs)
        if processed_dict is None:
            return processed_dict
        suppliers = []
        buildup_supplier = make_dataclass('BuildUpSupplier',
                                          ['name', 'products'])
        for key in processed_dict:
            supplier_obj = buildup_supplier(name=key,
                                            products=processed_dict[key])
            suppliers.append(supplier_obj)
        return suppliers


class ProductSchema(Schema):
    """
    A simple marshmallow schema for the data for each product lists for
    a supplier in part data. Returns this as a dataclass
    """
    partno = _LaxStrFeild(data_key='PartNo', required=True)
    link = fields.Str(data_key='Link')

    @post_load
    def _make_object(self, data, **_):
        buildup_product = make_dataclass('BuildUpProduct',
                                         data.keys())
        return buildup_product(**data)

class _ProductsField(fields.Dict):
    """
    _ProductsField is used by marshmallow to serialise and de-serialise
    the product data for a supplier listed in the part data.
    """

    def __init__(self, **kwargs):
        kwargs['keys'] = fields.Str()
        kwargs['values'] = _LaxStrFeild()
        super().__init__(**kwargs)

    def _validate_all_products(self, products):
        prod_schema = ProductSchema()
        validated_products = []
        for product in products:
            validated_products.append(prod_schema.load(product))
        return validated_products

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, list):
            products = []
            for sub_val in value:
                products.append(super()._deserialize(sub_val, attr, data, **kwargs))
        elif isinstance(value, dict):
            products = [super()._deserialize(value, attr, data, **kwargs)]
        else:
            raise ValidationError('Supplier data is corrupted')
        return self._validate_all_products(products)

class PartDataSchema(Schema):
    """
    A marshmallow schema for parsing the dara for each item in a part library
    """
    name = fields.Str(data_key='Name')
    description = fields.Str(data_key='Description', load_default=None, allow_none=True)
    specs = fields.Dict(load_default=None,
                        allow_none=True,
                        keys=fields.Str(),
                        values=_LaxStrFeild(),
                        data_key='Specs')
    suppliers = _SuppliersField(data_key='Suppliers', load_default=None, allow_none=True)

    @post_load
    def _make_part_data(self, data, **_):
        return PartData(**data)

@dataclass
class PartData:
    """
    Part data and object that represents the YAML data that sets information
    about the parts that need to be purchased. This is the data specific to the
    item (Such as the supplier, the material specifications, etc) not the data
    about how it is used within the documentation (This data his held in the
    UsedPart class).
    """
    name: str
    description: str
    specs: dict
    suppliers: list

    @property
    def markdown(self):
        """
        Generates the markdown for a part from a part library
        """

        md = f'# {self.name}\n\n'
        if self.description is not None:
            md += f'{self.description}\n\n'
        if self.specs is not None:
            md += self._specs_markdown()
        if self.suppliers is not None:
            md += self._supplier_markdown()
        return md

    @property
    def page_markdown(self):
        """
        Generates the markdown for part data in the fontmatter of a page
        """

        md = '\n\n---\n\n'
        if self.specs is not None:
            md += self._specs_markdown()
        if self.suppliers is not None:
            md += self._supplier_markdown()
        return md

    def _specs_markdown(self):
        """
        Generates the markdown for the specifications for part from a part library
        """

        md = "\n\n## Specifications\n\n|Attribute |Value|\n|---|---|\n"
        for key in self.specs:
            md += f'|{key}|{self.specs[key]:}|\n'
        return md

    @property
    def product_list(self):
        """
        Return list of all products listed for in this part data as tuples of supplier,
        part number, and link
        """
        all_products = []
        if self.suppliers is not None:
            for supplier in self.suppliers:
                for product in supplier.products:
                    try:
                        all_products.append((supplier.name, product.partno, product.link))
                    except AttributeError:
                        _LOGGER.warning('Incomplete product information provided. Supplier: '
                                        ' %s, Product: %s', supplier.name, self.name)
        return all_products

    def _supplier_markdown(self):
        """
        Generates the markdown for the suppliers of a part from a part library
        """
        kramdown = '{:target="_blank"}'
        md = "\n\n## Suppliers\n\n|Supplier |Part Number|\n|---|---|\n"
        for product in self.product_list:
            md += f"|{product[0]}|[{product[1]}]({product[2]}){kramdown}|\n"
        return md
