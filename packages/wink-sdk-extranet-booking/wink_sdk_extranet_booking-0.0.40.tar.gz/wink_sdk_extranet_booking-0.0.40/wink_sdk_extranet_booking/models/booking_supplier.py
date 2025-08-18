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
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional, Union
from wink_sdk_extranet_booking.models.booking_ancillary_supplier import BookingAncillarySupplier
from wink_sdk_extranet_booking.models.booking_contract_supplier import BookingContractSupplier
from wink_sdk_extranet_booking.models.booking_user_session_supplier import BookingUserSessionSupplier
from wink_sdk_extranet_booking.models.booking_user_supplier import BookingUserSupplier
from wink_sdk_extranet_booking.models.commissionable_entry_supplier import CommissionableEntrySupplier
from wink_sdk_extranet_booking.models.custom_monetary_amount import CustomMonetaryAmount
from wink_sdk_extranet_booking.models.customization_lightweight_supplier import CustomizationLightweightSupplier
from wink_sdk_extranet_booking.models.property_aggregate_lightweight_supplier import PropertyAggregateLightweightSupplier
from wink_sdk_extranet_booking.models.review_lightweight_supplier import ReviewLightweightSupplier
from wink_sdk_extranet_booking.models.room_stay_supplier import RoomStaySupplier
from wink_sdk_extranet_booking.models.social_supplier import SocialSupplier
from typing import Optional, Set
from typing_extensions import Self

