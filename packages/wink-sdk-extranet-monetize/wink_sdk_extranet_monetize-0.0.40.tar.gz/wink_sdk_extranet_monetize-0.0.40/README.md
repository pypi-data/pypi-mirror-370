# wink-sdk-extranet-monetize
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



# Extranet Monetize API
This part of the documentation concerns itself with the management of cancellation policies, promotions, restrictions etc. This API lets you create:

1. Add-ons: Manage add-ons.
2. Cancellation policies: Manage cancellation policies for your property.
3. Rate plan: Manage property rate plans.
4. Master rates: Manage perks for room type / rate plan combos.
5. Promotions: Manage promotions.
6. Promotion bundle: Manage bundled promotions.

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
pip install wink_sdk_extranet_monetize
```

Or you can install it directly from the repository using:
```sh
pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_extranet_monetize&subdirectory=wink-sdk-extranet-monetize
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_extranet_monetize&subdirectory=wink_sdk_extranet_monetize`)

Then import the package:
```python
import wink_sdk_extranet_monetize
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import wink_sdk_extranet_monetize
```

### Tests

Execute `pytest` to run the tests.

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import wink_sdk_extranet_monetize
from wink_sdk_extranet_monetize.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.wink.travel
# See configuration.py for a list of all supported configuration parameters.
configuration = wink_sdk_extranet_monetize.Configuration(
    host = "https://api.wink.travel"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]


# Enter a context with an instance of the API client
with wink_sdk_extranet_monetize.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = wink_sdk_extranet_monetize.AddOnApi(api_client)
    property_identifier = 'hotel-1' # str | Add multimedia record to add-on record owned by this property identifier
    add_on_identifier = 'add-on-1' # str | Add multimedia record to add-on with this identifier
    simple_multimedia = wink_sdk_extranet_monetize.SimpleMultimedia() # SimpleMultimedia | 
    wink_version = 'wink_version_example' # str |  (optional)

    try:
        # Add Multimedia
        api_response = api_instance.add_multimedia(property_identifier, add_on_identifier, simple_multimedia, wink_version=wink_version)
        print("The response of AddOnApi->add_multimedia:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AddOnApi->add_multimedia: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *https://api.wink.travel*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*AddOnApi* | [**add_multimedia**](docs/AddOnApi.md#add_multimedia) | **PATCH** /api/property/{propertyIdentifier}/add-on/{addOnIdentifier}/multimedia | Add Multimedia
*AddOnApi* | [**create_add_on**](docs/AddOnApi.md#create_add_on) | **POST** /api/property/{propertyIdentifier}/add-on | Create Add-On
*AddOnApi* | [**remove_add_on**](docs/AddOnApi.md#remove_add_on) | **DELETE** /api/property/{propertyIdentifier}/add-on/{addOnIdentifier} | Delete Add-On
*AddOnApi* | [**remove_multimedia**](docs/AddOnApi.md#remove_multimedia) | **DELETE** /api/property/{propertyIdentifier}/add-on/{addOnIdentifier}/multimedia/{multimediaIdentifier} | Delete Multimedia
*AddOnApi* | [**show_add_on**](docs/AddOnApi.md#show_add_on) | **GET** /api/property/{propertyIdentifier}/add-on/{addOnIdentifier} | Show Add-On
*AddOnApi* | [**show_add_ons**](docs/AddOnApi.md#show_add_ons) | **GET** /api/property/{propertyIdentifier}/add-on/list | Show Add-Ons
*AddOnApi* | [**update_add_on**](docs/AddOnApi.md#update_add_on) | **PUT** /api/property/{propertyIdentifier}/add-on/{addOnIdentifier} | Update Add-On
*AddOnApi* | [**update_add_on_multimedia**](docs/AddOnApi.md#update_add_on_multimedia) | **PATCH** /api/property/{propertyIdentifier}/add-on/{addOnIdentifier}/multimedia/{multimediaIdentifier} | Update Multimedia
*AddOnApi* | [**upload_binary_add_on_media**](docs/AddOnApi.md#upload_binary_add_on_media) | **POST** /api/property/{propertyIdentifier}/add-on/{addOnIdentifier}/multimedia | Upload Binary Multimedia
*CancellationPolicyApi* | [**create_cancellation_policy**](docs/CancellationPolicyApi.md#create_cancellation_policy) | **POST** /api/property/{propertyIdentifier}/cancellation-policy | Create Cancellation Policy
*CancellationPolicyApi* | [**is_cancellation_policy_removable**](docs/CancellationPolicyApi.md#is_cancellation_policy_removable) | **GET** /api/property/{propertyIdentifier}/cancellation-policy/{cancellationPolicyIdentifier}/removable | Verify Removable
*CancellationPolicyApi* | [**remove_cancellation_policy**](docs/CancellationPolicyApi.md#remove_cancellation_policy) | **DELETE** /api/property/{propertyIdentifier}/cancellation-policy/{cancellationPolicyIdentifier} | Delete Cancellation Policy
*CancellationPolicyApi* | [**show_cancellation_policy**](docs/CancellationPolicyApi.md#show_cancellation_policy) | **GET** /api/property/{propertyIdentifier}/cancellation-policy/{cancellationPolicyIdentifier} | Show Cancellation Policy
*CancellationPolicyApi* | [**show_cancellation_policy_list**](docs/CancellationPolicyApi.md#show_cancellation_policy_list) | **GET** /api/property/{propertyIdentifier}/cancellation-policy/list | Show Cancellation Policies
*CancellationPolicyApi* | [**update_cancellation_policy**](docs/CancellationPolicyApi.md#update_cancellation_policy) | **PUT** /api/property/{propertyIdentifier}/cancellation-policy/{cancellationPolicyIdentifier} | Update Cancellation Policy
*MasterRateApi* | [**set_perks**](docs/MasterRateApi.md#set_perks) | **PATCH** /api/property/{propertyIdentifier}/master-rate/{masterRateIdentifier}/perks | Set Master Rate Perks
*MasterRateApi* | [**show_master_rate**](docs/MasterRateApi.md#show_master_rate) | **GET** /api/property/{propertyIdentifier}/master-rate/{masterRateIdentifier} | Show Master Rate
*MasterRateApi* | [**show_master_rates**](docs/MasterRateApi.md#show_master_rates) | **GET** /api/property/{propertyIdentifier}/master-rate/list | Show Master Rates
*MasterRateApi* | [**toggle_master_rate**](docs/MasterRateApi.md#toggle_master_rate) | **PATCH** /api/property/{propertyIdentifier}/master-rate/{masterRateIdentifier}/toggle | Toggle Master Rate
*PromotionApi* | [**create_promotion**](docs/PromotionApi.md#create_promotion) | **POST** /api/property/{propertyIdentifier}/promotion | Create Promotion
*PromotionApi* | [**remove_rate_modifier**](docs/PromotionApi.md#remove_rate_modifier) | **DELETE** /api/property/{propertyIdentifier}/promotion/{rateModifierIdentifier} | Delete Promotion
*PromotionApi* | [**show_promotion**](docs/PromotionApi.md#show_promotion) | **GET** /api/property/{propertyIdentifier}/promotion/{rateModifierIdentifier} | Show Promotion
*PromotionApi* | [**show_promotions**](docs/PromotionApi.md#show_promotions) | **GET** /api/property/{propertyIdentifier}/promotion/list | Show Promotions
*PromotionApi* | [**update_promotion**](docs/PromotionApi.md#update_promotion) | **PUT** /api/property/{propertyIdentifier}/promotion/{rateModifierIdentifier} | Update Promotion
*PromotionBundleApi* | [**create_rate_modifier_bundle**](docs/PromotionBundleApi.md#create_rate_modifier_bundle) | **POST** /api/property/{propertyIdentifier}/promotion-bundle | Create Promotion Bundle
*PromotionBundleApi* | [**remove_rate_modifier_bundle**](docs/PromotionBundleApi.md#remove_rate_modifier_bundle) | **DELETE** /api/property/{propertyIdentifier}/promotion-bundle/{rateModifierBundleIdentifier} | Delete Promotion Bundle
*PromotionBundleApi* | [**show_rate_modifier_bundle**](docs/PromotionBundleApi.md#show_rate_modifier_bundle) | **GET** /api/property/{propertyIdentifier}/promotion-bundle/{rateModifierBundleIdentifier} | Show Promotion Bundle
*PromotionBundleApi* | [**show_rate_modifier_bundles**](docs/PromotionBundleApi.md#show_rate_modifier_bundles) | **GET** /api/property/{propertyIdentifier}/promotion-bundle/list | Show Promotion Bundles
*PromotionBundleApi* | [**update_rate_modifier_bundle**](docs/PromotionBundleApi.md#update_rate_modifier_bundle) | **PUT** /api/property/{propertyIdentifier}/promotion-bundle/{rateModifierBundleIdentifier} | Update Promotion Bundle
*RatePlanApi* | [**create_rate_plan**](docs/RatePlanApi.md#create_rate_plan) | **POST** /api/property/{propertyIdentifier}/rate-plan | Create Rate Plan
*RatePlanApi* | [**remove_rate_plan**](docs/RatePlanApi.md#remove_rate_plan) | **DELETE** /api/property/{propertyIdentifier}/rate-plan/{ratePlanIdentifier} | Delete Rate Plan
*RatePlanApi* | [**show_rate_plan**](docs/RatePlanApi.md#show_rate_plan) | **GET** /api/property/{propertyIdentifier}/rate-plan/{ratePlanIdentifier} | Show Rate Plan
*RatePlanApi* | [**show_rate_plans**](docs/RatePlanApi.md#show_rate_plans) | **GET** /api/property/{propertyIdentifier}/rate-plan/list | Show Rate Plans
*RatePlanApi* | [**update_rate_plan**](docs/RatePlanApi.md#update_rate_plan) | **PUT** /api/property/{propertyIdentifier}/rate-plan/{ratePlanIdentifier} | Update Rate Plan


## Documentation For Models

 - [AddOn](docs/AddOn.md)
 - [Address](docs/Address.md)
 - [AddressSupplier](docs/AddressSupplier.md)
 - [AdvanceBookingRateQualifierSupplier](docs/AdvanceBookingRateQualifierSupplier.md)
 - [ArrivalDaysOfWeekRateQualifierSupplier](docs/ArrivalDaysOfWeekRateQualifierSupplier.md)
 - [AvailableDaysOfWeekRateQualifierSupplier](docs/AvailableDaysOfWeekRateQualifierSupplier.md)
 - [BedSupplier](docs/BedSupplier.md)
 - [BedroomConfigurationSupplier](docs/BedroomConfigurationSupplier.md)
 - [BedroomSupplier](docs/BedroomSupplier.md)
 - [BlackoutDateSupplier](docs/BlackoutDateSupplier.md)
 - [CancellationPolicyException](docs/CancellationPolicyException.md)
 - [CancellationPolicyExceptionSupplier](docs/CancellationPolicyExceptionSupplier.md)
 - [CancellationPolicyExceptions](docs/CancellationPolicyExceptions.md)
 - [CancellationPolicyExceptionsSupplier](docs/CancellationPolicyExceptionsSupplier.md)
 - [CancellationPolicyLightweight](docs/CancellationPolicyLightweight.md)
 - [CancellationPolicyLightweightSupplier](docs/CancellationPolicyLightweightSupplier.md)
 - [CancellationPolicyRemovableResponseSupplier](docs/CancellationPolicyRemovableResponseSupplier.md)
 - [CancellationPolicySupplier](docs/CancellationPolicySupplier.md)
 - [CityRateQualifierSupplier](docs/CityRateQualifierSupplier.md)
 - [Contact](docs/Contact.md)
 - [ContactSupplier](docs/ContactSupplier.md)
 - [ContinentRateQualifierSupplier](docs/ContinentRateQualifierSupplier.md)
 - [CountryLightweight](docs/CountryLightweight.md)
 - [CountryLightweightSupplier](docs/CountryLightweightSupplier.md)
 - [CountryRateQualifierSupplier](docs/CountryRateQualifierSupplier.md)
 - [CustomMonetaryAmount](docs/CustomMonetaryAmount.md)
 - [DepartureDaysOfWeekRateQualifierSupplier](docs/DepartureDaysOfWeekRateQualifierSupplier.md)
 - [DowPatternGroup](docs/DowPatternGroup.md)
 - [DowPatternGroupSupplier](docs/DowPatternGroupSupplier.md)
 - [GenericErrorMessage](docs/GenericErrorMessage.md)
 - [GeoIpLightweightSupplier](docs/GeoIpLightweightSupplier.md)
 - [GeoJsonPoint](docs/GeoJsonPoint.md)
 - [GeoJsonPointSupplier](docs/GeoJsonPointSupplier.md)
 - [GeoNameCountrySupplier](docs/GeoNameCountrySupplier.md)
 - [GeoNameLightweight](docs/GeoNameLightweight.md)
 - [GeoNameLightweightSupplier](docs/GeoNameLightweightSupplier.md)
 - [IPRangeRateQualifierSupplier](docs/IPRangeRateQualifierSupplier.md)
 - [IdentifierNamePairSupplier](docs/IdentifierNamePairSupplier.md)
 - [LengthOfStayRateQualifierSupplier](docs/LengthOfStayRateQualifierSupplier.md)
 - [LocalizedDescription](docs/LocalizedDescription.md)
 - [LocalizedDescriptionSupplier](docs/LocalizedDescriptionSupplier.md)
 - [MasterRateSupplier](docs/MasterRateSupplier.md)
 - [MediaAuthorAttribution](docs/MediaAuthorAttribution.md)
 - [MediaAuthorAttributionSupplier](docs/MediaAuthorAttributionSupplier.md)
 - [MinutesBeforeBookingStartDateRateQualifierSupplier](docs/MinutesBeforeBookingStartDateRateQualifierSupplier.md)
 - [PrepayRateQualifierSupplier](docs/PrepayRateQualifierSupplier.md)
 - [PromotionRateQualifierSupplier](docs/PromotionRateQualifierSupplier.md)
 - [RatePlanLevelFee](docs/RatePlanLevelFee.md)
 - [RatePlanLevelFeeSupplier](docs/RatePlanLevelFeeSupplier.md)
 - [RatePlanLightweight](docs/RatePlanLightweight.md)
 - [RatePlanLightweightSupplier](docs/RatePlanLightweightSupplier.md)
 - [RatePlanSupplier](docs/RatePlanSupplier.md)
 - [RefundableRateQualifierSupplier](docs/RefundableRateQualifierSupplier.md)
 - [RemoveEntryResponse](docs/RemoveEntryResponse.md)
 - [RequiredDaysOfWeekRateQualifierSupplier](docs/RequiredDaysOfWeekRateQualifierSupplier.md)
 - [RoomRangeRateQualifierSupplier](docs/RoomRangeRateQualifierSupplier.md)
 - [RoomTypeLightweightSupplier](docs/RoomTypeLightweightSupplier.md)
 - [SellDateRateQualifierSupplier](docs/SellDateRateQualifierSupplier.md)
 - [SetMasterRatePerkRequestSupplier](docs/SetMasterRatePerkRequestSupplier.md)
 - [ShowRatePlan400Response](docs/ShowRatePlan400Response.md)
 - [SimpleDescription](docs/SimpleDescription.md)
 - [SimpleDescriptionSupplier](docs/SimpleDescriptionSupplier.md)
 - [SimpleMultimedia](docs/SimpleMultimedia.md)
 - [SimpleMultimediaSupplier](docs/SimpleMultimediaSupplier.md)
 - [Social](docs/Social.md)
 - [SocialSupplier](docs/SocialSupplier.md)
 - [SpecialRateBundleSupplier](docs/SpecialRateBundleSupplier.md)
 - [SpecialRateSupplier](docs/SpecialRateSupplier.md)
 - [StayDateRateQualifierSupplier](docs/StayDateRateQualifierSupplier.md)
 - [SubCountryLightweight](docs/SubCountryLightweight.md)
 - [SubCountryLightweightSupplier](docs/SubCountryLightweightSupplier.md)
 - [SubSubCountryLightweight](docs/SubSubCountryLightweight.md)
 - [SubSubCountryLightweightSupplier](docs/SubSubCountryLightweightSupplier.md)
 - [TimezoneRateQualifierSupplier](docs/TimezoneRateQualifierSupplier.md)
 - [ToggleMasterRateRequestSupplier](docs/ToggleMasterRateRequestSupplier.md)
 - [TransactionalTravelInventory](docs/TransactionalTravelInventory.md)
 - [TransactionalTravelInventorySupplier](docs/TransactionalTravelInventorySupplier.md)
 - [TravelInventoryRecognition](docs/TravelInventoryRecognition.md)
 - [TravelInventoryRecognitionSupplier](docs/TravelInventoryRecognitionSupplier.md)
 - [UpsertAddOnRequest](docs/UpsertAddOnRequest.md)
 - [UpsertAddressRequest](docs/UpsertAddressRequest.md)
 - [UpsertCancellationPolicyExceptionSupplier](docs/UpsertCancellationPolicyExceptionSupplier.md)
 - [UpsertCancellationPolicyExceptionsSupplier](docs/UpsertCancellationPolicyExceptionsSupplier.md)
 - [UpsertCancellationPolicyRequestSupplier](docs/UpsertCancellationPolicyRequestSupplier.md)
 - [UpsertRateModifierRequestSupplier](docs/UpsertRateModifierRequestSupplier.md)
 - [UpsertRatePlanRequestSupplier](docs/UpsertRatePlanRequestSupplier.md)
 - [UpsertSimpleDescription](docs/UpsertSimpleDescription.md)
 - [UpsertSpecialRateBundleRequestSupplier](docs/UpsertSpecialRateBundleRequestSupplier.md)
 - [VariableCharge](docs/VariableCharge.md)
 - [VariableChargeSupplier](docs/VariableChargeSupplier.md)


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


