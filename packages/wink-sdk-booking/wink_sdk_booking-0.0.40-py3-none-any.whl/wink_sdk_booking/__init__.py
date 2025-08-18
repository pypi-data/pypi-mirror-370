# coding: utf-8

# flake8: noqa

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Booking Engine API Welcome to the Booking Engine API - A programmer-friendly way to book inventory that was found on our platform. This API lets you:  1. Shopping Cart: Manage shopping cart. 2. Checkout: Move shopping cart items through the payment workflow. 3. Booking: Move selected inventory through to booking completion. 4. Review: Leave a review after a completed stay.  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.18.5
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


__version__ = "0.0.40"

# import apis into sdk package
from wink_sdk_booking.api.booking_api import BookingApi
from wink_sdk_booking.api.checkout_api import CheckoutApi
from wink_sdk_booking.api.review_api import ReviewApi
from wink_sdk_booking.api.shopping_cart_api import ShoppingCartApi

# import ApiClient
from wink_sdk_booking.api_response import ApiResponse
from wink_sdk_booking.api_client import ApiClient
from wink_sdk_booking.configuration import Configuration
from wink_sdk_booking.exceptions import OpenApiException
from wink_sdk_booking.exceptions import ApiTypeError
from wink_sdk_booking.exceptions import ApiValueError
from wink_sdk_booking.exceptions import ApiKeyError
from wink_sdk_booking.exceptions import ApiAttributeError
from wink_sdk_booking.exceptions import ApiException

