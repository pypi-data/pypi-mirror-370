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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Union
from wink_sdk_inventory.models.custom_monetary_amount import CustomMonetaryAmount
from wink_sdk_inventory.models.localized_description_non_authenticated_entity import LocalizedDescriptionNonAuthenticatedEntity
from wink_sdk_inventory.models.quote_lightweight_non_authenticated_entity import QuoteLightweightNonAuthenticatedEntity
from typing import Optional, Set
from typing_extensions import Self

class StayRateNonAuthenticatedEntity(BaseModel):
    """
    StayRateNonAuthenticatedEntity
    """ # noqa: E501
    user_specified_currency_base_total: Optional[CustomMonetaryAmount] = Field(default=None, description="Base total in user specified currency.", alias="userSpecifiedCurrencyBaseTotal")
    source_base_total: Optional[CustomMonetaryAmount] = Field(default=None, description="Base total in hotel's currency.", alias="sourceBaseTotal")
    internal_base_total: Optional[CustomMonetaryAmount] = Field(default=None, description="Base total in wink currency.", alias="internalBaseTotal")
    source_extra_pax_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Extra person modifier in hotel currency.", alias="sourceExtraPaxModifier")
    internal_extra_pax_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Extra person modifier in wink currency", alias="internalExtraPaxModifier")
    user_specified_currency_extra_pax_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Extra person modifier in user specified currency", alias="userSpecifiedCurrencyExtraPaxModifier")
    source_extra_child_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Extra child modifier in hotel currency", alias="sourceExtraChildModifier")
    internal_extra_child_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Extra child modifier in wink currency", alias="internalExtraChildModifier")
    user_specified_currency_extra_child_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Extra child modifier in user specified currcency", alias="userSpecifiedCurrencyExtraChildModifier")
    source_single_occupant_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Single occupant modifier in hotel currency", alias="sourceSingleOccupantModifier")
    internal_single_occupant_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Singe occupant modifier in wink currency", alias="internalSingleOccupantModifier")
    user_specified_currency_single_occupant_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Single occupant modifier in user specified currency", alias="userSpecifiedCurrencySingleOccupantModifier")
    source_promotional_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Rate discount modifiers in hotel currency", alias="sourcePromotionalModifier")
    internal_promotional_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Rate discount modifiers in wink currency", alias="internalPromotionalModifier")
    user_specified_currency_promotional_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Rate discount modifiers in user specified currency", alias="userSpecifiedCurrencyPromotionalModifier")
    source_premium_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Rate premiums modifiers in hotel currency", alias="sourcePremiumModifier")
    internal_premium_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Rate premiums modifiers in wink currency", alias="internalPremiumModifier")
    user_specified_currency_premium_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Rate premiums modifiers in user specified currency", alias="userSpecifiedCurrencyPremiumModifier")
    source_channel_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Channel / Membership modifier in hotel currency", alias="sourceChannelModifier")
    internal_channel_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Channel / Membership modifier in wink currency", alias="internalChannelModifier")
    user_specified_currency_channel_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Channel / Membership modifier in user specified currency", alias="userSpecifiedCurrencyChannelModifier")
    quantity: Optional[StrictInt] = Field(default=None, description="Quantity")
    min_occupancy: Optional[StrictInt] = Field(default=None, description="Minimum occupancy", alias="minOccupancy")
    max_occupancy: Optional[StrictInt] = Field(default=None, description="Maximum occupancy", alias="maxOccupancy")
    rate_source: Optional[StrictStr] = Field(default=None, description="Source", alias="rateSource")
    promotional_discount_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Promotional discount percent", alias="promotionalDiscountPercent")
    channel_discount_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Chanel discount percent", alias="channelDiscountPercent")
    premium_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Premium percent", alias="premiumPercent")
    available: Optional[StrictBool] = Field(default=None, description="Available")
    source_to_user_currency_quote: Optional[QuoteLightweightNonAuthenticatedEntity] = Field(default=None, description="Hotel to user currency exchange rate.", alias="sourceToUserCurrencyQuote")
    source_to_internal_currency_quote: Optional[QuoteLightweightNonAuthenticatedEntity] = Field(default=None, description="Hotel to wink currency exchange rate.", alias="sourceToInternalCurrencyQuote")
    offer_details: Optional[List[LocalizedDescriptionNonAuthenticatedEntity]] = Field(default=None, alias="offerDetails")
    promotional_codes: Optional[List[StrictStr]] = Field(default=None, alias="promotionalCodes")
    user_specified_currency_total: Optional[CustomMonetaryAmount] = Field(default=None, description="User-defined currency final price.", alias="userSpecifiedCurrencyTotal")
    source_total: Optional[CustomMonetaryAmount] = Field(default=None, description="Source currency final price.", alias="sourceTotal")
    internal_total: Optional[CustomMonetaryAmount] = Field(default=None, description="Internal currency final price.", alias="internalTotal")
    user_specified_currency_average_price_per_night: Optional[CustomMonetaryAmount] = Field(default=None, alias="userSpecifiedCurrencyAveragePricePerNight")
    internal_average_price_per_night: Optional[CustomMonetaryAmount] = Field(default=None, alias="internalAveragePricePerNight")
    source_average_price_per_night: Optional[CustomMonetaryAmount] = Field(default=None, alias="sourceAveragePricePerNight")
    total_discount_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="totalDiscountPercent")
    __properties: ClassVar[List[str]] = ["userSpecifiedCurrencyBaseTotal", "sourceBaseTotal", "internalBaseTotal", "sourceExtraPaxModifier", "internalExtraPaxModifier", "userSpecifiedCurrencyExtraPaxModifier", "sourceExtraChildModifier", "internalExtraChildModifier", "userSpecifiedCurrencyExtraChildModifier", "sourceSingleOccupantModifier", "internalSingleOccupantModifier", "userSpecifiedCurrencySingleOccupantModifier", "sourcePromotionalModifier", "internalPromotionalModifier", "userSpecifiedCurrencyPromotionalModifier", "sourcePremiumModifier", "internalPremiumModifier", "userSpecifiedCurrencyPremiumModifier", "sourceChannelModifier", "internalChannelModifier", "userSpecifiedCurrencyChannelModifier", "quantity", "minOccupancy", "maxOccupancy", "rateSource", "promotionalDiscountPercent", "channelDiscountPercent", "premiumPercent", "available", "sourceToUserCurrencyQuote", "sourceToInternalCurrencyQuote", "offerDetails", "promotionalCodes", "userSpecifiedCurrencyTotal", "sourceTotal", "internalTotal", "userSpecifiedCurrencyAveragePricePerNight", "internalAveragePricePerNight", "sourceAveragePricePerNight", "totalDiscountPercent"]

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
        """Create an instance of StayRateNonAuthenticatedEntity from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of user_specified_currency_base_total
        if self.user_specified_currency_base_total:
            _dict['userSpecifiedCurrencyBaseTotal'] = self.user_specified_currency_base_total.to_dict()
        # override the default output from pydantic by calling `to_dict()` of source_base_total
        if self.source_base_total:
            _dict['sourceBaseTotal'] = self.source_base_total.to_dict()
        # override the default output from pydantic by calling `to_dict()` of internal_base_total
        if self.internal_base_total:
            _dict['internalBaseTotal'] = self.internal_base_total.to_dict()
        # override the default output from pydantic by calling `to_dict()` of source_to_user_currency_quote
        if self.source_to_user_currency_quote:
            _dict['sourceToUserCurrencyQuote'] = self.source_to_user_currency_quote.to_dict()
        # override the default output from pydantic by calling `to_dict()` of source_to_internal_currency_quote
        if self.source_to_internal_currency_quote:
            _dict['sourceToInternalCurrencyQuote'] = self.source_to_internal_currency_quote.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in offer_details (list)
        _items = []
        if self.offer_details:
            for _item_offer_details in self.offer_details:
                if _item_offer_details:
                    _items.append(_item_offer_details.to_dict())
            _dict['offerDetails'] = _items
        # override the default output from pydantic by calling `to_dict()` of user_specified_currency_total
        if self.user_specified_currency_total:
            _dict['userSpecifiedCurrencyTotal'] = self.user_specified_currency_total.to_dict()
        # override the default output from pydantic by calling `to_dict()` of source_total
        if self.source_total:
            _dict['sourceTotal'] = self.source_total.to_dict()
        # override the default output from pydantic by calling `to_dict()` of internal_total
        if self.internal_total:
            _dict['internalTotal'] = self.internal_total.to_dict()
        # override the default output from pydantic by calling `to_dict()` of user_specified_currency_average_price_per_night
        if self.user_specified_currency_average_price_per_night:
            _dict['userSpecifiedCurrencyAveragePricePerNight'] = self.user_specified_currency_average_price_per_night.to_dict()
        # override the default output from pydantic by calling `to_dict()` of internal_average_price_per_night
        if self.internal_average_price_per_night:
            _dict['internalAveragePricePerNight'] = self.internal_average_price_per_night.to_dict()
        # override the default output from pydantic by calling `to_dict()` of source_average_price_per_night
        if self.source_average_price_per_night:
            _dict['sourceAveragePricePerNight'] = self.source_average_price_per_night.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of StayRateNonAuthenticatedEntity from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "userSpecifiedCurrencyBaseTotal": CustomMonetaryAmount.from_dict(obj["userSpecifiedCurrencyBaseTotal"]) if obj.get("userSpecifiedCurrencyBaseTotal") is not None else None,
            "sourceBaseTotal": CustomMonetaryAmount.from_dict(obj["sourceBaseTotal"]) if obj.get("sourceBaseTotal") is not None else None,
            "internalBaseTotal": CustomMonetaryAmount.from_dict(obj["internalBaseTotal"]) if obj.get("internalBaseTotal") is not None else None,
            "sourceExtraPaxModifier": obj.get("sourceExtraPaxModifier"),
            "internalExtraPaxModifier": obj.get("internalExtraPaxModifier"),
            "userSpecifiedCurrencyExtraPaxModifier": obj.get("userSpecifiedCurrencyExtraPaxModifier"),
            "sourceExtraChildModifier": obj.get("sourceExtraChildModifier"),
            "internalExtraChildModifier": obj.get("internalExtraChildModifier"),
            "userSpecifiedCurrencyExtraChildModifier": obj.get("userSpecifiedCurrencyExtraChildModifier"),
            "sourceSingleOccupantModifier": obj.get("sourceSingleOccupantModifier"),
            "internalSingleOccupantModifier": obj.get("internalSingleOccupantModifier"),
            "userSpecifiedCurrencySingleOccupantModifier": obj.get("userSpecifiedCurrencySingleOccupantModifier"),
            "sourcePromotionalModifier": obj.get("sourcePromotionalModifier"),
            "internalPromotionalModifier": obj.get("internalPromotionalModifier"),
            "userSpecifiedCurrencyPromotionalModifier": obj.get("userSpecifiedCurrencyPromotionalModifier"),
            "sourcePremiumModifier": obj.get("sourcePremiumModifier"),
            "internalPremiumModifier": obj.get("internalPremiumModifier"),
            "userSpecifiedCurrencyPremiumModifier": obj.get("userSpecifiedCurrencyPremiumModifier"),
            "sourceChannelModifier": obj.get("sourceChannelModifier"),
            "internalChannelModifier": obj.get("internalChannelModifier"),
            "userSpecifiedCurrencyChannelModifier": obj.get("userSpecifiedCurrencyChannelModifier"),
            "quantity": obj.get("quantity"),
            "minOccupancy": obj.get("minOccupancy"),
            "maxOccupancy": obj.get("maxOccupancy"),
            "rateSource": obj.get("rateSource"),
            "promotionalDiscountPercent": obj.get("promotionalDiscountPercent"),
            "channelDiscountPercent": obj.get("channelDiscountPercent"),
            "premiumPercent": obj.get("premiumPercent"),
            "available": obj.get("available"),
            "sourceToUserCurrencyQuote": QuoteLightweightNonAuthenticatedEntity.from_dict(obj["sourceToUserCurrencyQuote"]) if obj.get("sourceToUserCurrencyQuote") is not None else None,
            "sourceToInternalCurrencyQuote": QuoteLightweightNonAuthenticatedEntity.from_dict(obj["sourceToInternalCurrencyQuote"]) if obj.get("sourceToInternalCurrencyQuote") is not None else None,
            "offerDetails": [LocalizedDescriptionNonAuthenticatedEntity.from_dict(_item) for _item in obj["offerDetails"]] if obj.get("offerDetails") is not None else None,
            "promotionalCodes": obj.get("promotionalCodes"),
            "userSpecifiedCurrencyTotal": CustomMonetaryAmount.from_dict(obj["userSpecifiedCurrencyTotal"]) if obj.get("userSpecifiedCurrencyTotal") is not None else None,
            "sourceTotal": CustomMonetaryAmount.from_dict(obj["sourceTotal"]) if obj.get("sourceTotal") is not None else None,
            "internalTotal": CustomMonetaryAmount.from_dict(obj["internalTotal"]) if obj.get("internalTotal") is not None else None,
            "userSpecifiedCurrencyAveragePricePerNight": CustomMonetaryAmount.from_dict(obj["userSpecifiedCurrencyAveragePricePerNight"]) if obj.get("userSpecifiedCurrencyAveragePricePerNight") is not None else None,
            "internalAveragePricePerNight": CustomMonetaryAmount.from_dict(obj["internalAveragePricePerNight"]) if obj.get("internalAveragePricePerNight") is not None else None,
            "sourceAveragePricePerNight": CustomMonetaryAmount.from_dict(obj["sourceAveragePricePerNight"]) if obj.get("sourceAveragePricePerNight") is not None else None,
            "totalDiscountPercent": obj.get("totalDiscountPercent")
        })
        return _obj


