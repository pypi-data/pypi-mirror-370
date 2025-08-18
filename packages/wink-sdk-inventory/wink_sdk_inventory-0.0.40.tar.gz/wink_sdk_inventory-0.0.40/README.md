# wink-sdk-inventory
 # Introduction
 Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.
 Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.

 # Integrations
 We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.

 # Intended Audience
 Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.
 - Hotel chains
 - Hotel brands
 - Travel tech companies
 - Destination sites
 - Integrators
 - Aggregators
 - Destination management companies
 - Travel agencies
 - OTAs

 ## APIs
 Not every integrator needs every API. For that reason, we have separated APIs into context.

### Test API

 - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.

### Common APIs

- [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account.
- [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.

### Consume APIs
Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.

 - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.
 - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.
 - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..
 - [Booking](/booking): All APIs related to creating bookings on the platform.
 - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.

 ### Produce APIs
 Produce endpoints are for developers who want to create and manage travel inventory.

 #### Property
 - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.
 - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.
 - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.
 - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.
 - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.
 - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.
 - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.

 #### Affiliate
 - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.
 - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.
 - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.
 - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.
 - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.

 #### Rate provider
 - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.

 ### Taxonomy APIs
 Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.

 - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.

 ### Insight APIs
 Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.

 - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.

 ### Payment APIs
 Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.

 - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.

 ## SDKs
 We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).

 - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)

 ## Usage
 These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.

 ## Versioning
 We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.

 ## Release history
 - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md



# Inventory API
The Inventory API exposes endpoints to retrieve inventory you already know about. This API lets you:

1. Consume shareable links.
2. Load up a known property with availability.
3. Load up all inventories that were created by our affiliates such as grids, maps, and individual items.

Browse the endpoints in the left navigation bar to get started.



This Python package is automatically generated by the [OpenAPI Generator](https://openapi-generator.tech) project:

- API version: 30.18.5
- Package version: 0.0.40
- Generator version: 7.12.0
- Build package: org.openapitools.codegen.languages.PythonClientCodegen

## Requirements.

Python 3.8+

## Installation & Usage
### pip install

You can install the package from PyPi using:
```sh
pip install wink_sdk_inventory
```

Or you can install it directly from the repository using:
```sh
pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_inventory&subdirectory=wink-sdk-inventory
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_inventory&subdirectory=wink_sdk_inventory`)

Then import the package:
```python
import wink_sdk_inventory
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import wink_sdk_inventory
```

### Tests

Execute `pytest` to run the tests.

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import wink_sdk_inventory
from wink_sdk_inventory.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.wink.travel
# See configuration.py for a list of all supported configuration parameters.
configuration = wink_sdk_inventory.Configuration(
    host = "https://api.wink.travel"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]


