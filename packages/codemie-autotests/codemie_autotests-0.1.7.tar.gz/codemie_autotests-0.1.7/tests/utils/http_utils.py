import logging
from typing import TypeVar, Type, Optional, Any, Union, Dict, List

import requests
from pydantic import BaseModel

from codemie_sdk.utils.http import ApiRequestHandler
from codemie_sdk.utils.http import log_request

T = TypeVar("T", bound=Union[BaseModel, List[BaseModel], dict])

logger = logging.getLogger(__name__)


class RequestHandler(ApiRequestHandler):
    """Handles HTTP requests with consistent error handling and response parsing."""

    @log_request
    def post(
        self,
        endpoint: str,
        response_model: Type[T],
        json_data: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        wrap_response: bool = True,
    ) -> Union[T, requests.Response]:
        """Makes a POST request and parses the response.

        Args:
            endpoint: API endpoint path
            response_model: Pydantic model class or List[Model] for response
            json_data: JSON request body
            stream: Whether to return streaming response
            wrap_response: Whether response is wrapped in 'data' field

        Returns:
            Parsed response object/list or streaming response
        """
        if json_data:
            logger.debug(f"Request body: {json_data}")

        response = requests.post(
            url=f"{self._base_url}{endpoint}",
            headers=self._get_headers(),
            json=json_data,
            verify=self._verify_ssl,
            stream=stream,
        )

        if stream:
            return response

        return self._parse_response(response, response_model, wrap_response)
