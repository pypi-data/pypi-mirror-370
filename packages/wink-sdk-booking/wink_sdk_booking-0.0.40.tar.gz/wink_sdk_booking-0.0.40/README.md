# wink-sdk-booking
 # Introduction
 Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.
 Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.

 # Integrations
 We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.

 # Intended Audience
 Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.
 - Hotel chains
 - Hotel brands
 - Travel tech companies
 - Destination sites
 - Integrators
 - Aggregators
 - Destination management companies
 - Travel agencies
 - OTAs

 ## APIs
 Not every integrator needs every API. For that reason, we have separated APIs into context.

### Test API

 - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.

### Common APIs

- [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account.
- [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.

### Consume APIs
Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.

 - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.
 - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.
 - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..
 - [Booking](/booking): All APIs related to creating bookings on the platform.
 - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.

 ### Produce APIs
 Produce endpoints are for developers who want to create and manage travel inventory.

 #### Property
 - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.
 - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.
 - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.
 - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.
 - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.
 - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.
 - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.

 #### Affiliate
 - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.
 - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.
 - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.
 - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.
 - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.

 #### Rate provider
 - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.

 ### Taxonomy APIs
 Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.

 - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.

 ### Insight APIs
 Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.

 - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.

 ### Payment APIs
 Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.

 - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.

 ## SDKs
 We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).

 - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)

 ## Usage
 These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.

 ## Versioning
 We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.

 ## Release history
 - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md



# Booking Engine API
Welcome to the Booking Engine API - A programmer-friendly way to book inventory that was found on our platform. This API lets you:

1. Shopping Cart: Manage shopping cart.
2. Checkout: Move shopping cart items through the payment workflow.
3. Booking: Move selected inventory through to booking completion.
4. Review: Leave a review after a completed stay.

Browse the endpoints in the left navigation bar to get started.



This Python package is automatically generated by the [OpenAPI Generator](https://openapi-generator.tech) project:

- API version: 30.18.5
- Package version: 0.0.40
- Generator version: 7.12.0
- Build package: org.openapitools.codegen.languages.PythonClientCodegen

## Requirements.

Python 3.8+

## Installation & Usage
### pip install

You can install the package from PyPi using:
```sh
pip install wink_sdk_booking
```

Or you can install it directly from the repository using:
```sh
pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_booking&subdirectory=wink-sdk-booking
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_booking&subdirectory=wink_sdk_booking`)

Then import the package:
```python
import wink_sdk_booking
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import wink_sdk_booking
```

### Tests

Execute `pytest` to run the tests.

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import wink_sdk_booking
from wink_sdk_booking.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.wink.travel
# See configuration.py for a list of all supported configuration parameters.
configuration = wink_sdk_booking.Configuration(
    host = "https://api.wink.travel"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]


