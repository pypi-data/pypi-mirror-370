"""LookML dimension generator module."""

from typing import Any, Dict, List, Optional, Tuple

from dbt2lookml.enums import (
    LookerDateTimeframes,
    LookerDateTimeTypes,
    LookerDateTypes,
    LookerScalarTypes,
    LookerTimeTimeframes,
)
from dbt2lookml.generators.utils import get_column_name, map_bigquery_to_looker
from dbt2lookml.models.dbt import DbtModel, DbtModelColumn
from . import utils


class LookmlDimensionGenerator:
    """Lookml dimension generator."""

    def __init__(self, args):
        """Initialize the generator with CLI arguments."""
        self._cli_args = args

    def _format_label(self, name: Optional[str] = None, remove_date: bool = True) -> str:
        """Format a name into a human-readable label.

        Args:
            name: The name to format
            remove_date: Whether to remove '_date' from the name

        Returns:
            Formatted label string
        """
        if name is None:
            return ""
        if remove_date:
            name = name.replace("_date", "")
        return name.replace("_", " ").title()

    def _apply_meta_looker_attributes(
        self, target_dict: Dict[str, Any], column: DbtModelColumn, attributes: List[str]
    ) -> None:
        """Apply meta attributes from column to target dictionary if they exist.

        Args:
            target_dict: Dictionary to update with meta attributes
            column: Column containing meta attributes
            attributes: List of attribute names to apply
        """
        if column.meta and column.meta.looker and column.meta.looker.dimension is not None:
            for attr in attributes:
                value = getattr(column.meta.looker.dimension, attr, None)
                if value is not None:
                    if attr == "value_format_name":
                        meta_value = value.value
                    elif isinstance(value, bool):
                        meta_value = "yes" if value else "no"
                    else:
                        meta_value = value
                    target_dict[attr] = meta_value

    def _create_iso_field(
        self, field_type: str, column: DbtModelColumn, sql: str
    ) -> Dict[str, Any]:
        """Create an ISO year or week field.

        Args:
            field_type: Type of ISO field (year or week)
            column: Column to create field from
            sql: SQL expression for the field

        Returns:
            Dictionary containing ISO field definition
        """
        label_type = field_type.replace("_of_year", "")
        field = {
            "name": f"{column.name}_iso_{field_type}",
            "label": f"{self._format_label(column.name)} ISO {label_type.title()}",
            "type": "number",
            "sql": f"Extract(iso{label_type} from {sql})",
            "description": f"iso year for {column.name}",
            "group_label": "D Date",
            "value_format_name": "id",
        }
        self._apply_meta_looker_attributes(field, column, ["group_label", "label"])
        if field_type == "week_of_year":
            field["label"] = field["label"].replace("Week", "Week Of Year")
        return field

    def _get_looker_type(self, column: DbtModelColumn) -> str:
        """Get the category of a column's type.

        Args:
            column: Column to get type for

        Returns:
            Type category (scalar, date, time)
        """
        looker_type = map_bigquery_to_looker(column.data_type)
        if looker_type in LookerDateTimeTypes.values():
            return "time"
        elif looker_type in LookerDateTypes.values():
            return "date"
        return "scalar"

    def _create_dimension(
        self, column: DbtModelColumn, sql: str, is_hidden: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Create a basic dimension dictionary.

        Args:
            column: Column to create dimension from
            sql: SQL expression for the dimension
            is_hidden: Whether the dimension is hidden

        Returns:
            Dictionary containing dimension definition
        """
        data_type = map_bigquery_to_looker(column.data_type)
        if data_type is None:
            return None

        dimension: Dict[str, Any] = {"name": utils.safe_name(column.lookml_name)}

        # Add type for scalar types (should come before sql)
        if data_type in LookerScalarTypes.values():
            dimension["type"] = data_type

        dimension |= {"sql": sql, "description": column.description or ""}

        # Add primary key attributes
        if column.is_primary_key:
            dimension["primary_key"] = "yes"
            dimension["hidden"] = "yes"
            dimension["value_format_name"] = "id"
        elif is_hidden:
            dimension["hidden"] = "yes"

        # Handle array and struct types
        if "ARRAY" in f"{column.data_type}":
            dimension["hidden"] = "yes"
            dimension["tags"] = ["array"]
            dimension.pop("type", None)
        elif "STRUCT" in f"{column.data_type}":
            dimension["hidden"] = "no"
            dimension["tags"] = ["struct"]

        # Apply meta looker attributes
        self._apply_meta_looker_attributes(
            dimension,
            column,
            ["description", "group_label", "value_format_name", "label", "hidden"],
        )

        return dimension

    def lookml_dimension_group(
        self, column: DbtModelColumn, looker_type: str, table_format_sql: bool, model: DbtModel
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        """Create dimension group for date/time fields.

        Args:
            column: Column to create dimension group from
            looker_type: Type of dimension group (date, time)
            table_format_sql: Whether to format SQL for table
            model: Model containing column

        Returns:
            Tuple containing dimension group, dimension group set, and dimensions
        """
        if map_bigquery_to_looker(column.data_type) is None:
            return None, None, None

        if looker_type == "date":
            convert_tz = "no"
            timeframes = LookerDateTimeframes.values()
            column_name_adjusted = column.name.replace("_date", "")
        elif looker_type == "time":
            convert_tz = "yes"
            timeframes = LookerTimeTimeframes.values()
            column_name_adjusted = column.name.replace("_date", "")
        else:
            return None, None, None

        sql = get_column_name(column, table_format_sql)

        dimensions = []
        dimension_group = {
            "name": column_name_adjusted,
            "label": self._format_label(column.lookml_name),
            "type": 'time',
            "sql": sql,
            "description": column.description,
            "datatype": map_bigquery_to_looker(column.data_type),
            "timeframes": timeframes,
            "group_label": (
                "D Date"
                if column_name_adjusted == "d"
                else f"{self._format_label(column.lookml_name)}"
            ),
            "convert_tz": convert_tz,
        }
        self._apply_meta_looker_attributes(dimension_group, column, ["group_label", "label"])

        dimension_group_set = {
            "name": f"s_{column_name_adjusted}",
            "fields": [
                f"{column_name_adjusted}_{looker_time_timeframe}"
                for looker_time_timeframe in timeframes
            ],
        }

        if looker_type == "date":
            iso_year = self._create_iso_field("year", column, sql)
            iso_week_of_year = self._create_iso_field("week_of_year", column, sql)
            dimensions = [iso_year, iso_week_of_year]
            dimension_group_set["fields"].extend(
                [f"{column.name}_iso_year", f"{column.name}_iso_week_of_year"]
            )

        return dimension_group, dimension_group_set, dimensions

    def _create_single_array_dimension(self, column: DbtModelColumn) -> Dict[str, Any]:
        """Create a dimension for a simple array type.

        Args:
            column: Column to create dimension from

        Returns:
            Dictionary containing dimension definition
        """
        data_type = map_bigquery_to_looker(column.inner_types[0])
        return {
            "name": column.lookml_name,
            "type": data_type,
            "sql": column.lookml_name,
            "description": column.description or "",
        }

    def _is_single_type_array(self, column: DbtModelColumn) -> bool:
        """Check if column is a simple array type.

        Args:
            column: Column to check

        Returns:
            Whether column is a simple array type
        """
        return column.data_type == "ARRAY" and (
            len(column.inner_types) == 1 and " " not in column.inner_types[0]
        )

    def _add_dimension_to_dimension_group(
        self, model: DbtModel, dimensions: List[Dict[str, Any]], table_format_sql: bool = True
    ):
        """Add dimensions to dimension groups.

        Args:
            model: Model containing dimensions
            dimensions: List of dimensions to add
            table_format_sql: Whether to format SQL for table
        """
        for column in model.columns.values():
            if column.data_type == "DATE":
                _, _, dimension_group_dimensions = self.lookml_dimension_group(
                    column, "date", table_format_sql, model
                )
                if dimension_group_dimensions:
                    dimensions.extend(dimension_group_dimensions)

    def lookml_dimensions_from_model(
        self,
        model: DbtModel,
        include_names: Optional[List[str]] = None,
        exclude_names: Optional[List[str]] = None,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Generate dimensions from model.

        Args:
            model: Model to generate dimensions from
            include_names: List of names to include
            exclude_names: List of names to exclude

        Returns:
            Tuple containing dimensions and nested dimensions
        """
        if exclude_names is None:
            exclude_names = []
        dimensions: List[Dict[str, Any]] = []
        table_format_sql = True
        nested_dimensions: List[Dict[str, Any]] = []

        # First add ISO date dimensions for main view only
        if not include_names:  # Only for main view
            self._add_dimension_to_dimension_group(model, dimensions, table_format_sql)

        # Then add regular dimensions
        for column in model.columns.values():
            if include_names:
                table_format_sql = False

                # For nested views, only include fields that are children of the parent
                # or the parent itself if it's a simple array
                parent = include_names[0] if include_names else None
                if column.name == parent:
                    # Keep parent field only if it's a simple array (e.g. ARRAY<INT64>)
                    if self._is_single_type_array(column):
                        dimensions.append(self._create_single_array_dimension(column))
                    # Skip column equal to parent
                    continue
                elif not column.name.startswith(f"{parent}."):
                    continue

            if column.name in exclude_names or column.data_type == "DATETIME":
                continue

            # Skip date dimensions since we handled them above
            if column.data_type == "DATE" and not include_names:
                continue

            if column.data_type is None:
                continue

            column_name = get_column_name(column, table_format_sql)
            dimension = self._create_dimension(column, column_name)

            if dimension is not None:
                dimensions.append(dimension)

        return dimensions, nested_dimensions

    def lookml_dimension_groups_from_model(
        self,
        model: DbtModel,
        include_names: Optional[List[str]] = None,
        exclude_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate dimension groups from model.

        Args:
            model: Model to generate dimension groups from
            include_names: List of names to include
            exclude_names: List of names to exclude

        Returns:
            Dictionary containing dimension groups and dimension group sets
        """
        if exclude_names is None:
            exclude_names = []
        dimension_groups = []
        dimension_group_sets = []
        table_format_sql = not include_names

        for column in model.columns.values():
            if include_names and column.name not in include_names:
                continue

            if exclude_names and column.name in exclude_names:
                continue

            looker_type = self._get_looker_type(column)
            if looker_type in ("time", "date"):
                dimension_group, dimension_group_set, dimensions = self.lookml_dimension_group(
                    column=column,
                    looker_type=looker_type,
                    table_format_sql=table_format_sql,
                    model=model,
                )
                if dimension_group:
                    dimension_groups.append(dimension_group)
                if dimension_group_set:
                    dimension_group_sets.append(dimension_group_set)

        return {
            "dimension_groups": dimension_groups or None,
            "dimension_group_sets": dimension_group_sets or None,
        }
