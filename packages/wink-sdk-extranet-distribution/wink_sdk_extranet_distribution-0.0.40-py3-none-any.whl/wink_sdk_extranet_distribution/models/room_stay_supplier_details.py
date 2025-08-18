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
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from wink_sdk_extranet_distribution.models.bedroom_configuration_supplier_details import BedroomConfigurationSupplierDetails
from wink_sdk_extranet_distribution.models.cancellation_policy_lightweight_supplier_details import CancellationPolicyLightweightSupplierDetails
from wink_sdk_extranet_distribution.models.custom_monetary_amount import CustomMonetaryAmount
from wink_sdk_extranet_distribution.models.extra_charges_supplier_details import ExtraChargesSupplierDetails
from wink_sdk_extranet_distribution.models.guest_room_lightweight_supplier_details import GuestRoomLightweightSupplierDetails
from wink_sdk_extranet_distribution.models.perk_lightweight_supplier_details import PerkLightweightSupplierDetails
from wink_sdk_extranet_distribution.models.property_policy_supplier_details import PropertyPolicySupplierDetails
from wink_sdk_extranet_distribution.models.room_configuration_price_rate_plan_supplier_details import RoomConfigurationPriceRatePlanSupplierDetails
from wink_sdk_extranet_distribution.models.stay_rate_supplier_details import StayRateSupplierDetails
from typing import Optional, Set
from typing_extensions import Self

