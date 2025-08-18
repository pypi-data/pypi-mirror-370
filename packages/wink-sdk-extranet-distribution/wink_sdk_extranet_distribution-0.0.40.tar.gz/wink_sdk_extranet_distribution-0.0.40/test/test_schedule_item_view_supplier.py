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

from wink_sdk_extranet_distribution.models.schedule_item_view_supplier import ScheduleItemViewSupplier

class TestScheduleItemViewSupplier(unittest.TestCase):
    """ScheduleItemViewSupplier unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> ScheduleItemViewSupplier:
        """Test ScheduleItemViewSupplier
            include_optional is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `ScheduleItemViewSupplier`
        """
        model = ScheduleItemViewSupplier()
        if include_optional:
            return ScheduleItemViewSupplier(
                id = '',
                created_date = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                last_update = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                version = 12,
                data = wink_sdk_extranet_distribution.models.schedule_item_supplier.ScheduleItem_Supplier(
                    identifier = '', 
                    start = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                    start_timezone = '', 
                    end = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                    end_timezone = '', 
                    is_all_day = True, 
                    title = 'Jane Doe +1', 
                    description = 'Reservation for Jane Doe - 2 PAX', 
                    recurrence_rule = 'FREQ=DAILY;COUNT=5;', 
                    recurrence_id = 'schedule-parent-1', 
                    recurrence_exception = ["2017-12-22T03:07:58.742+0000"], 
                    owner_identifier = '', 
                    booking_identifier = '', 
                    booking_owner_identifier = '', 
                    hotel_identifier = '', 
                    type = 'MEETING_ROOM', 
                    attendees = 2, 
                    email = 'jane@doe.com', 
                    full_name = 'Jane Doe', 
                    first_name = 'Jane', 
                    last_name = 'Doe', 
                    venue_name = 'Restaurant 1', 
                    localized_venue_name = 'The Great Angus', 
                    contact = wink_sdk_extranet_distribution.models.contact_supplier.Contact_Supplier(
                        first_name = 'John', 
                        last_name = 'Smith', 
                        email = 'johnsmith@email.com', 
                        secondary_email = 'johnsmith2@email.com', 
                        phone_number = '+12125551212', 
                        full_name = 'John Smith', 
                        summary = 'John Smith (johnsmith@gmail.com / +12125551212)', ), 
                    address = wink_sdk_extranet_distribution.models.address_supplier.Address_Supplier(
                        address1 = '234 Near da beach', 
                        address2 = 'Pebble #5001', 
                        state = 'CA', 
                        postal_code = '90210', 
                        county = 'Alameda county', 
                        city = wink_sdk_extranet_distribution.models.geo_name_supplier.GeoName_Supplier(
                            geo_name_id = '5128581', 
                            type = 'CITY', 
                            name = 'New York City', 
                            url_name = 'new-york-city-united-states', 
                            ascii_name = 'New York City', 
                            location = {"type":"POINT","coordinates":[100.5581533,13.7370197]}, 
                            feature_code = '', 
                            country_code = '', 
                            timezone = 'America/New_York', 
                            country = wink_sdk_extranet_distribution.models.country_supplier.Country_Supplier(
                                iso = 'US', 
                                name = 'United States', 
                                capital = 'Washington', 
                                continent = 'NA', 
                                currency_code = 'USD', 
                                currency_name = 'Dollar', 
                                geo_name_id = '6252001', ), 
                            sub_country = wink_sdk_extranet_distribution.models.sub_country_supplier.SubCountry_Supplier(
                                name = 'New York', 
                                ascii_name = 'New York', 
                                geo_name_id = '5128638', ), 
                            sub_sub_country = wink_sdk_extranet_distribution.models.sub_sub_country_supplier.SubSubCountry_Supplier(
                                name = '', 
                                ascii_name = '', 
                                geo_name_id = '', ), ), 
                        valid = True, 
                        full_address = '11 At home, Suite 3C, New York City, NY 10010, United States', ), 
                    created = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                    last_modified = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                    sequence = 0, 
                    brand_name = 'Google', 
                    email_header_logo_url = 'https://path.to/my-image.jpg', 
                    logo_identifier = 'my-image', 
                    all_day = True, )
            )
        else:
            return ScheduleItemViewSupplier(
                data = wink_sdk_extranet_distribution.models.schedule_item_supplier.ScheduleItem_Supplier(
                    identifier = '', 
                    start = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                    start_timezone = '', 
                    end = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                    end_timezone = '', 
                    is_all_day = True, 
                    title = 'Jane Doe +1', 
                    description = 'Reservation for Jane Doe - 2 PAX', 
                    recurrence_rule = 'FREQ=DAILY;COUNT=5;', 
                    recurrence_id = 'schedule-parent-1', 
                    recurrence_exception = ["2017-12-22T03:07:58.742+0000"], 
                    owner_identifier = '', 
                    booking_identifier = '', 
                    booking_owner_identifier = '', 
                    hotel_identifier = '', 
                    type = 'MEETING_ROOM', 
                    attendees = 2, 
                    email = 'jane@doe.com', 
                    full_name = 'Jane Doe', 
                    first_name = 'Jane', 
                    last_name = 'Doe', 
                    venue_name = 'Restaurant 1', 
                    localized_venue_name = 'The Great Angus', 
                    contact = wink_sdk_extranet_distribution.models.contact_supplier.Contact_Supplier(
                        first_name = 'John', 
                        last_name = 'Smith', 
                        email = 'johnsmith@email.com', 
                        secondary_email = 'johnsmith2@email.com', 
                        phone_number = '+12125551212', 
                        full_name = 'John Smith', 
                        summary = 'John Smith (johnsmith@gmail.com / +12125551212)', ), 
                    address = wink_sdk_extranet_distribution.models.address_supplier.Address_Supplier(
                        address1 = '234 Near da beach', 
                        address2 = 'Pebble #5001', 
                        state = 'CA', 
                        postal_code = '90210', 
                        county = 'Alameda county', 
                        city = wink_sdk_extranet_distribution.models.geo_name_supplier.GeoName_Supplier(
                            geo_name_id = '5128581', 
                            type = 'CITY', 
                            name = 'New York City', 
                            url_name = 'new-york-city-united-states', 
                            ascii_name = 'New York City', 
                            location = {"type":"POINT","coordinates":[100.5581533,13.7370197]}, 
                            feature_code = '', 
                            country_code = '', 
                            timezone = 'America/New_York', 
                            country = wink_sdk_extranet_distribution.models.country_supplier.Country_Supplier(
                                iso = 'US', 
                                name = 'United States', 
                                capital = 'Washington', 
                                continent = 'NA', 
                                currency_code = 'USD', 
                                currency_name = 'Dollar', 
                                geo_name_id = '6252001', ), 
                            sub_country = wink_sdk_extranet_distribution.models.sub_country_supplier.SubCountry_Supplier(
                                name = 'New York', 
                                ascii_name = 'New York', 
                                geo_name_id = '5128638', ), 
                            sub_sub_country = wink_sdk_extranet_distribution.models.sub_sub_country_supplier.SubSubCountry_Supplier(
                                name = '', 
                                ascii_name = '', 
                                geo_name_id = '', ), ), 
                        valid = True, 
                        full_address = '11 At home, Suite 3C, New York City, NY 10010, United States', ), 
                    created = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                    last_modified = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                    sequence = 0, 
                    brand_name = 'Google', 
                    email_header_logo_url = 'https://path.to/my-image.jpg', 
                    logo_identifier = 'my-image', 
                    all_day = True, ),
        )
        """

    def testScheduleItemViewSupplier(self):
        """Test ScheduleItemViewSupplier"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
