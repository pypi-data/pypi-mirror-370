# coding: utf-8

# flake8: noqa

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md   # Extranet Booking API The Booking API exposes endpoints to manage bookings. This API lets you:  1. Booking: Manage bookings including cancellations. 2. Review: Manage user reviews. 3. Sync w. Calendar: Manage calendar sync with your favorite calendar software  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.18.5
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


__version__ = "0.0.40"

# import apis into sdk package
from wink_sdk_extranet_booking.api.booking_api import BookingApi
from wink_sdk_extranet_booking.api.calendar_sync_api import CalendarSyncApi
from wink_sdk_extranet_booking.api.review_api import ReviewApi

# import ApiClient
from wink_sdk_extranet_booking.api_response import ApiResponse
from wink_sdk_extranet_booking.api_client import ApiClient
from wink_sdk_extranet_booking.configuration import Configuration
from wink_sdk_extranet_booking.exceptions import OpenApiException
from wink_sdk_extranet_booking.exceptions import ApiTypeError
from wink_sdk_extranet_booking.exceptions import ApiValueError
from wink_sdk_extranet_booking.exceptions import ApiKeyError
from wink_sdk_extranet_booking.exceptions import ApiAttributeError
from wink_sdk_extranet_booking.exceptions import ApiException

# import models into sdk package
from wink_sdk_extranet_booking.models.aggregate_descriptor_supplier import AggregateDescriptorSupplier
from wink_sdk_extranet_booking.models.authenticated_user_supplier import AuthenticatedUserSupplier
from wink_sdk_extranet_booking.models.authenticated_user_supplier_details import AuthenticatedUserSupplierDetails
from wink_sdk_extranet_booking.models.bed_supplier import BedSupplier
from wink_sdk_extranet_booking.models.bed_supplier_details import BedSupplierDetails
from wink_sdk_extranet_booking.models.bedroom_configuration_supplier import BedroomConfigurationSupplier
from wink_sdk_extranet_booking.models.bedroom_configuration_supplier_details import BedroomConfigurationSupplierDetails
from wink_sdk_extranet_booking.models.bedroom_supplier import BedroomSupplier
from wink_sdk_extranet_booking.models.bedroom_supplier_details import BedroomSupplierDetails
from wink_sdk_extranet_booking.models.beneficiary_charge_supplier import BeneficiaryChargeSupplier
from wink_sdk_extranet_booking.models.beneficiary_charge_supplier_details import BeneficiaryChargeSupplierDetails
from wink_sdk_extranet_booking.models.beneficiary_supplier import BeneficiarySupplier
from wink_sdk_extranet_booking.models.beneficiary_supplier_details import BeneficiarySupplierDetails
from wink_sdk_extranet_booking.models.booking_analytics_supplier import BookingAnalyticsSupplier
from wink_sdk_extranet_booking.models.booking_ancillary_supplier import BookingAncillarySupplier
from wink_sdk_extranet_booking.models.booking_ancillary_supplier_details import BookingAncillarySupplierDetails
from wink_sdk_extranet_booking.models.booking_cancellable_supplier import BookingCancellableSupplier
from wink_sdk_extranet_booking.models.booking_contract_item_supplier import BookingContractItemSupplier
from wink_sdk_extranet_booking.models.booking_contract_item_supplier_details import BookingContractItemSupplierDetails
from wink_sdk_extranet_booking.models.booking_contract_payment_details_supplier import BookingContractPaymentDetailsSupplier
from wink_sdk_extranet_booking.models.booking_contract_payment_details_supplier_details import BookingContractPaymentDetailsSupplierDetails
from wink_sdk_extranet_booking.models.booking_contract_supplier import BookingContractSupplier
from wink_sdk_extranet_booking.models.booking_contract_supplier_details import BookingContractSupplierDetails
from wink_sdk_extranet_booking.models.booking_itinerary_room_configuration_child_supplier import BookingItineraryRoomConfigurationChildSupplier
from wink_sdk_extranet_booking.models.booking_itinerary_room_configuration_child_supplier_details import BookingItineraryRoomConfigurationChildSupplierDetails
from wink_sdk_extranet_booking.models.booking_itinerary_room_configuration_supplier import BookingItineraryRoomConfigurationSupplier
from wink_sdk_extranet_booking.models.booking_itinerary_room_configuration_supplier_details import BookingItineraryRoomConfigurationSupplierDetails
from wink_sdk_extranet_booking.models.booking_itinerary_supplier import BookingItinerarySupplier
from wink_sdk_extranet_booking.models.booking_itinerary_supplier_details import BookingItinerarySupplierDetails
from wink_sdk_extranet_booking.models.booking_overview_request_supplier import BookingOverviewRequestSupplier
from wink_sdk_extranet_booking.models.booking_supplier import BookingSupplier
from wink_sdk_extranet_booking.models.booking_supplier_details import BookingSupplierDetails
from wink_sdk_extranet_booking.models.booking_user_session_supplier import BookingUserSessionSupplier
from wink_sdk_extranet_booking.models.booking_user_session_supplier_details import BookingUserSessionSupplierDetails
from wink_sdk_extranet_booking.models.booking_user_supplier import BookingUserSupplier
from wink_sdk_extranet_booking.models.booking_user_supplier_details import BookingUserSupplierDetails
from wink_sdk_extranet_booking.models.boolean_response_supplier import BooleanResponseSupplier
from wink_sdk_extranet_booking.models.cal_dav_response_supplier import CalDavResponseSupplier
from wink_sdk_extranet_booking.models.cancellation_detail_supplier import CancellationDetailSupplier
from wink_sdk_extranet_booking.models.cancellation_policy_exception_supplier import CancellationPolicyExceptionSupplier
from wink_sdk_extranet_booking.models.cancellation_policy_exception_supplier_details import CancellationPolicyExceptionSupplierDetails
from wink_sdk_extranet_booking.models.cancellation_policy_exceptions_supplier import CancellationPolicyExceptionsSupplier
from wink_sdk_extranet_booking.models.cancellation_policy_exceptions_supplier_details import CancellationPolicyExceptionsSupplierDetails
from wink_sdk_extranet_booking.models.cancellation_policy_lightweight_supplier import CancellationPolicyLightweightSupplier
from wink_sdk_extranet_booking.models.cancellation_policy_lightweight_supplier_details import CancellationPolicyLightweightSupplierDetails
from wink_sdk_extranet_booking.models.chart_category_axis_supplier import ChartCategoryAxisSupplier
from wink_sdk_extranet_booking.models.chart_legend_supplier import ChartLegendSupplier
from wink_sdk_extranet_booking.models.chart_series_supplier import ChartSeriesSupplier
from wink_sdk_extranet_booking.models.chart_title_supplier import ChartTitleSupplier
from wink_sdk_extranet_booking.models.child_supplier import ChildSupplier
from wink_sdk_extranet_booking.models.child_supplier_details import ChildSupplierDetails
from wink_sdk_extranet_booking.models.commissionable_entry_supplier import CommissionableEntrySupplier
from wink_sdk_extranet_booking.models.commissionable_entry_supplier_details import CommissionableEntrySupplierDetails
from wink_sdk_extranet_booking.models.composite_filter_descriptor_supplier import CompositeFilterDescriptorSupplier
from wink_sdk_extranet_booking.models.contact_supplier import ContactSupplier
from wink_sdk_extranet_booking.models.contact_supplier_details import ContactSupplierDetails
from wink_sdk_extranet_booking.models.count_response_supplier import CountResponseSupplier
from wink_sdk_extranet_booking.models.country_lightweight_supplier import CountryLightweightSupplier
from wink_sdk_extranet_booking.models.country_lightweight_supplier_details import CountryLightweightSupplierDetails
from wink_sdk_extranet_booking.models.custom_monetary_amount import CustomMonetaryAmount
from wink_sdk_extranet_booking.models.customization_lightweight_supplier import CustomizationLightweightSupplier
from wink_sdk_extranet_booking.models.customization_lightweight_supplier_details import CustomizationLightweightSupplierDetails
from wink_sdk_extranet_booking.models.customization_theme_colors_supplier import CustomizationThemeColorsSupplier
from wink_sdk_extranet_booking.models.customization_theme_colors_supplier_details import CustomizationThemeColorsSupplierDetails
from wink_sdk_extranet_booking.models.daily_rate_supplier_details import DailyRateSupplierDetails
from wink_sdk_extranet_booking.models.extra_charge_supplier import ExtraChargeSupplier
from wink_sdk_extranet_booking.models.extra_charge_supplier_details import ExtraChargeSupplierDetails
from wink_sdk_extranet_booking.models.extra_charges_supplier import ExtraChargesSupplier
from wink_sdk_extranet_booking.models.extra_charges_supplier_details import ExtraChargesSupplierDetails
from wink_sdk_extranet_booking.models.filter_descriptor_supplier import FilterDescriptorSupplier
from wink_sdk_extranet_booking.models.general_manager_supplier import GeneralManagerSupplier
from wink_sdk_extranet_booking.models.general_manager_supplier_details import GeneralManagerSupplierDetails
from wink_sdk_extranet_booking.models.generic_error_message import GenericErrorMessage
from wink_sdk_extranet_booking.models.geo_json_point_supplier import GeoJsonPointSupplier
from wink_sdk_extranet_booking.models.geo_json_point_supplier_details import GeoJsonPointSupplierDetails
from wink_sdk_extranet_booking.models.geo_name_lightweight_supplier import GeoNameLightweightSupplier
from wink_sdk_extranet_booking.models.geo_name_lightweight_supplier_details import GeoNameLightweightSupplierDetails
from wink_sdk_extranet_booking.models.group_descriptor_supplier import GroupDescriptorSupplier
from wink_sdk_extranet_booking.models.grouped_booking_sales_metrics_supplier_details import GroupedBookingSalesMetricsSupplierDetails
from wink_sdk_extranet_booking.models.guest_room_lightweight_supplier import GuestRoomLightweightSupplier
from wink_sdk_extranet_booking.models.guest_room_lightweight_supplier_details import GuestRoomLightweightSupplierDetails
from wink_sdk_extranet_booking.models.guest_user_supplier import GuestUserSupplier
from wink_sdk_extranet_booking.models.guest_user_supplier_details import GuestUserSupplierDetails
from wink_sdk_extranet_booking.models.key_value_pair_supplier import KeyValuePairSupplier
from wink_sdk_extranet_booking.models.line_chart_supplier import LineChartSupplier
from wink_sdk_extranet_booking.models.localized_description_supplier import LocalizedDescriptionSupplier
from wink_sdk_extranet_booking.models.localized_description_supplier_details import LocalizedDescriptionSupplierDetails
from wink_sdk_extranet_booking.models.localized_price_supplier import LocalizedPriceSupplier
from wink_sdk_extranet_booking.models.localized_price_supplier_details import LocalizedPriceSupplierDetails
from wink_sdk_extranet_booking.models.media_author_attribution_supplier import MediaAuthorAttributionSupplier
from wink_sdk_extranet_booking.models.media_author_attribution_supplier_details import MediaAuthorAttributionSupplierDetails
from wink_sdk_extranet_booking.models.page_booking_supplier import PageBookingSupplier
from wink_sdk_extranet_booking.models.page_review_supplier import PageReviewSupplier
from wink_sdk_extranet_booking.models.pageable_object_supplier import PageableObjectSupplier
from wink_sdk_extranet_booking.models.payout_fee_supplier import PayoutFeeSupplier
from wink_sdk_extranet_booking.models.payout_fee_supplier_details import PayoutFeeSupplierDetails
from wink_sdk_extranet_booking.models.payout_supplier import PayoutSupplier
from wink_sdk_extranet_booking.models.payout_supplier_details import PayoutSupplierDetails
from wink_sdk_extranet_booking.models.perk_lightweight_supplier import PerkLightweightSupplier
from wink_sdk_extranet_booking.models.perk_lightweight_supplier_details import PerkLightweightSupplierDetails
from wink_sdk_extranet_booking.models.personal_supplier import PersonalSupplier
from wink_sdk_extranet_booking.models.personal_supplier_details import PersonalSupplierDetails
from wink_sdk_extranet_booking.models.preferences_supplier import PreferencesSupplier
from wink_sdk_extranet_booking.models.preferences_supplier_details import PreferencesSupplierDetails
from wink_sdk_extranet_booking.models.profile_lightweight_supplier import ProfileLightweightSupplier
from wink_sdk_extranet_booking.models.profile_lightweight_supplier_details import ProfileLightweightSupplierDetails
from wink_sdk_extranet_booking.models.profile_user_supplier import ProfileUserSupplier
from wink_sdk_extranet_booking.models.profile_user_supplier_details import ProfileUserSupplierDetails
from wink_sdk_extranet_booking.models.property_aggregate_lightweight_supplier import PropertyAggregateLightweightSupplier
from wink_sdk_extranet_booking.models.property_aggregate_lightweight_supplier_details import PropertyAggregateLightweightSupplierDetails
from wink_sdk_extranet_booking.models.property_booking_refund_request_supplier import PropertyBookingRefundRequestSupplier
from wink_sdk_extranet_booking.models.property_policy_supplier import PropertyPolicySupplier
from wink_sdk_extranet_booking.models.property_policy_supplier_details import PropertyPolicySupplierDetails
from wink_sdk_extranet_booking.models.quote_lightweight_supplier import QuoteLightweightSupplier
from wink_sdk_extranet_booking.models.quote_lightweight_supplier_details import QuoteLightweightSupplierDetails
from wink_sdk_extranet_booking.models.rate_plan_level_fee_supplier import RatePlanLevelFeeSupplier
from wink_sdk_extranet_booking.models.rate_plan_level_fee_supplier_details import RatePlanLevelFeeSupplierDetails
from wink_sdk_extranet_booking.models.refund_supplier import RefundSupplier
from wink_sdk_extranet_booking.models.refund_supplier_details import RefundSupplierDetails
from wink_sdk_extranet_booking.models.review_answer_supplier import ReviewAnswerSupplier
from wink_sdk_extranet_booking.models.review_answer_supplier_details import ReviewAnswerSupplierDetails
from wink_sdk_extranet_booking.models.review_lightweight_supplier import ReviewLightweightSupplier
from wink_sdk_extranet_booking.models.review_lightweight_supplier_details import ReviewLightweightSupplierDetails
from wink_sdk_extranet_booking.models.review_response_supplier import ReviewResponseSupplier
from wink_sdk_extranet_booking.models.review_supplier import ReviewSupplier
from wink_sdk_extranet_booking.models.review_user_supplier import ReviewUserSupplier
from wink_sdk_extranet_booking.models.review_user_supplier_details import ReviewUserSupplierDetails
from wink_sdk_extranet_booking.models.room_configuration_price_rate_plan_supplier import RoomConfigurationPriceRatePlanSupplier
from wink_sdk_extranet_booking.models.room_configuration_price_rate_plan_supplier_details import RoomConfigurationPriceRatePlanSupplierDetails
from wink_sdk_extranet_booking.models.room_configuration_supplier import RoomConfigurationSupplier
from wink_sdk_extranet_booking.models.room_configuration_supplier_details import RoomConfigurationSupplierDetails
from wink_sdk_extranet_booking.models.room_stay_supplier import RoomStaySupplier
from wink_sdk_extranet_booking.models.room_stay_supplier_details import RoomStaySupplierDetails
from wink_sdk_extranet_booking.models.show_review400_response import ShowReview400Response
from wink_sdk_extranet_booking.models.simple_address_supplier import SimpleAddressSupplier
from wink_sdk_extranet_booking.models.simple_address_supplier_details import SimpleAddressSupplierDetails
from wink_sdk_extranet_booking.models.simple_date_time_itinerary_supplier import SimpleDateTimeItinerarySupplier
from wink_sdk_extranet_booking.models.simple_date_time_itinerary_supplier_details import SimpleDateTimeItinerarySupplierDetails
from wink_sdk_extranet_booking.models.simple_description_supplier import SimpleDescriptionSupplier
from wink_sdk_extranet_booking.models.simple_description_supplier_details import SimpleDescriptionSupplierDetails
from wink_sdk_extranet_booking.models.simple_multimedia_supplier import SimpleMultimediaSupplier
from wink_sdk_extranet_booking.models.simple_multimedia_supplier_details import SimpleMultimediaSupplierDetails
from wink_sdk_extranet_booking.models.social_supplier import SocialSupplier
from wink_sdk_extranet_booking.models.social_supplier_details import SocialSupplierDetails
from wink_sdk_extranet_booking.models.sort_descriptor_supplier import SortDescriptorSupplier
from wink_sdk_extranet_booking.models.sort_object_supplier import SortObjectSupplier
from wink_sdk_extranet_booking.models.state_supplier import StateSupplier
from wink_sdk_extranet_booking.models.stay_rate_supplier import StayRateSupplier
from wink_sdk_extranet_booking.models.stay_rate_supplier_details import StayRateSupplierDetails
from wink_sdk_extranet_booking.models.sub_country_lightweight_supplier import SubCountryLightweightSupplier
from wink_sdk_extranet_booking.models.sub_country_lightweight_supplier_details import SubCountryLightweightSupplierDetails
from wink_sdk_extranet_booking.models.sub_sub_country_lightweight_supplier import SubSubCountryLightweightSupplier
from wink_sdk_extranet_booking.models.sub_sub_country_lightweight_supplier_details import SubSubCountryLightweightSupplierDetails
from wink_sdk_extranet_booking.models.supplier_contract_item_policy_supplier import SupplierContractItemPolicySupplier
from wink_sdk_extranet_booking.models.supplier_contract_item_policy_supplier_details import SupplierContractItemPolicySupplierDetails
from wink_sdk_extranet_booking.models.transactional_travel_inventory_supplier import TransactionalTravelInventorySupplier
from wink_sdk_extranet_booking.models.transactional_travel_inventory_supplier_details import TransactionalTravelInventorySupplierDetails
from wink_sdk_extranet_booking.models.travel_inventory_recognition_supplier import TravelInventoryRecognitionSupplier
from wink_sdk_extranet_booking.models.travel_inventory_recognition_supplier_details import TravelInventoryRecognitionSupplierDetails
from wink_sdk_extranet_booking.models.variable_charge_supplier import VariableChargeSupplier
from wink_sdk_extranet_booking.models.variable_charge_supplier_details import VariableChargeSupplierDetails
