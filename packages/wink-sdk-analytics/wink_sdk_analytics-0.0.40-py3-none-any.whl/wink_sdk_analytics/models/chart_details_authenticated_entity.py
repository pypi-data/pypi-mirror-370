# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reactive): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant reactive widget for all other entities.   - [TripPay](/reactive): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md   # Analytics API Welcome to the Affiliate API - A programmer-friendly way to get insight into platform-level activities and bookings.  

    The version of the OpenAPI document: 30.17.14
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from wink_sdk_analytics.models.key_value_pair_authenticated_entity import KeyValuePairAuthenticatedEntity
from typing import Optional, Set
from typing_extensions import Self

class ChartDetailsAuthenticatedEntity(BaseModel):
    """
    Chart properties allow you to choose how to visualize available data points. Choose how you want to:   - filter your data  - sort your data  - group your data  - include data in your data sets  - display currency amounts
    """ # noqa: E501
    series: StrictStr = Field(description="The time series to visualize")
    time_series_units: Optional[StrictInt] = Field(default=None, description="How many units of the time series type to visualize. Only required if start / end date not populated.", alias="timeSeriesUnits")
    start_date: Optional[datetime] = Field(default=None, description="Fixed date to start visualizations on", alias="startDate")
    end_date: Optional[datetime] = Field(default=None, description="Fixed date to end visualizations on", alias="endDate")
    filter_on_hotel_identifier: Optional[KeyValuePairAuthenticatedEntity] = Field(default=None, description="Filter on hotel identifier", alias="filterOnHotelIdentifier")
    filter_on_channel_sub_type: Optional[StrictStr] = Field(default=None, description="Filter on channel sub type. What channel sub-type helped make the booking.", alias="filterOnChannelSubType")
    filter_on_owner_identifier: Optional[KeyValuePairAuthenticatedEntity] = Field(default=None, description="Filter on seller identifier. What affiliate helped make this booking.", alias="filterOnOwnerIdentifier")
    filter_on_engine_country_geo_name_id: Optional[KeyValuePairAuthenticatedEntity] = Field(default=None, description="Filter on customization country geoNameId. Which country is this application from.", alias="filterOnEngineCountryGeoNameId")
    filter_on_engine_city_geo_name_id: Optional[KeyValuePairAuthenticatedEntity] = Field(default=None, description="Filter on city geoNameId. Which city is this application from.", alias="filterOnEngineCityGeoNameId")
    filter_on_engine_continent_code: Optional[KeyValuePairAuthenticatedEntity] = Field(default=None, description="Filter on continent. Which city is this application from.", alias="filterOnEngineContinentCode")
    filter_on_engine_configuration_identifier: Optional[KeyValuePairAuthenticatedEntity] = Field(default=None, description="Filter on customization. Which customization made this booking.", alias="filterOnEngineConfigurationIdentifier")
    filter_on_country_geo_name_id: Optional[KeyValuePairAuthenticatedEntity] = Field(default=None, description="Filter on country geoNameId. Which country is the traveler from.", alias="filterOnCountryGeoNameId")
    filter_on_city_geo_name_id: Optional[KeyValuePairAuthenticatedEntity] = Field(default=None, description="Filter on city geoNameId. Which city is the traveler from.", alias="filterOnCityGeoNameId")
    filter_on_continent_code: Optional[KeyValuePairAuthenticatedEntity] = Field(default=None, description="Filter on continent. Which continent is the traveler from.", alias="filterOnContinentCode")
    filter_on_user_identifier: Optional[KeyValuePairAuthenticatedEntity] = Field(default=None, description="Filter on user identifier. Which authenticated user made the booking.", alias="filterOnUserIdentifier")
    sort_on_page_visits: Optional[StrictBool] = Field(default=False, description="Sort on page visits", alias="sortOnPageVisits")
    sort_on_map_marker_visits: Optional[StrictBool] = Field(default=False, description="Sort on map marker visits", alias="sortOnMapMarkerVisits")
    sort_on_card_visits: Optional[StrictBool] = Field(default=False, description="Sort on card visits", alias="sortOnCardVisits")
    sort_on_bookings: Optional[StrictBool] = Field(default=False, description="Sort on bookings", alias="sortOnBookings")
    sort_on_cancellations: Optional[StrictBool] = Field(default=False, description="Sort on cancellations", alias="sortOnCancellations")
    sort_on_room_nights: Optional[StrictBool] = Field(default=False, description="Sort on room nights", alias="sortOnRoomNights")
    sort_on_meeting_rooms: Optional[StrictBool] = Field(default=False, description="Sort on meeting rooms", alias="sortOnMeetingRooms")
    sort_on_meeting_rooms_revenue: Optional[StrictBool] = Field(default=False, description="Sort on meeting rooms revenue", alias="sortOnMeetingRoomsRevenue")
    sort_on_restaurants: Optional[StrictBool] = Field(default=False, description="Sort on restaurants", alias="sortOnRestaurants")
    sort_on_restaurants_revenue: Optional[StrictBool] = Field(default=False, description="Sort on restaurants revenue", alias="sortOnRestaurantsRevenue")
    sort_on_spas: Optional[StrictBool] = Field(default=False, description="Sort on spas", alias="sortOnSpas")
    sort_on_spas_revenue: Optional[StrictBool] = Field(default=False, description="Sort on spas revenue", alias="sortOnSpasRevenue")
    sort_on_activities: Optional[StrictBool] = Field(default=False, description="Sort on activities", alias="sortOnActivities")
    sort_on_activities_revenue: Optional[StrictBool] = Field(default=False, description="Sort on activities revenue", alias="sortOnActivitiesRevenue")
    sort_on_attractions: Optional[StrictBool] = Field(default=False, description="Sort on attractions", alias="sortOnAttractions")
    sort_on_attractions_revenue: Optional[StrictBool] = Field(default=False, description="Sort on attractions revenue", alias="sortOnAttractionsRevenue")
    sort_on_places: Optional[StrictBool] = Field(default=False, description="Sort on places", alias="sortOnPlaces")
    sort_on_places_revenue: Optional[StrictBool] = Field(default=False, description="Sort on places revenue", alias="sortOnPlacesRevenue")
    sort_on_room_type_ancillaries: Optional[StrictBool] = Field(default=False, description="Sort on room type ancillaries", alias="sortOnRoomTypeAncillaries")
    sort_on_room_type_ancillaries_revenue: Optional[StrictBool] = Field(default=False, description="Sort on room type ancillaries revenue", alias="sortOnRoomTypeAncillariesRevenue")
    sort_on_add_ons: Optional[StrictBool] = Field(default=False, description="Sort on add-ons", alias="sortOnAddOns")
    sort_on_addons_revenue: Optional[StrictBool] = Field(default=False, description="Sort on add-on revenue", alias="sortOnAddonsRevenue")
    sort_on_total_room_revenue: Optional[StrictBool] = Field(default=False, description="Sort on total room revenue", alias="sortOnTotalRoomRevenue")
    sort_on_total_ancillaries_revenue: Optional[StrictBool] = Field(default=False, description="Sort on aggregate ancillaries revenue", alias="sortOnTotalAncillariesRevenue")
    sort_on_total_net_revenue: Optional[StrictBool] = Field(default=False, description="Sort on total net revenue", alias="sortOnTotalNetRevenue")
    sort_on_cancelled_room_nights: Optional[StrictBool] = Field(default=False, description="Sort on cancelled room nights", alias="sortOnCancelledRoomNights")
    sort_on_cancelled_meeting_rooms: Optional[StrictBool] = Field(default=False, description="Sort on cancelled meeting rooms", alias="sortOnCancelledMeetingRooms")
    sort_on_cancelled_meeting_rooms_revenue: Optional[StrictBool] = Field(default=False, description="Sort on cancelled meeting rooms revenue", alias="sortOnCancelledMeetingRoomsRevenue")
    sort_on_cancelled_restaurants: Optional[StrictBool] = Field(default=False, description="Sort on cancelled restaurants", alias="sortOnCancelledRestaurants")
    sort_on_cancelled_restaurants_revenue: Optional[StrictBool] = Field(default=False, description="Sort on cancelled restaurants revenue", alias="sortOnCancelledRestaurantsRevenue")
    sort_on_cancelled_spas: Optional[StrictBool] = Field(default=False, description="Sort on cancelled spas", alias="sortOnCancelledSpas")
    sort_on_cancelled_spas_revenue: Optional[StrictBool] = Field(default=False, description="Sort on cancelled spas revenue", alias="sortOnCancelledSpasRevenue")
    sort_on_cancelled_activities: Optional[StrictBool] = Field(default=False, description="Sort on cancelled activities", alias="sortOnCancelledActivities")
    sort_on_cancelled_activities_revenue: Optional[StrictBool] = Field(default=False, description="Sort on cancelled activities revenue", alias="sortOnCancelledActivitiesRevenue")
    sort_on_cancelled_attractions: Optional[StrictBool] = Field(default=False, description="Sort on cancelled attractions", alias="sortOnCancelledAttractions")
    sort_on_cancelled_attractions_revenue: Optional[StrictBool] = Field(default=False, description="Sort on cancelled attractions revenue", alias="sortOnCancelledAttractionsRevenue")
    sort_on_cancelled_places: Optional[StrictBool] = Field(default=False, description="Sort on cancelled places", alias="sortOnCancelledPlaces")
    sort_on_cancelled_places_revenue: Optional[StrictBool] = Field(default=False, description="Sort on cancelled places revenue", alias="sortOnCancelledPlacesRevenue")
    sort_on_cancelled_total_room_revenue: Optional[StrictBool] = Field(default=False, description="Sort on cancelled total room revenue", alias="sortOnCancelledTotalRoomRevenue")
    sort_on_cancelled_total_ancillaries_revenue: Optional[StrictBool] = Field(default=False, description="Sort on cancelled aggregate total ancillaries revenue", alias="sortOnCancelledTotalAncillariesRevenue")
    sort_on_cancelled_room_type_ancillaries: Optional[StrictBool] = Field(default=False, description="Sort on cancelled room type ancillaries", alias="sortOnCancelledRoomTypeAncillaries")
    sort_on_cancelled_room_type_ancillaries_revenue: Optional[StrictBool] = Field(default=False, description="Sort on cancelled room type ancillaries revenue", alias="sortOnCancelledRoomTypeAncillariesRevenue")
    sort_on_cancelled_add_ons: Optional[StrictBool] = Field(default=False, description="Sort on cancelled add-ons", alias="sortOnCancelledAddOns")
    sort_on_cancelled_addons_revenue: Optional[StrictBool] = Field(default=False, description="Sort on cancelled add-o revenue", alias="sortOnCancelledAddonsRevenue")
    sort_on_cancelled_total_net_revenue: Optional[StrictBool] = Field(default=False, description="Sort on cancelled total net revenue", alias="sortOnCancelledTotalNetRevenue")
    include_page_visits: Optional[StrictBool] = Field(default=False, description="Include page visits", alias="includePageVisits")
    include_map_marker_visits: Optional[StrictBool] = Field(default=False, description="Include map marker visits", alias="includeMapMarkerVisits")
    include_card_visits: Optional[StrictBool] = Field(default=False, description="Include card visits", alias="includeCardVisits")
    include_bookings: Optional[StrictBool] = Field(default=False, description="Include bookings", alias="includeBookings")
    include_cancellations: Optional[StrictBool] = Field(default=False, description="Include cancellations", alias="includeCancellations")
    include_room_nights: Optional[StrictBool] = Field(default=False, description="Include room nights", alias="includeRoomNights")
    include_meeting_rooms: Optional[StrictBool] = Field(default=False, description="Include meeting rooms", alias="includeMeetingRooms")
    include_meeting_rooms_revenue: Optional[StrictBool] = Field(default=False, description="Include meeting rooms revenue", alias="includeMeetingRoomsRevenue")
    include_restaurants: Optional[StrictBool] = Field(default=False, description="Include restaurants", alias="includeRestaurants")
    include_restaurants_revenue: Optional[StrictBool] = Field(default=False, description="Include restaurants revenue", alias="includeRestaurantsRevenue")
    include_spas: Optional[StrictBool] = Field(default=False, description="Include spas", alias="includeSpas")
    include_spas_revenue: Optional[StrictBool] = Field(default=False, description="Include spas revenue", alias="includeSpasRevenue")
    include_activities: Optional[StrictBool] = Field(default=False, description="Include activities", alias="includeActivities")
    include_activities_revenue: Optional[StrictBool] = Field(default=False, description="Include activities revenue", alias="includeActivitiesRevenue")
    include_attractions: Optional[StrictBool] = Field(default=False, description="Include attractions", alias="includeAttractions")
    include_attractions_revenue: Optional[StrictBool] = Field(default=False, description="Include attractions revenue", alias="includeAttractionsRevenue")
    include_places: Optional[StrictBool] = Field(default=False, description="Include places", alias="includePlaces")
    include_places_revenue: Optional[StrictBool] = Field(default=False, description="Include places revenue", alias="includePlacesRevenue")
    include_room_type_ancillaries: Optional[StrictBool] = Field(default=False, description="Include room type ancillaries", alias="includeRoomTypeAncillaries")
    include_room_type_ancillaries_revenue: Optional[StrictBool] = Field(default=False, description="Include packages revenue", alias="includeRoomTypeAncillariesRevenue")
    include_add_ons: Optional[StrictBool] = Field(default=False, description="Include add-ons", alias="includeAddOns")
    include_add_ons_revenue: Optional[StrictBool] = Field(default=False, description="Include add-ons revenue", alias="includeAddOnsRevenue")
    include_total_room_revenue: Optional[StrictBool] = Field(default=False, description="Include total room revenue", alias="includeTotalRoomRevenue")
    include_average_room_rate: Optional[StrictBool] = Field(default=False, description="Include average room rate", alias="includeAverageRoomRate")
    include_total_ancillaries_revenue: Optional[StrictBool] = Field(default=False, description="Include combined packages and add-os revenue", alias="includeTotalAncillariesRevenue")
    include_total_net_revenue: Optional[StrictBool] = Field(default=False, description="Include total net revenue", alias="includeTotalNetRevenue")
    include_cancelled_room_nights: Optional[StrictBool] = Field(default=False, description="Include cancelled room nights", alias="includeCancelledRoomNights")
    include_cancelled_meeting_rooms: Optional[StrictBool] = Field(default=False, description="Include cancelled meeting rooms", alias="includeCancelledMeetingRooms")
    include_cancelled_meeting_rooms_revenue: Optional[StrictBool] = Field(default=False, description="Include cancelled meeting rooms revenue", alias="includeCancelledMeetingRoomsRevenue")
    include_cancelled_restaurants: Optional[StrictBool] = Field(default=False, description="Include cancelled restaurants", alias="includeCancelledRestaurants")
    include_cancelled_restaurants_revenue: Optional[StrictBool] = Field(default=False, description="Include cancelled restaurants revenue", alias="includeCancelledRestaurantsRevenue")
    include_cancelled_spas: Optional[StrictBool] = Field(default=False, description="Include cancelled spas", alias="includeCancelledSpas")
    include_cancelled_spas_revenue: Optional[StrictBool] = Field(default=False, description="Include cancelled spas revenue", alias="includeCancelledSpasRevenue")
    include_cancelled_activities: Optional[StrictBool] = Field(default=False, description="Include cancelled activities", alias="includeCancelledActivities")
    include_cancelled_activities_revenue: Optional[StrictBool] = Field(default=False, description="Include cancelled activities revenue", alias="includeCancelledActivitiesRevenue")
    include_cancelled_attractions: Optional[StrictBool] = Field(default=False, description="Include cancelled attractions", alias="includeCancelledAttractions")
    include_cancelled_attractions_revenue: Optional[StrictBool] = Field(default=False, description="Include cancelled attractions revenue", alias="includeCancelledAttractionsRevenue")
    include_cancelled_places: Optional[StrictBool] = Field(default=False, description="Include cancelled places", alias="includeCancelledPlaces")
    include_cancelled_places_revenue: Optional[StrictBool] = Field(default=False, description="Include cancelled places revenue", alias="includeCancelledPlacesRevenue")
    include_cancelled_room_type_ancillaries: Optional[StrictBool] = Field(default=False, description="Include cancelled packages", alias="includeCancelledRoomTypeAncillaries")
    include_cancelled_room_type_ancillaries_revenue: Optional[StrictBool] = Field(default=False, description="Include cancelled packages revenue", alias="includeCancelledRoomTypeAncillariesRevenue")
    include_cancelled_add_ons: Optional[StrictBool] = Field(default=False, description="Include cancelled add-ons", alias="includeCancelledAddOns")
    include_cancelled_add_ons_revenue: Optional[StrictBool] = Field(default=False, description="Include cancelled add-ons revenue", alias="includeCancelledAddOnsRevenue")
    include_cancelled_total_room_revenue: Optional[StrictBool] = Field(default=False, description="Include cancelled total room revenue", alias="includeCancelledTotalRoomRevenue")
    include_cancelled_total_ancillaries_revenue: Optional[StrictBool] = Field(default=False, description="Include combined cancelled package and add-on revenue", alias="includeCancelledTotalAncillariesRevenue")
    include_cancelled_total_net_revenue: Optional[StrictBool] = Field(default=False, description="Include cancelled total net revenue", alias="includeCancelledTotalNetRevenue")
    group_on_channel_sub_type: Optional[StrictBool] = Field(default=False, description="Group on  channel sub type", alias="groupOnChannelSubType")
    group_on_owner_identifier: Optional[StrictBool] = Field(default=False, description="Group on owner identifier", alias="groupOnOwnerIdentifier")
    group_on_engine_country_geo_name_id: Optional[StrictBool] = Field(default=False, description="Group on application country geoNameId", alias="groupOnEngineCountryGeoNameId")
    group_on_engine_city_geo_name_id: Optional[StrictBool] = Field(default=False, description="Group on application city geoNameId", alias="groupOnEngineCityGeoNameId")
    group_on_engine_continent_code: Optional[StrictBool] = Field(default=False, description="Group on application continent code", alias="groupOnEngineContinentCode")
    group_on_engine_configuration_identifier: Optional[StrictBool] = Field(default=False, description="Group on customization identifier", alias="groupOnEngineConfigurationIdentifier")
    group_on_country_geo_name_id: Optional[StrictBool] = Field(default=False, description="Group on country geoNameId", alias="groupOnCountryGeoNameId")
    group_on_city_geo_name_id: Optional[StrictBool] = Field(default=False, description="Group on city geoNameId", alias="groupOnCityGeoNameId")
    group_on_continent_code: Optional[StrictBool] = Field(default=False, description="Group on continent code", alias="groupOnContinentCode")
    group_on_hotel_identifier: Optional[StrictBool] = Field(default=False, description="Group on hotel identifier", alias="groupOnHotelIdentifier")
    group_on_user_identifier: Optional[StrictBool] = Field(default=False, description="Group on user identifier", alias="groupOnUserIdentifier")
    currency_code: Optional[StrictStr] = Field(default='USD', description="Currency code", alias="currencyCode")
    __properties: ClassVar[List[str]] = ["series", "timeSeriesUnits", "startDate", "endDate", "filterOnHotelIdentifier", "filterOnChannelSubType", "filterOnOwnerIdentifier", "filterOnEngineCountryGeoNameId", "filterOnEngineCityGeoNameId", "filterOnEngineContinentCode", "filterOnEngineConfigurationIdentifier", "filterOnCountryGeoNameId", "filterOnCityGeoNameId", "filterOnContinentCode", "filterOnUserIdentifier", "sortOnPageVisits", "sortOnMapMarkerVisits", "sortOnCardVisits", "sortOnBookings", "sortOnCancellations", "sortOnRoomNights", "sortOnMeetingRooms", "sortOnMeetingRoomsRevenue", "sortOnRestaurants", "sortOnRestaurantsRevenue", "sortOnSpas", "sortOnSpasRevenue", "sortOnActivities", "sortOnActivitiesRevenue", "sortOnAttractions", "sortOnAttractionsRevenue", "sortOnPlaces", "sortOnPlacesRevenue", "sortOnRoomTypeAncillaries", "sortOnRoomTypeAncillariesRevenue", "sortOnAddOns", "sortOnAddonsRevenue", "sortOnTotalRoomRevenue", "sortOnTotalAncillariesRevenue", "sortOnTotalNetRevenue", "sortOnCancelledRoomNights", "sortOnCancelledMeetingRooms", "sortOnCancelledMeetingRoomsRevenue", "sortOnCancelledRestaurants", "sortOnCancelledRestaurantsRevenue", "sortOnCancelledSpas", "sortOnCancelledSpasRevenue", "sortOnCancelledActivities", "sortOnCancelledActivitiesRevenue", "sortOnCancelledAttractions", "sortOnCancelledAttractionsRevenue", "sortOnCancelledPlaces", "sortOnCancelledPlacesRevenue", "sortOnCancelledTotalRoomRevenue", "sortOnCancelledTotalAncillariesRevenue", "sortOnCancelledRoomTypeAncillaries", "sortOnCancelledRoomTypeAncillariesRevenue", "sortOnCancelledAddOns", "sortOnCancelledAddonsRevenue", "sortOnCancelledTotalNetRevenue", "includePageVisits", "includeMapMarkerVisits", "includeCardVisits", "includeBookings", "includeCancellations", "includeRoomNights", "includeMeetingRooms", "includeMeetingRoomsRevenue", "includeRestaurants", "includeRestaurantsRevenue", "includeSpas", "includeSpasRevenue", "includeActivities", "includeActivitiesRevenue", "includeAttractions", "includeAttractionsRevenue", "includePlaces", "includePlacesRevenue", "includeRoomTypeAncillaries", "includeRoomTypeAncillariesRevenue", "includeAddOns", "includeAddOnsRevenue", "includeTotalRoomRevenue", "includeAverageRoomRate", "includeTotalAncillariesRevenue", "includeTotalNetRevenue", "includeCancelledRoomNights", "includeCancelledMeetingRooms", "includeCancelledMeetingRoomsRevenue", "includeCancelledRestaurants", "includeCancelledRestaurantsRevenue", "includeCancelledSpas", "includeCancelledSpasRevenue", "includeCancelledActivities", "includeCancelledActivitiesRevenue", "includeCancelledAttractions", "includeCancelledAttractionsRevenue", "includeCancelledPlaces", "includeCancelledPlacesRevenue", "includeCancelledRoomTypeAncillaries", "includeCancelledRoomTypeAncillariesRevenue", "includeCancelledAddOns", "includeCancelledAddOnsRevenue", "includeCancelledTotalRoomRevenue", "includeCancelledTotalAncillariesRevenue", "includeCancelledTotalNetRevenue", "groupOnChannelSubType", "groupOnOwnerIdentifier", "groupOnEngineCountryGeoNameId", "groupOnEngineCityGeoNameId", "groupOnEngineContinentCode", "groupOnEngineConfigurationIdentifier", "groupOnCountryGeoNameId", "groupOnCityGeoNameId", "groupOnContinentCode", "groupOnHotelIdentifier", "groupOnUserIdentifier", "currencyCode"]

    @field_validator('series')
    def series_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['HOUR', 'DAY', 'MONTH', 'YEAR']):
            raise ValueError("must be one of enum values ('HOUR', 'DAY', 'MONTH', 'YEAR')")
        return value

    @field_validator('filter_on_channel_sub_type')
    def filter_on_channel_sub_type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['DIRECT', 'APPLICATION', 'HOTEL', 'TRAVELIKO', 'CORPORATE', 'TRAVEL_AGENT', 'INFLUENCER', 'BLOGGER', 'DESTINATION', 'CHANNEL_MANAGER', 'PROPERTY_MANAGEMENT_SYSTEM', 'CENTRAL_RESERVATION_SYSTEM', 'GOOGLE_HOTEL_API', 'MANAGEMENT_COMPANY', 'CHAIN', 'BRAND', 'EVENT_ORGANIZER']):
            raise ValueError("must be one of enum values ('DIRECT', 'APPLICATION', 'HOTEL', 'TRAVELIKO', 'CORPORATE', 'TRAVEL_AGENT', 'INFLUENCER', 'BLOGGER', 'DESTINATION', 'CHANNEL_MANAGER', 'PROPERTY_MANAGEMENT_SYSTEM', 'CENTRAL_RESERVATION_SYSTEM', 'GOOGLE_HOTEL_API', 'MANAGEMENT_COMPANY', 'CHAIN', 'BRAND', 'EVENT_ORGANIZER')")
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
        """Create an instance of ChartDetailsAuthenticatedEntity from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of filter_on_hotel_identifier
        if self.filter_on_hotel_identifier:
            _dict['filterOnHotelIdentifier'] = self.filter_on_hotel_identifier.to_dict()
        # override the default output from pydantic by calling `to_dict()` of filter_on_owner_identifier
        if self.filter_on_owner_identifier:
            _dict['filterOnOwnerIdentifier'] = self.filter_on_owner_identifier.to_dict()
        # override the default output from pydantic by calling `to_dict()` of filter_on_engine_country_geo_name_id
        if self.filter_on_engine_country_geo_name_id:
            _dict['filterOnEngineCountryGeoNameId'] = self.filter_on_engine_country_geo_name_id.to_dict()
        # override the default output from pydantic by calling `to_dict()` of filter_on_engine_city_geo_name_id
        if self.filter_on_engine_city_geo_name_id:
            _dict['filterOnEngineCityGeoNameId'] = self.filter_on_engine_city_geo_name_id.to_dict()
        # override the default output from pydantic by calling `to_dict()` of filter_on_engine_continent_code
        if self.filter_on_engine_continent_code:
            _dict['filterOnEngineContinentCode'] = self.filter_on_engine_continent_code.to_dict()
        # override the default output from pydantic by calling `to_dict()` of filter_on_engine_configuration_identifier
        if self.filter_on_engine_configuration_identifier:
            _dict['filterOnEngineConfigurationIdentifier'] = self.filter_on_engine_configuration_identifier.to_dict()
        # override the default output from pydantic by calling `to_dict()` of filter_on_country_geo_name_id
        if self.filter_on_country_geo_name_id:
            _dict['filterOnCountryGeoNameId'] = self.filter_on_country_geo_name_id.to_dict()
        # override the default output from pydantic by calling `to_dict()` of filter_on_city_geo_name_id
        if self.filter_on_city_geo_name_id:
            _dict['filterOnCityGeoNameId'] = self.filter_on_city_geo_name_id.to_dict()
        # override the default output from pydantic by calling `to_dict()` of filter_on_continent_code
        if self.filter_on_continent_code:
            _dict['filterOnContinentCode'] = self.filter_on_continent_code.to_dict()
        # override the default output from pydantic by calling `to_dict()` of filter_on_user_identifier
        if self.filter_on_user_identifier:
            _dict['filterOnUserIdentifier'] = self.filter_on_user_identifier.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ChartDetailsAuthenticatedEntity from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "series": obj.get("series"),
            "timeSeriesUnits": obj.get("timeSeriesUnits"),
            "startDate": obj.get("startDate"),
            "endDate": obj.get("endDate"),
            "filterOnHotelIdentifier": KeyValuePairAuthenticatedEntity.from_dict(obj["filterOnHotelIdentifier"]) if obj.get("filterOnHotelIdentifier") is not None else None,
            "filterOnChannelSubType": obj.get("filterOnChannelSubType"),
            "filterOnOwnerIdentifier": KeyValuePairAuthenticatedEntity.from_dict(obj["filterOnOwnerIdentifier"]) if obj.get("filterOnOwnerIdentifier") is not None else None,
            "filterOnEngineCountryGeoNameId": KeyValuePairAuthenticatedEntity.from_dict(obj["filterOnEngineCountryGeoNameId"]) if obj.get("filterOnEngineCountryGeoNameId") is not None else None,
            "filterOnEngineCityGeoNameId": KeyValuePairAuthenticatedEntity.from_dict(obj["filterOnEngineCityGeoNameId"]) if obj.get("filterOnEngineCityGeoNameId") is not None else None,
            "filterOnEngineContinentCode": KeyValuePairAuthenticatedEntity.from_dict(obj["filterOnEngineContinentCode"]) if obj.get("filterOnEngineContinentCode") is not None else None,
            "filterOnEngineConfigurationIdentifier": KeyValuePairAuthenticatedEntity.from_dict(obj["filterOnEngineConfigurationIdentifier"]) if obj.get("filterOnEngineConfigurationIdentifier") is not None else None,
            "filterOnCountryGeoNameId": KeyValuePairAuthenticatedEntity.from_dict(obj["filterOnCountryGeoNameId"]) if obj.get("filterOnCountryGeoNameId") is not None else None,
            "filterOnCityGeoNameId": KeyValuePairAuthenticatedEntity.from_dict(obj["filterOnCityGeoNameId"]) if obj.get("filterOnCityGeoNameId") is not None else None,
            "filterOnContinentCode": KeyValuePairAuthenticatedEntity.from_dict(obj["filterOnContinentCode"]) if obj.get("filterOnContinentCode") is not None else None,
            "filterOnUserIdentifier": KeyValuePairAuthenticatedEntity.from_dict(obj["filterOnUserIdentifier"]) if obj.get("filterOnUserIdentifier") is not None else None,
            "sortOnPageVisits": obj.get("sortOnPageVisits") if obj.get("sortOnPageVisits") is not None else False,
            "sortOnMapMarkerVisits": obj.get("sortOnMapMarkerVisits") if obj.get("sortOnMapMarkerVisits") is not None else False,
            "sortOnCardVisits": obj.get("sortOnCardVisits") if obj.get("sortOnCardVisits") is not None else False,
            "sortOnBookings": obj.get("sortOnBookings") if obj.get("sortOnBookings") is not None else False,
            "sortOnCancellations": obj.get("sortOnCancellations") if obj.get("sortOnCancellations") is not None else False,
            "sortOnRoomNights": obj.get("sortOnRoomNights") if obj.get("sortOnRoomNights") is not None else False,
            "sortOnMeetingRooms": obj.get("sortOnMeetingRooms") if obj.get("sortOnMeetingRooms") is not None else False,
            "sortOnMeetingRoomsRevenue": obj.get("sortOnMeetingRoomsRevenue") if obj.get("sortOnMeetingRoomsRevenue") is not None else False,
            "sortOnRestaurants": obj.get("sortOnRestaurants") if obj.get("sortOnRestaurants") is not None else False,
            "sortOnRestaurantsRevenue": obj.get("sortOnRestaurantsRevenue") if obj.get("sortOnRestaurantsRevenue") is not None else False,
            "sortOnSpas": obj.get("sortOnSpas") if obj.get("sortOnSpas") is not None else False,
            "sortOnSpasRevenue": obj.get("sortOnSpasRevenue") if obj.get("sortOnSpasRevenue") is not None else False,
            "sortOnActivities": obj.get("sortOnActivities") if obj.get("sortOnActivities") is not None else False,
            "sortOnActivitiesRevenue": obj.get("sortOnActivitiesRevenue") if obj.get("sortOnActivitiesRevenue") is not None else False,
            "sortOnAttractions": obj.get("sortOnAttractions") if obj.get("sortOnAttractions") is not None else False,
            "sortOnAttractionsRevenue": obj.get("sortOnAttractionsRevenue") if obj.get("sortOnAttractionsRevenue") is not None else False,
            "sortOnPlaces": obj.get("sortOnPlaces") if obj.get("sortOnPlaces") is not None else False,
            "sortOnPlacesRevenue": obj.get("sortOnPlacesRevenue") if obj.get("sortOnPlacesRevenue") is not None else False,
            "sortOnRoomTypeAncillaries": obj.get("sortOnRoomTypeAncillaries") if obj.get("sortOnRoomTypeAncillaries") is not None else False,
            "sortOnRoomTypeAncillariesRevenue": obj.get("sortOnRoomTypeAncillariesRevenue") if obj.get("sortOnRoomTypeAncillariesRevenue") is not None else False,
            "sortOnAddOns": obj.get("sortOnAddOns") if obj.get("sortOnAddOns") is not None else False,
            "sortOnAddonsRevenue": obj.get("sortOnAddonsRevenue") if obj.get("sortOnAddonsRevenue") is not None else False,
            "sortOnTotalRoomRevenue": obj.get("sortOnTotalRoomRevenue") if obj.get("sortOnTotalRoomRevenue") is not None else False,
            "sortOnTotalAncillariesRevenue": obj.get("sortOnTotalAncillariesRevenue") if obj.get("sortOnTotalAncillariesRevenue") is not None else False,
            "sortOnTotalNetRevenue": obj.get("sortOnTotalNetRevenue") if obj.get("sortOnTotalNetRevenue") is not None else False,
            "sortOnCancelledRoomNights": obj.get("sortOnCancelledRoomNights") if obj.get("sortOnCancelledRoomNights") is not None else False,
            "sortOnCancelledMeetingRooms": obj.get("sortOnCancelledMeetingRooms") if obj.get("sortOnCancelledMeetingRooms") is not None else False,
            "sortOnCancelledMeetingRoomsRevenue": obj.get("sortOnCancelledMeetingRoomsRevenue") if obj.get("sortOnCancelledMeetingRoomsRevenue") is not None else False,
            "sortOnCancelledRestaurants": obj.get("sortOnCancelledRestaurants") if obj.get("sortOnCancelledRestaurants") is not None else False,
            "sortOnCancelledRestaurantsRevenue": obj.get("sortOnCancelledRestaurantsRevenue") if obj.get("sortOnCancelledRestaurantsRevenue") is not None else False,
            "sortOnCancelledSpas": obj.get("sortOnCancelledSpas") if obj.get("sortOnCancelledSpas") is not None else False,
            "sortOnCancelledSpasRevenue": obj.get("sortOnCancelledSpasRevenue") if obj.get("sortOnCancelledSpasRevenue") is not None else False,
            "sortOnCancelledActivities": obj.get("sortOnCancelledActivities") if obj.get("sortOnCancelledActivities") is not None else False,
            "sortOnCancelledActivitiesRevenue": obj.get("sortOnCancelledActivitiesRevenue") if obj.get("sortOnCancelledActivitiesRevenue") is not None else False,
            "sortOnCancelledAttractions": obj.get("sortOnCancelledAttractions") if obj.get("sortOnCancelledAttractions") is not None else False,
            "sortOnCancelledAttractionsRevenue": obj.get("sortOnCancelledAttractionsRevenue") if obj.get("sortOnCancelledAttractionsRevenue") is not None else False,
            "sortOnCancelledPlaces": obj.get("sortOnCancelledPlaces") if obj.get("sortOnCancelledPlaces") is not None else False,
            "sortOnCancelledPlacesRevenue": obj.get("sortOnCancelledPlacesRevenue") if obj.get("sortOnCancelledPlacesRevenue") is not None else False,
            "sortOnCancelledTotalRoomRevenue": obj.get("sortOnCancelledTotalRoomRevenue") if obj.get("sortOnCancelledTotalRoomRevenue") is not None else False,
            "sortOnCancelledTotalAncillariesRevenue": obj.get("sortOnCancelledTotalAncillariesRevenue") if obj.get("sortOnCancelledTotalAncillariesRevenue") is not None else False,
            "sortOnCancelledRoomTypeAncillaries": obj.get("sortOnCancelledRoomTypeAncillaries") if obj.get("sortOnCancelledRoomTypeAncillaries") is not None else False,
            "sortOnCancelledRoomTypeAncillariesRevenue": obj.get("sortOnCancelledRoomTypeAncillariesRevenue") if obj.get("sortOnCancelledRoomTypeAncillariesRevenue") is not None else False,
            "sortOnCancelledAddOns": obj.get("sortOnCancelledAddOns") if obj.get("sortOnCancelledAddOns") is not None else False,
            "sortOnCancelledAddonsRevenue": obj.get("sortOnCancelledAddonsRevenue") if obj.get("sortOnCancelledAddonsRevenue") is not None else False,
            "sortOnCancelledTotalNetRevenue": obj.get("sortOnCancelledTotalNetRevenue") if obj.get("sortOnCancelledTotalNetRevenue") is not None else False,
            "includePageVisits": obj.get("includePageVisits") if obj.get("includePageVisits") is not None else False,
            "includeMapMarkerVisits": obj.get("includeMapMarkerVisits") if obj.get("includeMapMarkerVisits") is not None else False,
            "includeCardVisits": obj.get("includeCardVisits") if obj.get("includeCardVisits") is not None else False,
            "includeBookings": obj.get("includeBookings") if obj.get("includeBookings") is not None else False,
            "includeCancellations": obj.get("includeCancellations") if obj.get("includeCancellations") is not None else False,
            "includeRoomNights": obj.get("includeRoomNights") if obj.get("includeRoomNights") is not None else False,
            "includeMeetingRooms": obj.get("includeMeetingRooms") if obj.get("includeMeetingRooms") is not None else False,
            "includeMeetingRoomsRevenue": obj.get("includeMeetingRoomsRevenue") if obj.get("includeMeetingRoomsRevenue") is not None else False,
            "includeRestaurants": obj.get("includeRestaurants") if obj.get("includeRestaurants") is not None else False,
            "includeRestaurantsRevenue": obj.get("includeRestaurantsRevenue") if obj.get("includeRestaurantsRevenue") is not None else False,
            "includeSpas": obj.get("includeSpas") if obj.get("includeSpas") is not None else False,
            "includeSpasRevenue": obj.get("includeSpasRevenue") if obj.get("includeSpasRevenue") is not None else False,
            "includeActivities": obj.get("includeActivities") if obj.get("includeActivities") is not None else False,
            "includeActivitiesRevenue": obj.get("includeActivitiesRevenue") if obj.get("includeActivitiesRevenue") is not None else False,
            "includeAttractions": obj.get("includeAttractions") if obj.get("includeAttractions") is not None else False,
            "includeAttractionsRevenue": obj.get("includeAttractionsRevenue") if obj.get("includeAttractionsRevenue") is not None else False,
            "includePlaces": obj.get("includePlaces") if obj.get("includePlaces") is not None else False,
            "includePlacesRevenue": obj.get("includePlacesRevenue") if obj.get("includePlacesRevenue") is not None else False,
            "includeRoomTypeAncillaries": obj.get("includeRoomTypeAncillaries") if obj.get("includeRoomTypeAncillaries") is not None else False,
            "includeRoomTypeAncillariesRevenue": obj.get("includeRoomTypeAncillariesRevenue") if obj.get("includeRoomTypeAncillariesRevenue") is not None else False,
            "includeAddOns": obj.get("includeAddOns") if obj.get("includeAddOns") is not None else False,
            "includeAddOnsRevenue": obj.get("includeAddOnsRevenue") if obj.get("includeAddOnsRevenue") is not None else False,
            "includeTotalRoomRevenue": obj.get("includeTotalRoomRevenue") if obj.get("includeTotalRoomRevenue") is not None else False,
            "includeAverageRoomRate": obj.get("includeAverageRoomRate") if obj.get("includeAverageRoomRate") is not None else False,
            "includeTotalAncillariesRevenue": obj.get("includeTotalAncillariesRevenue") if obj.get("includeTotalAncillariesRevenue") is not None else False,
            "includeTotalNetRevenue": obj.get("includeTotalNetRevenue") if obj.get("includeTotalNetRevenue") is not None else False,
            "includeCancelledRoomNights": obj.get("includeCancelledRoomNights") if obj.get("includeCancelledRoomNights") is not None else False,
            "includeCancelledMeetingRooms": obj.get("includeCancelledMeetingRooms") if obj.get("includeCancelledMeetingRooms") is not None else False,
            "includeCancelledMeetingRoomsRevenue": obj.get("includeCancelledMeetingRoomsRevenue") if obj.get("includeCancelledMeetingRoomsRevenue") is not None else False,
            "includeCancelledRestaurants": obj.get("includeCancelledRestaurants") if obj.get("includeCancelledRestaurants") is not None else False,
            "includeCancelledRestaurantsRevenue": obj.get("includeCancelledRestaurantsRevenue") if obj.get("includeCancelledRestaurantsRevenue") is not None else False,
            "includeCancelledSpas": obj.get("includeCancelledSpas") if obj.get("includeCancelledSpas") is not None else False,
            "includeCancelledSpasRevenue": obj.get("includeCancelledSpasRevenue") if obj.get("includeCancelledSpasRevenue") is not None else False,
            "includeCancelledActivities": obj.get("includeCancelledActivities") if obj.get("includeCancelledActivities") is not None else False,
            "includeCancelledActivitiesRevenue": obj.get("includeCancelledActivitiesRevenue") if obj.get("includeCancelledActivitiesRevenue") is not None else False,
            "includeCancelledAttractions": obj.get("includeCancelledAttractions") if obj.get("includeCancelledAttractions") is not None else False,
            "includeCancelledAttractionsRevenue": obj.get("includeCancelledAttractionsRevenue") if obj.get("includeCancelledAttractionsRevenue") is not None else False,
            "includeCancelledPlaces": obj.get("includeCancelledPlaces") if obj.get("includeCancelledPlaces") is not None else False,
            "includeCancelledPlacesRevenue": obj.get("includeCancelledPlacesRevenue") if obj.get("includeCancelledPlacesRevenue") is not None else False,
            "includeCancelledRoomTypeAncillaries": obj.get("includeCancelledRoomTypeAncillaries") if obj.get("includeCancelledRoomTypeAncillaries") is not None else False,
            "includeCancelledRoomTypeAncillariesRevenue": obj.get("includeCancelledRoomTypeAncillariesRevenue") if obj.get("includeCancelledRoomTypeAncillariesRevenue") is not None else False,
            "includeCancelledAddOns": obj.get("includeCancelledAddOns") if obj.get("includeCancelledAddOns") is not None else False,
            "includeCancelledAddOnsRevenue": obj.get("includeCancelledAddOnsRevenue") if obj.get("includeCancelledAddOnsRevenue") is not None else False,
            "includeCancelledTotalRoomRevenue": obj.get("includeCancelledTotalRoomRevenue") if obj.get("includeCancelledTotalRoomRevenue") is not None else False,
            "includeCancelledTotalAncillariesRevenue": obj.get("includeCancelledTotalAncillariesRevenue") if obj.get("includeCancelledTotalAncillariesRevenue") is not None else False,
            "includeCancelledTotalNetRevenue": obj.get("includeCancelledTotalNetRevenue") if obj.get("includeCancelledTotalNetRevenue") is not None else False,
            "groupOnChannelSubType": obj.get("groupOnChannelSubType") if obj.get("groupOnChannelSubType") is not None else False,
            "groupOnOwnerIdentifier": obj.get("groupOnOwnerIdentifier") if obj.get("groupOnOwnerIdentifier") is not None else False,
            "groupOnEngineCountryGeoNameId": obj.get("groupOnEngineCountryGeoNameId") if obj.get("groupOnEngineCountryGeoNameId") is not None else False,
            "groupOnEngineCityGeoNameId": obj.get("groupOnEngineCityGeoNameId") if obj.get("groupOnEngineCityGeoNameId") is not None else False,
            "groupOnEngineContinentCode": obj.get("groupOnEngineContinentCode") if obj.get("groupOnEngineContinentCode") is not None else False,
            "groupOnEngineConfigurationIdentifier": obj.get("groupOnEngineConfigurationIdentifier") if obj.get("groupOnEngineConfigurationIdentifier") is not None else False,
            "groupOnCountryGeoNameId": obj.get("groupOnCountryGeoNameId") if obj.get("groupOnCountryGeoNameId") is not None else False,
            "groupOnCityGeoNameId": obj.get("groupOnCityGeoNameId") if obj.get("groupOnCityGeoNameId") is not None else False,
            "groupOnContinentCode": obj.get("groupOnContinentCode") if obj.get("groupOnContinentCode") is not None else False,
            "groupOnHotelIdentifier": obj.get("groupOnHotelIdentifier") if obj.get("groupOnHotelIdentifier") is not None else False,
            "groupOnUserIdentifier": obj.get("groupOnUserIdentifier") if obj.get("groupOnUserIdentifier") is not None else False,
            "currencyCode": obj.get("currencyCode") if obj.get("currencyCode") is not None else 'USD'
        })
        return _obj


