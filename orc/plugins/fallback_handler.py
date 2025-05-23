import json
import logging
from typing import Dict, List, Optional
from azure.storage.blob import BlobServiceClient
from datetime import datetime

logger = logging.getLogger(__name__)

class AreaContact:
    def __init__(self, name: str, email: str, phone: str):
        self.name = name
        self.email = email
        self.phone = phone

class CompanyArea:
    def __init__(self, area_id: str, area_name: str, keywords: List[str], 
                 contact: Dict[str, str], description: str):
        self.area_id = area_id
        self.area_name = area_name
        self.keywords = keywords
        self.contact = AreaContact(**contact)
        self.description = description

class FallbackConfig:
    def __init__(self, company_areas: List[Dict], default_contact: Dict[str, str], 
                 last_updated: str):
        self.areas = [CompanyArea(**area) for area in company_areas]
        self.default_contact = AreaContact(**default_contact)
        self.last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))

class FallbackHandler:
    def __init__(self, connection_string: str, container_name: str, blob_name: str):
        """
        Initialize the FallbackHandler with storage configuration.
        
        Args:
            connection_string: Azure Storage connection string for the fallback system
            container_name: Name of the container storing the fallback configuration
            blob_name: Name of the blob containing the fallback configuration
        """
        logger.debug(f"Initializing FallbackHandler with container: {container_name}, blob: {blob_name}")
        
        if not connection_string:
            logger.error("Storage connection string is required for fallback system")
            raise ValueError("Storage connection string is required for fallback system")
            
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_name = blob_name
        self._config: Optional[FallbackConfig] = None

    def _load_config(self) -> FallbackConfig:
        """Load the fallback configuration from Azure Blob Storage."""
        try:
            logger.debug(f"Loading fallback configuration from {self.container_name}/{self.blob_name}")
            blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            container_client = blob_service_client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(self.blob_name)
            
            config_data = json.loads(blob_client.download_blob().readall())
            logger.debug(f"Successfully loaded configuration with {len(config_data.get('company_areas', []))} areas")
            return FallbackConfig(**config_data)
        except Exception as e:
            logger.error(f"Error loading fallback configuration: {str(e)}")
            raise

    def get_config(self) -> FallbackConfig:
        """Get the current configuration, loading it if necessary."""
        if self._config is None:
            logger.debug("Configuration not loaded, loading now")
            self._config = self._load_config()
        return self._config

    def classify_query(self, query: str) -> Optional[CompanyArea]:
        """
        Classify the user query into a company area based on keywords and context.
        Returns the most relevant area or None if no match is found.
        """
        logger.debug(f"Classifying query: {query}")
        config = self.get_config()
        query_lower = query.lower()
        
        # Score each area based on keyword matches
        area_scores = []
        for area in config.areas:
            score = sum(1 for keyword in area.keywords if keyword.lower() in query_lower)
            if score > 0:
                area_scores.append((area, score))
                logger.debug(f"Area {area.area_name} matched with score {score}")
                logger.debug(f"Matched keywords: {[k for k in area.keywords if k.lower() in query_lower]}")
        
        # Return the area with the highest score, or None if no matches
        if area_scores:
            best_match = max(area_scores, key=lambda x: x[1])[0]
            logger.debug(f"Best matching area: {best_match.area_name}")
            return best_match
        logger.debug("No matching area found")
        return None

    def get_fallback_response(self, query: str) -> Dict[str, str]:
        """
        Generate a fallback response based on the query classification.
        Returns a dictionary with the response message and contact information.
        """
        logger.debug(f"Generating fallback response for query: {query}")
        area = self.classify_query(query)
        
        if area:
            logger.debug(f"Using area-specific contact for {area.area_name}")
            return {
                "message": f"Para consultas relacionadas con {area.area_name}, por favor contacte a:",
                "contact_name": area.contact.name,
                "contact_email": area.contact.email,
                "contact_phone": area.contact.phone,
                "area_description": area.description
            }
        else:
            logger.debug("Using default contact information")
            return {
                "message": "Para asistencia general, por favor contacte a:",
                "contact_name": self.get_config().default_contact.name,
                "contact_email": self.get_config().default_contact.email,
                "contact_phone": self.get_config().default_contact.phone,
                "area_description": "Administración General"
            } 