# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/engine-client): A single endpoint to retrieve whitelabel + customization information for the booking engine.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Extranet Monetize API This part of the documentation concerns itself with the management of cancellation policies, promotions, restrictions etc. This API lets you create:  1. Add-ons: Manage add-ons. 2. Cancellation policies: Manage cancellation policies for your property. 3. Rate plan: Manage property rate plans. 4. Master rates: Manage perks for room type / rate plan combos. 5. Promotions: Manage promotions. 6. Promotion bundle: Manage bundled promotions.  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.5.19
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from wink_sdk_extranet_monetize.models.rate_modifier_supplier import RateModifierSupplier

class TestRateModifierSupplier(unittest.TestCase):
    """RateModifierSupplier unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> RateModifierSupplier:
        """Test RateModifierSupplier
            include_optional is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `RateModifierSupplier`
        """
        model = RateModifierSupplier()
        if include_optional:
            return RateModifierSupplier(
                identifier = '',
                hotel_identifier = '',
                name = 'Early bird',
                type = 'DISCOUNT',
                modifier = wink_sdk_extranet_monetize.models.variable_charge_supplier.VariableCharge_Supplier(
                    type = 'FIXED', 
                    percent = 0.25, 
                    fixed_amount = wink_sdk_extranet_monetize.models.custom_monetary_amount.CustomMonetaryAmount(
                        amount = 1.337, 
                        currency = '', ), ),
                enabled = True,
                pricing_type = 'PER_PERSON_PER_NIGHT',
                descriptions = [
                    wink_sdk_extranet_monetize.models.localized_description_supplier.LocalizedDescription_Supplier(
                        description = 'This is a longer description in the specified language.', 
                        language = 'en', )
                    ],
                city_rate_qualifiers = [
                    wink_sdk_extranet_monetize.models.city_rate_qualifier_supplier.CityRateQualifier_Supplier(
                        city = wink_sdk_extranet_monetize.models.geo_ip_supplier.GeoIP_Supplier(
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
                    wink_sdk_extranet_monetize.models.continent_rate_qualifier_supplier.ContinentRateQualifier_Supplier(
                        continent = 'NA', )
                    ],
                country_rate_qualifiers = [
                    wink_sdk_extranet_monetize.models.country_rate_qualifier_supplier.CountryRateQualifier_Supplier(
                        country = wink_sdk_extranet_monetize.models.geo_name_country_supplier.GeoNameCountry_Supplier(
                            geo_name_id = '', 
                            continent_code = '', 
                            continent_name = '', 
                            country_iso_code = '', 
                            country_name = '', ), )
                    ],
                promotion_rate_qualifiers = [
                    wink_sdk_extranet_monetize.models.promotion_rate_qualifier_supplier.PromotionRateQualifier_Supplier(
                        promotion = 'NA', )
                    ],
                ip_range_rate_qualifiers = [
                    wink_sdk_extranet_monetize.models.ip_range_rate_qualifier_supplier.IPRangeRateQualifier_Supplier(
                        start_ip_range = '', 
                        end_ip_range = '', )
                    ],
                room_range_rate_qualifier = wink_sdk_extranet_monetize.models.room_range_rate_qualifier_supplier.RoomRangeRateQualifier_Supplier(
                    min_rooms = 1, 
                    max_rooms = 56, ),
                prepay_rate_qualifier = wink_sdk_extranet_monetize.models.prepay_rate_qualifier_supplier.PrepayRateQualifier_Supplier(
                    prepay = True, ),
                refundable_rate_qualifier = wink_sdk_extranet_monetize.models.refundable_rate_qualifier_supplier.RefundableRateQualifier_Supplier(
                    refundable = True, ),
                timezone_rate_qualifiers = [
                    wink_sdk_extranet_monetize.models.timezone_rate_qualifier_supplier.TimezoneRateQualifier_Supplier(
                        timezone = '', )
                    ],
                last_minute_rate_qualifier = wink_sdk_extranet_monetize.models.minutes_before_booking_start_date_rate_qualifier_supplier.MinutesBeforeBookingStartDateRateQualifier_Supplier(
                    seconds = 0, ),
                length_of_stay_rate_qualifier = wink_sdk_extranet_monetize.models.length_of_stay_rate_qualifier_supplier.LengthOfStayRateQualifier_Supplier(
                    min_los = 0, 
                    max_los = 0, ),
                advance_booking_rate_qualifier = wink_sdk_extranet_monetize.models.advance_booking_rate_qualifier_supplier.AdvanceBookingRateQualifier_Supplier(
                    min_advance_booking_offset = 0, 
                    max_advance_booking_offset = 0, ),
                stay_date_rate_qualifiers = [
                    wink_sdk_extranet_monetize.models.stay_date_rate_qualifier_supplier.StayDateRateQualifier_Supplier(
                        effective_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                        expire_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), )
                    ],
                sell_date_rate_qualifiers = [
                    wink_sdk_extranet_monetize.models.sell_date_rate_qualifier_supplier.SellDateRateQualifier_Supplier(
                        effective_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                        expire_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), )
                    ],
                available_days_of_week_rate_qualifier = wink_sdk_extranet_monetize.models.available_days_of_week_rate_qualifier_supplier.AvailableDaysOfWeekRateQualifier_Supplier(
                    days_of_week = wink_sdk_extranet_monetize.models.dow_pattern_group_supplier.DowPatternGroup_Supplier(
                        mon = True, 
                        tue = True, 
                        wed = True, 
                        thu = True, 
                        fri = True, 
                        sat = True, 
                        sun = True, 
                        disabled = True, ), ),
                arrival_days_of_week_rate_qualifier = wink_sdk_extranet_monetize.models.arrival_days_of_week_rate_qualifier_supplier.ArrivalDaysOfWeekRateQualifier_Supplier(
                    days_of_week = wink_sdk_extranet_monetize.models.dow_pattern_group_supplier.DowPatternGroup_Supplier(
                        mon = True, 
                        tue = True, 
                        wed = True, 
                        thu = True, 
                        fri = True, 
                        sat = True, 
                        sun = True, 
                        disabled = True, ), ),
                departure_days_of_week_rate_qualifier = wink_sdk_extranet_monetize.models.departure_days_of_week_rate_qualifier_supplier.DepartureDaysOfWeekRateQualifier_Supplier(
                    days_of_week = wink_sdk_extranet_monetize.models.dow_pattern_group_supplier.DowPatternGroup_Supplier(
                        mon = True, 
                        tue = True, 
                        wed = True, 
                        thu = True, 
                        fri = True, 
                        sat = True, 
                        sun = True, 
                        disabled = True, ), ),
                required_days_of_week_rate_qualifier = wink_sdk_extranet_monetize.models.required_days_of_week_rate_qualifier_supplier.RequiredDaysOfWeekRateQualifier_Supplier(
                    days_of_week = wink_sdk_extranet_monetize.models.dow_pattern_group_supplier.DowPatternGroup_Supplier(
                        mon = True, 
                        tue = True, 
                        wed = True, 
                        thu = True, 
                        fri = True, 
                        sat = True, 
                        sun = True, 
                        disabled = True, ), ),
                master_rate_identifiers = ["master-rate-1","master-rate-2"],
                add_on_identifiers = ["add-on-1","add-on-2"],
                rate_plan_identifiers = ["rate-plan-1","rate-plan-2"],
                blackout_dates = [
                    wink_sdk_extranet_monetize.models.blackout_date_supplier.BlackoutDate_Supplier(
                        effective_date = 'Wed Jan 01 07:00:00 ICT 2020', 
                        expire_date = 'Fri Jan 31 07:00:00 ICT 2020', )
                    ]
            )
        else:
            return RateModifierSupplier(
                identifier = '',
                hotel_identifier = '',
                name = 'Early bird',
                type = 'DISCOUNT',
                modifier = wink_sdk_extranet_monetize.models.variable_charge_supplier.VariableCharge_Supplier(
                    type = 'FIXED', 
                    percent = 0.25, 
                    fixed_amount = wink_sdk_extranet_monetize.models.custom_monetary_amount.CustomMonetaryAmount(
                        amount = 1.337, 
                        currency = '', ), ),
                enabled = True,
                pricing_type = 'PER_PERSON_PER_NIGHT',
                descriptions = [
                    wink_sdk_extranet_monetize.models.localized_description_supplier.LocalizedDescription_Supplier(
                        description = 'This is a longer description in the specified language.', 
                        language = 'en', )
                    ],
        )
        """

    def testRateModifierSupplier(self):
        """Test RateModifierSupplier"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
