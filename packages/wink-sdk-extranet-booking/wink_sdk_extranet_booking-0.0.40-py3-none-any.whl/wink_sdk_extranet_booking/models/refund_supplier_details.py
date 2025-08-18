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

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from wink_sdk_extranet_booking.models.custom_monetary_amount import CustomMonetaryAmount
from typing import Optional, Set
from typing_extensions import Self

class RefundSupplierDetails(BaseModel):
    """
    Refund objects allow you to refund a charge that has previously been created but not yet refunded. Funds will be refunded to the credit or debit card that was originally charged.
    """ # noqa: E501
    identifier: Annotated[str, Field(min_length=1, strict=True)] = Field(description="A unique identifier")
    acquirer_refund_identifier: Optional[StrictStr] = Field(default=None, description="The acquirer refund identifier. Will get attached once it comes in on the webhook.", alias="acquirerRefundIdentifier")
    requested_by_identifier: Optional[StrictStr] = Field(default=None, description="The SSO person / entity that requested the refund.", alias="requestedByIdentifier")
    refund: CustomMonetaryAmount = Field(description="The amount refunded")
    created: datetime = Field(description="When the amount was refunded")
    description: Annotated[str, Field(min_length=1, strict=True)] = Field(description="A description of the refund that can be displayed to booker")
    reason_type: StrictStr = Field(description="A description of the refund that can be displayed to booker", alias="reasonType")
    cancel_on_refund: StrictStr = Field(description="Whether to cancel the booking alongside requesting a refund.", alias="cancelOnRefund")
    status_type: StrictStr = Field(description="Status of the refund", alias="statusType")
    request_type: StrictStr = Field(description="The entity making the refund request", alias="requestType")
    request_status: StrictStr = Field(description="Status of the refund request", alias="requestStatus")
    request_response: StrictStr = Field(description="Admin may choose to respond to the refund request made by the hotel", alias="requestResponse")
    receipt_url: Optional[StrictStr] = Field(default=None, description="This is the receipt url that contains a friendly web confirmation page. Comes in on the webhook.", alias="receiptUrl")
    retries: Optional[StrictInt] = Field(default=0, description="In case a TripPay admin has to go in and re-send the refund request to Stripe, we want to not to the same calculations again when a retry is executed so we keep track of retries here.")
    allocation: Optional[StrictStr] = Field(default='EQUAL_DISTRIBUTION', description="The type of refund determines how the funds are deducted each beneficiary.")
    __properties: ClassVar[List[str]] = ["identifier", "acquirerRefundIdentifier", "requestedByIdentifier", "refund", "created", "description", "reasonType", "cancelOnRefund", "statusType", "requestType", "requestStatus", "requestResponse", "receiptUrl", "retries", "allocation"]

    @field_validator('reason_type')
    def reason_type_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['DUPLICATE', 'FRAUDULENT', 'REQUESTED_BY_CUSTOMER', 'GUEST_COMPLAINT', 'GUEST_BOOKED_INCORRECT_DATE', 'GUEST_SICK', 'OVERBOOKING', 'EMERGENCY', 'FLIGHT_CANCELLED', 'DEATH_IN_FAMILY', 'OTHER', 'EXPIRED_UNCAPTURED_CHARGE']):
            raise ValueError("must be one of enum values ('DUPLICATE', 'FRAUDULENT', 'REQUESTED_BY_CUSTOMER', 'GUEST_COMPLAINT', 'GUEST_BOOKED_INCORRECT_DATE', 'GUEST_SICK', 'OVERBOOKING', 'EMERGENCY', 'FLIGHT_CANCELLED', 'DEATH_IN_FAMILY', 'OTHER', 'EXPIRED_UNCAPTURED_CHARGE')")
        return value

    @field_validator('cancel_on_refund')
    def cancel_on_refund_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['NONE', 'CANCEL_ON_SUCCESSFUL_REFUND', 'CANCEL_REGARDLESS']):
            raise ValueError("must be one of enum values ('NONE', 'CANCEL_ON_SUCCESSFUL_REFUND', 'CANCEL_REGARDLESS')")
        return value

    @field_validator('status_type')
    def status_type_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['PENDING', 'SUCCEEDED', 'CANCELED', 'REQUIRES_ACTION', 'FAILED']):
            raise ValueError("must be one of enum values ('PENDING', 'SUCCEEDED', 'CANCELED', 'REQUIRES_ACTION', 'FAILED')")
        return value

    @field_validator('request_type')
    def request_type_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['BY_SUPPLIER', 'BY_ADMIN', 'BY_STRIPE', 'BY_SYSTEM', 'BY_AGENT']):
            raise ValueError("must be one of enum values ('BY_SUPPLIER', 'BY_ADMIN', 'BY_STRIPE', 'BY_SYSTEM', 'BY_AGENT')")
        return value

    @field_validator('request_status')
    def request_status_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['PENDING', 'APPROVED', 'REJECTED']):
            raise ValueError("must be one of enum values ('PENDING', 'APPROVED', 'REJECTED')")
        return value

    @field_validator('allocation')
    def allocation_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['FROM_SALE_ONLY', 'EQUAL_DISTRIBUTION', 'CUSTOMERS_ONLY']):
            raise ValueError("must be one of enum values ('FROM_SALE_ONLY', 'EQUAL_DISTRIBUTION', 'CUSTOMERS_ONLY')")
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
        """Create an instance of RefundSupplierDetails from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of refund
        if self.refund:
            _dict['refund'] = self.refund.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of RefundSupplierDetails from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "identifier": obj.get("identifier"),
            "acquirerRefundIdentifier": obj.get("acquirerRefundIdentifier"),
            "requestedByIdentifier": obj.get("requestedByIdentifier"),
            "refund": CustomMonetaryAmount.from_dict(obj["refund"]) if obj.get("refund") is not None else None,
            "created": obj.get("created"),
            "description": obj.get("description"),
            "reasonType": obj.get("reasonType"),
            "cancelOnRefund": obj.get("cancelOnRefund"),
            "statusType": obj.get("statusType"),
            "requestType": obj.get("requestType"),
            "requestStatus": obj.get("requestStatus"),
            "requestResponse": obj.get("requestResponse"),
            "receiptUrl": obj.get("receiptUrl"),
            "retries": obj.get("retries") if obj.get("retries") is not None else 0,
            "allocation": obj.get("allocation") if obj.get("allocation") is not None else 'EQUAL_DISTRIBUTION'
        })
        return _obj


