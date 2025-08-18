# wink-sdk-extranet-distribution
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



# Extranet Distribution API
The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink. This API lets you:

1. Verifier: Test your availability and promotions and create test bookings to simulate the entire booking workflow.
2. Sales Channels: Manage your sales channels.
3. Explore Network: Find new affiliates to work with.
4. Inventory: Manage inventory at the sales channel-level.
5. Calendars: Manage availability calendars for all your inventory.

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
pip install wink_sdk_extranet_distribution
```

Or you can install it directly from the repository using:
```sh
pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_extranet_distribution&subdirectory=wink-sdk-extranet-distribution
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_extranet_distribution&subdirectory=wink_sdk_extranet_distribution`)

Then import the package:
```python
import wink_sdk_extranet_distribution
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import wink_sdk_extranet_distribution
```

### Tests

Execute `pytest` to run the tests.

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import wink_sdk_extranet_distribution
from wink_sdk_extranet_distribution.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.wink.travel
# See configuration.py for a list of all supported configuration parameters.
configuration = wink_sdk_extranet_distribution.Configuration(
    host = "https://api.wink.travel"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]


# Enter a context with an instance of the API client
with wink_sdk_extranet_distribution.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = wink_sdk_extranet_distribution.AffiliateApi(api_client)
    property_identifier = 'hotel-1' # str | Display affiliates to this specified property
    state_supplier = wink_sdk_extranet_distribution.StateSupplier() # StateSupplier | 
    wink_version = 'wink_version_example' # str |  (optional)

    try:
        # Show Affiliates
        api_response = api_instance.browse_affiliates(property_identifier, state_supplier, wink_version=wink_version)
        print("The response of AffiliateApi->browse_affiliates:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AffiliateApi->browse_affiliates: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *https://api.wink.travel*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*AffiliateApi* | [**browse_affiliates**](docs/AffiliateApi.md#browse_affiliates) | **POST** /api/property/{propertyIdentifier}/sales/affiliate/grid | Show Affiliates
*AffiliateApi* | [**invite_affiliate**](docs/AffiliateApi.md#invite_affiliate) | **POST** /api/property/{propertyIdentifier}/sales/affiliate/invite | Send invite
*AffiliateApi* | [**show_affiliate**](docs/AffiliateApi.md#show_affiliate) | **GET** /api/property/{propertyIdentifier}/sales/affiliate/{companyIdentifier} | Show Affiliate
*AffiliateApi* | [**show_unique_city_list**](docs/AffiliateApi.md#show_unique_city_list) | **GET** /api/property/{propertyIdentifier}/sales/affiliate/city/list | Show Unique Affiliate Cities
*AffiliateApi* | [**show_unique_country_list**](docs/AffiliateApi.md#show_unique_country_list) | **GET** /api/property/{propertyIdentifier}/sales/affiliate/country/list | Show Unique Affiliate Countries
*DailyRateApi* | [**bulk_update_rate**](docs/DailyRateApi.md#bulk_update_rate) | **PUT** /api/property/{propertyIdentifier}/master-rate/{masterRateIdentifier}/rate/bulk | Update Daily Rates by Range
*DailyRateApi* | [**create_test_booking**](docs/DailyRateApi.md#create_test_booking) | **POST** /api/property/{propertyIdentifier}/sandbox/booking | Test Rate / Availability
*DailyRateApi* | [**show_all_hotel_rates**](docs/DailyRateApi.md#show_all_hotel_rates) | **POST** /api/property/{propertyIdentifier}/master-rate/rates/dates | Daily Rates by Hotel
*DailyRateApi* | [**show_all_master_rates_rates**](docs/DailyRateApi.md#show_all_master_rates_rates) | **POST** /api/property/{propertyIdentifier}/master-rate/{masterRateIdentifier}/rates/dates | Daily Rates by Master Rate
*DailyRateApi* | [**show_channels**](docs/DailyRateApi.md#show_channels) | **GET** /api/property/{propertyIdentifier}/sandbox/channel/list | List Sales Channels
*DailyRateApi* | [**show_daily_rates_page**](docs/DailyRateApi.md#show_daily_rates_page) | **POST** /api/property/{propertyIdentifier}/master-rate/{masterRateIdentifier}/rate/grid | Show Daily Rate Page
*DailyRateApi* | [**show_descriptive_inventory**](docs/DailyRateApi.md#show_descriptive_inventory) | **POST** /api/property/{propertyIdentifier}/sandbox/room/list | Test Rate / Availability
*DailyRateApi* | [**update_rate_list**](docs/DailyRateApi.md#update_rate_list) | **PUT** /api/property/{propertyIdentifier}/rate/update | Update Daily Rates by List
*InventoryApi* | [**show_channel_activities**](docs/InventoryApi.md#show_channel_activities) | **GET** /api/property/{propertyIdentifier}/sales/experience/activity/list | Show Activity Inventories
*InventoryApi* | [**show_channel_add_ons**](docs/InventoryApi.md#show_channel_add_ons) | **GET** /api/property/{propertyIdentifier}/sales/add-on/list | Show Add-On Inventories
*InventoryApi* | [**show_channel_attractions**](docs/InventoryApi.md#show_channel_attractions) | **GET** /api/property/{propertyIdentifier}/sales/experience/attraction/list | Show Attraction Inventories
*InventoryApi* | [**show_channel_meeting_rooms**](docs/InventoryApi.md#show_channel_meeting_rooms) | **GET** /api/property/{propertyIdentifier}/sales/meeting-room/list | Show Meeting Room Inventories
*InventoryApi* | [**show_channel_places**](docs/InventoryApi.md#show_channel_places) | **GET** /api/property/{propertyIdentifier}/sales/experience/place/list | Show Place Inventories
*InventoryApi* | [**show_channel_restaurants**](docs/InventoryApi.md#show_channel_restaurants) | **GET** /api/property/{propertyIdentifier}/sales/facility/restaurant/list | Show Restaurant Inventories
*InventoryApi* | [**show_channel_spas**](docs/InventoryApi.md#show_channel_spas) | **GET** /api/property/{propertyIdentifier}/sales/facility/spa/list | Show Spa Inventories
*InventoryApi* | [**show_inventory**](docs/InventoryApi.md#show_inventory) | **GET** /api/property/{propertyIdentifier}/sales/inventory/{inventoryIdentifier} | Show Inventory
*InventoryApi* | [**show_inventory_list**](docs/InventoryApi.md#show_inventory_list) | **GET** /api/property/{propertyIdentifier}/sales/inventory/list | Show Inventory List
*InventoryApi* | [**show_inventory_names**](docs/InventoryApi.md#show_inventory_names) | **GET** /api/property/{propertyIdentifier}/sales/inventory/name/list | Show Inventory Names
*InventoryApi* | [**show_inventory_types**](docs/InventoryApi.md#show_inventory_types) | **GET** /api/property/{propertyIdentifier}/sales/inventory/type/list | Show All Inventory Types
*InventoryApi* | [**show_master_rates**](docs/InventoryApi.md#show_master_rates) | **GET** /api/property/{propertyIdentifier}/sales/master-rate/list | Show Master Rates Inventories
*InventoryApi* | [**show_pageable_channel_inventory**](docs/InventoryApi.md#show_pageable_channel_inventory) | **POST** /api/property/{propertyIdentifier}/sales/inventory/grid | Search Inventory
*InventoryApi* | [**show_sales_channel_list_by_inventory**](docs/InventoryApi.md#show_sales_channel_list_by_inventory) | **GET** /api/property/{propertyIdentifier}/sales/inventory/{inventoryTypeIdentifier}/list | Show Inventory as Channels
*InventoryApi* | [**toggle_inventory_availability**](docs/InventoryApi.md#toggle_inventory_availability) | **PATCH** /api/property/{propertyIdentifier}/sales/inventory/{inventoryIdentifier} | Update Inventory
*InventoryApi* | [**toggle_inventory_list_availability**](docs/InventoryApi.md#toggle_inventory_list_availability) | **PATCH** /api/property/{propertyIdentifier}/sales/inventory/list | Update Inventory List
*InventoryUsageApi* | [**show_activity_usage**](docs/InventoryUsageApi.md#show_activity_usage) | **GET** /api/property/{propertyIdentifier}/inventory-usage/activity/{activityIdentifier} | Show Activity Usage
*InventoryUsageApi* | [**show_add_on_usage**](docs/InventoryUsageApi.md#show_add_on_usage) | **GET** /api/property/{propertyIdentifier}/inventory-usage/add-on/{addOnIdentifier} | Show Add-On Usage
*InventoryUsageApi* | [**show_attraction_usage**](docs/InventoryUsageApi.md#show_attraction_usage) | **GET** /api/property/{propertyIdentifier}/inventory-usage/attraction/{attractionIdentifier} | Show Attraction Usage
*InventoryUsageApi* | [**show_meeting_room_usage**](docs/InventoryUsageApi.md#show_meeting_room_usage) | **GET** /api/property/{propertyIdentifier}/inventory-usage/meeting-room/{meetingRoomIdentifier} | Show Meeting Room Usage
*InventoryUsageApi* | [**show_place_usage**](docs/InventoryUsageApi.md#show_place_usage) | **GET** /api/property/{propertyIdentifier}/inventory-usage/place/{placeIdentifier} | Show Place Usage
*InventoryUsageApi* | [**show_rate_plan_usage**](docs/InventoryUsageApi.md#show_rate_plan_usage) | **GET** /api/property/{propertyIdentifier}/inventory-usage/rate-plan/{ratePlanIdentifier} | Show Rate Plan Usage
*InventoryUsageApi* | [**show_restaurant_usage**](docs/InventoryUsageApi.md#show_restaurant_usage) | **GET** /api/property/{propertyIdentifier}/inventory-usage/restaurant/{restaurantIdentifier} | Show Restaurant Usage
*InventoryUsageApi* | [**show_room_type_usage**](docs/InventoryUsageApi.md#show_room_type_usage) | **GET** /api/property/{propertyIdentifier}/inventory-usage/room-type/{roomTypeIdentifier} | Show Room Type Usage
*InventoryUsageApi* | [**show_spa_usage**](docs/InventoryUsageApi.md#show_spa_usage) | **GET** /api/property/{propertyIdentifier}/inventory-usage/spa/{spaIdentifier} | Show Spa Usage
*SalesChannelApi* | [**create_sales_channel**](docs/SalesChannelApi.md#create_sales_channel) | **POST** /api/property/{propertyIdentifier}/sales/account | Create Sales Channel
*SalesChannelApi* | [**remove_sales_channel**](docs/SalesChannelApi.md#remove_sales_channel) | **DELETE** /api/property/{propertyIdentifier}/sales/account/{salesChannelIdentifier} | Remove Sales Channel
*SalesChannelApi* | [**show_accounts**](docs/SalesChannelApi.md#show_accounts) | **GET** /api/property/{propertyIdentifier}/sales/account/list | Show Sales Channels
*SalesChannelApi* | [**show_sales_channel**](docs/SalesChannelApi.md#show_sales_channel) | **GET** /api/property/{propertyIdentifier}/sales/account/{salesChannelIdentifier} | Show Sales Channel
*SalesChannelApi* | [**show_sales_channel_context_rate_modifier_bundle_pairs**](docs/SalesChannelApi.md#show_sales_channel_context_rate_modifier_bundle_pairs) | **GET** /api/property/{propertyIdentifier}/sales/account/rate-modifier-bundle/{rateModifierBundleIdentifier}/list | Show Rate Modifier Bundle Availability
*SalesChannelApi* | [**show_sales_channel_context_rate_modifier_pairs**](docs/SalesChannelApi.md#show_sales_channel_context_rate_modifier_pairs) | **GET** /api/property/{propertyIdentifier}/sales/account/rate-modifier/{rateModifierIdentifier}/list | Show Rate Modifier Availability
*SalesChannelApi* | [**toggle_sales_channel_promo_availability**](docs/SalesChannelApi.md#toggle_sales_channel_promo_availability) | **PATCH** /api/property/{propertyIdentifier}/sales/account/rate-modifier/{rateModifierIdentifier}/list | Update Sale Channels Rate Modifiers
*SalesChannelApi* | [**toggle_sales_channel_promo_bundle_availability**](docs/SalesChannelApi.md#toggle_sales_channel_promo_bundle_availability) | **PATCH** /api/property/{propertyIdentifier}/sales/account/rate-modifier-bundle/{rateModifierBundleIdentifier}/list | Update Sale Channels Rate Modifier Bundles
*SalesChannelApi* | [**update_sales_channel**](docs/SalesChannelApi.md#update_sales_channel) | **PATCH** /api/property/{propertyIdentifier}/sales/account/{salesChannelIdentifier} | Update Sales Channel
*SalesChannelRequestApi* | [**create_sales_channel_request**](docs/SalesChannelRequestApi.md#create_sales_channel_request) | **POST** /api/property/{propertyIdentifier}/sales-channel/request | Create Sales Channel Request
*SalesChannelRequestApi* | [**remove_sales_channel_request**](docs/SalesChannelRequestApi.md#remove_sales_channel_request) | **DELETE** /api/property/{propertyIdentifier}/sales-channel/request/{salesChannelRequestIdentifier} | Reject Sales Channel Request
*SalesChannelRequestApi* | [**show_sales_channel_requests**](docs/SalesChannelRequestApi.md#show_sales_channel_requests) | **GET** /api/property/{propertyIdentifier}/sales-channel/request/list | Show Sales Channel Requests
*SchedulerApi* | [**create_schedule_item**](docs/SchedulerApi.md#create_schedule_item) | **POST** /api/property/{propertyIdentifier}/schedule/{inventoryIdentifier} | Create Scheduler Item
*SchedulerApi* | [**remove_schedule_item**](docs/SchedulerApi.md#remove_schedule_item) | **DELETE** /api/property/{propertyIdentifier}/schedule/{inventoryIdentifier}/item/{identifier} | Delete Scheduler Item
*SchedulerApi* | [**show_schedule_items**](docs/SchedulerApi.md#show_schedule_items) | **GET** /api/property/{propertyIdentifier}/schedule/{inventoryIdentifier}/list | Show Scheduler Items
*SchedulerApi* | [**update_schedule_item**](docs/SchedulerApi.md#update_schedule_item) | **PUT** /api/property/{propertyIdentifier}/schedule/{inventoryIdentifier}/item/{identifier} | Update Scheduler Item


## Documentation For Models

 - [AddressSupplierDetails](docs/AddressSupplierDetails.md)
 - [AdvanceBookingRateQualifierSupplier](docs/AdvanceBookingRateQualifierSupplier.md)
 - [AdvanceBookingRateQualifierSupplierDetails](docs/AdvanceBookingRateQualifierSupplierDetails.md)
 - [AggregateDescriptorSupplier](docs/AggregateDescriptorSupplier.md)
 - [ArrivalDaysOfWeekRateQualifierSupplier](docs/ArrivalDaysOfWeekRateQualifierSupplier.md)
 - [ArrivalDaysOfWeekRateQualifierSupplierDetails](docs/ArrivalDaysOfWeekRateQualifierSupplierDetails.md)
 - [AuthenticatedUserSupplierDetails](docs/AuthenticatedUserSupplierDetails.md)
 - [AvailableDaysOfWeekRateQualifierSupplier](docs/AvailableDaysOfWeekRateQualifierSupplier.md)
 - [AvailableDaysOfWeekRateQualifierSupplierDetails](docs/AvailableDaysOfWeekRateQualifierSupplierDetails.md)
 - [BedSupplierDetails](docs/BedSupplierDetails.md)
 - [BedroomConfigurationSupplierDetails](docs/BedroomConfigurationSupplierDetails.md)
 - [BedroomSupplierDetails](docs/BedroomSupplierDetails.md)
 - [BeneficiaryChargeSupplierDetails](docs/BeneficiaryChargeSupplierDetails.md)
 - [BeneficiarySupplierDetails](docs/BeneficiarySupplierDetails.md)
 - [BlackoutDateSupplier](docs/BlackoutDateSupplier.md)
 - [BlackoutDateSupplierDetails](docs/BlackoutDateSupplierDetails.md)
 - [BookingAncillarySupplierDetails](docs/BookingAncillarySupplierDetails.md)
 - [BookingContractItemSupplierDetails](docs/BookingContractItemSupplierDetails.md)
 - [BookingContractPaymentDetailsSupplierDetails](docs/BookingContractPaymentDetailsSupplierDetails.md)
 - [BookingContractSupplierDetails](docs/BookingContractSupplierDetails.md)
 - [BookingItineraryRoomConfigurationChildSupplierDetails](docs/BookingItineraryRoomConfigurationChildSupplierDetails.md)
 - [BookingItineraryRoomConfigurationSupplierDetails](docs/BookingItineraryRoomConfigurationSupplierDetails.md)
 - [BookingItinerarySupplierDetails](docs/BookingItinerarySupplierDetails.md)
 - [BookingSupplierDetails](docs/BookingSupplierDetails.md)
 - [BookingTestNotificationSupplierDetails](docs/BookingTestNotificationSupplierDetails.md)
 - [BookingTestRequestSupplierDetails](docs/BookingTestRequestSupplierDetails.md)
 - [BookingUserSessionSupplierDetails](docs/BookingUserSessionSupplierDetails.md)
 - [BookingUserSupplierDetails](docs/BookingUserSupplierDetails.md)
 - [BooleanResponseSupplier](docs/BooleanResponseSupplier.md)
 - [CancellationPolicyExceptionSupplierDetails](docs/CancellationPolicyExceptionSupplierDetails.md)
 - [CancellationPolicyExceptionsSupplierDetails](docs/CancellationPolicyExceptionsSupplierDetails.md)
 - [CancellationPolicyLightweightSupplierDetails](docs/CancellationPolicyLightweightSupplierDetails.md)
 - [ChannelNameSupplier](docs/ChannelNameSupplier.md)
 - [ChannelNameSupplierDetails](docs/ChannelNameSupplierDetails.md)
 - [ChildSupplierDetails](docs/ChildSupplierDetails.md)
 - [CityRateQualifierSupplier](docs/CityRateQualifierSupplier.md)
 - [CityRateQualifierSupplierDetails](docs/CityRateQualifierSupplierDetails.md)
 - [CommissionableEntrySupplierDetails](docs/CommissionableEntrySupplierDetails.md)
 - [CompanyDetailsBookingSalesMetricsSupplier](docs/CompanyDetailsBookingSalesMetricsSupplier.md)
 - [CompositeFilterDescriptorSupplier](docs/CompositeFilterDescriptorSupplier.md)
 - [ContactSupplier](docs/ContactSupplier.md)
 - [ContactSupplierDetails](docs/ContactSupplierDetails.md)
 - [ContinentRateQualifierSupplier](docs/ContinentRateQualifierSupplier.md)
 - [ContinentRateQualifierSupplierDetails](docs/ContinentRateQualifierSupplierDetails.md)
 - [CountryLightweightSupplierDetails](docs/CountryLightweightSupplierDetails.md)
 - [CountryRateQualifierSupplier](docs/CountryRateQualifierSupplier.md)
 - [CountryRateQualifierSupplierDetails](docs/CountryRateQualifierSupplierDetails.md)
 - [CreateScheduleItemRequestSupplier](docs/CreateScheduleItemRequestSupplier.md)
 - [CustomMonetaryAmount](docs/CustomMonetaryAmount.md)
 - [CustomizationLightweightSupplierDetails](docs/CustomizationLightweightSupplierDetails.md)
 - [CustomizationThemeColorsSupplierDetails](docs/CustomizationThemeColorsSupplierDetails.md)
 - [DailyRateRateSupplierDetails](docs/DailyRateRateSupplierDetails.md)
 - [DailyRateSupplierDetails](docs/DailyRateSupplierDetails.md)
 - [DateRangeSupplier](docs/DateRangeSupplier.md)
 - [DepartureDaysOfWeekRateQualifierSupplier](docs/DepartureDaysOfWeekRateQualifierSupplier.md)
 - [DepartureDaysOfWeekRateQualifierSupplierDetails](docs/DepartureDaysOfWeekRateQualifierSupplierDetails.md)
 - [DescriptiveReasonSupplierDetails](docs/DescriptiveReasonSupplierDetails.md)
 - [DescriptiveRoomSupplierDetails](docs/DescriptiveRoomSupplierDetails.md)
 - [DescriptiveRoomTypeWithPriceConfigurationsSupplierDetails](docs/DescriptiveRoomTypeWithPriceConfigurationsSupplierDetails.md)
 - [DisplayCompanySupplier](docs/DisplayCompanySupplier.md)
 - [DisplayCompanyWithSalesMetricsSupplier](docs/DisplayCompanyWithSalesMetricsSupplier.md)
 - [DowPatternGroupSupplier](docs/DowPatternGroupSupplier.md)
 - [DowPatternGroupSupplierDetails](docs/DowPatternGroupSupplierDetails.md)
 - [ExtraChargeSupplierDetails](docs/ExtraChargeSupplierDetails.md)
 - [ExtraChargesSupplierDetails](docs/ExtraChargesSupplierDetails.md)
 - [FilterDescriptorSupplier](docs/FilterDescriptorSupplier.md)
 - [GeneralManagerSupplierDetails](docs/GeneralManagerSupplierDetails.md)
 - [GenericErrorMessage](docs/GenericErrorMessage.md)
 - [GeoIpLightweightSupplier](docs/GeoIpLightweightSupplier.md)
 - [GeoIpLightweightSupplierDetails](docs/GeoIpLightweightSupplierDetails.md)
 - [GeoJsonPointSupplier](docs/GeoJsonPointSupplier.md)
 - [GeoJsonPointSupplierDetails](docs/GeoJsonPointSupplierDetails.md)
 - [GeoNameCountrySupplier](docs/GeoNameCountrySupplier.md)
 - [GeoNameCountrySupplierDetails](docs/GeoNameCountrySupplierDetails.md)
 - [GeoNameLightweightSupplierDetails](docs/GeoNameLightweightSupplierDetails.md)
 - [GroupDescriptorSupplier](docs/GroupDescriptorSupplier.md)
 - [GroupedBookingSalesMetricsSupplier](docs/GroupedBookingSalesMetricsSupplier.md)
 - [GuestRoomLightweightSupplierDetails](docs/GuestRoomLightweightSupplierDetails.md)
 - [GuestUserSupplierDetails](docs/GuestUserSupplierDetails.md)
 - [IPRangeRateQualifierSupplier](docs/IPRangeRateQualifierSupplier.md)
 - [IPRangeRateQualifierSupplierDetails](docs/IPRangeRateQualifierSupplierDetails.md)
 - [InventoryAddressSupplier](docs/InventoryAddressSupplier.md)
 - [InventoryAddressSupplierDetails](docs/InventoryAddressSupplierDetails.md)
 - [InventorySupplier](docs/InventorySupplier.md)
 - [InventorySupplierDetails](docs/InventorySupplierDetails.md)
 - [InventoryUpdateRequestSupplier](docs/InventoryUpdateRequestSupplier.md)
 - [InventoryUsageItemSupplier](docs/InventoryUsageItemSupplier.md)
 - [InventoryUsageSupplier](docs/InventoryUsageSupplier.md)
 - [InviteAffiliateRequestSupplier](docs/InviteAffiliateRequestSupplier.md)
 - [KeyValuePairSupplier](docs/KeyValuePairSupplier.md)
 - [LengthOfStayRateQualifierSupplier](docs/LengthOfStayRateQualifierSupplier.md)
 - [LengthOfStayRateQualifierSupplierDetails](docs/LengthOfStayRateQualifierSupplierDetails.md)
 - [LocalizedDescriptionSupplier](docs/LocalizedDescriptionSupplier.md)
 - [LocalizedDescriptionSupplierDetails](docs/LocalizedDescriptionSupplierDetails.md)
 - [LocalizedPriceSupplierDetails](docs/LocalizedPriceSupplierDetails.md)
 - [LocalizedTransactionalTravelInventorySupplierDetails](docs/LocalizedTransactionalTravelInventorySupplierDetails.md)
 - [MasterRateSupplierDetails](docs/MasterRateSupplierDetails.md)
 - [MediaAuthorAttributionSupplier](docs/MediaAuthorAttributionSupplier.md)
 - [MediaAuthorAttributionSupplierDetails](docs/MediaAuthorAttributionSupplierDetails.md)
 - [MinutesBeforeBookingStartDateRateQualifierSupplier](docs/MinutesBeforeBookingStartDateRateQualifierSupplier.md)
 - [MinutesBeforeBookingStartDateRateQualifierSupplierDetails](docs/MinutesBeforeBookingStartDateRateQualifierSupplierDetails.md)
 - [PageDisplayCompanyWithSalesMetricsSupplier](docs/PageDisplayCompanyWithSalesMetricsSupplier.md)
 - [PageInventorySupplier](docs/PageInventorySupplier.md)
 - [PageRateSupplier](docs/PageRateSupplier.md)
 - [PageableObjectSupplier](docs/PageableObjectSupplier.md)
 - [PayoutFeeSupplierDetails](docs/PayoutFeeSupplierDetails.md)
 - [PayoutSupplierDetails](docs/PayoutSupplierDetails.md)
 - [PerkLightweightSupplierDetails](docs/PerkLightweightSupplierDetails.md)
 - [PersonalSupplierDetails](docs/PersonalSupplierDetails.md)
 - [PreferencesSupplierDetails](docs/PreferencesSupplierDetails.md)
 - [PrepayRateQualifierSupplier](docs/PrepayRateQualifierSupplier.md)
 - [PrepayRateQualifierSupplierDetails](docs/PrepayRateQualifierSupplierDetails.md)
 - [ProfileLightweightSupplierDetails](docs/ProfileLightweightSupplierDetails.md)
 - [ProfileUserSupplierDetails](docs/ProfileUserSupplierDetails.md)
 - [PromotionRateQualifierSupplier](docs/PromotionRateQualifierSupplier.md)
 - [PromotionRateQualifierSupplierDetails](docs/PromotionRateQualifierSupplierDetails.md)
 - [PropertyAggregateLightweightSupplierDetails](docs/PropertyAggregateLightweightSupplierDetails.md)
 - [PropertyPolicySupplierDetails](docs/PropertyPolicySupplierDetails.md)
 - [QuoteLightweightSupplierDetails](docs/QuoteLightweightSupplierDetails.md)
 - [RateKeySupplier](docs/RateKeySupplier.md)
 - [RatePlanLevelFeeSupplierDetails](docs/RatePlanLevelFeeSupplierDetails.md)
 - [RatePlanLightweightSupplierDetails](docs/RatePlanLightweightSupplierDetails.md)
 - [RateSupplier](docs/RateSupplier.md)
 - [RefundSupplierDetails](docs/RefundSupplierDetails.md)
 - [RefundableRateQualifierSupplier](docs/RefundableRateQualifierSupplier.md)
 - [RefundableRateQualifierSupplierDetails](docs/RefundableRateQualifierSupplierDetails.md)
 - [RequiredDaysOfWeekRateQualifierSupplier](docs/RequiredDaysOfWeekRateQualifierSupplier.md)
 - [RequiredDaysOfWeekRateQualifierSupplierDetails](docs/RequiredDaysOfWeekRateQualifierSupplierDetails.md)
 - [ReviewAnswerSupplierDetails](docs/ReviewAnswerSupplierDetails.md)
 - [ReviewLightweightSupplierDetails](docs/ReviewLightweightSupplierDetails.md)
 - [ReviewUserSupplierDetails](docs/ReviewUserSupplierDetails.md)
 - [RoomConfigurationPriceRatePlanSupplierDetails](docs/RoomConfigurationPriceRatePlanSupplierDetails.md)
 - [RoomConfigurationPriceSupplierDetails](docs/RoomConfigurationPriceSupplierDetails.md)
 - [RoomConfigurationSupplierDetails](docs/RoomConfigurationSupplierDetails.md)
 - [RoomRangeRateQualifierSupplier](docs/RoomRangeRateQualifierSupplier.md)
 - [RoomRangeRateQualifierSupplierDetails](docs/RoomRangeRateQualifierSupplierDetails.md)
 - [RoomStaySupplierDetails](docs/RoomStaySupplierDetails.md)
 - [RoomTypeLightweightSupplierDetails](docs/RoomTypeLightweightSupplierDetails.md)
 - [SalesChannelCreateRequestSupplier](docs/SalesChannelCreateRequestSupplier.md)
 - [SalesChannelLightweightSupplier](docs/SalesChannelLightweightSupplier.md)
 - [SalesChannelLightweightSupplierDetails](docs/SalesChannelLightweightSupplierDetails.md)
 - [SalesChannelRequestSupplier](docs/SalesChannelRequestSupplier.md)
 - [SalesChannelSupplier](docs/SalesChannelSupplier.md)
 - [SalesChannelUpdateRequestSupplier](docs/SalesChannelUpdateRequestSupplier.md)
 - [ScheduleItemSupplier](docs/ScheduleItemSupplier.md)
 - [SelectableKeyValuePairSupplier](docs/SelectableKeyValuePairSupplier.md)
 - [SellDateRateQualifierSupplier](docs/SellDateRateQualifierSupplier.md)
 - [SellDateRateQualifierSupplierDetails](docs/SellDateRateQualifierSupplierDetails.md)
 - [ShowInventory400Response](docs/ShowInventory400Response.md)
 - [SimpleAddressSupplier](docs/SimpleAddressSupplier.md)
 - [SimpleAddressSupplierDetails](docs/SimpleAddressSupplierDetails.md)
 - [SimpleDateTimeItinerarySupplierDetails](docs/SimpleDateTimeItinerarySupplierDetails.md)
 - [SimpleDescriptionSupplier](docs/SimpleDescriptionSupplier.md)
 - [SimpleDescriptionSupplierDetails](docs/SimpleDescriptionSupplierDetails.md)
 - [SimpleMultimediaSupplier](docs/SimpleMultimediaSupplier.md)
 - [SimpleMultimediaSupplierDetails](docs/SimpleMultimediaSupplierDetails.md)
 - [SocialSupplierDetails](docs/SocialSupplierDetails.md)
 - [SortDescriptorSupplier](docs/SortDescriptorSupplier.md)
 - [SortObjectSupplier](docs/SortObjectSupplier.md)
 - [SpecialRateBundleLightweightSupplier](docs/SpecialRateBundleLightweightSupplier.md)
 - [SpecialRateBundleLightweightSupplierDetails](docs/SpecialRateBundleLightweightSupplierDetails.md)
 - [SpecialRateLightweightSupplier](docs/SpecialRateLightweightSupplier.md)
 - [SpecialRateLightweightSupplierDetails](docs/SpecialRateLightweightSupplierDetails.md)
 - [StateSupplier](docs/StateSupplier.md)
 - [StayDateRateQualifierSupplier](docs/StayDateRateQualifierSupplier.md)
 - [StayDateRateQualifierSupplierDetails](docs/StayDateRateQualifierSupplierDetails.md)
 - [StayRateSupplierDetails](docs/StayRateSupplierDetails.md)
 - [SubCountryLightweightSupplierDetails](docs/SubCountryLightweightSupplierDetails.md)
 - [SubSubCountryLightweightSupplierDetails](docs/SubSubCountryLightweightSupplierDetails.md)
 - [SupplierContractItemPolicySupplierDetails](docs/SupplierContractItemPolicySupplierDetails.md)
 - [TimezoneRateQualifierSupplier](docs/TimezoneRateQualifierSupplier.md)
 - [TimezoneRateQualifierSupplierDetails](docs/TimezoneRateQualifierSupplierDetails.md)
 - [TransactionalTravelInventorySupplierDetails](docs/TransactionalTravelInventorySupplierDetails.md)
 - [TravelAgentSupplier](docs/TravelAgentSupplier.md)
 - [TravelInventoryRecognitionSupplierDetails](docs/TravelInventoryRecognitionSupplierDetails.md)
 - [UpdateScheduleItemRequestSupplier](docs/UpdateScheduleItemRequestSupplier.md)
 - [UpsertBulkRateRequestSupplier](docs/UpsertBulkRateRequestSupplier.md)
 - [UpsertIndividualRateRequestSupplier](docs/UpsertIndividualRateRequestSupplier.md)
 - [UpsertIndividualRateRequestWrapperSupplier](docs/UpsertIndividualRateRequestWrapperSupplier.md)
 - [UpsertSalesChannelRequestRequestSupplier](docs/UpsertSalesChannelRequestRequestSupplier.md)
 - [VariableChargeSupplier](docs/VariableChargeSupplier.md)
 - [VariableChargeSupplierDetails](docs/VariableChargeSupplierDetails.md)
 - [VerifyRatesRequestSupplierDetails](docs/VerifyRatesRequestSupplierDetails.md)


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


