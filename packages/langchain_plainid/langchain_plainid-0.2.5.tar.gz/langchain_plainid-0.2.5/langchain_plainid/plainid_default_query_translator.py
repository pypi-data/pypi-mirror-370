from typing import Dict, Tuple, Union

from langchain_core.structured_query import (
    Comparator,
    Comparison,
    Operation,
    Operator,
    StructuredQuery,
    Visitor,
)


class PlainIDDefaultQueryTranslator(Visitor):
    """Translate internal query language elements to valid filters."""

    allowed_operators = [Operator.AND, Operator.OR, Operator.NOT]
    """Subset of allowed logical operators."""
    allowed_comparators = [
        Comparator.EQ,
        Comparator.NE,
        Comparator.GT,
        Comparator.GTE,
        Comparator.LT,
        Comparator.LTE,
        Comparator.IN,
        Comparator.NIN,
        Comparator.CONTAIN,
        Comparator.LIKE,
    ]
    """Subset of allowed logical comparators."""

    # Mapping from langchain comparators/operators to PlainID filter syntax
    operator_mapping = {
        Operator.AND.value: "and",
        Operator.OR.value: "or",
        Operator.NOT.value: "not",
        Comparator.EQ.value: "eq",
        Comparator.NE.value: "neq",
        Comparator.GT.value: "gt",
        Comparator.GTE.value: "gte",
        Comparator.LT.value: "lt",
        Comparator.LTE.value: "lte",
        Comparator.IN.value: "in",
        Comparator.NIN.value: "nin",
        Comparator.CONTAIN.value: "contains",
        Comparator.LIKE.value: "like",
    }

    def _validate_func(self, func: Union[Operator, Comparator]) -> None:
        """Validate that the function is allowed."""
        if isinstance(func, Operator) and func not in self.allowed_operators:
            allowed_values = [op.value for op in self.allowed_operators]
            raise ValueError(
                f"Operator {func.value} not allowed. Allowed operators: {allowed_values}"
            )
        elif isinstance(func, Comparator) and func not in self.allowed_comparators:
            allowed_values = [comp.value for comp in self.allowed_comparators]
            raise ValueError(
                f"Comparator {func.value} not allowed. Allowed comparators: {allowed_values}"
            )

    def _format_func(self, func: Union[Operator, Comparator]) -> str:
        self._validate_func(func)
        mapped_value = self.operator_mapping.get(func.value, func.value)
        return f"${mapped_value}"

    def visit_operation(self, operation: Operation) -> Dict:
        args = [arg.accept(self) for arg in operation.arguments]
        return {self._format_func(operation.operator): args}

    def visit_comparison(self, comparison: Comparison) -> Dict:
        return {
            comparison.attribute: {
                self._format_func(comparison.comparator): comparison.value
            }
        }

    def visit_structured_query(
        self, structured_query: StructuredQuery
    ) -> Tuple[str, dict]:
        if structured_query.filter is None:
            kwargs = {}
        else:
            kwargs = {"filter": structured_query.filter.accept(self)}
        return structured_query.query, kwargs
