import dataclasses
import json
from collections import defaultdict
from typing import Any, Dict, List, Literal, Optional, overload

from . import datasets

_dataset_fields = {f.name for f in dataclasses.fields(datasets.Dataset) if not f.name.startswith('_')}

MatchMode = Literal['equals','notEquals', 'startsWith', 'endsWith', 'contains', 'similarTo', 'notContains', 'isNull', 'isNotNull', 'greaterThan', 'lessThan', 'includes', 'notIncludes']
OperatorMode = Literal['OR', 'AND']
SortOrder = Literal['ASC', 'DESC']

@dataclasses.dataclass
class FilterMetadata:
    """Represents a single filter condition"""

    def __init__(self, *,
                 value: Any,
                 match_mode: MatchMode = 'equals',
                 operator: OperatorMode = 'AND'):
        self.value = value
        self.match_mode = match_mode
        self.operator = operator

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {'value': self.value, 'matchMode': self.match_mode, 'operator': self.operator}


class SearchConfig:
    """Builder class for creating TableFilterMetadata objects"""

    records: int = 25
    offset: int = 0
    sort_order: SortOrder = 'ASC'
    sort_field: Optional[str] = None

    def __init__(self,
                 records: int = 25,
                 offset: int = 0,
                 sort_order: SortOrder = 'ASC',
                 sort_field: Optional[str] = None):

        # Validate that the field is a valid Dataset property
        if sort_field not in _dataset_fields and sort_field is not None:
            raise ValueError(f'Invalid sort field "{sort_field}". Must be one of: {sorted(_dataset_fields)}')

        if sort_order not in ['ASC', 'DESC']:
            raise ValueError(f'Invalid sort order "{sort_order}". Must be "ASC" or "DESC".')

        self.filters: Dict[str, List[FilterMetadata]] = defaultdict(list)
        self.records = records
        self.offset = offset
        self.sort_order = sort_order
        self.sort_field = sort_field

    def __str__(self) -> str:
        """Return a string summary of the search configuration"""
        parts = []
        
        # Add filter summary
        if self.filters:
            filter_parts = []
            for field, filter_list in self.filters.items():
                field_conditions = []
                for filter_meta in filter_list:
                    if filter_meta.match_mode in ('isNull', 'isNotNull'):
                        condition = f"{field} {filter_meta.match_mode}"
                    else:
                        condition = f"{field} {filter_meta.match_mode} '{filter_meta.value}'"
                    field_conditions.append(condition)
                
                # Join conditions for this field with the operator
                if len(field_conditions) > 1:
                    operator = filter_list[0].operator  # All filters for a field have same operator
                    field_summary = f"({f' {operator} '.join(field_conditions)})"
                else:
                    field_summary = field_conditions[0]
                filter_parts.append(field_summary)
            
            parts.append(f"Filters: {' AND '.join(filter_parts)}")
        else:
            parts.append("Filters: None")
        
        # Add pagination info
        parts.append(f"Records: {self.records}, Offset: {self.offset}")
        
        # Add sorting info
        if self.sort_field:
            parts.append(f"Sort: {self.sort_field} {self.sort_order}")
        else:
            parts.append("Sort: None")
        
        return f"SearchConfig({', '.join(parts)})"

    @overload
    def add_filter(self, field: str, *, match_mode: Literal['isNull', 'isNotNull'], operator: OperatorMode = 'AND') -> 'SearchConfig':
        ...

    @overload
    def add_filter(self, field: str, *, value: Any, match_mode: MatchMode = 'equals', operator: OperatorMode = 'AND') -> 'SearchConfig':
        ...

    def add_filter(self, field: str, *, value: Any = None, match_mode: MatchMode = 'equals', operator: OperatorMode = 'AND') -> 'SearchConfig':
        """
        Add a single filter for a field

        Args:
            field: The field name to filter on
            value: The value to filter by (optional for 'isNull' and 'isNotNull' match modes)
            match_mode: The match mode (e.g., 'contains', 'equals', 'startsWith')
            operator: The operator (e.g., 'and', 'or')

        Returns:
            Self for method chaining
        """
        # For isNull and isNotNull, value needs to be set but doesn't matter
        if match_mode in ('isNull', 'isNotNull') and value is not None:
            value = True

        # Validate that the field is a valid Dataset property
        if field not in _dataset_fields:
            raise ValueError(f'Invalid field "{field}". Must be one of: {sorted(_dataset_fields)}')

        filter_meta = FilterMetadata(value=value, match_mode=match_mode, operator=operator)
        existing_field_filters = self.filters[field]
        for existing_filter in existing_field_filters:
            # Can't have two different operators on the same field
            if existing_filter.operator != operator:
                raise ValueError(f'Cannot have homogeneous operators for the same field. Field: "{field}. Previous operator: "{existing_filter.operator}". Current field operator: "{operator}"')

            # Check for conflicting filter values
            if operator == 'AND':
                if existing_filter.match_mode == 'equals' and match_mode == 'equals' and existing_filter.value != value:
                    raise ValueError(f'Adding two "equals" filters with different values will never return any results. Field: "{field}". Values: "{existing_filter.value}", "{value}"')

                # Check for conflicting null/not null filters
                if (existing_filter.match_mode == 'isNull' and match_mode == 'isNotNull') or \
                        (existing_filter.match_mode == 'isNotNull' and match_mode == 'isNull'):
                    raise ValueError(f'Conflicting "isNull" and "isNotNull" filters for the same field will never return results. Field: "{field}"')

                # Check for conflicting equals and notEquals with same value
                if (existing_filter.match_mode == 'equals' and match_mode == 'notEquals' and existing_filter.value == value) or \
                        (existing_filter.match_mode == 'notEquals' and match_mode == 'equals' and existing_filter.value == value):
                    raise ValueError(f'Conflicting "equals" and "notEquals" filters for the same field with the same value will never return results. Field: "{field}". Value: "{value}"')

                # Check for conflicting greaterThan and lessThan filters
                if existing_filter.match_mode == 'greaterThan' and match_mode == 'lessThan' and \
                        isinstance(existing_filter.value, (float, int)) and isinstance(existing_filter.value, (float, int)) and \
                        value <= existing_filter.value:
                    raise ValueError(f'Conflicting "greaterThan" and "lessThan" filters will never return results. Field: "{field}". GreaterThan: "{existing_filter.value}", LessThan: "{value}"')
                if existing_filter.match_mode == 'lessThan' and match_mode == 'greaterThan' and \
                        isinstance(existing_filter.value, (float, int)) and isinstance(existing_filter.value, (float, int)):
                    if value >= existing_filter.value:
                        raise ValueError(f'Conflicting "greaterThan" and "lessThan" filters will never return results. Field: "{field}". GreaterThan: "{value}", LessThan: "{existing_filter.value}"')

                # Check for conflicting contains and notContains with same value
                if existing_filter.match_mode == 'contains' and match_mode == 'notContains' and existing_filter.value == value:
                    raise ValueError(f'Conflicting "contains" and "notContains" filters with the same value will never return results. Field: "{field}". Value: "{value}"')
                if existing_filter.match_mode == 'notContains' and match_mode == 'contains' and existing_filter.value == value:
                    raise ValueError(f'Conflicting "contains" and "notContains" filters with the same value will never return results. Field: "{field}". Value: "{value}"')

                # Check for conflicting includes and notIncludes with same value
                if existing_filter.match_mode == 'includes' and match_mode == 'notIncludes' and existing_filter.value == value:
                    raise ValueError(f'Conflicting "includes" and "notIncludes" filters with the same value will never return results. Field: "{field}". Value: "{value}"')
                if existing_filter.match_mode == 'notIncludes' and match_mode == 'includes' and existing_filter.value == value:
                    raise ValueError(f'Conflicting "includes" and "notIncludes" filters with the same value will never return results. Field: "{field}". Value: "{value}"')
        existing_field_filters.append(filter_meta)
        return self

    def build(self) -> Dict[str, Any]:
        """
        Build the final TableFilterMetadata object

        Returns:
            Dictionary representing TableFilterMetadata
        """

        filters_dict = {key: [_.to_dict() for _ in value] for key, value in self.filters.items()}

        return {'filters': json.dumps(filters_dict),
                'offset': self.offset,
                'sort_order': self.sort_order,
                'sort_field': self.sort_field,
                'records': self.records}

    def clone(self) -> 'SearchConfig':
        """
        Clones this object so that it can be used to keep track of results as they are fetched (or for other purposes).

        Returns:
             A search config object with the same exact attributes.
        """

        new_config = SearchConfig(records=self.records, offset=self.offset, sort_order=self.sort_order, sort_field=self.sort_field)
        new_config.filters = self.filters.copy()
        return new_config
