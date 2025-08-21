# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import typing as ty

from keystoneauth1.identity.v3 import base
from keystoneauth1 import session as ks_session

__all__ = ('PasswordMethod', 'Password')


class PasswordMethod(base.AuthMethod):
    """Construct a User/Password based authentication method.

    :param string password: Password for authentication.
    :param string username: Username for authentication.
    :param string user_id: User ID for authentication.
    :param string user_domain_id: User's domain ID for authentication.
    :param string user_domain_name: User's domain name for authentication.
    """

    password: str
    user_id: str | None = None
    username: str | None = None
    user_domain_id: str | None = None
    user_domain_name: str | None = None

    def __init__(
        self,
        *,
        password: str,
        user_id: str | None = None,
        username: str | None = None,
        user_domain_id: str | None = None,
        user_domain_name: str | None = None,
    ) -> None:
        self.password = password
        self.user_id = user_id
        self.username = username
        self.user_domain_id = user_domain_id
        self.user_domain_name = user_domain_name

    def get_auth_data(
        self,
        session: ks_session.Session,
        auth: base.Auth,
        headers: dict[str, str],
        request_kwargs: dict[str, object],
    ) -> tuple[None, None] | tuple[str, ty.Mapping[str, object]]:
        user: dict[str, ty.Any] = {'password': self.password}

        if self.user_id:
            user['id'] = self.user_id
        elif self.username:
            user['name'] = self.username

            if self.user_domain_id:
                user['domain'] = {'id': self.user_domain_id}
            elif self.user_domain_name:
                user['domain'] = {'name': self.user_domain_name}

        return 'password', {'user': user}

    def get_cache_id_elements(self) -> dict[str, str | None]:
        return {
            'password_password': self.password,
            'password_user_id': self.user_id,
            'password_username': self.username,
            'password_user_domain_id': self.user_domain_id,
            'password_user_domain_name': self.user_domain_name,
        }


class Password(base.Auth):
    """A plugin for authenticating with a username and password.

    :param string auth_url: Identity service endpoint for authentication.
    :param string password: Password for authentication.
    :param string user_id: User ID for authentication.
    :param string username: Username for authentication.
    :param string user_domain_id: User's domain ID for authentication.
    :param string user_domain_name: User's domain name for authentication.
    :param string trust_id: Trust ID for trust scoping.
    :param string system_scope: System information to scope to.
    :param string domain_id: Domain ID for domain scoping.
    :param string domain_name: Domain name for domain scoping.
    :param string project_id: Project ID for project scoping.
    :param string project_name: Project name for project scoping.
    :param string project_domain_id: Project's domain ID for project.
    :param string project_domain_name: Project's domain name for project.
    :param bool reauthenticate: Allow fetching a new token if the current one
                                is going to expire. (optional) default True
    """

    _auth_method_class = PasswordMethod

    def __init__(
        self,
        auth_url: str,
        password: str,
        user_id: str | None = None,
        username: str | None = None,
        user_domain_id: str | None = None,
        user_domain_name: str | None = None,
        *,
        unscoped: bool = False,
        trust_id: str | None = None,
        system_scope: str | None = None,
        domain_id: str | None = None,
        domain_name: str | None = None,
        project_id: str | None = None,
        project_name: str | None = None,
        project_domain_id: str | None = None,
        project_domain_name: str | None = None,
        reauthenticate: bool = True,
        include_catalog: bool = True,
    ) -> None:
        method = self._auth_method_class(
            password=password,
            user_id=user_id,
            username=username,
            user_domain_id=user_domain_id,
            user_domain_name=user_domain_name,
        )
        super().__init__(
            auth_url,
            [method],
            unscoped=unscoped,
            trust_id=trust_id,
            system_scope=system_scope,
            domain_id=domain_id,
            domain_name=domain_name,
            project_id=project_id,
            project_name=project_name,
            project_domain_id=project_domain_id,
            project_domain_name=project_domain_name,
            reauthenticate=reauthenticate,
            include_catalog=include_catalog,
        )