# Enter a context with an instance of the API client
with wink_sdk_inventory.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = wink_sdk_inventory.InventoryApi(api_client)
    inventory_unavailable_notification_non_authenticated_entity = wink_sdk_inventory.InventoryUnavailableNotificationNonAuthenticatedEntity() # InventoryUnavailableNotificationNonAuthenticatedEntity | 
    wink_version = 'wink_version_example' # str |  (optional)

    try:
        # Lacks Inventory
        api_response = api_instance.notify_property(inventory_unavailable_notification_non_authenticated_entity, wink_version=wink_version)
        print("The response of InventoryApi->notify_property:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling InventoryApi->notify_property: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *https://api.wink.travel*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*InventoryApi* | [**notify_property**](docs/InventoryApi.md#notify_property) | **POST** /api/inventory/unavailable | Lacks Inventory
*InventoryApi* | [**show_consumer_map**](docs/InventoryApi.md#show_consumer_map) | **GET** /api/sell/map/{inventoryMapIdentifier}/markers | Map + Markers
*InventoryApi* | [**show_inventory_grid_item**](docs/InventoryApi.md#show_inventory_grid_item) | **POST** /api/inventory/grid/item | Show Inventory Grid Item
*InventoryApi* | [**show_property_add_on**](docs/InventoryApi.md#show_property_add_on) | **POST** /api/add-on | Show Add-On Inventory
*InventoryApi* | [**show_property_aggregate**](docs/InventoryApi.md#show_property_aggregate) | **POST** /api/inventory/property | Show Property Inventory
*InventoryApi* | [**show_property_attraction**](docs/InventoryApi.md#show_property_attraction) | **POST** /api/experience/attraction | Show Attraction Inventory
*InventoryApi* | [**show_property_inventory**](docs/InventoryApi.md#show_property_inventory) | **POST** /api/inventory | Show Property
*InventoryApi* | [**show_property_list**](docs/InventoryApi.md#show_property_list) | **POST** /api/inventory/list | Show Property List
*InventoryApi* | [**show_property_meeting_room**](docs/InventoryApi.md#show_property_meeting_room) | **POST** /api/facility/meeting-room | Show Meeting Room Inventory
*InventoryApi* | [**show_property_place**](docs/InventoryApi.md#show_property_place) | **POST** /api/experience/place | Show Place Inventory
*InventoryApi* | [**show_property_recreation**](docs/InventoryApi.md#show_property_recreation) | **POST** /api/experience/activity | Show Activity Inventory
*InventoryApi* | [**show_property_restaurant**](docs/InventoryApi.md#show_property_restaurant) | **POST** /api/facility/restaurant | Show Restaurant Inventory
*InventoryApi* | [**show_property_room_type**](docs/InventoryApi.md#show_property_room_type) | **POST** /api/facility/room-type | Show Guest Room Inventory
*InventoryApi* | [**show_property_spa**](docs/InventoryApi.md#show_property_spa) | **POST** /api/facility/spa | Show Spa Inventory
*InventoryApi* | [**show_seller_inventory_list**](docs/InventoryApi.md#show_seller_inventory_list) | **POST** /api/inventory/grid | Search Inventory
*InventoryApi* | [**show_seller_inventory_ranked_list**](docs/InventoryApi.md#show_seller_inventory_ranked_list) | **POST** /api/inventory/ranked/grid | Show Ranked Inventories
*ShareableLinkApi* | [**show_consumable_url**](docs/ShareableLinkApi.md#show_consumable_url) | **POST** /api/shareable-link/{code} | Show Shareable Link


## Documentation For Models

 - [AbstractOpenGraphRedirectUrlNonAuthenticatedEntity](docs/AbstractOpenGraphRedirectUrlNonAuthenticatedEntity.md)
 - [ActivityLightweightNonAuthenticatedEntity](docs/ActivityLightweightNonAuthenticatedEntity.md)
 - [ActivityLocalizedInventoryNonAuthenticatedEntity](docs/ActivityLocalizedInventoryNonAuthenticatedEntity.md)
 - [ActivityLocalizedInventoryWithHotelBestPriceNonAuthenticatedEntity](docs/ActivityLocalizedInventoryWithHotelBestPriceNonAuthenticatedEntity.md)
 - [AddOnLightweightNonAuthenticatedEntity](docs/AddOnLightweightNonAuthenticatedEntity.md)
 - [AddOnLocalizedInventoryNonAuthenticatedEntity](docs/AddOnLocalizedInventoryNonAuthenticatedEntity.md)
 - [AddOnLocalizedInventoryWithHotelBestPriceNonAuthenticatedEntity](docs/AddOnLocalizedInventoryWithHotelBestPriceNonAuthenticatedEntity.md)
 - [AggregateActivityRequestNonAuthenticatedEntity](docs/AggregateActivityRequestNonAuthenticatedEntity.md)
 - [AggregateAddOnRequestNonAuthenticatedEntity](docs/AggregateAddOnRequestNonAuthenticatedEntity.md)
 - [AggregateAttractionRequestNonAuthenticatedEntity](docs/AggregateAttractionRequestNonAuthenticatedEntity.md)
 - [AggregateGreendexAnswersNonAuthenticatedEntity](docs/AggregateGreendexAnswersNonAuthenticatedEntity.md)
 - [AggregateGreendexScoreByCategoryNonAuthenticatedEntity](docs/AggregateGreendexScoreByCategoryNonAuthenticatedEntity.md)
 - [AggregateInventoryGridItemRequestNonAuthenticatedEntity](docs/AggregateInventoryGridItemRequestNonAuthenticatedEntity.md)
 - [AggregateMeetingRoomRequestNonAuthenticatedEntity](docs/AggregateMeetingRoomRequestNonAuthenticatedEntity.md)
 - [AggregatePlaceRequestNonAuthenticatedEntity](docs/AggregatePlaceRequestNonAuthenticatedEntity.md)
 - [AggregatePropertyRequestNonAuthenticatedEntity](docs/AggregatePropertyRequestNonAuthenticatedEntity.md)
 - [AggregateRestaurantRequestNonAuthenticatedEntity](docs/AggregateRestaurantRequestNonAuthenticatedEntity.md)
 - [AggregateRoomTypeRequestNonAuthenticatedEntity](docs/AggregateRoomTypeRequestNonAuthenticatedEntity.md)
 - [AggregateSellerInventoryListRequestNonAuthenticatedEntity](docs/AggregateSellerInventoryListRequestNonAuthenticatedEntity.md)
 - [AggregateSpaRequestNonAuthenticatedEntity](docs/AggregateSpaRequestNonAuthenticatedEntity.md)
 - [AnnouncementLightweightNonAuthenticatedEntity](docs/AnnouncementLightweightNonAuthenticatedEntity.md)
 - [AttractionLightweightNonAuthenticatedEntity](docs/AttractionLightweightNonAuthenticatedEntity.md)
 - [AttractionLocalizedInventoryNonAuthenticatedEntity](docs/AttractionLocalizedInventoryNonAuthenticatedEntity.md)
 - [AttractionLocalizedInventoryWithHotelBestPriceNonAuthenticatedEntity](docs/AttractionLocalizedInventoryWithHotelBestPriceNonAuthenticatedEntity.md)
 - [BedNonAuthenticatedEntity](docs/BedNonAuthenticatedEntity.md)
 - [BedroomConfigurationNonAuthenticatedEntity](docs/BedroomConfigurationNonAuthenticatedEntity.md)
 - [BedroomNonAuthenticatedEntity](docs/BedroomNonAuthenticatedEntity.md)
 - [CancellationPolicyExceptionNonAuthenticatedEntity](docs/CancellationPolicyExceptionNonAuthenticatedEntity.md)
 - [CancellationPolicyExceptionsNonAuthenticatedEntity](docs/CancellationPolicyExceptionsNonAuthenticatedEntity.md)
 - [CancellationPolicyLightweightNonAuthenticatedEntity](docs/CancellationPolicyLightweightNonAuthenticatedEntity.md)
 - [ChildNonAuthenticatedEntity](docs/ChildNonAuthenticatedEntity.md)
 - [ConfigurableGeoJsonCircleNonAuthenticatedEntity](docs/ConfigurableGeoJsonCircleNonAuthenticatedEntity.md)
 - [ConsumerDataMapNonAuthenticatedEntity](docs/ConsumerDataMapNonAuthenticatedEntity.md)
 - [ContactNonAuthenticatedEntity](docs/ContactNonAuthenticatedEntity.md)
 - [CustomMonetaryAmount](docs/CustomMonetaryAmount.md)
 - [DowPatternGroupNonAuthenticatedEntity](docs/DowPatternGroupNonAuthenticatedEntity.md)
 - [ExtraChargeNonAuthenticatedEntity](docs/ExtraChargeNonAuthenticatedEntity.md)
 - [ExtraChargesNonAuthenticatedEntity](docs/ExtraChargesNonAuthenticatedEntity.md)
 - [GeneralManagerNonAuthenticatedEntity](docs/GeneralManagerNonAuthenticatedEntity.md)
 - [GenericErrorMessage](docs/GenericErrorMessage.md)
 - [GeoJsonPointNonAuthenticatedEntity](docs/GeoJsonPointNonAuthenticatedEntity.md)
 - [GuestRoomLightweightNonAuthenticatedEntity](docs/GuestRoomLightweightNonAuthenticatedEntity.md)
 - [HotelInventoryListRequestNonAuthenticatedEntity](docs/HotelInventoryListRequestNonAuthenticatedEntity.md)
 - [HotelInventoryListResponseNonAuthenticatedEntity](docs/HotelInventoryListResponseNonAuthenticatedEntity.md)
 - [HotelInventoryRequestNonAuthenticatedEntity](docs/HotelInventoryRequestNonAuthenticatedEntity.md)
 - [HotelInventoryResponseNonAuthenticatedEntity](docs/HotelInventoryResponseNonAuthenticatedEntity.md)
 - [InventoryGridItemNonAuthenticatedEntity](docs/InventoryGridItemNonAuthenticatedEntity.md)
 - [InventoryMapLightweightNonAuthenticatedEntity](docs/InventoryMapLightweightNonAuthenticatedEntity.md)
 - [InventoryMapMarkerNonAuthenticatedEntity](docs/InventoryMapMarkerNonAuthenticatedEntity.md)
 - [InventoryUnavailableNotificationNonAuthenticatedEntity](docs/InventoryUnavailableNotificationNonAuthenticatedEntity.md)
 - [ItineraryNonAuthenticatedEntity](docs/ItineraryNonAuthenticatedEntity.md)
 - [LocalizedDescriptionNonAuthenticatedEntity](docs/LocalizedDescriptionNonAuthenticatedEntity.md)
 - [LocalizedPriceNonAuthenticatedEntity](docs/LocalizedPriceNonAuthenticatedEntity.md)
 - [LocalizedTransactionalTravelInventoryNonAuthenticatedEntity](docs/LocalizedTransactionalTravelInventoryNonAuthenticatedEntity.md)
 - [LookupLightweightNonAuthenticatedEntity](docs/LookupLightweightNonAuthenticatedEntity.md)
 - [MediaAuthorAttributionNonAuthenticatedEntity](docs/MediaAuthorAttributionNonAuthenticatedEntity.md)
 - [MeetingRoomLightweightNonAuthenticatedEntity](docs/MeetingRoomLightweightNonAuthenticatedEntity.md)
 - [MeetingRoomLocalizedInventoryNonAuthenticatedEntity](docs/MeetingRoomLocalizedInventoryNonAuthenticatedEntity.md)
 - [MeetingRoomLocalizedInventoryWithHotelBestPriceNonAuthenticatedEntity](docs/MeetingRoomLocalizedInventoryWithHotelBestPriceNonAuthenticatedEntity.md)
 - [MetaDataNonAuthenticatedEntity](docs/MetaDataNonAuthenticatedEntity.md)
 - [PageInventoryGridItemNonAuthenticatedEntity](docs/PageInventoryGridItemNonAuthenticatedEntity.md)
 - [PageableObjectNonAuthenticatedEntity](docs/PageableObjectNonAuthenticatedEntity.md)
 - [PlaceLightweightNonAuthenticatedEntity](docs/PlaceLightweightNonAuthenticatedEntity.md)
 - [PlaceLocalizedInventoryNonAuthenticatedEntity](docs/PlaceLocalizedInventoryNonAuthenticatedEntity.md)
 - [PlaceLocalizedInventoryWithHotelBestPriceNonAuthenticatedEntity](docs/PlaceLocalizedInventoryWithHotelBestPriceNonAuthenticatedEntity.md)
 - [PropertyAggregateLightweightNonAuthenticatedEntity](docs/PropertyAggregateLightweightNonAuthenticatedEntity.md)
 - [PropertyPolicyNonAuthenticatedEntity](docs/PropertyPolicyNonAuthenticatedEntity.md)
 - [PropertyWithBestPriceNonAuthenticatedEntity](docs/PropertyWithBestPriceNonAuthenticatedEntity.md)
 - [QuoteLightweightNonAuthenticatedEntity](docs/QuoteLightweightNonAuthenticatedEntity.md)
 - [RatePlanLevelFeeNonAuthenticatedEntity](docs/RatePlanLevelFeeNonAuthenticatedEntity.md)
 - [RestaurantLightweightNonAuthenticatedEntity](docs/RestaurantLightweightNonAuthenticatedEntity.md)
 - [RestaurantLocalizedInventoryNonAuthenticatedEntity](docs/RestaurantLocalizedInventoryNonAuthenticatedEntity.md)
 - [RestaurantLocalizedInventoryWithHotelBestPriceNonAuthenticatedEntity](docs/RestaurantLocalizedInventoryWithHotelBestPriceNonAuthenticatedEntity.md)
 - [RoomConfigurationNonAuthenticatedEntity](docs/RoomConfigurationNonAuthenticatedEntity.md)
 - [RoomConfigurationPriceNonAuthenticatedEntity](docs/RoomConfigurationPriceNonAuthenticatedEntity.md)
 - [RoomConfigurationPriceRatePlanNonAuthenticatedEntity](docs/RoomConfigurationPriceRatePlanNonAuthenticatedEntity.md)
 - [RoomTypeBestPriceNonAuthenticatedEntity](docs/RoomTypeBestPriceNonAuthenticatedEntity.md)
 - [RoomTypeWithPriceConfigurationNonAuthenticatedEntity](docs/RoomTypeWithPriceConfigurationNonAuthenticatedEntity.md)
 - [RoomTypeWithPriceConfigurationsNonAuthenticatedEntity](docs/RoomTypeWithPriceConfigurationsNonAuthenticatedEntity.md)
 - [SalesChannelInfoNonAuthenticatedEntity](docs/SalesChannelInfoNonAuthenticatedEntity.md)
 - [SellableItemLightweightNonAuthenticatedEntity](docs/SellableItemLightweightNonAuthenticatedEntity.md)
 - [SellableListLightweightNonAuthenticatedEntity](docs/SellableListLightweightNonAuthenticatedEntity.md)
 - [SellableListResponseNonAuthenticatedEntity](docs/SellableListResponseNonAuthenticatedEntity.md)
 - [SellableRankedListLightweightNonAuthenticatedEntity](docs/SellableRankedListLightweightNonAuthenticatedEntity.md)
 - [SellableRankedListResponseNonAuthenticatedEntity](docs/SellableRankedListResponseNonAuthenticatedEntity.md)
 - [SellerInventoryActivityNonAuthenticatedEntity](docs/SellerInventoryActivityNonAuthenticatedEntity.md)
 - [SellerInventoryAddOnNonAuthenticatedEntity](docs/SellerInventoryAddOnNonAuthenticatedEntity.md)
 - [SellerInventoryAttractionNonAuthenticatedEntity](docs/SellerInventoryAttractionNonAuthenticatedEntity.md)
 - [SellerInventoryGuestRoomNonAuthenticatedEntity](docs/SellerInventoryGuestRoomNonAuthenticatedEntity.md)
 - [SellerInventoryMeetingRoomNonAuthenticatedEntity](docs/SellerInventoryMeetingRoomNonAuthenticatedEntity.md)
 - [SellerInventoryPlaceNonAuthenticatedEntity](docs/SellerInventoryPlaceNonAuthenticatedEntity.md)
 - [SellerInventoryPropertyNonAuthenticatedEntity](docs/SellerInventoryPropertyNonAuthenticatedEntity.md)
 - [SellerInventoryRestaurantNonAuthenticatedEntity](docs/SellerInventoryRestaurantNonAuthenticatedEntity.md)
 - [SellerInventorySpaNonAuthenticatedEntity](docs/SellerInventorySpaNonAuthenticatedEntity.md)
 - [SellerMediaNonAuthenticatedEntity](docs/SellerMediaNonAuthenticatedEntity.md)
 - [ShowConsumableUrl400Response](docs/ShowConsumableUrl400Response.md)
 - [SimpleAddressNonAuthenticatedEntity](docs/SimpleAddressNonAuthenticatedEntity.md)
 - [SimpleDescriptionNonAuthenticatedEntity](docs/SimpleDescriptionNonAuthenticatedEntity.md)
 - [SimpleMultimediaNonAuthenticatedEntity](docs/SimpleMultimediaNonAuthenticatedEntity.md)
 - [SocialNonAuthenticatedEntity](docs/SocialNonAuthenticatedEntity.md)
 - [SortObjectNonAuthenticatedEntity](docs/SortObjectNonAuthenticatedEntity.md)
 - [SpaLightweightNonAuthenticatedEntity](docs/SpaLightweightNonAuthenticatedEntity.md)
 - [SpaLocalizedInventoryNonAuthenticatedEntity](docs/SpaLocalizedInventoryNonAuthenticatedEntity.md)
 - [SpaLocalizedInventoryWithHotelBestPriceNonAuthenticatedEntity](docs/SpaLocalizedInventoryWithHotelBestPriceNonAuthenticatedEntity.md)
 - [StayRateNonAuthenticatedEntity](docs/StayRateNonAuthenticatedEntity.md)
 - [TravelInventoryRecognitionNonAuthenticatedEntity](docs/TravelInventoryRecognitionNonAuthenticatedEntity.md)
 - [UserReviewAnswerNonAuthenticatedEntity](docs/UserReviewAnswerNonAuthenticatedEntity.md)
 - [UserReviewNonAuthenticatedEntity](docs/UserReviewNonAuthenticatedEntity.md)
 - [UserSessionNonAuthenticatedEntity](docs/UserSessionNonAuthenticatedEntity.md)


<a id="documentation-for-authorization"></a>
## Documentation For Authorization


Authentication schemes defined for the API:
<a id="oauth2ClientCredentials"></a>
### oauth2ClientCredentials

- **Type**: OAuth
- **Flow**: application
- **Authorization URL**: https://iam.wink.travel/oauth2/authorize
- **Scopes**: 
 - **inventory.read**: Read Wink data
 - **inventory.write**: Create Wink data
 - **inventory.remove**: Remove Wink data


## Author

bjorn@wink.travel


