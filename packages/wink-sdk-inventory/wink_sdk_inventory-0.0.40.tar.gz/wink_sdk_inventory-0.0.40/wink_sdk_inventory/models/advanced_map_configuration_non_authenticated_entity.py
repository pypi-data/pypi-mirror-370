# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/engine-client): A single endpoint to retrieve whitelabel + customization information for the booking engine.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reactive): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant reactive widget for all other entities.   - [TripPay](/reactive): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Inventory API The Inventory API exposes endpoints to retrieve inventory you already know about. This API lets you:  1. Consume shareable links. 2. Load up a known property with availability. 3. Load up all inventories that were created by our affiliates such as grids, maps, and individual items.  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.16.4
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from wink_sdk_inventory.models.configurable_geo_json_circle_non_authenticated_entity import ConfigurableGeoJsonCircleNonAuthenticatedEntity
from wink_sdk_inventory.models.configurable_geo_json_point_non_authenticated_entity import ConfigurableGeoJsonPointNonAuthenticatedEntity
from wink_sdk_inventory.models.configurable_geo_json_polygon_non_authenticated_entity import ConfigurableGeoJsonPolygonNonAuthenticatedEntity
from wink_sdk_inventory.models.configurable_geo_json_rectangle_non_authenticated_entity import ConfigurableGeoJsonRectangleNonAuthenticatedEntity
from wink_sdk_inventory.models.geo_json_point_non_authenticated_entity import GeoJsonPointNonAuthenticatedEntity
from typing import Optional, Set
from typing_extensions import Self

class AdvancedMapConfigurationNonAuthenticatedEntity(BaseModel):
    """
    Advanced map configuration
    """ # noqa: E501
    identifier: StrictStr = Field(description="Unique map identifier")
    owner_identifier: StrictStr = Field(description="Map owner identifier", alias="ownerIdentifier")
    engine_configuration_identifier: StrictStr = Field(description="Customization identifier", alias="engineConfigurationIdentifier")
    name: StrictStr = Field(description="Name of map")
    type_identifier: StrictStr = Field(description="Inventory type identifier. Either a single channel inventory identifier, a list identifier or a dynamic search identifier.", alias="typeIdentifier")
    type: StrictStr = Field(description="Type of blocking")
    center: GeoJsonPointNonAuthenticatedEntity
    draggable: StrictBool = Field(description="User can move around / pan the map")
    zoomable: StrictBool = Field(description="User can zoom in/out of the map")
    initial_zoom_level: Annotated[int, Field(le=21, strict=True, ge=0)] = Field(description="Valid Google maps zoom level", alias="initialZoomLevel")
    map_style: StrictStr = Field(description="Map style", alias="mapStyle")
    map_marker_color: StrictStr = Field(description="Map marker color", alias="mapMarkerColor")
    map_height: Annotated[int, Field(strict=True, ge=1)] = Field(description="Map height in pixels", alias="mapHeight")
    display_type: StrictStr = Field(description="Indicate which initial values to display first on the front-facing card", alias="displayType")
    circles: Optional[List[ConfigurableGeoJsonCircleNonAuthenticatedEntity]] = None
    rectangles: Optional[List[ConfigurableGeoJsonRectangleNonAuthenticatedEntity]] = None
    markers: Optional[List[ConfigurableGeoJsonPointNonAuthenticatedEntity]] = None
    polygons: Optional[List[ConfigurableGeoJsonPolygonNonAuthenticatedEntity]] = None
    __properties: ClassVar[List[str]] = ["identifier", "ownerIdentifier", "engineConfigurationIdentifier", "name", "typeIdentifier", "type", "center", "draggable", "zoomable", "initialZoomLevel", "mapStyle", "mapMarkerColor", "mapHeight", "displayType", "circles", "rectangles", "markers", "polygons"]

    @field_validator('type')
    def type_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['SINGLE', 'LIST', 'SEARCH']):
            raise ValueError("must be one of enum values ('SINGLE', 'LIST', 'SEARCH')")
        return value

    @field_validator('map_style')
    def map_style_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['normal', 'clean', 'bluish']):
            raise ValueError("must be one of enum values ('normal', 'clean', 'bluish')")
        return value

    @field_validator('map_marker_color')
    def map_marker_color_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['cc2138']):
            raise ValueError("must be one of enum values ('cc2138')")
        return value

    @field_validator('display_type')
    def display_type_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['NATIVE', 'HOTEL', 'ROOM']):
            raise ValueError("must be one of enum values ('NATIVE', 'HOTEL', 'ROOM')")
        return value

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of AdvancedMapConfigurationNonAuthenticatedEntity from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of center
        if self.center:
            _dict['center'] = self.center.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in circles (list)
        _items = []
        if self.circles:
            for _item_circles in self.circles:
                if _item_circles:
                    _items.append(_item_circles.to_dict())
            _dict['circles'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in rectangles (list)
        _items = []
        if self.rectangles:
            for _item_rectangles in self.rectangles:
                if _item_rectangles:
                    _items.append(_item_rectangles.to_dict())
            _dict['rectangles'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in markers (list)
        _items = []
        if self.markers:
            for _item_markers in self.markers:
                if _item_markers:
                    _items.append(_item_markers.to_dict())
            _dict['markers'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in polygons (list)
        _items = []
        if self.polygons:
            for _item_polygons in self.polygons:
                if _item_polygons:
                    _items.append(_item_polygons.to_dict())
            _dict['polygons'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of AdvancedMapConfigurationNonAuthenticatedEntity from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "identifier": obj.get("identifier"),
            "ownerIdentifier": obj.get("ownerIdentifier"),
            "engineConfigurationIdentifier": obj.get("engineConfigurationIdentifier"),
            "name": obj.get("name"),
            "typeIdentifier": obj.get("typeIdentifier"),
            "type": obj.get("type"),
            "center": GeoJsonPointNonAuthenticatedEntity.from_dict(obj["center"]) if obj.get("center") is not None else None,
            "draggable": obj.get("draggable") if obj.get("draggable") is not None else True,
            "zoomable": obj.get("zoomable") if obj.get("zoomable") is not None else True,
            "initialZoomLevel": obj.get("initialZoomLevel"),
            "mapStyle": obj.get("mapStyle"),
            "mapMarkerColor": obj.get("mapMarkerColor"),
            "mapHeight": obj.get("mapHeight"),
            "displayType": obj.get("displayType") if obj.get("displayType") is not None else 'NATIVE',
            "circles": [ConfigurableGeoJsonCircleNonAuthenticatedEntity.from_dict(_item) for _item in obj["circles"]] if obj.get("circles") is not None else None,
            "rectangles": [ConfigurableGeoJsonRectangleNonAuthenticatedEntity.from_dict(_item) for _item in obj["rectangles"]] if obj.get("rectangles") is not None else None,
            "markers": [ConfigurableGeoJsonPointNonAuthenticatedEntity.from_dict(_item) for _item in obj["markers"]] if obj.get("markers") is not None else None,
            "polygons": [ConfigurableGeoJsonPolygonNonAuthenticatedEntity.from_dict(_item) for _item in obj["polygons"]] if obj.get("polygons") is not None else None
        })
        return _obj


