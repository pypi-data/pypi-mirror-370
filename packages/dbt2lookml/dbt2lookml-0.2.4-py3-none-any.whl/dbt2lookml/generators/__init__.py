"""LookML Generator implementations."""

import os
from typing import Dict, Tuple

from dbt2lookml.generators.dimension import LookmlDimensionGenerator
from dbt2lookml.generators.explore import LookmlExploreGenerator
from dbt2lookml.generators.measure import LookmlMeasureGenerator
from dbt2lookml.generators.view import LookmlViewGenerator
from dbt2lookml.models.dbt import DbtModel, DbtModelColumn


class LookmlGenerator:
    """Main LookML generator that coordinates dimension, view, and explore generation."""

    def __init__(self, cli_args):
        self._cli_args = cli_args
        self.dimension_generator = LookmlDimensionGenerator(cli_args)
        self.view_generator = LookmlViewGenerator(cli_args)
        self.explore_generator = LookmlExploreGenerator(cli_args)
        self.measure_generator = LookmlMeasureGenerator(cli_args)

    def _get_view_label(self, model: DbtModel) -> str:
        """Get the view label from the model metadata or name."""
        # Check looker meta label first
        if hasattr(model.meta.looker, 'label') and model.meta.looker.label is not None:
            return model.meta.looker.label

        # Fall back to model name if available
        return model.name.replace("_", " ").title() if hasattr(model, 'name') else None

    def _extract_array_models(self, columns: list[DbtModelColumn]) -> list[DbtModelColumn]:
        """Extract array models from a list of columns."""
        return [
            column
            for column in columns
            if column.data_type is not None and column.data_type == 'ARRAY'
        ]

    def _get_excluded_array_names(self, model: DbtModel, array_models: list) -> list:
        """Get list of dimension names to exclude from main view."""
        exclude_names = []
        for array_model in array_models:
            # Don't exclude the array field itself from main view
            exclude_names.extend(
                col.name
                for col in model.columns.values()
                if col.name.startswith(f"{array_model.name}.")
            )
        return exclude_names

    def _get_file_path(self, model: DbtModel, view_name: str) -> str:
        """Get the file path for the LookML view.

        Args:
            model: The dbt model to generate a view for
            view_name: The name to use for the view

        Returns:
            str: The full file path for the LookML view file

        Example:
            >>> model = DbtModel(name="my_model", path="/path/to/models/my_model.sql")
            >>> generator._get_file_path(model, "my_view")
            "/path/to/models/my_view.view.lkml"
        """
        if self._cli_args.use_table_name:
            # When using table names, use the directory structure from the model path
            # but don't include the model name in the path
            directory = os.path.dirname(model.path)
            file_name = model.relation_name.split('.')[-1].strip('`')
            return os.path.join(directory, f'{file_name}.view.lkml')
        else:
            # Original behavior for model names
            file_path = os.path.join(model.path.split(model.name)[0])
            return f'{file_path}/{view_name}.view.lkml'

    def generate(self, model: DbtModel) -> Tuple[str, Dict]:
        """Generate LookML for a model.

        Args:
            model: The dbt model to generate LookML for

        Returns:
            tuple[str, dict]: A tuple containing:
                - str: The file path where the LookML should be written
                - dict: The generated LookML content

        Raises:
            ValueError: If the model is missing required attributes
        """
        # Get view name
        view_name = (
            model.relation_name.split('.')[-1].strip('`')
            if self._cli_args.use_table_name
            else model.name
        )

        # Get view label
        view_label = self._get_view_label(model)

        # Get array models and structure
        array_models = self._extract_array_models(list(model.columns.values()))
        exclude_names = self._get_excluded_array_names(model, array_models)

        # Create main view
        views = self.view_generator.generate(
            model=model,
            view_name=view_name,
            view_label=view_label,
            exclude_names=exclude_names,
            array_models=array_models,
            dimension_generator=self.dimension_generator,
            measure_generator=self.measure_generator,
        )

        # Create LookML base
        lookml = {
            'view': [views],
        }

        # Create explore if needed
        if (
            self._cli_args.build_explore
        ):  # When build_explore is True, we should generate the explore
            # Create explore
            explore = self.explore_generator.generate(
                model=model,
                view_name=view_name,
                view_label=view_label,
                array_models=array_models,
            )

            lookml['explore'] = explore

        return self._get_file_path(model, view_name), lookml


__all__ = ['LookmlGenerator']
