# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/engine-client): A single endpoint to retrieve whitelabel + customization information for the booking engine.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reactive): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant reactive widget for all other entities.   - [TripPay](/reactive): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Extranet Property Registration API This part of the documentation concerns itself about adding new properties to Wink. There are two endpoints for you to onboard a property:  1. Manage leads 2. Manually: Use this endpoint if you already have all the property data. Use case: You want to migrate your existing properties to Wink. 3. Intelligently: With the assistance of Google Business Pages, you can select an existing property on Google, ingest it with the lead endpoint and let us create a Wink property for you. Note: This isn't always straightforward in places with non-standard addresses.  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.16.4
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from wink_sdk_extranet_property_register.models.address_supplier import AddressSupplier
from wink_sdk_extranet_property_register.models.aggregate_greendex_answers_supplier import AggregateGreendexAnswersSupplier
from wink_sdk_extranet_property_register.models.contact_supplier import ContactSupplier
from wink_sdk_extranet_property_register.models.general_manager_supplier import GeneralManagerSupplier
from wink_sdk_extranet_property_register.models.geo_json_point_supplier import GeoJsonPointSupplier
from wink_sdk_extranet_property_register.models.key_value_pair_supplier import KeyValuePairSupplier
from wink_sdk_extranet_property_register.models.localized_description_supplier import LocalizedDescriptionSupplier
from wink_sdk_extranet_property_register.models.property_policy_supplier import PropertyPolicySupplier
from wink_sdk_extranet_property_register.models.simple_multimedia_supplier import SimpleMultimediaSupplier
from wink_sdk_extranet_property_register.models.social_supplier import SocialSupplier
from wink_sdk_extranet_property_register.models.travel_inventory_recognition_supplier import TravelInventoryRecognitionSupplier
from typing import Optional, Set
from typing_extensions import Self

