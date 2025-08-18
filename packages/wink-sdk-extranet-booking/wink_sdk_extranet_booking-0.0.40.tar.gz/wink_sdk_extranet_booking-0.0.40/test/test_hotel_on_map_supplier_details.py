# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/engine-client): A single endpoint to retrieve whitelabel + customization information for the booking engine.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md   # Extranet Booking API The Booking API exposes endpoints to manage bookings. This API lets you:  1. Booking: Manage bookings including cancellations. 2. Review: Manage user reviews. 3. Sync w. Calendar: Manage calendar sync with your favorite calendar software  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.5.19
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from wink_sdk_extranet_booking.models.hotel_on_map_supplier_details import HotelOnMapSupplierDetails

class TestHotelOnMapSupplierDetails(unittest.TestCase):
    """HotelOnMapSupplierDetails unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> HotelOnMapSupplierDetails:
        """Test HotelOnMapSupplierDetails
            include_optional is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `HotelOnMapSupplierDetails`
        """
        model = HotelOnMapSupplierDetails()
        if include_optional:
            return HotelOnMapSupplierDetails(
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
                location = {"type":"POINT","coordinates":[100.5581533,13.7370197]},
                short_descriptions = [
                    wink_sdk_extranet_booking.models.localized_description_supplier_details.LocalizedDescription_SupplierDetails(
                        description = 'This is a longer description in the specified language.', 
                        language = 'en', )
                    ],
                long_descriptions = [
                    wink_sdk_extranet_booking.models.localized_description_supplier_details.LocalizedDescription_SupplierDetails(
                        description = 'This is a longer description in the specified language.', 
                        language = 'en', )
                    ],
                aggregate_greendex_rating = 7.0,
                lifestyle_types = [
                    'LIFESTYLE_HEALTH_FITNESS'
                    ],
                total_reviews = 989,
                available = True,
                hotel_available = True,
                reservations = wink_sdk_extranet_booking.models.contact_supplier_details.Contact_SupplierDetails(
                    first_name = 'John', 
                    last_name = 'Smith', 
                    email = 'johnsmith@email.com', 
                    secondary_email = 'johnsmith2@email.com', 
                    phone_number = '+12125551212', 
                    full_name = 'John Smith', 
                    summary = 'John Smith (johnsmith@gmail.com / +12125551212)', ),
                socials = [
                    wink_sdk_extranet_booking.models.social_supplier_details.Social_SupplierDetails(
                        type = 'FACEBOOK', 
                        location = '', 
                        enabled = True, )
                    ],
                images = [
                    wink_sdk_extranet_booking.models.simple_multimedia_supplier_details.SimpleMultimedia_SupplierDetails(
                        multimedia_identifier = '', 
                        identifier = 'cloudinary-image-1', 
                        type = 'IMAGE', 
                        source = 'CLOUDINARY', 
                        sort = 10, 
                        angle = '-90', 
                        width = 2560, 
                        height = 1600, 
                        published = True, 
                        category = '1', 
                        descriptions = [
                            wink_sdk_extranet_booking.models.simple_description_supplier_details.SimpleDescription_SupplierDetails(
                                name = 'An example title', 
                                description = 'This is a longer description in the specified language.', 
                                language = 'en', )
                            ], 
                        lifestyle_type = 'LIFESTYLE_HEALTH_FITNESS', 
                        attribution = [
                            wink_sdk_extranet_booking.models.image_attribution_supplier_details.ImageAttribution_SupplierDetails(
                                url = 'https://maps.google.com/maps/contrib/111628493169070103594', 
                                name = 'Samuel Adams', )
                            ], 
                        is_landscape = True, )
                    ],
                videos = [
                    wink_sdk_extranet_booking.models.simple_multimedia_supplier_details.SimpleMultimedia_SupplierDetails(
                        multimedia_identifier = '', 
                        identifier = 'cloudinary-image-1', 
                        type = 'IMAGE', 
                        source = 'CLOUDINARY', 
                        sort = 10, 
                        angle = '-90', 
                        width = 2560, 
                        height = 1600, 
                        published = True, 
                        category = '1', 
                        descriptions = [
                            wink_sdk_extranet_booking.models.simple_description_supplier_details.SimpleDescription_SupplierDetails(
                                name = 'An example title', 
                                description = 'This is a longer description in the specified language.', 
                                language = 'en', )
                            ], 
                        lifestyle_type = 'LIFESTYLE_HEALTH_FITNESS', 
                        attribution = [
                            wink_sdk_extranet_booking.models.image_attribution_supplier_details.ImageAttribution_SupplierDetails(
                                url = 'https://maps.google.com/maps/contrib/111628493169070103594', 
                                name = 'Samuel Adams', )
                            ], 
                        is_landscape = True, )
                    ],
                policy = wink_sdk_extranet_booking.models.property_policy_supplier_details.PropertyPolicy_SupplierDetails(
                    children_allowed = True, 
                    children_minimum_age = 6, 
                    internet_availability = 'YES', 
                    internet_connection_type = 'WIFI', 
                    internet_connection_location = 'ENTIRE_PROPERTY', 
                    parking_availability = 'YES', 
                    parking_access = 'PRIVATE', 
                    pets_allowed = True, 
                    pet_max_weight_in_kilos = 10, 
                    pet_charge = wink_sdk_extranet_booking.models.custom_monetary_amount.CustomMonetaryAmount(
                        amount = 1.337, 
                        currency = '', ), 
                    check_out_time = '10:00', 
                    check_in_time = '14:00', ),
                third_party_reviews = [
                    wink_sdk_extranet_booking.models.travel_inventory_recognition_supplier_details.TravelInventoryRecognition_SupplierDetails(
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
                general_manager = wink_sdk_extranet_booking.models.general_manager_supplier_details.GeneralManager_SupplierDetails(
                    name = 'Jane Doe', 
                    image = wink_sdk_extranet_booking.models.simple_multimedia_supplier_details.SimpleMultimedia_SupplierDetails(
                        multimedia_identifier = '', 
                        identifier = 'cloudinary-image-1', 
                        type = 'IMAGE', 
                        source = 'CLOUDINARY', 
                        sort = 10, 
                        angle = '-90', 
                        width = 2560, 
                        height = 1600, 
                        published = True, 
                        category = '1', 
                        descriptions = [
                            wink_sdk_extranet_booking.models.simple_description_supplier_details.SimpleDescription_SupplierDetails(
                                name = 'An example title', 
                                description = 'This is a longer description in the specified language.', 
                                language = 'en', )
                            ], 
                        lifestyle_type = 'LIFESTYLE_HEALTH_FITNESS', 
                        attribution = [
                            wink_sdk_extranet_booking.models.image_attribution_supplier_details.ImageAttribution_SupplierDetails(
                                url = 'https://maps.google.com/maps/contrib/111628493169070103594', 
                                name = 'Samuel Adams', )
                            ], 
                        is_landscape = True, ), 
                    descriptions = [
                        wink_sdk_extranet_booking.models.localized_description_supplier_details.LocalizedDescription_SupplierDetails(
                            description = 'This is a longer description in the specified language.', 
                            language = 'en', )
                        ], ),
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
                address = wink_sdk_extranet_booking.models.address_supplier_details.Address_SupplierDetails(
                    address1 = '234 Near da beach', 
                    address2 = 'Pebble #5001', 
                    state = 'CA', 
                    postal_code = '90210', 
                    county = 'Alameda county', 
                    city = wink_sdk_extranet_booking.models.geo_name_supplier_details.GeoName_SupplierDetails(
                        geo_name_id = '5128581', 
                        type = 'CITY', 
                        name = 'New York City', 
                        url_name = 'new-york-city-united-states', 
                        ascii_name = 'New York City', 
                        location = {"type":"POINT","coordinates":[100.5581533,13.7370197]}, 
                        feature_code = '', 
                        country_code = '', 
                        timezone = 'America/New_York', 
                        country = wink_sdk_extranet_booking.models.country_supplier_details.Country_SupplierDetails(
                            iso = 'US', 
                            name = 'United States', 
                            capital = 'Washington', 
                            continent = 'NA', 
                            currency_code = 'USD', 
                            currency_name = 'Dollar', 
                            geo_name_id = '6252001', ), 
                        sub_country = wink_sdk_extranet_booking.models.sub_country_supplier_details.SubCountry_SupplierDetails(
                            name = 'New York', 
                            ascii_name = 'New York', 
                            geo_name_id = '5128638', ), 
                        sub_sub_country = wink_sdk_extranet_booking.models.sub_sub_country_supplier_details.SubSubCountry_SupplierDetails(
                            name = '', 
                            ascii_name = '', 
                            geo_name_id = '', ), ), 
                    valid = True, 
                    full_address = '11 At home, Suite 3C, New York City, NY 10010, United States', ),
                active = True,
                url_parameters = ''
            )
        else:
            return HotelOnMapSupplierDetails(
        )
        """

    def testHotelOnMapSupplierDetails(self):
        """Test HotelOnMapSupplierDetails"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
