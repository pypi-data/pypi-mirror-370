from abc import ABC, abstractmethod
from typing import List, Optional


class CategoryClassifierProvider(ABC):
    @abstractmethod
    def classify(self, input: str, all_categories: List[str], allowed_categories: List[str]) -> Optional[str]:
        """
        Classifies the input text and returns the category name.

        Args:
            input (str): The input text to be classified
            categories (List[str]): List of categories to classify input into
            allowed_categories (List[str]): List of categories that are allowed fro the user

        Returns:
            Optional[str]: The classified category name or None if classification failed
        """
