# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Extranet Property API This part of the documentation concerns itself with basic property management. It can:  1. Property: List existing properties. Manage property status. Change name and similar. 2. Notification: Read internal messages sent from Wink to your properties. 3. Announcement: Show pertinent messages to travelers in a pop-up window. 4. Geo-location: Set property geo-location. 5. Green Index: Answer eco-related questions regarding the property's recycling practices and much more. 6. Lifestyles: Manage lifestyles the property caters to. 7. Photos / Videos: Manage property media. 8. Policy: Manage property policy. I.e. Children, pets, wi-fi, parking etc. 9. Reputation: Manage awards, online / offline ratings etc. 10. Services: Manage property amenities. 11. Social media: Manage property social media networks. 12. Welcome text: Manage property descriptions  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.18.5
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501

import warnings
from pydantic import validate_call, Field, StrictFloat, StrictStr, StrictInt
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated

from pydantic import Field, StrictStr, field_validator
from typing import List, Optional
from typing_extensions import Annotated
from wink_sdk_extranet_property.models.property_supplier import PropertySupplier
from wink_sdk_extranet_property.models.travel_inventory_recognition_supplier import TravelInventoryRecognitionSupplier
from wink_sdk_extranet_property.models.upsert_recognition_supplier import UpsertRecognitionSupplier

from wink_sdk_extranet_property.api_client import ApiClient, RequestSerialized
from wink_sdk_extranet_property.api_response import ApiResponse
from wink_sdk_extranet_property.rest import RESTResponseType


class RecognitionApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def create_recognition(
        self,
        property_identifier: Annotated[StrictStr, Field(description="Associate new request record with this property identifier")],
        upsert_recognition_supplier: UpsertRecognitionSupplier,
        wink_version: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> PropertySupplier:
        """Create Recognition

        Create a new request

        :param property_identifier: Associate new request record with this property identifier (required)
        :type property_identifier: str
        :param upsert_recognition_supplier: (required)
        :type upsert_recognition_supplier: UpsertRecognitionSupplier
        :param wink_version:
        :type wink_version: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._create_recognition_serialize(
            property_identifier=property_identifier,
            upsert_recognition_supplier=upsert_recognition_supplier,
            wink_version=wink_version,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '500': "object",
            '403': "GenericErrorMessage",
            '401': "GenericErrorMessage",
            '400': "ShowRecognition400Response",
            '201': "PropertySupplier",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def create_recognition_with_http_info(
        self,
        property_identifier: Annotated[StrictStr, Field(description="Associate new request record with this property identifier")],
        upsert_recognition_supplier: UpsertRecognitionSupplier,
        wink_version: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[PropertySupplier]:
        """Create Recognition

        Create a new request

        :param property_identifier: Associate new request record with this property identifier (required)
        :type property_identifier: str
        :param upsert_recognition_supplier: (required)
        :type upsert_recognition_supplier: UpsertRecognitionSupplier
        :param wink_version:
        :type wink_version: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._create_recognition_serialize(
            property_identifier=property_identifier,
            upsert_recognition_supplier=upsert_recognition_supplier,
            wink_version=wink_version,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '500': "object",
            '403': "GenericErrorMessage",
            '401': "GenericErrorMessage",
            '400': "ShowRecognition400Response",
            '201': "PropertySupplier",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def create_recognition_without_preload_content(
        self,
        property_identifier: Annotated[StrictStr, Field(description="Associate new request record with this property identifier")],
        upsert_recognition_supplier: UpsertRecognitionSupplier,
        wink_version: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Create Recognition

        Create a new request

        :param property_identifier: Associate new request record with this property identifier (required)
        :type property_identifier: str
        :param upsert_recognition_supplier: (required)
        :type upsert_recognition_supplier: UpsertRecognitionSupplier
        :param wink_version:
        :type wink_version: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._create_recognition_serialize(
            property_identifier=property_identifier,
            upsert_recognition_supplier=upsert_recognition_supplier,
            wink_version=wink_version,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '500': "object",
            '403': "GenericErrorMessage",
            '401': "GenericErrorMessage",
            '400': "ShowRecognition400Response",
            '201': "PropertySupplier",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _create_recognition_serialize(
        self,
        property_identifier,
        upsert_recognition_supplier,
        wink_version,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if property_identifier is not None:
            _path_params['propertyIdentifier'] = property_identifier
        # process the query parameters
        # process the header parameters
        if wink_version is not None:
            _header_params['Wink-Version'] = wink_version
        # process the form parameters
        # process the body parameter
        if upsert_recognition_supplier is not None:
            _body_params = upsert_recognition_supplier


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json', 
                    'application/xml', 
                    'text/xml', 
                    'text/html', 
                    'text/plain', 
                    '*/*'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'oauth2ClientCredentials'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/api/property/{propertyIdentifier}/recognition',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def remove_recognition(
        self,
        property_identifier: Annotated[StrictStr, Field(description="Delete recognition record for property with this property identifier")],
        recognition_identifier: Annotated[StrictStr, Field(description="Delete recognition with this identifier")],
        wink_version: Optional[StrictStr] = None,
        accept: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> PropertySupplier:
        """Delete Recognition

        Delete a recognition by its identifier

        :param property_identifier: Delete recognition record for property with this property identifier (required)
        :type property_identifier: str
        :param recognition_identifier: Delete recognition with this identifier (required)
        :type recognition_identifier: str
        :param wink_version:
        :type wink_version: str
        :param accept:
        :type accept: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._remove_recognition_serialize(
            property_identifier=property_identifier,
            recognition_identifier=recognition_identifier,
            wink_version=wink_version,
            accept=accept,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '500': "object",
            '403': "GenericErrorMessage",
            '401': "GenericErrorMessage",
            '400': "ShowRecognition400Response",
            '200': "PropertySupplier",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def remove_recognition_with_http_info(
        self,
        property_identifier: Annotated[StrictStr, Field(description="Delete recognition record for property with this property identifier")],
        recognition_identifier: Annotated[StrictStr, Field(description="Delete recognition with this identifier")],
        wink_version: Optional[StrictStr] = None,
        accept: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[PropertySupplier]:
        """Delete Recognition

        Delete a recognition by its identifier

        :param property_identifier: Delete recognition record for property with this property identifier (required)
        :type property_identifier: str
        :param recognition_identifier: Delete recognition with this identifier (required)
        :type recognition_identifier: str
        :param wink_version:
        :type wink_version: str
        :param accept:
        :type accept: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._remove_recognition_serialize(
            property_identifier=property_identifier,
            recognition_identifier=recognition_identifier,
            wink_version=wink_version,
            accept=accept,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '500': "object",
            '403': "GenericErrorMessage",
            '401': "GenericErrorMessage",
            '400': "ShowRecognition400Response",
            '200': "PropertySupplier",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def remove_recognition_without_preload_content(
        self,
        property_identifier: Annotated[StrictStr, Field(description="Delete recognition record for property with this property identifier")],
        recognition_identifier: Annotated[StrictStr, Field(description="Delete recognition with this identifier")],
        wink_version: Optional[StrictStr] = None,
        accept: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Delete Recognition

        Delete a recognition by its identifier

        :param property_identifier: Delete recognition record for property with this property identifier (required)
        :type property_identifier: str
        :param recognition_identifier: Delete recognition with this identifier (required)
        :type recognition_identifier: str
        :param wink_version:
        :type wink_version: str
        :param accept:
        :type accept: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._remove_recognition_serialize(
            property_identifier=property_identifier,
            recognition_identifier=recognition_identifier,
            wink_version=wink_version,
            accept=accept,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '500': "object",
            '403': "GenericErrorMessage",
            '401': "GenericErrorMessage",
            '400': "ShowRecognition400Response",
            '200': "PropertySupplier",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _remove_recognition_serialize(
        self,
        property_identifier,
        recognition_identifier,
        wink_version,
        accept,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if property_identifier is not None:
            _path_params['propertyIdentifier'] = property_identifier
        if recognition_identifier is not None:
            _path_params['recognitionIdentifier'] = recognition_identifier
        # process the query parameters
        # process the header parameters
        if wink_version is not None:
            _header_params['Wink-Version'] = wink_version
        if accept is not None:
            _header_params['Accept'] = accept
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json', 
                    'application/xml', 
                    'text/xml', 
                    'text/html', 
                    'text/plain', 
                    '*/*'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'oauth2ClientCredentials'
        ]

        return self.api_client.param_serialize(
            method='DELETE',
            resource_path='/api/property/{propertyIdentifier}/recognition/{recognitionIdentifier}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def show_recognition(
        self,
        property_identifier: Annotated[StrictStr, Field(description="Show recognition belonging to this property identifier")],
        recognition_identifier: Annotated[StrictStr, Field(description="Show recognition associated with this identifier")],
        wink_version: Optional[StrictStr] = None,
        accept: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> TravelInventoryRecognitionSupplier:
        """Show Recognition

        Retrieve a recognition by its identifier

        :param property_identifier: Show recognition belonging to this property identifier (required)
        :type property_identifier: str
        :param recognition_identifier: Show recognition associated with this identifier (required)
        :type recognition_identifier: str
        :param wink_version:
        :type wink_version: str
        :param accept:
        :type accept: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._show_recognition_serialize(
            property_identifier=property_identifier,
            recognition_identifier=recognition_identifier,
            wink_version=wink_version,
            accept=accept,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '500': "object",
            '403': "GenericErrorMessage",
            '401': "GenericErrorMessage",
            '400': "ShowRecognition400Response",
            '200': "TravelInventoryRecognitionSupplier",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def show_recognition_with_http_info(
        self,
        property_identifier: Annotated[StrictStr, Field(description="Show recognition belonging to this property identifier")],
        recognition_identifier: Annotated[StrictStr, Field(description="Show recognition associated with this identifier")],
        wink_version: Optional[StrictStr] = None,
        accept: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[TravelInventoryRecognitionSupplier]:
        """Show Recognition

        Retrieve a recognition by its identifier

        :param property_identifier: Show recognition belonging to this property identifier (required)
        :type property_identifier: str
        :param recognition_identifier: Show recognition associated with this identifier (required)
        :type recognition_identifier: str
        :param wink_version:
        :type wink_version: str
        :param accept:
        :type accept: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._show_recognition_serialize(
            property_identifier=property_identifier,
            recognition_identifier=recognition_identifier,
            wink_version=wink_version,
            accept=accept,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '500': "object",
            '403': "GenericErrorMessage",
            '401': "GenericErrorMessage",
            '400': "ShowRecognition400Response",
            '200': "TravelInventoryRecognitionSupplier",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def show_recognition_without_preload_content(
        self,
        property_identifier: Annotated[StrictStr, Field(description="Show recognition belonging to this property identifier")],
        recognition_identifier: Annotated[StrictStr, Field(description="Show recognition associated with this identifier")],
        wink_version: Optional[StrictStr] = None,
        accept: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Show Recognition

        Retrieve a recognition by its identifier

        :param property_identifier: Show recognition belonging to this property identifier (required)
        :type property_identifier: str
        :param recognition_identifier: Show recognition associated with this identifier (required)
        :type recognition_identifier: str
        :param wink_version:
        :type wink_version: str
        :param accept:
        :type accept: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._show_recognition_serialize(
            property_identifier=property_identifier,
            recognition_identifier=recognition_identifier,
            wink_version=wink_version,
            accept=accept,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '500': "object",
            '403': "GenericErrorMessage",
            '401': "GenericErrorMessage",
            '400': "ShowRecognition400Response",
            '200': "TravelInventoryRecognitionSupplier",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _show_recognition_serialize(
        self,
        property_identifier,
        recognition_identifier,
        wink_version,
        accept,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if property_identifier is not None:
            _path_params['propertyIdentifier'] = property_identifier
        if recognition_identifier is not None:
            _path_params['recognitionIdentifier'] = recognition_identifier
        # process the query parameters
        # process the header parameters
        if wink_version is not None:
            _header_params['Wink-Version'] = wink_version
        if accept is not None:
            _header_params['Accept'] = accept
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json', 
                    'application/xml', 
                    'text/xml', 
                    'text/html', 
                    'text/plain', 
                    '*/*'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'oauth2ClientCredentials'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/api/property/{propertyIdentifier}/recognition/{recognitionIdentifier}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def show_recognitions(
        self,
        property_identifier: Annotated[StrictStr, Field(description="Show list of recognitions for this property identifier")],
        wink_version: Optional[StrictStr] = None,
        accept: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> List[TravelInventoryRecognitionSupplier]:
        """Show Recognitions

        Retrieve a list of all recognitions for property

        :param property_identifier: Show list of recognitions for this property identifier (required)
        :type property_identifier: str
        :param wink_version:
        :type wink_version: str
        :param accept:
        :type accept: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._show_recognitions_serialize(
            property_identifier=property_identifier,
            wink_version=wink_version,
            accept=accept,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '500': "object",
            '403': "GenericErrorMessage",
            '401': "GenericErrorMessage",
            '400': "ShowRecognition400Response",
            '200': "List[TravelInventoryRecognitionSupplier]",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def show_recognitions_with_http_info(
        self,
        property_identifier: Annotated[StrictStr, Field(description="Show list of recognitions for this property identifier")],
        wink_version: Optional[StrictStr] = None,
        accept: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[List[TravelInventoryRecognitionSupplier]]:
        """Show Recognitions

        Retrieve a list of all recognitions for property

        :param property_identifier: Show list of recognitions for this property identifier (required)
        :type property_identifier: str
        :param wink_version:
        :type wink_version: str
        :param accept:
        :type accept: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._show_recognitions_serialize(
            property_identifier=property_identifier,
            wink_version=wink_version,
            accept=accept,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '500': "object",
            '403': "GenericErrorMessage",
            '401': "GenericErrorMessage",
            '400': "ShowRecognition400Response",
            '200': "List[TravelInventoryRecognitionSupplier]",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def show_recognitions_without_preload_content(
        self,
        property_identifier: Annotated[StrictStr, Field(description="Show list of recognitions for this property identifier")],
        wink_version: Optional[StrictStr] = None,
        accept: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Show Recognitions

        Retrieve a list of all recognitions for property

        :param property_identifier: Show list of recognitions for this property identifier (required)
        :type property_identifier: str
        :param wink_version:
        :type wink_version: str
        :param accept:
        :type accept: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._show_recognitions_serialize(
            property_identifier=property_identifier,
            wink_version=wink_version,
            accept=accept,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '500': "object",
            '403': "GenericErrorMessage",
            '401': "GenericErrorMessage",
            '400': "ShowRecognition400Response",
            '200': "List[TravelInventoryRecognitionSupplier]",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _show_recognitions_serialize(
        self,
        property_identifier,
        wink_version,
        accept,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if property_identifier is not None:
            _path_params['propertyIdentifier'] = property_identifier
        # process the query parameters
        # process the header parameters
        if wink_version is not None:
            _header_params['Wink-Version'] = wink_version
        if accept is not None:
            _header_params['Accept'] = accept
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json', 
                    'application/xml', 
                    'text/xml', 
                    'text/html', 
                    'text/plain', 
                    '*/*'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'oauth2ClientCredentials'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/api/property/{propertyIdentifier}/recognition/list',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def show_recognitions_by_category(
        self,
        property_identifier: Annotated[StrictStr, Field(description="Show list of recognitions for this property identifier")],
        category: Annotated[StrictStr, Field(description="Filter list of recognitions by category")],
        wink_version: Optional[StrictStr] = None,
        accept: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> List[TravelInventoryRecognitionSupplier]:
        """Show Recognition by Category

        Retrieve list recognitions by category

        :param property_identifier: Show list of recognitions for this property identifier (required)
        :type property_identifier: str
        :param category: Filter list of recognitions by category (required)
        :type category: str
        :param wink_version:
        :type wink_version: str
        :param accept:
        :type accept: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._show_recognitions_by_category_serialize(
            property_identifier=property_identifier,
            category=category,
            wink_version=wink_version,
            accept=accept,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '500': "object",
            '403': "GenericErrorMessage",
            '401': "GenericErrorMessage",
            '400': "ShowRecognition400Response",
            '200': "List[TravelInventoryRecognitionSupplier]",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def show_recognitions_by_category_with_http_info(
        self,
        property_identifier: Annotated[StrictStr, Field(description="Show list of recognitions for this property identifier")],
        category: Annotated[StrictStr, Field(description="Filter list of recognitions by category")],
        wink_version: Optional[StrictStr] = None,
        accept: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[List[TravelInventoryRecognitionSupplier]]:
        """Show Recognition by Category

        Retrieve list recognitions by category

        :param property_identifier: Show list of recognitions for this property identifier (required)
        :type property_identifier: str
        :param category: Filter list of recognitions by category (required)
        :type category: str
        :param wink_version:
        :type wink_version: str
        :param accept:
        :type accept: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._show_recognitions_by_category_serialize(
            property_identifier=property_identifier,
            category=category,
            wink_version=wink_version,
            accept=accept,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '500': "object",
            '403': "GenericErrorMessage",
            '401': "GenericErrorMessage",
            '400': "ShowRecognition400Response",
            '200': "List[TravelInventoryRecognitionSupplier]",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def show_recognitions_by_category_without_preload_content(
        self,
        property_identifier: Annotated[StrictStr, Field(description="Show list of recognitions for this property identifier")],
        category: Annotated[StrictStr, Field(description="Filter list of recognitions by category")],
        wink_version: Optional[StrictStr] = None,
        accept: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Show Recognition by Category

        Retrieve list recognitions by category

        :param property_identifier: Show list of recognitions for this property identifier (required)
        :type property_identifier: str
        :param category: Filter list of recognitions by category (required)
        :type category: str
        :param wink_version:
        :type wink_version: str
        :param accept:
        :type accept: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._show_recognitions_by_category_serialize(
            property_identifier=property_identifier,
            category=category,
            wink_version=wink_version,
            accept=accept,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '500': "object",
            '403': "GenericErrorMessage",
            '401': "GenericErrorMessage",
            '400': "ShowRecognition400Response",
            '200': "List[TravelInventoryRecognitionSupplier]",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _show_recognitions_by_category_serialize(
        self,
        property_identifier,
        category,
        wink_version,
        accept,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if property_identifier is not None:
            _path_params['propertyIdentifier'] = property_identifier
        if category is not None:
            _path_params['category'] = category
        # process the query parameters
        # process the header parameters
        if wink_version is not None:
            _header_params['Wink-Version'] = wink_version
        if accept is not None:
            _header_params['Accept'] = accept
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json', 
                    'application/xml', 
                    'text/xml', 
                    'text/html', 
                    'text/plain', 
                    '*/*'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'oauth2ClientCredentials'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/api/property/{propertyIdentifier}/recognition/{category}/list',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def update_recognition(
        self,
        property_identifier: Annotated[StrictStr, Field(description="Update recognition record associated with this property identifier")],
        recognition_identifier: Annotated[StrictStr, Field(description="Update recognition with this identifier")],
        upsert_recognition_supplier: UpsertRecognitionSupplier,
        wink_version: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> PropertySupplier:
        """Update Recognition

        Update a recognition by its identifier

        :param property_identifier: Update recognition record associated with this property identifier (required)
        :type property_identifier: str
        :param recognition_identifier: Update recognition with this identifier (required)
        :type recognition_identifier: str
        :param upsert_recognition_supplier: (required)
        :type upsert_recognition_supplier: UpsertRecognitionSupplier
        :param wink_version:
        :type wink_version: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_recognition_serialize(
            property_identifier=property_identifier,
            recognition_identifier=recognition_identifier,
            upsert_recognition_supplier=upsert_recognition_supplier,
            wink_version=wink_version,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '500': "object",
            '403': "GenericErrorMessage",
            '401': "GenericErrorMessage",
            '400': "ShowRecognition400Response",
            '200': "PropertySupplier",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def update_recognition_with_http_info(
        self,
        property_identifier: Annotated[StrictStr, Field(description="Update recognition record associated with this property identifier")],
        recognition_identifier: Annotated[StrictStr, Field(description="Update recognition with this identifier")],
        upsert_recognition_supplier: UpsertRecognitionSupplier,
        wink_version: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[PropertySupplier]:
        """Update Recognition

        Update a recognition by its identifier

        :param property_identifier: Update recognition record associated with this property identifier (required)
        :type property_identifier: str
        :param recognition_identifier: Update recognition with this identifier (required)
        :type recognition_identifier: str
        :param upsert_recognition_supplier: (required)
        :type upsert_recognition_supplier: UpsertRecognitionSupplier
        :param wink_version:
        :type wink_version: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_recognition_serialize(
            property_identifier=property_identifier,
            recognition_identifier=recognition_identifier,
            upsert_recognition_supplier=upsert_recognition_supplier,
            wink_version=wink_version,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '500': "object",
            '403': "GenericErrorMessage",
            '401': "GenericErrorMessage",
            '400': "ShowRecognition400Response",
            '200': "PropertySupplier",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def update_recognition_without_preload_content(
        self,
        property_identifier: Annotated[StrictStr, Field(description="Update recognition record associated with this property identifier")],
        recognition_identifier: Annotated[StrictStr, Field(description="Update recognition with this identifier")],
        upsert_recognition_supplier: UpsertRecognitionSupplier,
        wink_version: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update Recognition

        Update a recognition by its identifier

        :param property_identifier: Update recognition record associated with this property identifier (required)
        :type property_identifier: str
        :param recognition_identifier: Update recognition with this identifier (required)
        :type recognition_identifier: str
        :param upsert_recognition_supplier: (required)
        :type upsert_recognition_supplier: UpsertRecognitionSupplier
        :param wink_version:
        :type wink_version: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_recognition_serialize(
            property_identifier=property_identifier,
            recognition_identifier=recognition_identifier,
            upsert_recognition_supplier=upsert_recognition_supplier,
            wink_version=wink_version,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '500': "object",
            '403': "GenericErrorMessage",
            '401': "GenericErrorMessage",
            '400': "ShowRecognition400Response",
            '200': "PropertySupplier",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_recognition_serialize(
        self,
        property_identifier,
        recognition_identifier,
        upsert_recognition_supplier,
        wink_version,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if property_identifier is not None:
            _path_params['propertyIdentifier'] = property_identifier
        if recognition_identifier is not None:
            _path_params['recognitionIdentifier'] = recognition_identifier
        # process the query parameters
        # process the header parameters
        if wink_version is not None:
            _header_params['Wink-Version'] = wink_version
        # process the form parameters
        # process the body parameter
        if upsert_recognition_supplier is not None:
            _body_params = upsert_recognition_supplier


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json', 
                    'application/xml', 
                    'text/xml', 
                    'text/html', 
                    'text/plain', 
                    '*/*'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'oauth2ClientCredentials'
        ]

        return self.api_client.param_serialize(
            method='PUT',
            resource_path='/api/property/{propertyIdentifier}/recognition/{recognitionIdentifier}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )


