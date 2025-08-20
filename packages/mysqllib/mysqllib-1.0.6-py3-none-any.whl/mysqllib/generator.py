from typing import Tuple, List, Dict, Union

ConditionsType = Union[Dict[str, Union[str, List[Union[str, int]], Dict]], List[Dict]]


def condition_generator(conditions: ConditionsType) -> Tuple[str, List[Union[str, int]]]:
    """
    Generates SQL condition clauses and values based on provided conditions, supporting AND and OR logic.

    Args:
        conditions (Union[Dict[str, Union[str, List[Union[str, int]], Dict]], List[Dict]]):
            Dictionary or list of conditions. Each dictionary can contain conditions where the key is the column name,
            and the value is either a simple value (for equality), a list with an operator and value,
            or nested dictionaries/lists with "OR" or "AND" keys for complex logic.

    Returns:
        Tuple[str, List[Union[str, int]]]:
            A tuple containing an SQL condition string and a list of corresponding values.
    """

    def process_conditions(conds: Union[Dict[str, Union[str, List[Union[str, int]], Dict]], List[Dict]],
                           join_operator: str = "AND") -> Tuple[str, List[Union[str, int]]]:
        sub_clauses = []
        sub_values = []

        if isinstance(conds, list):
            # If conds is a list, process each dictionary in it
            for cond in conds:
                clause, values = process_conditions(cond, "AND")
                sub_clauses.append(f"({clause})")
                sub_values.extend(values)
        else:
            # If conds is a dictionary, process normally
            for column, condition in conds.items():
                if column == "OR":
                    # Handle OR conditions
                    or_clause, or_values = process_conditions(condition, "OR")
                    sub_clauses.append(f"({or_clause})")
                    sub_values.extend(or_values)
                elif column == "AND":
                    # Handle AND conditions
                    and_clause, and_values = process_conditions(condition, "AND")
                    sub_clauses.append(f"({and_clause})")
                    sub_values.extend(and_values)
                else:
                    # Handle simple condition or operator-based condition
                    if isinstance(condition, list) and len(condition) == 2:
                        operator, value = condition
                        sub_clauses.append(f"{column} {operator} %s")
                        sub_values.append(value)
                    else:
                        sub_clauses.append(f"{column} = %s")
                        sub_values.append(condition)

        condition_str = f" {join_operator} ".join(sub_clauses)
        return condition_str, sub_values

    # Start processing the top-level conditions
    if isinstance(conditions, list):
        # If top-level conditions are a list, process each one separately
        main_clauses = []
        main_values = []
        for cond in conditions:
            clause, values = process_conditions(cond, "AND")
            main_clauses.append(f"({clause})")
            main_values.extend(values)
        condition_str = " OR ".join(main_clauses)  # Combine different sets with OR
    else:
        # If it's a single dictionary, process as usual
        condition_str, main_values = process_conditions(conditions)

    return condition_str, main_values
