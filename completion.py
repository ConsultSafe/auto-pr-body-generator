from prompt import Prompt
from uuid import uuid4
import logging
from enum import Enum


class Completion:
    class State(Enum):
        UNCOMPLETE = "UNCOMPLETE"
        COMPLETED = "COMPLETED"

    def __init__(self, prompt: Prompt, openai_client):
        self._id = f"hash(prompt)-{uuid4()}"
        self._openai_client = openai_client
        self._prompt = prompt
        self._state = self.State.UNCOMPLETE
        self._result = ""

    @property
    def id(self):
        return self._id

    @property
    def result(self):
        return self._result

    @property
    def state(self):
        return self._state

    def _complete_prompt(self) -> str:
        messages = [
            {"role": "system", "content": """
            You are an expert at summarising code changes in Pull Requests concisely and accurately for developers to have insight before reading the code.
            Format the following text into a Pull Request Body with the following headings in markdown format: 
             - Summary 
             - List of changes 
             - Refactoring Target
             Remove duplicate information.

            The following message will contain the text to format.
            """},
            {"role": "user", "content": self._prompt.text},
        ]
        response = self._openai_client.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages, max_tokens=16384
        )
        return response.choices[0].message['content']

    def complete(self):
        logging.info(f"completion_{self.id} - Completing prompt...")
        logging.info(f"completion_{self.id} - prompt to complete: ")
        logging.info(f"completion_{self.id} - {self._prompt}")
        self._result = self._complete_prompt()
        self._state = self.State.COMPLETED
        logging.info(f"completion_{self.id} - Complete")
        logging.info(f"completion_{self.id} - Result: {self.result}")

    def __eq__(self, completion: "Completion"):
        return self._id == completion._id

    def __repr__(self):
        return f"{self.id} - {self.state} - result: {self.result}"
