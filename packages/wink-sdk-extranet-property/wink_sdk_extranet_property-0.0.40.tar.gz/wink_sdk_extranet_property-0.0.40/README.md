# wink-sdk-extranet-property
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



# Extranet Property API
This part of the documentation concerns itself with basic property management. It can:

1. Property: List existing properties. Manage property status. Change name and similar.
2. Notification: Read internal messages sent from Wink to your properties.
3. Announcement: Show pertinent messages to travelers in a pop-up window.
4. Geo-location: Set property geo-location.
5. Green Index: Answer eco-related questions regarding the property's recycling practices and much more.
6. Lifestyles: Manage lifestyles the property caters to.
7. Photos / Videos: Manage property media.
8. Policy: Manage property policy. I.e. Children, pets, wi-fi, parking etc.
9. Reputation: Manage awards, online / offline ratings etc.
10. Services: Manage property amenities.
11. Social media: Manage property social media networks.
12. Welcome text: Manage property descriptions

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
pip install wink_sdk_extranet_property
```

Or you can install it directly from the repository using:
```sh
pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_extranet_property&subdirectory=wink-sdk-extranet-property
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_extranet_property&subdirectory=wink_sdk_extranet_property`)

Then import the package:
```python
import wink_sdk_extranet_property
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import wink_sdk_extranet_property
```

### Tests

Execute `pytest` to run the tests.

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import wink_sdk_extranet_property
from wink_sdk_extranet_property.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.wink.travel
# See configuration.py for a list of all supported configuration parameters.
configuration = wink_sdk_extranet_property.Configuration(
    host = "https://api.wink.travel"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]


# Enter a context with an instance of the API client
with wink_sdk_extranet_property.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = wink_sdk_extranet_property.AnnouncementApi(api_client)
    property_identifier = 'hotel-1' # str | Create announcement for this property identifier
    upsert_announcement_request_supplier = wink_sdk_extranet_property.UpsertAnnouncementRequestSupplier() # UpsertAnnouncementRequestSupplier | 
    wink_version = 'wink_version_example' # str |  (optional)

    try:
        # Create Announcement
        api_response = api_instance.create_announcement(property_identifier, upsert_announcement_request_supplier, wink_version=wink_version)
        print("The response of AnnouncementApi->create_announcement:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AnnouncementApi->create_announcement: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *https://api.wink.travel*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*AnnouncementApi* | [**create_announcement**](docs/AnnouncementApi.md#create_announcement) | **POST** /api/property/{propertyIdentifier}/announcement | Create Announcement
*AnnouncementApi* | [**remove_announcement**](docs/AnnouncementApi.md#remove_announcement) | **DELETE** /api/property/{propertyIdentifier}/announcement/{announcementIdentifier} | Delete Announcement
*AnnouncementApi* | [**show_announcement**](docs/AnnouncementApi.md#show_announcement) | **GET** /api/property/{propertyIdentifier}/announcement/{announcementIdentifier} | Show Announcement
*AnnouncementApi* | [**show_announcements**](docs/AnnouncementApi.md#show_announcements) | **GET** /api/property/{propertyIdentifier}/announcement/list | Show Announcements
*AnnouncementApi* | [**update_announcement**](docs/AnnouncementApi.md#update_announcement) | **PUT** /api/property/{propertyIdentifier}/announcement/{announcementIdentifier} | Update Announcement
*ChannelManagerApi* | [**update_channel_manager**](docs/ChannelManagerApi.md#update_channel_manager) | **PATCH** /api/property/{propertyIdentifier}/channel-manager | Set Channel Manager
*GeoLocationApi* | [**update_geo_location**](docs/GeoLocationApi.md#update_geo_location) | **PATCH** /api/property/{propertyIdentifier}/location | Set Geo-Location
*LifestyleApi* | [**show_lifestyles**](docs/LifestyleApi.md#show_lifestyles) | **GET** /api/property/{propertyIdentifier}/lifestyles | Show Lifestyles
*LifestyleApi* | [**update_lifestyles**](docs/LifestyleApi.md#update_lifestyles) | **PUT** /api/property/{propertyIdentifier}/lifestyles | Update Lifestyles
*MediaApi* | [**create_multimedia**](docs/MediaApi.md#create_multimedia) | **POST** /api/property/{propertyIdentifier}/multimedia | Create Multimedia
*MediaApi* | [**remove_media_list**](docs/MediaApi.md#remove_media_list) | **DELETE** /api/property/{propertyIdentifier}/multimedia/list | Delete Multimedia List
*MediaApi* | [**remove_multimedia**](docs/MediaApi.md#remove_multimedia) | **DELETE** /api/property/{propertyIdentifier}/multimedia/{multimediaIdentifier} | Delete Multimedia
*MediaApi* | [**show_media_list**](docs/MediaApi.md#show_media_list) | **GET** /api/property/{propertyIdentifier}/multimedia/list | Show Multimedia
*MediaApi* | [**update_media_list**](docs/MediaApi.md#update_media_list) | **POST** /api/property/{propertyIdentifier}/multimedia/list | Update Multimedia List
*MediaApi* | [**update_multimedia**](docs/MediaApi.md#update_multimedia) | **PUT** /api/property/{propertyIdentifier}/multimedia/{multimediaIdentifier} | Update Multimedia
*MediaApi* | [**upload_multipart_files**](docs/MediaApi.md#upload_multipart_files) | **POST** /api/property/{propertyIdentifier}/multimedia/upload | Upload Multimedia
*PolicyApi* | [**create_policy**](docs/PolicyApi.md#create_policy) | **POST** /api/property/{propertyIdentifier}/policy/property | Create property policy
*PolicyApi* | [**show_property_policy**](docs/PolicyApi.md#show_property_policy) | **GET** /api/property/{propertyIdentifier}/policy/property | Show property policy
*PolicyApi* | [**update_property_policy**](docs/PolicyApi.md#update_property_policy) | **PUT** /api/property/{propertyIdentifier}/policy/property | Update property policy
*PropertyApi* | [**change_property_name**](docs/PropertyApi.md#change_property_name) | **PATCH** /api/property/{propertyIdentifier}/change-name | Change Property Name
*PropertyApi* | [**improve_welcome_text**](docs/PropertyApi.md#improve_welcome_text) | **POST** /api/property/{propertyIdentifier}/welcome-text/improve | Improve Welcome Text
*PropertyApi* | [**is_hotel_name_unique**](docs/PropertyApi.md#is_hotel_name_unique) | **GET** /api/property/unique/name | Check Property Name Uniqueness
*PropertyApi* | [**is_hotel_url_name_unique**](docs/PropertyApi.md#is_hotel_url_name_unique) | **GET** /api/property/unique/url-name | Check Property Url Slug Uniqueness
*PropertyApi* | [**property_search**](docs/PropertyApi.md#property_search) | **POST** /api/property/grid | Property Search
*PropertyApi* | [**show_hotel_by_manager**](docs/PropertyApi.md#show_hotel_by_manager) | **GET** /api/property/{propertyIdentifier} | Show Property
*PropertyApi* | [**show_hotel_status**](docs/PropertyApi.md#show_hotel_status) | **GET** /api/property/{propertyIdentifier}/status | Show Property Status
*PropertyApi* | [**show_hotels_by_manager**](docs/PropertyApi.md#show_hotels_by_manager) | **GET** /api/property/list | Property List
*PropertyApi* | [**suggest_property_profile**](docs/PropertyApi.md#suggest_property_profile) | **POST** /api/property/{propertyIdentifier}/profile/suggest | Suggest property profile
*PropertyApi* | [**suggest_property_welcome_text**](docs/PropertyApi.md#suggest_property_welcome_text) | **POST** /api/property/{propertyIdentifier}/welcome-text/suggest | Suggest Property Welcome Text
*PropertyApi* | [**suggest_property_welcome_text1**](docs/PropertyApi.md#suggest_property_welcome_text1) | **POST** /api/property/{propertyIdentifier}/services/suggest | Suggest property amenities
*PropertyApi* | [**update_address**](docs/PropertyApi.md#update_address) | **PATCH** /api/property/{propertyIdentifier}/address | Update Property Address
*PropertyApi* | [**update_general_manager**](docs/PropertyApi.md#update_general_manager) | **PATCH** /api/property/{propertyIdentifier}/general-manager | Update General Manager
*PropertyApi* | [**update_hotel_status**](docs/PropertyApi.md#update_hotel_status) | **PATCH** /api/property/{propertyIdentifier}/status | Update Property Status
*PropertyApi* | [**update_property_profile**](docs/PropertyApi.md#update_property_profile) | **PATCH** /api/property/{propertyIdentifier}/profile | Update Property Profile
*PropertyApi* | [**update_reservations_desk**](docs/PropertyApi.md#update_reservations_desk) | **PATCH** /api/property/{propertyIdentifier}/contact-info | Update Reservations Desk
*PropertyApi* | [**update_services**](docs/PropertyApi.md#update_services) | **PATCH** /api/property/{propertyIdentifier}/services | Update Property Services
*PropertyApi* | [**update_welcome_text**](docs/PropertyApi.md#update_welcome_text) | **PATCH** /api/property/{propertyIdentifier}/welcome-text | Update Property Text
*PropertyApi* | [**upload_general_manager_profile_picture**](docs/PropertyApi.md#upload_general_manager_profile_picture) | **POST** /api/property/{propertyIdentifier}/multimedia/general-manager/upload | Upload General Manager Image
*RecognitionApi* | [**create_recognition**](docs/RecognitionApi.md#create_recognition) | **POST** /api/property/{propertyIdentifier}/recognition | Create Recognition
*RecognitionApi* | [**remove_recognition**](docs/RecognitionApi.md#remove_recognition) | **DELETE** /api/property/{propertyIdentifier}/recognition/{recognitionIdentifier} | Delete Recognition
*RecognitionApi* | [**show_recognition**](docs/RecognitionApi.md#show_recognition) | **GET** /api/property/{propertyIdentifier}/recognition/{recognitionIdentifier} | Show Recognition
*RecognitionApi* | [**show_recognitions**](docs/RecognitionApi.md#show_recognitions) | **GET** /api/property/{propertyIdentifier}/recognition/list | Show Recognitions
*RecognitionApi* | [**show_recognitions_by_category**](docs/RecognitionApi.md#show_recognitions_by_category) | **GET** /api/property/{propertyIdentifier}/recognition/{category}/list | Show Recognition by Category
*RecognitionApi* | [**update_recognition**](docs/RecognitionApi.md#update_recognition) | **PUT** /api/property/{propertyIdentifier}/recognition/{recognitionIdentifier} | Update Recognition
*SocialNetworkApi* | [**show_social_networks**](docs/SocialNetworkApi.md#show_social_networks) | **GET** /api/property/{propertyIdentifier}/social-networks | Show Social Networks
*SocialNetworkApi* | [**update_socials**](docs/SocialNetworkApi.md#update_socials) | **PATCH** /api/property/{propertyIdentifier}/social-networks | Update Social Networks


## Documentation For Models

 - [AddressSupplier](docs/AddressSupplier.md)
 - [AggregateDescriptorSupplier](docs/AggregateDescriptorSupplier.md)
 - [AggregateGreendexAnswersSupplier](docs/AggregateGreendexAnswersSupplier.md)
 - [AggregateGreendexScoreByCategorySupplier](docs/AggregateGreendexScoreByCategorySupplier.md)
 - [AnnouncementSupplier](docs/AnnouncementSupplier.md)
 - [ChangePropertyNameRequestSupplier](docs/ChangePropertyNameRequestSupplier.md)
 - [CompositeFilterDescriptorSupplier](docs/CompositeFilterDescriptorSupplier.md)
 - [ContactSupplier](docs/ContactSupplier.md)
 - [CountryLightweightSupplier](docs/CountryLightweightSupplier.md)
 - [CustomMonetaryAmount](docs/CustomMonetaryAmount.md)
 - [FilterDescriptorSupplier](docs/FilterDescriptorSupplier.md)
 - [GeneralManagerSupplier](docs/GeneralManagerSupplier.md)
 - [GenericErrorMessage](docs/GenericErrorMessage.md)
 - [GeoJsonPointSupplier](docs/GeoJsonPointSupplier.md)
 - [GeoNameLightweightSupplier](docs/GeoNameLightweightSupplier.md)
 - [GroupDescriptorSupplier](docs/GroupDescriptorSupplier.md)
 - [ImproveWelcomeTextRequestSupplier](docs/ImproveWelcomeTextRequestSupplier.md)
 - [KeyValuePairSupplier](docs/KeyValuePairSupplier.md)
 - [LifestylesResponseSupplier](docs/LifestylesResponseSupplier.md)
 - [LocalizedDescriptionSupplier](docs/LocalizedDescriptionSupplier.md)
 - [MediaAuthorAttributionSupplier](docs/MediaAuthorAttributionSupplier.md)
 - [PagePropertySupplier](docs/PagePropertySupplier.md)
 - [PageableObjectSupplier](docs/PageableObjectSupplier.md)
 - [PropertyLightweightSupplier](docs/PropertyLightweightSupplier.md)
 - [PropertyPolicySupplier](docs/PropertyPolicySupplier.md)
 - [PropertySupplier](docs/PropertySupplier.md)
 - [ShowRecognition400Response](docs/ShowRecognition400Response.md)
 - [SimpleDescriptionSupplier](docs/SimpleDescriptionSupplier.md)
 - [SimpleMultimediaSupplier](docs/SimpleMultimediaSupplier.md)
 - [SocialNetworksRequestSupplier](docs/SocialNetworksRequestSupplier.md)
 - [SocialNetworksResponseSupplier](docs/SocialNetworksResponseSupplier.md)
 - [SocialSupplier](docs/SocialSupplier.md)
 - [SortDescriptorSupplier](docs/SortDescriptorSupplier.md)
 - [SortObjectSupplier](docs/SortObjectSupplier.md)
 - [StateSupplier](docs/StateSupplier.md)
 - [SubCountryLightweightSupplier](docs/SubCountryLightweightSupplier.md)
 - [SubSubCountryLightweightSupplier](docs/SubSubCountryLightweightSupplier.md)
 - [SuggestAmenitiesRequestSupplier](docs/SuggestAmenitiesRequestSupplier.md)
 - [SuggestProfileRequestSupplier](docs/SuggestProfileRequestSupplier.md)
 - [SuggestProfileResponseSupplier](docs/SuggestProfileResponseSupplier.md)
 - [SuggestWelcomeTextRequestSupplier](docs/SuggestWelcomeTextRequestSupplier.md)
 - [TravelInventoryRecognitionSupplier](docs/TravelInventoryRecognitionSupplier.md)
 - [UniqueResultSupplier](docs/UniqueResultSupplier.md)
 - [UpdateChannelManagerRequestSupplier](docs/UpdateChannelManagerRequestSupplier.md)
 - [UpdateExternalHotelStatusRequestSupplier](docs/UpdateExternalHotelStatusRequestSupplier.md)
 - [UpdateLifestylesRequestSupplier](docs/UpdateLifestylesRequestSupplier.md)
 - [UpdateLocationRequestSupplier](docs/UpdateLocationRequestSupplier.md)
 - [UpdatePropertyAmenitiesAndServicesRequestSupplier](docs/UpdatePropertyAmenitiesAndServicesRequestSupplier.md)
 - [UpsertAddressRequestSupplier](docs/UpsertAddressRequestSupplier.md)
 - [UpsertAnnouncementRequestSupplier](docs/UpsertAnnouncementRequestSupplier.md)
 - [UpsertContactInfoRequestSupplier](docs/UpsertContactInfoRequestSupplier.md)
 - [UpsertPropertyAddressRequestSupplier](docs/UpsertPropertyAddressRequestSupplier.md)
 - [UpsertPropertyProfileRequestSupplier](docs/UpsertPropertyProfileRequestSupplier.md)
 - [UpsertRecognitionSupplier](docs/UpsertRecognitionSupplier.md)
 - [UpsertSimpleDescriptionSupplier](docs/UpsertSimpleDescriptionSupplier.md)
 - [UpsertWelcomeTextRequestSupplier](docs/UpsertWelcomeTextRequestSupplier.md)


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


