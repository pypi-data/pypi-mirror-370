from dataclasses import dataclass, field

from ..internal.expressions.runtime import evaluate


@dataclass
class _PaginationHelper:
    supported: bool = False
    results_attribute: str = ""
    results: list = field(default_factory=list)
    iter_idx: int = 0
    iter_func: callable = None


@dataclass
class Paginator:
    """
    This class allows to paginate the results of an API response instance.
    """

    _pagination: _PaginationHelper = field(
        default_factory=_PaginationHelper, compare=False
    )

    def __iter__(self):
        self._pagination.iter_idx = 0
        return self

    def __next__(self) -> bool:
        if not self._pagination.results:
            self._pagination.results = evaluate(
                self.http_response(), self._pagination.results_attribute
            )

        results = self._pagination.results
        if self._pagination.iter_idx >= len(results):
            if self._pagination.iter_func:
                next_results = self._pagination.iter_func()
                self._pagination.iter_func = next_results._pagination.iter_func
                self._pagination.results.extend(
                    evaluate(
                        next_results.http_response(), self._pagination.results_attribute
                    )
                )

        if self._pagination.iter_idx >= len(results):
            raise StopIteration

        i = self._pagination.iter_idx
        self._pagination.iter_idx = self._pagination.iter_idx + 1
        return results[i]
