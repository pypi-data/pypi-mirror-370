# wink-sdk-extranet-property-register
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



# Extranet Property Registration API
This part of the documentation concerns itself about adding new properties to Wink. There are two endpoints for you to onboard a property:

1. Manage leads
2. Manually: Use this endpoint if you already have all the property data. Use case: You want to migrate your existing properties to Wink.
3. Intelligently: With the assistance of Google Business Pages, you can select an existing property on Google, ingest it with the lead endpoint and let us create a Wink property for you. Note: This isn't always straightforward in places with non-standard addresses.

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
pip install wink_sdk_extranet_property_register
```

Or you can install it directly from the repository using:
```sh
pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_extranet_property_register&subdirectory=wink-sdk-extranet-property-register
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/wink-travel/wink-sdk-python.git@v0.0.40#egg=wink_sdk_extranet_property_register&subdirectory=wink_sdk_extranet_property_register`)

Then import the package:
```python
import wink_sdk_extranet_property_register
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import wink_sdk_extranet_property_register
```

### Tests

Execute `pytest` to run the tests.

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import wink_sdk_extranet_property_register
from wink_sdk_extranet_property_register.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.wink.travel
# See configuration.py for a list of all supported configuration parameters.
configuration = wink_sdk_extranet_property_register.Configuration(
    host = "https://api.wink.travel"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]


# Enter a context with an instance of the API client
with wink_sdk_extranet_property_register.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = wink_sdk_extranet_property_register.ManageLeadsApi(api_client)
    google_place_detail_request_supplier = wink_sdk_extranet_property_register.GooglePlaceDetailRequestSupplier() # GooglePlaceDetailRequestSupplier | 
    wink_version = 'wink_version_example' # str |  (optional)

    try:
        # Create Lead
        api_response = api_instance.create_lead(google_place_detail_request_supplier, wink_version=wink_version)
        print("The response of ManageLeadsApi->create_lead:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ManageLeadsApi->create_lead: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *https://api.wink.travel*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*ManageLeadsApi* | [**create_lead**](docs/ManageLeadsApi.md#create_lead) | **POST** /api/lead | Create Lead
*ManageLeadsApi* | [**remove_lead**](docs/ManageLeadsApi.md#remove_lead) | **DELETE** /api/lead/{leadIdentifier} | Delete Lead
*ManageLeadsApi* | [**show_lead**](docs/ManageLeadsApi.md#show_lead) | **GET** /api/lead/{leadIdentifier} | Show Lead
*ManageLeadsApi* | [**show_lead_count**](docs/ManageLeadsApi.md#show_lead_count) | **GET** /api/lead/count | Count Leads
*ManageLeadsApi* | [**show_lead_list**](docs/ManageLeadsApi.md#show_lead_list) | **GET** /api/lead/list | Show Lead List
*PropertyRegistrationApi* | [**is_property_name_unique**](docs/PropertyRegistrationApi.md#is_property_name_unique) | **GET** /api/property/name | Property Name Check
*PropertyRegistrationApi* | [**register_property_intelligently**](docs/PropertyRegistrationApi.md#register_property_intelligently) | **POST** /api/property/register/intelligent/{leadIdentifier} | Register Property Intelligently
*PropertyRegistrationApi* | [**register_property_manually**](docs/PropertyRegistrationApi.md#register_property_manually) | **POST** /api/property/register/manual | Register Property Manually


## Documentation For Models

 - [AddressSupplier](docs/AddressSupplier.md)
 - [AggregateGreendexAnswersSupplier](docs/AggregateGreendexAnswersSupplier.md)
 - [AggregateGreendexScoreByCategorySupplier](docs/AggregateGreendexScoreByCategorySupplier.md)
 - [ContactSupplier](docs/ContactSupplier.md)
 - [CountResponseSupplier](docs/CountResponseSupplier.md)
 - [CountryLightweightSupplier](docs/CountryLightweightSupplier.md)
 - [CustomMonetaryAmount](docs/CustomMonetaryAmount.md)
 - [GeneralManagerSupplier](docs/GeneralManagerSupplier.md)
 - [GenericErrorMessage](docs/GenericErrorMessage.md)
 - [GeoJsonPointSupplier](docs/GeoJsonPointSupplier.md)
 - [GeoNameLightweightSupplier](docs/GeoNameLightweightSupplier.md)
 - [GooglePlaceDetailRequestSupplier](docs/GooglePlaceDetailRequestSupplier.md)
 - [IntelligentProfileSupplier](docs/IntelligentProfileSupplier.md)
 - [IntelligentPropertyRegistrationRequestSupplier](docs/IntelligentPropertyRegistrationRequestSupplier.md)
 - [IsPropertyNameUnique400Response](docs/IsPropertyNameUnique400Response.md)
 - [KeyValuePairSupplier](docs/KeyValuePairSupplier.md)
 - [LocalizedDescriptionSupplier](docs/LocalizedDescriptionSupplier.md)
 - [ManualPropertyRegistrationRequestSupplier](docs/ManualPropertyRegistrationRequestSupplier.md)
 - [MediaAuthorAttributionSupplier](docs/MediaAuthorAttributionSupplier.md)
 - [PropertyPolicySupplier](docs/PropertyPolicySupplier.md)
 - [PropertySupplier](docs/PropertySupplier.md)
 - [SimpleAddressSupplier](docs/SimpleAddressSupplier.md)
 - [SimpleDescriptionSupplier](docs/SimpleDescriptionSupplier.md)
 - [SimpleMultimediaSupplier](docs/SimpleMultimediaSupplier.md)
 - [SocialSupplier](docs/SocialSupplier.md)
 - [SubCountryLightweightSupplier](docs/SubCountryLightweightSupplier.md)
 - [SubSubCountryLightweightSupplier](docs/SubSubCountryLightweightSupplier.md)
 - [SupplierLeadSupplier](docs/SupplierLeadSupplier.md)
 - [TravelInventoryRecognitionSupplier](docs/TravelInventoryRecognitionSupplier.md)
 - [UniqueResultSupplier](docs/UniqueResultSupplier.md)
 - [UpsertAddressRequestSupplier](docs/UpsertAddressRequestSupplier.md)


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


