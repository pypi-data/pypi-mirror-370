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

from wink_sdk_extranet_distribution.models.descriptive_room_supplier_details import DescriptiveRoomSupplierDetails

class TestDescriptiveRoomSupplierDetails(unittest.TestCase):
    """DescriptiveRoomSupplierDetails unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> DescriptiveRoomSupplierDetails:
        """Test DescriptiveRoomSupplierDetails
            include_optional is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `DescriptiveRoomSupplierDetails`
        """
        model = DescriptiveRoomSupplierDetails()
        if include_optional:
            return DescriptiveRoomSupplierDetails(
                identifier = '',
                room_name = '',
                accessible_master_rates = [
                    wink_sdk_extranet_distribution.models.master_rate_supplier_details.MasterRate_SupplierDetails(
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
                                    fixed_amount = , 
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
                        perks_value = 56, )
                    ],
                inaccessible_master_rates = [
                    wink_sdk_extranet_distribution.models.descriptive_reason_supplier_details.DescriptiveReason_SupplierDetails(
                        identifier = '', 
                        name = '', 
                        map = {
                            'key' : ''
                            }, 
                        reasons = [
                            ''
                            ], )
                    ],
                accessible_inventory = [
                    wink_sdk_extranet_distribution.models.inventory_supplier_details.Inventory_SupplierDetails(
                        identifier = '', 
                        sales_channel = wink_sdk_extranet_distribution.models.sales_channel_supplier_details.SalesChannel_SupplierDetails(
                            identifier = '', 
                            supplier_identifier = '', 
                            supplier_name = 'Hotel 1', 
                            supplier_available = True, 
                            sub_type = 'DIRECT', 
                            owner_identifier = '', 
                            owner_name = 'Owner 1', 
                            enabled = True, 
                            channel_disabled = True, 
                            blacklisted = True, 
                            percent_discount = 0.15, 
                            commission = 0.2, 
                            rate_modifiers = [
                                wink_sdk_extranet_distribution.models.rate_modifier_supplier_details.RateModifier_SupplierDetails(
                                    identifier = '', 
                                    hotel_identifier = '', 
                                    name = 'Early bird', 
                                    type = 'DISCOUNT', 
                                    modifier = wink_sdk_extranet_distribution.models.variable_charge_supplier_details.VariableCharge_SupplierDetails(
                                        type = 'FIXED', 
                                        percent = 0.25, 
                                        fixed_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                                            amount = 1.337, 
                                            currency = '', ), ), 
                                    enabled = True, 
                                    pricing_type = 'PER_PERSON_PER_NIGHT', 
                                    descriptions = [
                                        wink_sdk_extranet_distribution.models.localized_description_supplier_details.LocalizedDescription_SupplierDetails(
                                            description = 'This is a longer description in the specified language.', 
                                            language = 'en', )
                                        ], 
                                    city_rate_qualifiers = [
                                        wink_sdk_extranet_distribution.models.city_rate_qualifier_supplier_details.CityRateQualifier_SupplierDetails(
                                            city = wink_sdk_extranet_distribution.models.geo_ip_supplier_details.GeoIP_SupplierDetails(
                                                geo_name_id = '8798734', 
                                                locale_code = 'en', 
                                                continent_code = 'NA', 
                                                continent_name = 'North America', 
                                                country_iso_code = 'US', 
                                                country_name = 'United States', 
                                                city_name = 'New York', 
                                                timezone = 'America/New_York', 
                                                sub_division1_code = 'NY', 
                                                sub_division1_name = 'NY', 
                                                sub_division2_code = '', 
                                                sub_division2_name = '', ), )
                                        ], 
                                    continent_rate_qualifiers = [
                                        wink_sdk_extranet_distribution.models.continent_rate_qualifier_supplier_details.ContinentRateQualifier_SupplierDetails(
                                            continent = 'NA', )
                                        ], 
                                    country_rate_qualifiers = [
                                        wink_sdk_extranet_distribution.models.country_rate_qualifier_supplier_details.CountryRateQualifier_SupplierDetails(
                                            country = wink_sdk_extranet_distribution.models.geo_name_country_supplier_details.GeoNameCountry_SupplierDetails(
                                                geo_name_id = '', 
                                                continent_code = '', 
                                                continent_name = '', 
                                                country_iso_code = '', 
                                                country_name = '', ), )
                                        ], 
                                    promotion_rate_qualifiers = [
                                        wink_sdk_extranet_distribution.models.promotion_rate_qualifier_supplier_details.PromotionRateQualifier_SupplierDetails(
                                            promotion = 'NA', )
                                        ], 
                                    ip_range_rate_qualifiers = [
                                        wink_sdk_extranet_distribution.models.ip_range_rate_qualifier_supplier_details.IPRangeRateQualifier_SupplierDetails(
                                            start_ip_range = '', 
                                            end_ip_range = '', )
                                        ], 
                                    room_range_rate_qualifier = wink_sdk_extranet_distribution.models.room_range_rate_qualifier_supplier_details.RoomRangeRateQualifier_SupplierDetails(
                                        min_rooms = 1, 
                                        max_rooms = 56, ), 
                                    prepay_rate_qualifier = wink_sdk_extranet_distribution.models.prepay_rate_qualifier_supplier_details.PrepayRateQualifier_SupplierDetails(
                                        prepay = True, ), 
                                    refundable_rate_qualifier = wink_sdk_extranet_distribution.models.refundable_rate_qualifier_supplier_details.RefundableRateQualifier_SupplierDetails(
                                        refundable = True, ), 
                                    timezone_rate_qualifiers = [
                                        wink_sdk_extranet_distribution.models.timezone_rate_qualifier_supplier_details.TimezoneRateQualifier_SupplierDetails(
                                            timezone = '', )
                                        ], 
                                    last_minute_rate_qualifier = wink_sdk_extranet_distribution.models.minutes_before_booking_start_date_rate_qualifier_supplier_details.MinutesBeforeBookingStartDateRateQualifier_SupplierDetails(
                                        seconds = 0, ), 
                                    length_of_stay_rate_qualifier = wink_sdk_extranet_distribution.models.length_of_stay_rate_qualifier_supplier_details.LengthOfStayRateQualifier_SupplierDetails(
                                        min_los = 0, 
                                        max_los = 0, ), 
                                    advance_booking_rate_qualifier = wink_sdk_extranet_distribution.models.advance_booking_rate_qualifier_supplier_details.AdvanceBookingRateQualifier_SupplierDetails(
                                        min_advance_booking_offset = 0, 
                                        max_advance_booking_offset = 0, ), 
                                    stay_date_rate_qualifiers = [
                                        wink_sdk_extranet_distribution.models.stay_date_rate_qualifier_supplier_details.StayDateRateQualifier_SupplierDetails(
                                            effective_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                                            expire_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), )
                                        ], 
                                    sell_date_rate_qualifiers = [
                                        wink_sdk_extranet_distribution.models.sell_date_rate_qualifier_supplier_details.SellDateRateQualifier_SupplierDetails(
                                            effective_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                                            expire_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), )
                                        ], 
                                    available_days_of_week_rate_qualifier = wink_sdk_extranet_distribution.models.available_days_of_week_rate_qualifier_supplier_details.AvailableDaysOfWeekRateQualifier_SupplierDetails(
                                        days_of_week = wink_sdk_extranet_distribution.models.dow_pattern_group_supplier_details.DowPatternGroup_SupplierDetails(
                                            mon = True, 
                                            tue = True, 
                                            wed = True, 
                                            thu = True, 
                                            fri = True, 
                                            sat = True, 
                                            sun = True, 
                                            disabled = True, ), ), 
                                    arrival_days_of_week_rate_qualifier = wink_sdk_extranet_distribution.models.arrival_days_of_week_rate_qualifier_supplier_details.ArrivalDaysOfWeekRateQualifier_SupplierDetails(
                                        days_of_week = wink_sdk_extranet_distribution.models.dow_pattern_group_supplier_details.DowPatternGroup_SupplierDetails(
                                            mon = True, 
                                            tue = True, 
                                            wed = True, 
                                            thu = True, 
                                            fri = True, 
                                            sat = True, 
                                            sun = True, 
                                            disabled = True, ), ), 
                                    departure_days_of_week_rate_qualifier = wink_sdk_extranet_distribution.models.departure_days_of_week_rate_qualifier_supplier_details.DepartureDaysOfWeekRateQualifier_SupplierDetails(
                                        days_of_week = , ), 
                                    required_days_of_week_rate_qualifier = wink_sdk_extranet_distribution.models.required_days_of_week_rate_qualifier_supplier_details.RequiredDaysOfWeekRateQualifier_SupplierDetails(
                                        days_of_week = , ), 
                                    master_rate_identifiers = ["master-rate-1","master-rate-2"], 
                                    add_on_identifiers = ["add-on-1","add-on-2"], 
                                    rate_plan_identifiers = ["rate-plan-1","rate-plan-2"], 
                                    blackout_dates = [
                                        wink_sdk_extranet_distribution.models.blackout_date_supplier_details.BlackoutDate_SupplierDetails(
                                            effective_date = 'Wed Jan 01 07:00:00 ICT 2020', 
                                            expire_date = 'Fri Jan 31 07:00:00 ICT 2020', )
                                        ], )
                                ], 
                            rate_modifier_bundles = [
                                wink_sdk_extranet_distribution.models.rate_modifier_bundle_supplier_details.RateModifierBundle_SupplierDetails(
                                    identifier = '', 
                                    hotel_identifier = '', 
                                    name = 'Early bird - Long Term', 
                                    enabled = True, 
                                    items = [
                                        wink_sdk_extranet_distribution.models.rate_modifier_supplier_details.RateModifier_SupplierDetails(
                                            identifier = '', 
                                            hotel_identifier = '', 
                                            name = 'Early bird', 
                                            type = 'DISCOUNT', 
                                            modifier = wink_sdk_extranet_distribution.models.variable_charge_supplier_details.VariableCharge_SupplierDetails(
                                                type = 'FIXED', 
                                                percent = 0.25, ), 
                                            enabled = True, 
                                            pricing_type = 'PER_PERSON_PER_NIGHT', 
                                            descriptions = [
                                                wink_sdk_extranet_distribution.models.localized_description_supplier_details.LocalizedDescription_SupplierDetails(
                                                    description = 'This is a longer description in the specified language.', 
                                                    language = 'en', )
                                                ], 
                                            master_rate_identifiers = ["master-rate-1","master-rate-2"], 
                                            add_on_identifiers = ["add-on-1","add-on-2"], 
                                            rate_plan_identifiers = ["rate-plan-1","rate-plan-2"], )
                                        ], 
                                    modifier_override = , 
                                    type = 'DISCOUNT', 
                                    pricing_type = 'PER_STAY', 
                                    has_fixed_discount_modifier = True, 
                                    has_percent_discount_modifier = True, 
                                    is_valid = True, 
                                    description = [
                                        
                                        ], )
                                ], ), 
                        inventory_type = 'GUEST_ROOM', 
                        inventory_identifier = '', 
                        inventory_name = '', 
                        inventory_name_in_english = '', 
                        enabled = True, 
                        image_identifier = '', 
                        price_point = 'THREE', 
                        location = {"type":"POINT","coordinates":[100.5581533,13.7370197]}, 
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
                        quantity = 100, 
                        commissionable = True, 
                        bookable = True, 
                        lowest_price = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                            amount = 1.337, 
                            currency = '', ), 
                        lowest_display_price = , 
                        hotel = wink_sdk_extranet_distribution.models.hotel_on_map_supplier_details.HotelOnMap_SupplierDetails(
                            identifier = 'document-1', 
                            hotel_identifier = '', 
                            name = 'The Loveliest Hotel', 
                            local_name = 'Det Beste Hotellet', 
                            chain = 'Hotel chain', 
                            brand = 'Hotel brand', 
                            url_name = 'the-loveliest-hotel-new-york-united-states', 
                            star_rating = 4, 
                            bookings = 6054, 
                            aggregate_review_rating = 7.8, 
                            short_descriptions = [
                                
                                ], 
                            long_descriptions = [
                                
                                ], 
                            aggregate_greendex_rating = 7.0, 
                            lifestyle_types = [
                                'LIFESTYLE_HEALTH_FITNESS'
                                ], 
                            total_reviews = 989, 
                            available = True, 
                            hotel_available = True, 
                            reservations = wink_sdk_extranet_distribution.models.contact_supplier_details.Contact_SupplierDetails(
                                first_name = 'John', 
                                last_name = 'Smith', 
                                email = 'johnsmith@email.com', 
                                secondary_email = 'johnsmith2@email.com', 
                                phone_number = '+12125551212', 
                                full_name = 'John Smith', 
                                summary = 'John Smith (johnsmith@gmail.com / +12125551212)', ), 
                            socials = [
                                wink_sdk_extranet_distribution.models.social_supplier_details.Social_SupplierDetails(
                                    type = 'FACEBOOK', 
                                    enabled = True, )
                                ], 
                            images = [
                                cl-image-1
                                ], 
                            videos = [
                                cl-image-1
                                ], 
                            policy = wink_sdk_extranet_distribution.models.property_policy_supplier_details.PropertyPolicy_SupplierDetails(
                                children_allowed = True, 
                                children_minimum_age = 6, 
                                internet_availability = 'YES', 
                                internet_connection_type = 'WIFI', 
                                internet_connection_location = 'ENTIRE_PROPERTY', 
                                parking_availability = 'YES', 
                                parking_access = 'PRIVATE', 
                                pets_allowed = True, 
                                pet_max_weight_in_kilos = 10, 
                                pet_charge = , 
                                check_out_time = '10:00', 
                                check_in_time = '14:00', ), 
                            third_party_reviews = [
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
                            attractions = 5, 
                            recreations = 3, 
                            pois = 9, 
                            restaurants = 2, 
                            meeting_rooms = 2, 
                            spas = 1, 
                            add_ons = 5, 
                            general_manager = wink_sdk_extranet_distribution.models.general_manager_supplier_details.GeneralManager_SupplierDetails(
                                name = 'Jane Doe', 
                                image = cl-image-1, ), 
                            location_category = '34', 
                            segment_category = '7', 
                            hotel_category = '45', 
                            architectural_style = '7', 
                            when_built = '1927', 
                            currency_code = 'USD', 
                            membership_rate_discount = 9, 
                            price_score = 9, 
                            perk_score = 4, 
                            package_score = 4, 
                            loyalty_score = 5, 
                            popular_score = 45, 
                            experience_score = 5, 
                            availability_score = 5, 
                            views = 10432, 
                            hotel_amenity_codes = ["1","7"], 
                            property_accessibility_codes = ["1","7"], 
                            property_security_codes = ["1","7"], 
                            number_of_rooms = 32, 
                            active = True, 
                            url_parameters = '', ), )
                    ],
                accessible_rate_plans = [
                    wink_sdk_extranet_distribution.models.descriptive_reason_supplier_details.DescriptiveReason_SupplierDetails(
                        identifier = '', 
                        name = '', 
                        map = {
                            'key' : ''
                            }, 
                        reasons = [
                            ''
                            ], )
                    ],
                inaccessible_rate_plans = [
                    wink_sdk_extranet_distribution.models.descriptive_reason_supplier_details.DescriptiveReason_SupplierDetails(
                        identifier = '', 
                        name = '', 
                        map = {
                            'key' : ''
                            }, 
                        reasons = [
                            ''
                            ], )
                    ],
                accessible_availability = [
                    wink_sdk_extranet_distribution.models.descriptive_room_type_with_price_configurations_supplier_details.DescriptiveRoomTypeWithPriceConfigurations_SupplierDetails(
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
                        available = True, 
                        best_price = wink_sdk_extranet_distribution.models.room_configuration_price_supplier_details.RoomConfigurationPrice_SupplierDetails(
                            adults = 56, 
                            children = 56, 
                            start_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                            end_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                            room_rate_identifier = '', 
                            room_rate_internal_name = '', 
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
                                        fixed_amount = , 
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
                            perk_types = [
                                'PERK_LOYALTY_POINTS'
                                ], 
                            price = wink_sdk_extranet_distribution.models.stay_rate_supplier_details.StayRate_SupplierDetails(
                                user_specified_currency_base_total = , 
                                source_base_total = , 
                                internal_base_total = , 
                                source_extra_pax_modifier = 15, 
                                internal_extra_pax_modifier = 15, 
                                user_specified_currency_extra_pax_modifier = 15, 
                                source_extra_child_modifier = 15, 
                                internal_extra_child_modifier = 15, 
                                user_specified_currency_extra_child_modifier = 15, 
                                source_single_occupant_modifier = -15, 
                                internal_single_occupant_modifier = -15, 
                                user_specified_currency_single_occupant_modifier = -15, 
                                source_promotional_modifier = -40, 
                                internal_promotional_modifier = -40, 
                                user_specified_currency_promotional_modifier = -40, 
                                source_premium_modifier = 40, 
                                internal_premium_modifier = 40, 
                                user_specified_currency_premium_modifier = 40, 
                                source_channel_modifier = -10, 
                                internal_channel_modifier = -10, 
                                user_specified_currency_channel_modifier = -10, 
                                quantity = 56, 
                                min_occupancy = 56, 
                                max_occupancy = 56, 
                                rate_source = '', 
                                promotional_discount_percent = 1.337, 
                                channel_discount_percent = 1.337, 
                                premium_percent = 1.337, 
                                available = True, 
                                source_to_user_currency_quote = wink_sdk_extranet_distribution.models.quote_supplier_details.Quote_SupplierDetails(
                                    source = '', 
                                    target = '', 
                                    exchange_rate = 1.337, 
                                    timestamp = 56, ), 
                                source_to_internal_currency_quote = wink_sdk_extranet_distribution.models.quote_supplier_details.Quote_SupplierDetails(
                                    source = '', 
                                    target = '', 
                                    exchange_rate = 1.337, 
                                    timestamp = 56, ), 
                                offer_details = [
                                    wink_sdk_extranet_distribution.models.localized_description_supplier_details.LocalizedDescription_SupplierDetails(
                                        description = 'This is a longer description in the specified language.', 
                                        language = 'en', )
                                    ], 
                                promotional_codes = [
                                    ''
                                    ], 
                                user_specified_currency_total = , 
                                source_total = , 
                                internal_total = , 
                                user_specified_currency_average_price_per_night = , 
                                internal_average_price_per_night = , 
                                source_average_price_per_night = , 
                                total_discount_percent = 1.337, ), 
                            extra_charges = wink_sdk_extranet_distribution.models.extra_charges_supplier_details.ExtraCharges_SupplierDetails(
                                items = [
                                    wink_sdk_extranet_distribution.models.items.Items(
                                        rate_plan_level_fee = wink_sdk_extranet_distribution.models.rate_plan_level_fee_supplier_details.RatePlanLevelFee_SupplierDetails(
                                            descriptions = [
                                                
                                                ], 
                                            fixed_amount = , 
                                            type = 'PER_DAY', ), 
                                        unit_price = wink_sdk_extranet_distribution.models.localized_price_supplier_details.LocalizedPrice_SupplierDetails(
                                            source_to_user_currency_quote = , 
                                            source_to_internal_currency_quote = , 
                                            user_specified_currency_base_total = , 
                                            source_base_total = , 
                                            internal_base_total = , 
                                            user_specified_currency_promotional_modifier = -40, 
                                            source_promotional_modifier = -40, 
                                            internal_promotional_modifier = -40, 
                                            user_specified_currency_premium_modifier = 40, 
                                            source_premium_modifier = 40, 
                                            internal_premium_modifier = 40, 
                                            user_specified_currency_channel_modifier = -10, 
                                            source_channel_modifier = -10, 
                                            internal_channel_modifier = -10, 
                                            quantity = 56, 
                                            promotional_discount_percent = 1.337, 
                                            channel_discount_percent = 1.337, 
                                            premium_percent = 1.337, 
                                            has_channel_discount = True, 
                                            has_premium = True, 
                                            has_promotion = True, 
                                            total_discount_percent = 1.337, ), )
                                    ], ), 
                            configuration = wink_sdk_extranet_distribution.models.room_configuration_supplier_details.RoomConfiguration_SupplierDetails(
                                adults = 2, 
                                children = [
                                    wink_sdk_extranet_distribution.models.child_supplier_details.Child_SupplierDetails(
                                        quantity = 1, 
                                        age = 0, )
                                    ], ), 
                            add_on_offers = [
                                wink_sdk_extranet_distribution.models.add_on_localized_inventory_supplier_details.AddOnLocalizedInventory_SupplierDetails(
                                    add_on = wink_sdk_extranet_distribution.models.add_on_supplier_details.AddOn_SupplierDetails(
                                        identifier = '', 
                                        hotel_identifier = '', 
                                        featured_ind = False, 
                                        lifestyle_type = 'LIFESTYLE_HEALTH_FITNESS', 
                                        location = {"type":"POINT","coordinates":[100.5581533,13.7370197]}, 
                                        descriptions = [
                                            
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
                                                timezone = 'America/New_York', ), 
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
                                        price_point = 'THREE', 
                                        applicable_start = 'Thu Jan 01 07:00:00 ICT 1970', 
                                        applicable_end = 'Tue Dec 01 07:00:00 ICT 1970', 
                                        reservation_required_ind = False, 
                                        opens = '09:00', 
                                        closes = '17:30', 
                                        days_of_week = , 
                                        number_of_units = 10, 
                                        rate_plan_identifier = '', 
                                        mandatory = True, ), 
                                    price_list = [
                                        wink_sdk_extranet_distribution.models.localized_transactional_travel_inventory_supplier_details.LocalizedTransactionalTravelInventory_SupplierDetails(
                                            identifier = '', 
                                            name = '1 hour session', 
                                            descriptions = [
                                                
                                                ], 
                                            pricing_type = 'PER_STAY', 
                                            price = wink_sdk_extranet_distribution.models.localized_price_supplier_details.LocalizedPrice_SupplierDetails(
                                                source_to_user_currency_quote = , 
                                                source_to_internal_currency_quote = , 
                                                user_specified_currency_base_total = , 
                                                source_base_total = , 
                                                internal_base_total = , 
                                                user_specified_currency_promotional_modifier = -40, 
                                                source_promotional_modifier = -40, 
                                                internal_promotional_modifier = -40, 
                                                user_specified_currency_premium_modifier = 40, 
                                                source_premium_modifier = 40, 
                                                internal_premium_modifier = 40, 
                                                user_specified_currency_channel_modifier = -10, 
                                                source_channel_modifier = -10, 
                                                internal_channel_modifier = -10, 
                                                quantity = 56, 
                                                promotional_discount_percent = 1.337, 
                                                channel_discount_percent = 1.337, 
                                                premium_percent = 1.337, 
                                                has_channel_discount = True, 
                                                has_premium = True, 
                                                has_promotion = True, 
                                                total_discount_percent = 1.337, ), 
                                            min_pax = 2, 
                                            max_pax = 10, 
                                            promotion = '', )
                                        ], 
                                    channel_inventory_identifier = '', 
                                    commissionable = True, 
                                    commission = 0.1, 
                                    direct = True, )
                                ], 
                            perk_value = 56, 
                            active_cancellation_policy = , 
                            room_nights = 56, 
                            list = [
                                wink_sdk_extranet_distribution.models.localized_transactional_travel_inventory_supplier_details.LocalizedTransactionalTravelInventory_SupplierDetails(
                                    identifier = '', 
                                    name = '1 hour session', 
                                    descriptions = , 
                                    pricing_type = 'PER_STAY', 
                                    price = , 
                                    min_pax = 2, 
                                    max_pax = 10, 
                                    promotion = '', )
                                ], 
                            channel_inventory_identifier = '', 
                            commissionable = True, 
                            commission = 0.1, 
                            direct = True, 
                            price_list = [
                                
                                ], 
                            source_total = , 
                            user_specified_currency_total = , 
                            internal_total = , 
                            available = True, 
                            rate_source = '', ), 
                        price_configurations = [
                            wink_sdk_extranet_distribution.models.room_configuration_price_supplier_details.RoomConfigurationPrice_SupplierDetails(
                                adults = 56, 
                                start_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                                end_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                                room_rate_identifier = '', 
                                room_rate_internal_name = '', 
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
                                    cancellation_policy_identifier = 'cancellation-policy-1', ), 
                                price = wink_sdk_extranet_distribution.models.stay_rate_supplier_details.StayRate_SupplierDetails(
                                    source_extra_pax_modifier = 15, 
                                    internal_extra_pax_modifier = 15, 
                                    user_specified_currency_extra_pax_modifier = 15, 
                                    source_extra_child_modifier = 15, 
                                    internal_extra_child_modifier = 15, 
                                    user_specified_currency_extra_child_modifier = 15, 
                                    source_single_occupant_modifier = -15, 
                                    internal_single_occupant_modifier = -15, 
                                    user_specified_currency_single_occupant_modifier = -15, 
                                    source_promotional_modifier = -40, 
                                    internal_promotional_modifier = -40, 
                                    user_specified_currency_promotional_modifier = -40, 
                                    source_premium_modifier = 40, 
                                    internal_premium_modifier = 40, 
                                    user_specified_currency_premium_modifier = 40, 
                                    source_channel_modifier = -10, 
                                    internal_channel_modifier = -10, 
                                    user_specified_currency_channel_modifier = -10, 
                                    quantity = 56, 
                                    min_occupancy = 56, 
                                    max_occupancy = 56, 
                                    rate_source = '', 
                                    promotional_discount_percent = 1.337, 
                                    channel_discount_percent = 1.337, 
                                    premium_percent = 1.337, 
                                    available = True, 
                                    total_discount_percent = 1.337, ), 
                                configuration = wink_sdk_extranet_distribution.models.room_configuration_supplier_details.RoomConfiguration_SupplierDetails(
                                    adults = 2, ), 
                                perk_value = 56, 
                                active_cancellation_policy = , 
                                room_nights = 56, 
                                channel_inventory_identifier = '', 
                                commissionable = True, 
                                commission = 0.1, 
                                direct = True, 
                                available = True, 
                                rate_source = '', )
                            ], 
                        inaccessible_availability_reason = wink_sdk_extranet_distribution.models.descriptive_reason_supplier_details.DescriptiveReason_SupplierDetails(
                            identifier = '', 
                            name = '', 
                            map = {
                                'key' : ''
                                }, 
                            reasons = [
                                ''
                                ], ), )
                    ],
                inaccessible_availability = [
                    wink_sdk_extranet_distribution.models.descriptive_reason_supplier_details.DescriptiveReason_SupplierDetails(
                        identifier = '', 
                        name = '', 
                        map = {
                            'key' : ''
                            }, 
                        reasons = [
                            ''
                            ], )
                    ]
            )
        else:
            return DescriptiveRoomSupplierDetails(
        )
        """

    def testDescriptiveRoomSupplierDetails(self):
        """Test DescriptiveRoomSupplierDetails"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
