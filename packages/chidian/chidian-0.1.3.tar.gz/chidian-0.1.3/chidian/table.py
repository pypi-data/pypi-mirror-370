import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterator, Optional, Union

from .core import get

"""
A `Table` is a lightweight, sparse table implementation that treats a collection of dictionaries as rows in a table.

Each dictionary represents a row with potentially different keys (columns), making it ideal for heterogeneous,
nested data. Provides a middle ground between the strictness of DataFrames and raw list[dict]/dict[str, dict].

Supports path-based queries, filtering, mapping, and other functional operations.
"""


class Table:
    def __init__(
        self,
        rows: Union[list[dict[str, Any]], dict[str, dict[str, Any]], None] = None,
    ):
        """
        Initialize a Table from rows.

        Args:
            rows: Either:
                - list[dict]: Each dict is a row, auto-keyed by index ($0, $1, ...)
                - dict[str, dict]: Pre-keyed rows (keys preserved)
                - None: Empty table
        """
        self._rows: list[dict[str, Any]] = []
        self._row_keys: dict[str, int] = {}  # Maps row keys to indices
        self._key_to_row: dict[str, dict[str, Any]] = {}  # Maps $ keys to row dicts

        # Initialize rows based on input type
        if rows is not None:
            if isinstance(rows, list):
                self._rows = rows
                # Store rows by index using $-syntax
                for i, row in enumerate(rows):
                    key = f"${i}"
                    self._key_to_row[key] = row
                    self._row_keys[key] = i
            elif isinstance(rows, dict):
                self._rows = list(rows.values())
                # Store rows by their original keys
                for i, (key, row) in enumerate(rows.items()):
                    # Ensure keys start with $ for consistency
                    if not key.startswith("$"):
                        key = f"${key}"
                    self._key_to_row[key] = row
                    self._row_keys[key] = i

    def get(self, path: str, default: Any = None) -> Union[Any, list[Any]]:
        """
        Extract values from rows using a path expression.

        If path starts with $, extracts from a specific row only.
        Otherwise, extracts from all rows.

        Uses the existing chidian.core.get() engine to navigate nested structures.

        Args:
            path: Path expression:
                  - "$0.name" or "$bob.name": Extract from specific row
                  - "name" or "patient.id": Extract from all rows
            default: Value to use when path doesn't exist

        Returns:
            - Single value when using $-prefixed path for specific row
            - List of values (one per row) when extracting from all rows

        Examples:
            >>> t = Table([
            ...     {"name": "John", "age": 30},
            ...     {"name": "Jane", "age": 25},
            ...     {"name": "Bob"}  # Note: no age
            ... ])
            >>> t.get("name")
            ["John", "Jane", "Bob"]
            >>> t.get("$0.name")
            "John"
            >>> t.get("$1.age")
            25
            >>> t.get("$2.age", default=0)
            0
            >>> t.append({"name": "Alice"}, custom_key="alice")
            >>> t.get("$alice.name")
            "Alice"
        """
        # Check if path starts with $ (specific row access)
        if path.startswith("$"):
            # Extract row key and remaining path
            parts = path.split(".", 1)
            row_key = parts[0]

            # Check if this key exists
            if row_key not in self._key_to_row:
                return default

            # Get the specific row
            row = self._key_to_row[row_key]

            # If there's a remaining path, extract from the row
            if len(parts) > 1:
                return get(row, parts[1], default=default)
            else:
                # Just the row key itself, return the whole row
                return row

        # Original behavior: extract from all rows
        results = []
        for row in self._rows:
            value = get(row, path, default=default)
            results.append(value)
        return results

    @property
    def columns(self) -> set[str]:
        """
        Return the union of all keys across all rows.

        This represents the "sparse columns" of the table.

        Examples:
            >>> t = Table([
            ...     {"name": "John", "age": 30},
            ...     {"name": "Jane", "city": "NYC"}
            ... ])
            >>> t.columns
            {"name", "age", "city"}
        """
        all_keys: set[str] = set()
        for row in self._rows:
            all_keys.update(row.keys())
        return all_keys

    def to_list(self) -> list[dict[str, Any]]:
        """Return rows as a plain list of dicts."""
        return self._rows.copy()

    def to_dict(self) -> dict[str, dict[str, Any]]:
        """Return rows as a dict keyed by row identifiers."""
        return self._key_to_row.copy()

    def append(self, row: dict[str, Any], custom_key: Optional[str] = None) -> None:
        """
        Add a new row to the table.

        This operation may expand the logical column set if the new row
        contains keys not seen in existing rows.

        Args:
            row: Dictionary representing the new row
            custom_key: Optional row identifier (defaults to $n where n is the index)
                        If provided and doesn't start with $, will be prefixed with $

        Examples:
            >>> t = Table([{"name": "John"}])
            >>> t.append({"name": "Jane", "age": 25})  # Adds 'age' column
            >>> t.append({"name": "Bob", "city": "NYC"}, custom_key="bob")  # Adds 'city' column
            >>> len(t)
            3
        """
        self._rows.append(row)

        if custom_key is None:
            # Use $-prefixed index as key
            key = f"${len(self._rows) - 1}"
        else:
            # Ensure custom keys start with $
            if not custom_key.startswith("$"):
                key = f"${custom_key}"
            else:
                key = custom_key

        self._key_to_row[key] = row
        self._row_keys[key] = len(self._rows) - 1

    def filter(self, predicate: Union[str, Callable[[dict], bool]]) -> "Table":
        """
        Filter rows based on a predicate.

        Args:
            predicate: Either:
                - Callable: Function that takes a row dict and returns bool
                - str: DSL filter expression

        Returns:
            New Table with only rows matching the predicate

        Examples:
            >>> t = Table([{"name": "John", "age": 30}, {"name": "Jane", "age": 25}])
            >>> t.filter(lambda row: row.get("age", 0) > 26)  # Returns Table with just John
            >>> t.filter("age > 26")
            >>> t.filter("status = 'active' AND age >= 18")
            >>> t.filter("addresses[0].city = 'NYC'")
        """
        if isinstance(predicate, str):
            from .lib.filter_parser import parse_filter

            predicate = parse_filter(predicate)

        # Functional predicate implementation
        filtered_rows = [row for row in self._rows if predicate(row)]
        return Table(filtered_rows)

    def map(self, transform: Callable[[dict], dict]) -> "Table":
        """
        Transform each row using the provided function.

        Args:
            transform: Function that takes a row dict and returns a new dict

        Returns:
            New Table with transformed rows

        Examples:
            >>> t = Table([{"name": "john"}, {"name": "jane"}])
            >>> t2 = t.map(lambda row: {**row, "name": row["name"].upper()})
            >>> t2.get("name")
            ["JOHN", "JANE"]

            >>> # Add computed field
            >>> t3 = t.map(lambda row: {**row, "name_length": len(row.get("name", ""))})
        """
        transformed_rows = [transform(row) for row in self._rows]
        return Table(transformed_rows)

    def select(self, query: str) -> "Table":
        """
        Project columns and create a new Table using DSL syntax.

        Args:
            query: DSL column selection expression

        Returns:
            New Table with selected columns

        Examples:
            >>> t.select("name, age")  # Select specific columns
            >>> t.select("*")  # Select all columns
            >>> t.select("patient.id -> patient_id, status")  # Rename column
            >>> t.select("name, addresses[0].city -> primary_city")  # Nested + rename
        """
        from .lib.select_parser import parse_select

        parsed = parse_select(query)

        # Handle wildcard selection
        if parsed == "*":
            return Table(self._rows.copy())

        # Handle column specifications
        if not isinstance(parsed, list):
            # This shouldn't happen based on parse_select implementation
            raise ValueError("Unexpected parser result")

        new_rows = []
        for row in self._rows:
            new_row = {}

            for spec in parsed:
                # Get value using path
                value = get(row, spec.path, default=None)

                # Use rename if specified, otherwise use the last segment of path
                if spec.rename_to:
                    key = spec.rename_to
                else:
                    # Extract last part of path as column name
                    # e.g., "patient.id" -> "id", "name" -> "name"
                    path_parts = spec.path.split(".")
                    # Remove array indices from last part
                    last_part = path_parts[-1].split("[")[0]
                    key = last_part

                new_row[key] = value

            new_rows.append(new_row)

        return Table(new_rows)

    def unique(self, path: str) -> list[Any]:
        """
        Get unique values from a column path.

        Args:
            path: Path expression to extract values from

        Returns:
            List of unique values found at the path
        """
        values = self.get(path)
        seen = set()
        unique_values = []
        for value in values:
            # Handle unhashable types by converting to string for dedup
            try:
                if value not in seen:
                    seen.add(value)
                    unique_values.append(value)
            except TypeError:
                # Unhashable type, use string representation for dedup
                str_value = str(value)
                if str_value not in seen:
                    seen.add(str_value)
                    unique_values.append(value)
        return unique_values

    def group_by(self, path: str) -> dict[Any, "Table"]:
        """
        Group rows by values at a given path.

        Args:
            path: Path expression to group by

        Returns:
            Dictionary mapping unique values to Tables containing matching rows
        """
        groups: dict[Any, list[dict[str, Any]]] = {}

        for row in self._rows:
            group_value = get(row, path, default=None)
            # Handle unhashable types by converting to string
            try:
                hash(group_value)
                key = group_value
            except TypeError:
                key = str(group_value)

            if key not in groups:
                groups[key] = []
            groups[key].append(row)

        return {key: Table(rows) for key, rows in groups.items()}

    def extract(self, path: str) -> "Table":
        """
        Extract values from all rows using a path and return as a new Table.

        This method is particularly useful for extracting nested structures
        like FHIR Bundle entries or other collections within your data.

        Args:
            path: Path expression to extract from each row
                  - Supports wildcards: "entries[*].resource"
                  - Supports nested paths: "patient.address[0].city"

        Returns:
            New Table where each extracted value becomes a row.
            If path uses wildcards and returns lists, the lists are flattened.
            None values are filtered out.

        Examples:
            >>> # FHIR Bundle example
            >>> bundle_table = Table([fhir_bundle])
            >>> resources = bundle_table.extract("entries[*].resource")

            >>> # Extract nested values from multiple rows
            >>> patients_table = Table([patient1, patient2, patient3])
            >>> addresses = patients_table.extract("address[*]")

            >>> # Simple field extraction
            >>> names = patients_table.extract("name.given[0]")
        """
        # Get extracted values using existing logic
        extracted = self.get(path)

        # Handle the case where get() returns a single value (shouldn't happen for non-$ paths, but be safe)
        if not isinstance(extracted, list):
            extracted = [extracted]

        # Flatten any nested lists and filter out None values
        flattened = []
        for item in extracted:
            if item is None:
                continue
            elif isinstance(item, list):
                # Flatten lists from wildcard extractions
                flattened.extend(item)
            else:
                flattened.append(item)

        # Return new Table with extracted values as rows
        return Table(flattened)

    @classmethod
    def from_path(cls, data: Any, path: str) -> "Table":
        """
        Create a Table by extracting a path from source data.

        This is a convenience constructor that's perfect for extracting
        collections from complex nested structures like FHIR Bundles.

        Args:
            data: Source data structure (dict, list, or any nested structure)
            path: Path expression to extract
                  - "entries[*].resource" for FHIR Bundle resources
                  - "results[*].observation" for lab results
                  - "items[*]" for simple list extraction

        Returns:
            New Table with extracted data as rows

        Examples:
            >>> # Extract FHIR Bundle resources directly
            >>> resources_table = Table.from_path(fhir_bundle, "entries[*].resource")

            >>> # Extract nested arrays
            >>> observations = Table.from_path(lab_report, "results[*].observation")

            >>> # Extract from lists
            >>> items = Table.from_path({"data": [item1, item2]}, "data[*]")
        """
        # Create temporary single-row table with the source data
        temp_table = cls([data])

        # Extract the path and return the result
        return temp_table.extract(f"$0.{path}")

    def join(
        self,
        other: "Table",
        on: str | tuple[str, str] | list[str | tuple[str, str]] | None = None,
        how: str = "left",
        suffixes: tuple[str, str] = ("", "_2"),
    ) -> "Table":
        """
        Join two tables based on matching column values.

        Supports SQL-like join operations with flexible key specification
        and path-based column access.

        Args:
            other: The right table to join with
            on: Join key specification:
                - str: Same column name in both tables ("id")
                - tuple: Different names (("id", "patient_id"))
                - list[str]: Multiple columns, same names (["id", "type"])
                - list[tuple]: Multiple columns, different names
                  ([("patient_id", "subject_id"), ("date", "visit_date")])
                - None: Natural join on all common columns
            how: Join type - "left" (default), "inner", "right", or "outer"
            suffixes: Tuple of suffixes for conflicting column names.
                     Default ("", "_2") adds "_2" to right table conflicts.

        Returns:
            New Table with joined data

        Examples:
            >>> # Simple join on same column
            >>> patients.join(visits, on="patient_id")

            >>> # Join with different column names
            >>> patients.join(visits, on=("id", "patient_id"))

            >>> # Multiple join keys
            >>> orders.join(items, on=[("order_id", "oid"), "date"])

            >>> # Inner join with path expression
            >>> patients.join(observations,
            ...              on=("id", "subject.reference"),
            ...              how="inner")
        """
        # Parse the 'on' parameter to get join column specifications
        left_keys, right_keys = self._parse_join_keys(on, other)

        # Build lookup dictionary from right table for efficient joining
        right_lookup = self._build_join_lookup(other, right_keys)

        # Perform the join based on the specified type
        if how == "left":
            return self._left_join(left_keys, right_lookup, suffixes)
        elif how == "inner":
            return self._inner_join(left_keys, right_lookup, suffixes)
        elif how == "right":
            return self._right_join(
                other, left_keys, right_keys, right_lookup, suffixes
            )
        elif how == "outer":
            return self._outer_join(left_keys, right_lookup, suffixes)
        else:
            raise ValueError(
                f"Invalid join type: {how}. Must be 'left', 'inner', 'right', or 'outer'"
            )

    def _parse_join_keys(
        self,
        on: str | tuple[str, str] | list[str | tuple[str, str]] | None,
        other: "Table",
    ) -> tuple[list[str], list[str]]:
        """Parse the 'on' parameter to extract left and right join keys."""
        if on is None:
            # Natural join - find common columns
            common = self.columns & other.columns
            if not common:
                raise ValueError("No common columns found for natural join")
            left_keys = list(common)
            right_keys = list(common)
        elif isinstance(on, str):
            # Single column, same name
            left_keys = [on]
            right_keys = [on]
        elif isinstance(on, tuple) and len(on) == 2:
            # Single column, different names
            left_keys = [on[0]]
            right_keys = [on[1]]
        elif isinstance(on, list):
            left_keys = []
            right_keys = []
            for item in on:
                if isinstance(item, str):
                    # Same column name
                    left_keys.append(item)
                    right_keys.append(item)
                elif isinstance(item, tuple) and len(item) == 2:
                    # Different column names
                    left_keys.append(item[0])
                    right_keys.append(item[1])
                else:
                    raise ValueError(f"Invalid join key specification: {item}")
        else:
            raise ValueError(f"Invalid 'on' parameter: {on}")

        return left_keys, right_keys

    def _build_join_lookup(
        self, table: "Table", keys: list[str]
    ) -> dict[tuple, list[dict[str, Any]]]:
        """Build a lookup dictionary for efficient joining."""
        lookup: dict[tuple, list[dict[str, Any]]] = {}

        for row in table._rows:
            # Extract key values using get() to support paths
            key_values = []
            for key in keys:
                value = get(row, key, default=None)
                # Convert unhashable types to strings for lookup
                try:
                    hash(value)
                    key_values.append(value)
                except TypeError:
                    key_values.append(str(value))

            key_tuple = tuple(key_values)
            if key_tuple not in lookup:
                lookup[key_tuple] = []
            lookup[key_tuple].append(row)

        return lookup

    def _merge_rows(
        self,
        left_row: dict[str, Any],
        right_row: dict[str, Any] | None,
        suffixes: tuple[str, str],
        join_keys: set[str] | None = None,
    ) -> dict[str, Any]:
        """Merge two rows, handling column conflicts with suffixes."""
        if right_row is None:
            return left_row.copy()

        merged = left_row.copy()
        left_suffix, right_suffix = suffixes
        join_keys = join_keys or set()

        for key, value in right_row.items():
            if key in merged:
                # Check if this is a join key - if so, don't apply suffixes
                if key in join_keys:
                    # Join key - keep as-is (left value takes precedence)
                    continue

                # Column conflict - apply suffixes
                if left_suffix:
                    # Rename left column
                    merged[key + left_suffix] = merged[key]
                    del merged[key]

                if right_suffix:
                    merged[key + right_suffix] = value
                elif not left_suffix:
                    # No suffixes - right overwrites left
                    merged[key] = value
            else:
                # No conflict
                merged[key] = value

        return merged

    def _left_join(
        self,
        left_keys: list[str],
        right_lookup: dict[tuple, list[dict[str, Any]]],
        suffixes: tuple[str, str],
    ) -> "Table":
        """Perform a left outer join."""
        result_rows = []

        for left_row in self._rows:
            # Extract key values from left row
            key_values = []
            for key in left_keys:
                value = get(left_row, key, default=None)
                try:
                    hash(value)
                    key_values.append(value)
                except TypeError:
                    key_values.append(str(value))

            key_tuple = tuple(key_values)
            matching_rows = right_lookup.get(key_tuple, [None])

            # Create a result row for each match (or one with None if no matches)
            for right_row in matching_rows:
                result_rows.append(
                    self._merge_rows(left_row, right_row, suffixes, set(left_keys))
                )

        return Table(result_rows)

    def _inner_join(
        self,
        left_keys: list[str],
        right_lookup: dict[tuple, list[dict[str, Any]]],
        suffixes: tuple[str, str],
    ) -> "Table":
        """Perform an inner join."""
        result_rows = []

        for left_row in self._rows:
            # Extract key values from left row
            key_values = []
            for key in left_keys:
                value = get(left_row, key, default=None)
                try:
                    hash(value)
                    key_values.append(value)
                except TypeError:
                    key_values.append(str(value))

            key_tuple = tuple(key_values)
            matching_rows = right_lookup.get(key_tuple, [])

            # Only add rows when there are matches
            for right_row in matching_rows:
                result_rows.append(
                    self._merge_rows(left_row, right_row, suffixes, set(left_keys))
                )

        return Table(result_rows)

    def _right_join(
        self,
        other: "Table",
        left_keys: list[str],
        right_keys: list[str],
        right_lookup: dict[tuple, list[dict[str, Any]]],
        suffixes: tuple[str, str],
    ) -> "Table":
        """Perform a right outer join."""
        # Build lookup for left table
        left_lookup = self._build_join_lookup(self, left_keys)

        result_rows = []
        for right_row in other._rows:
            # Extract key values from right row
            key_values = []
            for key in right_keys:
                value = get(right_row, key, default=None)
                try:
                    hash(value)
                    key_values.append(value)
                except TypeError:
                    key_values.append(str(value))

            key_tuple = tuple(key_values)
            matching_rows = left_lookup.get(key_tuple, [None])

            # Create a result row for each match (or one with None if no matches)
            for left_row in matching_rows:
                if left_row is None:
                    # No match - just use right row
                    result_rows.append(right_row.copy())
                else:
                    result_rows.append(
                        self._merge_rows(left_row, right_row, suffixes, set(left_keys))
                    )

        return Table(result_rows)

    def _outer_join(
        self,
        left_keys: list[str],
        right_lookup: dict[tuple, list[dict[str, Any]]],
        suffixes: tuple[str, str],
    ) -> "Table":
        """Perform a full outer join."""
        result_rows = []
        seen_right_keys = set()

        # Process all left rows
        for left_row in self._rows:
            # Extract key values from left row
            key_values = []
            for key in left_keys:
                value = get(left_row, key, default=None)
                try:
                    hash(value)
                    key_values.append(value)
                except TypeError:
                    key_values.append(str(value))

            key_tuple = tuple(key_values)
            matching_rows = right_lookup.get(key_tuple, [None])

            if matching_rows != [None]:
                seen_right_keys.add(key_tuple)

            for right_row in matching_rows:
                result_rows.append(
                    self._merge_rows(left_row, right_row, suffixes, set(left_keys))
                )

        # Add unmatched right rows
        for key_tuple, right_rows in right_lookup.items():
            if key_tuple not in seen_right_keys:
                for right_row in right_rows:
                    result_rows.append(right_row.copy())

        return Table(result_rows)

    def __getitem__(self, key: str) -> Any:
        """
        Enhanced access with dot syntax support.

        Supports both row access and path-based access:
        - table["$0"] → returns the row dict
        - table["$0.name"] → extracts value using path syntax
        - table["column"] → extracts column values from all rows (same as get())

        Args:
            key: Either a row key ("$0") or a path expression ("$0.name", "column")

        Returns:
            For row keys: the row dict
            For path expressions: the extracted value(s)

        Examples:
            >>> table["$0"]  # Get entire row
            {"name": "John", "age": 30}
            >>> table["$0.name"]  # Get specific field from row
            "John"
            >>> table["name"]  # Get column from all rows
            ["John", "Jane", "Bob"]
        """
        # Check if this is a path expression (contains dot) or column access
        if "." in key or not key.startswith("$"):
            # Use the get() method which handles path syntax
            return self.get(key)

        # Row key access
        if key in self._key_to_row:
            return self._key_to_row[key]
        else:
            raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        """Check if a row key exists in the table."""
        return key in self._key_to_row

    def __setitem__(self, key: str, value: dict[str, Any]) -> None:
        """Set a row by key (mainly for internal use)."""
        if not key.startswith("$"):
            raise ValueError("Row keys must start with '$'")
        self._key_to_row[key] = value
        # Note: This doesn't update _rows or _row_keys for simplicity
        # Main usage should be through append() method

    def head(self, n: int = 5) -> "Table":
        """
        Return first n rows.

        Args:
            n: Number of rows to return (default 5)

        Returns:
            New Table with first n rows
        """
        return Table(self._rows[:n])

    def tail(self, n: int = 5) -> "Table":
        """
        Return last n rows.

        Args:
            n: Number of rows to return (default 5)

        Returns:
            New Table with last n rows
        """
        return Table(self._rows[-n:])

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """
        Iterate over rows in insertion order.

        Examples:
            >>> t = Table([{"id": 1}, {"id": 2}])
            >>> for row in t:
            ...     print(row["id"])
            1
            2
        """
        return iter(self._rows)

    def __len__(self) -> int:
        """
        Return the number of rows in the table.

        Examples:
            >>> t = Table([{"id": 1}, {"id": 2}])
            >>> len(t)
            2
        """
        return len(self._rows)

    @classmethod
    def from_csv(
        cls,
        path: str | Path,
        *,
        delimiter: str = ",",
        encoding: str = "utf-8",
        header: bool | int = True,
        columns: list[str] | None = None,
        dtypes: dict[str, type] | None = None,
        parse_dates: bool | list[str] = False,
        null_values: list[str] | None = None,
        skip_rows: int = 0,
        max_rows: int | None = None,
    ) -> "Table":
        """
        Create a Table from a CSV file.
        
        Args:
            path: Path to the CSV file
            delimiter: Field delimiter (default: ",")
            encoding: File encoding (default: "utf-8")
            header: Whether first row contains headers (True), 
                    row index of headers (int), or no headers (False)
            columns: Column names to use (overrides file headers)
            dtypes: Dict mapping column names to types for parsing
            parse_dates: Parse date columns. If True, auto-detect.
                         If list, parse specified columns as dates
            null_values: List of strings to interpret as null/None
            skip_rows: Number of rows to skip from beginning
            max_rows: Maximum number of rows to read
        
        Returns:
            New Table with CSV data as rows
        
        Examples:
            >>> # Basic usage
            >>> table = Table.from_csv("data.csv")
            
            >>> # Custom delimiter and encoding
            >>> table = Table.from_csv("data.tsv", delimiter="\t", encoding="latin-1")
            
            >>> # Specify column types
            >>> table = Table.from_csv("data.csv", dtypes={
            ...     "age": int,
            ...     "salary": float,
            ...     "active": bool
            ... })
            
            >>> # Parse date columns
            >>> table = Table.from_csv("orders.csv", parse_dates=["order_date", "ship_date"])
            
            >>> # Handle missing values
            >>> table = Table.from_csv("data.csv", null_values=["NA", "N/A", "null", ""])
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")
        
        # Default null values if not specified
        if null_values is None:
            null_values = ["NA", "N/A", "null", ""]
        
        rows = []
        
        try:
            with open(path, "r", encoding=encoding, newline="") as f:
                # Skip initial rows if requested
                for _ in range(skip_rows):
                    next(f, None)
                
                reader = csv.reader(f, delimiter=delimiter)
                
                # Handle header
                first_data_row = None
                if header is True:
                    # First row is header
                    file_columns = next(reader, [])
                elif isinstance(header, int) and header is not False:
                    # Header at specific row index
                    for _ in range(header):
                        next(reader, None)
                    file_columns = next(reader, [])
                else:
                    # No header - first row is data
                    file_columns = None
                    first_data_row = next(reader, None)
                
                # Use provided columns or file columns or generate numeric columns
                if columns:
                    column_names = columns
                elif file_columns:
                    column_names = file_columns
                else:
                    # Generate column names based on first row
                    if first_data_row:
                        column_names = [f"col_{i}" for i in range(len(first_data_row))]
                    else:
                        column_names = []
                
                # Process the first data row if we read it during header handling
                if first_data_row and column_names:
                    # Handle column count mismatch
                    row_data = first_data_row[:]  # Make a copy
                    if len(row_data) != len(column_names):
                        if len(row_data) < len(column_names):
                            # Pad with None
                            row_data.extend([None] * (len(column_names) - len(row_data)))
                        else:
                            # Truncate
                            row_data = row_data[:len(column_names)]
                    
                    row_dict = cls._process_csv_row(
                        row_data, column_names, dtypes, parse_dates, null_values
                    )
                    rows.append(row_dict)
                
                # Read remaining rows
                row_count = len(rows)  # Account for any rows already processed
                for row_data in reader:
                    if max_rows and row_count >= max_rows:
                        break
                    
                    if len(row_data) != len(column_names):
                        # Handle rows with different number of columns
                        if len(row_data) < len(column_names):
                            # Pad with None
                            row_data.extend([None] * (len(column_names) - len(row_data)))
                        else:
                            # Truncate
                            row_data = row_data[:len(column_names)]
                    
                    row_dict = cls._process_csv_row(
                        row_data, column_names, dtypes, parse_dates, null_values
                    )
                    rows.append(row_dict)
                    row_count += 1
        
        except PermissionError:
            raise PermissionError(f"Permission denied reading file: {path}")
        except Exception as e:
            raise ValueError(f"Error reading CSV file {path}: {e}")
        
        return cls(rows)
    
    @classmethod
    def _process_csv_row(
        cls,
        row_data: list[str],
        column_names: list[str],
        dtypes: dict[str, type] | None,
        parse_dates: bool | list[str],
        null_values: list[str],
    ) -> dict[str, Any]:
        """Process a single CSV row, applying type conversions."""
        row_dict = {}
        
        for col_name, value in zip(column_names, row_data):
            # Check for null values
            if value in null_values:
                row_dict[col_name] = None
                continue
            
            # Apply type conversion
            if dtypes and col_name in dtypes:
                # Explicit type conversion
                try:
                    if dtypes[col_name] == bool:
                        row_dict[col_name] = value.lower() in ("true", "1", "yes", "y")
                    else:
                        row_dict[col_name] = dtypes[col_name](value)
                except (ValueError, TypeError):
                    # Keep as string if conversion fails
                    row_dict[col_name] = value
            elif parse_dates:
                # Date parsing
                if (isinstance(parse_dates, list) and col_name in parse_dates) or \
                   (parse_dates is True and cls._looks_like_date(value)):
                    try:
                        # Try common date formats
                        for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y",
                                   "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"]:
                            try:
                                row_dict[col_name] = datetime.strptime(value, fmt)
                                break
                            except ValueError:
                                continue
                        else:
                            # No format matched, keep as string
                            row_dict[col_name] = value
                    except Exception:
                        row_dict[col_name] = value
                else:
                    # Auto-infer type
                    row_dict[col_name] = cls._infer_type(value)
            else:
                # Auto-infer type
                row_dict[col_name] = cls._infer_type(value)
        
        return row_dict
    
    @classmethod
    def _infer_type(cls, value: str) -> Any:
        """Attempt to infer and convert string value to appropriate type."""
        # Handle None case
        if value is None:
            return None
        
        # Check for boolean
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Check if it looks like JSON
        if (value.startswith('{') and value.endswith('}')) or \
           (value.startswith('[') and value.endswith(']')):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        
        # Return as string
        return value
    
    @classmethod
    def _looks_like_date(cls, value: str) -> bool:
        """Heuristic to check if a string looks like a date."""
        # Simple heuristics
        if len(value) < 6 or len(value) > 30:
            return False
        
        # Check for common date separators and patterns
        date_indicators = ["-", "/", ":", "20", "19"]
        matches = sum(1 for indicator in date_indicators if indicator in value)
        return matches >= 2
    
    def to_csv(
        self,
        path: str | Path,
        *,
        delimiter: str = ",",
        encoding: str = "utf-8",
        header: bool = True,
        columns: list[str] | None = None,
        index: bool = False,
        null_value: str = "",
        float_format: str | None = None,
        date_format: str | None = None,
        mode: str = "w",
    ) -> None:
        """
        Write the Table to a CSV file.
        
        Args:
            path: Output file path
            delimiter: Field delimiter (default: ",")
            encoding: File encoding (default: "utf-8")
            header: Whether to write column headers
            columns: Specific columns to write (default: all columns)
            index: Whether to write row keys as first column
            null_value: String representation for None values
            float_format: Format string for floating point numbers (e.g., "%.2f")
            date_format: Format string for datetime objects (e.g., "%Y-%m-%d")
            mode: File write mode ("w" for overwrite, "a" for append)
        
        Examples:
            >>> # Basic export
            >>> table.to_csv("output.csv")
            
            >>> # Tab-separated with specific columns
            >>> table.to_csv("output.tsv", delimiter="\t", columns=["name", "age", "city"])
            
            >>> # Include row keys and format numbers
            >>> table.to_csv("output.csv", index=True, float_format="%.2f")
            
            >>> # Append to existing file
            >>> table.to_csv("output.csv", mode="a", header=False)
        """
        path = Path(path)
        
        # Determine columns to write
        if columns:
            write_columns = columns
        else:
            # Get all columns from the table
            write_columns = list(self.columns)
        
        # Add index column if requested
        if index:
            write_columns = ["_index"] + write_columns
        
        try:
            with open(path, mode, encoding=encoding, newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=write_columns,
                    delimiter=delimiter,
                    extrasaction='ignore'  # Ignore extra fields not in fieldnames
                )
                
                # Write header if requested
                if header:
                    writer.writeheader()
                
                # Write rows
                for i, row in enumerate(self._rows):
                    write_row = {}
                    
                    # Add index if requested
                    if index:
                        # Get the row key
                        row_key = None
                        for key, idx in self._row_keys.items():
                            if idx == i:
                                row_key = key
                                break
                        write_row["_index"] = row_key or f"${i}"
                    
                    # Process each column
                    for col in write_columns:
                        if col == "_index":
                            continue  # Already handled
                        
                        value = row.get(col)
                        
                        # Format the value
                        if value is None:
                            write_row[col] = null_value
                        elif isinstance(value, float) and float_format:
                            write_row[col] = float_format % value
                        elif isinstance(value, datetime) and date_format:
                            write_row[col] = value.strftime(date_format)
                        elif isinstance(value, (dict, list)):
                            # Serialize complex types as JSON
                            write_row[col] = json.dumps(value)
                        else:
                            write_row[col] = str(value)
                    
                    writer.writerow(write_row)
        
        except PermissionError:
            raise PermissionError(f"Permission denied writing to file: {path}")
        except Exception as e:
            raise ValueError(f"Error writing CSV file {path}: {e}")
    
    @classmethod
    def from_parquet(
        cls,
        path: str | Path,
        *,
        columns: list[str] | None = None,
        filters: list[tuple] | None = None,
        use_nullable_dtypes: bool = True,
    ) -> "Table":
        """
        Create a Table from a Parquet file.
        
        Args:
            path: Path to the Parquet file
            columns: Specific columns to read (default: all)
            filters: Row-level filters using PyArrow syntax
                     e.g., [("age", ">", 18), ("city", "in", ["NYC", "LA"])]
            use_nullable_dtypes: Use pandas nullable dtypes for better None handling
        
        Returns:
            New Table with Parquet data as rows
        
        Examples:
            >>> # Basic usage
            >>> table = Table.from_parquet("data.parquet")
            
            >>> # Read specific columns
            >>> table = Table.from_parquet("data.parquet", columns=["id", "name", "score"])
            
            >>> # Apply filters during read
            >>> table = Table.from_parquet("data.parquet", filters=[
            ...     ("year", ">=", 2020),
            ...     ("status", "==", "active")
            ... ])
        
        Note: Requires pyarrow to be installed
        """
        pa, pq = cls._check_pyarrow()
        
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Parquet file not found: {path}")
        
        try:
            # Read parquet file
            table = pq.read_table(
                path,
                columns=columns,
                filters=filters,
            )
            
            # Convert to list of dicts using PyArrow directly
            rows = []
            
            # Convert PyArrow table to Python objects
            for i in range(table.num_rows):
                row_dict = {}
                for j, column_name in enumerate(table.column_names):
                    column = table.column(j)
                    value = column[i].as_py()  # Convert to Python object
                    row_dict[column_name] = value
                rows.append(row_dict)
            
            return cls(rows)
        
        except PermissionError:
            raise PermissionError(f"Permission denied reading file: {path}")
        except Exception as e:
            raise ValueError(f"Error reading Parquet file {path}: {e}")
    
    def to_parquet(
        self,
        path: str | Path,
        *,
        compression: str = "snappy",
        columns: list[str] | None = None,
        index: bool = False,
        partition_cols: list[str] | None = None,
        schema: Any | None = None,
    ) -> None:
        """
        Write the Table to a Parquet file.
        
        Args:
            path: Output file path or directory (if using partitions)
            compression: Compression codec ("snappy", "gzip", "brotli", "lz4", "zstd", or None)
            columns: Specific columns to write (default: all)
            index: Whether to write row keys as a column
            partition_cols: Columns to use for partitioning the dataset
            schema: PyArrow schema for explicit type control
        
        Examples:
            >>> # Basic export
            >>> table.to_parquet("output.parquet")
            
            >>> # With compression and specific columns
            >>> table.to_parquet("output.parquet", 
            ...                  compression="gzip",
            ...                  columns=["id", "name", "metrics"])
            
            >>> # Partitioned dataset
            >>> table.to_parquet("output_dir/",
            ...                  partition_cols=["year", "month"])
        
        Note: Requires pyarrow to be installed
        """
        pa, pq = self._check_pyarrow()
        
        path = Path(path)
        
        # Prepare data for writing
        write_data = []
        
        for i, row in enumerate(self._rows):
            write_row = {}
            
            # Add index if requested
            if index:
                # Get the row key
                row_key = None
                for key, idx in self._row_keys.items():
                    if idx == i:
                        row_key = key
                        break
                write_row["_index"] = row_key or f"${i}"
            
            # Add specified columns or all columns
            if columns:
                for col in columns:
                    write_row[col] = row.get(col)
            else:
                write_row.update(row)
            
            write_data.append(write_row)
        
        try:
            # Convert to PyArrow table
            if schema:
                # Use provided schema
                pa_table = pa.Table.from_pylist(write_data, schema=schema)
            else:
                # Auto-infer schema
                pa_table = pa.Table.from_pylist(write_data)
            
            # Write to parquet
            if partition_cols:
                # Partitioned dataset
                pq.write_to_dataset(
                    pa_table,
                    root_path=path,
                    partition_cols=partition_cols,
                    compression=compression,
                )
            else:
                # Single file
                pq.write_table(
                    pa_table,
                    path,
                    compression=compression,
                )
        
        except PermissionError:
            raise PermissionError(f"Permission denied writing to file: {path}")
        except Exception as e:
            raise ValueError(f"Error writing Parquet file {path}: {e}")
    
    @classmethod
    def _check_pyarrow(cls):
        """Check if pyarrow is available and return the modules."""
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
            return pa, pq
        except ImportError:
            raise ImportError(
                "Parquet support requires pyarrow. "
                "Install with: uv add pyarrow"
            )
