# coding: utf-8

# flake8: noqa

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Inventory API The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it. This API lets you:  1. Manage customizations. 2. Shareable Links: Manage shareable supplier / inventory links. 3. Inventory: Manage individual inventory items. 4. Lists: Manage curated / ranked grids. 5. Maps: Manage maps.  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.18.5
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


__version__ = "0.0.40"

# import apis into sdk package
from wink_sdk_affiliate_inventory.api.customization_api import CustomizationApi
from wink_sdk_affiliate_inventory.api.embeddable_inventories_api import EmbeddableInventoriesApi
from wink_sdk_affiliate_inventory.api.grids_api import GridsApi
from wink_sdk_affiliate_inventory.api.inventory_links_api import InventoryLinksApi
from wink_sdk_affiliate_inventory.api.items_api import ItemsApi
from wink_sdk_affiliate_inventory.api.maps_api import MapsApi
from wink_sdk_affiliate_inventory.api.ranked_grids_api import RankedGridsApi
from wink_sdk_affiliate_inventory.api.supplier_links_api import SupplierLinksApi

# import ApiClient
from wink_sdk_affiliate_inventory.api_response import ApiResponse
from wink_sdk_affiliate_inventory.api_client import ApiClient
from wink_sdk_affiliate_inventory.configuration import Configuration
from wink_sdk_affiliate_inventory.exceptions import OpenApiException
from wink_sdk_affiliate_inventory.exceptions import ApiTypeError
from wink_sdk_affiliate_inventory.exceptions import ApiValueError
from wink_sdk_affiliate_inventory.exceptions import ApiKeyError
from wink_sdk_affiliate_inventory.exceptions import ApiAttributeError
from wink_sdk_affiliate_inventory.exceptions import ApiException

# import models into sdk package
from wink_sdk_affiliate_inventory.models.boolean_response_affiliate import BooleanResponseAffiliate
from wink_sdk_affiliate_inventory.models.campaign_inventory_affiliate import CampaignInventoryAffiliate
from wink_sdk_affiliate_inventory.models.child_affiliate import ChildAffiliate
from wink_sdk_affiliate_inventory.models.configurable_geo_json_circle_affiliate import ConfigurableGeoJsonCircleAffiliate
from wink_sdk_affiliate_inventory.models.country_lightweight_affiliate import CountryLightweightAffiliate
from wink_sdk_affiliate_inventory.models.create_inventory_map_syndication_entry_request_affiliate import CreateInventoryMapSyndicationEntryRequestAffiliate
from wink_sdk_affiliate_inventory.models.create_sellable_item_syndicated_item_request_affiliate import CreateSellableItemSyndicatedItemRequestAffiliate
from wink_sdk_affiliate_inventory.models.create_sellable_ranked_list_syndicated_item_request_affiliate import CreateSellableRankedListSyndicatedItemRequestAffiliate
from wink_sdk_affiliate_inventory.models.create_seller_url_syndication_entry_request_affiliate import CreateSellerUrlSyndicationEntryRequestAffiliate
from wink_sdk_affiliate_inventory.models.create_static_list_syndication_entry_request_affiliate import CreateStaticListSyndicationEntryRequestAffiliate
from wink_sdk_affiliate_inventory.models.create_supplier_url_syndication_entry_request_affiliate import CreateSupplierUrlSyndicationEntryRequestAffiliate
from wink_sdk_affiliate_inventory.models.custom_monetary_amount import CustomMonetaryAmount
from wink_sdk_affiliate_inventory.models.customization_affiliate import CustomizationAffiliate
from wink_sdk_affiliate_inventory.models.customization_theme_colors_affiliate import CustomizationThemeColorsAffiliate
from wink_sdk_affiliate_inventory.models.generic_error_message import GenericErrorMessage
from wink_sdk_affiliate_inventory.models.geo_json_point_affiliate import GeoJsonPointAffiliate
from wink_sdk_affiliate_inventory.models.geo_name_lightweight_affiliate import GeoNameLightweightAffiliate
from wink_sdk_affiliate_inventory.models.inventory_map_affiliate import InventoryMapAffiliate
from wink_sdk_affiliate_inventory.models.inventory_map_marker_affiliate import InventoryMapMarkerAffiliate
from wink_sdk_affiliate_inventory.models.key_value_pair_affiliate import KeyValuePairAffiliate
from wink_sdk_affiliate_inventory.models.lookup_lightweight_affiliate import LookupLightweightAffiliate
from wink_sdk_affiliate_inventory.models.media_author_attribution_affiliate import MediaAuthorAttributionAffiliate
from wink_sdk_affiliate_inventory.models.room_configuration_affiliate import RoomConfigurationAffiliate
from wink_sdk_affiliate_inventory.models.sellable_inventory_url_affiliate import SellableInventoryUrlAffiliate
from wink_sdk_affiliate_inventory.models.sellable_item_affiliate import SellableItemAffiliate
from wink_sdk_affiliate_inventory.models.sellable_list_affiliate import SellableListAffiliate
from wink_sdk_affiliate_inventory.models.sellable_ranked_list_affiliate import SellableRankedListAffiliate
from wink_sdk_affiliate_inventory.models.sellable_supplier_url_affiliate import SellableSupplierUrlAffiliate
from wink_sdk_affiliate_inventory.models.show_supplier_url400_response import ShowSupplierUrl400Response
from wink_sdk_affiliate_inventory.models.simple_description_affiliate import SimpleDescriptionAffiliate
from wink_sdk_affiliate_inventory.models.simple_multimedia_affiliate import SimpleMultimediaAffiliate
from wink_sdk_affiliate_inventory.models.sub_country_lightweight_affiliate import SubCountryLightweightAffiliate
from wink_sdk_affiliate_inventory.models.sub_sub_country_lightweight_affiliate import SubSubCountryLightweightAffiliate
from wink_sdk_affiliate_inventory.models.syndicated_item_affiliate import SyndicatedItemAffiliate
from wink_sdk_affiliate_inventory.models.upsert_customization_request_affiliate import UpsertCustomizationRequestAffiliate
from wink_sdk_affiliate_inventory.models.upsert_inventory_map_request_affiliate import UpsertInventoryMapRequestAffiliate
from wink_sdk_affiliate_inventory.models.upsert_sellable_inventory_url_request_affiliate import UpsertSellableInventoryUrlRequestAffiliate
from wink_sdk_affiliate_inventory.models.upsert_sellable_item_request_affiliate import UpsertSellableItemRequestAffiliate
from wink_sdk_affiliate_inventory.models.upsert_sellable_list_request_affiliate import UpsertSellableListRequestAffiliate
from wink_sdk_affiliate_inventory.models.upsert_sellable_ranked_list_request_affiliate import UpsertSellableRankedListRequestAffiliate
from wink_sdk_affiliate_inventory.models.upsert_sellable_supplier_url_request_affiliate import UpsertSellableSupplierUrlRequestAffiliate
from wink_sdk_affiliate_inventory.models.upsert_supplier_inventory_map_request_affiliate import UpsertSupplierInventoryMapRequestAffiliate
from wink_sdk_affiliate_inventory.models.upsert_supplier_sellable_item_request_affiliate import UpsertSupplierSellableItemRequestAffiliate