class RoomStaySupplierDetails(BaseModel):
    """
    RoomStaySupplierDetails
    """ # noqa: E501
    policy: PropertyPolicySupplierDetails = Field(description="Property policy information.")
    room: GuestRoomLightweightSupplierDetails = Field(description="Guest room details.")
    rooms: StrictInt = Field(description="Number of rooms. Always 1 since we switched to creating one booking per room.")
    bedroom_configuration: BedroomConfigurationSupplierDetails = Field(description="Desired bedroom layout", alias="bedroomConfiguration")
    adults: StrictInt = Field(description="The actual amount of adults as determined by the hotel's policy.")
    children: StrictInt = Field(description="The actual amount of children as determined by the hotel's policy.")
    start_date: date = Field(description="Stay start date", alias="startDate")
    end_date: date = Field(description="Stay end date", alias="endDate")
    price: StayRateSupplierDetails = Field(description="Price details")
    room_rate_identifier: Annotated[str, Field(min_length=1, strict=True)] = Field(description="Master rate identifier", alias="roomRateIdentifier")
    room_rate_internal_name: Annotated[str, Field(min_length=1, strict=True)] = Field(description="Master rate internal name", alias="roomRateInternalName")
    rate_plan: RoomConfigurationPriceRatePlanSupplierDetails = Field(description="Rate plan used for this stay", alias="ratePlan")
    perk_types: Optional[List[PerkLightweightSupplierDetails]] = Field(default=None, description="List of perks that came with the master rate", alias="perkTypes")
    extra_charges: ExtraChargesSupplierDetails = Field(description="Rate plan-level extra charges", alias="extraCharges")
    active_cancellation_policy: CancellationPolicyLightweightSupplierDetails = Field(description="Based on the itinerary, the cancellation policy could be taken directly from the rate plan or it could be a policy exception also listed on the rate plan", alias="activeCancellationPolicy")
    cancellable_by_hotel: Optional[StrictBool] = Field(default=None, alias="cancellableByHotel")
    cancellable_with_potential_charge: Optional[StrictBool] = Field(default=None, alias="cancellableWithPotentialCharge")
    room_nights: Optional[StrictInt] = Field(default=None, description="Total number of nights the guest stays at the hotel. -1 indicates there is an error.", alias="roomNights")
    guests: Optional[StrictInt] = None
    rate_source: Optional[StrictStr] = Field(default=None, alias="rateSource")
    source_total: Optional[CustomMonetaryAmount] = Field(default=None, alias="sourceTotal")
    user_specified_currency_total: Optional[CustomMonetaryAmount] = Field(default=None, alias="userSpecifiedCurrencyTotal")
    internal_total: Optional[CustomMonetaryAmount] = Field(default=None, alias="internalTotal")
    cancellable: Optional[StrictBool] = None
    __properties: ClassVar[List[str]] = ["policy", "room", "rooms", "bedroomConfiguration", "adults", "children", "startDate", "endDate", "price", "roomRateIdentifier", "roomRateInternalName", "ratePlan", "perkTypes", "extraCharges", "activeCancellationPolicy", "cancellableByHotel", "cancellableWithPotentialCharge", "roomNights", "guests", "rateSource", "sourceTotal", "userSpecifiedCurrencyTotal", "internalTotal", "cancellable"]

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
        """Create an instance of RoomStaySupplierDetails from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of policy
        if self.policy:
            _dict['policy'] = self.policy.to_dict()
        # override the default output from pydantic by calling `to_dict()` of room
        if self.room:
            _dict['room'] = self.room.to_dict()
        # override the default output from pydantic by calling `to_dict()` of bedroom_configuration
        if self.bedroom_configuration:
            _dict['bedroomConfiguration'] = self.bedroom_configuration.to_dict()
        # override the default output from pydantic by calling `to_dict()` of price
        if self.price:
            _dict['price'] = self.price.to_dict()
        # override the default output from pydantic by calling `to_dict()` of rate_plan
        if self.rate_plan:
            _dict['ratePlan'] = self.rate_plan.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in perk_types (list)
        _items = []
        if self.perk_types:
            for _item_perk_types in self.perk_types:
                if _item_perk_types:
                    _items.append(_item_perk_types.to_dict())
            _dict['perkTypes'] = _items
        # override the default output from pydantic by calling `to_dict()` of extra_charges
        if self.extra_charges:
            _dict['extraCharges'] = self.extra_charges.to_dict()
        # override the default output from pydantic by calling `to_dict()` of active_cancellation_policy
        if self.active_cancellation_policy:
            _dict['activeCancellationPolicy'] = self.active_cancellation_policy.to_dict()
        # override the default output from pydantic by calling `to_dict()` of source_total
        if self.source_total:
            _dict['sourceTotal'] = self.source_total.to_dict()
        # override the default output from pydantic by calling `to_dict()` of user_specified_currency_total
        if self.user_specified_currency_total:
            _dict['userSpecifiedCurrencyTotal'] = self.user_specified_currency_total.to_dict()
        # override the default output from pydantic by calling `to_dict()` of internal_total
        if self.internal_total:
            _dict['internalTotal'] = self.internal_total.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of RoomStaySupplierDetails from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "policy": PropertyPolicySupplierDetails.from_dict(obj["policy"]) if obj.get("policy") is not None else None,
            "room": GuestRoomLightweightSupplierDetails.from_dict(obj["room"]) if obj.get("room") is not None else None,
            "rooms": obj.get("rooms") if obj.get("rooms") is not None else 1,
            "bedroomConfiguration": BedroomConfigurationSupplierDetails.from_dict(obj["bedroomConfiguration"]) if obj.get("bedroomConfiguration") is not None else None,
            "adults": obj.get("adults") if obj.get("adults") is not None else 2,
            "children": obj.get("children") if obj.get("children") is not None else 0,
            "startDate": obj.get("startDate"),
            "endDate": obj.get("endDate"),
            "price": StayRateSupplierDetails.from_dict(obj["price"]) if obj.get("price") is not None else None,
            "roomRateIdentifier": obj.get("roomRateIdentifier"),
            "roomRateInternalName": obj.get("roomRateInternalName"),
            "ratePlan": RoomConfigurationPriceRatePlanSupplierDetails.from_dict(obj["ratePlan"]) if obj.get("ratePlan") is not None else None,
            "perkTypes": [PerkLightweightSupplierDetails.from_dict(_item) for _item in obj["perkTypes"]] if obj.get("perkTypes") is not None else None,
            "extraCharges": ExtraChargesSupplierDetails.from_dict(obj["extraCharges"]) if obj.get("extraCharges") is not None else None,
            "activeCancellationPolicy": CancellationPolicyLightweightSupplierDetails.from_dict(obj["activeCancellationPolicy"]) if obj.get("activeCancellationPolicy") is not None else None,
            "cancellableByHotel": obj.get("cancellableByHotel"),
            "cancellableWithPotentialCharge": obj.get("cancellableWithPotentialCharge"),
            "roomNights": obj.get("roomNights"),
            "guests": obj.get("guests"),
            "rateSource": obj.get("rateSource"),
            "sourceTotal": CustomMonetaryAmount.from_dict(obj["sourceTotal"]) if obj.get("sourceTotal") is not None else None,
            "userSpecifiedCurrencyTotal": CustomMonetaryAmount.from_dict(obj["userSpecifiedCurrencyTotal"]) if obj.get("userSpecifiedCurrencyTotal") is not None else None,
            "internalTotal": CustomMonetaryAmount.from_dict(obj["internalTotal"]) if obj.get("internalTotal") is not None else None,
            "cancellable": obj.get("cancellable")
        })
        return _obj


