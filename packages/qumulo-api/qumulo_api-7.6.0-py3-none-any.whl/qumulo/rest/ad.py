# Copyright (c) 2013 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.


from typing import Any, Dict, List, Optional, Union

import qumulo.lib.request as request

from qumulo.lib.uri import UriBuilder

# Values for the advanced AD setting controlling DCERPC signing.
VALID_SIGNING_CHOICES = ('NO_SIGNING', 'WANT_SIGNING', 'REQUIRE_SIGNING')

# Values for the advanced AD setting controlling DCERPC sealing.
VALID_SEALING_CHOICES = ('NO_SEALING', 'WANT_SEALING', 'REQUIRE_SEALING')

# Values for the advanced AD setting controlling DCERPC encryption.
VALID_ENCRYPTION_CHOICES = ('NO_AES', 'WANT_AES', 'REQUIRE_AES')

MonitorURI = Dict[str, str]
AdLdapObject = Dict[str, Any]


class ActiveDirectory:
    def __init__(self, client: request.SendRequestObject):
        self.client = client

    def list_ad(self) -> Dict[str, Any]:
        method = 'GET'
        uri = '/v1/ad/status'

        return self.client.send_request(method, uri).data

    def poll_ad(self) -> Dict[str, Any]:
        method = 'GET'
        uri = '/v1/ad/monitor'

        return self.client.send_request(method, uri).data

    def dismiss_ad_error(self) -> Dict[str, Any]:
        method = 'POST'
        uri = '/v1/ad/dismiss-error'

        return self.client.send_request(method, uri).data

    def join_ad(
        self,
        domain: object,
        username: object,
        password: object,
        ou: Optional[object] = None,
        domain_netbios: Optional[object] = None,
        enable_ldap: Optional[bool] = False,
        base_dn: Optional[object] = None,
        search_trusted_domains: Optional[bool] = None,
        domain_controllers: Optional[str] = None,
        dns_config_id: Optional[int] = None,
    ) -> MonitorURI:
        method = 'POST'
        uri = '/v1/ad/join'

        if ou is None:
            ou = ''
        if domain_netbios is None:
            domain_netbios = ''
        if base_dn is None:
            base_dn = ''

        config: Dict[str, Any] = {
            'domain': str(domain),
            'domain_netbios': str(domain_netbios),
            'user': str(username),
            'password': str(password),
            'ou': str(ou),
            'use_ad_posix_attributes': enable_ldap,
            'base_dn': str(base_dn),
        }
        if search_trusted_domains is not None:
            config['search_trusted_domains'] = search_trusted_domains
        if domain_controllers is not None:
            config['domain_controllers'] = domain_controllers
        if dns_config_id is not None:
            config['dns_config_id'] = dns_config_id

        return self.client.send_request(method, uri, body=config).data

    def reconfigure_ad(
        self,
        enable_ldap: Optional[bool] = None,
        base_dn: Optional[str] = None,
        search_trusted_domains: Optional[bool] = None,
        domain: Optional[str] = None,
        domain_controllers: Optional[str] = None,
        dns_config_id: Optional[int] = None,
    ) -> MonitorURI:
        method = 'POST'
        uri = '/v1/ad/reconfigure'

        config: Dict[str, Union[int, str, bool]] = {}
        if enable_ldap is not None:
            config['use_ad_posix_attributes'] = enable_ldap
        if base_dn is not None:
            config['base_dn'] = base_dn
        if domain is not None:
            config['domain'] = domain
        if search_trusted_domains is not None:
            config['search_trusted_domains'] = search_trusted_domains
        if domain_controllers is not None:
            config['domain_controllers'] = domain_controllers
        if dns_config_id is not None:
            config['dns_config_id'] = dns_config_id

        return self.client.send_request(method, uri, body=config).data

    def leave_ad(
        self,
        domain: object,
        username: object,
        password: object,
        dns_config_id: Optional[int] = None,
    ) -> MonitorURI:
        method = 'POST'
        uri = '/v1/ad/leave'

        # XXX scott: support none for these in the api, also, don't call domain
        # assistant script in that case
        if username is None:
            username = ''
        if password is None:
            password = ''

        config: Dict[str, Union[int, str]] = {
            'domain': str(domain),
            'user': str(username),
            'password': str(password),
        }
        if dns_config_id is not None:
            config['dns_config_id'] = dns_config_id

        return self.client.send_request(method, uri, body=config).data

    def cancel_ad(self) -> MonitorURI:
        method = 'POST'
        uri = '/v1/ad/cancel'

        return self.client.send_request(method, uri).data

    def uid_to_sid_get(self, uid: object) -> List[str]:
        method = 'GET'
        uri = '/v1/ad/uids/' + str(uid) + '/sids/'

        return self.client.send_request(method, uri).data

    def username_to_sid_get(self, name: object) -> List[str]:
        return self.client.send_request('GET', f'/v1/ad/usernames/{name}/sids/').data

    def name_to_ad_accounts(self, name: object) -> List[AdLdapObject]:
        uri = UriBuilder(path='/v1/ad/usernames')
        uri.add_path_component(str(name))
        uri.add_path_component('objects')
        uri.append_slash()
        return self.client.send_request('GET', str(uri)).data

    def sid_to_uid_get(self, sid: str) -> Dict[str, int]:
        method = 'GET'
        uri = '/v1/ad/sids/' + sid + '/uid'

        return self.client.send_request(method, uri).data

    def sid_to_username_get(self, sid: object) -> str:
        return self.client.send_request('GET', f'/v1/ad/sids/{sid}/username').data

    def sid_to_gid_get(self, sid: str) -> Dict[str, int]:
        method = 'GET'
        uri = '/v1/ad/sids/' + sid + '/gid'

        return self.client.send_request(method, uri).data

    def sid_to_ad_account(self, sid: str) -> AdLdapObject:
        return self.client.send_request('GET', '/v1/ad/sids/' + sid + '/object').data

    def gid_to_sid_get(self, gid: object) -> List[str]:
        method = 'GET'
        uri = '/v1/ad/gids/' + str(gid) + '/sids/'

        return self.client.send_request(method, uri).data

    def sid_to_expanded_group_sids_get(self, sid: str) -> List[Dict[str, str]]:
        method = 'GET'
        uri = '/v1/ad/sids/' + sid + '/expanded-groups/'

        return self.client.send_request(method, uri).data

    def distinguished_name_to_ad_account(self, distinguished_name: object) -> AdLdapObject:
        uri = UriBuilder(path='/v1/ad/distinguished-names/')
        uri.add_path_component(str(distinguished_name))
        uri.add_path_component('object')
        return self.client.send_request('GET', str(uri)).data

    def get_advanced_settings(self) -> request.RestResponse:
        method = 'GET'
        uri = '/v1/ad/settings'
        return self.client.send_request(method, uri)

    def set_advanced_settings(
        self, signing: object, sealing: object, crypto: object, if_match: Optional[str] = None
    ) -> Dict[str, str]:
        """
        This method controls advanced Active Directory settings.

        @param signing  Configure DCERPC signing to be off, prefer signing, or require
                        signing. Must be one of NO_SIGNING, WANT_SIGNING, or REQUIRE_SIGNING

        @param sealing  Configure DCERPC sealing to be off, prefer sealing, or require
                        sealing. Must be one of NO_SEALING, WANT_SEALING, or REQUIRE_SEALING

        @param crypto   Configure DCERPC to not use encryption, prefer AES encryption,
                        or require AES encryption. Must be one of NO_AES, WANT_AES, or
                        REQUIRE_AES
        """
        method = 'PUT'
        uri = '/v1/ad/settings'
        body = {'signing': str(signing), 'sealing': str(sealing), 'crypto': str(crypto)}

        return self.client.send_request(method, uri, body=body, if_match=if_match).data
