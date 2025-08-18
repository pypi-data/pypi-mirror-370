# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Extranet Distribution API The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink. This API lets you:  1. Verifier: Test your availability and promotions and create test bookings to simulate the entire booking workflow. 2. Sales Channels: Manage your sales channels. 3. Explore Network: Find new affiliates to work with. 4. Inventory: Manage inventory at the sales channel-level. 5. Calendars: Manage availability calendars for all your inventory.  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.18.5
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import date
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Union
from typing_extensions import Annotated
from wink_sdk_extranet_distribution.models.custom_monetary_amount import CustomMonetaryAmount
from wink_sdk_extranet_distribution.models.daily_rate_rate_supplier_details import DailyRateRateSupplierDetails
from wink_sdk_extranet_distribution.models.localized_description_supplier_details import LocalizedDescriptionSupplierDetails
from wink_sdk_extranet_distribution.models.quote_lightweight_supplier_details import QuoteLightweightSupplierDetails
from typing import Optional, Set
from typing_extensions import Self

class DailyRateSupplierDetails(BaseModel):
    """
    DailyRateSupplierDetails
    """ # noqa: E501
    source_base_rate: Optional[CustomMonetaryAmount] = Field(default=None, alias="sourceBaseRate")
    internal_base_rate: Optional[CustomMonetaryAmount] = Field(default=None, alias="internalBaseRate")
    user_specified_currency_base_rate: Optional[CustomMonetaryAmount] = Field(default=None, alias="userSpecifiedCurrencyBaseRate")
    source_extra_pax_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="sourceExtraPaxModifier")
    internal_extra_pax_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="internalExtraPaxModifier")
    user_specified_currency_extra_pax_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="userSpecifiedCurrencyExtraPaxModifier")
    source_extra_child_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="sourceExtraChildModifier")
    internal_extra_child_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="internalExtraChildModifier")
    user_specified_currency_extra_child_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="userSpecifiedCurrencyExtraChildModifier")
    source_single_occupant_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="sourceSingleOccupantModifier")
    internal_single_occupant_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="internalSingleOccupantModifier")
    user_specified_currency_single_occupant_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="userSpecifiedCurrencySingleOccupantModifier")
    source_promotional_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="sourcePromotionalModifier")
    internal_promotional_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="internalPromotionalModifier")
    user_specified_currency_promotional_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="userSpecifiedCurrencyPromotionalModifier")
    source_premium_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="sourcePremiumModifier")
    internal_premium_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="internalPremiumModifier")
    user_specified_currency_premium_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="userSpecifiedCurrencyPremiumModifier")
    source_channel_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="sourceChannelModifier")
    internal_channel_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="internalChannelModifier")
    user_specified_currency_channel_modifier: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="userSpecifiedCurrencyChannelModifier")
    available: Optional[StrictBool] = None
    is_start_date: Optional[StrictBool] = Field(default=None, alias="isStartDate")
    is_end_date: Optional[StrictBool] = Field(default=None, alias="isEndDate")
    is_between_date: Optional[StrictBool] = Field(default=None, alias="isBetweenDate")
    is_last_night: Optional[StrictBool] = Field(default=None, alias="isLastNight")
    offer_details: Optional[List[LocalizedDescriptionSupplierDetails]] = Field(default=None, alias="offerDetails")
    has_modification: Optional[StrictBool] = Field(default=None, alias="hasModification")
    is_bundled_modifier: Optional[StrictBool] = Field(default=None, alias="isBundledModifier")
    has_channel_discount: Optional[StrictBool] = Field(default=None, alias="hasChannelDiscount")
    channel_discount_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="channelDiscountPercent")
    promotional_discount_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="promotionalDiscountPercent")
    premium_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="premiumPercent")
    promotion: Optional[StrictStr] = None
    adults: Optional[StrictInt] = None
    children: Optional[StrictInt] = None
    rate: DailyRateRateSupplierDetails
    max_adult_occupancy: Annotated[int, Field(strict=True, ge=1)] = Field(description="Maximum number of adults allowed in a room type.", alias="maxAdultOccupancy")
    max_child_occupancy: Annotated[int, Field(strict=True, ge=0)] = Field(description="Maximum number of children allowed in a room type.", alias="maxChildOccupancy")
    included_adult_occupancy: Annotated[int, Field(strict=True, ge=0)] = Field(description="The number of pax the room price was meant for", alias="includedAdultOccupancy")
    included_child_occupancy: Annotated[int, Field(strict=True, ge=0)] = Field(description="The number of children the room price was meant for", alias="includedChildOccupancy")
    source_to_user_currency_quote: QuoteLightweightSupplierDetails = Field(alias="sourceToUserCurrencyQuote")
    source_to_internal_currency_quote: QuoteLightweightSupplierDetails = Field(alias="sourceToInternalCurrencyQuote")
    phantom: StrictBool
    start_date: Optional[StrictBool] = Field(default=None, alias="startDate")
    between_date: Optional[StrictBool] = Field(default=None, alias="betweenDate")
    last_night: Optional[StrictBool] = Field(default=None, alias="lastNight")
    bundled_modifier: Optional[StrictBool] = Field(default=None, alias="bundledModifier")
    close_on_departure: Optional[StrictBool] = Field(default=None, alias="closeOnDeparture")
    inventory_available: Optional[StrictBool] = Field(default=None, alias="inventoryAvailable")
    master_availability: Optional[StrictBool] = Field(default=None, alias="masterAvailability")
    close_on_arrival: Optional[StrictBool] = Field(default=None, alias="closeOnArrival")
    rate_identifier: Optional[StrictStr] = Field(default=None, alias="rateIdentifier")
    var_date: Optional[date] = Field(default=None, alias="date")
    source: Optional[StrictStr] = None
    quantity: Optional[StrictInt] = None
    source_rate: Optional[CustomMonetaryAmount] = Field(default=None, alias="sourceRate")
    user_specified_currency_rate: Optional[CustomMonetaryAmount] = Field(default=None, alias="userSpecifiedCurrencyRate")
    internal_rate: Optional[CustomMonetaryAmount] = Field(default=None, alias="internalRate")
    end_date: Optional[StrictBool] = Field(default=None, alias="endDate")
    max_occupancy: Optional[StrictInt] = Field(default=None, alias="maxOccupancy")
    min_occupancy: Optional[StrictInt] = Field(default=None, alias="minOccupancy")
    base_rate: Optional[CustomMonetaryAmount] = Field(default=None, alias="baseRate")
    min_los: Optional[StrictInt] = Field(default=None, alias="minLOS")
    max_los: Optional[StrictInt] = Field(default=None, alias="maxLOS")
    total_discount_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="totalDiscountPercent")
    __properties: ClassVar[List[str]] = ["sourceBaseRate", "internalBaseRate", "userSpecifiedCurrencyBaseRate", "sourceExtraPaxModifier", "internalExtraPaxModifier", "userSpecifiedCurrencyExtraPaxModifier", "sourceExtraChildModifier", "internalExtraChildModifier", "userSpecifiedCurrencyExtraChildModifier", "sourceSingleOccupantModifier", "internalSingleOccupantModifier", "userSpecifiedCurrencySingleOccupantModifier", "sourcePromotionalModifier", "internalPromotionalModifier", "userSpecifiedCurrencyPromotionalModifier", "sourcePremiumModifier", "internalPremiumModifier", "userSpecifiedCurrencyPremiumModifier", "sourceChannelModifier", "internalChannelModifier", "userSpecifiedCurrencyChannelModifier", "available", "isStartDate", "isEndDate", "isBetweenDate", "isLastNight", "offerDetails", "hasModification", "isBundledModifier", "hasChannelDiscount", "channelDiscountPercent", "promotionalDiscountPercent", "premiumPercent", "promotion", "adults", "children", "rate", "maxAdultOccupancy", "maxChildOccupancy", "includedAdultOccupancy", "includedChildOccupancy", "sourceToUserCurrencyQuote", "sourceToInternalCurrencyQuote", "phantom", "startDate", "betweenDate", "lastNight", "bundledModifier", "closeOnDeparture", "inventoryAvailable", "masterAvailability", "closeOnArrival", "rateIdentifier", "date", "source", "quantity", "sourceRate", "userSpecifiedCurrencyRate", "internalRate", "endDate", "maxOccupancy", "minOccupancy", "baseRate", "minLOS", "maxLOS", "totalDiscountPercent"]

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
        """Create an instance of DailyRateSupplierDetails from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of source_base_rate
        if self.source_base_rate:
            _dict['sourceBaseRate'] = self.source_base_rate.to_dict()
        # override the default output from pydantic by calling `to_dict()` of internal_base_rate
        if self.internal_base_rate:
            _dict['internalBaseRate'] = self.internal_base_rate.to_dict()
        # override the default output from pydantic by calling `to_dict()` of user_specified_currency_base_rate
        if self.user_specified_currency_base_rate:
            _dict['userSpecifiedCurrencyBaseRate'] = self.user_specified_currency_base_rate.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in offer_details (list)
        _items = []
        if self.offer_details:
            for _item_offer_details in self.offer_details:
                if _item_offer_details:
                    _items.append(_item_offer_details.to_dict())
            _dict['offerDetails'] = _items
        # override the default output from pydantic by calling `to_dict()` of rate
        if self.rate:
            _dict['rate'] = self.rate.to_dict()
        # override the default output from pydantic by calling `to_dict()` of source_to_user_currency_quote
        if self.source_to_user_currency_quote:
            _dict['sourceToUserCurrencyQuote'] = self.source_to_user_currency_quote.to_dict()
        # override the default output from pydantic by calling `to_dict()` of source_to_internal_currency_quote
        if self.source_to_internal_currency_quote:
            _dict['sourceToInternalCurrencyQuote'] = self.source_to_internal_currency_quote.to_dict()
        # override the default output from pydantic by calling `to_dict()` of source_rate
        if self.source_rate:
            _dict['sourceRate'] = self.source_rate.to_dict()
        # override the default output from pydantic by calling `to_dict()` of user_specified_currency_rate
        if self.user_specified_currency_rate:
            _dict['userSpecifiedCurrencyRate'] = self.user_specified_currency_rate.to_dict()
        # override the default output from pydantic by calling `to_dict()` of internal_rate
        if self.internal_rate:
            _dict['internalRate'] = self.internal_rate.to_dict()
        # override the default output from pydantic by calling `to_dict()` of base_rate
        if self.base_rate:
            _dict['baseRate'] = self.base_rate.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of DailyRateSupplierDetails from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "sourceBaseRate": CustomMonetaryAmount.from_dict(obj["sourceBaseRate"]) if obj.get("sourceBaseRate") is not None else None,
            "internalBaseRate": CustomMonetaryAmount.from_dict(obj["internalBaseRate"]) if obj.get("internalBaseRate") is not None else None,
            "userSpecifiedCurrencyBaseRate": CustomMonetaryAmount.from_dict(obj["userSpecifiedCurrencyBaseRate"]) if obj.get("userSpecifiedCurrencyBaseRate") is not None else None,
            "sourceExtraPaxModifier": obj.get("sourceExtraPaxModifier"),
            "internalExtraPaxModifier": obj.get("internalExtraPaxModifier"),
            "userSpecifiedCurrencyExtraPaxModifier": obj.get("userSpecifiedCurrencyExtraPaxModifier"),
            "sourceExtraChildModifier": obj.get("sourceExtraChildModifier"),
            "internalExtraChildModifier": obj.get("internalExtraChildModifier"),
            "userSpecifiedCurrencyExtraChildModifier": obj.get("userSpecifiedCurrencyExtraChildModifier"),
            "sourceSingleOccupantModifier": obj.get("sourceSingleOccupantModifier"),
            "internalSingleOccupantModifier": obj.get("internalSingleOccupantModifier"),
            "userSpecifiedCurrencySingleOccupantModifier": obj.get("userSpecifiedCurrencySingleOccupantModifier"),
            "sourcePromotionalModifier": obj.get("sourcePromotionalModifier"),
            "internalPromotionalModifier": obj.get("internalPromotionalModifier"),
            "userSpecifiedCurrencyPromotionalModifier": obj.get("userSpecifiedCurrencyPromotionalModifier"),
            "sourcePremiumModifier": obj.get("sourcePremiumModifier"),
            "internalPremiumModifier": obj.get("internalPremiumModifier"),
            "userSpecifiedCurrencyPremiumModifier": obj.get("userSpecifiedCurrencyPremiumModifier"),
            "sourceChannelModifier": obj.get("sourceChannelModifier"),
            "internalChannelModifier": obj.get("internalChannelModifier"),
            "userSpecifiedCurrencyChannelModifier": obj.get("userSpecifiedCurrencyChannelModifier"),
            "available": obj.get("available"),
            "isStartDate": obj.get("isStartDate"),
            "isEndDate": obj.get("isEndDate"),
            "isBetweenDate": obj.get("isBetweenDate"),
            "isLastNight": obj.get("isLastNight"),
            "offerDetails": [LocalizedDescriptionSupplierDetails.from_dict(_item) for _item in obj["offerDetails"]] if obj.get("offerDetails") is not None else None,
            "hasModification": obj.get("hasModification"),
            "isBundledModifier": obj.get("isBundledModifier"),
            "hasChannelDiscount": obj.get("hasChannelDiscount"),
            "channelDiscountPercent": obj.get("channelDiscountPercent"),
            "promotionalDiscountPercent": obj.get("promotionalDiscountPercent"),
            "premiumPercent": obj.get("premiumPercent"),
            "promotion": obj.get("promotion"),
            "adults": obj.get("adults"),
            "children": obj.get("children"),
            "rate": DailyRateRateSupplierDetails.from_dict(obj["rate"]) if obj.get("rate") is not None else None,
            "maxAdultOccupancy": obj.get("maxAdultOccupancy") if obj.get("maxAdultOccupancy") is not None else 2,
            "maxChildOccupancy": obj.get("maxChildOccupancy") if obj.get("maxChildOccupancy") is not None else 0,
            "includedAdultOccupancy": obj.get("includedAdultOccupancy") if obj.get("includedAdultOccupancy") is not None else 2,
            "includedChildOccupancy": obj.get("includedChildOccupancy") if obj.get("includedChildOccupancy") is not None else 0,
            "sourceToUserCurrencyQuote": QuoteLightweightSupplierDetails.from_dict(obj["sourceToUserCurrencyQuote"]) if obj.get("sourceToUserCurrencyQuote") is not None else None,
            "sourceToInternalCurrencyQuote": QuoteLightweightSupplierDetails.from_dict(obj["sourceToInternalCurrencyQuote"]) if obj.get("sourceToInternalCurrencyQuote") is not None else None,
            "phantom": obj.get("phantom"),
            "startDate": obj.get("startDate"),
            "betweenDate": obj.get("betweenDate"),
            "lastNight": obj.get("lastNight"),
            "bundledModifier": obj.get("bundledModifier"),
            "closeOnDeparture": obj.get("closeOnDeparture"),
            "inventoryAvailable": obj.get("inventoryAvailable"),
            "masterAvailability": obj.get("masterAvailability"),
            "closeOnArrival": obj.get("closeOnArrival"),
            "rateIdentifier": obj.get("rateIdentifier"),
            "date": obj.get("date"),
            "source": obj.get("source"),
            "quantity": obj.get("quantity"),
            "sourceRate": CustomMonetaryAmount.from_dict(obj["sourceRate"]) if obj.get("sourceRate") is not None else None,
            "userSpecifiedCurrencyRate": CustomMonetaryAmount.from_dict(obj["userSpecifiedCurrencyRate"]) if obj.get("userSpecifiedCurrencyRate") is not None else None,
            "internalRate": CustomMonetaryAmount.from_dict(obj["internalRate"]) if obj.get("internalRate") is not None else None,
            "endDate": obj.get("endDate"),
            "maxOccupancy": obj.get("maxOccupancy"),
            "minOccupancy": obj.get("minOccupancy"),
            "baseRate": CustomMonetaryAmount.from_dict(obj["baseRate"]) if obj.get("baseRate") is not None else None,
            "minLOS": obj.get("minLOS"),
            "maxLOS": obj.get("maxLOS"),
            "totalDiscountPercent": obj.get("totalDiscountPercent")
        })
        return _obj


