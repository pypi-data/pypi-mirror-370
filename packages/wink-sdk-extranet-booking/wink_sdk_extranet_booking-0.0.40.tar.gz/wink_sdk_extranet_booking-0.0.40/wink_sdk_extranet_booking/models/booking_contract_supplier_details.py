# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md   # Extranet Booking API The Booking API exposes endpoints to manage bookings. This API lets you:  1. Booking: Manage bookings including cancellations. 2. Review: Manage user reviews. 3. Sync w. Calendar: Manage calendar sync with your favorite calendar software  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.18.5
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional, Union
from typing_extensions import Annotated
from wink_sdk_extranet_booking.models.authenticated_user_supplier_details import AuthenticatedUserSupplierDetails
from wink_sdk_extranet_booking.models.beneficiary_supplier_details import BeneficiarySupplierDetails
from wink_sdk_extranet_booking.models.booking_contract_item_supplier_details import BookingContractItemSupplierDetails
from wink_sdk_extranet_booking.models.booking_contract_payment_details_supplier_details import BookingContractPaymentDetailsSupplierDetails
from wink_sdk_extranet_booking.models.custom_monetary_amount import CustomMonetaryAmount
from wink_sdk_extranet_booking.models.payout_supplier_details import PayoutSupplierDetails
from wink_sdk_extranet_booking.models.quote_lightweight_supplier_details import QuoteLightweightSupplierDetails
from wink_sdk_extranet_booking.models.refund_supplier_details import RefundSupplierDetails
from typing import Optional, Set
from typing_extensions import Self

class BookingContractSupplierDetails(BaseModel):
    """
    BookingContractSupplierDetails
    """ # noqa: E501
    booking_contract_identifier: Optional[StrictStr] = Field(default=None, description="Document UUID", alias="bookingContractIdentifier")
    created_date: Optional[datetime] = Field(default=None, description="Datetime this record was first created", alias="createdDate")
    last_update: Optional[datetime] = Field(default=None, description="Datetime this record was last updated", alias="lastUpdate")
    federated_organization_identifier: Annotated[str, Field(min_length=1, strict=True)] = Field(description="The auth realm owner ID", alias="federatedOrganizationIdentifier")
    federated_organization_name: Annotated[str, Field(min_length=1, strict=True)] = Field(description="The auth realm owner name", alias="federatedOrganizationName")
    user: AuthenticatedUserSupplierDetails = Field(description="The authenticated user ID that made the request")
    ip_address: Annotated[str, Field(min_length=1, strict=True)] = Field(description="Caller's IP address", alias="ipAddress")
    trace_id: Annotated[str, Field(min_length=1, strict=True)] = Field(description="Way to track which booking contracts were made together", alias="traceId")
    source_url: Annotated[str, Field(min_length=1, strict=True)] = Field(description="Where did the booking occur", alias="sourceUrl")
    identifier: Annotated[str, Field(min_length=1, strict=True)] = Field(description="Unique identifier used to track the contract. Create a UUID for this purpose.")
    supplier_identifier: Annotated[str, Field(min_length=1, strict=True)] = Field(description="Supplier identifier", alias="supplierIdentifier")
    supplier_name: Annotated[str, Field(min_length=1, strict=True)] = Field(description="Supplier name", alias="supplierName")
    display_price_quote: QuoteLightweightSupplierDetails = Field(description="The quote used to create totalDisplayPrice.", alias="displayPriceQuote")
    supplier_price_quote: QuoteLightweightSupplierDetails = Field(description="The quote used to create totalSupplierPrice.", alias="supplierPriceQuote")
    internal_price_quote: QuoteLightweightSupplierDetails = Field(description="The quote used to create totalInternalPrice.", alias="internalPriceQuote")
    capture_price_quote: QuoteLightweightSupplierDetails = Field(description="The quote used to create totalCapturePrice.", alias="capturePriceQuote")
    item_list: Annotated[List[BookingContractItemSupplierDetails], Field(min_length=1, max_length=2147483647)] = Field(description="Holds one booking line item for a specific supplier.", alias="itemList")
    external_supplier_identifier: Optional[StrictStr] = Field(default=None, description="Contract creator can choose to geoname this record with her own identifier", alias="externalSupplierIdentifier")
    external_supplier_booking_code: Optional[StrictStr] = Field(default=None, description="External booking code generated by the affiliate", alias="externalSupplierBookingCode")
    payment: BookingContractPaymentDetailsSupplierDetails = Field(description="Payment details the merchant provided us at the time of payment.")
    cancelled: StrictBool = Field(description="Optional geoname externalIdentifier to remote inventory.")
    cancelled_on: Optional[datetime] = Field(default=None, description="When the booking was cancelled.", alias="cancelledOn")
    canceller: Optional[StrictStr] = Field(default=None, description="Type of entity that cancelled the booking.")
    cancellation_type: Optional[StrictStr] = Field(default=None, description="Reason type.", alias="cancellationType")
    canceller_user_identifier: Optional[StrictStr] = Field(default=None, description="User identifier that cancelled the entity.", alias="cancellerUserIdentifier")
    cancel_reason: Optional[StrictStr] = Field(default=None, description="Reason for cancellation.", alias="cancelReason")
    funds_processed: Optional[StrictBool] = Field(default=None, description="Whether a funds transfer request has been created for this booking.", alias="fundsProcessed")
    refunds: Optional[List[RefundSupplierDetails]] = Field(default=None, description="An optional list of refunds that occurred with this booking. If the refund amount(s) is the same as the total price, the booking also gets cancelled.")
    payouts: Optional[List[PayoutSupplierDetails]] = Field(default=None, description="An optional list of refunds that occurred with this booking. If the refund amount(s) is the same as the total price, the booking also gets cancelled.")
    source_currency: Annotated[str, Field(min_length=1, strict=True)] = Field(description="The source currency", alias="sourceCurrency")
    display_currency: Annotated[str, Field(min_length=1, strict=True)] = Field(description="The display currency", alias="displayCurrency")
    supplier_currency: Annotated[str, Field(min_length=1, strict=True)] = Field(description="The supplier currency", alias="supplierCurrency")
    internal_currency: Annotated[str, Field(min_length=1, strict=True)] = Field(description="The internal currency", alias="internalCurrency")
    capture_currency: Annotated[str, Field(min_length=1, strict=True)] = Field(description="The capture currency", alias="captureCurrency")
    source_amount: Union[Annotated[float, Field(strict=True, ge=0)], Annotated[int, Field(strict=True, ge=0)]] = Field(description="The total initial price as quoted in the original TripPay contract.", alias="sourceAmount")
    display_amount: Union[Annotated[float, Field(strict=True, ge=0)], Annotated[int, Field(strict=True, ge=0)]] = Field(description="The total display price.", alias="displayAmount")
    supplier_amount: Union[Annotated[float, Field(strict=True, ge=0)], Annotated[int, Field(strict=True, ge=0)]] = Field(description="The total supplier price.", alias="supplierAmount")
    internal_amount: Union[Annotated[float, Field(strict=True, ge=0)], Annotated[int, Field(strict=True, ge=0)]] = Field(alias="internalAmount")
    capture_amount: Union[Annotated[float, Field(strict=True, ge=0)], Annotated[int, Field(strict=True, ge=0)]] = Field(description="The total capture price.", alias="captureAmount")
    source_amount_refund_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The source amount still due after a partial refund occurs.", alias="sourceAmountRefundModifier")
    display_amount_refund_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The display amount still due after a partial refund occurs.", alias="displayAmountRefundModifier")
    supplier_amount_refund_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The supplier amount still due after a partial refund occurs.", alias="supplierAmountRefundModifier")
    internal_amount_refund_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The internal amount still due after a partial refund occurs.", alias="internalAmountRefundModifier")
    capture_amount_refund_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The capture amount still due after a partial refund occurs.", alias="captureAmountRefundModifier")
    net_source_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The total initial price as quoted in the original TripPay contract.", alias="netSourceAmount")
    net_display_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The total display price.", alias="netDisplayAmount")
    net_supplier_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The total supplier price.", alias="netSupplierAmount")
    net_internal_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="netInternalAmount")
    net_capture_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The total capture price.", alias="netCaptureAmount")
    metadata: Optional[Dict[str, StrictStr]] = Field(default=None, description="Place to add more data related to the booking contract.")
    net_commissionable_total_source_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in source currency the affiliate is owed.", alias="netCommissionableTotalSourceAmount")
    net_commissionable_total_capture_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in capture currency the affiliate is owed.", alias="netCommissionableTotalCaptureAmount")
    net_commissionable_total_display_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in display currency the affiliate is owed.", alias="netCommissionableTotalDisplayAmount")
    net_commissionable_total_supplier_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in supplier currency the affiliate is owed.", alias="netCommissionableTotalSupplierAmount")
    net_commissionable_total_internal_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in internal currency the affiliate is owed.", alias="netCommissionableTotalInternalAmount")
    net_total_fees_and_commissions_source_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in source currency that is fees and commission.", alias="netTotalFeesAndCommissionsSourceAmount")
    net_total_fees_and_commissions_capture_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in capture currency the affiliate is owed.", alias="netTotalFeesAndCommissionsCaptureAmount")
    net_total_fees_and_commissions_display_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in display currency the affiliate is owed.", alias="netTotalFeesAndCommissionsDisplayAmount")
    net_total_fees_and_commissions_supplier_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in supplier currency the affiliate is owed.", alias="netTotalFeesAndCommissionsSupplierAmount")
    net_total_fees_and_commissions_internal_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in internal currency the affiliate is owed.", alias="netTotalFeesAndCommissionsInternalAmount")
    net_total_fees_source_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in source currency that is fees and commission.", alias="netTotalFeesSourceAmount")
    net_total_fees_capture_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in capture currency the affiliate is owed.", alias="netTotalFeesCaptureAmount")
    net_total_fees_display_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in display currency the affiliate is owed.", alias="netTotalFeesDisplayAmount")
    net_total_fees_supplier_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in supplier currency the affiliate is owed.", alias="netTotalFeesSupplierAmount")
    net_total_fees_internal_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in internal currency the affiliate is owed.", alias="netTotalFeesInternalAmount")
    net_total_trip_pay_fee_source_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in source currency that is fees and commission.", alias="netTotalTripPayFeeSourceAmount")
    net_total_trip_pay_fee_capture_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in capture currency the affiliate is owed.", alias="netTotalTripPayFeeCaptureAmount")
    net_total_trip_pay_fee_display_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in display currency the affiliate is owed.", alias="netTotalTripPayFeeDisplayAmount")
    net_total_trip_pay_fee_supplier_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in supplier currency the affiliate is owed.", alias="netTotalTripPayFeeSupplierAmount")
    net_total_trip_pay_fee_internal_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in internal currency the affiliate is owed.", alias="netTotalTripPayFeeInternalAmount")
    net_total_sales_source_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in source currency that is fees and commission.", alias="netTotalSalesSourceAmount")
    net_total_sales_capture_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in capture currency the affiliate is owed.", alias="netTotalSalesCaptureAmount")
    net_total_sales_display_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in display currency the affiliate is owed.", alias="netTotalSalesDisplayAmount")
    net_total_sales_supplier_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in supplier currency the affiliate is owed.", alias="netTotalSalesSupplierAmount")
    net_total_sales_internal_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in internal currency the affiliate is owed.", alias="netTotalSalesInternalAmount")
    commissionable_total_source_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in source currency the affiliate is owed.", alias="commissionableTotalSourceAmount")
    commissionable_total_capture_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in capture currency the affiliate is owed.", alias="commissionableTotalCaptureAmount")
    commissionable_total_display_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in display currency the affiliate is owed.", alias="commissionableTotalDisplayAmount")
    commissionable_total_supplier_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in supplier currency the affiliate is owed.", alias="commissionableTotalSupplierAmount")
    commissionable_total_internal_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in internal currency the affiliate is owed.", alias="commissionableTotalInternalAmount")
    total_fees_and_commissions_source_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in source currency that is fees and commission.", alias="totalFeesAndCommissionsSourceAmount")
    total_fees_and_commissions_capture_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in capture currency the affiliate is owed.", alias="totalFeesAndCommissionsCaptureAmount")
    total_fees_and_commissions_display_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in display currency the affiliate is owed.", alias="totalFeesAndCommissionsDisplayAmount")
    total_fees_and_commissions_supplier_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in supplier currency the affiliate is owed.", alias="totalFeesAndCommissionsSupplierAmount")
    total_fees_and_commissions_internal_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in internal currency the affiliate is owed.", alias="totalFeesAndCommissionsInternalAmount")
    total_fees_source_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in source currency that is fees and commission.", alias="totalFeesSourceAmount")
    total_fees_capture_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in capture currency the affiliate is owed.", alias="totalFeesCaptureAmount")
    total_fees_display_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in display currency the affiliate is owed.", alias="totalFeesDisplayAmount")
    total_fees_supplier_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in supplier currency the affiliate is owed.", alias="totalFeesSupplierAmount")
    total_fees_internal_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in internal currency the affiliate is owed.", alias="totalFeesInternalAmount")
    total_trip_pay_fee_source_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in source currency that is fees and commission.", alias="totalTripPayFeeSourceAmount")
    total_trip_pay_fee_capture_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in capture currency the affiliate is owed.", alias="totalTripPayFeeCaptureAmount")
    total_trip_pay_fee_display_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in display currency the affiliate is owed.", alias="totalTripPayFeeDisplayAmount")
    total_trip_pay_fee_supplier_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in supplier currency the affiliate is owed.", alias="totalTripPayFeeSupplierAmount")
    total_trip_pay_fee_internal_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in internal currency the affiliate is owed.", alias="totalTripPayFeeInternalAmount")
    total_sales_source_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in source currency that is fees and commission.", alias="totalSalesSourceAmount")
    total_sales_capture_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in capture currency the affiliate is owed.", alias="totalSalesCaptureAmount")
    total_sales_display_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in display currency the affiliate is owed.", alias="totalSalesDisplayAmount")
    total_sales_supplier_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in supplier currency the affiliate is owed.", alias="totalSalesSupplierAmount")
    total_sales_internal_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in internal currency the affiliate is owed.", alias="totalSalesInternalAmount")
    funds_available_date: Optional[date] = Field(default=None, description="Returns the date the funds will be released to the customer.", alias="fundsAvailableDate")
    total_fees_in_percent_with_refund: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="All amounts that are not of type SALE", alias="totalFeesInPercentWithRefund")
    total_fees_in_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="All amounts that are not of type SALE before a refund was applied", alias="totalFeesInPercent")
    total_trip_pay_fee_in_percent_with_refund: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="All amounts that are not of type SALE", alias="totalTripPayFeeInPercentWithRefund")
    total_trip_pay_fee_in_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="All amounts that are not of type SALE before a refund was applied", alias="totalTripPayFeeInPercent")
    total_commissions_in_percent_with_refund: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="All amounts that are not of type SALE", alias="totalCommissionsInPercentWithRefund")
    total_commissions_in_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="All amounts that are not of type SALE before a refund was applied", alias="totalCommissionsInPercent")
    total_fees_and_commissions_in_percent_with_refund: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="All amounts that are not of type SALE", alias="totalFeesAndCommissionsInPercentWithRefund")
    total_fees_and_commissions_in_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="All amounts that are not of type SALE before a refund was applied", alias="totalFeesAndCommissionsInPercent")
    original_fees_in_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="All amounts that are not of type SALE before a refund was applied", alias="originalFeesInPercent")
    original_affiliate_agency_fees_in_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Affiliate agent fee in percent", alias="originalAffiliateAgencyFeesInPercent")
    original_supplier_agency_fees_in_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Supplier agent fee in percent", alias="originalSupplierAgencyFeesInPercent")
    original_commissions_in_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="All amounts that are not of type SALE before a refund was applied", alias="originalCommissionsInPercent")
    net_total_customers_source_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in source currency that is fees and commission.", alias="netTotalCustomersSourceAmount")
    net_total_customers_capture_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in capture currency the affiliate is owed.", alias="netTotalCustomersCaptureAmount")
    net_total_customers_display_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in display currency the affiliate is owed.", alias="netTotalCustomersDisplayAmount")
    net_total_customers_supplier_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in supplier currency the affiliate is owed.", alias="netTotalCustomersSupplierAmount")
    net_total_customers_internal_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in internal currency the affiliate is owed.", alias="netTotalCustomersInternalAmount")
    total_affiliate_agency_fees_source_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in source currency owed affiliate agency.", alias="totalAffiliateAgencyFeesSourceAmount")
    total_affiliate_agency_fees_capture_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in capture currency owed affiliate agency.", alias="totalAffiliateAgencyFeesCaptureAmount")
    total_affiliate_agency_fees_display_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in display currency owed affiliate agency.", alias="totalAffiliateAgencyFeesDisplayAmount")
    total_affiliate_agency_fees_supplier_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in supplier currency owed affiliate agency.", alias="totalAffiliateAgencyFeesSupplierAmount")
    total_affiliate_agency_fees_internal_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in internal currency owed affiliate agency.", alias="totalAffiliateAgencyFeesInternalAmount")
    total_supplier_agency_fees_source_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in source currency owed supplier agency.", alias="totalSupplierAgencyFeesSourceAmount")
    total_supplier_agency_fees_capture_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in capture currency owed supplier agency.", alias="totalSupplierAgencyFeesCaptureAmount")
    total_supplier_agency_fees_display_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in display currency owed supplier agency.", alias="totalSupplierAgencyFeesDisplayAmount")
    total_supplier_agency_fees_supplier_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in supplier currency owed supplier agency.", alias="totalSupplierAgencyFeesSupplierAmount")
    total_supplier_agency_fees_internal_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in internal currency owed supplier agency.", alias="totalSupplierAgencyFeesInternalAmount")
    net_total_affiliate_agency_fees_source_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in source currency owed affiliate agency.", alias="netTotalAffiliateAgencyFeesSourceAmount")
    net_total_affiliate_agency_fees_capture_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in capture currency owed affiliate agency.", alias="netTotalAffiliateAgencyFeesCaptureAmount")
    net_total_affiliate_agency_fees_display_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in display currency owed affiliate agency.", alias="netTotalAffiliateAgencyFeesDisplayAmount")
    net_total_affiliate_agency_fees_supplier_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in supplier currency owed affiliate agency.", alias="netTotalAffiliateAgencyFeesSupplierAmount")
    net_total_affiliate_agency_fees_internal_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in internal currency owed affiliate agency.", alias="netTotalAffiliateAgencyFeesInternalAmount")
    net_total_supplier_agency_fees_source_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in source currency owed supplier agency.", alias="netTotalSupplierAgencyFeesSourceAmount")
    net_total_supplier_agency_fees_capture_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in capture currency owed supplier agency.", alias="netTotalSupplierAgencyFeesCaptureAmount")
    net_total_supplier_agency_fees_display_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in display currency owed supplier agency.", alias="netTotalSupplierAgencyFeesDisplayAmount")
    net_total_supplier_agency_fees_supplier_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in supplier currency owed supplier agency.", alias="netTotalSupplierAgencyFeesSupplierAmount")
    net_total_supplier_agency_fees_internal_amount: Optional[CustomMonetaryAmount] = Field(default=None, description="Returns the total amount in internal currency owed supplier agency.", alias="netTotalSupplierAgencyFeesInternalAmount")
    has_refunds: Optional[StrictBool] = Field(default=None, description="Indicates whether any refund in any state is present.", alias="hasRefunds")
    has_successful_refunds: Optional[StrictBool] = Field(default=None, description="Indicates whether a successful refund is present.", alias="hasSuccessfulRefunds")
    has_pending_refunds: Optional[StrictBool] = Field(default=None, description="Indicates whether a pending refund is present.", alias="hasPendingRefunds")
    has_failed_refunds: Optional[StrictBool] = Field(default=None, description="Indicates whether a failed refund is present.", alias="hasFailedRefunds")
    platform_identifier: Optional[StrictStr] = Field(default=None, description="Returns the account identifier for the beneficiary taking a platform fee", alias="platformIdentifier")
    total_funds_grouped_by_beneficiary: Optional[List[BeneficiarySupplierDetails]] = Field(default=None, description="Returns all the beneficiaries in this contract with their total amounts", alias="totalFundsGroupedByBeneficiary")
    total_tokens_earned: Optional[StrictInt] = Field(default=None, description="Total amount of tokens minted on this contract.", alias="totalTokensEarned")
    self_acquiring: Optional[StrictBool] = Field(default=None, alias="selfAcquiring")
    lodging: Optional[BookingContractItemSupplierDetails] = Field(default=None, description="Returns the lodging item only.")
    cancellable_by_agent: Optional[StrictBool] = Field(default=None, description="Whether the booking can still be cancelled completely by an agent.", alias="cancellableByAgent")
    cancellable_by_supplier: Optional[StrictBool] = Field(default=None, description="Whether the booking can still be cancelled completely by the supplier.", alias="cancellableBySupplier")
    cancellable_by_traveler: Optional[StrictBool] = Field(default=None, description="Whether the booking can still be cancelled completely by the traveller.", alias="cancellableByTraveler")
    fully_refunded: Optional[StrictBool] = Field(default=None, alias="fullyRefunded")
    cancellable_with_no_charges: Optional[StrictBool] = Field(default=None, description="Whether the cancellation comes at no cost to the traveler.", alias="cancellableWithNoCharges")
    is_cancellable_with_potential_charges: Optional[StrictBool] = Field(default=None, description="Whether a cancellation comes with partial charges. I.e. Only some of the items in contract are not fully refundable.", alias="isCancellableWithPotentialCharges")
    __properties: ClassVar[List[str]] = ["bookingContractIdentifier", "createdDate", "lastUpdate", "federatedOrganizationIdentifier", "federatedOrganizationName", "user", "ipAddress", "traceId", "sourceUrl", "identifier", "supplierIdentifier", "supplierName", "displayPriceQuote", "supplierPriceQuote", "internalPriceQuote", "capturePriceQuote", "itemList", "externalSupplierIdentifier", "externalSupplierBookingCode", "payment", "cancelled", "cancelledOn", "canceller", "cancellationType", "cancellerUserIdentifier", "cancelReason", "fundsProcessed", "refunds", "payouts", "sourceCurrency", "displayCurrency", "supplierCurrency", "internalCurrency", "captureCurrency", "sourceAmount", "displayAmount", "supplierAmount", "internalAmount", "captureAmount", "sourceAmountRefundModifier", "displayAmountRefundModifier", "supplierAmountRefundModifier", "internalAmountRefundModifier", "captureAmountRefundModifier", "netSourceAmount", "netDisplayAmount", "netSupplierAmount", "netInternalAmount", "netCaptureAmount", "metadata", "netCommissionableTotalSourceAmount", "netCommissionableTotalCaptureAmount", "netCommissionableTotalDisplayAmount", "netCommissionableTotalSupplierAmount", "netCommissionableTotalInternalAmount", "netTotalFeesAndCommissionsSourceAmount", "netTotalFeesAndCommissionsCaptureAmount", "netTotalFeesAndCommissionsDisplayAmount", "netTotalFeesAndCommissionsSupplierAmount", "netTotalFeesAndCommissionsInternalAmount", "netTotalFeesSourceAmount", "netTotalFeesCaptureAmount", "netTotalFeesDisplayAmount", "netTotalFeesSupplierAmount", "netTotalFeesInternalAmount", "netTotalTripPayFeeSourceAmount", "netTotalTripPayFeeCaptureAmount", "netTotalTripPayFeeDisplayAmount", "netTotalTripPayFeeSupplierAmount", "netTotalTripPayFeeInternalAmount", "netTotalSalesSourceAmount", "netTotalSalesCaptureAmount", "netTotalSalesDisplayAmount", "netTotalSalesSupplierAmount", "netTotalSalesInternalAmount", "commissionableTotalSourceAmount", "commissionableTotalCaptureAmount", "commissionableTotalDisplayAmount", "commissionableTotalSupplierAmount", "commissionableTotalInternalAmount", "totalFeesAndCommissionsSourceAmount", "totalFeesAndCommissionsCaptureAmount", "totalFeesAndCommissionsDisplayAmount", "totalFeesAndCommissionsSupplierAmount", "totalFeesAndCommissionsInternalAmount", "totalFeesSourceAmount", "totalFeesCaptureAmount", "totalFeesDisplayAmount", "totalFeesSupplierAmount", "totalFeesInternalAmount", "totalTripPayFeeSourceAmount", "totalTripPayFeeCaptureAmount", "totalTripPayFeeDisplayAmount", "totalTripPayFeeSupplierAmount", "totalTripPayFeeInternalAmount", "totalSalesSourceAmount", "totalSalesCaptureAmount", "totalSalesDisplayAmount", "totalSalesSupplierAmount", "totalSalesInternalAmount", "fundsAvailableDate", "totalFeesInPercentWithRefund", "totalFeesInPercent", "totalTripPayFeeInPercentWithRefund", "totalTripPayFeeInPercent", "totalCommissionsInPercentWithRefund", "totalCommissionsInPercent", "totalFeesAndCommissionsInPercentWithRefund", "totalFeesAndCommissionsInPercent", "originalFeesInPercent", "originalAffiliateAgencyFeesInPercent", "originalSupplierAgencyFeesInPercent", "originalCommissionsInPercent", "netTotalCustomersSourceAmount", "netTotalCustomersCaptureAmount", "netTotalCustomersDisplayAmount", "netTotalCustomersSupplierAmount", "netTotalCustomersInternalAmount", "totalAffiliateAgencyFeesSourceAmount", "totalAffiliateAgencyFeesCaptureAmount", "totalAffiliateAgencyFeesDisplayAmount", "totalAffiliateAgencyFeesSupplierAmount", "totalAffiliateAgencyFeesInternalAmount", "totalSupplierAgencyFeesSourceAmount", "totalSupplierAgencyFeesCaptureAmount", "totalSupplierAgencyFeesDisplayAmount", "totalSupplierAgencyFeesSupplierAmount", "totalSupplierAgencyFeesInternalAmount", "netTotalAffiliateAgencyFeesSourceAmount", "netTotalAffiliateAgencyFeesCaptureAmount", "netTotalAffiliateAgencyFeesDisplayAmount", "netTotalAffiliateAgencyFeesSupplierAmount", "netTotalAffiliateAgencyFeesInternalAmount", "netTotalSupplierAgencyFeesSourceAmount", "netTotalSupplierAgencyFeesCaptureAmount", "netTotalSupplierAgencyFeesDisplayAmount", "netTotalSupplierAgencyFeesSupplierAmount", "netTotalSupplierAgencyFeesInternalAmount", "hasRefunds", "hasSuccessfulRefunds", "hasPendingRefunds", "hasFailedRefunds", "platformIdentifier", "totalFundsGroupedByBeneficiary", "totalTokensEarned", "selfAcquiring", "lodging", "cancellableByAgent", "cancellableBySupplier", "cancellableByTraveler", "fullyRefunded", "cancellableWithNoCharges", "isCancellableWithPotentialCharges"]

    @field_validator('canceller')
    def canceller_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['SALES_CHANNEL', 'SUPPLIER', 'TRAVELER', 'ACQUIRER', 'ADMINISTRATOR']):
            raise ValueError("must be one of enum values ('SALES_CHANNEL', 'SUPPLIER', 'TRAVELER', 'ACQUIRER', 'ADMINISTRATOR')")
        return value

    @field_validator('cancellation_type')
    def cancellation_type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['DUPLICATE', 'CANCELLATION', 'NO_SHOW', 'CC_INVALID', 'CC_INSUFFICIENT', 'DISCRETIONARY']):
            raise ValueError("must be one of enum values ('DUPLICATE', 'CANCELLATION', 'NO_SHOW', 'CC_INVALID', 'CC_INSUFFICIENT', 'DISCRETIONARY')")
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
        """Create an instance of BookingContractSupplierDetails from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of user
        if self.user:
            _dict['user'] = self.user.to_dict()
        # override the default output from pydantic by calling `to_dict()` of display_price_quote
        if self.display_price_quote:
            _dict['displayPriceQuote'] = self.display_price_quote.to_dict()
        # override the default output from pydantic by calling `to_dict()` of supplier_price_quote
        if self.supplier_price_quote:
            _dict['supplierPriceQuote'] = self.supplier_price_quote.to_dict()
        # override the default output from pydantic by calling `to_dict()` of internal_price_quote
        if self.internal_price_quote:
            _dict['internalPriceQuote'] = self.internal_price_quote.to_dict()
        # override the default output from pydantic by calling `to_dict()` of capture_price_quote
        if self.capture_price_quote:
            _dict['capturePriceQuote'] = self.capture_price_quote.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in item_list (list)
        _items = []
        if self.item_list:
            for _item_item_list in self.item_list:
                if _item_item_list:
                    _items.append(_item_item_list.to_dict())
            _dict['itemList'] = _items
        # override the default output from pydantic by calling `to_dict()` of payment
        if self.payment:
            _dict['payment'] = self.payment.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in refunds (list)
        _items = []
        if self.refunds:
            for _item_refunds in self.refunds:
                if _item_refunds:
                    _items.append(_item_refunds.to_dict())
            _dict['refunds'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in payouts (list)
        _items = []
        if self.payouts:
            for _item_payouts in self.payouts:
                if _item_payouts:
                    _items.append(_item_payouts.to_dict())
            _dict['payouts'] = _items
        # override the default output from pydantic by calling `to_dict()` of net_commissionable_total_source_amount
        if self.net_commissionable_total_source_amount:
            _dict['netCommissionableTotalSourceAmount'] = self.net_commissionable_total_source_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_commissionable_total_capture_amount
        if self.net_commissionable_total_capture_amount:
            _dict['netCommissionableTotalCaptureAmount'] = self.net_commissionable_total_capture_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_commissionable_total_display_amount
        if self.net_commissionable_total_display_amount:
            _dict['netCommissionableTotalDisplayAmount'] = self.net_commissionable_total_display_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_commissionable_total_supplier_amount
        if self.net_commissionable_total_supplier_amount:
            _dict['netCommissionableTotalSupplierAmount'] = self.net_commissionable_total_supplier_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_commissionable_total_internal_amount
        if self.net_commissionable_total_internal_amount:
            _dict['netCommissionableTotalInternalAmount'] = self.net_commissionable_total_internal_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_fees_and_commissions_source_amount
        if self.net_total_fees_and_commissions_source_amount:
            _dict['netTotalFeesAndCommissionsSourceAmount'] = self.net_total_fees_and_commissions_source_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_fees_and_commissions_capture_amount
        if self.net_total_fees_and_commissions_capture_amount:
            _dict['netTotalFeesAndCommissionsCaptureAmount'] = self.net_total_fees_and_commissions_capture_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_fees_and_commissions_display_amount
        if self.net_total_fees_and_commissions_display_amount:
            _dict['netTotalFeesAndCommissionsDisplayAmount'] = self.net_total_fees_and_commissions_display_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_fees_and_commissions_supplier_amount
        if self.net_total_fees_and_commissions_supplier_amount:
            _dict['netTotalFeesAndCommissionsSupplierAmount'] = self.net_total_fees_and_commissions_supplier_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_fees_and_commissions_internal_amount
        if self.net_total_fees_and_commissions_internal_amount:
            _dict['netTotalFeesAndCommissionsInternalAmount'] = self.net_total_fees_and_commissions_internal_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_fees_source_amount
        if self.net_total_fees_source_amount:
            _dict['netTotalFeesSourceAmount'] = self.net_total_fees_source_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_fees_capture_amount
        if self.net_total_fees_capture_amount:
            _dict['netTotalFeesCaptureAmount'] = self.net_total_fees_capture_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_fees_display_amount
        if self.net_total_fees_display_amount:
            _dict['netTotalFeesDisplayAmount'] = self.net_total_fees_display_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_fees_supplier_amount
        if self.net_total_fees_supplier_amount:
            _dict['netTotalFeesSupplierAmount'] = self.net_total_fees_supplier_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_fees_internal_amount
        if self.net_total_fees_internal_amount:
            _dict['netTotalFeesInternalAmount'] = self.net_total_fees_internal_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_trip_pay_fee_source_amount
        if self.net_total_trip_pay_fee_source_amount:
            _dict['netTotalTripPayFeeSourceAmount'] = self.net_total_trip_pay_fee_source_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_trip_pay_fee_capture_amount
        if self.net_total_trip_pay_fee_capture_amount:
            _dict['netTotalTripPayFeeCaptureAmount'] = self.net_total_trip_pay_fee_capture_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_trip_pay_fee_display_amount
        if self.net_total_trip_pay_fee_display_amount:
            _dict['netTotalTripPayFeeDisplayAmount'] = self.net_total_trip_pay_fee_display_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_trip_pay_fee_supplier_amount
        if self.net_total_trip_pay_fee_supplier_amount:
            _dict['netTotalTripPayFeeSupplierAmount'] = self.net_total_trip_pay_fee_supplier_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_trip_pay_fee_internal_amount
        if self.net_total_trip_pay_fee_internal_amount:
            _dict['netTotalTripPayFeeInternalAmount'] = self.net_total_trip_pay_fee_internal_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_sales_source_amount
        if self.net_total_sales_source_amount:
            _dict['netTotalSalesSourceAmount'] = self.net_total_sales_source_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_sales_capture_amount
        if self.net_total_sales_capture_amount:
            _dict['netTotalSalesCaptureAmount'] = self.net_total_sales_capture_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_sales_display_amount
        if self.net_total_sales_display_amount:
            _dict['netTotalSalesDisplayAmount'] = self.net_total_sales_display_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_sales_supplier_amount
        if self.net_total_sales_supplier_amount:
            _dict['netTotalSalesSupplierAmount'] = self.net_total_sales_supplier_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_sales_internal_amount
        if self.net_total_sales_internal_amount:
            _dict['netTotalSalesInternalAmount'] = self.net_total_sales_internal_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of commissionable_total_source_amount
        if self.commissionable_total_source_amount:
            _dict['commissionableTotalSourceAmount'] = self.commissionable_total_source_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of commissionable_total_capture_amount
        if self.commissionable_total_capture_amount:
            _dict['commissionableTotalCaptureAmount'] = self.commissionable_total_capture_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of commissionable_total_display_amount
        if self.commissionable_total_display_amount:
            _dict['commissionableTotalDisplayAmount'] = self.commissionable_total_display_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of commissionable_total_supplier_amount
        if self.commissionable_total_supplier_amount:
            _dict['commissionableTotalSupplierAmount'] = self.commissionable_total_supplier_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of commissionable_total_internal_amount
        if self.commissionable_total_internal_amount:
            _dict['commissionableTotalInternalAmount'] = self.commissionable_total_internal_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_fees_and_commissions_source_amount
        if self.total_fees_and_commissions_source_amount:
            _dict['totalFeesAndCommissionsSourceAmount'] = self.total_fees_and_commissions_source_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_fees_and_commissions_capture_amount
        if self.total_fees_and_commissions_capture_amount:
            _dict['totalFeesAndCommissionsCaptureAmount'] = self.total_fees_and_commissions_capture_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_fees_and_commissions_display_amount
        if self.total_fees_and_commissions_display_amount:
            _dict['totalFeesAndCommissionsDisplayAmount'] = self.total_fees_and_commissions_display_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_fees_and_commissions_supplier_amount
        if self.total_fees_and_commissions_supplier_amount:
            _dict['totalFeesAndCommissionsSupplierAmount'] = self.total_fees_and_commissions_supplier_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_fees_and_commissions_internal_amount
        if self.total_fees_and_commissions_internal_amount:
            _dict['totalFeesAndCommissionsInternalAmount'] = self.total_fees_and_commissions_internal_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_fees_source_amount
        if self.total_fees_source_amount:
            _dict['totalFeesSourceAmount'] = self.total_fees_source_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_fees_capture_amount
        if self.total_fees_capture_amount:
            _dict['totalFeesCaptureAmount'] = self.total_fees_capture_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_fees_display_amount
        if self.total_fees_display_amount:
            _dict['totalFeesDisplayAmount'] = self.total_fees_display_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_fees_supplier_amount
        if self.total_fees_supplier_amount:
            _dict['totalFeesSupplierAmount'] = self.total_fees_supplier_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_fees_internal_amount
        if self.total_fees_internal_amount:
            _dict['totalFeesInternalAmount'] = self.total_fees_internal_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_trip_pay_fee_source_amount
        if self.total_trip_pay_fee_source_amount:
            _dict['totalTripPayFeeSourceAmount'] = self.total_trip_pay_fee_source_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_trip_pay_fee_capture_amount
        if self.total_trip_pay_fee_capture_amount:
            _dict['totalTripPayFeeCaptureAmount'] = self.total_trip_pay_fee_capture_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_trip_pay_fee_display_amount
        if self.total_trip_pay_fee_display_amount:
            _dict['totalTripPayFeeDisplayAmount'] = self.total_trip_pay_fee_display_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_trip_pay_fee_supplier_amount
        if self.total_trip_pay_fee_supplier_amount:
            _dict['totalTripPayFeeSupplierAmount'] = self.total_trip_pay_fee_supplier_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_trip_pay_fee_internal_amount
        if self.total_trip_pay_fee_internal_amount:
            _dict['totalTripPayFeeInternalAmount'] = self.total_trip_pay_fee_internal_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_sales_source_amount
        if self.total_sales_source_amount:
            _dict['totalSalesSourceAmount'] = self.total_sales_source_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_sales_capture_amount
        if self.total_sales_capture_amount:
            _dict['totalSalesCaptureAmount'] = self.total_sales_capture_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_sales_display_amount
        if self.total_sales_display_amount:
            _dict['totalSalesDisplayAmount'] = self.total_sales_display_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_sales_supplier_amount
        if self.total_sales_supplier_amount:
            _dict['totalSalesSupplierAmount'] = self.total_sales_supplier_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_sales_internal_amount
        if self.total_sales_internal_amount:
            _dict['totalSalesInternalAmount'] = self.total_sales_internal_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_customers_source_amount
        if self.net_total_customers_source_amount:
            _dict['netTotalCustomersSourceAmount'] = self.net_total_customers_source_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_customers_capture_amount
        if self.net_total_customers_capture_amount:
            _dict['netTotalCustomersCaptureAmount'] = self.net_total_customers_capture_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_customers_display_amount
        if self.net_total_customers_display_amount:
            _dict['netTotalCustomersDisplayAmount'] = self.net_total_customers_display_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_customers_supplier_amount
        if self.net_total_customers_supplier_amount:
            _dict['netTotalCustomersSupplierAmount'] = self.net_total_customers_supplier_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_customers_internal_amount
        if self.net_total_customers_internal_amount:
            _dict['netTotalCustomersInternalAmount'] = self.net_total_customers_internal_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_affiliate_agency_fees_source_amount
        if self.total_affiliate_agency_fees_source_amount:
            _dict['totalAffiliateAgencyFeesSourceAmount'] = self.total_affiliate_agency_fees_source_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_affiliate_agency_fees_capture_amount
        if self.total_affiliate_agency_fees_capture_amount:
            _dict['totalAffiliateAgencyFeesCaptureAmount'] = self.total_affiliate_agency_fees_capture_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_affiliate_agency_fees_display_amount
        if self.total_affiliate_agency_fees_display_amount:
            _dict['totalAffiliateAgencyFeesDisplayAmount'] = self.total_affiliate_agency_fees_display_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_affiliate_agency_fees_supplier_amount
        if self.total_affiliate_agency_fees_supplier_amount:
            _dict['totalAffiliateAgencyFeesSupplierAmount'] = self.total_affiliate_agency_fees_supplier_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_affiliate_agency_fees_internal_amount
        if self.total_affiliate_agency_fees_internal_amount:
            _dict['totalAffiliateAgencyFeesInternalAmount'] = self.total_affiliate_agency_fees_internal_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_supplier_agency_fees_source_amount
        if self.total_supplier_agency_fees_source_amount:
            _dict['totalSupplierAgencyFeesSourceAmount'] = self.total_supplier_agency_fees_source_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_supplier_agency_fees_capture_amount
        if self.total_supplier_agency_fees_capture_amount:
            _dict['totalSupplierAgencyFeesCaptureAmount'] = self.total_supplier_agency_fees_capture_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_supplier_agency_fees_display_amount
        if self.total_supplier_agency_fees_display_amount:
            _dict['totalSupplierAgencyFeesDisplayAmount'] = self.total_supplier_agency_fees_display_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_supplier_agency_fees_supplier_amount
        if self.total_supplier_agency_fees_supplier_amount:
            _dict['totalSupplierAgencyFeesSupplierAmount'] = self.total_supplier_agency_fees_supplier_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_supplier_agency_fees_internal_amount
        if self.total_supplier_agency_fees_internal_amount:
            _dict['totalSupplierAgencyFeesInternalAmount'] = self.total_supplier_agency_fees_internal_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_affiliate_agency_fees_source_amount
        if self.net_total_affiliate_agency_fees_source_amount:
            _dict['netTotalAffiliateAgencyFeesSourceAmount'] = self.net_total_affiliate_agency_fees_source_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_affiliate_agency_fees_capture_amount
        if self.net_total_affiliate_agency_fees_capture_amount:
            _dict['netTotalAffiliateAgencyFeesCaptureAmount'] = self.net_total_affiliate_agency_fees_capture_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_affiliate_agency_fees_display_amount
        if self.net_total_affiliate_agency_fees_display_amount:
            _dict['netTotalAffiliateAgencyFeesDisplayAmount'] = self.net_total_affiliate_agency_fees_display_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_affiliate_agency_fees_supplier_amount
        if self.net_total_affiliate_agency_fees_supplier_amount:
            _dict['netTotalAffiliateAgencyFeesSupplierAmount'] = self.net_total_affiliate_agency_fees_supplier_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_affiliate_agency_fees_internal_amount
        if self.net_total_affiliate_agency_fees_internal_amount:
            _dict['netTotalAffiliateAgencyFeesInternalAmount'] = self.net_total_affiliate_agency_fees_internal_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_supplier_agency_fees_source_amount
        if self.net_total_supplier_agency_fees_source_amount:
            _dict['netTotalSupplierAgencyFeesSourceAmount'] = self.net_total_supplier_agency_fees_source_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_supplier_agency_fees_capture_amount
        if self.net_total_supplier_agency_fees_capture_amount:
            _dict['netTotalSupplierAgencyFeesCaptureAmount'] = self.net_total_supplier_agency_fees_capture_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_supplier_agency_fees_display_amount
        if self.net_total_supplier_agency_fees_display_amount:
            _dict['netTotalSupplierAgencyFeesDisplayAmount'] = self.net_total_supplier_agency_fees_display_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_supplier_agency_fees_supplier_amount
        if self.net_total_supplier_agency_fees_supplier_amount:
            _dict['netTotalSupplierAgencyFeesSupplierAmount'] = self.net_total_supplier_agency_fees_supplier_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of net_total_supplier_agency_fees_internal_amount
        if self.net_total_supplier_agency_fees_internal_amount:
            _dict['netTotalSupplierAgencyFeesInternalAmount'] = self.net_total_supplier_agency_fees_internal_amount.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in total_funds_grouped_by_beneficiary (list)
        _items = []
        if self.total_funds_grouped_by_beneficiary:
            for _item_total_funds_grouped_by_beneficiary in self.total_funds_grouped_by_beneficiary:
                if _item_total_funds_grouped_by_beneficiary:
                    _items.append(_item_total_funds_grouped_by_beneficiary.to_dict())
            _dict['totalFundsGroupedByBeneficiary'] = _items
        # override the default output from pydantic by calling `to_dict()` of lodging
        if self.lodging:
            _dict['lodging'] = self.lodging.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of BookingContractSupplierDetails from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "bookingContractIdentifier": obj.get("bookingContractIdentifier"),
            "createdDate": obj.get("createdDate"),
            "lastUpdate": obj.get("lastUpdate"),
            "federatedOrganizationIdentifier": obj.get("federatedOrganizationIdentifier"),
            "federatedOrganizationName": obj.get("federatedOrganizationName"),
            "user": AuthenticatedUserSupplierDetails.from_dict(obj["user"]) if obj.get("user") is not None else None,
            "ipAddress": obj.get("ipAddress"),
            "traceId": obj.get("traceId"),
            "sourceUrl": obj.get("sourceUrl"),
            "identifier": obj.get("identifier"),
            "supplierIdentifier": obj.get("supplierIdentifier"),
            "supplierName": obj.get("supplierName"),
            "displayPriceQuote": QuoteLightweightSupplierDetails.from_dict(obj["displayPriceQuote"]) if obj.get("displayPriceQuote") is not None else None,
            "supplierPriceQuote": QuoteLightweightSupplierDetails.from_dict(obj["supplierPriceQuote"]) if obj.get("supplierPriceQuote") is not None else None,
            "internalPriceQuote": QuoteLightweightSupplierDetails.from_dict(obj["internalPriceQuote"]) if obj.get("internalPriceQuote") is not None else None,
            "capturePriceQuote": QuoteLightweightSupplierDetails.from_dict(obj["capturePriceQuote"]) if obj.get("capturePriceQuote") is not None else None,
            "itemList": [BookingContractItemSupplierDetails.from_dict(_item) for _item in obj["itemList"]] if obj.get("itemList") is not None else None,
            "externalSupplierIdentifier": obj.get("externalSupplierIdentifier"),
            "externalSupplierBookingCode": obj.get("externalSupplierBookingCode"),
            "payment": BookingContractPaymentDetailsSupplierDetails.from_dict(obj["payment"]) if obj.get("payment") is not None else None,
            "cancelled": obj.get("cancelled") if obj.get("cancelled") is not None else False,
            "cancelledOn": obj.get("cancelledOn"),
            "canceller": obj.get("canceller"),
            "cancellationType": obj.get("cancellationType"),
            "cancellerUserIdentifier": obj.get("cancellerUserIdentifier"),
            "cancelReason": obj.get("cancelReason"),
            "fundsProcessed": obj.get("fundsProcessed"),
            "refunds": [RefundSupplierDetails.from_dict(_item) for _item in obj["refunds"]] if obj.get("refunds") is not None else None,
            "payouts": [PayoutSupplierDetails.from_dict(_item) for _item in obj["payouts"]] if obj.get("payouts") is not None else None,
            "sourceCurrency": obj.get("sourceCurrency"),
            "displayCurrency": obj.get("displayCurrency"),
            "supplierCurrency": obj.get("supplierCurrency"),
            "internalCurrency": obj.get("internalCurrency"),
            "captureCurrency": obj.get("captureCurrency"),
            "sourceAmount": obj.get("sourceAmount"),
            "displayAmount": obj.get("displayAmount"),
            "supplierAmount": obj.get("supplierAmount"),
            "internalAmount": obj.get("internalAmount"),
            "captureAmount": obj.get("captureAmount"),
            "sourceAmountRefundModifier": obj.get("sourceAmountRefundModifier"),
            "displayAmountRefundModifier": obj.get("displayAmountRefundModifier"),
            "supplierAmountRefundModifier": obj.get("supplierAmountRefundModifier"),
            "internalAmountRefundModifier": obj.get("internalAmountRefundModifier"),
            "captureAmountRefundModifier": obj.get("captureAmountRefundModifier"),
            "netSourceAmount": obj.get("netSourceAmount"),
            "netDisplayAmount": obj.get("netDisplayAmount"),
            "netSupplierAmount": obj.get("netSupplierAmount"),
            "netInternalAmount": obj.get("netInternalAmount"),
            "netCaptureAmount": obj.get("netCaptureAmount"),
            "metadata": obj.get("metadata"),
            "netCommissionableTotalSourceAmount": CustomMonetaryAmount.from_dict(obj["netCommissionableTotalSourceAmount"]) if obj.get("netCommissionableTotalSourceAmount") is not None else None,
            "netCommissionableTotalCaptureAmount": CustomMonetaryAmount.from_dict(obj["netCommissionableTotalCaptureAmount"]) if obj.get("netCommissionableTotalCaptureAmount") is not None else None,
            "netCommissionableTotalDisplayAmount": CustomMonetaryAmount.from_dict(obj["netCommissionableTotalDisplayAmount"]) if obj.get("netCommissionableTotalDisplayAmount") is not None else None,
            "netCommissionableTotalSupplierAmount": CustomMonetaryAmount.from_dict(obj["netCommissionableTotalSupplierAmount"]) if obj.get("netCommissionableTotalSupplierAmount") is not None else None,
            "netCommissionableTotalInternalAmount": CustomMonetaryAmount.from_dict(obj["netCommissionableTotalInternalAmount"]) if obj.get("netCommissionableTotalInternalAmount") is not None else None,
            "netTotalFeesAndCommissionsSourceAmount": CustomMonetaryAmount.from_dict(obj["netTotalFeesAndCommissionsSourceAmount"]) if obj.get("netTotalFeesAndCommissionsSourceAmount") is not None else None,
            "netTotalFeesAndCommissionsCaptureAmount": CustomMonetaryAmount.from_dict(obj["netTotalFeesAndCommissionsCaptureAmount"]) if obj.get("netTotalFeesAndCommissionsCaptureAmount") is not None else None,
            "netTotalFeesAndCommissionsDisplayAmount": CustomMonetaryAmount.from_dict(obj["netTotalFeesAndCommissionsDisplayAmount"]) if obj.get("netTotalFeesAndCommissionsDisplayAmount") is not None else None,
            "netTotalFeesAndCommissionsSupplierAmount": CustomMonetaryAmount.from_dict(obj["netTotalFeesAndCommissionsSupplierAmount"]) if obj.get("netTotalFeesAndCommissionsSupplierAmount") is not None else None,
            "netTotalFeesAndCommissionsInternalAmount": CustomMonetaryAmount.from_dict(obj["netTotalFeesAndCommissionsInternalAmount"]) if obj.get("netTotalFeesAndCommissionsInternalAmount") is not None else None,
            "netTotalFeesSourceAmount": CustomMonetaryAmount.from_dict(obj["netTotalFeesSourceAmount"]) if obj.get("netTotalFeesSourceAmount") is not None else None,
            "netTotalFeesCaptureAmount": CustomMonetaryAmount.from_dict(obj["netTotalFeesCaptureAmount"]) if obj.get("netTotalFeesCaptureAmount") is not None else None,
            "netTotalFeesDisplayAmount": CustomMonetaryAmount.from_dict(obj["netTotalFeesDisplayAmount"]) if obj.get("netTotalFeesDisplayAmount") is not None else None,
            "netTotalFeesSupplierAmount": CustomMonetaryAmount.from_dict(obj["netTotalFeesSupplierAmount"]) if obj.get("netTotalFeesSupplierAmount") is not None else None,
            "netTotalFeesInternalAmount": CustomMonetaryAmount.from_dict(obj["netTotalFeesInternalAmount"]) if obj.get("netTotalFeesInternalAmount") is not None else None,
            "netTotalTripPayFeeSourceAmount": CustomMonetaryAmount.from_dict(obj["netTotalTripPayFeeSourceAmount"]) if obj.get("netTotalTripPayFeeSourceAmount") is not None else None,
            "netTotalTripPayFeeCaptureAmount": CustomMonetaryAmount.from_dict(obj["netTotalTripPayFeeCaptureAmount"]) if obj.get("netTotalTripPayFeeCaptureAmount") is not None else None,
            "netTotalTripPayFeeDisplayAmount": CustomMonetaryAmount.from_dict(obj["netTotalTripPayFeeDisplayAmount"]) if obj.get("netTotalTripPayFeeDisplayAmount") is not None else None,
            "netTotalTripPayFeeSupplierAmount": CustomMonetaryAmount.from_dict(obj["netTotalTripPayFeeSupplierAmount"]) if obj.get("netTotalTripPayFeeSupplierAmount") is not None else None,
            "netTotalTripPayFeeInternalAmount": CustomMonetaryAmount.from_dict(obj["netTotalTripPayFeeInternalAmount"]) if obj.get("netTotalTripPayFeeInternalAmount") is not None else None,
            "netTotalSalesSourceAmount": CustomMonetaryAmount.from_dict(obj["netTotalSalesSourceAmount"]) if obj.get("netTotalSalesSourceAmount") is not None else None,
            "netTotalSalesCaptureAmount": CustomMonetaryAmount.from_dict(obj["netTotalSalesCaptureAmount"]) if obj.get("netTotalSalesCaptureAmount") is not None else None,
            "netTotalSalesDisplayAmount": CustomMonetaryAmount.from_dict(obj["netTotalSalesDisplayAmount"]) if obj.get("netTotalSalesDisplayAmount") is not None else None,
            "netTotalSalesSupplierAmount": CustomMonetaryAmount.from_dict(obj["netTotalSalesSupplierAmount"]) if obj.get("netTotalSalesSupplierAmount") is not None else None,
            "netTotalSalesInternalAmount": CustomMonetaryAmount.from_dict(obj["netTotalSalesInternalAmount"]) if obj.get("netTotalSalesInternalAmount") is not None else None,
            "commissionableTotalSourceAmount": CustomMonetaryAmount.from_dict(obj["commissionableTotalSourceAmount"]) if obj.get("commissionableTotalSourceAmount") is not None else None,
            "commissionableTotalCaptureAmount": CustomMonetaryAmount.from_dict(obj["commissionableTotalCaptureAmount"]) if obj.get("commissionableTotalCaptureAmount") is not None else None,
            "commissionableTotalDisplayAmount": CustomMonetaryAmount.from_dict(obj["commissionableTotalDisplayAmount"]) if obj.get("commissionableTotalDisplayAmount") is not None else None,
            "commissionableTotalSupplierAmount": CustomMonetaryAmount.from_dict(obj["commissionableTotalSupplierAmount"]) if obj.get("commissionableTotalSupplierAmount") is not None else None,
            "commissionableTotalInternalAmount": CustomMonetaryAmount.from_dict(obj["commissionableTotalInternalAmount"]) if obj.get("commissionableTotalInternalAmount") is not None else None,
            "totalFeesAndCommissionsSourceAmount": CustomMonetaryAmount.from_dict(obj["totalFeesAndCommissionsSourceAmount"]) if obj.get("totalFeesAndCommissionsSourceAmount") is not None else None,
            "totalFeesAndCommissionsCaptureAmount": CustomMonetaryAmount.from_dict(obj["totalFeesAndCommissionsCaptureAmount"]) if obj.get("totalFeesAndCommissionsCaptureAmount") is not None else None,
            "totalFeesAndCommissionsDisplayAmount": CustomMonetaryAmount.from_dict(obj["totalFeesAndCommissionsDisplayAmount"]) if obj.get("totalFeesAndCommissionsDisplayAmount") is not None else None,
            "totalFeesAndCommissionsSupplierAmount": CustomMonetaryAmount.from_dict(obj["totalFeesAndCommissionsSupplierAmount"]) if obj.get("totalFeesAndCommissionsSupplierAmount") is not None else None,
            "totalFeesAndCommissionsInternalAmount": CustomMonetaryAmount.from_dict(obj["totalFeesAndCommissionsInternalAmount"]) if obj.get("totalFeesAndCommissionsInternalAmount") is not None else None,
            "totalFeesSourceAmount": CustomMonetaryAmount.from_dict(obj["totalFeesSourceAmount"]) if obj.get("totalFeesSourceAmount") is not None else None,
            "totalFeesCaptureAmount": CustomMonetaryAmount.from_dict(obj["totalFeesCaptureAmount"]) if obj.get("totalFeesCaptureAmount") is not None else None,
            "totalFeesDisplayAmount": CustomMonetaryAmount.from_dict(obj["totalFeesDisplayAmount"]) if obj.get("totalFeesDisplayAmount") is not None else None,
            "totalFeesSupplierAmount": CustomMonetaryAmount.from_dict(obj["totalFeesSupplierAmount"]) if obj.get("totalFeesSupplierAmount") is not None else None,
            "totalFeesInternalAmount": CustomMonetaryAmount.from_dict(obj["totalFeesInternalAmount"]) if obj.get("totalFeesInternalAmount") is not None else None,
            "totalTripPayFeeSourceAmount": CustomMonetaryAmount.from_dict(obj["totalTripPayFeeSourceAmount"]) if obj.get("totalTripPayFeeSourceAmount") is not None else None,
            "totalTripPayFeeCaptureAmount": CustomMonetaryAmount.from_dict(obj["totalTripPayFeeCaptureAmount"]) if obj.get("totalTripPayFeeCaptureAmount") is not None else None,
            "totalTripPayFeeDisplayAmount": CustomMonetaryAmount.from_dict(obj["totalTripPayFeeDisplayAmount"]) if obj.get("totalTripPayFeeDisplayAmount") is not None else None,
            "totalTripPayFeeSupplierAmount": CustomMonetaryAmount.from_dict(obj["totalTripPayFeeSupplierAmount"]) if obj.get("totalTripPayFeeSupplierAmount") is not None else None,
            "totalTripPayFeeInternalAmount": CustomMonetaryAmount.from_dict(obj["totalTripPayFeeInternalAmount"]) if obj.get("totalTripPayFeeInternalAmount") is not None else None,
            "totalSalesSourceAmount": CustomMonetaryAmount.from_dict(obj["totalSalesSourceAmount"]) if obj.get("totalSalesSourceAmount") is not None else None,
            "totalSalesCaptureAmount": CustomMonetaryAmount.from_dict(obj["totalSalesCaptureAmount"]) if obj.get("totalSalesCaptureAmount") is not None else None,
            "totalSalesDisplayAmount": CustomMonetaryAmount.from_dict(obj["totalSalesDisplayAmount"]) if obj.get("totalSalesDisplayAmount") is not None else None,
            "totalSalesSupplierAmount": CustomMonetaryAmount.from_dict(obj["totalSalesSupplierAmount"]) if obj.get("totalSalesSupplierAmount") is not None else None,
            "totalSalesInternalAmount": CustomMonetaryAmount.from_dict(obj["totalSalesInternalAmount"]) if obj.get("totalSalesInternalAmount") is not None else None,
            "fundsAvailableDate": obj.get("fundsAvailableDate"),
            "totalFeesInPercentWithRefund": obj.get("totalFeesInPercentWithRefund"),
            "totalFeesInPercent": obj.get("totalFeesInPercent"),
            "totalTripPayFeeInPercentWithRefund": obj.get("totalTripPayFeeInPercentWithRefund"),
            "totalTripPayFeeInPercent": obj.get("totalTripPayFeeInPercent"),
            "totalCommissionsInPercentWithRefund": obj.get("totalCommissionsInPercentWithRefund"),
            "totalCommissionsInPercent": obj.get("totalCommissionsInPercent"),
            "totalFeesAndCommissionsInPercentWithRefund": obj.get("totalFeesAndCommissionsInPercentWithRefund"),
            "totalFeesAndCommissionsInPercent": obj.get("totalFeesAndCommissionsInPercent"),
            "originalFeesInPercent": obj.get("originalFeesInPercent"),
            "originalAffiliateAgencyFeesInPercent": obj.get("originalAffiliateAgencyFeesInPercent"),
            "originalSupplierAgencyFeesInPercent": obj.get("originalSupplierAgencyFeesInPercent"),
            "originalCommissionsInPercent": obj.get("originalCommissionsInPercent"),
            "netTotalCustomersSourceAmount": CustomMonetaryAmount.from_dict(obj["netTotalCustomersSourceAmount"]) if obj.get("netTotalCustomersSourceAmount") is not None else None,
            "netTotalCustomersCaptureAmount": CustomMonetaryAmount.from_dict(obj["netTotalCustomersCaptureAmount"]) if obj.get("netTotalCustomersCaptureAmount") is not None else None,
            "netTotalCustomersDisplayAmount": CustomMonetaryAmount.from_dict(obj["netTotalCustomersDisplayAmount"]) if obj.get("netTotalCustomersDisplayAmount") is not None else None,
            "netTotalCustomersSupplierAmount": CustomMonetaryAmount.from_dict(obj["netTotalCustomersSupplierAmount"]) if obj.get("netTotalCustomersSupplierAmount") is not None else None,
            "netTotalCustomersInternalAmount": CustomMonetaryAmount.from_dict(obj["netTotalCustomersInternalAmount"]) if obj.get("netTotalCustomersInternalAmount") is not None else None,
            "totalAffiliateAgencyFeesSourceAmount": CustomMonetaryAmount.from_dict(obj["totalAffiliateAgencyFeesSourceAmount"]) if obj.get("totalAffiliateAgencyFeesSourceAmount") is not None else None,
            "totalAffiliateAgencyFeesCaptureAmount": CustomMonetaryAmount.from_dict(obj["totalAffiliateAgencyFeesCaptureAmount"]) if obj.get("totalAffiliateAgencyFeesCaptureAmount") is not None else None,
            "totalAffiliateAgencyFeesDisplayAmount": CustomMonetaryAmount.from_dict(obj["totalAffiliateAgencyFeesDisplayAmount"]) if obj.get("totalAffiliateAgencyFeesDisplayAmount") is not None else None,
            "totalAffiliateAgencyFeesSupplierAmount": CustomMonetaryAmount.from_dict(obj["totalAffiliateAgencyFeesSupplierAmount"]) if obj.get("totalAffiliateAgencyFeesSupplierAmount") is not None else None,
            "totalAffiliateAgencyFeesInternalAmount": CustomMonetaryAmount.from_dict(obj["totalAffiliateAgencyFeesInternalAmount"]) if obj.get("totalAffiliateAgencyFeesInternalAmount") is not None else None,
            "totalSupplierAgencyFeesSourceAmount": CustomMonetaryAmount.from_dict(obj["totalSupplierAgencyFeesSourceAmount"]) if obj.get("totalSupplierAgencyFeesSourceAmount") is not None else None,
            "totalSupplierAgencyFeesCaptureAmount": CustomMonetaryAmount.from_dict(obj["totalSupplierAgencyFeesCaptureAmount"]) if obj.get("totalSupplierAgencyFeesCaptureAmount") is not None else None,
            "totalSupplierAgencyFeesDisplayAmount": CustomMonetaryAmount.from_dict(obj["totalSupplierAgencyFeesDisplayAmount"]) if obj.get("totalSupplierAgencyFeesDisplayAmount") is not None else None,
            "totalSupplierAgencyFeesSupplierAmount": CustomMonetaryAmount.from_dict(obj["totalSupplierAgencyFeesSupplierAmount"]) if obj.get("totalSupplierAgencyFeesSupplierAmount") is not None else None,
            "totalSupplierAgencyFeesInternalAmount": CustomMonetaryAmount.from_dict(obj["totalSupplierAgencyFeesInternalAmount"]) if obj.get("totalSupplierAgencyFeesInternalAmount") is not None else None,
            "netTotalAffiliateAgencyFeesSourceAmount": CustomMonetaryAmount.from_dict(obj["netTotalAffiliateAgencyFeesSourceAmount"]) if obj.get("netTotalAffiliateAgencyFeesSourceAmount") is not None else None,
            "netTotalAffiliateAgencyFeesCaptureAmount": CustomMonetaryAmount.from_dict(obj["netTotalAffiliateAgencyFeesCaptureAmount"]) if obj.get("netTotalAffiliateAgencyFeesCaptureAmount") is not None else None,
            "netTotalAffiliateAgencyFeesDisplayAmount": CustomMonetaryAmount.from_dict(obj["netTotalAffiliateAgencyFeesDisplayAmount"]) if obj.get("netTotalAffiliateAgencyFeesDisplayAmount") is not None else None,
            "netTotalAffiliateAgencyFeesSupplierAmount": CustomMonetaryAmount.from_dict(obj["netTotalAffiliateAgencyFeesSupplierAmount"]) if obj.get("netTotalAffiliateAgencyFeesSupplierAmount") is not None else None,
            "netTotalAffiliateAgencyFeesInternalAmount": CustomMonetaryAmount.from_dict(obj["netTotalAffiliateAgencyFeesInternalAmount"]) if obj.get("netTotalAffiliateAgencyFeesInternalAmount") is not None else None,
            "netTotalSupplierAgencyFeesSourceAmount": CustomMonetaryAmount.from_dict(obj["netTotalSupplierAgencyFeesSourceAmount"]) if obj.get("netTotalSupplierAgencyFeesSourceAmount") is not None else None,
            "netTotalSupplierAgencyFeesCaptureAmount": CustomMonetaryAmount.from_dict(obj["netTotalSupplierAgencyFeesCaptureAmount"]) if obj.get("netTotalSupplierAgencyFeesCaptureAmount") is not None else None,
            "netTotalSupplierAgencyFeesDisplayAmount": CustomMonetaryAmount.from_dict(obj["netTotalSupplierAgencyFeesDisplayAmount"]) if obj.get("netTotalSupplierAgencyFeesDisplayAmount") is not None else None,
            "netTotalSupplierAgencyFeesSupplierAmount": CustomMonetaryAmount.from_dict(obj["netTotalSupplierAgencyFeesSupplierAmount"]) if obj.get("netTotalSupplierAgencyFeesSupplierAmount") is not None else None,
            "netTotalSupplierAgencyFeesInternalAmount": CustomMonetaryAmount.from_dict(obj["netTotalSupplierAgencyFeesInternalAmount"]) if obj.get("netTotalSupplierAgencyFeesInternalAmount") is not None else None,
            "hasRefunds": obj.get("hasRefunds"),
            "hasSuccessfulRefunds": obj.get("hasSuccessfulRefunds"),
            "hasPendingRefunds": obj.get("hasPendingRefunds"),
            "hasFailedRefunds": obj.get("hasFailedRefunds"),
            "platformIdentifier": obj.get("platformIdentifier"),
            "totalFundsGroupedByBeneficiary": [BeneficiarySupplierDetails.from_dict(_item) for _item in obj["totalFundsGroupedByBeneficiary"]] if obj.get("totalFundsGroupedByBeneficiary") is not None else None,
            "totalTokensEarned": obj.get("totalTokensEarned"),
            "selfAcquiring": obj.get("selfAcquiring"),
            "lodging": BookingContractItemSupplierDetails.from_dict(obj["lodging"]) if obj.get("lodging") is not None else None,
            "cancellableByAgent": obj.get("cancellableByAgent"),
            "cancellableBySupplier": obj.get("cancellableBySupplier"),
            "cancellableByTraveler": obj.get("cancellableByTraveler"),
            "fullyRefunded": obj.get("fullyRefunded"),
            "cancellableWithNoCharges": obj.get("cancellableWithNoCharges"),
            "isCancellableWithPotentialCharges": obj.get("isCancellableWithPotentialCharges")
        })
        return _obj


