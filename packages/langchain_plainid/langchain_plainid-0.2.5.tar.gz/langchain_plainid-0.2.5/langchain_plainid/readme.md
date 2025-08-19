# langchain_plainid

PlainID for LangChain. Library which helps you to integrate PlainID with LangChain.

## Installation

Based on your environment, you can install the library using pip:

```bash
pip install langchain_plainid
```

## Setup with PlainID

Once you have installed the library, you can set up PlainID access.

1. Retrieve your PlainID credentials to access the platform - client ID and client secret.
2. Find you PlainID base URL. For productiщn platform you can use `https://platform-product.us1.plainid.io`.

_Note_ URL starts from `platform-product`.

These are 3 parameters you need to use with the library.  
_Note_ Please don't share your credentials with anyone, don't store them in your code. Use environment variables or secret management tools to store them.

## Category filtering

To use category filtering with this library, you need to setup related ruleset in PlainID.  
e.g if we are using `categories` template name, we need to add the following ruleset:

```rego
# METADATA
# custom:
#   plainid:
#     kind: Ruleset
#     name: All
ruleset(asset, identity, requestParams, action) if {
	asset.template == "categories"
}
```

and setup what categories are available in PlainID through asset types.
e.g. add the following assets: `contract`, `HR`.

Now it's time to use category filtering in your LangChain application.

```python
	from langchain_plainid import PlainIDCategorizer, PlainIDPermissionsProvider


	permissions_provider = PlainIDPermissionsProvider(
	    client_id="your_client_id",
	    client_secret="your_client_secret",
	    base_url="https://platform-product.us1.plainid.io",
		plainid_categories_resource_type="categories")

    plainid_categorizer = PlainIDCategorizer(classifier_provider=<classifier>,permissions_provider=permissions_provider)
    chain = plainid_categorizer
    query = "I'd like to know the weather forecast for today"
	result = chain.invoke(f"{query}") # push your prompt to the chain
```

Categorizer will connect to PlainID and retrieve the list of categories available in your PlainID account.
Then it will classify your prompt with provided `classifier` and pass your query to the next chain element or break execution with `ValueError` exception.

### Category classifiers

We provide 2 classifiers out of the box:

#### LLMCategoryClassifierProvider

This classifier uses LLM to classify your prompt. It uses `langchain` LLMs to classify your prompt. You can configure it with any LLM you want.

```python
	from langchain_plainid import LLMCategoryClassifierProvider

	llm_classifier = LLMCategoryClassifierProvider(llm=OllamaLLM(model="llama2"))
```

Use it with caution, quality of classification depends on the LLM you are using. Some base models could return bad or even wrong results, so use it with big models (OpenAI, Anthropic, etc.) or with models which are trained for classification tasks.

#### ZeroShotCategoryClassifierProvider

This used LLM model which suits best for classification tasks. During the work it will download the model from HuggingFace and use it to classify your prompt.

```python
	from langchain_plainid import ZeroShotCategoryClassifierProvider

	zeroshot_classifier = ZeroShotCategoryClassifierProvider()
```

Use it if you want better classification results, but also have free space on your disk, and can wait for the model to be downloaded.

## Anonymizer

To use anonymizer with this library, you need to setup related ruleset in PlainID.
e.g if we are using `entities` template name, we need to add the following ruleset:

```rego
# METADATA
# custom:
#   plainid:
#     kind: Ruleset
#     name: PERSON
ruleset(asset, identity, requestParams, action) if {
	asset.template == "entities"
	asset["path"] == "PERSON"
	action.id in ["MASK"]
}
```

We support 2 actions: `MASK` and `ENCRYPT`. You can use them to mask or encrypt your data.
Data is always masked with `***` symbols.

