# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Inventory API The Inventory API exposes endpoints to retrieve inventory you already know about. This API lets you:  1. Consume shareable links. 2. Load up a known property with availability. 3. Load up all inventories that were created by our affiliates such as grids, maps, and individual items.  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.18.5
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from wink_sdk_inventory.models.activity_localized_inventory_non_authenticated_entity import ActivityLocalizedInventoryNonAuthenticatedEntity
from wink_sdk_inventory.models.aggregate_greendex_answers_non_authenticated_entity import AggregateGreendexAnswersNonAuthenticatedEntity
from wink_sdk_inventory.models.announcement_lightweight_non_authenticated_entity import AnnouncementLightweightNonAuthenticatedEntity
from wink_sdk_inventory.models.attraction_localized_inventory_non_authenticated_entity import AttractionLocalizedInventoryNonAuthenticatedEntity
from wink_sdk_inventory.models.meeting_room_localized_inventory_non_authenticated_entity import MeetingRoomLocalizedInventoryNonAuthenticatedEntity
from wink_sdk_inventory.models.meta_data_non_authenticated_entity import MetaDataNonAuthenticatedEntity
from wink_sdk_inventory.models.place_localized_inventory_non_authenticated_entity import PlaceLocalizedInventoryNonAuthenticatedEntity
from wink_sdk_inventory.models.property_aggregate_lightweight_non_authenticated_entity import PropertyAggregateLightweightNonAuthenticatedEntity
from wink_sdk_inventory.models.restaurant_localized_inventory_non_authenticated_entity import RestaurantLocalizedInventoryNonAuthenticatedEntity
from wink_sdk_inventory.models.room_type_with_price_configuration_non_authenticated_entity import RoomTypeWithPriceConfigurationNonAuthenticatedEntity
from wink_sdk_inventory.models.room_type_with_price_configurations_non_authenticated_entity import RoomTypeWithPriceConfigurationsNonAuthenticatedEntity
from wink_sdk_inventory.models.sales_channel_info_non_authenticated_entity import SalesChannelInfoNonAuthenticatedEntity
from wink_sdk_inventory.models.simple_multimedia_non_authenticated_entity import SimpleMultimediaNonAuthenticatedEntity
from wink_sdk_inventory.models.spa_localized_inventory_non_authenticated_entity import SpaLocalizedInventoryNonAuthenticatedEntity
from wink_sdk_inventory.models.travel_inventory_recognition_non_authenticated_entity import TravelInventoryRecognitionNonAuthenticatedEntity
from wink_sdk_inventory.models.user_review_non_authenticated_entity import UserReviewNonAuthenticatedEntity
from typing import Optional, Set
from typing_extensions import Self

