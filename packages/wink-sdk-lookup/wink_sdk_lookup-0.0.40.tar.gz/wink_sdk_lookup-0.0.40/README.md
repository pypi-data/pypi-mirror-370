# wink-sdk-lookup
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



# Lookup API
The Lookup API exposes endpoints to search for inventory by region, type. It's the entryway to bookable inventory when you don't yet know what you are looking for.

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
pip install wink_sdk_lookup
```

Or you can install it directly from the repository using:
```sh
pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_lookup&subdirectory=wink-sdk-lookup
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_lookup&subdirectory=wink_sdk_lookup`)

Then import the package:
```python
import wink_sdk_lookup
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import wink_sdk_lookup
```

### Tests

Execute `pytest` to run the tests.

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import wink_sdk_lookup
from wink_sdk_lookup.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.wink.travel
# See configuration.py for a list of all supported configuration parameters.
configuration = wink_sdk_lookup.Configuration(
    host = "https://api.wink.travel"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]


# Enter a context with an instance of the API client
with wink_sdk_lookup.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = wink_sdk_lookup.LookupApi(api_client)
    agency_score_request_non_authenticated_entity = wink_sdk_lookup.AgencyScoreRequestNonAuthenticatedEntity() # AgencyScoreRequestNonAuthenticatedEntity | 
    engine_configuration_identifier = 'engine_configuration_identifier_example' # str | Engine configuration identifier (optional)
    wink_version = 'wink_version_example' # str |  (optional)
    accept = 'accept_example' # str |  (optional)

    try:
        # Ranked Agency Search
        api_response = api_instance.score_inventory_by_agency(agency_score_request_non_authenticated_entity, engine_configuration_identifier=engine_configuration_identifier, wink_version=wink_version, accept=accept)
        print("The response of LookupApi->score_inventory_by_agency:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling LookupApi->score_inventory_by_agency: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *https://api.wink.travel*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*LookupApi* | [**score_inventory_by_agency**](docs/LookupApi.md#score_inventory_by_agency) | **POST** /api/ranked/search/agency | Ranked Agency Search
*LookupApi* | [**score_inventory_by_city**](docs/LookupApi.md#score_inventory_by_city) | **POST** /api/ranked/search/city | Ranked City Search
*LookupApi* | [**search_by_geo_location**](docs/LookupApi.md#search_by_geo_location) | **POST** /api/search/geo | By Geo-Location
*LookupApi* | [**search_inventory_by_city**](docs/LookupApi.md#search_inventory_by_city) | **POST** /api/search/city | City Search
*LookupApi* | [**search_score_by_country**](docs/LookupApi.md#search_score_by_country) | **POST** /api/ranked/search/country | Ranked Country Search
*LookupApi* | [**search_score_by_global**](docs/LookupApi.md#search_score_by_global) | **POST** /api/ranked/search/global | Ranked Global Search
*LookupApi* | [**search_suggestions**](docs/LookupApi.md#search_suggestions) | **GET** /api/search | Search Lookups
*LookupApi* | [**show_hotel_aggregate_per_country**](docs/LookupApi.md#show_hotel_aggregate_per_country) | **GET** /api/property/aggregate-per-country | Aggregate Properties by Country
*LookupApi* | [**show_lookup**](docs/LookupApi.md#show_lookup) | **GET** /api/lookup/{urlName} | Show Lookup


## Documentation For Models

 - [AgencyScoreRequestNonAuthenticatedEntity](docs/AgencyScoreRequestNonAuthenticatedEntity.md)
 - [BedNonAuthenticatedEntity](docs/BedNonAuthenticatedEntity.md)
 - [BedroomConfigurationNonAuthenticatedEntity](docs/BedroomConfigurationNonAuthenticatedEntity.md)
 - [BedroomNonAuthenticatedEntity](docs/BedroomNonAuthenticatedEntity.md)
 - [CancellationPolicyExceptionNonAuthenticatedEntity](docs/CancellationPolicyExceptionNonAuthenticatedEntity.md)
 - [CancellationPolicyExceptionsNonAuthenticatedEntity](docs/CancellationPolicyExceptionsNonAuthenticatedEntity.md)
 - [CancellationPolicyLightweightNonAuthenticatedEntity](docs/CancellationPolicyLightweightNonAuthenticatedEntity.md)
 - [ChildNonAuthenticatedEntity](docs/ChildNonAuthenticatedEntity.md)
 - [CityScoreRequestNonAuthenticatedEntity](docs/CityScoreRequestNonAuthenticatedEntity.md)
 - [CitySearchRequestNonAuthenticatedEntity](docs/CitySearchRequestNonAuthenticatedEntity.md)
 - [ContactNonAuthenticatedEntity](docs/ContactNonAuthenticatedEntity.md)
 - [CountryScoreRequestNonAuthenticatedEntity](docs/CountryScoreRequestNonAuthenticatedEntity.md)
 - [CustomMonetaryAmount](docs/CustomMonetaryAmount.md)
 - [ExtraChargeNonAuthenticatedEntity](docs/ExtraChargeNonAuthenticatedEntity.md)
 - [ExtraChargesNonAuthenticatedEntity](docs/ExtraChargesNonAuthenticatedEntity.md)
 - [GeneralManagerNonAuthenticatedEntity](docs/GeneralManagerNonAuthenticatedEntity.md)
 - [GenericErrorMessage](docs/GenericErrorMessage.md)
 - [GeoJsonLineStringNonAuthenticatedEntity](docs/GeoJsonLineStringNonAuthenticatedEntity.md)
 - [GeoJsonPointNonAuthenticatedEntity](docs/GeoJsonPointNonAuthenticatedEntity.md)
 - [GeoJsonPolygonNonAuthenticatedEntity](docs/GeoJsonPolygonNonAuthenticatedEntity.md)
 - [GlobalScoreRequestNonAuthenticatedEntity](docs/GlobalScoreRequestNonAuthenticatedEntity.md)
 - [GuestRoomLightweightNonAuthenticatedEntity](docs/GuestRoomLightweightNonAuthenticatedEntity.md)
 - [HotelPerCountryCountNonAuthenticatedEntity](docs/HotelPerCountryCountNonAuthenticatedEntity.md)
 - [ItineraryNonAuthenticatedEntity](docs/ItineraryNonAuthenticatedEntity.md)
 - [LocalizedDescriptionNonAuthenticatedEntity](docs/LocalizedDescriptionNonAuthenticatedEntity.md)
 - [LocalizedPriceNonAuthenticatedEntity](docs/LocalizedPriceNonAuthenticatedEntity.md)
 - [LocalizedTransactionalTravelInventoryNonAuthenticatedEntity](docs/LocalizedTransactionalTravelInventoryNonAuthenticatedEntity.md)
 - [LookupCachedNonAuthenticatedEntity](docs/LookupCachedNonAuthenticatedEntity.md)
 - [LookupLightweightNonAuthenticatedEntity](docs/LookupLightweightNonAuthenticatedEntity.md)
 - [MapRequestNonAuthenticatedEntity](docs/MapRequestNonAuthenticatedEntity.md)
 - [MediaAuthorAttributionNonAuthenticatedEntity](docs/MediaAuthorAttributionNonAuthenticatedEntity.md)
 - [PagePropertyWithBestPriceNonAuthenticatedEntity](docs/PagePropertyWithBestPriceNonAuthenticatedEntity.md)
 - [PageableObjectNonAuthenticatedEntity](docs/PageableObjectNonAuthenticatedEntity.md)
 - [PointNonAuthenticatedEntity](docs/PointNonAuthenticatedEntity.md)
 - [PropertyAggregateLightweightNonAuthenticatedEntity](docs/PropertyAggregateLightweightNonAuthenticatedEntity.md)
 - [PropertyPolicyNonAuthenticatedEntity](docs/PropertyPolicyNonAuthenticatedEntity.md)
 - [PropertyWithBestPriceNonAuthenticatedEntity](docs/PropertyWithBestPriceNonAuthenticatedEntity.md)
 - [QuoteLightweightNonAuthenticatedEntity](docs/QuoteLightweightNonAuthenticatedEntity.md)
 - [RatePlanLevelFeeNonAuthenticatedEntity](docs/RatePlanLevelFeeNonAuthenticatedEntity.md)
 - [RoomConfigurationNonAuthenticatedEntity](docs/RoomConfigurationNonAuthenticatedEntity.md)
 - [RoomConfigurationPriceNonAuthenticatedEntity](docs/RoomConfigurationPriceNonAuthenticatedEntity.md)
 - [RoomConfigurationPriceRatePlanNonAuthenticatedEntity](docs/RoomConfigurationPriceRatePlanNonAuthenticatedEntity.md)
 - [RoomTypeBestPriceNonAuthenticatedEntity](docs/RoomTypeBestPriceNonAuthenticatedEntity.md)
 - [SearchByGeoLocation400Response](docs/SearchByGeoLocation400Response.md)
 - [SearchFiltersNonAuthenticatedEntity](docs/SearchFiltersNonAuthenticatedEntity.md)
 - [SimpleAddressNonAuthenticatedEntity](docs/SimpleAddressNonAuthenticatedEntity.md)
 - [SimpleDescriptionNonAuthenticatedEntity](docs/SimpleDescriptionNonAuthenticatedEntity.md)
 - [SimpleMultimediaNonAuthenticatedEntity](docs/SimpleMultimediaNonAuthenticatedEntity.md)
 - [SocialNonAuthenticatedEntity](docs/SocialNonAuthenticatedEntity.md)
 - [SortObjectNonAuthenticatedEntity](docs/SortObjectNonAuthenticatedEntity.md)
 - [StayRateNonAuthenticatedEntity](docs/StayRateNonAuthenticatedEntity.md)
 - [TravelInventoryRecognitionNonAuthenticatedEntity](docs/TravelInventoryRecognitionNonAuthenticatedEntity.md)
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


