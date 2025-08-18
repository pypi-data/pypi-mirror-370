"""
Category validation helper functions for validating hierarchical category dictionaries.

This module contains all the helper functions used by DataValidator.check_categories_dict()
to validate the structure and relationships of category hierarchies.
"""

import logging

from foundry_sdk.etl.constants import DummyNames

logger = logging.getLogger(__name__)


def validate_basic_structure(categories_dict: dict) -> None:
    """Validate basic dictionary structure."""
    if not isinstance(categories_dict, dict):
        msg = f"categories_dict must be a dictionary, got {type(categories_dict).__name__}"
        raise TypeError(msg)

    if not categories_dict:
        raise ValueError("categories_dict cannot be empty")


def validate_levels_structure(categories_dict: dict) -> tuple[list[int], dict[int, set[str]]]:
    """Validate level structure and return levels and categories by level."""
    try:
        levels = sorted(categories_dict.keys())
    except TypeError as e:
        msg = f"All level keys must be integers, got mixed types: {list(categories_dict.keys())}"
        raise TypeError(msg) from e

    # Ensure all keys are integers
    non_integer_keys = [k for k in categories_dict if not isinstance(k, int)]
    if non_integer_keys:
        msg = f"All level keys must be integers, got non-integers: {non_integer_keys}"
        raise TypeError(msg)

    # Check for negative levels
    negative_levels = [k for k in levels if k < 0]
    if negative_levels:
        msg = f"Level keys must be non-negative, got: {negative_levels}"
        raise ValueError(msg)

    # Check for sequential levels starting from 0
    expected_levels = list(range(len(levels)))
    if levels != expected_levels:
        msg = f"Levels must be sequential starting from 0, got: {levels}, expected: {expected_levels}"
        raise ValueError(msg)

    # Check that each level contains a dictionary and validate level 0
    categories_by_level = {}
    for level, level_dict in categories_dict.items():
        if not isinstance(level_dict, dict):
            msg = f"Level {level} must contain a dictionary, got {type(level_dict).__name__}"
            raise TypeError(msg)

        if not level_dict:
            msg = f"Level {level} cannot be empty"
            raise ValueError(msg)

        # Level 0 validation
        if level == 0:
            for category_name, parent_value in level_dict.items():
                if parent_value is not None:
                    msg = f"Level 0 category '{category_name}' must have None as parent, got: {parent_value}"
                    raise ValueError(msg)

        categories_by_level[level] = set()

    return levels, categories_by_level


def validate_category_names(categories_dict: dict, categories_by_level: dict[int, set[str]]) -> set[str]:
    """Validate category names and populate categories_by_level."""
    all_categories = set()

    for level, level_dict in categories_dict.items():
        for category_name in level_dict:
            # Check category name type
            if not isinstance(category_name, str):
                msg = f"Category names must be strings, got {type(category_name).__name__}: {category_name} at level {level}"
                raise TypeError(msg)

            # Check for empty category names
            if not category_name.strip():
                msg = f"Category names cannot be empty at level {level}"
                raise ValueError(msg)

            # Check for uniqueness
            if category_name in all_categories:
                msg = f"Category name '{category_name}' appears multiple times across levels"
                raise ValueError(msg)

            all_categories.add(category_name)
            categories_by_level[level].add(category_name)

    return all_categories


def validate_parent_child_relationships(categories_dict: dict, categories_by_level: dict[int, set[str]]) -> list[str]:
    """Validate parent-child relationships and return categories with multiple parents."""
    multi_parent_categories = []

    for level, level_dict in categories_dict.items():
        if level == 0:
            continue  # Level 0 already validated

        for category_name, parent_value in level_dict.items():
            # Check parent value type
            if not isinstance(parent_value, list):
                msg = f"Category '{category_name}' at level {level} must have a list of parents, got {type(parent_value).__name__}: {parent_value}"
                raise TypeError(msg)

            if not parent_value:
                msg = f"Category '{category_name}' at level {level} must have at least one parent"
                raise ValueError(msg)

            # Check for multiple parents (warning only)
            if len(parent_value) > 1:
                multi_parent_categories.append(category_name)

            # Validate each parent
            for parent_name in parent_value:
                if not isinstance(parent_name, str):
                    msg = f"Parent names must be strings, got {type(parent_name).__name__}: {parent_name} for category '{category_name}'"
                    raise TypeError(msg)

                # Check parent existence in higher levels
                parent_found = any(parent_name in categories_by_level[parent_level] for parent_level in range(level))

                if not parent_found:
                    msg = f"Parent '{parent_name}' for category '{category_name}' at level {level} not found in any higher level (0 to {level - 1})"
                    raise ValueError(msg)

                # Check for self-reference
                if parent_name == category_name:
                    msg = f"Category '{category_name}' cannot be its own parent"
                    raise ValueError(msg)

    return multi_parent_categories


def check_circular_dependencies(categories_dict: dict) -> None:
    """Check for circular dependencies in the category hierarchy."""

    def has_circular_dependency(category: str, visited: set, path: set) -> bool:
        if category in path:
            return True
        if category in visited:
            return False

        visited.add(category)
        path.add(category)

        # Find parents of this category
        for level, level_dict in categories_dict.items():
            if category in level_dict and level > 0:
                parents = level_dict[category]
                for parent in parents:
                    if has_circular_dependency(parent, visited, path):
                        return True

        path.remove(category)
        return False

    visited = set()
    for level, level_dict in categories_dict.items():
        if level == 0:
            continue
        for category_name in level_dict:
            if has_circular_dependency(category_name, visited, set()):
                msg = f"Circular dependency detected involving category '{category_name}'"
                raise ValueError(msg)


def check_reachability(categories_dict: dict, categories_by_level: dict[int, set[str]]) -> None:
    """Ensure all categories are reachable from level 0."""
    reachable = set(categories_by_level[0])  # Start with level 0 categories

    for level in range(1, len(categories_dict)):
        newly_reachable = set()
        for category_name, parents in categories_dict[level].items():
            if any(parent in reachable for parent in parents):
                newly_reachable.add(category_name)

        if not newly_reachable and categories_by_level[level]:
            unreachable = categories_by_level[level]
            msg = f"Categories at level {level} are not reachable from level 0: {sorted(unreachable)}"
            raise ValueError(msg)

        reachable.update(newly_reachable)


def validate_dummy_category(all_categories: set[str]) -> None:
    """Validate dummy category if present."""
    dummy_category_name = DummyNames.DUMMY_CATEGORY.value
    if dummy_category_name in all_categories:
        logger.info("Dummy category '%s' found in categories", dummy_category_name)


def log_warnings_and_success(multi_parent_categories: list[str], all_categories: set[str], total_levels: int) -> None:
    """Log warnings and success message."""
    max_displayed_categories = 10

    if multi_parent_categories:
        sorted_multi_parent = sorted(multi_parent_categories)
        displayed_categories = sorted_multi_parent[:max_displayed_categories]
        total_count = len(multi_parent_categories)

        if total_count > max_displayed_categories:
            logger.warning(
                "Some categories have multiple parent categories, ensure this is intentional: %s (showing first %d of %d)",
                displayed_categories,
                max_displayed_categories,
                total_count,
            )
        else:
            logger.warning(
                "Some categories have multiple parent categories, ensure this is intentional: %s",
                displayed_categories,
            )

    total_categories = len(all_categories)
    logger.info("Check on categories_dict passed. Found %d categories across %d levels", total_categories, total_levels)