The list of possible anonymization sources are based on PII entities. We are using `presidio` library from Microsoft to detect PII entities in your text. You can find the list of supported entities [here](https://microsoft.github.io/presidio/supported_entities/)

```python
	from langchain_plainid import PlainIDPermissionsProvider,PlainIDAnonymizer


	permissions_provider = PlainIDPermissionsProvider(
	    client_id="your_client_id",
	    client_secret="your_client_secret",
	    base_url="https://platform-product.us1.plainid.io",
		plainid_entities_resource_type="entities")

    plainid_anonymizer = PlainIDAnonymizer(permissions_provider=permissions_provider, encrypt_key="your_encryption_key")
    chain = plainid_anonymizer
    query = "What's the name of the person who is responsible for the contract?"
	result = chain.invoke(f"{query}") # push your prompt to the chain
```

Anonymizer will connect to PlainID and retrieve the list of categories available in your PlainID account.
Then it will classify your text and anonymize it. Processed text will be passed the next chain element or break execution with `ValueError` exception. Exception will be raised if there are some problems, or misalignment in your PlainID ruleset.

## Power of creating your chains with PlainID's internal category filtering and anonymization

As a result you can add something like this to your processing chain:

```python
	chain = plainid_categorizer | llm | vector_store | anonymizer | output_parser
```

This will allow you to filter your data based on categories and anonymize it before passing to the next chain element. You can use any chain element you want, and it will work with PlainID's internal category filtering and anonymization.

## PlainID retriever

To use category filtering with this library, you need to setup related policies in PlainID.  
e.g if we are using `customer` template name, we need to add the following ruleset to filter data based on `country` metadata and some `test_num` field:

```rego
# METADATA
# custom:
#   plainid:
#     kind: Ruleset
#     name: rs1
ruleset(asset, identity, requestParams, action) if {
	asset.template == "customer"
	asset["country"] == "Sweden"
	asset["country"] != "Russia"
	contains(asset["country"], "we")
	startswith(asset["country"], "Sw")
}

# METADATA
# custom:
#   plainid:
#     kind: Ruleset
#     name: rs1
ruleset(asset, identity, requestParams, action) if {
	asset.template == "customer"
	asset["country"] in ["aaa", "bbb"]
	asset["age"] <= 11111
	endswith(asset["country"], "wwww")
}
```

_Note_ that you need to add `country` and `age` parameters to your vector store as `metadata`. This is what PlainID will use to filter your data.

```python
	from langchain_community.vectorstores import Chroma
	from langchain_core.documents import Document
	from langchain_plainid import PlainIDRetriever

	 docs = [
            Document(
                page_content="Stockholm is the capital of Sweden.",
                metadata={"country": "Sweden", "age": 5},
            ),
            Document(
                page_content="Oslo is the capital of Norway.",
                metadata={"country": "Norway", "age": 5},
            ),
            Document(
                page_content="Copenhagen is the capital of Denmark.",
                metadata={"country": "Denmark", "age": 5},
            ),
            Document(
                page_content="Helsinki is the capital of Finland.",
                metadata={"country": "Finland", "age": 5},
            ),
            Document(
                page_content="Malmö is a city in Sweden.",
                metadata={"country": "Sweden", "age": 5},
            ),
        ]

	vector_store = Chroma.from_documents(documents, embeddings)
    plainid_retriever = PlainIDRetriever(vectorstore=vector_store, filter_provider=filter_provider)
    docs = plainid_retriever.invoke("What is the capital of Sweden?")

```

### PlainID filter provider

Filter provider is used to connect to PlainID and retrieve the list of categories available in your PlainID account. The following parameters are required:

```python
base_url (str): Base URL for PlainID service
client_id (str): Client ID for authentication
client_secret (str): Client secret for authentication
entity_id (str): Entity ID for the request
entity_type_id (str): Entity type ID for the request
```

### Supported vector stores and limitations

We support different vector stores, but some of them have limitations in filtering or querying data.
Below is the list of tested vector stores and their limitations (list of not supported PlainID operators).

### FAISS

It doesn't support STARTSWITH, ENDSWITH, CONTAINS operators.

### Chroma

It doesn't support IN, NOT_IN, STARTSWITH, ENDSWITH, CONTAINS operators.
