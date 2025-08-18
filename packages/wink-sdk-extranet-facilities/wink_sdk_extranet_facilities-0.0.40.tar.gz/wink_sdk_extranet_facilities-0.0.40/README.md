# wink-sdk-extranet-facilities
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



# Extranet Facilities API
This part of the documentation concerns itself with the management of facilities, on and off the property. This API lets you create:

1. Guest room: Manage room types on and off the premises.
2. Meeting room: Manage meeting rooms on and off the premises.
3. Restaurant: Manage restaurants on and off the premises.
4. Spa: Manage spas on and off the premises.

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
pip install wink_sdk_extranet_facilities
```

Or you can install it directly from the repository using:
```sh
pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_extranet_facilities&subdirectory=wink-sdk-extranet-facilities
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_extranet_facilities&subdirectory=wink_sdk_extranet_facilities`)

Then import the package:
```python
import wink_sdk_extranet_facilities
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import wink_sdk_extranet_facilities
```

### Tests

Execute `pytest` to run the tests.

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import wink_sdk_extranet_facilities
from wink_sdk_extranet_facilities.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.wink.travel
# See configuration.py for a list of all supported configuration parameters.
configuration = wink_sdk_extranet_facilities.Configuration(
    host = "https://api.wink.travel"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]


# Enter a context with an instance of the API client
with wink_sdk_extranet_facilities.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = wink_sdk_extranet_facilities.GuestRoomApi(api_client)
    property_identifier = 'hotel-1' # str | Create room type owned by this property identifier
    upsert_room_type_request_supplier = wink_sdk_extranet_facilities.UpsertRoomTypeRequestSupplier() # UpsertRoomTypeRequestSupplier | 
    wink_version = 'wink_version_example' # str |  (optional)

    try:
        # Create Guest Room
        api_response = api_instance.create_guest_room(property_identifier, upsert_room_type_request_supplier, wink_version=wink_version)
        print("The response of GuestRoomApi->create_guest_room:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling GuestRoomApi->create_guest_room: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *https://api.wink.travel*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*GuestRoomApi* | [**create_guest_room**](docs/GuestRoomApi.md#create_guest_room) | **POST** /api/property/{propertyIdentifier}/facility/room-type | Create Guest Room
*GuestRoomApi* | [**duplicate_guest_room**](docs/GuestRoomApi.md#duplicate_guest_room) | **POST** /api/property/{propertyIdentifier}/facility/room-type/{roomTypeIdentifier}/duplicate | Duplicate Guest Room
*GuestRoomApi* | [**improve_guest_room**](docs/GuestRoomApi.md#improve_guest_room) | **PUT** /api/property/{propertyIdentifier}/facility/room-type/{roomTypeIdentifier}/improve | Improve Guest Room
*GuestRoomApi* | [**remove_guest_room**](docs/GuestRoomApi.md#remove_guest_room) | **DELETE** /api/property/{propertyIdentifier}/facility/room-type/{roomTypeIdentifier} | Delete Guest Room
*GuestRoomApi* | [**remove_multimedia**](docs/GuestRoomApi.md#remove_multimedia) | **DELETE** /api/property/{propertyIdentifier}/facility/room-type/{roomTypeIdentifier}/multimedia/{multimediaIdentifier} | Delete Guest Room Multimedia
*GuestRoomApi* | [**show_guest_room**](docs/GuestRoomApi.md#show_guest_room) | **GET** /api/property/{propertyIdentifier}/facility/room-type/{roomTypeIdentifier} | Show Guest Room
*GuestRoomApi* | [**show_guest_rooms**](docs/GuestRoomApi.md#show_guest_rooms) | **GET** /api/property/{propertyIdentifier}/facility/room-type/list | Show Guest Rooms
*GuestRoomApi* | [**update_guest_room**](docs/GuestRoomApi.md#update_guest_room) | **PUT** /api/property/{propertyIdentifier}/facility/room-type/{roomTypeIdentifier} | Update Guest Room
*GuestRoomApi* | [**upload_guest_room_media**](docs/GuestRoomApi.md#upload_guest_room_media) | **POST** /api/property/{propertyIdentifier}/facility/room-type/{roomTypeIdentifier}/multimedia | Add Multimedia to Room
*MeetingRoomApi* | [**create_meeting_room**](docs/MeetingRoomApi.md#create_meeting_room) | **POST** /api/property/{propertyIdentifier}/facility/meeting-room | Create Meeting Room
*MeetingRoomApi* | [**remove_meeting_room**](docs/MeetingRoomApi.md#remove_meeting_room) | **DELETE** /api/property/{propertyIdentifier}/facility/meeting-room/{meetingRoomIdentifier} | Delete Meeting Room
*MeetingRoomApi* | [**remove_multimedia2**](docs/MeetingRoomApi.md#remove_multimedia2) | **DELETE** /api/property/{propertyIdentifier}/facility/meeting-room/{meetingRoomIdentifier}/multimedia/{multimediaIdentifier} | Delete Multimedia
*MeetingRoomApi* | [**show_meeting_room**](docs/MeetingRoomApi.md#show_meeting_room) | **GET** /api/property/{propertyIdentifier}/facility/meeting-room/{meetingRoomIdentifier} | Show Meeting Room
*MeetingRoomApi* | [**show_meeting_room_pairs**](docs/MeetingRoomApi.md#show_meeting_room_pairs) | **GET** /api/property/{propertyIdentifier}/facility/meeting-room/list/pair | Show Reference Pairs
*MeetingRoomApi* | [**show_meeting_rooms**](docs/MeetingRoomApi.md#show_meeting_rooms) | **GET** /api/property/{propertyIdentifier}/facility/meeting-room/list | Show Meeting Rooms
*MeetingRoomApi* | [**update_meeting_room**](docs/MeetingRoomApi.md#update_meeting_room) | **PUT** /api/property/{propertyIdentifier}/facility/meeting-room/{meetingRoomIdentifier} | Update Meeting Room
*MeetingRoomApi* | [**upload_meeting_room_media**](docs/MeetingRoomApi.md#upload_meeting_room_media) | **POST** /api/property/{propertyIdentifier}/facility/meeting-room/{meetingRoomIdentifier}/multimedia | Upload Binary Multimedia
*RestaurantApi* | [**create_restaurant**](docs/RestaurantApi.md#create_restaurant) | **POST** /api/property/{propertyIdentifier}/facility/restaurant | Create Restaurant
*RestaurantApi* | [**remove_multimedia1**](docs/RestaurantApi.md#remove_multimedia1) | **DELETE** /api/property/{propertyIdentifier}/facility/restaurant/{restaurantIdentifier}/multimedia/{multimediaIdentifier} | Delete Multimedia
*RestaurantApi* | [**remove_restaurant**](docs/RestaurantApi.md#remove_restaurant) | **DELETE** /api/property/{propertyIdentifier}/facility/restaurant/{restaurantIdentifier} | Delete Restaurant
*RestaurantApi* | [**show_restaurant**](docs/RestaurantApi.md#show_restaurant) | **GET** /api/property/{propertyIdentifier}/facility/restaurant/{restaurantIdentifier} | Show Restaurant
*RestaurantApi* | [**show_restaurant_pairs**](docs/RestaurantApi.md#show_restaurant_pairs) | **GET** /api/property/{propertyIdentifier}/facility/restaurant/list/pair | Show Reference Pairs
*RestaurantApi* | [**show_restaurants**](docs/RestaurantApi.md#show_restaurants) | **GET** /api/property/{propertyIdentifier}/facility/restaurant/list | Show Restaurants
*RestaurantApi* | [**update_restaurant**](docs/RestaurantApi.md#update_restaurant) | **PUT** /api/property/{propertyIdentifier}/facility/restaurant/{restaurantIdentifier} | Update Restaurant
*RestaurantApi* | [**upload_restaurant_media**](docs/RestaurantApi.md#upload_restaurant_media) | **POST** /api/property/{propertyIdentifier}/facility/restaurant/{restaurantIdentifier}/multimedia | Upload Binary Multimedia
*SpaApi* | [**create_spa**](docs/SpaApi.md#create_spa) | **POST** /api/property/{propertyIdentifier}/facility/spa | Create Spa
*SpaApi* | [**delete_multimedia**](docs/SpaApi.md#delete_multimedia) | **DELETE** /api/property/{propertyIdentifier}/facility/spa/{spaIdentifier}/multimedia/{multimediaIdentifier} | Delete Multimedia
*SpaApi* | [**remove_spa**](docs/SpaApi.md#remove_spa) | **DELETE** /api/property/{propertyIdentifier}/facility/spa/{spaIdentifier} | Delete Spa
*SpaApi* | [**show_spa**](docs/SpaApi.md#show_spa) | **GET** /api/property/{propertyIdentifier}/facility/spa/{spaIdentifier} | Show Spa
*SpaApi* | [**show_spa_pairs**](docs/SpaApi.md#show_spa_pairs) | **GET** /api/property/{propertyIdentifier}/facility/spa/list/pair | Show Reference Pairs
*SpaApi* | [**show_spas**](docs/SpaApi.md#show_spas) | **GET** /api/property/{propertyIdentifier}/facility/spa/list | Show Spas
*SpaApi* | [**update_spa**](docs/SpaApi.md#update_spa) | **PUT** /api/property/{propertyIdentifier}/facility/spa/{spaIdentifier} | Update Spa
*SpaApi* | [**upload_spa_media**](docs/SpaApi.md#upload_spa_media) | **POST** /api/property/{propertyIdentifier}/facility/spa/{spaIdentifier}/multimedia | Upload Binary Multimedia


## Documentation For Models

 - [Address](docs/Address.md)
 - [AddressSupplier](docs/AddressSupplier.md)
 - [Bed](docs/Bed.md)
 - [BedSupplier](docs/BedSupplier.md)
 - [Bedroom](docs/Bedroom.md)
 - [BedroomConfiguration](docs/BedroomConfiguration.md)
 - [BedroomConfigurationSupplier](docs/BedroomConfigurationSupplier.md)
 - [BedroomSupplier](docs/BedroomSupplier.md)
 - [Contact](docs/Contact.md)
 - [ContactSupplier](docs/ContactSupplier.md)
 - [CountryLightweight](docs/CountryLightweight.md)
 - [CountryLightweightSupplier](docs/CountryLightweightSupplier.md)
 - [CustomMonetaryAmount](docs/CustomMonetaryAmount.md)
 - [DowPatternGroupSupplier](docs/DowPatternGroupSupplier.md)
 - [DuplicateGuestRoomRequestSupplier](docs/DuplicateGuestRoomRequestSupplier.md)
 - [GenericErrorMessage](docs/GenericErrorMessage.md)
 - [GeoJsonPoint](docs/GeoJsonPoint.md)
 - [GeoJsonPointSupplier](docs/GeoJsonPointSupplier.md)
 - [GeoNameLightweight](docs/GeoNameLightweight.md)
 - [GeoNameLightweightSupplier](docs/GeoNameLightweightSupplier.md)
 - [ImproveRoomTypeRequestSupplier](docs/ImproveRoomTypeRequestSupplier.md)
 - [ImproveRoomTypeResponseSupplier](docs/ImproveRoomTypeResponseSupplier.md)
 - [KeyValuePairSupplier](docs/KeyValuePairSupplier.md)
 - [MediaAuthorAttribution](docs/MediaAuthorAttribution.md)
 - [MediaAuthorAttributionSupplier](docs/MediaAuthorAttributionSupplier.md)
 - [MeetingRoomSupplier](docs/MeetingRoomSupplier.md)
 - [RestaurantSupplier](docs/RestaurantSupplier.md)
 - [RoomType](docs/RoomType.md)
 - [RoomTypeSupplier](docs/RoomTypeSupplier.md)
 - [ShowSpa400Response](docs/ShowSpa400Response.md)
 - [SimpleDescription](docs/SimpleDescription.md)
 - [SimpleDescriptionSupplier](docs/SimpleDescriptionSupplier.md)
 - [SimpleMultimedia](docs/SimpleMultimedia.md)
 - [SimpleMultimediaSupplier](docs/SimpleMultimediaSupplier.md)
 - [Social](docs/Social.md)
 - [SocialSupplier](docs/SocialSupplier.md)
 - [SpaSupplier](docs/SpaSupplier.md)
 - [SubCountryLightweight](docs/SubCountryLightweight.md)
 - [SubCountryLightweightSupplier](docs/SubCountryLightweightSupplier.md)
 - [SubSubCountryLightweight](docs/SubSubCountryLightweight.md)
 - [SubSubCountryLightweightSupplier](docs/SubSubCountryLightweightSupplier.md)
 - [TransactionalTravelInventory](docs/TransactionalTravelInventory.md)
 - [TransactionalTravelInventorySupplier](docs/TransactionalTravelInventorySupplier.md)
 - [TravelInventoryRecognition](docs/TravelInventoryRecognition.md)
 - [TravelInventoryRecognitionSupplier](docs/TravelInventoryRecognitionSupplier.md)
 - [UpsertAddressRequestSupplier](docs/UpsertAddressRequestSupplier.md)
 - [UpsertMeetingRoomRequestSupplier](docs/UpsertMeetingRoomRequestSupplier.md)
 - [UpsertRestaurantRequestSupplier](docs/UpsertRestaurantRequestSupplier.md)
 - [UpsertRoomTypeRequestSupplier](docs/UpsertRoomTypeRequestSupplier.md)
 - [UpsertSimpleDescriptionSupplier](docs/UpsertSimpleDescriptionSupplier.md)
 - [UpsertSpaRequestSupplier](docs/UpsertSpaRequestSupplier.md)


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