# Enter a context with an instance of the API client
with wink_sdk_booking.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = wink_sdk_booking.BookingApi(api_client)
    booking_identifier = 'booking-1' # str | Cancel booking by identifier
    cancellation_detail_booker = wink_sdk_booking.CancellationDetailBooker() # CancellationDetailBooker | 
    wink_version = 'wink_version_example' # str |  (optional)

    try:
        # Cancel Booking
        api_response = api_instance.cancel_booking(booking_identifier, cancellation_detail_booker, wink_version=wink_version)
        print("The response of BookingApi->cancel_booking:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling BookingApi->cancel_booking: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *https://api.wink.travel*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*BookingApi* | [**cancel_booking**](docs/BookingApi.md#cancel_booking) | **PATCH** /api/booking/{bookingIdentifier} | Cancel Booking
*BookingApi* | [**cancel_group_booking**](docs/BookingApi.md#cancel_group_booking) | **PATCH** /api/booking/group/{groupIdentifier} | Cancel Group Booking
*BookingApi* | [**resend_booking_confirmation_email**](docs/BookingApi.md#resend_booking_confirmation_email) | **PATCH** /api/booking/{bookingIdentifier}/resend | Resend Booking Confirmation
*BookingApi* | [**show_booking**](docs/BookingApi.md#show_booking) | **GET** /api/booking/{bookingIdentifier} | Show Booking
*BookingApi* | [**show_booking_by_transaction_id**](docs/BookingApi.md#show_booking_by_transaction_id) | **GET** /api/booking/tx/{transactionIdentifier} | Show Booking by TX ID
*BookingApi* | [**show_booking_grid**](docs/BookingApi.md#show_booking_grid) | **POST** /api/booking/grid | Search Bookings
*BookingApi* | [**show_bookings**](docs/BookingApi.md#show_bookings) | **GET** /api/booking/list | Show Booking List
*BookingApi* | [**show_bookings_by_review_state**](docs/BookingApi.md#show_bookings_by_review_state) | **GET** /api/booking/review/list | Show Bookings by Review
*BookingApi* | [**show_bookings_by_state**](docs/BookingApi.md#show_bookings_by_state) | **GET** /api/booking/state | Show Bookings by Time
*BookingApi* | [**show_grouped_bookings**](docs/BookingApi.md#show_grouped_bookings) | **GET** /api/booking/group/{groupIdentifier} | Show Grouped Bookings
*CheckoutApi* | [**checkout**](docs/CheckoutApi.md#checkout) | **POST** /api/checkout | Prepare reactive
*ReviewApi* | [**populate_review**](docs/ReviewApi.md#populate_review) | **GET** /api/booking/{bookingIdentifier}/review/questions | Show Review Template
*ReviewApi* | [**submit_review**](docs/ReviewApi.md#submit_review) | **POST** /api/booking/{bookingIdentifier}/review | Submit Review
*ShoppingCartApi* | [**create_cart**](docs/ShoppingCartApi.md#create_cart) | **POST** /api/shopping-cart | Create Shopping Cart
*ShoppingCartApi* | [**create_carts**](docs/ShoppingCartApi.md#create_carts) | **POST** /api/shopping-cart/list | Create Shopping Carts
*ShoppingCartApi* | [**delete_cart**](docs/ShoppingCartApi.md#delete_cart) | **DELETE** /api/shopping-cart/{shoppingCartIdentifier} | Remove Shopping Cart
*ShoppingCartApi* | [**delete_cart_item**](docs/ShoppingCartApi.md#delete_cart_item) | **DELETE** /api/shopping-cart/{shoppingCartIdentifier}/item/{shoppingCartItemIdentifier} | Remove Shopping Cart Item
*ShoppingCartApi* | [**delete_cart_item_ancillary**](docs/ShoppingCartApi.md#delete_cart_item_ancillary) | **DELETE** /api/shopping-cart/{shoppingCartIdentifier}/item/{shoppingCartItemIdentifier}/ancillary/{shoppingCartItemAncillaryIdentifier} | Remove Shopping Cart Item Ancillary
*ShoppingCartApi* | [**delete_carts**](docs/ShoppingCartApi.md#delete_carts) | **DELETE** /api/shopping-cart | Empty Shopping Carts
*ShoppingCartApi* | [**empty_cart**](docs/ShoppingCartApi.md#empty_cart) | **DELETE** /api/shopping-cart/{shoppingCartIdentifier}/empty | Empty Shopping Cart
*ShoppingCartApi* | [**show_cart**](docs/ShoppingCartApi.md#show_cart) | **GET** /api/shopping-cart/{shoppingCartIdentifier} | Show Shopping Cart
*ShoppingCartApi* | [**show_carts**](docs/ShoppingCartApi.md#show_carts) | **GET** /api/shopping-cart/list | Show Shopping Carts
*ShoppingCartApi* | [**update_cart_item**](docs/ShoppingCartApi.md#update_cart_item) | **PATCH** /api/shopping-cart/{shoppingCartIdentifier}/item/{shoppingCartItemIdentifier} | Update Shopping Cart Item


## Documentation For Models

 - [AggregateDescriptorBooker](docs/AggregateDescriptorBooker.md)
 - [AuthenticatedUserBooker](docs/AuthenticatedUserBooker.md)
 - [BedAuthenticatedEntity](docs/BedAuthenticatedEntity.md)
 - [BedBooker](docs/BedBooker.md)
 - [BedroomAuthenticatedEntity](docs/BedroomAuthenticatedEntity.md)
 - [BedroomBooker](docs/BedroomBooker.md)
 - [BedroomConfigurationAuthenticatedEntity](docs/BedroomConfigurationAuthenticatedEntity.md)
 - [BedroomConfigurationBooker](docs/BedroomConfigurationBooker.md)
 - [BeneficiaryBooker](docs/BeneficiaryBooker.md)
 - [BeneficiaryChargeBooker](docs/BeneficiaryChargeBooker.md)
 - [BookingAncillaryBooker](docs/BookingAncillaryBooker.md)
 - [BookingBooker](docs/BookingBooker.md)
 - [BookingContractBooker](docs/BookingContractBooker.md)
 - [BookingContractItemBooker](docs/BookingContractItemBooker.md)
 - [BookingContractPaymentDetailsBooker](docs/BookingContractPaymentDetailsBooker.md)
 - [BookingItineraryBooker](docs/BookingItineraryBooker.md)
 - [BookingItineraryRoomConfigurationBooker](docs/BookingItineraryRoomConfigurationBooker.md)
 - [BookingItineraryRoomConfigurationChildBooker](docs/BookingItineraryRoomConfigurationChildBooker.md)
 - [BookingUserBooker](docs/BookingUserBooker.md)
 - [BookingUserRequestAuthenticatedEntity](docs/BookingUserRequestAuthenticatedEntity.md)
 - [BookingUserSessionBooker](docs/BookingUserSessionBooker.md)
 - [BooleanResponseAuthenticatedEntity](docs/BooleanResponseAuthenticatedEntity.md)
 - [BooleanResponseBooker](docs/BooleanResponseBooker.md)
 - [CancellationDetailBooker](docs/CancellationDetailBooker.md)
 - [CancellationPolicyExceptionAuthenticatedEntity](docs/CancellationPolicyExceptionAuthenticatedEntity.md)
 - [CancellationPolicyExceptionBooker](docs/CancellationPolicyExceptionBooker.md)
 - [CancellationPolicyExceptionsAuthenticatedEntity](docs/CancellationPolicyExceptionsAuthenticatedEntity.md)
 - [CancellationPolicyExceptionsBooker](docs/CancellationPolicyExceptionsBooker.md)
 - [CancellationPolicyLightweightAuthenticatedEntity](docs/CancellationPolicyLightweightAuthenticatedEntity.md)
 - [CancellationPolicyLightweightBooker](docs/CancellationPolicyLightweightBooker.md)
 - [CheckoutRequestAuthenticatedEntity](docs/CheckoutRequestAuthenticatedEntity.md)
 - [CheckoutResponseAuthenticatedEntity](docs/CheckoutResponseAuthenticatedEntity.md)
 - [ChildAuthenticatedEntity](docs/ChildAuthenticatedEntity.md)
 - [ChildBooker](docs/ChildBooker.md)
 - [CommissionableEntryBooker](docs/CommissionableEntryBooker.md)
 - [CompositeFilterDescriptorBooker](docs/CompositeFilterDescriptorBooker.md)
 - [ContactAuthenticatedEntity](docs/ContactAuthenticatedEntity.md)
 - [ContactBooker](docs/ContactBooker.md)
 - [CountryLightweightBooker](docs/CountryLightweightBooker.md)
 - [CreateCart400Response](docs/CreateCart400Response.md)
 - [CustomMonetaryAmount](docs/CustomMonetaryAmount.md)
 - [CustomizationLightweightBooker](docs/CustomizationLightweightBooker.md)
 - [CustomizationThemeColorsBooker](docs/CustomizationThemeColorsBooker.md)
 - [ExtraChargeAuthenticatedEntity](docs/ExtraChargeAuthenticatedEntity.md)
 - [ExtraChargeBooker](docs/ExtraChargeBooker.md)
 - [ExtraChargesAuthenticatedEntity](docs/ExtraChargesAuthenticatedEntity.md)
 - [ExtraChargesBooker](docs/ExtraChargesBooker.md)
 - [FilterDescriptorBooker](docs/FilterDescriptorBooker.md)
 - [GeneralManagerAuthenticatedEntity](docs/GeneralManagerAuthenticatedEntity.md)
 - [GeneralManagerBooker](docs/GeneralManagerBooker.md)
 - [GenericErrorMessage](docs/GenericErrorMessage.md)
 - [GeoJsonPointAuthenticatedEntity](docs/GeoJsonPointAuthenticatedEntity.md)
 - [GeoJsonPointBooker](docs/GeoJsonPointBooker.md)
 - [GeoNameLightweightBooker](docs/GeoNameLightweightBooker.md)
 - [GroupDescriptorBooker](docs/GroupDescriptorBooker.md)
 - [GuestRoomLightweightAuthenticatedEntity](docs/GuestRoomLightweightAuthenticatedEntity.md)
 - [GuestRoomLightweightBooker](docs/GuestRoomLightweightBooker.md)
 - [GuestUserBooker](docs/GuestUserBooker.md)
 - [LocalizedDescriptionAuthenticatedEntity](docs/LocalizedDescriptionAuthenticatedEntity.md)
 - [LocalizedDescriptionBooker](docs/LocalizedDescriptionBooker.md)
 - [LocalizedPriceAuthenticatedEntity](docs/LocalizedPriceAuthenticatedEntity.md)
 - [LocalizedPriceBooker](docs/LocalizedPriceBooker.md)
 - [MediaAuthorAttributionAuthenticatedEntity](docs/MediaAuthorAttributionAuthenticatedEntity.md)
 - [MediaAuthorAttributionBooker](docs/MediaAuthorAttributionBooker.md)
 - [PageBookingBooker](docs/PageBookingBooker.md)
 - [PageableObjectBooker](docs/PageableObjectBooker.md)
 - [PayableContractResponseAuthenticatedEntity](docs/PayableContractResponseAuthenticatedEntity.md)
 - [PayoutBooker](docs/PayoutBooker.md)
 - [PayoutFeeBooker](docs/PayoutFeeBooker.md)
 - [PerkLightweightAuthenticatedEntity](docs/PerkLightweightAuthenticatedEntity.md)
 - [PerkLightweightBooker](docs/PerkLightweightBooker.md)
 - [PersonalBooker](docs/PersonalBooker.md)
 - [PreferencesBooker](docs/PreferencesBooker.md)
 - [ProfileLightweightBooker](docs/ProfileLightweightBooker.md)
 - [ProfileUserBooker](docs/ProfileUserBooker.md)
 - [PropertyAggregateLightweightAuthenticatedEntity](docs/PropertyAggregateLightweightAuthenticatedEntity.md)
 - [PropertyAggregateLightweightBooker](docs/PropertyAggregateLightweightBooker.md)
 - [PropertyPolicyAuthenticatedEntity](docs/PropertyPolicyAuthenticatedEntity.md)
 - [PropertyPolicyBooker](docs/PropertyPolicyBooker.md)
 - [QuoteLightweightAuthenticatedEntity](docs/QuoteLightweightAuthenticatedEntity.md)
 - [QuoteLightweightBooker](docs/QuoteLightweightBooker.md)
 - [RatePlanLevelFeeAuthenticatedEntity](docs/RatePlanLevelFeeAuthenticatedEntity.md)
 - [RatePlanLevelFeeBooker](docs/RatePlanLevelFeeBooker.md)
 - [RealtimeShoppingCartAuthenticatedEntity](docs/RealtimeShoppingCartAuthenticatedEntity.md)
 - [RealtimeShoppingCartItemAuthenticatedEntity](docs/RealtimeShoppingCartItemAuthenticatedEntity.md)
 - [RefundBooker](docs/RefundBooker.md)
 - [RemoveEntryResponseAuthenticatedEntity](docs/RemoveEntryResponseAuthenticatedEntity.md)
 - [ReviewAnswerAuthenticatedEntity](docs/ReviewAnswerAuthenticatedEntity.md)
 - [ReviewAnswerBooker](docs/ReviewAnswerBooker.md)
 - [ReviewAuthenticatedEntity](docs/ReviewAuthenticatedEntity.md)
 - [ReviewLightweightBooker](docs/ReviewLightweightBooker.md)
 - [ReviewTemplateAuthenticatedEntity](docs/ReviewTemplateAuthenticatedEntity.md)
 - [ReviewUserAuthenticatedEntity](docs/ReviewUserAuthenticatedEntity.md)
 - [ReviewUserBooker](docs/ReviewUserBooker.md)
 - [RoomConfigurationAuthenticatedEntity](docs/RoomConfigurationAuthenticatedEntity.md)
 - [RoomConfigurationBooker](docs/RoomConfigurationBooker.md)
 - [RoomConfigurationPriceRatePlanAuthenticatedEntity](docs/RoomConfigurationPriceRatePlanAuthenticatedEntity.md)
 - [RoomConfigurationPriceRatePlanBooker](docs/RoomConfigurationPriceRatePlanBooker.md)
 - [RoomStayAuthenticatedEntity](docs/RoomStayAuthenticatedEntity.md)
 - [RoomStayBooker](docs/RoomStayBooker.md)
 - [SimpleAddressAuthenticatedEntity](docs/SimpleAddressAuthenticatedEntity.md)
 - [SimpleAddressBooker](docs/SimpleAddressBooker.md)
 - [SimpleDateTimeItineraryBooker](docs/SimpleDateTimeItineraryBooker.md)
 - [SimpleDescriptionAuthenticatedEntity](docs/SimpleDescriptionAuthenticatedEntity.md)
 - [SimpleDescriptionBooker](docs/SimpleDescriptionBooker.md)
 - [SimpleMultimediaAuthenticatedEntity](docs/SimpleMultimediaAuthenticatedEntity.md)
 - [SimpleMultimediaBooker](docs/SimpleMultimediaBooker.md)
 - [SocialAuthenticatedEntity](docs/SocialAuthenticatedEntity.md)
 - [SocialBooker](docs/SocialBooker.md)
 - [SortDescriptorBooker](docs/SortDescriptorBooker.md)
 - [SortObjectBooker](docs/SortObjectBooker.md)
 - [StateBooker](docs/StateBooker.md)
 - [StayRateAuthenticatedEntity](docs/StayRateAuthenticatedEntity.md)
 - [StayRateBooker](docs/StayRateBooker.md)
 - [SubCountryLightweightBooker](docs/SubCountryLightweightBooker.md)
 - [SubSubCountryLightweightBooker](docs/SubSubCountryLightweightBooker.md)
 - [SubmitReviewAnswerAuthenticatedEntity](docs/SubmitReviewAnswerAuthenticatedEntity.md)
 - [SubmitReviewRequestAuthenticatedEntity](docs/SubmitReviewRequestAuthenticatedEntity.md)
 - [SupplierContractItemPolicyBooker](docs/SupplierContractItemPolicyBooker.md)
 - [TravelInventoryRecognitionAuthenticatedEntity](docs/TravelInventoryRecognitionAuthenticatedEntity.md)
 - [TravelInventoryRecognitionBooker](docs/TravelInventoryRecognitionBooker.md)
 - [UpsertShoppingCartItemRequestAuthenticatedEntity](docs/UpsertShoppingCartItemRequestAuthenticatedEntity.md)


<a id="documentation-for-authorization"></a>
## Documentation For Authorization


Authentication schemes defined for the API:
<a id="oauth2ClientCredentials"></a>
### oauth2ClientCredentials

- **Type**: OAuth
- **Flow**: application
- **Authorization URL**: https://iam.wink.travel/oauth2/authorize
- **Scopes**: 
 - **inventory.read**: Read Wink data
 - **inventory.write**: Create Wink data
 - **inventory.remove**: Remove Wink data


## Author

bjorn@wink.travel


