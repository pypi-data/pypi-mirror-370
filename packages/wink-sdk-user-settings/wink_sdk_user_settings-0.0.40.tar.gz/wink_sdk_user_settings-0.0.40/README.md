# wink-sdk-user-settings
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



# User Settings API
The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink. This API lets you:

1. Bucket List: Manage your bucket list on Wink.
2. Webhook: Subscribe to receive Wink events as they occur in realtime.
3. User: Manage user settings.

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
pip install wink_sdk_user_settings
```

Or you can install it directly from the repository using:
```sh
pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_user_settings&subdirectory=wink-sdk-user-settings
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_user_settings&subdirectory=wink_sdk_user_settings`)

Then import the package:
```python
import wink_sdk_user_settings
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import wink_sdk_user_settings
```

### Tests

Execute `pytest` to run the tests.

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import wink_sdk_user_settings
from wink_sdk_user_settings.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.wink.travel
# See configuration.py for a list of all supported configuration parameters.
configuration = wink_sdk_user_settings.Configuration(
    host = "https://api.wink.travel"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]


# Enter a context with an instance of the API client
with wink_sdk_user_settings.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = wink_sdk_user_settings.ApplicationApi(api_client)
    upsert_application_request = wink_sdk_user_settings.UpsertApplicationRequest() # UpsertApplicationRequest | 
    wink_version = 'wink_version_example' # str |  (optional)

    try:
        # Create Application
        api_response = api_instance.create_application(upsert_application_request, wink_version=wink_version)
        print("The response of ApplicationApi->create_application:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ApplicationApi->create_application: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *https://api.wink.travel*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*ApplicationApi* | [**create_application**](docs/ApplicationApi.md#create_application) | **POST** /api/application | Create Application
*ApplicationApi* | [**delete_application**](docs/ApplicationApi.md#delete_application) | **DELETE** /api/application/{id} | Delete Application
*ApplicationApi* | [**load_application**](docs/ApplicationApi.md#load_application) | **GET** /api/application/{id} | Show Application
*ApplicationApi* | [**revoke_application**](docs/ApplicationApi.md#revoke_application) | **GET** /api/application/{id}/revoke | Revoke Application Credentials
*ApplicationApi* | [**show_applications**](docs/ApplicationApi.md#show_applications) | **GET** /api/application/list | Show Applications
*ApplicationApi* | [**update_application**](docs/ApplicationApi.md#update_application) | **PATCH** /api/application/{id} | Update Application
*BucketListApi* | [**add_bucket_list_entry**](docs/BucketListApi.md#add_bucket_list_entry) | **POST** /api/bucket-list | Create Bucket List
*BucketListApi* | [**remove_bucket_list**](docs/BucketListApi.md#remove_bucket_list) | **DELETE** /api/bucket-list/{bucketListItemIdentifier} | Delete Bucket List Entry
*BucketListApi* | [**show_bucket_list**](docs/BucketListApi.md#show_bucket_list) | **GET** /api/bucket-list | Get Bucket Lists
*BucketListApi* | [**show_bucket_list_entries**](docs/BucketListApi.md#show_bucket_list_entries) | **GET** /api/bucket-list/entries | Get Bucket List
*BucketListApi* | [**show_bucket_list_entry**](docs/BucketListApi.md#show_bucket_list_entry) | **GET** /api/bucket-list/{type}/{identifier} | Get Bucket List Entries
*UserSettingsApi* | [**change_password**](docs/UserSettingsApi.md#change_password) | **PATCH** /api/user-settings/change-password | Change password
*UserSettingsApi* | [**show_profile**](docs/UserSettingsApi.md#show_profile) | **GET** /api/profile | Show Profile
*UserSettingsApi* | [**show_user_profile**](docs/UserSettingsApi.md#show_user_profile) | **GET** /api/user-settings/profile | Show User Profile
*UserSettingsApi* | [**update_profile**](docs/UserSettingsApi.md#update_profile) | **PUT** /api/profile | Update Profile
*UserSettingsApi* | [**update_user_profile**](docs/UserSettingsApi.md#update_user_profile) | **PATCH** /api/user-settings/profile | Update User Profile
*WebhookApi* | [**create_webhook**](docs/WebhookApi.md#create_webhook) | **POST** /api/webhook | Create Webhook
*WebhookApi* | [**delete_webhook**](docs/WebhookApi.md#delete_webhook) | **DELETE** /api/webhook/{id} | Delete Webhook
*WebhookApi* | [**load_webhook**](docs/WebhookApi.md#load_webhook) | **GET** /api/webhook/{id} | Show Webhook
*WebhookApi* | [**show_webhook_events**](docs/WebhookApi.md#show_webhook_events) | **GET** /api/webhook/event/list | Show Webhook Event List
*WebhookApi* | [**show_webhooks**](docs/WebhookApi.md#show_webhooks) | **GET** /api/webhook/list | Show Webhooks
*WebhookApi* | [**update_webhook**](docs/WebhookApi.md#update_webhook) | **PATCH** /api/webhook/{id} | Update Webhook


## Documentation For Models

 - [Application](docs/Application.md)
 - [BooleanResponse](docs/BooleanResponse.md)
 - [BucketListEntryAuthenticatedEntity](docs/BucketListEntryAuthenticatedEntity.md)
 - [BucketListEntryRequestAuthenticatedEntity](docs/BucketListEntryRequestAuthenticatedEntity.md)
 - [BucketListEntryViewAuthenticatedEntity](docs/BucketListEntryViewAuthenticatedEntity.md)
 - [BucketListEntryWrapperAuthenticatedEntity](docs/BucketListEntryWrapperAuthenticatedEntity.md)
 - [ChangePasswordRequest](docs/ChangePasswordRequest.md)
 - [CreateApplicationResponse](docs/CreateApplicationResponse.md)
 - [CustomMonetaryAmount](docs/CustomMonetaryAmount.md)
 - [GenericErrorMessage](docs/GenericErrorMessage.md)
 - [GeoJsonPointAuthenticatedEntity](docs/GeoJsonPointAuthenticatedEntity.md)
 - [InventoryAddressAuthenticatedEntity](docs/InventoryAddressAuthenticatedEntity.md)
 - [InventoryAuthenticatedEntity](docs/InventoryAuthenticatedEntity.md)
 - [KeyValuePair](docs/KeyValuePair.md)
 - [LocalizedDescriptionAuthenticatedEntity](docs/LocalizedDescriptionAuthenticatedEntity.md)
 - [ManagingEntity](docs/ManagingEntity.md)
 - [MediaAuthorAttribution](docs/MediaAuthorAttribution.md)
 - [MediaAuthorAttributionAuthenticatedEntity](docs/MediaAuthorAttributionAuthenticatedEntity.md)
 - [PersonalNonAuthenticatedEntity](docs/PersonalNonAuthenticatedEntity.md)
 - [PreferencesNonAuthenticatedEntity](docs/PreferencesNonAuthenticatedEntity.md)
 - [ProfileNonAuthenticatedEntity](docs/ProfileNonAuthenticatedEntity.md)
 - [ProfileUserNonAuthenticatedEntity](docs/ProfileUserNonAuthenticatedEntity.md)
 - [RemoveEntryResponse](docs/RemoveEntryResponse.md)
 - [RevokeClientIdResponse](docs/RevokeClientIdResponse.md)
 - [SalesChannelLightweightAuthenticatedEntity](docs/SalesChannelLightweightAuthenticatedEntity.md)
 - [ShowProfile400Response](docs/ShowProfile400Response.md)
 - [SimpleDescription](docs/SimpleDescription.md)
 - [SimpleDescriptionAuthenticatedEntity](docs/SimpleDescriptionAuthenticatedEntity.md)
 - [SimpleMultimedia](docs/SimpleMultimedia.md)
 - [SimpleMultimediaAuthenticatedEntity](docs/SimpleMultimediaAuthenticatedEntity.md)
 - [SpecialRateBundleLightweightAuthenticatedEntity](docs/SpecialRateBundleLightweightAuthenticatedEntity.md)
 - [SpecialRateLightweightAuthenticatedEntity](docs/SpecialRateLightweightAuthenticatedEntity.md)
 - [UpdateApplicationResponse](docs/UpdateApplicationResponse.md)
 - [UpsertApplicationRequest](docs/UpsertApplicationRequest.md)
 - [UpsertProfileRequestNonAuthenticatedEntity](docs/UpsertProfileRequestNonAuthenticatedEntity.md)
 - [UpsertUserProfileRequest](docs/UpsertUserProfileRequest.md)
 - [UpsertUserProfileResponse](docs/UpsertUserProfileResponse.md)
 - [UpsertWebhookRequest](docs/UpsertWebhookRequest.md)
 - [Webhook](docs/Webhook.md)


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