class BookingSupplier(BaseModel):
    """
    BookingSupplier
    """ # noqa: E501
    id: Optional[StrictStr] = Field(default=None, description="Document UUID")
    created_date: Optional[datetime] = Field(default=None, description="Datetime this record was first created", alias="createdDate")
    last_update: Optional[datetime] = Field(default=None, description="Datetime this record was last updated", alias="lastUpdate")
    version: Optional[StrictInt] = Field(default=None, description="Version property that shows how many times this document has been persisted. Document will not persist if the version property is less than current version property in the system. Result in an optimistic locking exception.")
    creation: StrictStr = Field(description="Communicates whether the booking was created normally or if it failed or was just for testing.")
    group_identifier: StrictStr = Field(description="Unique record identifier for the collection of bookings that were made at the same time.", alias="groupIdentifier")
    customization: CustomizationLightweightSupplier = Field(description="Which customization configuration record did the entity application used to facilitate in making this booking happen.")
    booking_code: StrictStr = Field(description="Unique user-friendly booking geoname. This code should be used when corresponding with travelers.", alias="bookingCode")
    user: BookingUserSupplier = Field(description="User details for the authenticated person that made the booking.")
    user_session: BookingUserSessionSupplier = Field(description="User session state as it was when the user made the booking.", alias="userSession")
    server_url: StrictStr = Field(description="The URL the booking occurred", alias="serverUrl")
    socials: Optional[List[SocialSupplier]] = Field(default=None, description="List of all social network account property has for the traveler to get in touch.")
    review: Optional[ReviewLightweightSupplier] = Field(default=None, description="User review created by the traveler after the booking completed.")
    email_header_logo_url: StrictStr = Field(description="Full url of the image logo optimized for emails", alias="emailHeaderLogoUrl")
    logo_identifier: Optional[StrictStr] = Field(default=None, description="Logo cloudinary identifier for potential reuse", alias="logoIdentifier")
    hotel: PropertyAggregateLightweightSupplier = Field(description="Combined property data.")
    room_stay: Optional[RoomStaySupplier] = Field(default=None, description="All information about the room that was booked.", alias="roomStay")
    special_requests: Optional[StrictStr] = Field(default=None, description="Free text where the traveler can add a message to the property.", alias="specialRequests")
    comment: Optional[StrictStr] = Field(default=None, description="Internal comment field the platform can add and make available to channel manager partners.")
    early_check_in_charge: Optional[CustomMonetaryAmount] = Field(default=None, description="Early check-in charge fixed amount that is due if guest checks out early.", alias="earlyCheckInCharge")
    late_check_out_charge: Optional[CustomMonetaryAmount] = Field(default=None, description="Late check-out charge fixed amount that is due if guest checks out late.", alias="lateCheckOutCharge")
    early_check_in_charge_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Early check-in charge calculated in percent of first room night price.", alias="earlyCheckInChargePercent")
    late_check_out_charge_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Early check-in charge calculated in percent of first room night price.", alias="lateCheckOutChargePercent")
    hotel_image_url: StrictStr = Field(description="Absolute URL of hotel image that can be used as-is", alias="hotelImageUrl")
    room_image_url: StrictStr = Field(description="Absolute URL of room image that can be used as-is", alias="roomImageUrl")
    commission_list: Optional[List[CommissionableEntrySupplier]] = Field(default=None, description="List of all travel inventory entries that are due a commission to the affiliate.", alias="commissionList")
    ancillary_list: Optional[List[BookingAncillarySupplier]] = Field(default=None, alias="ancillaryList")
    booking_contract: Optional[BookingContractSupplier] = Field(default=None, description="Booking contract created by TripPay", alias="bookingContract")
    static_map_image_url: Optional[StrictStr] = Field(default=None, description="Url of map image that can be sent via email", alias="staticMapImageUrl")
    static_map_url: Optional[StrictStr] = Field(default=None, description="Url of map image location on Google Maps", alias="staticMapUrl")
    status: Optional[StrictStr] = Field(default=None, description="Convenience data point to show which status the booking currently has.")
    spas: Optional[List[BookingAncillarySupplier]] = Field(default=None, description="Spa reservation records.")
    meeting_rooms: Optional[List[BookingAncillarySupplier]] = Field(default=None, description="Meeting room reservation records.", alias="meetingRooms")
    restaurants: Optional[List[BookingAncillarySupplier]] = Field(default=None, description="Restaurant reservation records.")
    activities: Optional[List[BookingAncillarySupplier]] = Field(default=None, description="Activity reservation records.")
    attractions: Optional[List[BookingAncillarySupplier]] = Field(default=None, description="Attraction reservation records.")
    places: Optional[List[BookingAncillarySupplier]] = Field(default=None, description="Place reservation records.")
    room_type_ancillaries: Optional[List[BookingAncillarySupplier]] = Field(default=None, description="Room type ancillary records.", alias="roomTypeAncillaries")
    add_ons: Optional[List[BookingAncillarySupplier]] = Field(default=None, description="Add-on records.", alias="addOns")
    cancellable_by_agent: Optional[StrictBool] = Field(default=None, description="Whether the booking can still be cancelled completely by the agent.", alias="cancellableByAgent")
    rate_source: Optional[StrictStr] = Field(default=None, description="Rate origin. This is usually the property channel manager.", alias="rateSource")
    has_add_ons: Optional[StrictBool] = Field(default=None, description="Convenience data point to check if any add-on offers are in this booking.", alias="hasAddOns")
    cancellable_by_supplier: Optional[StrictBool] = Field(default=None, description="Whether the booking can still be cancelled completely by the supplier.", alias="cancellableBySupplier")
    cancellable_by_traveler: Optional[StrictBool] = Field(default=None, description="Whether the booking can still be cancelled completely by the traveller.", alias="cancellableByTraveler")
    has_breakfast: Optional[StrictBool] = Field(default=None, description="Convenience data point to get to breakfast quickly.", alias="hasBreakfast")
    has_brunch: Optional[StrictBool] = Field(default=None, description="Convenience data point to get to brunch quickly.", alias="hasBrunch")
    has_lunch: Optional[StrictBool] = Field(default=None, description="Convenience data point to get to lunch quickly.", alias="hasLunch")
    has_dinner: Optional[StrictBool] = Field(default=None, description="Convenience data point to get to dinner quickly.", alias="hasDinner")
    has_all_inclusive: Optional[StrictBool] = Field(default=None, description="Convenience data point to get to all-inclusive quickly.", alias="hasAllInclusive")
    has_all_inclusive_plus_alcohol: Optional[StrictBool] = Field(default=None, description="Convenience data point to get to all-inclusive with alcohol quickly.", alias="hasAllInclusivePlusAlcohol")
    has_room_type_ancillaries: Optional[StrictBool] = Field(default=None, description="Convenience data point to check if any room type ancillaries are in this booking.", alias="hasRoomTypeAncillaries")
    has_food: Optional[StrictBool] = Field(default=None, description="Convenience data point to check if any food is included in this booking.", alias="hasFood")
    has_restaurants: Optional[StrictBool] = Field(default=None, description="Convenience data point to check if any restaurant reservations are included in this booking.", alias="hasRestaurants")
    has_meeting_rooms: Optional[StrictBool] = Field(default=None, description="Convenience data point to check if any meeting room reservations are included in this booking.", alias="hasMeetingRooms")
    has_spas: Optional[StrictBool] = Field(default=None, description="Convenience data point to check if any spa reservations are included in this booking.", alias="hasSpas")
    has_activities: Optional[StrictBool] = Field(default=None, description="Convenience data point to check if any activity reservations are included in this booking.", alias="hasActivities")
    has_attractions: Optional[StrictBool] = Field(default=None, description="Convenience data point to check if any attractions reservations are included in this booking.", alias="hasAttractions")
    has_places: Optional[StrictBool] = Field(default=None, description="Convenience data point to check if any place reservations are included in this booking.", alias="hasPlaces")
    reporting_daily_rate_list: Optional[List[Any]] = Field(default=None, alias="reportingDailyRateList")
    reporting_ancillary_list: Optional[List[Any]] = Field(default=None, alias="reportingAncillaryList")
    reporting_extra_charge_list: Optional[List[Any]] = Field(default=None, alias="reportingExtraChargeList")
    __properties: ClassVar[List[str]] = ["id", "createdDate", "lastUpdate", "version", "creation", "groupIdentifier", "customization", "bookingCode", "user", "userSession", "serverUrl", "socials", "review", "emailHeaderLogoUrl", "logoIdentifier", "hotel", "roomStay", "specialRequests", "comment", "earlyCheckInCharge", "lateCheckOutCharge", "earlyCheckInChargePercent", "lateCheckOutChargePercent", "hotelImageUrl", "roomImageUrl", "commissionList", "ancillaryList", "bookingContract", "staticMapImageUrl", "staticMapUrl", "status", "spas", "meetingRooms", "restaurants", "activities", "attractions", "places", "roomTypeAncillaries", "addOns", "cancellableByAgent", "rateSource", "hasAddOns", "cancellableBySupplier", "cancellableByTraveler", "hasBreakfast", "hasBrunch", "hasLunch", "hasDinner", "hasAllInclusive", "hasAllInclusivePlusAlcohol", "hasRoomTypeAncillaries", "hasFood", "hasRestaurants", "hasMeetingRooms", "hasSpas", "hasActivities", "hasAttractions", "hasPlaces", "reportingDailyRateList", "reportingAncillaryList", "reportingExtraChargeList"]

    @field_validator('creation')
    def creation_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['NORMAL', 'TEST', 'FAILED']):
            raise ValueError("must be one of enum values ('NORMAL', 'TEST', 'FAILED')")
        return value

    @field_validator('status')
    def status_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['CANCELLED_BY_HOTEL', 'CANCELLED_BY_GUEST', 'CANCELLED_BY_ADMIN', 'CANCELLED_BY_SALES_CHANNEL', 'PAST', 'FUTURE', 'CANCELLED_BY_ACQUIRER', 'ACTIVE', 'FAILED', 'FULLY_REFUNDED']):
            raise ValueError("must be one of enum values ('CANCELLED_BY_HOTEL', 'CANCELLED_BY_GUEST', 'CANCELLED_BY_ADMIN', 'CANCELLED_BY_SALES_CHANNEL', 'PAST', 'FUTURE', 'CANCELLED_BY_ACQUIRER', 'ACTIVE', 'FAILED', 'FULLY_REFUNDED')")
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
        """Create an instance of BookingSupplier from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of customization
        if self.customization:
            _dict['customization'] = self.customization.to_dict()
        # override the default output from pydantic by calling `to_dict()` of user
        if self.user:
            _dict['user'] = self.user.to_dict()
        # override the default output from pydantic by calling `to_dict()` of user_session
        if self.user_session:
            _dict['userSession'] = self.user_session.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in socials (list)
        _items = []
        if self.socials:
            for _item_socials in self.socials:
                if _item_socials:
                    _items.append(_item_socials.to_dict())
            _dict['socials'] = _items
        # override the default output from pydantic by calling `to_dict()` of review
        if self.review:
            _dict['review'] = self.review.to_dict()
        # override the default output from pydantic by calling `to_dict()` of hotel
        if self.hotel:
            _dict['hotel'] = self.hotel.to_dict()
        # override the default output from pydantic by calling `to_dict()` of room_stay
        if self.room_stay:
            _dict['roomStay'] = self.room_stay.to_dict()
        # override the default output from pydantic by calling `to_dict()` of early_check_in_charge
        if self.early_check_in_charge:
            _dict['earlyCheckInCharge'] = self.early_check_in_charge.to_dict()
        # override the default output from pydantic by calling `to_dict()` of late_check_out_charge
        if self.late_check_out_charge:
            _dict['lateCheckOutCharge'] = self.late_check_out_charge.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in commission_list (list)
        _items = []
        if self.commission_list:
            for _item_commission_list in self.commission_list:
                if _item_commission_list:
                    _items.append(_item_commission_list.to_dict())
            _dict['commissionList'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in ancillary_list (list)
        _items = []
        if self.ancillary_list:
            for _item_ancillary_list in self.ancillary_list:
                if _item_ancillary_list:
                    _items.append(_item_ancillary_list.to_dict())
            _dict['ancillaryList'] = _items
        # override the default output from pydantic by calling `to_dict()` of booking_contract
        if self.booking_contract:
            _dict['bookingContract'] = self.booking_contract.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in spas (list)
        _items = []
        if self.spas:
            for _item_spas in self.spas:
                if _item_spas:
                    _items.append(_item_spas.to_dict())
            _dict['spas'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in meeting_rooms (list)
        _items = []
        if self.meeting_rooms:
            for _item_meeting_rooms in self.meeting_rooms:
                if _item_meeting_rooms:
                    _items.append(_item_meeting_rooms.to_dict())
            _dict['meetingRooms'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in restaurants (list)
        _items = []
        if self.restaurants:
            for _item_restaurants in self.restaurants:
                if _item_restaurants:
                    _items.append(_item_restaurants.to_dict())
            _dict['restaurants'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in activities (list)
        _items = []
        if self.activities:
            for _item_activities in self.activities:
                if _item_activities:
                    _items.append(_item_activities.to_dict())
            _dict['activities'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in attractions (list)
        _items = []
        if self.attractions:
            for _item_attractions in self.attractions:
                if _item_attractions:
                    _items.append(_item_attractions.to_dict())
            _dict['attractions'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in places (list)
        _items = []
        if self.places:
            for _item_places in self.places:
                if _item_places:
                    _items.append(_item_places.to_dict())
            _dict['places'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in room_type_ancillaries (list)
        _items = []
        if self.room_type_ancillaries:
            for _item_room_type_ancillaries in self.room_type_ancillaries:
                if _item_room_type_ancillaries:
                    _items.append(_item_room_type_ancillaries.to_dict())
            _dict['roomTypeAncillaries'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in add_ons (list)
        _items = []
        if self.add_ons:
            for _item_add_ons in self.add_ons:
                if _item_add_ons:
                    _items.append(_item_add_ons.to_dict())
            _dict['addOns'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of BookingSupplier from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "createdDate": obj.get("createdDate"),
            "lastUpdate": obj.get("lastUpdate"),
            "version": obj.get("version"),
            "creation": obj.get("creation") if obj.get("creation") is not None else 'NORMAL',
            "groupIdentifier": obj.get("groupIdentifier"),
            "customization": CustomizationLightweightSupplier.from_dict(obj["customization"]) if obj.get("customization") is not None else None,
            "bookingCode": obj.get("bookingCode"),
            "user": BookingUserSupplier.from_dict(obj["user"]) if obj.get("user") is not None else None,
            "userSession": BookingUserSessionSupplier.from_dict(obj["userSession"]) if obj.get("userSession") is not None else None,
            "serverUrl": obj.get("serverUrl"),
            "socials": [SocialSupplier.from_dict(_item) for _item in obj["socials"]] if obj.get("socials") is not None else None,
            "review": ReviewLightweightSupplier.from_dict(obj["review"]) if obj.get("review") is not None else None,
            "emailHeaderLogoUrl": obj.get("emailHeaderLogoUrl"),
            "logoIdentifier": obj.get("logoIdentifier"),
            "hotel": PropertyAggregateLightweightSupplier.from_dict(obj["hotel"]) if obj.get("hotel") is not None else None,
            "roomStay": RoomStaySupplier.from_dict(obj["roomStay"]) if obj.get("roomStay") is not None else None,
            "specialRequests": obj.get("specialRequests"),
            "comment": obj.get("comment"),
            "earlyCheckInCharge": CustomMonetaryAmount.from_dict(obj["earlyCheckInCharge"]) if obj.get("earlyCheckInCharge") is not None else None,
            "lateCheckOutCharge": CustomMonetaryAmount.from_dict(obj["lateCheckOutCharge"]) if obj.get("lateCheckOutCharge") is not None else None,
            "earlyCheckInChargePercent": obj.get("earlyCheckInChargePercent"),
            "lateCheckOutChargePercent": obj.get("lateCheckOutChargePercent"),
            "hotelImageUrl": obj.get("hotelImageUrl"),
            "roomImageUrl": obj.get("roomImageUrl"),
            "commissionList": [CommissionableEntrySupplier.from_dict(_item) for _item in obj["commissionList"]] if obj.get("commissionList") is not None else None,
            "ancillaryList": [BookingAncillarySupplier.from_dict(_item) for _item in obj["ancillaryList"]] if obj.get("ancillaryList") is not None else None,
            "bookingContract": BookingContractSupplier.from_dict(obj["bookingContract"]) if obj.get("bookingContract") is not None else None,
            "staticMapImageUrl": obj.get("staticMapImageUrl"),
            "staticMapUrl": obj.get("staticMapUrl"),
            "status": obj.get("status"),
            "spas": [BookingAncillarySupplier.from_dict(_item) for _item in obj["spas"]] if obj.get("spas") is not None else None,
            "meetingRooms": [BookingAncillarySupplier.from_dict(_item) for _item in obj["meetingRooms"]] if obj.get("meetingRooms") is not None else None,
            "restaurants": [BookingAncillarySupplier.from_dict(_item) for _item in obj["restaurants"]] if obj.get("restaurants") is not None else None,
            "activities": [BookingAncillarySupplier.from_dict(_item) for _item in obj["activities"]] if obj.get("activities") is not None else None,
            "attractions": [BookingAncillarySupplier.from_dict(_item) for _item in obj["attractions"]] if obj.get("attractions") is not None else None,
            "places": [BookingAncillarySupplier.from_dict(_item) for _item in obj["places"]] if obj.get("places") is not None else None,
            "roomTypeAncillaries": [BookingAncillarySupplier.from_dict(_item) for _item in obj["roomTypeAncillaries"]] if obj.get("roomTypeAncillaries") is not None else None,
            "addOns": [BookingAncillarySupplier.from_dict(_item) for _item in obj["addOns"]] if obj.get("addOns") is not None else None,
            "cancellableByAgent": obj.get("cancellableByAgent"),
            "rateSource": obj.get("rateSource"),
            "hasAddOns": obj.get("hasAddOns"),
            "cancellableBySupplier": obj.get("cancellableBySupplier"),
            "cancellableByTraveler": obj.get("cancellableByTraveler"),
            "hasBreakfast": obj.get("hasBreakfast"),
            "hasBrunch": obj.get("hasBrunch"),
            "hasLunch": obj.get("hasLunch"),
            "hasDinner": obj.get("hasDinner"),
            "hasAllInclusive": obj.get("hasAllInclusive"),
            "hasAllInclusivePlusAlcohol": obj.get("hasAllInclusivePlusAlcohol"),
            "hasRoomTypeAncillaries": obj.get("hasRoomTypeAncillaries"),
            "hasFood": obj.get("hasFood"),
            "hasRestaurants": obj.get("hasRestaurants"),
            "hasMeetingRooms": obj.get("hasMeetingRooms"),
            "hasSpas": obj.get("hasSpas"),
            "hasActivities": obj.get("hasActivities"),
            "hasAttractions": obj.get("hasAttractions"),
            "hasPlaces": obj.get("hasPlaces"),
            "reportingDailyRateList": obj.get("reportingDailyRateList"),
            "reportingAncillaryList": obj.get("reportingAncillaryList"),
            "reportingExtraChargeList": obj.get("reportingExtraChargeList")
        })
        return _obj


