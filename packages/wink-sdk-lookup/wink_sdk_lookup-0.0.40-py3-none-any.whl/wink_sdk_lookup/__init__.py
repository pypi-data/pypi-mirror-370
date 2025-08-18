# coding: utf-8

# flake8: noqa

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Lookup API The Lookup API exposes endpoints to search for inventory by region, type. It's the entryway to bookable inventory when you don't yet know what you are looking for.  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.18.5
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


__version__ = "0.0.40"

# import apis into sdk package
from wink_sdk_lookup.api.lookup_api import LookupApi

# import ApiClient
from wink_sdk_lookup.api_response import ApiResponse
from wink_sdk_lookup.api_client import ApiClient
from wink_sdk_lookup.configuration import Configuration
from wink_sdk_lookup.exceptions import OpenApiException
from wink_sdk_lookup.exceptions import ApiTypeError
from wink_sdk_lookup.exceptions import ApiValueError
from wink_sdk_lookup.exceptions import ApiKeyError
from wink_sdk_lookup.exceptions import ApiAttributeError
from wink_sdk_lookup.exceptions import ApiException

# import models into sdk package
from wink_sdk_lookup.models.agency_score_request_non_authenticated_entity import AgencyScoreRequestNonAuthenticatedEntity
from wink_sdk_lookup.models.bed_non_authenticated_entity import BedNonAuthenticatedEntity
from wink_sdk_lookup.models.bedroom_configuration_non_authenticated_entity import BedroomConfigurationNonAuthenticatedEntity
from wink_sdk_lookup.models.bedroom_non_authenticated_entity import BedroomNonAuthenticatedEntity
from wink_sdk_lookup.models.cancellation_policy_exception_non_authenticated_entity import CancellationPolicyExceptionNonAuthenticatedEntity
from wink_sdk_lookup.models.cancellation_policy_exceptions_non_authenticated_entity import CancellationPolicyExceptionsNonAuthenticatedEntity
from wink_sdk_lookup.models.cancellation_policy_lightweight_non_authenticated_entity import CancellationPolicyLightweightNonAuthenticatedEntity
from wink_sdk_lookup.models.child_non_authenticated_entity import ChildNonAuthenticatedEntity
from wink_sdk_lookup.models.city_score_request_non_authenticated_entity import CityScoreRequestNonAuthenticatedEntity
from wink_sdk_lookup.models.city_search_request_non_authenticated_entity import CitySearchRequestNonAuthenticatedEntity
from wink_sdk_lookup.models.contact_non_authenticated_entity import ContactNonAuthenticatedEntity
from wink_sdk_lookup.models.country_score_request_non_authenticated_entity import CountryScoreRequestNonAuthenticatedEntity
from wink_sdk_lookup.models.custom_monetary_amount import CustomMonetaryAmount
from wink_sdk_lookup.models.extra_charge_non_authenticated_entity import ExtraChargeNonAuthenticatedEntity
from wink_sdk_lookup.models.extra_charges_non_authenticated_entity import ExtraChargesNonAuthenticatedEntity
from wink_sdk_lookup.models.general_manager_non_authenticated_entity import GeneralManagerNonAuthenticatedEntity
from wink_sdk_lookup.models.generic_error_message import GenericErrorMessage
from wink_sdk_lookup.models.geo_json_line_string_non_authenticated_entity import GeoJsonLineStringNonAuthenticatedEntity
from wink_sdk_lookup.models.geo_json_point_non_authenticated_entity import GeoJsonPointNonAuthenticatedEntity
from wink_sdk_lookup.models.geo_json_polygon_non_authenticated_entity import GeoJsonPolygonNonAuthenticatedEntity
from wink_sdk_lookup.models.global_score_request_non_authenticated_entity import GlobalScoreRequestNonAuthenticatedEntity
from wink_sdk_lookup.models.guest_room_lightweight_non_authenticated_entity import GuestRoomLightweightNonAuthenticatedEntity
from wink_sdk_lookup.models.hotel_per_country_count_non_authenticated_entity import HotelPerCountryCountNonAuthenticatedEntity
from wink_sdk_lookup.models.itinerary_non_authenticated_entity import ItineraryNonAuthenticatedEntity
from wink_sdk_lookup.models.localized_description_non_authenticated_entity import LocalizedDescriptionNonAuthenticatedEntity
from wink_sdk_lookup.models.localized_price_non_authenticated_entity import LocalizedPriceNonAuthenticatedEntity
from wink_sdk_lookup.models.localized_transactional_travel_inventory_non_authenticated_entity import LocalizedTransactionalTravelInventoryNonAuthenticatedEntity
from wink_sdk_lookup.models.lookup_cached_non_authenticated_entity import LookupCachedNonAuthenticatedEntity
from wink_sdk_lookup.models.lookup_lightweight_non_authenticated_entity import LookupLightweightNonAuthenticatedEntity
from wink_sdk_lookup.models.map_request_non_authenticated_entity import MapRequestNonAuthenticatedEntity
from wink_sdk_lookup.models.media_author_attribution_non_authenticated_entity import MediaAuthorAttributionNonAuthenticatedEntity
from wink_sdk_lookup.models.page_property_with_best_price_non_authenticated_entity import PagePropertyWithBestPriceNonAuthenticatedEntity
from wink_sdk_lookup.models.pageable_object_non_authenticated_entity import PageableObjectNonAuthenticatedEntity
from wink_sdk_lookup.models.point_non_authenticated_entity import PointNonAuthenticatedEntity
from wink_sdk_lookup.models.property_aggregate_lightweight_non_authenticated_entity import PropertyAggregateLightweightNonAuthenticatedEntity
from wink_sdk_lookup.models.property_policy_non_authenticated_entity import PropertyPolicyNonAuthenticatedEntity
from wink_sdk_lookup.models.property_with_best_price_non_authenticated_entity import PropertyWithBestPriceNonAuthenticatedEntity
from wink_sdk_lookup.models.quote_lightweight_non_authenticated_entity import QuoteLightweightNonAuthenticatedEntity
from wink_sdk_lookup.models.rate_plan_level_fee_non_authenticated_entity import RatePlanLevelFeeNonAuthenticatedEntity
from wink_sdk_lookup.models.room_configuration_non_authenticated_entity import RoomConfigurationNonAuthenticatedEntity
from wink_sdk_lookup.models.room_configuration_price_non_authenticated_entity import RoomConfigurationPriceNonAuthenticatedEntity
from wink_sdk_lookup.models.room_configuration_price_rate_plan_non_authenticated_entity import RoomConfigurationPriceRatePlanNonAuthenticatedEntity
from wink_sdk_lookup.models.room_type_best_price_non_authenticated_entity import RoomTypeBestPriceNonAuthenticatedEntity
from wink_sdk_lookup.models.search_by_geo_location400_response import SearchByGeoLocation400Response
from wink_sdk_lookup.models.search_filters_non_authenticated_entity import SearchFiltersNonAuthenticatedEntity
from wink_sdk_lookup.models.simple_address_non_authenticated_entity import SimpleAddressNonAuthenticatedEntity
from wink_sdk_lookup.models.simple_description_non_authenticated_entity import SimpleDescriptionNonAuthenticatedEntity
from wink_sdk_lookup.models.simple_multimedia_non_authenticated_entity import SimpleMultimediaNonAuthenticatedEntity
from wink_sdk_lookup.models.social_non_authenticated_entity import SocialNonAuthenticatedEntity
from wink_sdk_lookup.models.sort_object_non_authenticated_entity import SortObjectNonAuthenticatedEntity
from wink_sdk_lookup.models.stay_rate_non_authenticated_entity import StayRateNonAuthenticatedEntity
from wink_sdk_lookup.models.travel_inventory_recognition_non_authenticated_entity import TravelInventoryRecognitionNonAuthenticatedEntity
from wink_sdk_lookup.models.user_session_non_authenticated_entity import UserSessionNonAuthenticatedEntity
