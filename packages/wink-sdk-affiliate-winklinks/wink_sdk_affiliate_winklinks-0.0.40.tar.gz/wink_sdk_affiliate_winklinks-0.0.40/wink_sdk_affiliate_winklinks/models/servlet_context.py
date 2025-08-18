# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reactive): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant reactive widget for all other entities.   - [TripPay](/reactive): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # WinkLinks API The WinkLinks API exposes endpoints to manage WinkLink entries, categories and settings. This API lets you:  1. Entries: Manage WinkLinks entries. 2. Categories: Manage WinkLinks tags. 2. Settings: Configure WinkLinks account.  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.17.5
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from wink_sdk_affiliate_winklinks.models.application_context_class_loader_parent import ApplicationContextClassLoaderParent
from wink_sdk_affiliate_winklinks.models.filter_registration import FilterRegistration
from wink_sdk_affiliate_winklinks.models.jsp_config_descriptor import JspConfigDescriptor
from wink_sdk_affiliate_winklinks.models.servlet_registration import ServletRegistration
from wink_sdk_affiliate_winklinks.models.session_cookie_config import SessionCookieConfig
from typing import Optional, Set
from typing_extensions import Self

class ServletContext(BaseModel):
    """
    ServletContext
    """ # noqa: E501
    class_loader: Optional[ApplicationContextClassLoaderParent] = Field(default=None, alias="classLoader")
    major_version: Optional[StrictInt] = Field(default=None, alias="majorVersion")
    minor_version: Optional[StrictInt] = Field(default=None, alias="minorVersion")
    session_tracking_modes: Optional[List[StrictStr]] = Field(default=None, alias="sessionTrackingModes")
    init_parameter_names: Optional[Any] = Field(default=None, alias="initParameterNames")
    attribute_names: Optional[Any] = Field(default=None, alias="attributeNames")
    context_path: Optional[StrictStr] = Field(default=None, alias="contextPath")
    servlet_context_name: Optional[StrictStr] = Field(default=None, alias="servletContextName")
    effective_major_version: Optional[StrictInt] = Field(default=None, alias="effectiveMajorVersion")
    effective_minor_version: Optional[StrictInt] = Field(default=None, alias="effectiveMinorVersion")
    server_info: Optional[StrictStr] = Field(default=None, alias="serverInfo")
    session_cookie_config: Optional[SessionCookieConfig] = Field(default=None, alias="sessionCookieConfig")
    session_timeout: Optional[StrictInt] = Field(default=None, alias="sessionTimeout")
    servlet_registrations: Optional[Dict[str, ServletRegistration]] = Field(default=None, alias="servletRegistrations")
    default_session_tracking_modes: Optional[List[StrictStr]] = Field(default=None, alias="defaultSessionTrackingModes")
    filter_registrations: Optional[Dict[str, FilterRegistration]] = Field(default=None, alias="filterRegistrations")
    effective_session_tracking_modes: Optional[List[StrictStr]] = Field(default=None, alias="effectiveSessionTrackingModes")
    jsp_config_descriptor: Optional[JspConfigDescriptor] = Field(default=None, alias="jspConfigDescriptor")
    virtual_server_name: Optional[StrictStr] = Field(default=None, alias="virtualServerName")
    request_character_encoding: Optional[StrictStr] = Field(default=None, alias="requestCharacterEncoding")
    response_character_encoding: Optional[StrictStr] = Field(default=None, alias="responseCharacterEncoding")
    __properties: ClassVar[List[str]] = ["classLoader", "majorVersion", "minorVersion", "sessionTrackingModes", "initParameterNames", "attributeNames", "contextPath", "servletContextName", "effectiveMajorVersion", "effectiveMinorVersion", "serverInfo", "sessionCookieConfig", "sessionTimeout", "servletRegistrations", "defaultSessionTrackingModes", "filterRegistrations", "effectiveSessionTrackingModes", "jspConfigDescriptor", "virtualServerName", "requestCharacterEncoding", "responseCharacterEncoding"]

    @field_validator('session_tracking_modes')
    def session_tracking_modes_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        for i in value:
            if i not in set(['COOKIE', 'URL', 'SSL']):
                raise ValueError("each list item must be one of ('COOKIE', 'URL', 'SSL')")
        return value

    @field_validator('default_session_tracking_modes')
    def default_session_tracking_modes_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        for i in value:
            if i not in set(['COOKIE', 'URL', 'SSL']):
                raise ValueError("each list item must be one of ('COOKIE', 'URL', 'SSL')")
        return value

    @field_validator('effective_session_tracking_modes')
    def effective_session_tracking_modes_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        for i in value:
            if i not in set(['COOKIE', 'URL', 'SSL']):
                raise ValueError("each list item must be one of ('COOKIE', 'URL', 'SSL')")
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
        """Create an instance of ServletContext from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of class_loader
        if self.class_loader:
            _dict['classLoader'] = self.class_loader.to_dict()
        # override the default output from pydantic by calling `to_dict()` of session_cookie_config
        if self.session_cookie_config:
            _dict['sessionCookieConfig'] = self.session_cookie_config.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each value in servlet_registrations (dict)
        _field_dict = {}
        if self.servlet_registrations:
            for _key_servlet_registrations in self.servlet_registrations:
                if self.servlet_registrations[_key_servlet_registrations]:
                    _field_dict[_key_servlet_registrations] = self.servlet_registrations[_key_servlet_registrations].to_dict()
            _dict['servletRegistrations'] = _field_dict
        # override the default output from pydantic by calling `to_dict()` of each value in filter_registrations (dict)
        _field_dict = {}
        if self.filter_registrations:
            for _key_filter_registrations in self.filter_registrations:
                if self.filter_registrations[_key_filter_registrations]:
                    _field_dict[_key_filter_registrations] = self.filter_registrations[_key_filter_registrations].to_dict()
            _dict['filterRegistrations'] = _field_dict
        # override the default output from pydantic by calling `to_dict()` of jsp_config_descriptor
        if self.jsp_config_descriptor:
            _dict['jspConfigDescriptor'] = self.jsp_config_descriptor.to_dict()
        # set to None if init_parameter_names (nullable) is None
        # and model_fields_set contains the field
        if self.init_parameter_names is None and "init_parameter_names" in self.model_fields_set:
            _dict['initParameterNames'] = None

        # set to None if attribute_names (nullable) is None
        # and model_fields_set contains the field
        if self.attribute_names is None and "attribute_names" in self.model_fields_set:
            _dict['attributeNames'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ServletContext from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "classLoader": ApplicationContextClassLoaderParent.from_dict(obj["classLoader"]) if obj.get("classLoader") is not None else None,
            "majorVersion": obj.get("majorVersion"),
            "minorVersion": obj.get("minorVersion"),
            "sessionTrackingModes": obj.get("sessionTrackingModes"),
            "initParameterNames": obj.get("initParameterNames"),
            "attributeNames": obj.get("attributeNames"),
            "contextPath": obj.get("contextPath"),
            "servletContextName": obj.get("servletContextName"),
            "effectiveMajorVersion": obj.get("effectiveMajorVersion"),
            "effectiveMinorVersion": obj.get("effectiveMinorVersion"),
            "serverInfo": obj.get("serverInfo"),
            "sessionCookieConfig": SessionCookieConfig.from_dict(obj["sessionCookieConfig"]) if obj.get("sessionCookieConfig") is not None else None,
            "sessionTimeout": obj.get("sessionTimeout"),
            "servletRegistrations": dict(
                (_k, ServletRegistration.from_dict(_v))
                for _k, _v in obj["servletRegistrations"].items()
            )
            if obj.get("servletRegistrations") is not None
            else None,
            "defaultSessionTrackingModes": obj.get("defaultSessionTrackingModes"),
            "filterRegistrations": dict(
                (_k, FilterRegistration.from_dict(_v))
                for _k, _v in obj["filterRegistrations"].items()
            )
            if obj.get("filterRegistrations") is not None
            else None,
            "effectiveSessionTrackingModes": obj.get("effectiveSessionTrackingModes"),
            "jspConfigDescriptor": JspConfigDescriptor.from_dict(obj["jspConfigDescriptor"]) if obj.get("jspConfigDescriptor") is not None else None,
            "virtualServerName": obj.get("virtualServerName"),
            "requestCharacterEncoding": obj.get("requestCharacterEncoding"),
            "responseCharacterEncoding": obj.get("responseCharacterEncoding")
        })
        return _obj


