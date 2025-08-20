import os
import httpx
from typing import List, Optional, Dict, Any
import logging
from dotenv import load_dotenv
from listings_db_contracts import (
    Listing as ListingContract, 
    ListingCreate as CreateListingContract,
    EstateAgent as EstateAgentContract,
    EstateAgentCreate, 
    Location as LocationContract,
    Image as ImageContract,
    ImageCreate,
    Address as AddressContract,
    ClientType,
    PropertyType,
    TenancyType,
    Floorplan as FloorplanContract,
    FloorplanCreate,
)


# Load environment variables from a .env file if present
load_dotenv()

logger = logging.getLogger(__name__)

class ListingsDBAPIClient:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, timeout: Optional[int] = 30):
        # Prefer environment variables
        env_base_url = os.getenv("LISTINGS_DB_BASE_URL", "http://localhost:8000")
        # Ensure API base includes /api suffix for API endpoints
        self.base_url = (base_url or env_base_url).rstrip("/") + "/api"
        self.health_base_url = (base_url or env_base_url).rstrip("/")

        self.api_key = api_key or os.getenv("LISTINGS_DB_API_KEY")
        self.client = httpx.Client(timeout=timeout)

    def _auth_headers(self, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def _request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}{endpoint}"
        # Merge/attach auth headers
        headers = kwargs.pop("headers", {}) or {}
        headers = self._auth_headers(headers)
        try:
            response = self.client.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                message = error_data.get("detail", e.response.text)
            except ValueError:
                message = e.response.text
            raise Exception(f"API request failed with status {e.response.status_code}: {message}") from e
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}") from e

    # --- Listings Endpoints ---
    def get_listings(self, skip: int = 0, limit: int = 10) -> List[ListingContract]:
        """Retrieves a paginated list of listings."""
        response_data = self._request("GET", f"/listings/?skip={skip}&limit={limit}")
        return [ListingContract.model_validate(item) for item in response_data]

    def get_all_listings(self) -> List[ListingContract]:
        """Retrieves all listings by paginating through the get_listings endpoint."""
        all_listings = []
        skip = 0
        limit = 100
        while True:
            response = self.get_listings(skip=skip, limit=limit)
            if not response:
                break
            all_listings.extend(response)
            skip += limit
        return all_listings

    def get_listing(self, listing_id: int) -> ListingContract:
        """Retrieves a single listing by its ID."""
        response_data = self._request("GET", f"/listings/{listing_id}")
        return ListingContract.model_validate(response_data)

    def create_listing(self, listing: CreateListingContract) -> ListingContract:
        listing_json = listing.model_dump_json(exclude_none=True)
        response = self._request("POST", "/listings/", content=listing_json, headers={"Content-Type": "application/json"})
        return ListingContract.model_validate(response)

    def create_listing_raw(self, listing_data: dict) -> httpx.Response:
        """Creates a listing by sending raw data, returning the full response."""
        headers = self._auth_headers({"Content-Type": "application/json"})
        return self.client.post(f"{self.base_url}/listings/", json=listing_data, headers=headers)

    def update_listing(self, listing_id: int, listing: dict) -> ListingContract:
        headers = self._auth_headers({"Content-Type": "application/json"})
        response = self.client.put(f"{self.base_url}/listings/{listing_id}", json=listing, headers=headers)
        response.raise_for_status()
        return ListingContract.model_validate(response.json())

    def delete_listing(self, listing_id: int) -> ListingContract:
        response_data = self._request("DELETE", f"/listings/{listing_id}")
        return ListingContract.model_validate(response_data)

    def find_listing_by_agent_reference(self, agent_reference: str, estate_agent_id: int) -> ListingContract:
        """Finds a listing by agent reference and estate agent ID."""
        response_data = self._request("GET", f"/listings/find/{estate_agent_id}/{agent_reference}")
        return ListingContract.model_validate(response_data)

    def validate_listing_exists(self, listing_id: int) -> dict:
        """Validates if a listing exists."""
        return self._request("GET", f"/listings/{listing_id}/validate")
    
    def add_image_to_listing(self, listing_id: int, image: ImageCreate) -> ImageContract:
        """Adds a single image to a listing."""
        image_json = image.model_dump_json(exclude_none=True)
        response_data = self._request("POST", f"/listings/{listing_id}/images/", content=image_json, headers={"Content-Type": "application/json"})
        return ImageContract.model_validate(response_data)

    def add_images_to_listing(self, listing_id: int, images: List[ImageCreate]) -> List[ImageContract]:
        """Adds multiple images to a listing."""
        images_json = [img.model_dump(exclude_none=True) for img in images]
        response_data = self._request("POST", f"/listings/{listing_id}/images/bulk", json=images_json)
        return [ImageContract.model_validate(item) for item in response_data]
    
    def add_floorplan_to_listing(self, listing_id: int, floorplan: FloorplanCreate) -> FloorplanContract:
        """Adds a single floorplan to a listing."""
        floorplan_json = floorplan.model_dump_json(exclude_none=True)
        response_data = self._request("POST", f"/listings/{listing_id}/floorplans/", content=floorplan_json, headers={"Content-Type": "application/json"})
        return FloorplanContract.model_validate(response_data)

    def add_floorplans_to_listing(self, listing_id: int, floorplans: List[FloorplanCreate]) -> List[FloorplanContract]:
        """Adds multiple floorplans to a listing."""
        floorplans_json = [fp.model_dump(exclude_none=True) for fp in floorplans]
        response_data = self._request("POST", f"/listings/{listing_id}/floorplans/bulk", json=floorplans_json)
        return [FloorplanContract.model_validate(item) for item in response_data]

    # --- Image Endpoints ---
    def get_images_for_listing(self, listing_id: int) -> List[ImageContract]:
        """Gets all images associated with a specific listing."""
        response_data = self._request("GET", f"/listings/{listing_id}/images/")
        return [ImageContract.model_validate(item) for item in response_data]

    def get_image(self, image_id: int) -> ImageContract:
        """Gets a single image by its ID."""
        response_data = self._request("GET", f"/images/{image_id}")
        return ImageContract.model_validate(response_data)

    def create_image(self, image: ImageCreate) -> ImageContract:
        """Creates a new image."""
        image_json = image.model_dump_json(exclude_none=True)
        response_data = self._request("POST", "/images/", content=image_json, headers={"Content-Type": "application/json"})
        return ImageContract.model_validate(response_data)

    # --- Floorplan Endpoints ---
    def get_floorplans_for_listing(self, listing_id: int) -> List[FloorplanContract]:
        """Gets all floorplans associated with a specific listing."""
        response_data = self._request("GET", f"/listings/{listing_id}/floorplans/")
        return [FloorplanContract.model_validate(item) for item in response_data]
    
    def get_floorplan(self, floorplan_id: int) -> FloorplanContract:
        """Gets a single floorplan by its ID."""
        response_data = self._request("GET", f"/floorplans/{floorplan_id}")
        return FloorplanContract.model_validate(response_data)
    
    def create_floorplan(self, floorplan: FloorplanCreate) -> FloorplanContract:
        """Creates a new floorplan."""
        floorplan_json = floorplan.model_dump_json(exclude_none=True)
        response_data = self._request("POST", "/floorplans/", content=floorplan_json, headers={"Content-Type": "application/json"})
        return FloorplanContract.model_validate(response_data)

    # --- Estate Agents Endpoints ---
    def get_estate_agents(self, skip: int = 0, limit: int = 100) -> List[EstateAgentContract]:
        agents_data = self._request("GET", f"/estate_agents/?skip={skip}&limit={limit}")
        return [EstateAgentContract.model_validate(agent_data) for agent_data in agents_data]

    def get_estate_agent(self, estate_agent_id: int) -> EstateAgentContract:
        response_data = self._request("GET", f"/estate_agents/{estate_agent_id}")
        return EstateAgentContract.model_validate(response_data)

    def create_estate_agent(self, estate_agent: EstateAgentCreate) -> EstateAgentContract:
        agent_json = estate_agent.model_dump_json(exclude_none=True)
        response_data = self._request("POST", "/estate_agents/", content=agent_json, headers={"Content-Type": "application/json"})
        return EstateAgentContract.model_validate(response_data)

    def update_estate_agent(self, estate_agent_id: int, estate_agent: dict) -> EstateAgentContract:
        headers = self._auth_headers({"Content-Type": "application/json"})
        response = self.client.put(f"{self.base_url}/estate_agents/{estate_agent_id}", json=estate_agent, headers=headers)
        response.raise_for_status()
        return EstateAgentContract.model_validate(response.json())

    def delete_estate_agent(self, estate_agent_id: int) -> EstateAgentContract:
        response_data = self._request("DELETE", f"/estate_agents/{estate_agent_id}")
        return EstateAgentContract.model_validate(response_data)

    def close(self):
        self.client.close()

    # --- Health Check ---
    def health_check(self) -> dict:
        """Performs a health check on the API (no auth)."""
        url = f"{self.health_base_url}/health"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json() 