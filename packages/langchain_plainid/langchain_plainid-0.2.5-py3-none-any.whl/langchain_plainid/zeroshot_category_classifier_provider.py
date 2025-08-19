import logging
from typing import List, Optional

from transformers import pipeline

from .category_classifier_provider import CategoryClassifierProvider

ALL_CATEGORIES = [
    "Weather",
    "Finance",
    "Healthcare",
    "Technology",
    "Education",
    "Sports",
    "Entertainment",
    "Politics",
    "Food",
    "Travel",
    "Fashion",
    "Automotive",
    "Science",
    "Religion",
    "Military",
    "Agriculture",
    "Art",
    "Environment",
    "Law",
    "History",
    "Literature",
    "Mathematics",
    "Architecture",
    "Psychology",
    "Music",
]


class ZeroShotCategoryClassifierProvider(CategoryClassifierProvider):
    """
    A zero-shot category classifier provider implementation.
    Uses Hugging Face transformers pipeline for classification.
    """

    def __init__(self, model_name: str,threshold: float = 0.5):
        self.model_name = model_name
        self.zeroshot_classifier = pipeline(
            "zero-shot-classification", model=model_name
        )
        self.threshold = threshold

    def classify(self, input: str, all_categories: List[str] = [], allowed_categories: List[str] = []) -> Optional[str]:
        """
        Classifies the input text using zero-shot classification.

        Args:
            input (str): The input text to be classified
            categories (List[str]): List of categories to classify input into

        Returns:
            str: The input text, or raises ValueError if no match is found.
        """
        all_categories_lower = [c.lower() for c in all_categories]
      
        if not all_categories_lower:
            raise ValueError("Categories list cannot be empty")


        result = self.zeroshot_classifier(input, all_categories_lower, multi_label=False)
        if result["scores"][0] < self.threshold:
            logging.warning(f"Classification score {result['scores'][0]} is below threshold")
            raise ValueError(
                f"Classification score {result['scores'][0]} is below threshold {self.threshold}"
            )
        top_category = result["labels"][0]
        
        categories_map = {category.lower(): category for category in allowed_categories}

        top_category_lower = top_category.lower()
        if top_category_lower in categories_map:
            matched_category = categories_map[top_category_lower]
            logging.debug(
                f"Classified '{input}' as '{matched_category}' with score {result['scores'][0]}"
            )
            return input

        raise ValueError(
            f"Top category '{top_category}' not in allowed categories: {allowed_categories}"
        )

