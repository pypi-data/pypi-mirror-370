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

from wink_sdk_extranet_distribution.models.booking_contract_supplier_details import BookingContractSupplierDetails

class TestBookingContractSupplierDetails(unittest.TestCase):
    """BookingContractSupplierDetails unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> BookingContractSupplierDetails:
        """Test BookingContractSupplierDetails
            include_optional is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `BookingContractSupplierDetails`
        """
        model = BookingContractSupplierDetails()
        if include_optional:
            return BookingContractSupplierDetails(
                booking_contract_identifier = '',
                created_date = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                last_update = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                federated_organization_identifier = 'owner-1',
                federated_organization_name = 'Wink',
                user = user-1,
                ip_address = '111.222.333.444',
                trace_id = 'T-123456',
                source_url = 'https://www.traveliko.com',
                identifier = '',
                supplier_identifier = '',
                supplier_name = 'Supplier One',
                display_price_quote = wink_sdk_extranet_distribution.models.quote_supplier_details.Quote_SupplierDetails(
                    source = '', 
                    target = '', 
                    exchange_rate = 1.337, 
                    timestamp = 56, ),
                supplier_price_quote = wink_sdk_extranet_distribution.models.quote_supplier_details.Quote_SupplierDetails(
                    source = '', 
                    target = '', 
                    exchange_rate = 1.337, 
                    timestamp = 56, ),
                internal_price_quote = wink_sdk_extranet_distribution.models.quote_supplier_details.Quote_SupplierDetails(
                    source = '', 
                    target = '', 
                    exchange_rate = 1.337, 
                    timestamp = 56, ),
                capture_price_quote = wink_sdk_extranet_distribution.models.quote_supplier_details.Quote_SupplierDetails(
                    source = '', 
                    target = '', 
                    exchange_rate = 1.337, 
                    timestamp = 56, ),
                item_list = [
                    wink_sdk_extranet_distribution.models.booking_contract_item_supplier_details.BookingContractItem_SupplierDetails(
                        supplier_item_booking_code = 'TP-ASDFG1234', 
                        user = wink_sdk_extranet_distribution.models.guest_user_supplier_details.GuestUser_SupplierDetails(
                            user_identifier = '', 
                            first_name = 'John', 
                            last_name = 'Smith', 
                            email = 'john.smith@email.com', 
                            telephone = '+1 212 555 1212', 
                            profile = wink_sdk_extranet_distribution.models.profile_supplier_details.Profile_SupplierDetails(
                                profile_identifier = '', 
                                user_identifier = '', 
                                share = True, 
                                user = wink_sdk_extranet_distribution.models.profile_user_supplier_details.ProfileUser_SupplierDetails(
                                    first_name = 'Avid', 
                                    last_name = 'Travelman', 
                                    email = 'avid@travelman.com', 
                                    phone = '0123456789', 
                                    profile_picture_url = '', 
                                    full_name = 'John Smith', ), 
                                personal = wink_sdk_extranet_distribution.models.personal_supplier_details.Personal_SupplierDetails(
                                    gender = 'MALE', 
                                    birth_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                                    marital_status = 'ANNULLED', 
                                    child_quantity = 56, 
                                    citizenship = '', 
                                    address1 = '', 
                                    address2 = '', 
                                    city = '', 
                                    state = '', 
                                    postal_code = '', 
                                    country = '', 
                                    preferred_currency = 'USD', 
                                    language = '', 
                                    contact_person = [
                                        wink_sdk_extranet_distribution.models.contact_supplier_details.Contact_SupplierDetails(
                                            first_name = 'John', 
                                            last_name = 'Smith', 
                                            email = 'johnsmith@email.com', 
                                            secondary_email = 'johnsmith2@email.com', 
                                            phone_number = '+12125551212', 
                                            full_name = 'John Smith', 
                                            summary = 'John Smith (johnsmith@gmail.com / +12125551212)', )
                                        ], 
                                    phys_chall_name = [
                                        ''
                                        ], 
                                    pet_info = [
                                        wink_sdk_extranet_distribution.models.pet_info_dto_supplier_details.PetInfoDto_SupplierDetails(
                                            name = '', 
                                            type = '', )
                                        ], ), 
                                preferences = wink_sdk_extranet_distribution.models.preferences_supplier_details.Preferences_SupplierDetails(
                                    property_location_pref = '', 
                                    property_type_pref = '', 
                                    hotel_chain_pref = '', 
                                    property_amenity_pref = [
                                        ''
                                        ], 
                                    recreation_srvc_pref = [
                                        ''
                                        ], 
                                    business_srvc_pref = [
                                        ''
                                        ], 
                                    security_feature_pref = [
                                        ''
                                        ], 
                                    phys_chal_feature_pref = [
                                        ''
                                        ], 
                                    smoking_allowed = True, 
                                    room_location_pref = '', 
                                    bed_type_pref = '', 
                                    food_srvc_pref = '', 
                                    room_amenity_pref = [
                                        ''
                                        ], 
                                    guest_type = '', 
                                    meal_pref = '', 
                                    cuisine_pref = '', 
                                    interest_pref = [
                                        ''
                                        ], 
                                    beverage_pref = [
                                        ''
                                        ], 
                                    food_pref = [
                                        ''
                                        ], 
                                    allergies = [
                                        ''
                                        ], 
                                    pets_pref = [
                                        ''
                                        ], ), ), 
                            full_name = 'John Smith', ), 
                        name_in_english = 'Deluxe King', 
                        description_in_english = 'This is the best deluxe king that money can buy.', 
                        itinerary = wink_sdk_extranet_distribution.models.simple_date_time_itinerary_supplier_details.SimpleDateTimeItinerary_SupplierDetails(
                            start_date = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                            end_date = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                            adults = 0, 
                            children = 0, 
                            hours = 56, 
                            guests = 56, 
                            nights = 56, ), 
                        pricing_type = 'PER_STAY', 
                        type = 'LODGING', 
                        beneficiary_list = [
                            wink_sdk_extranet_distribution.models.beneficiary_supplier_details.Beneficiary_SupplierDetails(
                                account_identifier = 'account-1', 
                                account_name = 'Account 1', 
                                account_email = 'account@one.com', 
                                account_url = 'https://some.url', 
                                type = 'COMMISSION', 
                                amount_due = wink_sdk_extranet_distribution.models.beneficiary_charge_supplier_details.BeneficiaryCharge_SupplierDetails(
                                    type = 'PERCENTAGE', 
                                    percent = 1.337, ), 
                                source_currency = 'USD', 
                                display_currency = 'USD', 
                                supplier_currency = 'USD', 
                                internal_currency = 'USD', 
                                capture_currency = 'USD', 
                                source_amount = 50, 
                                display_amount = 50, 
                                supplier_amount = 50, 
                                internal_amount = 50, 
                                capture_amount = 50, 
                                source_amount_refund_modifier = 5, 
                                display_amount_refund_modifier = 5, 
                                supplier_amount_refund_modifier = 5, 
                                internal_amount_refund_modifier = 5, 
                                capture_amount_refund_modifier = 5, 
                                pending_refunds = [
                                    wink_sdk_extranet_distribution.models.pending_refund_supplier_details.PendingRefund_SupplierDetails(
                                        refund_identifier = 'refund-1', 
                                        source_amount_refund_modifier = 5, 
                                        display_amount_refund_modifier = 5, 
                                        supplier_amount_refund_modifier = 5, 
                                        internal_amount_refund_modifier = 5, 
                                        capture_amount_refund_modifier = 5, )
                                    ], 
                                net_source_amount = 0, 
                                net_display_amount = 0, 
                                net_supplier_amount = 0, 
                                net_internal_amount = 0, 
                                net_capture_amount = 0, 
                                metadata = {
                                    'key' : ''
                                    }, )
                            ], 
                        payable = 'PREPAY', 
                        policy = wink_sdk_extranet_distribution.models.supplier_contract_item_policy_supplier_details.SupplierContractItemPolicy_SupplierDetails(
                            refundable = True, 
                            advance_cancellation_free_of_charge = 'UNTIL_EIGHTEEN_HUNDRED_HOURS_ON_DAY_OF_ARRIVAL', 
                            refundable_cancellation_charge = 'FIFTY_PERCENT', 
                            no_show_charge = 'SAME_AS_CANCELLATION_FEE', 
                            non_refundable_cancellation_charge = 'SEVENTY_PERCENT', 
                            non_refundable_deadline = 'SEVEN_DAYS_BEFORE_ARRIVAL', 
                            non_refundable_after_deadline_cancellation_charge = 'ONE_HUNDRED_PERCENT', 
                            external_identifier = 'policy-1', 
                            fully_refundable = True, 
                            partially_refundable = True, ), 
                        external_identifier = 'room-type-1', 
                        tokens_earned = 12, 
                        daily_rate_list = [
                            wink_sdk_extranet_distribution.models.daily_rate_supplier_details.DailyRate_SupplierDetails(
                                source_base_rate = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                                    amount = 1.337, 
                                    currency = '', ), 
                                internal_base_rate = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                                    amount = 1.337, 
                                    currency = '', ), 
                                user_specified_currency_base_rate = , 
                                source_extra_pax_modifier = 1.337, 
                                internal_extra_pax_modifier = 1.337, 
                                user_specified_currency_extra_pax_modifier = 1.337, 
                                source_extra_child_modifier = 1.337, 
                                internal_extra_child_modifier = 1.337, 
                                user_specified_currency_extra_child_modifier = 1.337, 
                                source_single_occupant_modifier = 1.337, 
                                internal_single_occupant_modifier = 1.337, 
                                user_specified_currency_single_occupant_modifier = 1.337, 
                                source_promotional_modifier = 1.337, 
                                internal_promotional_modifier = 1.337, 
                                user_specified_currency_promotional_modifier = 1.337, 
                                source_premium_modifier = 1.337, 
                                internal_premium_modifier = 1.337, 
                                user_specified_currency_premium_modifier = 1.337, 
                                source_channel_modifier = 1.337, 
                                internal_channel_modifier = 1.337, 
                                user_specified_currency_channel_modifier = 1.337, 
                                available = True, 
                                is_start_date = True, 
                                is_end_date = True, 
                                is_between_date = True, 
                                is_last_night = True, 
                                offer_details = [
                                    wink_sdk_extranet_distribution.models.localized_description_supplier_details.LocalizedDescription_SupplierDetails(
                                        description = 'This is a longer description in the specified language.', 
                                        language = 'en', )
                                    ], 
                                has_modification = True, 
                                is_bundled_modifier = True, 
                                has_channel_discount = True, 
                                channel_discount_percent = 1.337, 
                                promotional_discount_percent = 1.337, 
                                premium_percent = 1.337, 
                                promotion = '', 
                                adults = 56, 
                                children = 56, 
                                rate = wink_sdk_extranet_distribution.models.daily_rate_rate_supplier_details.DailyRateRate_SupplierDetails(
                                    identifier = 'daily-rate-1', 
                                    hotel_identifier = '', 
                                    rate_source = 'TRAVELIKO', 
                                    rate_plan_identifier = '', 
                                    guest_room_identifier = '', 
                                    rate = , 
                                    master = True, 
                                    closed_on_arrival = False, 
                                    closed_on_departure = False, 
                                    date = 'Mon Aug 24 07:00:00 ICT 2020', 
                                    quantity = 9, 
                                    min_occupancy = 1, 
                                    max_occupancy = 2, 
                                    min_length_of_stay = 4, 
                                    max_length_of_stay = 8, 
                                    single_occupancy_rate_modifier = wink_sdk_extranet_distribution.models.variable_charge_supplier_details.VariableCharge_SupplierDetails(
                                        type = 'FIXED', 
                                        percent = 0.25, 
                                        fixed_amount = , ), 
                                    extra_pax_rate_modifier = wink_sdk_extranet_distribution.models.variable_charge_supplier_details.VariableCharge_SupplierDetails(
                                        type = 'FIXED', 
                                        percent = 0.25, ), 
                                    extra_child_rate_modifier = , ), 
                                max_adult_occupancy = 1, 
                                max_child_occupancy = 0, 
                                included_adult_occupancy = 2, 
                                included_child_occupancy = 0, 
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
                                phantom = True, 
                                close_on_departure = True, 
                                inventory_available = True, 
                                master_availability = True, 
                                close_on_arrival = True, 
                                rate_identifier = '', 
                                date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                                source = '', 
                                start_date = True, 
                                between_date = True, 
                                last_night = True, 
                                bundled_modifier = True, 
                                source_rate = , 
                                total_discount_percent = 1.337, 
                                base_rate = , 
                                user_specified_currency_rate = , 
                                internal_rate = , 
                                end_date = True, 
                                quantity = 56, 
                                min_occupancy = 56, 
                                max_occupancy = 56, 
                                min_los = 56, 
                                max_los = 56, )
                            ], 
                        cancelled = True, 
                        source_currency = 'USD', 
                        display_currency = 'USD', 
                        supplier_currency = 'USD', 
                        internal_currency = 'USD', 
                        capture_currency = 'USD', 
                        source_amount = 0, 
                        display_amount = 0, 
                        supplier_amount = 0, 
                        internal_amount = 0, 
                        capture_amount = 0, 
                        source_amount_refund_modifier = 0, 
                        display_amount_refund_modifier = 0, 
                        supplier_amount_refund_modifier = 0, 
                        internal_amount_refund_modifier = 0, 
                        capture_amount_refund_modifier = 0, 
                        net_source_amount = 0, 
                        net_display_amount = 0, 
                        net_supplier_amount = 0, 
                        net_internal_amount = 0, 
                        net_capture_amount = 0, 
                        metadata = {
                            'key' : ''
                            }, 
                        cancellable_by_traveler = True, 
                        cancellable_with_no_charges = True, 
                        cancellable_with_potential_charges = True, 
                        cancellable_by_supplier_or_agent = True, )
                    ],
                external_supplier_identifier = 'supplier-a',
                external_supplier_booking_code = 'external-booking-code-1',
                payment = wink_sdk_extranet_distribution.models.booking_contract_payment_details_supplier_details.BookingContractPaymentDetails_SupplierDetails(
                    acquirer_identifier = 'stripe-world', 
                    vendor = 'STRIPE', 
                    transaction_identifier = 'tx-1', 
                    customer_identifier = 'customer-1', 
                    charge_identifier = 'charge-1', 
                    status = 'INITIALIZED', 
                    agent_invoiced_date = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                    agent_invoice_identifier = 'invoice-1', 
                    redirect_url = '', 
                    fees = [
                        wink_sdk_extranet_distribution.models.fee_supplier_details.Fee_SupplierDetails(
                            identifier = 'ABC1234', 
                            fee = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                                amount = 1.337, 
                                currency = '', ), 
                            type = 'ACQUIRING', 
                            description = '', )
                        ], 
                    vendor_specific = {
                        'key' : ''
                        }, ),
                cancelled = False,
                cancelled_on = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                canceller = 'SALES_CHANNEL',
                cancellation_type = 'DUPLICATE',
                canceller_user_identifier = '',
                cancel_reason = '',
                funds_added_to_ledger = False,
                funds_processed = False,
                refunds = [
                    wink_sdk_extranet_distribution.models.refund_supplier_details.Refund_SupplierDetails(
                        identifier = 'refund-1', 
                        acquirer_refund_identifier = 'r-123456', 
                        requested_by_identifier = 'user-1', 
                        refund = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                            amount = 1.337, 
                            currency = '', ), 
                        created = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        description = 'Customer made a mistake', 
                        reason_type = 'DUPLICATE', 
                        cancel_on_refund = 'NONE', 
                        status_type = 'SUCCEEDED', 
                        request_type = 'BY_ADMIN', 
                        request_status = 'APPROVED', 
                        request_response = 'We have rejected your request. Your cancellation policy does not warrant a manual refund.', 
                        receipt_url = 'https://pay.stripe.com/receipts/payment/CAcaFwoVYWNjdF8xSXcxazVBQ3F2UW9nN1IxKIPqo54GMgbHKn45YQY6LBbCZ62655YzamuWDVeWAaw7uApCrxewxjSsZX4C9Lef5jY9JeYFrOVx3IaI', 
                        retries = 0, 
                        allocation = 'EQUAL_DISTRIBUTION', )
                    ],
                payouts = [
                    wink_sdk_extranet_distribution.models.payout_supplier_details.Payout_SupplierDetails(
                        vendor = 'STRIPE', 
                        vendor_identifier = '', 
                        vendor_name = '', 
                        vendor_token_key = '', 
                        identifier = '', 
                        beneficiary_identifier = '', 
                        external_payee_identifier = 'stripe-cardholder-1', 
                        type = 'BANK_TRANSFER', 
                        entry = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                            amount = 1.337, 
                            currency = '', ), 
                        fees = [
                            wink_sdk_extranet_distribution.models.payout_fee_supplier_details.PayoutFee_SupplierDetails(
                                identifier = '', 
                                fee = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                                    amount = 1.337, 
                                    currency = '', ), 
                                type = 'FX', 
                                candidate = 'PAYOR', 
                                description = '', )
                            ], 
                        created = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        description = 'Card created successfully', 
                        payout_id = 'stripe-card-1', 
                        reference_code = 'ABC1234', 
                        reference_code_date = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        status = 'SCHEDULED', )
                    ],
                source_currency = 'USD',
                display_currency = 'USD',
                supplier_currency = 'USD',
                internal_currency = 'USD',
                capture_currency = 'USD',
                source_amount = 0,
                display_amount = 0,
                supplier_amount = 0,
                internal_amount = 0,
                capture_amount = 0,
                source_amount_refund_modifier = 1.337,
                display_amount_refund_modifier = 1.337,
                supplier_amount_refund_modifier = 1.337,
                internal_amount_refund_modifier = 1.337,
                capture_amount_refund_modifier = 1.337,
                net_source_amount = 1.337,
                net_display_amount = 1.337,
                net_supplier_amount = 1.337,
                net_internal_amount = 1.337,
                net_capture_amount = 1.337,
                metadata = {
                    'key' : ''
                    },
                net_commissionable_total_source_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_commissionable_total_capture_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_commissionable_total_display_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_commissionable_total_supplier_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_commissionable_total_internal_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_fees_and_commissions_source_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_fees_and_commissions_capture_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_fees_and_commissions_display_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_fees_and_commissions_supplier_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_fees_and_commissions_internal_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_fees_source_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_fees_capture_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_fees_display_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_fees_supplier_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_fees_internal_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_trip_pay_fee_source_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_trip_pay_fee_capture_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_trip_pay_fee_display_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_trip_pay_fee_supplier_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_trip_pay_fee_internal_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_sales_source_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_sales_capture_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_sales_display_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_sales_supplier_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_sales_internal_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                commissionable_total_source_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                commissionable_total_capture_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                commissionable_total_display_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                commissionable_total_supplier_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                commissionable_total_internal_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_fees_and_commissions_source_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_fees_and_commissions_capture_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_fees_and_commissions_display_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_fees_and_commissions_supplier_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_fees_and_commissions_internal_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_fees_source_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_fees_capture_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_fees_display_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_fees_supplier_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_fees_internal_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_trip_pay_fee_source_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_trip_pay_fee_capture_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_trip_pay_fee_display_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_trip_pay_fee_supplier_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_trip_pay_fee_internal_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_sales_source_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_sales_capture_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_sales_display_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_sales_supplier_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                total_sales_internal_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                funds_available_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(),
                total_fees_in_percent_with_refund = 1.337,
                total_fees_in_percent = 1.337,
                total_trip_pay_fee_in_percent_with_refund = 1.337,
                total_trip_pay_fee_in_percent = 1.337,
                total_commissions_in_percent_with_refund = 1.337,
                total_commissions_in_percent = 1.337,
                total_fees_and_commissions_in_percent_with_refund = 1.337,
                total_fees_and_commissions_in_percent = 1.337,
                original_fees_in_percent = 1.337,
                original_commissions_in_percent = 1.337,
                net_total_customers_source_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_customers_capture_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_customers_display_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_customers_supplier_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                net_total_customers_internal_amount = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                    amount = 1.337, 
                    currency = '', ),
                has_refunds = True,
                has_successful_refunds = True,
                has_pending_refunds = True,
                has_failed_refunds = True,
                platform_identifier = '',
                total_funds_grouped_by_beneficiary = [
                    wink_sdk_extranet_distribution.models.beneficiary_supplier_details.Beneficiary_SupplierDetails(
                        account_identifier = 'account-1', 
                        account_name = 'Account 1', 
                        account_email = 'account@one.com', 
                        account_url = 'https://some.url', 
                        type = 'COMMISSION', 
                        amount_due = wink_sdk_extranet_distribution.models.beneficiary_charge_supplier_details.BeneficiaryCharge_SupplierDetails(
                            type = 'PERCENTAGE', 
                            percent = 1.337, ), 
                        source_currency = 'USD', 
                        display_currency = 'USD', 
                        supplier_currency = 'USD', 
                        internal_currency = 'USD', 
                        capture_currency = 'USD', 
                        source_amount = 50, 
                        display_amount = 50, 
                        supplier_amount = 50, 
                        internal_amount = 50, 
                        capture_amount = 50, 
                        source_amount_refund_modifier = 5, 
                        display_amount_refund_modifier = 5, 
                        supplier_amount_refund_modifier = 5, 
                        internal_amount_refund_modifier = 5, 
                        capture_amount_refund_modifier = 5, 
                        pending_refunds = [
                            wink_sdk_extranet_distribution.models.pending_refund_supplier_details.PendingRefund_SupplierDetails(
                                refund_identifier = 'refund-1', 
                                source_amount_refund_modifier = 5, 
                                display_amount_refund_modifier = 5, 
                                supplier_amount_refund_modifier = 5, 
                                internal_amount_refund_modifier = 5, 
                                capture_amount_refund_modifier = 5, )
                            ], 
                        net_source_amount = 0, 
                        net_display_amount = 0, 
                        net_supplier_amount = 0, 
                        net_internal_amount = 0, 
                        net_capture_amount = 0, 
                        metadata = {
                            'key' : ''
                            }, )
                    ],
                total_tokens_earned = 56,
                cancellable_by_supplier = True,
                cancellable_by_traveler = True,
                self_acquiring = True,
                lodging = wink_sdk_extranet_distribution.models.booking_contract_item_supplier_details.BookingContractItem_SupplierDetails(
                    supplier_item_booking_code = 'TP-ASDFG1234', 
                    user = wink_sdk_extranet_distribution.models.guest_user_supplier_details.GuestUser_SupplierDetails(
                        user_identifier = '', 
                        first_name = 'John', 
                        last_name = 'Smith', 
                        email = 'john.smith@email.com', 
                        telephone = '+1 212 555 1212', 
                        profile = wink_sdk_extranet_distribution.models.profile_supplier_details.Profile_SupplierDetails(
                            profile_identifier = '', 
                            user_identifier = '', 
                            share = True, 
                            user = wink_sdk_extranet_distribution.models.profile_user_supplier_details.ProfileUser_SupplierDetails(
                                first_name = 'Avid', 
                                last_name = 'Travelman', 
                                email = 'avid@travelman.com', 
                                phone = '0123456789', 
                                profile_picture_url = '', 
                                full_name = 'John Smith', ), 
                            personal = wink_sdk_extranet_distribution.models.personal_supplier_details.Personal_SupplierDetails(
                                gender = 'MALE', 
                                birth_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                                marital_status = 'ANNULLED', 
                                child_quantity = 56, 
                                citizenship = '', 
                                address1 = '', 
                                address2 = '', 
                                city = '', 
                                state = '', 
                                postal_code = '', 
                                country = '', 
                                preferred_currency = 'USD', 
                                language = '', 
                                contact_person = [
                                    wink_sdk_extranet_distribution.models.contact_supplier_details.Contact_SupplierDetails(
                                        first_name = 'John', 
                                        last_name = 'Smith', 
                                        email = 'johnsmith@email.com', 
                                        secondary_email = 'johnsmith2@email.com', 
                                        phone_number = '+12125551212', 
                                        full_name = 'John Smith', 
                                        summary = 'John Smith (johnsmith@gmail.com / +12125551212)', )
                                    ], 
                                phys_chall_name = [
                                    ''
                                    ], 
                                pet_info = [
                                    wink_sdk_extranet_distribution.models.pet_info_dto_supplier_details.PetInfoDto_SupplierDetails(
                                        name = '', 
                                        type = '', )
                                    ], ), 
                            preferences = wink_sdk_extranet_distribution.models.preferences_supplier_details.Preferences_SupplierDetails(
                                property_location_pref = '', 
                                property_type_pref = '', 
                                hotel_chain_pref = '', 
                                property_amenity_pref = [
                                    ''
                                    ], 
                                recreation_srvc_pref = [
                                    ''
                                    ], 
                                business_srvc_pref = [
                                    ''
                                    ], 
                                security_feature_pref = [
                                    ''
                                    ], 
                                phys_chal_feature_pref = [
                                    ''
                                    ], 
                                smoking_allowed = True, 
                                room_location_pref = '', 
                                bed_type_pref = '', 
                                food_srvc_pref = '', 
                                room_amenity_pref = [
                                    ''
                                    ], 
                                guest_type = '', 
                                meal_pref = '', 
                                cuisine_pref = '', 
                                interest_pref = [
                                    ''
                                    ], 
                                beverage_pref = [
                                    ''
                                    ], 
                                food_pref = [
                                    ''
                                    ], 
                                allergies = [
                                    ''
                                    ], 
                                pets_pref = [
                                    ''
                                    ], ), ), 
                        full_name = 'John Smith', ), 
                    name_in_english = 'Deluxe King', 
                    description_in_english = 'This is the best deluxe king that money can buy.', 
                    itinerary = wink_sdk_extranet_distribution.models.simple_date_time_itinerary_supplier_details.SimpleDateTimeItinerary_SupplierDetails(
                        start_date = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        end_date = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        adults = 0, 
                        children = 0, 
                        hours = 56, 
                        guests = 56, 
                        nights = 56, ), 
                    pricing_type = 'PER_STAY', 
                    type = 'LODGING', 
                    beneficiary_list = [
                        wink_sdk_extranet_distribution.models.beneficiary_supplier_details.Beneficiary_SupplierDetails(
                            account_identifier = 'account-1', 
                            account_name = 'Account 1', 
                            account_email = 'account@one.com', 
                            account_url = 'https://some.url', 
                            type = 'COMMISSION', 
                            amount_due = wink_sdk_extranet_distribution.models.beneficiary_charge_supplier_details.BeneficiaryCharge_SupplierDetails(
                                type = 'PERCENTAGE', 
                                percent = 1.337, ), 
                            source_currency = 'USD', 
                            display_currency = 'USD', 
                            supplier_currency = 'USD', 
                            internal_currency = 'USD', 
                            capture_currency = 'USD', 
                            source_amount = 50, 
                            display_amount = 50, 
                            supplier_amount = 50, 
                            internal_amount = 50, 
                            capture_amount = 50, 
                            source_amount_refund_modifier = 5, 
                            display_amount_refund_modifier = 5, 
                            supplier_amount_refund_modifier = 5, 
                            internal_amount_refund_modifier = 5, 
                            capture_amount_refund_modifier = 5, 
                            pending_refunds = [
                                wink_sdk_extranet_distribution.models.pending_refund_supplier_details.PendingRefund_SupplierDetails(
                                    refund_identifier = 'refund-1', 
                                    source_amount_refund_modifier = 5, 
                                    display_amount_refund_modifier = 5, 
                                    supplier_amount_refund_modifier = 5, 
                                    internal_amount_refund_modifier = 5, 
                                    capture_amount_refund_modifier = 5, )
                                ], 
                            net_source_amount = 0, 
                            net_display_amount = 0, 
                            net_supplier_amount = 0, 
                            net_internal_amount = 0, 
                            net_capture_amount = 0, 
                            metadata = {
                                'key' : ''
                                }, )
                        ], 
                    payable = 'PREPAY', 
                    policy = wink_sdk_extranet_distribution.models.supplier_contract_item_policy_supplier_details.SupplierContractItemPolicy_SupplierDetails(
                        refundable = True, 
                        advance_cancellation_free_of_charge = 'UNTIL_EIGHTEEN_HUNDRED_HOURS_ON_DAY_OF_ARRIVAL', 
                        refundable_cancellation_charge = 'FIFTY_PERCENT', 
                        no_show_charge = 'SAME_AS_CANCELLATION_FEE', 
                        non_refundable_cancellation_charge = 'SEVENTY_PERCENT', 
                        non_refundable_deadline = 'SEVEN_DAYS_BEFORE_ARRIVAL', 
                        non_refundable_after_deadline_cancellation_charge = 'ONE_HUNDRED_PERCENT', 
                        external_identifier = 'policy-1', 
                        fully_refundable = True, 
                        partially_refundable = True, ), 
                    external_identifier = 'room-type-1', 
                    tokens_earned = 12, 
                    daily_rate_list = [
                        wink_sdk_extranet_distribution.models.daily_rate_supplier_details.DailyRate_SupplierDetails(
                            source_base_rate = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                                amount = 1.337, 
                                currency = '', ), 
                            internal_base_rate = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                                amount = 1.337, 
                                currency = '', ), 
                            user_specified_currency_base_rate = , 
                            source_extra_pax_modifier = 1.337, 
                            internal_extra_pax_modifier = 1.337, 
                            user_specified_currency_extra_pax_modifier = 1.337, 
                            source_extra_child_modifier = 1.337, 
                            internal_extra_child_modifier = 1.337, 
                            user_specified_currency_extra_child_modifier = 1.337, 
                            source_single_occupant_modifier = 1.337, 
                            internal_single_occupant_modifier = 1.337, 
                            user_specified_currency_single_occupant_modifier = 1.337, 
                            source_promotional_modifier = 1.337, 
                            internal_promotional_modifier = 1.337, 
                            user_specified_currency_promotional_modifier = 1.337, 
                            source_premium_modifier = 1.337, 
                            internal_premium_modifier = 1.337, 
                            user_specified_currency_premium_modifier = 1.337, 
                            source_channel_modifier = 1.337, 
                            internal_channel_modifier = 1.337, 
                            user_specified_currency_channel_modifier = 1.337, 
                            available = True, 
                            is_start_date = True, 
                            is_end_date = True, 
                            is_between_date = True, 
                            is_last_night = True, 
                            offer_details = [
                                wink_sdk_extranet_distribution.models.localized_description_supplier_details.LocalizedDescription_SupplierDetails(
                                    description = 'This is a longer description in the specified language.', 
                                    language = 'en', )
                                ], 
                            has_modification = True, 
                            is_bundled_modifier = True, 
                            has_channel_discount = True, 
                            channel_discount_percent = 1.337, 
                            promotional_discount_percent = 1.337, 
                            premium_percent = 1.337, 
                            promotion = '', 
                            adults = 56, 
                            children = 56, 
                            rate = wink_sdk_extranet_distribution.models.daily_rate_rate_supplier_details.DailyRateRate_SupplierDetails(
                                identifier = 'daily-rate-1', 
                                hotel_identifier = '', 
                                rate_source = 'TRAVELIKO', 
                                rate_plan_identifier = '', 
                                guest_room_identifier = '', 
                                rate = , 
                                master = True, 
                                closed_on_arrival = False, 
                                closed_on_departure = False, 
                                date = 'Mon Aug 24 07:00:00 ICT 2020', 
                                quantity = 9, 
                                min_occupancy = 1, 
                                max_occupancy = 2, 
                                min_length_of_stay = 4, 
                                max_length_of_stay = 8, 
                                single_occupancy_rate_modifier = wink_sdk_extranet_distribution.models.variable_charge_supplier_details.VariableCharge_SupplierDetails(
                                    type = 'FIXED', 
                                    percent = 0.25, 
                                    fixed_amount = , ), 
                                extra_pax_rate_modifier = wink_sdk_extranet_distribution.models.variable_charge_supplier_details.VariableCharge_SupplierDetails(
                                    type = 'FIXED', 
                                    percent = 0.25, ), 
                                extra_child_rate_modifier = , ), 
                            max_adult_occupancy = 1, 
                            max_child_occupancy = 0, 
                            included_adult_occupancy = 2, 
                            included_child_occupancy = 0, 
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
                            phantom = True, 
                            close_on_departure = True, 
                            inventory_available = True, 
                            master_availability = True, 
                            close_on_arrival = True, 
                            rate_identifier = '', 
                            date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                            source = '', 
                            start_date = True, 
                            between_date = True, 
                            last_night = True, 
                            bundled_modifier = True, 
                            source_rate = , 
                            total_discount_percent = 1.337, 
                            base_rate = , 
                            user_specified_currency_rate = , 
                            internal_rate = , 
                            end_date = True, 
                            quantity = 56, 
                            min_occupancy = 56, 
                            max_occupancy = 56, 
                            min_los = 56, 
                            max_los = 56, )
                        ], 
                    cancelled = True, 
                    source_currency = 'USD', 
                    display_currency = 'USD', 
                    supplier_currency = 'USD', 
                    internal_currency = 'USD', 
                    capture_currency = 'USD', 
                    source_amount = 0, 
                    display_amount = 0, 
                    supplier_amount = 0, 
                    internal_amount = 0, 
                    capture_amount = 0, 
                    source_amount_refund_modifier = 0, 
                    display_amount_refund_modifier = 0, 
                    supplier_amount_refund_modifier = 0, 
                    internal_amount_refund_modifier = 0, 
                    capture_amount_refund_modifier = 0, 
                    net_source_amount = 0, 
                    net_display_amount = 0, 
                    net_supplier_amount = 0, 
                    net_internal_amount = 0, 
                    net_capture_amount = 0, 
                    metadata = {
                        'key' : ''
                        }, 
                    cancellable_by_traveler = True, 
                    cancellable_with_no_charges = True, 
                    cancellable_with_potential_charges = True, 
                    cancellable_by_supplier_or_agent = True, ),
                cancellable_by_agent = True,
                cancellable_with_no_charges = True,
                is_cancellable_with_potential_charges = True
            )
        else:
            return BookingContractSupplierDetails(
                federated_organization_identifier = 'owner-1',
                federated_organization_name = 'Wink',
                user = user-1,
                ip_address = '111.222.333.444',
                trace_id = 'T-123456',
                source_url = 'https://www.traveliko.com',
                identifier = '',
                supplier_identifier = '',
                supplier_name = 'Supplier One',
                display_price_quote = wink_sdk_extranet_distribution.models.quote_supplier_details.Quote_SupplierDetails(
                    source = '', 
                    target = '', 
                    exchange_rate = 1.337, 
                    timestamp = 56, ),
                supplier_price_quote = wink_sdk_extranet_distribution.models.quote_supplier_details.Quote_SupplierDetails(
                    source = '', 
                    target = '', 
                    exchange_rate = 1.337, 
                    timestamp = 56, ),
                internal_price_quote = wink_sdk_extranet_distribution.models.quote_supplier_details.Quote_SupplierDetails(
                    source = '', 
                    target = '', 
                    exchange_rate = 1.337, 
                    timestamp = 56, ),
                capture_price_quote = wink_sdk_extranet_distribution.models.quote_supplier_details.Quote_SupplierDetails(
                    source = '', 
                    target = '', 
                    exchange_rate = 1.337, 
                    timestamp = 56, ),
                item_list = [
                    wink_sdk_extranet_distribution.models.booking_contract_item_supplier_details.BookingContractItem_SupplierDetails(
                        supplier_item_booking_code = 'TP-ASDFG1234', 
                        user = wink_sdk_extranet_distribution.models.guest_user_supplier_details.GuestUser_SupplierDetails(
                            user_identifier = '', 
                            first_name = 'John', 
                            last_name = 'Smith', 
                            email = 'john.smith@email.com', 
                            telephone = '+1 212 555 1212', 
                            profile = wink_sdk_extranet_distribution.models.profile_supplier_details.Profile_SupplierDetails(
                                profile_identifier = '', 
                                user_identifier = '', 
                                share = True, 
                                user = wink_sdk_extranet_distribution.models.profile_user_supplier_details.ProfileUser_SupplierDetails(
                                    first_name = 'Avid', 
                                    last_name = 'Travelman', 
                                    email = 'avid@travelman.com', 
                                    phone = '0123456789', 
                                    profile_picture_url = '', 
                                    full_name = 'John Smith', ), 
                                personal = wink_sdk_extranet_distribution.models.personal_supplier_details.Personal_SupplierDetails(
                                    gender = 'MALE', 
                                    birth_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                                    marital_status = 'ANNULLED', 
                                    child_quantity = 56, 
                                    citizenship = '', 
                                    address1 = '', 
                                    address2 = '', 
                                    city = '', 
                                    state = '', 
                                    postal_code = '', 
                                    country = '', 
                                    preferred_currency = 'USD', 
                                    language = '', 
                                    contact_person = [
                                        wink_sdk_extranet_distribution.models.contact_supplier_details.Contact_SupplierDetails(
                                            first_name = 'John', 
                                            last_name = 'Smith', 
                                            email = 'johnsmith@email.com', 
                                            secondary_email = 'johnsmith2@email.com', 
                                            phone_number = '+12125551212', 
                                            full_name = 'John Smith', 
                                            summary = 'John Smith (johnsmith@gmail.com / +12125551212)', )
                                        ], 
                                    phys_chall_name = [
                                        ''
                                        ], 
                                    pet_info = [
                                        wink_sdk_extranet_distribution.models.pet_info_dto_supplier_details.PetInfoDto_SupplierDetails(
                                            name = '', 
                                            type = '', )
                                        ], ), 
                                preferences = wink_sdk_extranet_distribution.models.preferences_supplier_details.Preferences_SupplierDetails(
                                    property_location_pref = '', 
                                    property_type_pref = '', 
                                    hotel_chain_pref = '', 
                                    property_amenity_pref = [
                                        ''
                                        ], 
                                    recreation_srvc_pref = [
                                        ''
                                        ], 
                                    business_srvc_pref = [
                                        ''
                                        ], 
                                    security_feature_pref = [
                                        ''
                                        ], 
                                    phys_chal_feature_pref = [
                                        ''
                                        ], 
                                    smoking_allowed = True, 
                                    room_location_pref = '', 
                                    bed_type_pref = '', 
                                    food_srvc_pref = '', 
                                    room_amenity_pref = [
                                        ''
                                        ], 
                                    guest_type = '', 
                                    meal_pref = '', 
                                    cuisine_pref = '', 
                                    interest_pref = [
                                        ''
                                        ], 
                                    beverage_pref = [
                                        ''
                                        ], 
                                    food_pref = [
                                        ''
                                        ], 
                                    allergies = [
                                        ''
                                        ], 
                                    pets_pref = [
                                        ''
                                        ], ), ), 
                            full_name = 'John Smith', ), 
                        name_in_english = 'Deluxe King', 
                        description_in_english = 'This is the best deluxe king that money can buy.', 
                        itinerary = wink_sdk_extranet_distribution.models.simple_date_time_itinerary_supplier_details.SimpleDateTimeItinerary_SupplierDetails(
                            start_date = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                            end_date = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                            adults = 0, 
                            children = 0, 
                            hours = 56, 
                            guests = 56, 
                            nights = 56, ), 
                        pricing_type = 'PER_STAY', 
                        type = 'LODGING', 
                        beneficiary_list = [
                            wink_sdk_extranet_distribution.models.beneficiary_supplier_details.Beneficiary_SupplierDetails(
                                account_identifier = 'account-1', 
                                account_name = 'Account 1', 
                                account_email = 'account@one.com', 
                                account_url = 'https://some.url', 
                                type = 'COMMISSION', 
                                amount_due = wink_sdk_extranet_distribution.models.beneficiary_charge_supplier_details.BeneficiaryCharge_SupplierDetails(
                                    type = 'PERCENTAGE', 
                                    percent = 1.337, ), 
                                source_currency = 'USD', 
                                display_currency = 'USD', 
                                supplier_currency = 'USD', 
                                internal_currency = 'USD', 
                                capture_currency = 'USD', 
                                source_amount = 50, 
                                display_amount = 50, 
                                supplier_amount = 50, 
                                internal_amount = 50, 
                                capture_amount = 50, 
                                source_amount_refund_modifier = 5, 
                                display_amount_refund_modifier = 5, 
                                supplier_amount_refund_modifier = 5, 
                                internal_amount_refund_modifier = 5, 
                                capture_amount_refund_modifier = 5, 
                                pending_refunds = [
                                    wink_sdk_extranet_distribution.models.pending_refund_supplier_details.PendingRefund_SupplierDetails(
                                        refund_identifier = 'refund-1', 
                                        source_amount_refund_modifier = 5, 
                                        display_amount_refund_modifier = 5, 
                                        supplier_amount_refund_modifier = 5, 
                                        internal_amount_refund_modifier = 5, 
                                        capture_amount_refund_modifier = 5, )
                                    ], 
                                net_source_amount = 0, 
                                net_display_amount = 0, 
                                net_supplier_amount = 0, 
                                net_internal_amount = 0, 
                                net_capture_amount = 0, 
                                metadata = {
                                    'key' : ''
                                    }, )
                            ], 
                        payable = 'PREPAY', 
                        policy = wink_sdk_extranet_distribution.models.supplier_contract_item_policy_supplier_details.SupplierContractItemPolicy_SupplierDetails(
                            refundable = True, 
                            advance_cancellation_free_of_charge = 'UNTIL_EIGHTEEN_HUNDRED_HOURS_ON_DAY_OF_ARRIVAL', 
                            refundable_cancellation_charge = 'FIFTY_PERCENT', 
                            no_show_charge = 'SAME_AS_CANCELLATION_FEE', 
                            non_refundable_cancellation_charge = 'SEVENTY_PERCENT', 
                            non_refundable_deadline = 'SEVEN_DAYS_BEFORE_ARRIVAL', 
                            non_refundable_after_deadline_cancellation_charge = 'ONE_HUNDRED_PERCENT', 
                            external_identifier = 'policy-1', 
                            fully_refundable = True, 
                            partially_refundable = True, ), 
                        external_identifier = 'room-type-1', 
                        tokens_earned = 12, 
                        daily_rate_list = [
                            wink_sdk_extranet_distribution.models.daily_rate_supplier_details.DailyRate_SupplierDetails(
                                source_base_rate = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                                    amount = 1.337, 
                                    currency = '', ), 
                                internal_base_rate = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                                    amount = 1.337, 
                                    currency = '', ), 
                                user_specified_currency_base_rate = , 
                                source_extra_pax_modifier = 1.337, 
                                internal_extra_pax_modifier = 1.337, 
                                user_specified_currency_extra_pax_modifier = 1.337, 
                                source_extra_child_modifier = 1.337, 
                                internal_extra_child_modifier = 1.337, 
                                user_specified_currency_extra_child_modifier = 1.337, 
                                source_single_occupant_modifier = 1.337, 
                                internal_single_occupant_modifier = 1.337, 
                                user_specified_currency_single_occupant_modifier = 1.337, 
                                source_promotional_modifier = 1.337, 
                                internal_promotional_modifier = 1.337, 
                                user_specified_currency_promotional_modifier = 1.337, 
                                source_premium_modifier = 1.337, 
                                internal_premium_modifier = 1.337, 
                                user_specified_currency_premium_modifier = 1.337, 
                                source_channel_modifier = 1.337, 
                                internal_channel_modifier = 1.337, 
                                user_specified_currency_channel_modifier = 1.337, 
                                available = True, 
                                is_start_date = True, 
                                is_end_date = True, 
                                is_between_date = True, 
                                is_last_night = True, 
                                offer_details = [
                                    wink_sdk_extranet_distribution.models.localized_description_supplier_details.LocalizedDescription_SupplierDetails(
                                        description = 'This is a longer description in the specified language.', 
                                        language = 'en', )
                                    ], 
                                has_modification = True, 
                                is_bundled_modifier = True, 
                                has_channel_discount = True, 
                                channel_discount_percent = 1.337, 
                                promotional_discount_percent = 1.337, 
                                premium_percent = 1.337, 
                                promotion = '', 
                                adults = 56, 
                                children = 56, 
                                rate = wink_sdk_extranet_distribution.models.daily_rate_rate_supplier_details.DailyRateRate_SupplierDetails(
                                    identifier = 'daily-rate-1', 
                                    hotel_identifier = '', 
                                    rate_source = 'TRAVELIKO', 
                                    rate_plan_identifier = '', 
                                    guest_room_identifier = '', 
                                    rate = , 
                                    master = True, 
                                    closed_on_arrival = False, 
                                    closed_on_departure = False, 
                                    date = 'Mon Aug 24 07:00:00 ICT 2020', 
                                    quantity = 9, 
                                    min_occupancy = 1, 
                                    max_occupancy = 2, 
                                    min_length_of_stay = 4, 
                                    max_length_of_stay = 8, 
                                    single_occupancy_rate_modifier = wink_sdk_extranet_distribution.models.variable_charge_supplier_details.VariableCharge_SupplierDetails(
                                        type = 'FIXED', 
                                        percent = 0.25, 
                                        fixed_amount = , ), 
                                    extra_pax_rate_modifier = wink_sdk_extranet_distribution.models.variable_charge_supplier_details.VariableCharge_SupplierDetails(
                                        type = 'FIXED', 
                                        percent = 0.25, ), 
                                    extra_child_rate_modifier = , ), 
                                max_adult_occupancy = 1, 
                                max_child_occupancy = 0, 
                                included_adult_occupancy = 2, 
                                included_child_occupancy = 0, 
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
                                phantom = True, 
                                close_on_departure = True, 
                                inventory_available = True, 
                                master_availability = True, 
                                close_on_arrival = True, 
                                rate_identifier = '', 
                                date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                                source = '', 
                                start_date = True, 
                                between_date = True, 
                                last_night = True, 
                                bundled_modifier = True, 
                                source_rate = , 
                                total_discount_percent = 1.337, 
                                base_rate = , 
                                user_specified_currency_rate = , 
                                internal_rate = , 
                                end_date = True, 
                                quantity = 56, 
                                min_occupancy = 56, 
                                max_occupancy = 56, 
                                min_los = 56, 
                                max_los = 56, )
                            ], 
                        cancelled = True, 
                        source_currency = 'USD', 
                        display_currency = 'USD', 
                        supplier_currency = 'USD', 
                        internal_currency = 'USD', 
                        capture_currency = 'USD', 
                        source_amount = 0, 
                        display_amount = 0, 
                        supplier_amount = 0, 
                        internal_amount = 0, 
                        capture_amount = 0, 
                        source_amount_refund_modifier = 0, 
                        display_amount_refund_modifier = 0, 
                        supplier_amount_refund_modifier = 0, 
                        internal_amount_refund_modifier = 0, 
                        capture_amount_refund_modifier = 0, 
                        net_source_amount = 0, 
                        net_display_amount = 0, 
                        net_supplier_amount = 0, 
                        net_internal_amount = 0, 
                        net_capture_amount = 0, 
                        metadata = {
                            'key' : ''
                            }, 
                        cancellable_by_traveler = True, 
                        cancellable_with_no_charges = True, 
                        cancellable_with_potential_charges = True, 
                        cancellable_by_supplier_or_agent = True, )
                    ],
                payment = wink_sdk_extranet_distribution.models.booking_contract_payment_details_supplier_details.BookingContractPaymentDetails_SupplierDetails(
                    acquirer_identifier = 'stripe-world', 
                    vendor = 'STRIPE', 
                    transaction_identifier = 'tx-1', 
                    customer_identifier = 'customer-1', 
                    charge_identifier = 'charge-1', 
                    status = 'INITIALIZED', 
                    agent_invoiced_date = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                    agent_invoice_identifier = 'invoice-1', 
                    redirect_url = '', 
                    fees = [
                        wink_sdk_extranet_distribution.models.fee_supplier_details.Fee_SupplierDetails(
                            identifier = 'ABC1234', 
                            fee = wink_sdk_extranet_distribution.models.custom_monetary_amount.CustomMonetaryAmount(
                                amount = 1.337, 
                                currency = '', ), 
                            type = 'ACQUIRING', 
                            description = '', )
                        ], 
                    vendor_specific = {
                        'key' : ''
                        }, ),
                source_currency = 'USD',
                display_currency = 'USD',
                supplier_currency = 'USD',
                internal_currency = 'USD',
                capture_currency = 'USD',
                source_amount = 0,
                display_amount = 0,
                supplier_amount = 0,
                internal_amount = 0,
                capture_amount = 0,
        )
        """

    def testBookingContractSupplierDetails(self):
        """Test BookingContractSupplierDetails"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
