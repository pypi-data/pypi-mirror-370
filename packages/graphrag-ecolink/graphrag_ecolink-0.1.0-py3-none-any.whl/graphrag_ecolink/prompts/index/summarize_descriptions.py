# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A file containing prompts definition."""

SUMMARIZE_PROMPT = """
You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.
Given one or more entities, and a list of descriptions, all related to the same entity or group of entities.
Please concatenate all of these into a single, comprehensive description. Make sure to include information collected from all the descriptions.
If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.
Make sure it is written in third person, and include the entity names so we have the full context.
Limit the final description length to {max_length} words.
Please preserve all entity names in their **original form** exactly as they appear in the text. Do not transliterate (e.g., into Pinyin) or translate them into English. Entity names and description should remain in Chinese characters if they appear in Chinese in the original text.

#######
-Data-
Entities: {entity_name}
Description List: {description_list}
#######
Output:
"""