# import models into sdk package
from wink_sdk_booking.models.aggregate_descriptor_booker import AggregateDescriptorBooker
from wink_sdk_booking.models.authenticated_user_booker import AuthenticatedUserBooker
from wink_sdk_booking.models.bed_authenticated_entity import BedAuthenticatedEntity
from wink_sdk_booking.models.bed_booker import BedBooker
from wink_sdk_booking.models.bedroom_authenticated_entity import BedroomAuthenticatedEntity
from wink_sdk_booking.models.bedroom_booker import BedroomBooker
from wink_sdk_booking.models.bedroom_configuration_authenticated_entity import BedroomConfigurationAuthenticatedEntity
from wink_sdk_booking.models.bedroom_configuration_booker import BedroomConfigurationBooker
from wink_sdk_booking.models.beneficiary_booker import BeneficiaryBooker
from wink_sdk_booking.models.beneficiary_charge_booker import BeneficiaryChargeBooker
from wink_sdk_booking.models.booking_ancillary_booker import BookingAncillaryBooker
from wink_sdk_booking.models.booking_booker import BookingBooker
from wink_sdk_booking.models.booking_contract_booker import BookingContractBooker
from wink_sdk_booking.models.booking_contract_item_booker import BookingContractItemBooker
from wink_sdk_booking.models.booking_contract_payment_details_booker import BookingContractPaymentDetailsBooker
from wink_sdk_booking.models.booking_itinerary_booker import BookingItineraryBooker
from wink_sdk_booking.models.booking_itinerary_room_configuration_booker import BookingItineraryRoomConfigurationBooker
from wink_sdk_booking.models.booking_itinerary_room_configuration_child_booker import BookingItineraryRoomConfigurationChildBooker
from wink_sdk_booking.models.booking_user_booker import BookingUserBooker
from wink_sdk_booking.models.booking_user_request_authenticated_entity import BookingUserRequestAuthenticatedEntity
from wink_sdk_booking.models.booking_user_session_booker import BookingUserSessionBooker
from wink_sdk_booking.models.boolean_response_authenticated_entity import BooleanResponseAuthenticatedEntity
from wink_sdk_booking.models.boolean_response_booker import BooleanResponseBooker
from wink_sdk_booking.models.cancellation_detail_booker import CancellationDetailBooker
from wink_sdk_booking.models.cancellation_policy_exception_authenticated_entity import CancellationPolicyExceptionAuthenticatedEntity
from wink_sdk_booking.models.cancellation_policy_exception_booker import CancellationPolicyExceptionBooker
from wink_sdk_booking.models.cancellation_policy_exceptions_authenticated_entity import CancellationPolicyExceptionsAuthenticatedEntity
from wink_sdk_booking.models.cancellation_policy_exceptions_booker import CancellationPolicyExceptionsBooker
from wink_sdk_booking.models.cancellation_policy_lightweight_authenticated_entity import CancellationPolicyLightweightAuthenticatedEntity
from wink_sdk_booking.models.cancellation_policy_lightweight_booker import CancellationPolicyLightweightBooker
from wink_sdk_booking.models.checkout_request_authenticated_entity import CheckoutRequestAuthenticatedEntity
from wink_sdk_booking.models.checkout_response_authenticated_entity import CheckoutResponseAuthenticatedEntity
from wink_sdk_booking.models.child_authenticated_entity import ChildAuthenticatedEntity
from wink_sdk_booking.models.child_booker import ChildBooker
from wink_sdk_booking.models.commissionable_entry_booker import CommissionableEntryBooker
from wink_sdk_booking.models.composite_filter_descriptor_booker import CompositeFilterDescriptorBooker
from wink_sdk_booking.models.contact_authenticated_entity import ContactAuthenticatedEntity
from wink_sdk_booking.models.contact_booker import ContactBooker
from wink_sdk_booking.models.country_lightweight_booker import CountryLightweightBooker
from wink_sdk_booking.models.create_cart400_response import CreateCart400Response
from wink_sdk_booking.models.custom_monetary_amount import CustomMonetaryAmount
from wink_sdk_booking.models.customization_lightweight_booker import CustomizationLightweightBooker
from wink_sdk_booking.models.customization_theme_colors_booker import CustomizationThemeColorsBooker
from wink_sdk_booking.models.extra_charge_authenticated_entity import ExtraChargeAuthenticatedEntity
from wink_sdk_booking.models.extra_charge_booker import ExtraChargeBooker
from wink_sdk_booking.models.extra_charges_authenticated_entity import ExtraChargesAuthenticatedEntity
from wink_sdk_booking.models.extra_charges_booker import ExtraChargesBooker
from wink_sdk_booking.models.filter_descriptor_booker import FilterDescriptorBooker
from wink_sdk_booking.models.general_manager_authenticated_entity import GeneralManagerAuthenticatedEntity
from wink_sdk_booking.models.general_manager_booker import GeneralManagerBooker
from wink_sdk_booking.models.generic_error_message import GenericErrorMessage
from wink_sdk_booking.models.geo_json_point_authenticated_entity import GeoJsonPointAuthenticatedEntity
from wink_sdk_booking.models.geo_json_point_booker import GeoJsonPointBooker
from wink_sdk_booking.models.geo_name_lightweight_booker import GeoNameLightweightBooker
from wink_sdk_booking.models.group_descriptor_booker import GroupDescriptorBooker
from wink_sdk_booking.models.guest_room_lightweight_authenticated_entity import GuestRoomLightweightAuthenticatedEntity
from wink_sdk_booking.models.guest_room_lightweight_booker import GuestRoomLightweightBooker
from wink_sdk_booking.models.guest_user_booker import GuestUserBooker
from wink_sdk_booking.models.localized_description_authenticated_entity import LocalizedDescriptionAuthenticatedEntity
from wink_sdk_booking.models.localized_description_booker import LocalizedDescriptionBooker
from wink_sdk_booking.models.localized_price_authenticated_entity import LocalizedPriceAuthenticatedEntity
from wink_sdk_booking.models.localized_price_booker import LocalizedPriceBooker
from wink_sdk_booking.models.media_author_attribution_authenticated_entity import MediaAuthorAttributionAuthenticatedEntity
from wink_sdk_booking.models.media_author_attribution_booker import MediaAuthorAttributionBooker
from wink_sdk_booking.models.page_booking_booker import PageBookingBooker
from wink_sdk_booking.models.pageable_object_booker import PageableObjectBooker
from wink_sdk_booking.models.payable_contract_response_authenticated_entity import PayableContractResponseAuthenticatedEntity
from wink_sdk_booking.models.payout_booker import PayoutBooker
from wink_sdk_booking.models.payout_fee_booker import PayoutFeeBooker
from wink_sdk_booking.models.perk_lightweight_authenticated_entity import PerkLightweightAuthenticatedEntity
from wink_sdk_booking.models.perk_lightweight_booker import PerkLightweightBooker
from wink_sdk_booking.models.personal_booker import PersonalBooker
from wink_sdk_booking.models.preferences_booker import PreferencesBooker
from wink_sdk_booking.models.profile_lightweight_booker import ProfileLightweightBooker
from wink_sdk_booking.models.profile_user_booker import ProfileUserBooker
from wink_sdk_booking.models.property_aggregate_lightweight_authenticated_entity import PropertyAggregateLightweightAuthenticatedEntity
from wink_sdk_booking.models.property_aggregate_lightweight_booker import PropertyAggregateLightweightBooker
from wink_sdk_booking.models.property_policy_authenticated_entity import PropertyPolicyAuthenticatedEntity
from wink_sdk_booking.models.property_policy_booker import PropertyPolicyBooker
from wink_sdk_booking.models.quote_lightweight_authenticated_entity import QuoteLightweightAuthenticatedEntity
from wink_sdk_booking.models.quote_lightweight_booker import QuoteLightweightBooker
from wink_sdk_booking.models.rate_plan_level_fee_authenticated_entity import RatePlanLevelFeeAuthenticatedEntity
from wink_sdk_booking.models.rate_plan_level_fee_booker import RatePlanLevelFeeBooker
from wink_sdk_booking.models.realtime_shopping_cart_authenticated_entity import RealtimeShoppingCartAuthenticatedEntity
from wink_sdk_booking.models.realtime_shopping_cart_item_authenticated_entity import RealtimeShoppingCartItemAuthenticatedEntity
from wink_sdk_booking.models.refund_booker import RefundBooker
from wink_sdk_booking.models.remove_entry_response_authenticated_entity import RemoveEntryResponseAuthenticatedEntity
from wink_sdk_booking.models.review_answer_authenticated_entity import ReviewAnswerAuthenticatedEntity
from wink_sdk_booking.models.review_answer_booker import ReviewAnswerBooker
from wink_sdk_booking.models.review_authenticated_entity import ReviewAuthenticatedEntity
from wink_sdk_booking.models.review_lightweight_booker import ReviewLightweightBooker
from wink_sdk_booking.models.review_template_authenticated_entity import ReviewTemplateAuthenticatedEntity
from wink_sdk_booking.models.review_user_authenticated_entity import ReviewUserAuthenticatedEntity
from wink_sdk_booking.models.review_user_booker import ReviewUserBooker
from wink_sdk_booking.models.room_configuration_authenticated_entity import RoomConfigurationAuthenticatedEntity
from wink_sdk_booking.models.room_configuration_booker import RoomConfigurationBooker
from wink_sdk_booking.models.room_configuration_price_rate_plan_authenticated_entity import RoomConfigurationPriceRatePlanAuthenticatedEntity
from wink_sdk_booking.models.room_configuration_price_rate_plan_booker import RoomConfigurationPriceRatePlanBooker
from wink_sdk_booking.models.room_stay_authenticated_entity import RoomStayAuthenticatedEntity
from wink_sdk_booking.models.room_stay_booker import RoomStayBooker
from wink_sdk_booking.models.simple_address_authenticated_entity import SimpleAddressAuthenticatedEntity
from wink_sdk_booking.models.simple_address_booker import SimpleAddressBooker
from wink_sdk_booking.models.simple_date_time_itinerary_booker import SimpleDateTimeItineraryBooker
from wink_sdk_booking.models.simple_description_authenticated_entity import SimpleDescriptionAuthenticatedEntity
from wink_sdk_booking.models.simple_description_booker import SimpleDescriptionBooker
from wink_sdk_booking.models.simple_multimedia_authenticated_entity import SimpleMultimediaAuthenticatedEntity
from wink_sdk_booking.models.simple_multimedia_booker import SimpleMultimediaBooker
from wink_sdk_booking.models.social_authenticated_entity import SocialAuthenticatedEntity
from wink_sdk_booking.models.social_booker import SocialBooker
from wink_sdk_booking.models.sort_descriptor_booker import SortDescriptorBooker
from wink_sdk_booking.models.sort_object_booker import SortObjectBooker
from wink_sdk_booking.models.state_booker import StateBooker
from wink_sdk_booking.models.stay_rate_authenticated_entity import StayRateAuthenticatedEntity
from wink_sdk_booking.models.stay_rate_booker import StayRateBooker
from wink_sdk_booking.models.sub_country_lightweight_booker import SubCountryLightweightBooker
from wink_sdk_booking.models.sub_sub_country_lightweight_booker import SubSubCountryLightweightBooker
from wink_sdk_booking.models.submit_review_answer_authenticated_entity import SubmitReviewAnswerAuthenticatedEntity
from wink_sdk_booking.models.submit_review_request_authenticated_entity import SubmitReviewRequestAuthenticatedEntity
from wink_sdk_booking.models.supplier_contract_item_policy_booker import SupplierContractItemPolicyBooker
from wink_sdk_booking.models.travel_inventory_recognition_authenticated_entity import TravelInventoryRecognitionAuthenticatedEntity
from wink_sdk_booking.models.travel_inventory_recognition_booker import TravelInventoryRecognitionBooker
from wink_sdk_booking.models.upsert_shopping_cart_item_request_authenticated_entity import UpsertShoppingCartItemRequestAuthenticatedEntity
