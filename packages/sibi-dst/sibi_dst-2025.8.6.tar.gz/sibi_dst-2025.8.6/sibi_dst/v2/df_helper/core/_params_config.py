from typing import Optional, Dict, Union, List

from pydantic import BaseModel, model_validator, Field

dataframe_params: Dict[str, Union[None, str, bool, int, None]] = {
    "fieldnames": None,
    "index_col": None,
    "coerce_float": False,
    "verbose": True,
    "datetime_index": False,
    "column_names": None,
    "chunk_size": 1000,
}
# dataframe_options is a dictionary that provides additional options for modifying a pandas DataFrame.
# These options include parameters for handling duplicate values, sorting, grouping, and other DataFrame operations.

dataframe_options: Dict[str, Union[bool, str, int, None]] = {
    "debug": False,  # Whether to print debug information
    "duplicate_expr": None,  # Expression for identifying duplicate values
    "duplicate_keep": 'last',  # How to handle duplicate values ('first', 'last', or False)
    "sort_field": None,  # Field to use for sorting the DataFrame
    "group_by_expr": None,  # Expression for grouping the DataFrame
    "group_expr": None  # Expression for aggregating functions to the grouped DataFrame
}

LOOKUP_SEP = "__"


class ParamsConfig(BaseModel):
    """
    Defines a configuration model for parameters with functionality for parsing,
    validation, and conversion of legacy filters.

    This class extends BaseModel from Pydantic and is designed to handle multiple
    sets of configurations, including field mappings, filters, dataframe parameters,
    and dataframe options. It allows for flexible parsing of parameters across a
    variety of supported structures and ensures that legacy filters can be
    appropriately converted for compatibility.

    :ivar field_map: Maps field names to their equivalent legacy field names.
    :type field_map: Optional[Dict]
    :ivar legacy_filters: Indicates whether legacy filters should be processed.
    :type legacy_filters: bool
    :ivar sticky_filters: Stores additional filters as key-value pairs that persist
        across parameter parsing.
    :type sticky_filters: Dict[str, Union[str, bool, int, float, list, tuple]]
    :ivar filters: Holds all the current filters including sticky and dynamically
        parsed filters.
    :type filters: Dict[str, Union[str, Dict, bool, int, float, list, tuple]]
    :ivar df_params: Contains parameters related to dataframe configurations in a
        structured format.
    :type df_params: Dict[str, Union[tuple, str, bool, None]]
    :ivar df_options: Stores optional configurations for a dataframe, allowing for
        additional behavior customization.
    :type df_options: Dict[str, Union[bool, str, None]]
    :ivar params: Dictionary of parameters provided for configuration, supporting
        both basic and nested structures.
    :type params: Dict[str, Union[str, bool, int, float, List[Union[str, int, bool, float]]]]
    """
    field_map: Optional[Dict] = Field(default_factory=dict)
    legacy_filters: bool = False
    sticky_filters: Dict[str, Union[str, bool, int, float, list, tuple]] = Field(default_factory=dict)
    filters: Dict[str, Union[str, Dict, bool, int, float, list, tuple]] = Field(default_factory=dict)
    df_params: Dict[str, Union[tuple, str, bool, None]] = Field(default_factory=dict)
    df_options: Dict[str, Union[bool, str, None]] = Field(default_factory=dict)
    params: Dict[str, Union[str, bool, int, float, List[Union[str, int, bool, float]]]] = Field(default_factory=dict)

    @model_validator(mode='after')
    def check_params(self):
        if self.params is not None:
            self.parse_params(self.params)
        return self

    def parse_params(self, params):
        """
        Parses and separates the given parameters into specific categories such as dataframe parameters,
        dataframe options, and filters. Updates existing class attributes with the parsed values,
        retaining any sticky filters. Also handles the legacy filters if provided.

        :param params: Dictionary containing parameters to process. These parameters can include specific
            keys relevant for dataframe configuration (e.g., dataframe parameters, dataframe options)
            as well as arbitrary filter settings.
        :type params: dict
        :return: None
        """
        self.legacy_filters = params.pop('legacy_filters', self.legacy_filters)
        self.field_map = params.pop('field_map', self.field_map)
        self.sticky_filters = params.pop('params', self.sticky_filters)
        df_params, df_options, filters = {}, {}, {}
        for k, v in params.items():
            if k in dataframe_params.keys():
                df_params.update({k: v})
            elif k in dataframe_options.keys():
                df_options.update({k: v})
            else:
                filters.update({k: v})
        self.filters = {**self.sticky_filters, **filters}
        self.df_params = {**self.df_params, **df_params}
        self.df_options = {**self.df_options, **df_options}
        if self.legacy_filters:
            self.convert_legacy_filters()

    def convert_legacy_filters(self):
        """
            Converts legacy filter fields in the `self.filters` dictionary to their
            modern equivalents using the mappings provided in `self.field_map`.
            This method ensures backward compatibility for filters by automatically
            translating the old field names into the current system.

            The function first verifies that the required dictionaries (`legacy_filters`,
            `field_map`, `filters`) are valid. It creates a reverse map of `field_map` for
            efficient lookup, processes the key names within `self.filters`, and updates
            them to reflect the legacy mapping.

            :raises KeyError: If any required dictionary key is missing during processing.

            :param self.legacy_filters: A boolean flag indicating whether legacy filters
                are being used.
            :type self.legacy_filters: bool

        """
        if not self.legacy_filters or not self.field_map or not self.filters:
            return
        # create a reverse map of the field_map
        reverse_map = {v: k for k, v in self.field_map.items()}

        new_filters = {}
        for filter_field, value in self.filters.items():
            # split the filter_field if LOOKUP_SEP exists
            parts = filter_field.split(LOOKUP_SEP, 1)

            # replace each part with its legacy equivalent if it exists
            new_parts = [reverse_map.get(part, part) for part in parts]

            # join the parts back together and add to the new filters
            new_filter_field = LOOKUP_SEP.join(new_parts)
            new_filters[new_filter_field] = value

        self.filters = new_filters
