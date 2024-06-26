from prompt import Prompt
from completion import Completion
import inspect
import logging


class PrBodyGenerator:
    MAX_SUMMARY_DEPTH = 5
    PR_BODY_PROMPT = Prompt(
        inspect.cleandoc(
            """ 
            Format the following text into a Pull Request Body with the following sections in markdown: 
             - Summary 
             - List of changes 
             - Refactoring Target
             Remove duplicate information.

            Text to format: 
            """
        )
    )

    def __init__(self, openai_client, diff_analysis: str):
        self.openai_client = openai_client
        self.body = diff_analysis

    def generate_body(self):
        logging.info("Initial body")
        logging.info(self.body)

        body_formatting_prompt = self.PR_BODY_PROMPT.concat(
            Prompt(self.body).wrap("###")
        )
        # Sumarize body
        if not body_formatting_prompt.is_valid:
            self.body = str(self.summarize(Prompt(self.body)))
            logging.info("=== summarized body ===")
            logging.info(self.body)

        # Add PR and markdown
        body_completion = Completion(body_formatting_prompt, self.openai_client)
        body_completion.complete()
        self.body = body_completion.result

        logging.info("=== Final Body ===")
        logging.info(self.body)

    def summarize(self, prompt: Prompt, depth=0) -> Prompt:
        if prompt.is_valid:
            return prompt

        print(f"Summarzing at depth {depth}...")
        if depth >= self.MAX_SUMMARY_DEPTH:
            print("Max depth, returning prompt as is")
            return prompt

        next_depth = depth + 1

        summary_prompt = Prompt(inspect.cleandoc(""" Summarize the following text: """))
        complete_prompt = summary_prompt.concat(prompt)
        if complete_prompt.is_valid:
            print(f"Finaly summary at depth {depth}, returning prompt")
            summary_completion = Completion(complete_prompt, self.openai_client)
            summary_completion.complete()
            return Prompt(summary_completion.result)

        split_prompts = Prompt(self.body).split()
        print(f"Too big to summarize, splitted in {len(split_prompts)} prompts")
        summary = Prompt("")
        for split_prompt in split_prompts:
            summary = summary.concat(self.summarize(split_prompt, next_depth))
        return self.summarize(summary, next_depth)