class HotelSupplier(BaseModel):
    """
    Hotel data
    """ # noqa: E501
    hotel_identifier: StrictStr = Field(description="Unique hotel identifier", alias="hotelIdentifier")
    name: StrictStr = Field(description="Unique hotel trade name. The hotel name must be unique. If there are multiple hotels with the same name, we recommend appending destination to the name. [Verify uniqueness here](#operation/isHotelNameUnique).")
    hotel_code: StrictStr = Field(description="A shorter unique code to refer to the hotel. Country Code + 5 digit number", alias="hotelCode")
    local_name: Optional[StrictStr] = Field(default=None, description="Name of the hotel in its local language if you use it for domestic guests.", alias="localName")
    legal_name: StrictStr = Field(description="Legal name of your hotel as it is registered.", alias="legalName")
    url_name: StrictStr = Field(description="Unique url-friendly slug to identify property", alias="urlName")
    currency_code: StrictStr = Field(description="Currency code", alias="currencyCode")
    status: StrictStr = Field(description="wink.travel sets this status as the hotel moves through the payment workflow and manually for approval.")
    external_status: StrictStr = Field(description="Property goes active by changing externalStatus from 6 (Inactive) to 1 (Active) according to OTA property status.", alias="externalStatus")
    multimedias: Optional[List[SimpleMultimediaSupplier]] = Field(default=None, description="List of images / videos of property.")
    recognition_list: Optional[List[TravelInventoryRecognitionSupplier]] = Field(default=None, description="Inventory-level recognition.", alias="recognitionList")
    remote_ip: Optional[StrictStr] = Field(default=None, alias="remoteIp")
    location_category: Optional[StrictStr] = Field(default=None, description="Supported OTA specification `LOC` code. See [OTA geoname data](#operation/showAvailableCodesForCategory)", alias="locationCategory")
    segment_category: Optional[StrictStr] = Field(default=None, description="Supported OTA specification `SEG` code. See [OTA geoname data](#operation/showAvailableCodesForCategory)", alias="segmentCategory")
    hotel_category: Optional[StrictStr] = Field(default=None, description="Supported OTA specification `PCT` code. See [OTA geoname data](#operation/showAvailableCodesForCategory)", alias="hotelCategory")
    architectural_style: Optional[StrictStr] = Field(default=None, description="Supported OTA specification `ARC` code. See [OTA geoname data](#operation/showAvailableCodesForCategory)", alias="architecturalStyle")
    when_built: Optional[StrictStr] = Field(default=None, description="Year the property was constructed.", alias="whenBuilt")
    hotel_chain: Optional[StrictStr] = Field(default=None, description="Hotel chain name if property is part of that chain.", alias="hotelChain")
    hotel_brand: Optional[StrictStr] = Field(default=None, description="Hotel brand name if property is part of that brand.", alias="hotelBrand")
    other_channel_manager: Optional[StrictStr] = Field(default=None, description="If the property is currently using a channel manager but it isn't yet part of our list, chose 'OTHER_CHANNEL_MANAGER' as channelManager and fill in the name of the channel manager here", alias="otherChannelManager")
    license_number: Optional[StrictStr] = Field(default=None, description="If the property has a valid license number to run a hotel in their country, add it here.", alias="licenseNumber")
    stars: Optional[Annotated[int, Field(le=6, strict=True, ge=0)]] = Field(default=None, description="Hotel star rating.")
    general_manager: Optional[GeneralManagerSupplier] = Field(default=None, alias="generalManager")
    short_descriptions: Optional[List[LocalizedDescriptionSupplier]] = Field(default=None, description="Localized short descriptions of property.", alias="shortDescriptions")
    long_descriptions: Optional[List[LocalizedDescriptionSupplier]] = Field(default=None, description="Localized long descriptions of property.", alias="longDescriptions")
    hotel_amenity_codes: Optional[List[StrictStr]] = Field(default=None, description="Supported OTA specification `HAC` code. See [OTA geoname data](#operation/showAvailableCodesForCategory).", alias="hotelAmenityCodes")
    property_accessibility_codes: Optional[List[StrictStr]] = Field(default=None, description="Supported OTA specification `PHY` code. See [OTA geoname data](#operation/showAvailableCodesForCategory).", alias="propertyAccessibilityCodes")
    property_security_codes: Optional[List[StrictStr]] = Field(default=None, description="Supported OTA specification `SEC` code. See [OTA geoname data](#operation/showAvailableCodesForCategory).", alias="propertySecurityCodes")
    location_point: Optional[GeoJsonPointSupplier] = Field(default=None, alias="locationPoint")
    policy: Optional[PropertyPolicySupplier] = None
    socials: Optional[List[SocialSupplier]] = Field(default=None, description="List of all social network account property has.")
    owner_contact: Optional[ContactSupplier] = Field(default=None, alias="ownerContact")
    reservations_contact: Optional[ContactSupplier] = Field(default=None, alias="reservationsContact")
    accounting_contact: Optional[ContactSupplier] = Field(default=None, alias="accountingContact")
    accounting_address: Optional[AddressSupplier] = Field(default=None, alias="accountingAddress")
    lifestyle_types: Optional[List[StrictStr]] = Field(default=None, description="List of all lifestyles property has associated with. See [Lifestyle geoname data](#operation/showLifestyles)", alias="lifestyleTypes")
    green_index_scores: Optional[AggregateGreendexAnswersSupplier] = Field(default=None, alias="greenIndexScores")
    agreement_accepted: StrictBool = Field(description="Property has accepted our terms and conditions.", alias="agreementAccepted")
    marketing_optin_allowed: Optional[StrictBool] = Field(default=None, description="Property agreed to let the payment use its logo and images for marketing purposes (with proper credits).", alias="marketingOptinAllowed")
    logos: Optional[List[SimpleMultimediaSupplier]] = Field(default=None, description="List of logo images of property")
    number_of_rooms: Annotated[int, Field(strict=True, ge=0)] = Field(description="Number of rooms / keys for property", alias="numberOfRooms")
    address: Optional[AddressSupplier] = None
    reservation_desk_start_time: Optional[StrictStr] = Field(default=None, description="If the reservation desk does not operate 24 hours, enter a start time.", alias="reservationDeskStartTime")
    reservation_desk_end_time: Optional[StrictStr] = Field(default=None, description="If the reservation desk does not operate 24 hours, enter an end time.", alias="reservationDeskEndTime")
    website: Optional[StrictStr] = Field(default=None, description="Property brand.com website.")
    google_maps_url: Optional[StrictStr] = Field(default=None, description="Google Maps URL of the place", alias="googleMapsUrl")
    metadata: Optional[Dict[str, Dict[str, Any]]] = Field(default=None, description="Place to put stuff into")
    previous_url_name_list: Optional[List[StrictStr]] = Field(default=None, description="Previous url names", alias="previousUrlNameList")
    rate_provider: Optional[KeyValuePairSupplier] = Field(default=None, alias="rateProvider")
    active: Optional[StrictBool] = Field(default=None, description="Property is both approved and activated.")
    social_networks: Optional[StrictBool] = Field(default=None, description="Whether property has any social networks associated with her profile.", alias="socialNetworks")
    lifestyles: Optional[StrictBool] = Field(default=None, description="Whether property has any lifestyles associated with her profile.")
    full_address: Optional[StrictStr] = Field(default=None, description="Concatenated address into a single string", alias="fullAddress")
    property_active: Optional[StrictBool] = Field(default=None, description="Property activated itself and went live.", alias="propertyActive")
    platform_active: Optional[StrictBool] = Field(default=None, description="Platform approved property.", alias="platformActive")
    contract_signer_full_name: Optional[StrictStr] = Field(default=None, description="Concatenated name of contract signer into one string.", alias="contractSignerFullName")
    __properties: ClassVar[List[str]] = ["hotelIdentifier", "name", "hotelCode", "localName", "legalName", "urlName", "currencyCode", "status", "externalStatus", "multimedias", "recognitionList", "remoteIp", "locationCategory", "segmentCategory", "hotelCategory", "architecturalStyle", "whenBuilt", "hotelChain", "hotelBrand", "otherChannelManager", "licenseNumber", "stars", "generalManager", "shortDescriptions", "longDescriptions", "hotelAmenityCodes", "propertyAccessibilityCodes", "propertySecurityCodes", "locationPoint", "policy", "socials", "ownerContact", "reservationsContact", "accountingContact", "accountingAddress", "lifestyleTypes", "greenIndexScores", "agreementAccepted", "marketingOptinAllowed", "logos", "numberOfRooms", "address", "reservationDeskStartTime", "reservationDeskEndTime", "website", "googleMapsUrl", "metadata", "previousUrlNameList", "rateProvider", "active", "socialNetworks", "lifestyles", "fullAddress", "propertyActive", "platformActive", "contractSignerFullName"]

    @field_validator('status')
    def status_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['ACTIVE', 'DISABLED', 'SUSPENDED', 'REMOVED', 'WAITING_ON_CONTRACT', 'CONTRACT_SIGNED']):
            raise ValueError("must be one of enum values ('ACTIVE', 'DISABLED', 'SUSPENDED', 'REMOVED', 'WAITING_ON_CONTRACT', 'CONTRACT_SIGNED')")
        return value

    @field_validator('lifestyle_types')
    def lifestyle_types_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        for i in value:
            if i not in set(['LIFESTYLE_HEALTH_FITNESS', 'LIFESTYLE_RELAX', 'LIFESTYLE_ADULT_ONLY', 'LIFESTYLE_ADVENTURE', 'LIFESTYLE_BUSINESS', 'LIFESTYLE_LGBT', 'LIFESTYLE_SINGLE_PARENT', 'LIFESTYLE_SOLO_FEMALE', 'LIFESTYLE_BEAUTY', 'LIFESTYLE_FOODIE', 'LIFESTYLE_FAMILY', 'LIFESTYLE_ROMANCE', 'LIFESTYLE_COUPLE', 'LIFESTYLE_SOLO', 'LIFESTYLE_BACKPACKER', 'LIFESTYLE_SHOPPING', 'LIFESTYLE_SPORTS', 'LIFESTYLE_MOUNTAIN', 'LIFESTYLE_BEACH', 'LIFESTYLE_CITY', 'LIFESTYLE_COUNTRY', 'LIFESTYLE_CULTURE', 'LIFESTYLE_ECO']):
                raise ValueError("each list item must be one of ('LIFESTYLE_HEALTH_FITNESS', 'LIFESTYLE_RELAX', 'LIFESTYLE_ADULT_ONLY', 'LIFESTYLE_ADVENTURE', 'LIFESTYLE_BUSINESS', 'LIFESTYLE_LGBT', 'LIFESTYLE_SINGLE_PARENT', 'LIFESTYLE_SOLO_FEMALE', 'LIFESTYLE_BEAUTY', 'LIFESTYLE_FOODIE', 'LIFESTYLE_FAMILY', 'LIFESTYLE_ROMANCE', 'LIFESTYLE_COUPLE', 'LIFESTYLE_SOLO', 'LIFESTYLE_BACKPACKER', 'LIFESTYLE_SHOPPING', 'LIFESTYLE_SPORTS', 'LIFESTYLE_MOUNTAIN', 'LIFESTYLE_BEACH', 'LIFESTYLE_CITY', 'LIFESTYLE_COUNTRY', 'LIFESTYLE_CULTURE', 'LIFESTYLE_ECO')")
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
        """Create an instance of HotelSupplier from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in multimedias (list)
        _items = []
        if self.multimedias:
            for _item_multimedias in self.multimedias:
                if _item_multimedias:
                    _items.append(_item_multimedias.to_dict())
            _dict['multimedias'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in recognition_list (list)
        _items = []
        if self.recognition_list:
            for _item_recognition_list in self.recognition_list:
                if _item_recognition_list:
                    _items.append(_item_recognition_list.to_dict())
            _dict['recognitionList'] = _items
        # override the default output from pydantic by calling `to_dict()` of general_manager
        if self.general_manager:
            _dict['generalManager'] = self.general_manager.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in short_descriptions (list)
        _items = []
        if self.short_descriptions:
            for _item_short_descriptions in self.short_descriptions:
                if _item_short_descriptions:
                    _items.append(_item_short_descriptions.to_dict())
            _dict['shortDescriptions'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in long_descriptions (list)
        _items = []
        if self.long_descriptions:
            for _item_long_descriptions in self.long_descriptions:
                if _item_long_descriptions:
                    _items.append(_item_long_descriptions.to_dict())
            _dict['longDescriptions'] = _items
        # override the default output from pydantic by calling `to_dict()` of location_point
        if self.location_point:
            _dict['locationPoint'] = self.location_point.to_dict()
        # override the default output from pydantic by calling `to_dict()` of policy
        if self.policy:
            _dict['policy'] = self.policy.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in socials (list)
        _items = []
        if self.socials:
            for _item_socials in self.socials:
                if _item_socials:
                    _items.append(_item_socials.to_dict())
            _dict['socials'] = _items
        # override the default output from pydantic by calling `to_dict()` of owner_contact
        if self.owner_contact:
            _dict['ownerContact'] = self.owner_contact.to_dict()
        # override the default output from pydantic by calling `to_dict()` of reservations_contact
        if self.reservations_contact:
            _dict['reservationsContact'] = self.reservations_contact.to_dict()
        # override the default output from pydantic by calling `to_dict()` of accounting_contact
        if self.accounting_contact:
            _dict['accountingContact'] = self.accounting_contact.to_dict()
        # override the default output from pydantic by calling `to_dict()` of accounting_address
        if self.accounting_address:
            _dict['accountingAddress'] = self.accounting_address.to_dict()
        # override the default output from pydantic by calling `to_dict()` of green_index_scores
        if self.green_index_scores:
            _dict['greenIndexScores'] = self.green_index_scores.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in logos (list)
        _items = []
        if self.logos:
            for _item_logos in self.logos:
                if _item_logos:
                    _items.append(_item_logos.to_dict())
            _dict['logos'] = _items
        # override the default output from pydantic by calling `to_dict()` of address
        if self.address:
            _dict['address'] = self.address.to_dict()
        # override the default output from pydantic by calling `to_dict()` of rate_provider
        if self.rate_provider:
            _dict['rateProvider'] = self.rate_provider.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of HotelSupplier from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "hotelIdentifier": obj.get("hotelIdentifier"),
            "name": obj.get("name"),
            "hotelCode": obj.get("hotelCode"),
            "localName": obj.get("localName"),
            "legalName": obj.get("legalName"),
            "urlName": obj.get("urlName"),
            "currencyCode": obj.get("currencyCode"),
            "status": obj.get("status") if obj.get("status") is not None else 'WAITING_ON_CONTRACT',
            "externalStatus": obj.get("externalStatus") if obj.get("externalStatus") is not None else '6',
            "multimedias": [SimpleMultimediaSupplier.from_dict(_item) for _item in obj["multimedias"]] if obj.get("multimedias") is not None else None,
            "recognitionList": [TravelInventoryRecognitionSupplier.from_dict(_item) for _item in obj["recognitionList"]] if obj.get("recognitionList") is not None else None,
            "remoteIp": obj.get("remoteIp"),
            "locationCategory": obj.get("locationCategory"),
            "segmentCategory": obj.get("segmentCategory"),
            "hotelCategory": obj.get("hotelCategory"),
            "architecturalStyle": obj.get("architecturalStyle"),
            "whenBuilt": obj.get("whenBuilt"),
            "hotelChain": obj.get("hotelChain"),
            "hotelBrand": obj.get("hotelBrand"),
            "otherChannelManager": obj.get("otherChannelManager"),
            "licenseNumber": obj.get("licenseNumber"),
            "stars": obj.get("stars"),
            "generalManager": GeneralManagerSupplier.from_dict(obj["generalManager"]) if obj.get("generalManager") is not None else None,
            "shortDescriptions": [LocalizedDescriptionSupplier.from_dict(_item) for _item in obj["shortDescriptions"]] if obj.get("shortDescriptions") is not None else None,
            "longDescriptions": [LocalizedDescriptionSupplier.from_dict(_item) for _item in obj["longDescriptions"]] if obj.get("longDescriptions") is not None else None,
            "hotelAmenityCodes": obj.get("hotelAmenityCodes"),
            "propertyAccessibilityCodes": obj.get("propertyAccessibilityCodes"),
            "propertySecurityCodes": obj.get("propertySecurityCodes"),
            "locationPoint": GeoJsonPointSupplier.from_dict(obj["locationPoint"]) if obj.get("locationPoint") is not None else None,
            "policy": PropertyPolicySupplier.from_dict(obj["policy"]) if obj.get("policy") is not None else None,
            "socials": [SocialSupplier.from_dict(_item) for _item in obj["socials"]] if obj.get("socials") is not None else None,
            "ownerContact": ContactSupplier.from_dict(obj["ownerContact"]) if obj.get("ownerContact") is not None else None,
            "reservationsContact": ContactSupplier.from_dict(obj["reservationsContact"]) if obj.get("reservationsContact") is not None else None,
            "accountingContact": ContactSupplier.from_dict(obj["accountingContact"]) if obj.get("accountingContact") is not None else None,
            "accountingAddress": AddressSupplier.from_dict(obj["accountingAddress"]) if obj.get("accountingAddress") is not None else None,
            "lifestyleTypes": obj.get("lifestyleTypes"),
            "greenIndexScores": AggregateGreendexAnswersSupplier.from_dict(obj["greenIndexScores"]) if obj.get("greenIndexScores") is not None else None,
            "agreementAccepted": obj.get("agreementAccepted"),
            "marketingOptinAllowed": obj.get("marketingOptinAllowed"),
            "logos": [SimpleMultimediaSupplier.from_dict(_item) for _item in obj["logos"]] if obj.get("logos") is not None else None,
            "numberOfRooms": obj.get("numberOfRooms"),
            "address": AddressSupplier.from_dict(obj["address"]) if obj.get("address") is not None else None,
            "reservationDeskStartTime": obj.get("reservationDeskStartTime"),
            "reservationDeskEndTime": obj.get("reservationDeskEndTime"),
            "website": obj.get("website"),
            "googleMapsUrl": obj.get("googleMapsUrl"),
            "metadata": obj.get("metadata"),
            "previousUrlNameList": obj.get("previousUrlNameList"),
            "rateProvider": KeyValuePairSupplier.from_dict(obj["rateProvider"]) if obj.get("rateProvider") is not None else None,
            "active": obj.get("active"),
            "socialNetworks": obj.get("socialNetworks"),
            "lifestyles": obj.get("lifestyles"),
            "fullAddress": obj.get("fullAddress"),
            "propertyActive": obj.get("propertyActive"),
            "platformActive": obj.get("platformActive"),
            "contractSignerFullName": obj.get("contractSignerFullName")
        })
        return _obj


