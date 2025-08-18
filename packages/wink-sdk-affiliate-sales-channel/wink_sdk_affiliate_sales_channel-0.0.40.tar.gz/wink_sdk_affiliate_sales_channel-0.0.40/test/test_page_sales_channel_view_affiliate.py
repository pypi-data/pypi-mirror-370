# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/engine-client): A single endpoint to retrieve whitelabel + customization information for the booking engine.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Sales Channel API The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones. This API lets you:  1. Sales Channel: Manage existing sales channels. 2. Relationship Request: Manage relationship requests. 3. Available Supplier: Browse available suppliers to connect with.  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.5.19
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from wink_sdk_affiliate_sales_channel.models.page_sales_channel_view_affiliate import PageSalesChannelViewAffiliate

class TestPageSalesChannelViewAffiliate(unittest.TestCase):
    """PageSalesChannelViewAffiliate unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> PageSalesChannelViewAffiliate:
        """Test PageSalesChannelViewAffiliate
            include_optional is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `PageSalesChannelViewAffiliate`
        """
        model = PageSalesChannelViewAffiliate()
        if include_optional:
            return PageSalesChannelViewAffiliate(
                total_elements = 56,
                total_pages = 56,
                size = 56,
                content = [
                    wink_sdk_affiliate_sales_channel.models.sales_channel_view_affiliate.SalesChannelView_Affiliate(
                        id = 'doc-1', 
                        created_date = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        last_update = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        version = 12, 
                        sales_channel = wink_sdk_affiliate_sales_channel.models.sales_channel_affiliate.SalesChannel_Affiliate(
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
                                wink_sdk_affiliate_sales_channel.models.rate_modifier_affiliate.RateModifier_Affiliate(
                                    identifier = '', 
                                    hotel_identifier = '', 
                                    name = 'Early bird', 
                                    type = 'DISCOUNT', 
                                    modifier = wink_sdk_affiliate_sales_channel.models.variable_charge_affiliate.VariableCharge_Affiliate(), 
                                    enabled = True, 
                                    pricing_type = 'PER_PERSON_PER_NIGHT', 
                                    descriptions = [
                                        wink_sdk_affiliate_sales_channel.models.localized_description_affiliate.LocalizedDescription_Affiliate(
                                            description = 'This is a longer description in the specified language.', 
                                            language = 'en', )
                                        ], 
                                    city_rate_qualifiers = [
                                        wink_sdk_affiliate_sales_channel.models.city_rate_qualifier_affiliate.CityRateQualifier_Affiliate()
                                        ], 
                                    continent_rate_qualifiers = [
                                        wink_sdk_affiliate_sales_channel.models.continent_rate_qualifier_affiliate.ContinentRateQualifier_Affiliate()
                                        ], 
                                    country_rate_qualifiers = [
                                        wink_sdk_affiliate_sales_channel.models.country_rate_qualifier_affiliate.CountryRateQualifier_Affiliate()
                                        ], 
                                    promotion_rate_qualifiers = [
                                        wink_sdk_affiliate_sales_channel.models.promotion_rate_qualifier_affiliate.PromotionRateQualifier_Affiliate()
                                        ], 
                                    ip_range_rate_qualifiers = [
                                        wink_sdk_affiliate_sales_channel.models.ip_range_rate_qualifier_affiliate.IPRangeRateQualifier_Affiliate()
                                        ], 
                                    room_range_rate_qualifier = wink_sdk_affiliate_sales_channel.models.room_range_rate_qualifier_affiliate.RoomRangeRateQualifier_Affiliate(), 
                                    prepay_rate_qualifier = wink_sdk_affiliate_sales_channel.models.prepay_rate_qualifier_affiliate.PrepayRateQualifier_Affiliate(), 
                                    refundable_rate_qualifier = wink_sdk_affiliate_sales_channel.models.refundable_rate_qualifier_affiliate.RefundableRateQualifier_Affiliate(), 
                                    timezone_rate_qualifiers = [
                                        wink_sdk_affiliate_sales_channel.models.timezone_rate_qualifier_affiliate.TimezoneRateQualifier_Affiliate()
                                        ], 
                                    last_minute_rate_qualifier = wink_sdk_affiliate_sales_channel.models.minutes_before_booking_start_date_rate_qualifier_affiliate.MinutesBeforeBookingStartDateRateQualifier_Affiliate(), 
                                    length_of_stay_rate_qualifier = wink_sdk_affiliate_sales_channel.models.length_of_stay_rate_qualifier_affiliate.LengthOfStayRateQualifier_Affiliate(), 
                                    advance_booking_rate_qualifier = wink_sdk_affiliate_sales_channel.models.advance_booking_rate_qualifier_affiliate.AdvanceBookingRateQualifier_Affiliate(), 
                                    stay_date_rate_qualifiers = [
                                        wink_sdk_affiliate_sales_channel.models.stay_date_rate_qualifier_affiliate.StayDateRateQualifier_Affiliate()
                                        ], 
                                    sell_date_rate_qualifiers = [
                                        wink_sdk_affiliate_sales_channel.models.sell_date_rate_qualifier_affiliate.SellDateRateQualifier_Affiliate()
                                        ], 
                                    available_days_of_week_rate_qualifier = wink_sdk_affiliate_sales_channel.models.available_days_of_week_rate_qualifier_affiliate.AvailableDaysOfWeekRateQualifier_Affiliate(), 
                                    arrival_days_of_week_rate_qualifier = wink_sdk_affiliate_sales_channel.models.arrival_days_of_week_rate_qualifier_affiliate.ArrivalDaysOfWeekRateQualifier_Affiliate(), 
                                    departure_days_of_week_rate_qualifier = wink_sdk_affiliate_sales_channel.models.departure_days_of_week_rate_qualifier_affiliate.DepartureDaysOfWeekRateQualifier_Affiliate(), 
                                    required_days_of_week_rate_qualifier = wink_sdk_affiliate_sales_channel.models.required_days_of_week_rate_qualifier_affiliate.RequiredDaysOfWeekRateQualifier_Affiliate(), 
                                    master_rate_identifiers = ["master-rate-1","master-rate-2"], 
                                    add_on_identifiers = ["add-on-1","add-on-2"], 
                                    rate_plan_identifiers = ["rate-plan-1","rate-plan-2"], 
                                    blackout_dates = [
                                        wink_sdk_affiliate_sales_channel.models.blackout_date_affiliate.BlackoutDate_Affiliate()
                                        ], )
                                ], 
                            rate_modifier_bundles = [
                                wink_sdk_affiliate_sales_channel.models.rate_modifier_bundle_affiliate.RateModifierBundle_Affiliate(
                                    identifier = '', 
                                    hotel_identifier = '', 
                                    name = 'Early bird - Long Term', 
                                    enabled = True, 
                                    items = [
                                        wink_sdk_affiliate_sales_channel.models.rate_modifier_affiliate.RateModifier_Affiliate(
                                            identifier = '', 
                                            hotel_identifier = '', 
                                            name = 'Early bird', 
                                            type = 'DISCOUNT', 
                                            modifier = wink_sdk_affiliate_sales_channel.models.variable_charge_affiliate.VariableCharge_Affiliate(), 
                                            enabled = True, 
                                            pricing_type = 'PER_PERSON_PER_NIGHT', 
                                            descriptions = [
                                                wink_sdk_affiliate_sales_channel.models.localized_description_affiliate.LocalizedDescription_Affiliate(
                                                    description = 'This is a longer description in the specified language.', 
                                                    language = 'en', )
                                                ], 
                                            master_rate_identifiers = ["master-rate-1","master-rate-2"], 
                                            add_on_identifiers = ["add-on-1","add-on-2"], 
                                            rate_plan_identifiers = ["rate-plan-1","rate-plan-2"], )
                                        ], 
                                    modifier_override = wink_sdk_affiliate_sales_channel.models.variable_charge_affiliate.VariableCharge_Affiliate(), 
                                    type = 'DISCOUNT', 
                                    pricing_type = 'PER_STAY', 
                                    has_fixed_discount_modifier = True, 
                                    has_percent_discount_modifier = True, 
                                    is_valid = True, 
                                    description = [
                                        
                                        ], )
                                ], ), )
                    ],
                number = 56,
                sort = [
                    wink_sdk_affiliate_sales_channel.models.sort_object.SortObject(
                        direction = '', 
                        null_handling = '', 
                        ascending = True, 
                        property = '', 
                        ignore_case = True, )
                    ],
                number_of_elements = 56,
                pageable = wink_sdk_affiliate_sales_channel.models.pageable_object_affiliate.PageableObject_Affiliate(
                    offset = 56, 
                    sort = [
                        wink_sdk_affiliate_sales_channel.models.sort_object.SortObject(
                            direction = '', 
                            null_handling = '', 
                            ascending = True, 
                            property = '', 
                            ignore_case = True, )
                        ], 
                    unpaged = True, 
                    page_number = 56, 
                    page_size = 56, 
                    paged = True, ),
                first = True,
                last = True,
                empty = True
            )
        else:
            return PageSalesChannelViewAffiliate(
        )
        """

    def testPageSalesChannelViewAffiliate(self):
        """Test PageSalesChannelViewAffiliate"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
