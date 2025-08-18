# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reactive): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant reactive widget for all other entities.   - [TripPay](/reactive): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Inventory API The Inventory API exposes endpoints to retrieve inventory you already know about. This API lets you:  1. Consume shareable links. 2. Load up a known property with availability. 3. Load up all inventories that were created by our affiliates such as grids, maps, and individual items.  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.17.14
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
from wink_sdk_inventory.models.itinerary_non_authenticated_entity import ItineraryNonAuthenticatedEntity
from wink_sdk_inventory.models.seller_media_non_authenticated_entity import SellerMediaNonAuthenticatedEntity
from wink_sdk_inventory.models.seller_url_price_non_authenticated_entity import SellerUrlPriceNonAuthenticatedEntity
from typing import Optional, Set
from typing_extensions import Self

class ConsumableSellerUrlNonAuthenticatedEntity(BaseModel):
    """
    ConsumableSellerUrlNonAuthenticatedEntity
    """ # noqa: E501
    language: Optional[StrictStr] = Field(default='en', description="Which language the seller wanted to use")
    currency: Optional[StrictStr] = Field(default='USD', description="Which currency the seller is using")
    title: Optional[StrictStr] = Field(default=None, description="Link title")
    description: Optional[StrictStr] = Field(default=None, description="Link description")
    keywords: Optional[StrictStr] = Field(default=None, description="Comma-separated keyword values that can be used to populate HTML metadata")
    unique_id: Optional[StrictStr] = Field(default=None, description="The URL ID that uniquely represents this link", alias="uniqueId")
    twitter_account: Optional[StrictStr] = Field(default=None, description="Optional X account ID", alias="twitterAccount")
    facebook_app_id: Optional[StrictStr] = Field(default=None, description="Optional Facebook app ID", alias="facebookAppId")
    image: Optional[SellerMediaNonAuthenticatedEntity] = Field(default=None, description="The image you want to accompany this link")
    video: Optional[SellerMediaNonAuthenticatedEntity] = Field(default=None, description="The video you want to accompany this link")
    transact_url: Optional[StrictStr] = Field(default=None, description="The transation url, or where to redirect to when clicking the CTA button.", alias="transactUrl")
    supplier_identifier: Optional[StrictStr] = Field(default=None, description="The owner ID of the inventory you want to sell", alias="supplierIdentifier")
    supplier_name: Optional[StrictStr] = Field(default=None, description="The owner name of the inventory you want to sell", alias="supplierName")
    supplier_url_name: Optional[StrictStr] = Field(default=None, description="The owner url name of the inventory you want to sell", alias="supplierUrlName")
    supplier_brand: Optional[StrictStr] = Field(default=None, description="In case the property is part of a brand", alias="supplierBrand")
    available: Optional[StrictBool] = Field(default=None, description="Whether inventory is available for sale")
    price: Optional[SellerUrlPriceNonAuthenticatedEntity] = None
    city_name: Optional[StrictStr] = Field(default=None, description="City where inventory is located", alias="cityName")
    country_name: Optional[StrictStr] = Field(default=None, description="Country where inventory is located", alias="countryName")
    inventory_type: Optional[StrictStr] = Field(default=None, description="Type of inventory", alias="inventoryType")
    itinerary: ItineraryNonAuthenticatedEntity = Field(description="Dates and travel info.")
    __properties: ClassVar[List[str]] = ["language", "currency", "title", "description", "keywords", "uniqueId", "twitterAccount", "facebookAppId", "image", "video", "transactUrl", "supplierIdentifier", "supplierName", "supplierUrlName", "supplierBrand", "available", "price", "cityName", "countryName", "inventoryType", "itinerary"]

    @field_validator('inventory_type')
    def inventory_type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['HOTEL', 'GUEST_ROOM', 'MEETING_ROOM', 'RESTAURANT', 'SPA', 'ADD_ON', 'ATTRACTION', 'ACTIVITY', 'PLACE']):
            raise ValueError("must be one of enum values ('HOTEL', 'GUEST_ROOM', 'MEETING_ROOM', 'RESTAURANT', 'SPA', 'ADD_ON', 'ATTRACTION', 'ACTIVITY', 'PLACE')")
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
        """Create an instance of ConsumableSellerUrlNonAuthenticatedEntity from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of image
        if self.image:
            _dict['image'] = self.image.to_dict()
        # override the default output from pydantic by calling `to_dict()` of video
        if self.video:
            _dict['video'] = self.video.to_dict()
        # override the default output from pydantic by calling `to_dict()` of price
        if self.price:
            _dict['price'] = self.price.to_dict()
        # override the default output from pydantic by calling `to_dict()` of itinerary
        if self.itinerary:
            _dict['itinerary'] = self.itinerary.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ConsumableSellerUrlNonAuthenticatedEntity from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "language": obj.get("language") if obj.get("language") is not None else 'en',
            "currency": obj.get("currency") if obj.get("currency") is not None else 'USD',
            "title": obj.get("title"),
            "description": obj.get("description"),
            "keywords": obj.get("keywords"),
            "uniqueId": obj.get("uniqueId"),
            "twitterAccount": obj.get("twitterAccount"),
            "facebookAppId": obj.get("facebookAppId"),
            "image": SellerMediaNonAuthenticatedEntity.from_dict(obj["image"]) if obj.get("image") is not None else None,
            "video": SellerMediaNonAuthenticatedEntity.from_dict(obj["video"]) if obj.get("video") is not None else None,
            "transactUrl": obj.get("transactUrl"),
            "supplierIdentifier": obj.get("supplierIdentifier"),
            "supplierName": obj.get("supplierName"),
            "supplierUrlName": obj.get("supplierUrlName"),
            "supplierBrand": obj.get("supplierBrand"),
            "available": obj.get("available"),
            "price": SellerUrlPriceNonAuthenticatedEntity.from_dict(obj["price"]) if obj.get("price") is not None else None,
            "cityName": obj.get("cityName"),
            "countryName": obj.get("countryName"),
            "inventoryType": obj.get("inventoryType"),
            "itinerary": ItineraryNonAuthenticatedEntity.from_dict(obj["itinerary"]) if obj.get("itinerary") is not None else None
        })
        return _obj