class HotelInventoryResponseNonAuthenticatedEntity(BaseModel):
    """
    HotelInventoryResponseNonAuthenticatedEntity
    """ # noqa: E501
    hotel_identifier: Optional[StrictStr] = Field(default=None, description="Unique property identifier to retrieve inventory for.", alias="hotelIdentifier")
    url_name: Optional[StrictStr] = Field(default=None, description="Unique url-friendly record identifier of property.", alias="urlName")
    hotel: Optional[PropertyAggregateLightweightNonAuthenticatedEntity] = Field(default=None, description="Property details")
    green_index_scores: Optional[AggregateGreendexAnswersNonAuthenticatedEntity] = Field(default=None, description="Detailed Green Index scores on hoe the property scores by category", alias="greenIndexScores")
    room_types: Optional[List[RoomTypeWithPriceConfigurationsNonAuthenticatedEntity]] = Field(default=None, description="List of room types with price configurations based on the itinerary that was passed on the user session.", alias="roomTypes")
    meeting_rooms: Optional[List[MeetingRoomLocalizedInventoryNonAuthenticatedEntity]] = Field(default=None, description="List of property meeting rooms on and off the premises.", alias="meetingRooms")
    restaurants: Optional[List[RestaurantLocalizedInventoryNonAuthenticatedEntity]] = Field(default=None, description="List of property restaurants on and off the premises.")
    spas: Optional[List[SpaLocalizedInventoryNonAuthenticatedEntity]] = Field(default=None, description="List of property spas on and off the premises.")
    activities: Optional[List[ActivityLocalizedInventoryNonAuthenticatedEntity]] = Field(default=None, description="List of property activities on and off the premises.")
    attractions: Optional[List[AttractionLocalizedInventoryNonAuthenticatedEntity]] = Field(default=None, description="List of property attractions on and off the premises.")
    places: Optional[List[PlaceLocalizedInventoryNonAuthenticatedEntity]] = Field(default=None, description="List of property places on and off the premises.")
    metadata: Optional[List[MetaDataNonAuthenticatedEntity]] = Field(default=None, description="List of property meta data.")
    images: Optional[List[SimpleMultimediaNonAuthenticatedEntity]] = Field(default=None, description="List of property images")
    videos: Optional[List[SimpleMultimediaNonAuthenticatedEntity]] = Field(default=None, description="List of property videos")
    recognitions: Optional[List[TravelInventoryRecognitionNonAuthenticatedEntity]] = Field(default=None, description="List of property recognitions")
    announcements: Optional[List[AnnouncementLightweightNonAuthenticatedEntity]] = Field(default=None, description="List of property announcements")
    reviews: Optional[List[UserReviewNonAuthenticatedEntity]] = Field(default=None, description="List of property reviews")
    sales_channel: Optional[SalesChannelInfoNonAuthenticatedEntity] = Field(default=None, description="Sales channel that owns this booking", alias="salesChannel")
    cheapest_room_types: Optional[List[RoomTypeWithPriceConfigurationNonAuthenticatedEntity]] = Field(default=None, description="Uses the content from roomTypes and displays the lowest price for each room type that is available.", alias="cheapestRoomTypes")
    available: Optional[StrictBool] = None
    lowest_price: Optional[RoomTypeWithPriceConfigurationNonAuthenticatedEntity] = Field(default=None, description="Uses the content from roomTypes and shows the room type with the lowest price.", alias="lowestPrice")
    __properties: ClassVar[List[str]] = ["hotelIdentifier", "urlName", "hotel", "greenIndexScores", "roomTypes", "meetingRooms", "restaurants", "spas", "activities", "attractions", "places", "metadata", "images", "videos", "recognitions", "announcements", "reviews", "salesChannel", "cheapestRoomTypes", "available", "lowestPrice"]

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
        """Create an instance of HotelInventoryResponseNonAuthenticatedEntity from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of hotel
        if self.hotel:
            _dict['hotel'] = self.hotel.to_dict()
        # override the default output from pydantic by calling `to_dict()` of green_index_scores
        if self.green_index_scores:
            _dict['greenIndexScores'] = self.green_index_scores.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in room_types (list)
        _items = []
        if self.room_types:
            for _item_room_types in self.room_types:
                if _item_room_types:
                    _items.append(_item_room_types.to_dict())
            _dict['roomTypes'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in meeting_rooms (list)
        _items = []
        if self.meeting_rooms:
            for _item_meeting_rooms in self.meeting_rooms:
                if _item_meeting_rooms:
                    _items.append(_item_meeting_rooms.to_dict())
            _dict['meetingRooms'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in restaurants (list)
        _items = []
        if self.restaurants:
            for _item_restaurants in self.restaurants:
                if _item_restaurants:
                    _items.append(_item_restaurants.to_dict())
            _dict['restaurants'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in spas (list)
        _items = []
        if self.spas:
            for _item_spas in self.spas:
                if _item_spas:
                    _items.append(_item_spas.to_dict())
            _dict['spas'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in activities (list)
        _items = []
        if self.activities:
            for _item_activities in self.activities:
                if _item_activities:
                    _items.append(_item_activities.to_dict())
            _dict['activities'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in attractions (list)
        _items = []
        if self.attractions:
            for _item_attractions in self.attractions:
                if _item_attractions:
                    _items.append(_item_attractions.to_dict())
            _dict['attractions'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in places (list)
        _items = []
        if self.places:
            for _item_places in self.places:
                if _item_places:
                    _items.append(_item_places.to_dict())
            _dict['places'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in metadata (list)
        _items = []
        if self.metadata:
            for _item_metadata in self.metadata:
                if _item_metadata:
                    _items.append(_item_metadata.to_dict())
            _dict['metadata'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in images (list)
        _items = []
        if self.images:
            for _item_images in self.images:
                if _item_images:
                    _items.append(_item_images.to_dict())
            _dict['images'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in videos (list)
        _items = []
        if self.videos:
            for _item_videos in self.videos:
                if _item_videos:
                    _items.append(_item_videos.to_dict())
            _dict['videos'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in recognitions (list)
        _items = []
        if self.recognitions:
            for _item_recognitions in self.recognitions:
                if _item_recognitions:
                    _items.append(_item_recognitions.to_dict())
            _dict['recognitions'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in announcements (list)
        _items = []
        if self.announcements:
            for _item_announcements in self.announcements:
                if _item_announcements:
                    _items.append(_item_announcements.to_dict())
            _dict['announcements'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in reviews (list)
        _items = []
        if self.reviews:
            for _item_reviews in self.reviews:
                if _item_reviews:
                    _items.append(_item_reviews.to_dict())
            _dict['reviews'] = _items
        # override the default output from pydantic by calling `to_dict()` of sales_channel
        if self.sales_channel:
            _dict['salesChannel'] = self.sales_channel.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in cheapest_room_types (list)
        _items = []
        if self.cheapest_room_types:
            for _item_cheapest_room_types in self.cheapest_room_types:
                if _item_cheapest_room_types:
                    _items.append(_item_cheapest_room_types.to_dict())
            _dict['cheapestRoomTypes'] = _items
        # override the default output from pydantic by calling `to_dict()` of lowest_price
        if self.lowest_price:
            _dict['lowestPrice'] = self.lowest_price.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of HotelInventoryResponseNonAuthenticatedEntity from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "hotelIdentifier": obj.get("hotelIdentifier"),
            "urlName": obj.get("urlName"),
            "hotel": PropertyAggregateLightweightNonAuthenticatedEntity.from_dict(obj["hotel"]) if obj.get("hotel") is not None else None,
            "greenIndexScores": AggregateGreendexAnswersNonAuthenticatedEntity.from_dict(obj["greenIndexScores"]) if obj.get("greenIndexScores") is not None else None,
            "roomTypes": [RoomTypeWithPriceConfigurationsNonAuthenticatedEntity.from_dict(_item) for _item in obj["roomTypes"]] if obj.get("roomTypes") is not None else None,
            "meetingRooms": [MeetingRoomLocalizedInventoryNonAuthenticatedEntity.from_dict(_item) for _item in obj["meetingRooms"]] if obj.get("meetingRooms") is not None else None,
            "restaurants": [RestaurantLocalizedInventoryNonAuthenticatedEntity.from_dict(_item) for _item in obj["restaurants"]] if obj.get("restaurants") is not None else None,
            "spas": [SpaLocalizedInventoryNonAuthenticatedEntity.from_dict(_item) for _item in obj["spas"]] if obj.get("spas") is not None else None,
            "activities": [ActivityLocalizedInventoryNonAuthenticatedEntity.from_dict(_item) for _item in obj["activities"]] if obj.get("activities") is not None else None,
            "attractions": [AttractionLocalizedInventoryNonAuthenticatedEntity.from_dict(_item) for _item in obj["attractions"]] if obj.get("attractions") is not None else None,
            "places": [PlaceLocalizedInventoryNonAuthenticatedEntity.from_dict(_item) for _item in obj["places"]] if obj.get("places") is not None else None,
            "metadata": [MetaDataNonAuthenticatedEntity.from_dict(_item) for _item in obj["metadata"]] if obj.get("metadata") is not None else None,
            "images": [SimpleMultimediaNonAuthenticatedEntity.from_dict(_item) for _item in obj["images"]] if obj.get("images") is not None else None,
            "videos": [SimpleMultimediaNonAuthenticatedEntity.from_dict(_item) for _item in obj["videos"]] if obj.get("videos") is not None else None,
            "recognitions": [TravelInventoryRecognitionNonAuthenticatedEntity.from_dict(_item) for _item in obj["recognitions"]] if obj.get("recognitions") is not None else None,
            "announcements": [AnnouncementLightweightNonAuthenticatedEntity.from_dict(_item) for _item in obj["announcements"]] if obj.get("announcements") is not None else None,
            "reviews": [UserReviewNonAuthenticatedEntity.from_dict(_item) for _item in obj["reviews"]] if obj.get("reviews") is not None else None,
            "salesChannel": SalesChannelInfoNonAuthenticatedEntity.from_dict(obj["salesChannel"]) if obj.get("salesChannel") is not None else None,
            "cheapestRoomTypes": [RoomTypeWithPriceConfigurationNonAuthenticatedEntity.from_dict(_item) for _item in obj["cheapestRoomTypes"]] if obj.get("cheapestRoomTypes") is not None else None,
            "available": obj.get("available"),
            "lowestPrice": RoomTypeWithPriceConfigurationNonAuthenticatedEntity.from_dict(obj["lowestPrice"]) if obj.get("lowestPrice") is not None else None
        })
        return _obj


