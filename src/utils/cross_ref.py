from typing import List, Dict, Any
from src.models.llm import GeminiClient
import logging
import json

class CrossReferencer:
    """
    Uses an LLM to intelligently compare and contrast multiple documents.
    """
    def __init__(self, gemini_client: GeminiClient):
        """
        Initializes the CrossReferencer with a GeminiClient instance.

        Args:
            gemini_client: An active instance of the GeminiClient.
        """
        if not isinstance(gemini_client, GeminiClient):
            raise TypeError("gemini_client must be an instance of GeminiClient")
        self.llm = gemini_client

    def compare_documents(
        self,
        doc_texts: List[str],
        doc_names: List[str],
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Compares multiple documents against each other based on a query.

        Args:
            doc_texts: A list of the full text content of the documents.
            doc_names: A list of the names of the documents.
            query: The user's query to focus the comparison.

        Returns:
            A list of dictionaries, each containing the comparison between two documents.
        """
        if len(doc_texts) < 2:
            logging.warning("Cross-referencing requires at least two documents.")
            return []

        results = []
        # Compare each pair of documents
        for i in range(len(doc_texts)):
            for j in range(i + 1, len(doc_texts)):
                try:
                    comparison = self._llm_compare(
                        text1=doc_texts[i],
                        text2=doc_texts[j],
                        name1=doc_names[i],
                        name2=doc_names[j],
                        query=query
                    )
                    results.append(comparison)
                except Exception as e:
                    logging.error(f"Failed to compare {doc_names[i]} and {doc_names[j]}: {e}")
                    results.append({
                        "doc1": doc_names[i],
                        "doc2": doc_names[j],
                        "error": str(e)
                    })
        
        # Sort results by the AI-generated similarity score
        return sorted(results, key=lambda x: x.get("similarity_score", 0), reverse=True)

    def _llm_compare(
        self,
        text1: str,
        text2: str,
        name1: str,
        name2: str,
        query: str
    ) -> Dict[str, Any]:
        """
        Uses the LLM to generate a structured comparison of two texts.
        """
        # This prompt asks the LLM to act as an analyst and return a JSON object.
        prompt = f"""
        As a policy analyst, compare the following two documents based on the user's query.

        User Query: "{query}"

        Document 1 Name: "{name1}"
        Document 1 Content:
        ---
        {text1[:2000]}
        ---

        Document 2 Name: "{name2}"
        Document 2 Content:
        ---
        {text2[:2000]}
        ---

        Please provide your analysis in a valid JSON format with the following structure:
        {{
          "doc1": "{name1}",
          "doc2": "{name2}",
          "similarities": [
            "List the key similarities related to the query here.",
            "Finding 2",
            "..."
          ],
          "differences": [
            "List the key differences related to the query here.",
            "Finding 2",
            "..."
          ],
          "similarity_score": <An integer score from 1 (very different) to 10 (very similar)>
        }}
        """

        # Use a temporary, specific generation config for this task
        json_gen_config = {
            "temperature": 0.1,
            "response_mime_type": "application/json",
        }

        # We don't need conversation history for this one-off task
        response_text = self.llm.generate(
            prompt=prompt,
            history=[],
            context={"generation_config": json_gen_config} # Pass a special config
        )

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            logging.error("Failed to decode LLM response as JSON.")
            # Return a structured error if JSON parsing fails
            return {
                "doc1": name1,
                "doc2": name2,
                "error": "Failed to get a valid comparison from the AI.",
                "raw_response": response_text
            }
