# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Inventory API The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it. This API lets you:  1. Manage customizations. 2. Shareable Links: Manage shareable supplier / inventory links. 3. Inventory: Manage individual inventory items. 4. Lists: Manage curated / ranked grids. 5. Maps: Manage maps.  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.18.5
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from typing import Optional, Set
from typing_extensions import Self

class SellableSupplierUrlAffiliate(BaseModel):
    """
    SellableSupplierUrlAffiliate
    """ # noqa: E501
    id: Optional[StrictStr] = Field(default=None, description="Document UUID")
    created_date: Optional[datetime] = Field(default=None, description="Datetime this record was first created", alias="createdDate")
    last_update: Optional[datetime] = Field(default=None, description="Datetime this record was last updated", alias="lastUpdate")
    version: Optional[StrictInt] = Field(default=None, description="Version property that shows how many times this document has been persisted. Document will not persist if the version property is less than current version property in the system. Result in an optimistic locking exception.")
    user_identifier: Annotated[str, Field(min_length=1, strict=True)] = Field(description="Creator of entry", alias="userIdentifier")
    owner_identifier: Annotated[str, Field(min_length=1, strict=True)] = Field(description="AffiliateAccount identifier", alias="ownerIdentifier")
    name: Annotated[str, Field(min_length=1, strict=True)] = Field(description="Descriptive name of this url for seller use only")
    customization_identifier: Annotated[str, Field(min_length=1, strict=True)] = Field(description="Customization identifier", alias="customizationIdentifier")
    descriptions: Annotated[List[Any], Field(min_length=1, max_length=2147483647)]
    multimedias: Optional[List[Any]] = None
    keywords: Annotated[List[Any], Field(min_length=1, max_length=2147483647)]
    unique_id: Annotated[str, Field(min_length=1, strict=True)] = Field(description="Unique link id", alias="uniqueId")
    twitter_account: Optional[StrictStr] = Field(default=None, description="Twitter account is used with OpenGraph data", alias="twitterAccount")
    facebook_app_id: Optional[StrictStr] = Field(default=None, description="Facebook APP ID is used with OpenGraph data", alias="facebookAppId")
    theme: Optional[StrictStr] = Field(default=None, description="Url theme controls the look and feel of the ad banner.")
    status: StrictStr = Field(description="Url sell status")
    supplier_identifier: Annotated[str, Field(min_length=1, strict=True)] = Field(description="The entity supplying the inventory. Usually a hotel.", alias="supplierIdentifier")
    animate: Optional[StrictBool] = Field(default=False, description="Create an animated gif instead of a list of images")
    animate_delay: Optional[StrictInt] = Field(default=-1, description="Animation delay in milliseconds", alias="animateDelay")
    __properties: ClassVar[List[str]] = ["id", "createdDate", "lastUpdate", "version", "userIdentifier", "ownerIdentifier", "name", "customizationIdentifier", "descriptions", "multimedias", "keywords", "uniqueId", "twitterAccount", "facebookAppId", "theme", "status", "supplierIdentifier", "animate", "animateDelay"]

    @field_validator('theme')
    def theme_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['THEME_1']):
            raise ValueError("must be one of enum values ('THEME_1')")
        return value

    @field_validator('status')
    def status_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['ACTIVE', 'INACTIVE', 'REMOVED']):
            raise ValueError("must be one of enum values ('ACTIVE', 'INACTIVE', 'REMOVED')")
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
        """Create an instance of SellableSupplierUrlAffiliate from a JSON string"""
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
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of SellableSupplierUrlAffiliate from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "createdDate": obj.get("createdDate"),
            "lastUpdate": obj.get("lastUpdate"),
            "version": obj.get("version"),
            "userIdentifier": obj.get("userIdentifier"),
            "ownerIdentifier": obj.get("ownerIdentifier"),
            "name": obj.get("name"),
            "customizationIdentifier": obj.get("customizationIdentifier"),
            "descriptions": obj.get("descriptions"),
            "multimedias": obj.get("multimedias"),
            "keywords": obj.get("keywords"),
            "uniqueId": obj.get("uniqueId"),
            "twitterAccount": obj.get("twitterAccount"),
            "facebookAppId": obj.get("facebookAppId"),
            "theme": obj.get("theme"),
            "status": obj.get("status"),
            "supplierIdentifier": obj.get("supplierIdentifier"),
            "animate": obj.get("animate") if obj.get("animate") is not None else False,
            "animateDelay": obj.get("animateDelay") if obj.get("animateDelay") is not None else -1
        })
        return _obj


