"""
Prompt templates for LLM interactions in the news thread analysis system.
"""

SUMMARIZE_NEWS = """You are a professional news writer. Your task is to summarize the following news article.

News Title:
{title}

News Description:
{description}

News Content:
{content}

Please provide a concise summary that includes the key points and entities from the news. The summary should be informative and capture the essence of the article."""

SIMILARITY_SCORE = """You are a news expert. Your task is to analyze the similarity between a news article and an existing news thread.

News Article:
Title: {news_title}
Description: {news_description}
Content: {news_content}

Existing Thread:
Title: {thread_title}
Summary: {thread_summary}

Please analyze the similarities and differences between the news article and the existing thread. Consider factors such as:
- Topic relevance
- Key entities mentioned
- Geographic locations
- Time relevance
- Event connections

Provide your analysis and assign a similarity score between 0 and 100 (inclusive), where:
- 0 means not relevant at all
- 100 means exactly matching or highly related

Your response must be a valid JSON object with the following structure:
{{
    "llm_similarity_justification": "Your detailed reasoning for the similarity score",
    "llm_similarity_score": <integer between 0 and 100>
}}"""

UPDATE_THREAD_SUMMARY = """You are a professional news writer. Your task is to update an existing news thread based on a new article being added to it.

New News Article:
Title: {news_title}
Description: {news_description}
Content: {news_content}

Current Thread:
Title: {thread_title}
Summary: {thread_summary}

Please provide:
1. An updated thread title that reflects the evolving story
2. An updated thread summary incorporating the new information
3. Determine if this news likely concludes or resolves the thread

For the status determination:
- Use "likely resolved" if the news represents a conclusion (e.g., final court verdict, competition outcome, resolution of conflict)
- Use "evolving" if the story is still developing

Your response must be a valid JSON object with the following structure:
{{
    "llm_title": "Updated thread title",
    "llm_summary": "Updated comprehensive summary incorporating the new article",
    "status": "evolving" or "likely resolved"
}}"""
