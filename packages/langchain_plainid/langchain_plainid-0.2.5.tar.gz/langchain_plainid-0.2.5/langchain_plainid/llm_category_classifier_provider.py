from typing import List, Optional
from langchain_plainid import CategoryClassifierProvider
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



CLASSIFICATION_PROMPT = """
    You are a smart agent with an ability to classify text into categories.
    You will be given a text and you will classify it into one of the categories.
    If the text does not match any category, respond with "Other".
    Categories: {categories}
    Text: {query}
    Respond with only the top category name."""

class LLMCategoryClassifierProvider(CategoryClassifierProvider):
    def __init__(self, llm ,prompt_template = None):
        super().__init__()
        self.llm = llm
        if prompt_template is None:
            self.prompt_template = CLASSIFICATION_PROMPT
        else:
            self.prompt_template = prompt_template
        
    def classify(self, query: str, all_categories: List[str], allowed_categories: List[str]) -> Optional[str]:
        all_categories_lower = [c.lower() for c in all_categories]
        input_categories_lower = [c.lower() for c in allowed_categories]
        
        prompt = ChatPromptTemplate.from_template(self.prompt_template)
        chain = prompt | self.llm  | StrOutputParser()
        top_category = chain.invoke({"query": query, "categories": all_categories_lower, "allowed_categories": input_categories_lower})
        logger.info(f"LLM classification result: {top_category}")
        categories_map = {category.lower(): category for category in allowed_categories}
        if top_category.lower() in categories_map:
            matched_category = categories_map[top_category.lower()]
            logging.debug(
                f"Classified '{query}' as '{matched_category}'"
            )
            return query
        raise ValueError(
            f"Top category '{top_category}' not in allowed categories: {allowed_categories}"
        )
