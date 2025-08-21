"""LLM related functions."""
import logging

logger = logging.getLogger(__name__)

import base64
import json

from openai import AsyncOpenAI as OpenAI
from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part,
)

from src.utils import cache_on_disk


# flake8: noqa
# pylint: disable=all
class LlmClient:
    """A client for interacting with large language models (LLMs)."""

    def __init__(self, openai_key=None, parameters=None):
        """Initialize the LLM client."""
        # Initialize the model parameters
        self.model_params = {
            "temperature": parameters.get("temperature", 0),
            "max_output_tokens": parameters.get("maxOutputTokens", 8000),
            "top_p": parameters.get("top_p", 0.8),
            "top_k": parameters.get("top_k", 40),
            "seed": parameters.get("seed", 42),
        }
        self.model_id = parameters.get("model_id", "gemini-1.5-pro-001")
        # Initialize the safety configuration
        self.safety_config = {
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        }
        # Initialize the Gemini client
        self.geminy_client = self._initialize_gemini()
        if openai_key is not None:
            # Initialize the ChatGPT client
            self.chatgpt_client = self._create_client_chatgpt(openai_key)

    def _initialize_gemini(self):
        """Ask the Gemini model a question.

        Returns:
            str: The response from the model.
        """
        # Initialize the model if it is not already initialized
        model_gen = GenerativeModel(model_name=self.model_id)
        self.model_config = GenerationConfig(**self.model_params)

        return model_gen

    def _create_client_chatgpt(self, openai_key):
        client = OpenAI(api_key=openai_key)
        return client

    async def ask_gemini(
        self,
        prompt: str,
        document: str = None,
        response_schema: dict = None,
        response_mime_type: str = "application/json",
    ):
        """Ask the Gemini model a question.

        Args:
            prompt (str): The prompt to send to the model.
            document (str, optional): An optional document to provide context.
            response_schema (dict, optional): Defines a specific response schema for the model.

        Returns:
            str: The response from the model.
        """
        try:

            # Start with the default model configuration
            config = self.model_config

            # Add response_schema if provided. This is only supported for Gemini 1.5 Flash & Pro models
            if response_schema is not None:
                config = GenerationConfig(
                    response_schema=response_schema,
                    response_mime_type=response_mime_type,
                    **self.model_params,
                )

            # Prepare inputs for the model
            inputs = [document, prompt] if document else prompt

            # Generate the response
            model_response = await cache_on_disk(
                self.geminy_client.generate_content_async,
                contents=inputs,
                generation_config=config,
                safety_settings=self.safety_config,
            )

            response_text = model_response.text

            return response_text

        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            return "{}"

    async def get_unified_json_genai(
        self, prompt, document=None, response_schema=None, model="gemini"
    ):
        """Send a prompt to a Google Cloud AI Platform model and returns the generated json.

        Args:
            prompt (str): The prompt to send to the LLM model.
            document: Content of the PDF document
            response_schema: The schema to use for the response
            model (str): The model to use for the response ["gemini" or "chatGPT"]. Default is "gemini".

        Returns:
            dict: The generated json from the model.
        """
        # Ask the LLM model
        if model.lower() in {"chatgpt", "openai", "gpt"}:
            response = await self.ask_chatgpt(prompt, document, response_schema)
        else:
            # Default to Gemini
            response = await self.ask_gemini(prompt, document, response_schema)

        try:
            return json.loads(response)
        except json.decoder.JSONDecodeError as e:
            logger.error(e)
            return {}

    def prepare_document_for_gemini(self, file_content):
        """Prepare a document from file content by encoding it to base64.

        Args:
            file_content (bytes): The binary content of the file to be processed.

        Returns:
            Part: A document object ready for processing by the language model.
        """
        # Convert binary file to base64
        pdf_base64 = base64.b64encode(file_content).decode("utf-8")

        # Create the document for the model
        document = Part.from_data(
            mime_type="application/pdf", data=base64.b64decode(pdf_base64)
        )

        return document

    async def ask_chatgpt(self, prompt: str, document=None, response_schema=None):
        """Ask the chatgpt model a question.

        Args:
            prompt (str): The prompt to ask the model.
            document (base64): the image to send the model
            response_schema (dict): The schema to use for the response
        Returns:
            str: The response from the model.
        """
        # Check if chatgpt_client was initialised
        if self.chatgpt_client is None:
            logger.error("Attempting to call chatgpt model that was not initialised.")
            return ""

        inputs = [{"type": "text", "text": prompt}]
        if document:
            inputs.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{document}",
                    },
                }
            )
        completion = await cache_on_disk(
            self.chatgpt_client.chat.completions.create,
            model="gpt-4o",
            temperature=0.1,
            messages=[{"role": "user", "content": inputs}],
            response_format=response_schema,
        )
        response = completion.choices[0].message.content
        return response


def prompt_excel_extraction(excel_structured_text):
    """Write a prompt to extract data from Excel files.

    Args:
        excel_structured_text (str): The structured text of the Excel file.

    Returns:
        prompt str: The prompt for common json.
    """
    prompt = f"""{excel_structured_text}

    Task: Fill in the following dictionary from the information in the given in the above excel data.

    Instructions:
    - Do not change the keys of the following dictionary.
    - The values should be filled in as per the schema provided below.
    - If an entity contains a 'display_name', consider its properties as child data points in the below format.
    {{'data-field': {{
        'child-data-field': 'type -occurrence_type- description',
          }}
    }}
    - The entity with 'display_name' can be extracted multiple times. Please pay attention to the occurrence_type.
    - Ensure the schema reflects the hierarchical relationship.
    - Use the data field description to understand the context of the data.

    """
    return prompt


# pylint: enable=all
