# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/engine-client): A single endpoint to retrieve whitelabel + customization information for the booking engine.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Extranet Distribution API The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink. This API lets you:  1. Verifier: Test your availability and promotions and create test bookings to simulate the entire booking workflow. 2. Sales Channels: Manage your sales channels. 3. Explore Network: Find new affiliates to work with. 4. Inventory: Manage inventory at the sales channel-level. 5. Calendars: Manage availability calendars for all your inventory.  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.5.19
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from wink_sdk_extranet_distribution.models.master_rate_supplier_details import MasterRateSupplierDetails

class TestMasterRateSupplierDetails(unittest.TestCase):
    """MasterRateSupplierDetails unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> MasterRateSupplierDetails:
        """Test MasterRateSupplierDetails
            include_optional is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `MasterRateSupplierDetails`
        """
        model = MasterRateSupplierDetails()
        if include_optional:
            return MasterRateSupplierDetails(
                identifier = '',
                hotel_identifier = '',
                name = 'Premium King - BAR',
                guest_room_identifier = '',
                rate_plan_identifier = '',
                room = wink_sdk_extranet_distribution.models.guest_room_supplier_details.GuestRoom_SupplierDetails(
                    identifier = '', 
                    hotel_identifier = '', 
                    featured_ind = False, 
                    lifestyle_type = 'LIFESTYLE_HEALTH_FITNESS', 
                    location = {"type":"POINT","coordinates":[100.5581533,13.7370197]}, 
                    descriptions = [
                        wink_sdk_extranet_distribution.models.simple_description_supplier_details.SimpleDescription_SupplierDetails(
                            name = 'An example title', 
                            description = 'This is a longer description in the specified language.', 
                            language = 'en', )
                        ], 
                    multimedias = [
                        cl-image-1
                        ], 
                    contact = wink_sdk_extranet_distribution.models.contact_supplier_details.Contact_SupplierDetails(
                        first_name = 'John', 
                        last_name = 'Smith', 
                        email = 'johnsmith@email.com', 
                        secondary_email = 'johnsmith2@email.com', 
                        phone_number = '+12125551212', 
                        full_name = 'John Smith', 
                        summary = 'John Smith (johnsmith@gmail.com / +12125551212)', ), 
                    address = wink_sdk_extranet_distribution.models.address_supplier_details.Address_SupplierDetails(
                        address1 = '234 Near da beach', 
                        address2 = 'Pebble #5001', 
                        state = 'CA', 
                        postal_code = '90210', 
                        county = 'Alameda county', 
                        city = wink_sdk_extranet_distribution.models.geo_name_supplier_details.GeoName_SupplierDetails(
                            geo_name_id = '5128581', 
                            type = 'CITY', 
                            name = 'New York City', 
                            url_name = 'new-york-city-united-states', 
                            ascii_name = 'New York City', 
                            feature_code = '', 
                            country_code = '', 
                            timezone = 'America/New_York', 
                            country = wink_sdk_extranet_distribution.models.country_supplier_details.Country_SupplierDetails(
                                iso = 'US', 
                                name = 'United States', 
                                capital = 'Washington', 
                                continent = 'NA', 
                                currency_code = 'USD', 
                                currency_name = 'Dollar', 
                                geo_name_id = '6252001', ), 
                            sub_country = wink_sdk_extranet_distribution.models.sub_country_supplier_details.SubCountry_SupplierDetails(
                                name = 'New York', 
                                ascii_name = 'New York', 
                                geo_name_id = '5128638', ), 
                            sub_sub_country = wink_sdk_extranet_distribution.models.sub_sub_country_supplier_details.SubSubCountry_SupplierDetails(
                                name = '', 
                                ascii_name = '', 
                                geo_name_id = '', ), ), 
                        valid = True, 
                        full_address = '11 At home, Suite 3C, New York City, NY 10010, United States', ), 
                    commissionable = True, 
                    name = 'Archery lesson', 
                    proximity_code = '1', 
                    sort = 1, 
                    min_age_appropriate_code = '1', 
                    bookable = True, 
                    active = True, 
                    disability_features = ["1"], 
                    security_features = ["1"], 
                    socials = [
                        wink_sdk_extranet_distribution.models.social_supplier_details.Social_SupplierDetails(
                            type = 'FACEBOOK', 
                            enabled = True, )
                        ], 
                    price_point = 'THREE', 
                    recognition_list = [
                        wink_sdk_extranet_distribution.models.travel_inventory_recognition_supplier_details.TravelInventoryRecognition_SupplierDetails(
                            identifier = '', 
                            category = 'AWARD', 
                            type = 'PERCENT_RATING', 
                            provider = 'Michelin', 
                            rating = 8.5, 
                            max_rating = 10, 
                            date = 'Sat Oct 24 07:00:00 ICT 2020', 
                            official_appointment_ind = True, 
                            rating_symbol = '*', )
                        ], 
                    transactional_inventory_list = [
                        wink_sdk_extranet_distribution.models.transactional_travel_inventory_supplier_details.TransactionalTravelInventory_SupplierDetails(
                            identifier = '', 
                            name = '1 hour session', 
                            descriptions = [
                                wink_sdk_extranet_distribution.models.simple_description_supplier_details.SimpleDescription_SupplierDetails(
                                    name = 'An example title', 
                                    description = 'This is a longer description in the specified language.', 
                                    language = 'en', )
                                ], 
                            pricing_type = 'PER_STAY', 
                            base_price = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                                amount = 1.337, 
                                currency = '', ), 
                            discounted_price = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                                amount = 1.337, 
                                currency = '', ), 
                            min_pax = 2, 
                            max_pax = 10, 
                            percent_premium = 0.1, 
                            percent_discount = 0.1, )
                        ], 
                    max_occupancy = 2, 
                    min_occupancy = 1, 
                    quantity = 40, 
                    non_smoking = True, 
                    bedroom_configuration_list = [
                        wink_sdk_extranet_distribution.models.bedroom_configuration_supplier_details.BedroomConfiguration_SupplierDetails(
                            identifier = '', 
                            name = '', 
                            bedroom_list = [
                                wink_sdk_extranet_distribution.models.bedroom_supplier_details.Bedroom_SupplierDetails(
                                    type = 'MASTER', 
                                    bed_list = [
                                        wink_sdk_extranet_distribution.models.bed_supplier_details.Bed_SupplierDetails(
                                            bed_type_code = '1', 
                                            quantity = 10, )
                                        ], )
                                ], )
                        ], 
                    size = 55, 
                    max_adult_occupancy = 1, 
                    max_child_occupancy = 0, 
                    bathroom_count = 0, 
                    living_room_count = 0, 
                    max_rollaways = 0, 
                    room_category = '1', 
                    floor = '', 
                    room_location_code = '1', 
                    room_view_code = '1', 
                    composite = False, 
                    composite_count = 2, 
                    room_classification_code = '1', 
                    room_architecture_code = '1', 
                    room_gender = 'Unknown', 
                    shared_room_ind = False, 
                    max_cribs = 1, 
                    amenities = ["1","7"], 
                    included_adult_occupancy = 2, 
                    included_child_occupancy = 0, 
                    base_rate = , 
                    min_rate = , ),
                rate_plan = wink_sdk_extranet_distribution.models.rate_plan_supplier_details.RatePlan_SupplierDetails(
                    identifier = '', 
                    hotel_identifier = '', 
                    name = 'BAR 1', 
                    prepaid = False, 
                    enabled = False, 
                    breakfast = False, 
                    brunch = False, 
                    lunch = False, 
                    dinner = False, 
                    all_inclusive = False, 
                    all_inclusive_plus_alcohol = False, 
                    sell_start_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                    sell_end_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                    stay_start_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                    stay_end_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                    loyalty_points_accrue = False, 
                    max_advance_booking_offset = 10, 
                    min_advance_booking_offset = 3, 
                    min_total_occupancy = 4, 
                    max_total_occupancy = 4, 
                    min_los = 3, 
                    max_los = 5, 
                    min_age = 26, 
                    max_age = 50, 
                    rate_plan_level_fees = [
                        wink_sdk_extranet_distribution.models.rate_plan_level_fee_supplier_details.RatePlanLevelFee_SupplierDetails(
                            descriptions = [
                                wink_sdk_extranet_distribution.models.localized_description_supplier_details.LocalizedDescription_SupplierDetails(
                                    description = 'This is a longer description in the specified language.', 
                                    language = 'en', )
                                ], 
                            fixed_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                                amount = 1.337, 
                                currency = '', ), 
                            type = 'PER_DAY', )
                        ], 
                    available_days_of_week = wink_sdk_extranet_distribution.models.dow_pattern_group_supplier_details.DowPatternGroup_SupplierDetails(
                        mon = True, 
                        tue = True, 
                        wed = True, 
                        thu = True, 
                        fri = True, 
                        sat = True, 
                        sun = True, 
                        disabled = True, ), 
                    arrival_days_of_week = wink_sdk_extranet_distribution.models.dow_pattern_group_supplier_details.DowPatternGroup_SupplierDetails(
                        mon = True, 
                        tue = True, 
                        wed = True, 
                        thu = True, 
                        fri = True, 
                        sat = True, 
                        sun = True, 
                        disabled = True, ), 
                    departure_days_of_week = , 
                    required_days_of_week = , 
                    early_check_in_charge = wink_sdk_extranet_distribution.models.variable_charge_supplier_details.VariableCharge_SupplierDetails(
                        type = 'FIXED', 
                        percent = 0.25, ), 
                    late_check_out_charge = wink_sdk_extranet_distribution.models.variable_charge_supplier_details.VariableCharge_SupplierDetails(
                        type = 'FIXED', 
                        percent = 0.25, ), 
                    cancellation_policy_identifier = 'cancellation-policy-1', 
                    cancellation_policy = wink_sdk_extranet_distribution.models.cancellation_policy_supplier_details.CancellationPolicy_SupplierDetails(
                        identifier = '', 
                        hotel_identifier = '', 
                        refundable = False, 
                        advance_cancellation_free_of_charge = 'UNTIL_EIGHTEEN_HUNDRED_HOURS_ON_DAY_OF_ARRIVAL', 
                        refundable_cancellation_charge = 'FIFTY_PERCENT', 
                        no_show_charge = 'SAME_AS_CANCELLATION_FEE', 
                        non_refundable_cancellation_charge = 'SEVENTY_PERCENT', 
                        non_refundable_deadline = 'SEVEN_DAYS_BEFORE_ARRIVAL', 
                        non_refundable_after_deadline_cancellation_charge = 'ONE_HUNDRED_PERCENT', 
                        policy_code = '', ), 
                    cancellation_policy_exceptions = wink_sdk_extranet_distribution.models.cancellation_policy_exceptions_supplier_details.CancellationPolicyExceptions_SupplierDetails(
                        list = [
                            wink_sdk_extranet_distribution.models.cancellation_policy_exception_supplier_details.CancellationPolicyException_SupplierDetails(
                                cancellation_policy_identifier = '', 
                                cancellation_policy = wink_sdk_extranet_distribution.models.cancellation_policy_supplier_details.CancellationPolicy_SupplierDetails(
                                    identifier = '', 
                                    hotel_identifier = '', 
                                    refundable = False, 
                                    advance_cancellation_free_of_charge = 'UNTIL_EIGHTEEN_HUNDRED_HOURS_ON_DAY_OF_ARRIVAL', 
                                    refundable_cancellation_charge = 'FIFTY_PERCENT', 
                                    no_show_charge = 'SAME_AS_CANCELLATION_FEE', 
                                    non_refundable_cancellation_charge = 'SEVENTY_PERCENT', 
                                    non_refundable_deadline = 'SEVEN_DAYS_BEFORE_ARRIVAL', 
                                    non_refundable_after_deadline_cancellation_charge = 'ONE_HUNDRED_PERCENT', 
                                    policy_code = '', ), 
                                start_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                                end_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), )
                            ], ), 
                    single_occupancy_rate_modifier = , 
                    extra_pax_rate_modifier = , 
                    extra_child_rate_modifier = , ),
                enabled = True,
                perk_types = [
                    'PERK_WINE'
                    ],
                perks_value = 56
            )
        else:
            return MasterRateSupplierDetails(
                guest_room_identifier = '',
                rate_plan_identifier = '',
                enabled = True,
        )
        """

    def testMasterRateSupplierDetails(self):
        """Test MasterRateSupplierDetails"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
