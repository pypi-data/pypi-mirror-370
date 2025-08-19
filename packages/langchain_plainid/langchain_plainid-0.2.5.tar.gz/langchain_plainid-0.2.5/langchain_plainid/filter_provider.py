from abc import ABC,abstractmethod
from typing import (Any,
	Callable,
    Dict,
	Optional,
	Union,
)

class PlainIDFilterProvider (ABC):
	@abstractmethod
	def get_filter(self) -> Optional[Union[Callable, Dict[str, Any]]]:
		"""
		Returns a PlainID filter string that can be used to filter the documents in the vector store.
		"""