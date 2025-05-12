import logging
from typing import List
from datetime import datetime
import json

import requests
from requests.exceptions import RequestException

from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_gateway import StoreGateway


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def _default_serializer(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]) -> bool:
        """
        Save the processed road data to the Store API.

        Parameters:
            processed_agent_data_batch (List[ProcessedAgentData]): Processed road data to be saved.

        Returns:
            bool: True if the data is successfully saved, False otherwise.
        """
        logging.info("Saving data to Store API")

        url = f"{self.api_base_url}/processed_agent_data/"
        payload = [item.model_dump() for item in processed_agent_data_batch]

        try:
            json_payload = json.dumps(payload, default=self._default_serializer)
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, data=json_payload, headers=headers)

            if response.status_code != 200:
                logging.error(
                    f"Store API returned status {response.status_code}.\n"
                    f"Payload: {json_payload}\n"
                    f"Response content: {response.text}"
                )
                return False
            return True

        except RequestException as e:
            logging.error(f"Request to Store API failed: {e}")
            return False
