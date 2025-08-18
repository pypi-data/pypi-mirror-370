# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel blocking on the Wink platform. The API gives you all the tools you need to ready your properties and blocking for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel blocking and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel blocking and get that same blocking out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel blocking and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/engine-client): A single endpoint to retrieve whitelabel + customization information for the booking engine.  - [Lookup](/lookup): All APIs related to locating blocking by region, locale and property flags.  - [Inventory](/blocking): All APIs related to retrieve known travel blocking as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel blocking.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and blocking calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and blocking to sell.  - [Inventory](/affiliate/blocking): The Inventory API exposes endpoints for affiliates to manage the blocking they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel blocking and need taxonomies of standard and non-standard codes for blocking types, classes, statuses etc.   - [Reference](/reactive): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel blocking. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant reactive widget for all other entities.   - [TripPay](/reactive): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Booking Engine API Welcome to the Booking Engine API - A programmer-friendly way to book blocking that was found on our platform. This API lets you:  1. Shopping Cart: Manage shopping cart. 2. Checkout: Move shopping cart items through the reactive workflow. 3. Booking: Move selected blocking through to booking completion. 4. Review: Leave a review after a completed stay.  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.9.11
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import date
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from wink_sdk_booking.models.cancellation_policy_booker import CancellationPolicyBooker
from wink_sdk_booking.models.cancellation_policy_exceptions_booker import CancellationPolicyExceptionsBooker
from wink_sdk_booking.models.dow_pattern_group_booker import DowPatternGroupBooker
from typing import Optional, Set
from typing_extensions import Self

