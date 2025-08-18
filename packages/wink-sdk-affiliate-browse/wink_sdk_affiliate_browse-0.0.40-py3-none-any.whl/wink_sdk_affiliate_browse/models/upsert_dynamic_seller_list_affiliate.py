# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/engine-client): A single endpoint to retrieve whitelabel + customization information for the booking engine.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reactive): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant reactive widget for all other entities.   - [TripPay](/reactive): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Browse API The Browse API exposes endpoints to find suppliers and inventory to sell. This API lets you:  1. Browse: Find inventory and suppliers. 2. Saved Search: Manage saved searches 3. Curated List: Manage curated lists  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.16.4
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from wink_sdk_affiliate_browse.models.geo_json_point_affiliate import GeoJsonPointAffiliate
from typing import Optional, Set
from typing_extensions import Self

class UpsertDynamicSellerListAffiliate(BaseModel):
    """
    UpsertDynamicSellerListAffiliate
    """ # noqa: E501
    name: StrictStr = Field(description="Name of dynamic list for when user want to persist it")
    property_name: Optional[StrictStr] = Field(default=None, description="Regex expression filter matching on property name.", alias="propertyName")
    location_categories: Optional[List[StrictStr]] = Field(default=None, description="Supported OTA specification `LOC` code. See [OTA geoname data](#operation/showAvailableCodesForCategory)", alias="locationCategories")
    segment_categories: Optional[List[StrictStr]] = Field(default=None, description="Supported OTA specification `SEG` code. See [OTA geoname data](#operation/showAvailableCodesForCategory)", alias="segmentCategories")
    hotel_categories: Optional[List[StrictStr]] = Field(default=None, description="Supported OTA specification `PCT` code. See [OTA geoname data](#operation/showAvailableCodesForCategory)", alias="hotelCategories")
    architectural_styles: Optional[List[StrictStr]] = Field(default=None, description="Supported OTA specification `ARC` code. See [OTA geoname data](#operation/showAvailableCodesForCategory)", alias="architecturalStyles")
    inventory_name: Optional[StrictStr] = Field(default=None, description="Regex expression filter matching on blocking name", alias="inventoryName")
    continents: Optional[List[StrictStr]] = Field(default=None, description="Continent filter")
    countries: Optional[List[StrictStr]] = Field(default=None, description="Country filter")
    cities: Optional[List[StrictStr]] = Field(default=None, description="City filter")
    show_eco_friendly: Optional[StrictBool] = Field(default=False, description="Filter on eco-friendly hotels", alias="showEcoFriendly")
    show_pet_friendly: Optional[StrictBool] = Field(default=False, description="Filter on pet-friendly hotels", alias="showPetFriendly")
    show_child_friendly: Optional[StrictBool] = Field(default=False, description="Filter on child-friendly hotels", alias="showChildFriendly")
    show_popular: Optional[StrictBool] = Field(default=False, description="Filter on hotel that has had a certain amount of bookings", alias="showPopular")
    show_direct_only: Optional[StrictBool] = Field(default=False, description="Filter on direct blocking", alias="showDirectOnly")
    lifestyles: Optional[List[StrictStr]] = Field(default=None, description="Filter on lifestyles")
    hotel_stars: Optional[StrictInt] = Field(default=None, description="Filter on number of stars the hotel has.", alias="hotelStars")
    aggregate_review_rating: Optional[StrictInt] = Field(default=None, description="Filter on aggregate review score the hotel has", alias="aggregateReviewRating")
    near_point: Optional[GeoJsonPointAffiliate] = Field(default=None, alias="nearPoint")
    radius_in_meters: Optional[StrictInt] = Field(default=None, description="Use this in conjunction with `nearPoint`. Control the distance from point we are searching for.", alias="radiusInMeters")
    inventory_types: Optional[List[StrictStr]] = Field(default=None, description="Filter on blocking types", alias="inventoryTypes")
    primary_order_by: Optional[StrictStr] = Field(default=None, description="Control how you want the search results sorted. Options are:   - 1: Inventory name - 2: Price: High to low - 3: Price: Low to high - 4: Commission: High to low - 5: Commission: Low to high - 6: Discount: High to low - 7: Discount: Low to high ", alias="primaryOrderBy")
    __properties: ClassVar[List[str]] = ["name", "propertyName", "locationCategories", "segmentCategories", "hotelCategories", "architecturalStyles", "inventoryName", "continents", "countries", "cities", "showEcoFriendly", "showPetFriendly", "showChildFriendly", "showPopular", "showDirectOnly", "lifestyles", "hotelStars", "aggregateReviewRating", "nearPoint", "radiusInMeters", "inventoryTypes", "primaryOrderBy"]

    @field_validator('lifestyles')
    def lifestyles_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        for i in value:
            if i not in set(['LIFESTYLE_HEALTH_FITNESS', 'LIFESTYLE_RELAX', 'LIFESTYLE_ADULT_ONLY', 'LIFESTYLE_ADVENTURE', 'LIFESTYLE_BUSINESS', 'LIFESTYLE_LGBT', 'LIFESTYLE_SINGLE_PARENT', 'LIFESTYLE_SOLO_FEMALE', 'LIFESTYLE_BEAUTY', 'LIFESTYLE_FOODIE', 'LIFESTYLE_FAMILY', 'LIFESTYLE_ROMANCE', 'LIFESTYLE_COUPLE', 'LIFESTYLE_SOLO', 'LIFESTYLE_BACKPACKER', 'LIFESTYLE_SHOPPING', 'LIFESTYLE_SPORTS', 'LIFESTYLE_MOUNTAIN', 'LIFESTYLE_BEACH', 'LIFESTYLE_CITY', 'LIFESTYLE_COUNTRY', 'LIFESTYLE_CULTURE', 'LIFESTYLE_ECO']):
                raise ValueError("each list item must be one of ('LIFESTYLE_HEALTH_FITNESS', 'LIFESTYLE_RELAX', 'LIFESTYLE_ADULT_ONLY', 'LIFESTYLE_ADVENTURE', 'LIFESTYLE_BUSINESS', 'LIFESTYLE_LGBT', 'LIFESTYLE_SINGLE_PARENT', 'LIFESTYLE_SOLO_FEMALE', 'LIFESTYLE_BEAUTY', 'LIFESTYLE_FOODIE', 'LIFESTYLE_FAMILY', 'LIFESTYLE_ROMANCE', 'LIFESTYLE_COUPLE', 'LIFESTYLE_SOLO', 'LIFESTYLE_BACKPACKER', 'LIFESTYLE_SHOPPING', 'LIFESTYLE_SPORTS', 'LIFESTYLE_MOUNTAIN', 'LIFESTYLE_BEACH', 'LIFESTYLE_CITY', 'LIFESTYLE_COUNTRY', 'LIFESTYLE_CULTURE', 'LIFESTYLE_ECO')")
        return value

    @field_validator('inventory_types')
    def inventory_types_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        for i in value:
            if i not in set(['GUEST_ROOM', 'ADD_ON', 'MEETING_ROOM', 'RESTAURANT', 'SPA', 'ATTRACTION', 'PLACE', 'ACTIVITY']):
                raise ValueError("each list item must be one of ('GUEST_ROOM', 'ADD_ON', 'MEETING_ROOM', 'RESTAURANT', 'SPA', 'ATTRACTION', 'PLACE', 'ACTIVITY')")
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
        """Create an instance of UpsertDynamicSellerListAffiliate from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of near_point
        if self.near_point:
            _dict['nearPoint'] = self.near_point.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of UpsertDynamicSellerListAffiliate from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "name": obj.get("name"),
            "propertyName": obj.get("propertyName"),
            "locationCategories": obj.get("locationCategories"),
            "segmentCategories": obj.get("segmentCategories"),
            "hotelCategories": obj.get("hotelCategories"),
            "architecturalStyles": obj.get("architecturalStyles"),
            "inventoryName": obj.get("inventoryName"),
            "continents": obj.get("continents"),
            "countries": obj.get("countries"),
            "cities": obj.get("cities"),
            "showEcoFriendly": obj.get("showEcoFriendly") if obj.get("showEcoFriendly") is not None else False,
            "showPetFriendly": obj.get("showPetFriendly") if obj.get("showPetFriendly") is not None else False,
            "showChildFriendly": obj.get("showChildFriendly") if obj.get("showChildFriendly") is not None else False,
            "showPopular": obj.get("showPopular") if obj.get("showPopular") is not None else False,
            "showDirectOnly": obj.get("showDirectOnly") if obj.get("showDirectOnly") is not None else False,
            "lifestyles": obj.get("lifestyles"),
            "hotelStars": obj.get("hotelStars"),
            "aggregateReviewRating": obj.get("aggregateReviewRating"),
            "nearPoint": GeoJsonPointAffiliate.from_dict(obj["nearPoint"]) if obj.get("nearPoint") is not None else None,
            "radiusInMeters": obj.get("radiusInMeters"),
            "inventoryTypes": obj.get("inventoryTypes"),
            "primaryOrderBy": obj.get("primaryOrderBy")
        })
        return _obj


