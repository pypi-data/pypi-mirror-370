import requests
from typing import Optional, Dict, Any

class PageIndexAPIError(Exception):
    """Custom exception for PageIndex API errors."""
    pass

class PageIndexClient:
    """
    Python SDK client for the PageIndex API.
    """

    BASE_URL = "https://api.pageindex.ai"

    def __init__(self, api_key: str):
        """
        Initialize the client with your API key.
        """
        self.api_key = api_key

    def _headers(self) -> Dict[str, str]:
        return {"api_key": self.api_key}

    # ---------- DOCUMENT SUBMISSION ----------

    def submit_document(self, file_path: str) -> Dict[str, Any]:
        """
        Upload a PDF document for processing. The system will automatically process both tree generation and OCR.
        Immediately returns a document identifier (`doc_id`) for subsequent operations.

        Args:
            file_path (str): Path to the PDF file.

        Returns:
            dict: {'doc_id': ...}
        """
        files = {'file': open(file_path, "rb")}
        data = {'if_retrieval': True}
        
        response = requests.post(
            f"{self.BASE_URL}/doc/",
            headers=self._headers(),
            files=files,
            data=data
        )
        files['file'].close()
        
        if response.status_code != 200:
            raise PageIndexAPIError(f"Failed to submit document: {response.text}")
        return response.json()

    # ---------- OCR FUNCTIONALITY ----------

    def get_ocr(self, doc_id: str, format: str = "page") -> Dict[str, Any]:
        """
        Get OCR processing status and results.

        Args:
            doc_id (str): Document ID.
            format (str): Result format. Use 'page' for page-based results or 'node' for node-based results. Defaults to 'page'.

        Returns:
            dict: API response with status and, if ready, OCR results.
        """
        # Validate format parameter
        if format not in ["page", "node"]:
            raise ValueError("Format parameter must be either 'page' or 'node'")
        
        response = requests.get(
            f"{self.BASE_URL}/doc/{doc_id}/?type=ocr&format={format}",
            headers=self._headers()
        )
        if response.status_code != 200:
            raise PageIndexAPIError(f"Failed to get OCR result: {response.text}")
        return response.json()

    # ---------- TREE GENERATION ----------

    def get_tree(self, doc_id: str, node_summary: bool = False) -> Dict[str, Any]:
        """
        Get tree generation status and results.

        Args:
            doc_id (str): Document ID.

        Returns:
            dict: API response with status and, if ready, tree structure.
        """
        response = requests.get(
            f"{self.BASE_URL}/doc/{doc_id}/?type=tree&summary={node_summary}",
            headers=self._headers()
        )
        if response.status_code != 200:
            raise PageIndexAPIError(f"Failed to get tree result: {response.text}")
        return response.json()

    def is_retrieval_ready(self, doc_id: str) -> bool:
        """
        Check if a document is ready for retrieval.

        Args:
            doc_id (str): Document ID.

        Returns:
            bool: True if document is ready for retrieval, False otherwise.
        """
        try:
            result = self.get_tree(doc_id)
            return result.get("retrieval_ready", False)
        except PageIndexAPIError:
            return False

    # ---------- RETRIEVAL ----------

    def submit_query(self, doc_id: str, query: str, thinking: bool = False) -> Dict[str, Any]:
        """
        Submit a retrieval query for a specific PageIndex document.

        Args:
            doc_id (str): Document ID.
            query (str): User question or information need.
            thinking (bool, optional): If true, enables deeper retrieval. Default is False.

        Returns:
            dict: {'retrieval_id': ...}
        """
        payload = {
            "doc_id": doc_id,
            "query": query,
            "thinking": thinking
        }
        response = requests.post(
            f"{self.BASE_URL}/retrieval/",
            headers=self._headers(),
            json=payload
        )
        if response.status_code != 200:
            raise PageIndexAPIError(f"Failed to submit retrieval: {response.text}")
        return response.json()

    def get_retrieval(self, retrieval_id: str) -> Dict[str, Any]:
        """
        Get retrieval status and results.

        Args:
            retrieval_id (str): Retrieval ID.

        Returns:
            dict: Retrieval status and results.
        """
        response = requests.get(
            f"{self.BASE_URL}/retrieval/{retrieval_id}/",
            headers=self._headers()
        )
        if response.status_code != 200:
            raise PageIndexAPIError(f"Failed to get retrieval result: {response.text}")
        return response.json()

    # ---------- DOCUMENT MANAGEMENT ----------

    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Delete a PageIndex document and all its associated data.

        Args:
            doc_id (str): Document ID.

        Returns:
            dict: API response.
        """
        response = requests.delete(
            f"{self.BASE_URL}/doc/{doc_id}/",
            headers=self._headers()
        )
        if response.status_code != 200:
            raise PageIndexAPIError(f"Failed to delete document: {response.text}")
        return response.json() 