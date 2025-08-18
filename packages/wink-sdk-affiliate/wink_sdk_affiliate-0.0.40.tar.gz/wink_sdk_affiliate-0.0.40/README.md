# wink-sdk-affiliate
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



# Affiliate API
The Affiliate API exposes endpoints to manage affiliate accounts. This API lets you:

1. Create affiliates.
2. Create account managers

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
pip install wink_sdk_affiliate
```

Or you can install it directly from the repository using:
```sh
pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_affiliate&subdirectory=wink-sdk-affiliate
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_affiliate&subdirectory=wink_sdk_affiliate`)

Then import the package:
```python
import wink_sdk_affiliate
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import wink_sdk_affiliate
```

### Tests

Execute `pytest` to run the tests.

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import wink_sdk_affiliate
from wink_sdk_affiliate.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.wink.travel
# See configuration.py for a list of all supported configuration parameters.
configuration = wink_sdk_affiliate.Configuration(
    host = "https://api.wink.travel"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]


# Enter a context with an instance of the API client
with wink_sdk_affiliate.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = wink_sdk_affiliate.AccountManagerApi(api_client)
    company_identifier = 'hotel-1' # str | AffiliateAccount identifier for which to accept invite to
    wink_version = 'wink_version_example' # str |  (optional)
    accept = 'accept_example' # str |  (optional)

    try:
        # Accept Invite
        api_response = api_instance.accept_manager_invite(company_identifier, wink_version=wink_version, accept=accept)
        print("The response of AccountManagerApi->accept_manager_invite:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AccountManagerApi->accept_manager_invite: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *https://api.wink.travel*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*AccountManagerApi* | [**accept_manager_invite**](docs/AccountManagerApi.md#accept_manager_invite) | **GET** /api/manager/invite/{companyIdentifier}/accept | Accept Invite
*AccountManagerApi* | [**invite_manager**](docs/AccountManagerApi.md#invite_manager) | **PATCH** /api/manager/invite | Invite Manager
*AccountManagerApi* | [**reject_invite**](docs/AccountManagerApi.md#reject_invite) | **DELETE** /api/manager/invite/{companyIdentifier}/reject | Reject Invite
*AccountManagerApi* | [**remove_company_user**](docs/AccountManagerApi.md#remove_company_user) | **DELETE** /api/manager/{email} | Remove Manager
*AccountManagerApi* | [**remove_manager_agency**](docs/AccountManagerApi.md#remove_manager_agency) | **DELETE** /api/manager/agency | Remove Managing Agency
*AccountManagerApi* | [**show_manager_invite_list**](docs/AccountManagerApi.md#show_manager_invite_list) | **GET** /api/manager/invite/list | Show Invites
*AccountManagerApi* | [**update_manager_agency**](docs/AccountManagerApi.md#update_manager_agency) | **PATCH** /api/manager/agency | Set Managing Agency
*AffiliateApi* | [**create_company**](docs/AffiliateApi.md#create_company) | **POST** /api/affiliate | Create Affiliate
*AffiliateApi* | [**is_affiliate_account_name_unique**](docs/AffiliateApi.md#is_affiliate_account_name_unique) | **POST** /api/affiliate-name-check | Verify Affiliate Name
*AffiliateApi* | [**is_company_url_name_unique**](docs/AffiliateApi.md#is_company_url_name_unique) | **POST** /api/affiliate-url-name-check | Verify Affiliate Url Name
*AffiliateApi* | [**remove_company**](docs/AffiliateApi.md#remove_company) | **DELETE** /api/affiliate/{companyIdentifier} | Delete Affiliate
*AffiliateApi* | [**remove_my_account**](docs/AffiliateApi.md#remove_my_account) | **DELETE** /api/my-account | Delete Affiliate
*AffiliateApi* | [**search_affiliates**](docs/AffiliateApi.md#search_affiliates) | **POST** /api/affiliate/grid | Affiliate Search
*AffiliateApi* | [**show_booking_analytics**](docs/AffiliateApi.md#show_booking_analytics) | **POST** /api/affiliate/{companyIdentifier}/booking/analytics | Affiliate Booking Analytics
*AffiliateApi* | [**show_booking_overview**](docs/AffiliateApi.md#show_booking_overview) | **GET** /api/affiliate/{companyIdentifier}/booking/overview | Affiliate Booking Overview
*AffiliateApi* | [**show_companies**](docs/AffiliateApi.md#show_companies) | **GET** /api/affiliate/list | Show Affiliates
*AffiliateApi* | [**show_company**](docs/AffiliateApi.md#show_company) | **GET** /api/affiliate/{companyIdentifier} | Show Affiliate
*AffiliateApi* | [**show_my_account**](docs/AffiliateApi.md#show_my_account) | **GET** /api/my-account | Show My Account
*AffiliateApi* | [**show_sales_channels**](docs/AffiliateApi.md#show_sales_channels) | **GET** /api/sales-channel/search | Sales Channel Search
*AffiliateApi* | [**update_company**](docs/AffiliateApi.md#update_company) | **PATCH** /api/affiliate/{companyIdentifier} | Update Affiliate
*AffiliateApi* | [**update_company1**](docs/AffiliateApi.md#update_company1) | **PATCH** /api/affiliate/{companyIdentifier}/status | Toggle Affiliate Status
*AffiliateApi* | [**update_company_address**](docs/AffiliateApi.md#update_company_address) | **PATCH** /api/affiliate/{companyIdentifier}/address | Update Affiliate Address
*AffiliateApi* | [**update_company_logo**](docs/AffiliateApi.md#update_company_logo) | **PATCH** /api/affiliate/{companyIdentifier}/logo | Update Affiliate Logo
*AffiliateApi* | [**update_company_online_presence**](docs/AffiliateApi.md#update_company_online_presence) | **PATCH** /api/affiliate/{companyIdentifier}/online-presence | Update Affiliate Online Presence
*AffiliateApi* | [**update_my_account**](docs/AffiliateApi.md#update_my_account) | **PATCH** /api/my-account/status | Toggle My Account Status
*AffiliateApi* | [**update_my_account_address**](docs/AffiliateApi.md#update_my_account_address) | **PATCH** /api/my-account/address | Update My Account Address
*AffiliateApi* | [**update_my_account_logo**](docs/AffiliateApi.md#update_my_account_logo) | **PATCH** /api/my-account/logo | Update My Account Logo
*AffiliateApi* | [**update_my_account_online_presence**](docs/AffiliateApi.md#update_my_account_online_presence) | **PATCH** /api/my-account/online-presence | Update My Account Online Presence
*AffiliateApi* | [**update_profile**](docs/AffiliateApi.md#update_profile) | **PATCH** /api/affiliate/{companyIdentifier}/profile | Update Profile


## Documentation For Models

 - [AddressAffiliate](docs/AddressAffiliate.md)
 - [AddressSupplier](docs/AddressSupplier.md)
 - [AffiliateAccountAffiliate](docs/AffiliateAccountAffiliate.md)
 - [AffiliateAccountSupplier](docs/AffiliateAccountSupplier.md)
 - [AffiliateAccountUserAffiliate](docs/AffiliateAccountUserAffiliate.md)
 - [AffiliateAccountUserSupplier](docs/AffiliateAccountUserSupplier.md)
 - [AggregateDescriptorSupplier](docs/AggregateDescriptorSupplier.md)
 - [BookingAnalyticsSupplier](docs/BookingAnalyticsSupplier.md)
 - [BookingOverviewRequestSupplier](docs/BookingOverviewRequestSupplier.md)
 - [ChartCategoryAxisSupplier](docs/ChartCategoryAxisSupplier.md)
 - [ChartLegendSupplier](docs/ChartLegendSupplier.md)
 - [ChartSeriesSupplier](docs/ChartSeriesSupplier.md)
 - [ChartTitleSupplier](docs/ChartTitleSupplier.md)
 - [CompositeFilterDescriptorSupplier](docs/CompositeFilterDescriptorSupplier.md)
 - [CountryLightweightAffiliate](docs/CountryLightweightAffiliate.md)
 - [CountryLightweightSupplier](docs/CountryLightweightSupplier.md)
 - [CreateAffiliateAccountRequestAffiliate](docs/CreateAffiliateAccountRequestAffiliate.md)
 - [CreateCompany400Response](docs/CreateCompany400Response.md)
 - [CustomMonetaryAmount](docs/CustomMonetaryAmount.md)
 - [FilterDescriptorSupplier](docs/FilterDescriptorSupplier.md)
 - [GenericErrorMessage](docs/GenericErrorMessage.md)
 - [GeoJsonPointAffiliate](docs/GeoJsonPointAffiliate.md)
 - [GeoJsonPointSupplier](docs/GeoJsonPointSupplier.md)
 - [GeoNameLightweightAffiliate](docs/GeoNameLightweightAffiliate.md)
 - [GeoNameLightweightSupplier](docs/GeoNameLightweightSupplier.md)
 - [GroupDescriptorSupplier](docs/GroupDescriptorSupplier.md)
 - [GroupedBookingSalesMetricsSupplierDetails](docs/GroupedBookingSalesMetricsSupplierDetails.md)
 - [InviteManagerRequestAffiliate](docs/InviteManagerRequestAffiliate.md)
 - [KeyValuePairAffiliate](docs/KeyValuePairAffiliate.md)
 - [LineChartSupplier](docs/LineChartSupplier.md)
 - [ManagedByEntityAffiliate](docs/ManagedByEntityAffiliate.md)
 - [ManagedByEntityRulesAffiliate](docs/ManagedByEntityRulesAffiliate.md)
 - [ManagedByEntityRulesSupplier](docs/ManagedByEntityRulesSupplier.md)
 - [ManagedByEntitySupplier](docs/ManagedByEntitySupplier.md)
 - [ManagerInviteAcceptedSupplier](docs/ManagerInviteAcceptedSupplier.md)
 - [ManagerInviteAffiliate](docs/ManagerInviteAffiliate.md)
 - [MediaAuthorAttributionAffiliate](docs/MediaAuthorAttributionAffiliate.md)
 - [MediaAuthorAttributionSupplier](docs/MediaAuthorAttributionSupplier.md)
 - [PageAffiliateAccountSupplier](docs/PageAffiliateAccountSupplier.md)
 - [PageableObjectSupplier](docs/PageableObjectSupplier.md)
 - [SimpleDescriptionAffiliate](docs/SimpleDescriptionAffiliate.md)
 - [SimpleDescriptionSupplier](docs/SimpleDescriptionSupplier.md)
 - [SimpleMultimediaAffiliate](docs/SimpleMultimediaAffiliate.md)
 - [SimpleMultimediaSupplier](docs/SimpleMultimediaSupplier.md)
 - [SortDescriptorSupplier](docs/SortDescriptorSupplier.md)
 - [SortObjectSupplier](docs/SortObjectSupplier.md)
 - [StateSupplier](docs/StateSupplier.md)
 - [SubCountryLightweightAffiliate](docs/SubCountryLightweightAffiliate.md)
 - [SubCountryLightweightSupplier](docs/SubCountryLightweightSupplier.md)
 - [SubSubCountryLightweightAffiliate](docs/SubSubCountryLightweightAffiliate.md)
 - [SubSubCountryLightweightSupplier](docs/SubSubCountryLightweightSupplier.md)
 - [TravelAgentSupplier](docs/TravelAgentSupplier.md)
 - [UniqueRequestAffiliate](docs/UniqueRequestAffiliate.md)
 - [UniqueResultAffiliate](docs/UniqueResultAffiliate.md)
 - [UpsertAddressRequestAffiliate](docs/UpsertAddressRequestAffiliate.md)
 - [UpsertAffiliateAccountProfileRequestAffiliate](docs/UpsertAffiliateAccountProfileRequestAffiliate.md)
 - [UpsertCompanyLogoRequestAffiliate](docs/UpsertCompanyLogoRequestAffiliate.md)
 - [UpsertCompanyOnlinePresenceRequestAffiliate](docs/UpsertCompanyOnlinePresenceRequestAffiliate.md)
 - [UpsertCompanyRequestAffiliate](docs/UpsertCompanyRequestAffiliate.md)
 - [UpsertCompanyStatusRequestAffiliate](docs/UpsertCompanyStatusRequestAffiliate.md)
 - [UpsertManagedByAgencyRequestAffiliate](docs/UpsertManagedByAgencyRequestAffiliate.md)


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