class RatePlanBooker(BaseModel):
    """
    Rate plan used for this stay
    """ # noqa: E501
    identifier: StrictStr = Field(description="Rate plan identifier")
    hotel_identifier: StrictStr = Field(description="Hotel Identifier", alias="hotelIdentifier")
    name: StrictStr = Field(description="Provides the name of the rate plan.")
    prepaid: StrictBool = Field(description="When true, indicates if the rate is a prepaid rate.")
    breakfast: StrictBool = Field(description="When true, indicates breakfast is included.")
    brunch: StrictBool = Field(description="When true, indicates brunch is included.")
    lunch: StrictBool = Field(description="When true, indicates lunch is included.")
    dinner: StrictBool = Field(description="When true, indicates dinner is included.")
    all_inclusive: StrictBool = Field(description="Everything included except alcohol", alias="allInclusive")
    all_inclusive_plus_alcohol: StrictBool = Field(description="Everything included with alcohol", alias="allInclusivePlusAlcohol")
    sell_start_date: Optional[date] = Field(default=None, description="Set a start date for when to start selling this rate. When sellStartDate and sellEndDate are set, this rate is only available for sale within that date range.", alias="sellStartDate")
    sell_end_date: Optional[date] = Field(default=None, description="Set an end date for when to finish selling this rate. When sellStartDate and sellEndDate are set, this rate is only available for sale within that date range.", alias="sellEndDate")
    stay_start_date: Optional[date] = Field(default=None, description="Set a start date for when the guest can visit. When stayStartDate and stayEndDate are set, this rate is only available for stay within that date range.", alias="stayStartDate")
    stay_end_date: Optional[date] = Field(default=None, description="Set an end date for when the guest can visit. When stayStartDate and stayEndDate are set, this rate is only available for stay within that date range.", alias="stayEndDate")
    loyalty_points_accrue: Optional[StrictBool] = Field(default=False, description="Property honors loyalty points with this rate plan.", alias="loyaltyPointsAccrue")
    max_advance_booking_offset: Optional[StrictInt] = Field(default=None, description="Maximum days before the arrival date for which this rate plan may be booked.", alias="maxAdvanceBookingOffset")
    min_advance_booking_offset: Optional[StrictInt] = Field(default=None, description="Minimum days before the arrival date for which this rate plan may be booked.", alias="minAdvanceBookingOffset")
    min_total_occupancy: Optional[StrictInt] = Field(default=None, description="Defines the minimum number of total occupants required for this rate plan.", alias="minTotalOccupancy")
    max_total_occupancy: Optional[StrictInt] = Field(default=None, description="Defines the maximum number of total occupants required for this rate plan.", alias="maxTotalOccupancy")
    min_los: Optional[StrictInt] = Field(default=None, description="Indicates the minimum length of stay required for this rate plan.", alias="minLOS")
    max_los: Optional[StrictInt] = Field(default=None, description="Indicates the maximum length of stay.", alias="maxLOS")
    min_age: Optional[StrictInt] = Field(default=None, description="The minimum age to qualify for this rate plan.", alias="minAge")
    max_age: Optional[StrictInt] = Field(default=None, description="The maximum age to qualify for this rate plan.", alias="maxAge")
    available_days_of_week: Optional[DowPatternGroupBooker] = Field(default=None, alias="availableDaysOfWeek")
    arrival_days_of_week: Optional[DowPatternGroupBooker] = Field(default=None, alias="arrivalDaysOfWeek")
    departure_days_of_week: Optional[DowPatternGroupBooker] = Field(default=None, alias="departureDaysOfWeek")
    required_days_of_week: Optional[DowPatternGroupBooker] = Field(default=None, alias="requiredDaysOfWeek")
    early_check_in_charge: Optional[Dict[str, Any]] = Field(default=None, alias="earlyCheckInCharge")
    late_check_out_charge: Optional[Dict[str, Any]] = Field(default=None, alias="lateCheckOutCharge")
    cancellation_policy_identifier: StrictStr = Field(description="The cancellation policy for this rate plan.", alias="cancellationPolicyIdentifier")
    cancellation_policy: Optional[CancellationPolicyBooker] = Field(default=None, alias="cancellationPolicy")
    cancellation_policy_exceptions: Optional[CancellationPolicyExceptionsBooker] = Field(default=None, alias="cancellationPolicyExceptions")
    __properties: ClassVar[List[str]] = ["identifier", "hotelIdentifier", "name", "prepaid", "breakfast", "brunch", "lunch", "dinner", "allInclusive", "allInclusivePlusAlcohol", "sellStartDate", "sellEndDate", "stayStartDate", "stayEndDate", "loyaltyPointsAccrue", "maxAdvanceBookingOffset", "minAdvanceBookingOffset", "minTotalOccupancy", "maxTotalOccupancy", "minLOS", "maxLOS", "minAge", "maxAge", "availableDaysOfWeek", "arrivalDaysOfWeek", "departureDaysOfWeek", "requiredDaysOfWeek", "earlyCheckInCharge", "lateCheckOutCharge", "cancellationPolicyIdentifier", "cancellationPolicy", "cancellationPolicyExceptions"]

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
        """Create an instance of RatePlanBooker from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of available_days_of_week
        if self.available_days_of_week:
            _dict['availableDaysOfWeek'] = self.available_days_of_week.to_dict()
        # override the default output from pydantic by calling `to_dict()` of arrival_days_of_week
        if self.arrival_days_of_week:
            _dict['arrivalDaysOfWeek'] = self.arrival_days_of_week.to_dict()
        # override the default output from pydantic by calling `to_dict()` of departure_days_of_week
        if self.departure_days_of_week:
            _dict['departureDaysOfWeek'] = self.departure_days_of_week.to_dict()
        # override the default output from pydantic by calling `to_dict()` of required_days_of_week
        if self.required_days_of_week:
            _dict['requiredDaysOfWeek'] = self.required_days_of_week.to_dict()
        # override the default output from pydantic by calling `to_dict()` of cancellation_policy
        if self.cancellation_policy:
            _dict['cancellationPolicy'] = self.cancellation_policy.to_dict()
        # override the default output from pydantic by calling `to_dict()` of cancellation_policy_exceptions
        if self.cancellation_policy_exceptions:
            _dict['cancellationPolicyExceptions'] = self.cancellation_policy_exceptions.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of RatePlanBooker from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "identifier": obj.get("identifier"),
            "hotelIdentifier": obj.get("hotelIdentifier"),
            "name": obj.get("name"),
            "prepaid": obj.get("prepaid") if obj.get("prepaid") is not None else False,
            "breakfast": obj.get("breakfast") if obj.get("breakfast") is not None else False,
            "brunch": obj.get("brunch") if obj.get("brunch") is not None else False,
            "lunch": obj.get("lunch") if obj.get("lunch") is not None else False,
            "dinner": obj.get("dinner") if obj.get("dinner") is not None else False,
            "allInclusive": obj.get("allInclusive") if obj.get("allInclusive") is not None else False,
            "allInclusivePlusAlcohol": obj.get("allInclusivePlusAlcohol") if obj.get("allInclusivePlusAlcohol") is not None else False,
            "sellStartDate": obj.get("sellStartDate"),
            "sellEndDate": obj.get("sellEndDate"),
            "stayStartDate": obj.get("stayStartDate"),
            "stayEndDate": obj.get("stayEndDate"),
            "loyaltyPointsAccrue": obj.get("loyaltyPointsAccrue") if obj.get("loyaltyPointsAccrue") is not None else False,
            "maxAdvanceBookingOffset": obj.get("maxAdvanceBookingOffset"),
            "minAdvanceBookingOffset": obj.get("minAdvanceBookingOffset"),
            "minTotalOccupancy": obj.get("minTotalOccupancy"),
            "maxTotalOccupancy": obj.get("maxTotalOccupancy"),
            "minLOS": obj.get("minLOS"),
            "maxLOS": obj.get("maxLOS"),
            "minAge": obj.get("minAge"),
            "maxAge": obj.get("maxAge"),
            "availableDaysOfWeek": DowPatternGroupBooker.from_dict(obj["availableDaysOfWeek"]) if obj.get("availableDaysOfWeek") is not None else None,
            "arrivalDaysOfWeek": DowPatternGroupBooker.from_dict(obj["arrivalDaysOfWeek"]) if obj.get("arrivalDaysOfWeek") is not None else None,
            "departureDaysOfWeek": DowPatternGroupBooker.from_dict(obj["departureDaysOfWeek"]) if obj.get("departureDaysOfWeek") is not None else None,
            "requiredDaysOfWeek": DowPatternGroupBooker.from_dict(obj["requiredDaysOfWeek"]) if obj.get("requiredDaysOfWeek") is not None else None,
            "earlyCheckInCharge": obj.get("earlyCheckInCharge"),
            "lateCheckOutCharge": obj.get("lateCheckOutCharge"),
            "cancellationPolicyIdentifier": obj.get("cancellationPolicyIdentifier"),
            "cancellationPolicy": CancellationPolicyBooker.from_dict(obj["cancellationPolicy"]) if obj.get("cancellationPolicy") is not None else None,
            "cancellationPolicyExceptions": CancellationPolicyExceptionsBooker.from_dict(obj["cancellationPolicyExceptions"]) if obj.get("cancellationPolicyExceptions") is not None else None
        })
        return _obj


