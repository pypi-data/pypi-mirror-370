"""Prompt library module."""
import json
import os
from pathlib import Path
from typing import Dict


class PromptLibrary:
    """
    Prompt library is a prompt generation manager class.

    It loads prompts from local directory and also loads placeholder dictionaries.
    It provides a method to generate complete prompts.
    """

    def __init__(self, path_to_library: Path):
        """Initialize the PromptLibrary class."""
        self._load_library(path_to_library)

    def _load_library(self, path_to_library: Path):
        self.library = {}
        prompt_types = [
            f for f in os.listdir(path_to_library) if os.path.isdir(path_to_library / f)
        ]
        for prompt_type in prompt_types:
            self.library[prompt_type] = {}
            prompt_subtypes = [
                f
                for f in os.listdir(path_to_library / prompt_type)
                if os.path.isdir(path_to_library / prompt_type / f)
            ]
            for prompt_subtype in prompt_subtypes:
                self.library[prompt_type][prompt_subtype] = {}
                self._load_prompt(path_to_library, prompt_type, prompt_subtype)

    def _load_prompt(
        self, path_to_library: Path, prompt_type: str, prompt_subtype: str
    ):
        files = os.listdir(path_to_library / prompt_type / prompt_subtype)
        for file in files:
            if file == "placeholders.json":
                with open(path_to_library / prompt_type / prompt_subtype / file) as f:
                    placeholders = json.load(f)
                    self.library[prompt_type][prompt_subtype][
                        "placeholders"
                    ] = placeholders
            elif ".txt" in file:
                with open(path_to_library / prompt_type / prompt_subtype / file) as f:
                    prompt = f.read()
                    self.library[prompt_type][prompt_subtype]["prompt"] = prompt

    def create_prompt(self, prompt: str, placeholders: Dict[str, str]) -> str:
        """Create a prompt by replacing placeholders in the prompt template text. Main function of the PromptLibrary class.

        Args:
            prompt: prompt template.
            placeholders: dictionary of placeholders keys and values.

        Returns:
            str: complete prompt.

        """
        result = prompt
        for placeholder in placeholders.keys():
            result = result.replace(placeholder, str(placeholders[placeholder]))
        return result


prompt_library = PromptLibrary(Path(__file__).parent / "library")
