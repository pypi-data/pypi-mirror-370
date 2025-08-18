# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/engine-client): A single endpoint to retrieve whitelabel + customization information for the booking engine.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reactive): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant reactive widget for all other entities.   - [TripPay](/reactive): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Booking Engine API Welcome to the Booking Engine API - A programmer-friendly way to book inventory that was found on our platform. This API lets you:  1. Shopping Cart: Manage shopping cart. 2. Checkout: Move shopping cart items through the reactive workflow. 3. Booking: Move selected inventory through to booking completion. 4. Review: Leave a review after a completed stay.  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.16.4
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
from typing import Any, ClassVar, Dict, List, Union
from wink_sdk_booking.models.contact_authenticated_entity import ContactAuthenticatedEntity
from wink_sdk_booking.models.localized_price_authenticated_entity import LocalizedPriceAuthenticatedEntity
from wink_sdk_booking.models.simple_address_authenticated_entity import SimpleAddressAuthenticatedEntity
from typing import Optional, Set
from typing_extensions import Self

class BookingAncillaryAuthenticatedEntity(BaseModel):
    """
    Extra reservations of spas, meeting rooms etc that should accompany the room type booking.
    """ # noqa: E501
    identifier: StrictStr = Field(description="Ancillary identifier")
    hotel_identifier: StrictStr = Field(description="Hotel identifier", alias="hotelIdentifier")
    type_identifier: StrictStr = Field(description="Travel blocking identifier", alias="typeIdentifier")
    transactional_travel_inventory_identifier: StrictStr = Field(description="Travel blocking identifier", alias="transactionalTravelInventoryIdentifier")
    name: StrictStr = Field(description="Name of blocking")
    pricing_type: StrictStr = Field(description="Pricing type", alias="pricingType")
    type: StrictStr = Field(description="Inventory type")
    price: LocalizedPriceAuthenticatedEntity
    start_date: datetime = Field(description="Date start time when reservation was made for.", alias="startDate")
    end_date: datetime = Field(description="Date end time when reservation was made for.", alias="endDate")
    attendees: StrictInt = Field(description="Number of guests that are part of this reservation.")
    image_identifier: StrictStr = Field(description="Cloudinary image identifier", alias="imageIdentifier")
    image_url: StrictStr = Field(description="Absolute URL to image of blocking", alias="imageUrl")
    localized_name: StrictStr = Field(description="Name of travel blocking in traveler language (if available). Defaults to English.", alias="localizedName")
    localized_description: StrictStr = Field(description="Description of travel blocking in traveler language (if available). Defaults to English.", alias="localizedDescription")
    contact: ContactAuthenticatedEntity
    address: SimpleAddressAuthenticatedEntity
    commissionable: StrictBool
    mandatory: StrictBool
    commission: Union[StrictFloat, StrictInt]
    __properties: ClassVar[List[str]] = ["identifier", "hotelIdentifier", "typeIdentifier", "transactionalTravelInventoryIdentifier", "name", "pricingType", "type", "price", "startDate", "endDate", "attendees", "imageIdentifier", "imageUrl", "localizedName", "localizedDescription", "contact", "address", "commissionable", "mandatory", "commission"]

    @field_validator('pricing_type')
    def pricing_type_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['PER_STAY', 'PER_DAY', 'PER_NIGHT', 'PER_USE', 'PER_HOUR', 'PER_PERSON', 'PER_PERSON_PER_NIGHT', 'PER_PERSON_PER_HOUR', 'PER_ADULT', 'PER_ADULT_PER_NIGHT', 'PER_ADULT_PER_HOUR', 'PER_CHILD', 'PER_CHILD_PER_NIGHT', 'PER_CHILD_PER_HOUR']):
            raise ValueError("must be one of enum values ('PER_STAY', 'PER_DAY', 'PER_NIGHT', 'PER_USE', 'PER_HOUR', 'PER_PERSON', 'PER_PERSON_PER_NIGHT', 'PER_PERSON_PER_HOUR', 'PER_ADULT', 'PER_ADULT_PER_NIGHT', 'PER_ADULT_PER_HOUR', 'PER_CHILD', 'PER_CHILD_PER_NIGHT', 'PER_CHILD_PER_HOUR')")
        return value

    @field_validator('type')
    def type_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['ROOM_TYPE_ANCILLARY', 'ADD_ON', 'MEETING_ROOM', 'SPA', 'RESTAURANT', 'ACTIVITY', 'ATTRACTION', 'PLACE']):
            raise ValueError("must be one of enum values ('ROOM_TYPE_ANCILLARY', 'ADD_ON', 'MEETING_ROOM', 'SPA', 'RESTAURANT', 'ACTIVITY', 'ATTRACTION', 'PLACE')")
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
        """Create an instance of BookingAncillaryAuthenticatedEntity from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of price
        if self.price:
            _dict['price'] = self.price.to_dict()
        # override the default output from pydantic by calling `to_dict()` of contact
        if self.contact:
            _dict['contact'] = self.contact.to_dict()
        # override the default output from pydantic by calling `to_dict()` of address
        if self.address:
            _dict['address'] = self.address.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of BookingAncillaryAuthenticatedEntity from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "identifier": obj.get("identifier"),
            "hotelIdentifier": obj.get("hotelIdentifier"),
            "typeIdentifier": obj.get("typeIdentifier"),
            "transactionalTravelInventoryIdentifier": obj.get("transactionalTravelInventoryIdentifier"),
            "name": obj.get("name"),
            "pricingType": obj.get("pricingType"),
            "type": obj.get("type"),
            "price": LocalizedPriceAuthenticatedEntity.from_dict(obj["price"]) if obj.get("price") is not None else None,
            "startDate": obj.get("startDate"),
            "endDate": obj.get("endDate"),
            "attendees": obj.get("attendees") if obj.get("attendees") is not None else 1,
            "imageIdentifier": obj.get("imageIdentifier"),
            "imageUrl": obj.get("imageUrl"),
            "localizedName": obj.get("localizedName"),
            "localizedDescription": obj.get("localizedDescription"),
            "contact": ContactAuthenticatedEntity.from_dict(obj["contact"]) if obj.get("contact") is not None else None,
            "address": SimpleAddressAuthenticatedEntity.from_dict(obj["address"]) if obj.get("address") is not None else None,
            "commissionable": obj.get("commissionable"),
            "mandatory": obj.get("mandatory"),
            "commission": obj.get("commission")
        })
        return _obj


