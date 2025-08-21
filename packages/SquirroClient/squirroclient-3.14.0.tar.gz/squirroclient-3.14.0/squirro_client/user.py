import re

from .util import _dumps, deprecation


class UserApiMixin:
    """Mixin class which encapsulates the functionality of the user API
    service.

    All the methods of this class are made available in the
    [[SquirroClient]] class.
    """

    def get_user_data(self, user_id, include_projects=False, api_version="v1"):
        """Return data about a specific user, including any custom values.

        :param user_id: User identifier.
        :param include_projects: Return a list of all the user's projects.
        :param api_version: The version of the API to use (optional).
        :returns: A dictionary which contains the user data.

        Example::

            >>> client.get_user_data('H5Qv-WhgSBGW0WL8xolSCQ')
            {u'email': u'test@test.com',
             u'id': u'H5Qv-WhgSBGW0WL8xolSCQ',
             u'tenant': u'test'}

        """

        url = f"{self.user_api_url}/{api_version}/{self.tenant}/users/{user_id}"
        params = {"include_projects": include_projects}
        res = self._perform_request("get", url, params=params)
        return self._process_response(res)

    def update_user_data(self, user_id, changes, api_version="v1"):
        """Update data for the given user. Any value can be set and will be
        returned again when getting the user.

        :param user_id: User identifier.
        :param changes: A dictionary containing user data to be updated.
        :param api_version: API version to use.
        :returns: A dictionary which contains the updated user data.

        Example::

            >>> client.update_user_data('H5Qv-WhgSBGW0WL8xolSCQ',
            ...                         {'name': 'John Smith'})
            {u'email': u'test@test.com',
             u'id': u'H5Qv-WhgSBGW0WL8xolSCQ',
             u'name': u'John Smith',
             u'tenant': u'test'}

        """

        url = f"{self.user_api_url}/{api_version}/{self.tenant}/users/{user_id}"

        if api_version == "v1":
            headers = {"Content-Type": "application/json"}
            res = self._perform_request(
                "put", url, data=_dumps(changes), headers=headers
            )

        else:
            res = self._perform_request("put", url, data=changes)

        return self._process_response(res)

    def change_user_password(
        self,
        user_id,
        current_password,
        new_password,
        new_password_confirm,
    ):
        """
        Change a user's password.

        :param user_id: User identifier.
        :param current_password: User's current password.
        :param new_password: User's new password.
        :param new_password_confirm: User's new password for confirmation.
        """
        headers = {"Content-Type": "application/json"}

        url = (
            f"{self.user_api_url}/{self.version}/{self.tenant}/users/{user_id}/password"
        )

        data = {
            "current_password": current_password,
            "new_password": new_password,
            "new_password_confirm": new_password_confirm,
        }

        res = self._perform_request("put", url, data=_dumps(data), headers=headers)
        return self._process_response(res)

    def get_users_password_policy(self):
        """Retrieve the password policy for users' passwords."""
        url = f"{self.user_api_url}/{self.version}/{self.tenant}/users/password_policy"
        res = self._perform_request("get", url)
        return self._process_response(res)

    def get_authentication(self, user_id, service):
        """Retrieves an authentication for a given service.

        :param user_id: User identifier
        :param service: Authentication service
        :returns: A dictionary containing the authentication data.

        Example::

            >>> client.get_authentication('H5Qv-WhgSBGW0WL8xolSCQ', 'facebook')
            {u'access_secret': u'secret',
             u'access_secret_expires': u'2014-01-09T08:40:00',
             u'access_token': u'token',
             u'access_token_expires': u'2014-01-09T08:40:00',
             u'display_name': u'John Smith',
             u'service_user': u'1234567',
             u'state': u'ok'}
        """

        url = f"{self.user_api_url}/{self.version}/{self.tenant}/authentications/{service}/{user_id}"

        res = self._perform_request("get", url)
        return self._process_response(res, [200])

    def new_or_modify_authentication(
        self,
        user_id,
        service,
        service_user,
        access_token,
        access_secret=None,
        display_name=None,
        access_token_expires=None,
        access_secret_expires=None,
    ):
        """Create a new authentication or modify an existing authentication
        for an external service.

        :param user_id: User identifier.
        :param service: Authentication service.
        :param service_user: Service user identifier.
        :param access_token: Service access token.
        :param access_secret: Service access secret.
        :param display_name: Service user display name.
        :param access_token_expires: Expiry date for service access token.
        :param access_secret_expires: Expiry date for service access secret.
        :returns: A dictionary containing the updated authentication data.

        Example::

            >>> client.new_or_modify_authentication(
            ...     'H5Qv-WhgSBGW0WL8xolSCQ', 'facebook', '1234567', 'token',
            ...     'secret', 'John Smith',
            ...     datetime.datetime(2014, 1, 9, 8, 40),
            ...     datetime.datetime(2014, 1, 9, 8, 40))
            {u'access_secret': u'secret',
             u'access_secret_expires': u'2014-01-09T08:40:00',
             u'access_token': u'token',
             u'access_token_expires': u'2014-01-09T08:40:00',
             u'display_name': u'John Smith',
             u'service_user': u'1234567',
             u'state': u'ok'}
        """

        url = f"{self.user_api_url}/{self.version}/{self.tenant}/authentications/{service}/{user_id}"

        # build data
        data = {"service_user": service_user, "access_token": access_token}
        if display_name is not None:
            data["display_name"] = display_name
        if access_secret is not None:
            data["access_secret"] = access_secret
        if access_token_expires is not None:
            data["access_token_expires"] = self._format_date(access_token_expires)
        if access_secret_expires is not None:
            data["access_secret_expires"] = self._format_date(access_secret_expires)

        # build params
        params = {"client_id": self.client_id, "client_secret": self.client_secret}

        headers = {"Content-Type": "application/json"}

        res = self._perform_request(
            "post", url, params=params, data=_dumps(data), headers=headers
        )
        return self._process_response(res, [200, 201])

    def delete_authentication(self, user_id, service):
        """Delete an authentication.

        :param user_id: User identifier.
        :param service: Service name.

        Example::

            >>> client.delete_authentication('H5Qv-WhgSBGW0WL8xolSCQ',
            ...                              'facebook')
        """

        url = f"{self.user_api_url}/{self.version}/{self.tenant}/authentications/{service}/{user_id}"

        res = self._perform_request("delete", url)
        return self._process_response(res, [204])

    def new_grant(self, user_id, type, for_client_id=None, project_permissions=None):
        """Create a new grant.

        :param user_id: User identifier.
        :param type: Token type, either `user` or `service`.
        :param for_client_id: Client id of the service the token is for. Only
            used when type is `service`.
        :param project_permissions: List of permissions granted with this
            grant.
        :returns: A dictionary containing the `refresh_token` and the `id` of
            the grant.

        Example::

            >>> client.new_grant('H5Qv-WhgSBGW0WL8xolSCQ', 'service',
            ...                  'abdc0183029498f20c38')
            {u'id': u'yL0dnd17RNe9Jpn7uAa8Bw',
             u'refresh_token': u'b4c7440364afb80c2...14e2d538b0b773894ea2'}
        """

        url = f"{self.user_api_url}/{self.version}/{self.tenant}/users/{user_id}/grants"

        params = {
            "type": type,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        # If the type is session we need to pass the target
        if type == "service":
            params["for_client_id"] = for_client_id

        if project_permissions:
            if isinstance(project_permissions, list):
                project_permissions = ",".join(project_permissions)
            params["project_permissions"] = project_permissions

        res = self._perform_request("post", url, data=params)
        return self._process_response(res, [201])

    def delete_grant(self, user_id, grant_id):
        """Delete a grant.

        :param user_id: User identifier.
        :param grant_id: Grant identifier.

        Example::

            >>> client.delete_grant(
            ...     'H5Qv-WhgSBGW0WL8xolSCQ', 'yL0dnd17RNe9Jpn7uAa8Bw')
        """

        return self.delete_session(user_id, grant_id)

    def get_user_grants(self, user_id):
        """Get all grants for the provided user.

        :param user_id: User identifier.
        :returns: A dictionary where the value of `grants` is a list of the
            grants.

        Example::

            >>> client.get_user_grants('H5Qv-WhgSBGW0WL8xolSCQ')
            {u'grants': [{u'created_at': u'2012-12-21 16:00:01',
                          u'valid_to': u'2022-12-21 16:00:01',
                          u'id': u'yL0dnd17RNe9Jpn7uAa8Bw', u'type': u'user'}]}
        """

        url = f"{self.user_api_url}/{self.version}/{self.tenant}/users/{user_id}/grants"

        params = {"client_id": self.client_id, "client_secret": self.client_secret}

        res = self._perform_request("get", url, params=params)
        return self._process_response(res, [200])

    def get_session(self, user_id, session_id):
        """Get data of a specific session.

        :param user_id: User identifier.
        :param session_id: Session identifier

        Example::

            >>> client.get_session('H5Qv-WhgSBGW0WL8xolSCQ', 'yL0dnd17RNe9Jpn7uAa8Bw')
        """

        url = (
            f"{self.user_api_url}/{self.version}/{self.tenant}"
            f"/users/{user_id}/sessions/{session_id}"
        )

        res = self._perform_request("get", url)
        return self._process_response(res, [200])

    def delete_session(self, user_id, session_id):
        """Delete a session.

        :param user_id: User identifier.
        :param session_id: Session identifier

        Example::

            >>> client.delete_session('H5Qv-WhgSBGW0WL8xolSCQ',
            ...                       'yL0dnd17RNe9Jpn7uAa8Bw')
        """

        url = (
            f"{self.user_api_url}/{self.version}/{self.tenant}"
            f"/users/{user_id}/sessions/{session_id}"
        )

        res = self._perform_request("delete", url)
        return self._process_response(res, [204])

    def get_users(self, include_config=None):
        """Returns all users within the logged-in users tenant.

        :param include_config: Boolean Whether to include user configuration or
            not. Defaults to True

        Example::

            >>> client.get_users()
            {u'users': [
                {
                    u'email': u'user01@example.com',
                    u'full_name': u'User 1',
                    u'id': u'H5Qv-WhgSBGW0WL8xolSCQ',
                    u'role': u'user',
                    u'role_permissions': [u'user'],
                    u'tenant': u'lW8-FnZlQYWBimxFknYitw',
                    …
                }
            ]}
        """
        params = {}
        if include_config is not None:
            params["include_config"] = include_config

        url = f"{self.user_api_url}/{self.version}/{self.tenant}/users"

        res = self._perform_request("get", url, params=params)
        return self._process_response(res, [200])

    def add_user(self, email=None, password=None, role=None):
        """
        Add a new user to the current tenant.

        :param email: Email address of the user.
        :param password: Password of the user.
        :param role: role of the user in the tenant. Must be one of:
            admin, user, demo, reader
        """
        headers = {"Content-Type": "application/json"}
        data = {}

        email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if email and email_regex.match(email):
            data["email"] = email
        if password:
            data["password"] = password
        if role:
            data["role"] = role

        url = f"{self.user_api_url}/v0/{self.tenant}/users"

        res = self._perform_request("post", url, data=_dumps(data), headers=headers)
        return self._process_response(res, [201])

    def delete_user(self, user_id):
        """Delete a user from the system.

        :param user_id: Identifier of the user to delete.

        Example::

            >>> client.delete_user('H5Qv-WhgSBGW0WL8xolSCQ')
        """
        url = f"{self.user_api_url}/{self.version}/{self.tenant}/users/{user_id}"
        res = self._perform_request("delete", url)
        return self._process_response(res, [204])

    def get_project_members(self, project_id):
        """Returns all users and groups associated with the given project.

        :param project_id: Project identifier.

        Example::

            >>> client.get_project_members('2sic33jZTi-ifflvQAVcfw')
            {u'members': [{
               u'email': u'user01@example.com',
               u'full_name': u'User 1',
               u'member_id': u'H5Qv-WhgSBGW0WL8xolSCQ',
               u'member_type': u'user',
               u'server_role': u'user',
               u'project_role': u'reader',
               u'project_id': '2sic33jZTi-ifflvQAVcfw'
               u'permissions': [u'fingerprints.read.*',
                                u'fingerprints.write.create.adhoc',
                                u'items.read.*',
                                u'previews.read.*',
                                u'projects.read.*',
                                u'savedsearches.read.*',
                                u'scores.read.*',
                                u'signals.read.*',
                                u'sources.read.*']},
                …
            ]}

        The permissions list reflects the permissions the given user or group
        has in this project. The permissions depend on the user's project role
        and server role.
        """
        url = (
            f"{self.user_api_url}/{self.version}/{self.tenant}/"
            f"projects/{project_id}/members"
        )

        res = self._perform_request("get", url)
        return self._process_response(res, [200])

    def get_token_from_msexchuid(self, msexchuid):
        """Retrieves the OAUTH2 authentication token for a given user based
            on their MS Exchange UID (if it exists).

        :param msexchuid: Microsoft Exchange UID
        :returns: A dictionary containing the OAUTH2 token and the Squirro user id.

        Example::

            >>> client.get_token_from_msexchuid('89edf14d-90c4-834d-9efc-cd20a93fc74b')
            {
                u'oauth2_token': u'5ad37930dda85a7...6c066b2253dba8d19',
                u'user_id': u'vP7h4g7EThuJKIfMorHTUQ',
            }
        """

        msg = (
            "The `get_token_from_msexchuid` method is obsolete. It has been replaced by"
            " the `get_token_from_msexchuid_token` method."
        )
        deprecation(msg)
        raise NotImplementedError(msg)

    def get_token_from_msexchuid_token(self, msexchuid_token):
        """
        Retrieves an OAUTH2 authentication token based on the provided MS Exchange user
        identity token.

        :param msexchuid_token: a Microsoft Exchange user identity token (JWT).
        :return: A dictionary containing the OAUTH2 token and the Squirro user id.

        Example::

            >>> client.get_token_from_msexchuid_token("<your.jwt.token>")
            {
                u'oauth2_token': u'5ad37930dda85a7...6c066b2253dba8d19',
                u'user_id': u'vP7h4g7EThuJKIfMorHTUQ',
            }
        """
        url = f"{self.user_api_url}/msexchange/oauth2_token"

        params = {"msexchuid_token": msexchuid_token}

        res = self._perform_request("get", url, params=params)
        return self._process_response(res, [200])

    def add_project_member(self, project_id, role, user_id=None, group_id=None):
        """Adds a user or group to a project as a member.

        :param project_id: Project identifier of the project in which to add
            the member.
        :param role: Role of the member. Allowed values: `reader`, `member`,
            `admin`.
        :param user_id: Identifier of the user to be added (can't be combined
            with `group_id`).
        :param group_id: Identifier of the group to be added (can't be
            combined with `user_id`).

        Example::

            >>> client.add_project_member('2sic33jZTi-ifflvQAVcfw', 'member',
                                          user_id='H5Qv-WhgSBGW0WL8xolSCQ')
            {
               u'email': u'user01@example.com',
               u'full_name': u'User 1',
               u'member_id': u'H5Qv-WhgSBGW0WL8xolSCQ',
               u'member_type': u'user',
               u'server_role': u'user',
               u'project_role': u'member',
               u'project_id': '2sic33jZTi-ifflvQAVcfw'
               u'permissions': [u'fingerprints.*',
                                u'items.*',
                                u'previews.*',
                                u'projects.read.*',
                                u'projects.write.*',
                                u'savedsearches.*',
                                u'scores.*',
                                u'signals.*',
                                u'sources.*']
            }
        """
        url = (
            f"{self.user_api_url}/{self.version}/{self.tenant}/"
            f"projects/{project_id}/members"
        )

        data = {"user_id": user_id, "group_id": group_id, "role": role}
        res = self._perform_request("post", url, data=data)
        return self._process_response(res, [200])

    def update_project_member(self, project_id, member_id, role):
        """Modifies a project membership.

        Right now only the role can be changed, so that argument is required.

        :param project_id: Project identifier of the project in which to
            modify the member.
        :param member_id: Identifier of the user or group to be updated.
        :param role: New role of the member. Allowed values: `reader`,
            `member`, `admin`.

        Example::

            >>> client.update_project_member('2sic33jZTi-ifflvQAVcfw',
            ...                              'H5Qv-WhgSBGW0WL8xolSCQ',
            ...                              'admin')
            {
               u'email': u'user01@example.com',
               u'full_name': u'User 1',
               u'member_id': u'H5Qv-WhgSBGW0WL8xolSCQ',
               u'member_type': u'admin',
               …
            }
        """
        url = (
            f"{self.user_api_url}/{self.version}/{self.tenant}/"
            f"projects/{project_id}/members/{member_id}"
        )
        res = self._perform_request("put", url, data={"role": role})
        return self._process_response(res)

    def delete_project_member(self, project_id, member_id):
        """Removes a user or group from a project as a member.

        :param project_id: Project identifier of the project to remove the
            member from.
        :param member_id: Identifier of the user or group to be removed.

        Example::

            >>> client.delete_project_member('2sic33jZTi-ifflvQAVcfw',
                                             'H5Qv-WhgSBGW0WL8xolSCQ')
        """
        url = (
            f"{self.user_api_url}/{self.version}/{self.tenant}/"
            f"projects/{project_id}/members/{member_id}"
        )
        res = self._perform_request("delete", url)
        return self._process_response(res, [204])

    def get_groups(self):
        """Returns all groups within the logged-in users tenant.

        Example::

            >>> client.get_groups()
            [{u'id': u'1jo-WmmyRvC8UYtPMIQaoQ',
              u'name': 'Team East',
              u'members': [
                  {
                      u'email': u'user01@example.com',
                      u'full_name': u'User 1',
                      u'id': u'H5Qv-WhgSBGW0WL8xolSCQ',
                      u'role': u'user',
                      u'role_permissions': [u'user'],
                      u'tenant': 'lW8-FnZlQYWBimxFknYitw'
                  }
              ]
             }
            ]
        """
        url = f"{self.user_api_url}/{self.version}/{self.tenant}/groups"
        res = self._perform_request("get", url)
        return self._process_response(res, [200])

    def create_group(self, name, members=None):
        """Create a new group.

        :param name: Group name
        :param members: List of members that should be added to the group.
            This is a list of dictionaries, where only the `id` field is used
            for each entry.

        Example::

            >>> client.create_group('Team East', members=[{"id": "5efzuNRpQ266E3O11b0h2w"}])
            {
                'id': '1jo-WmmyRvC8UYtPMIQaoQ',
                'name': 'Team East',
                'members': [
                  {
                      'email': 'user01@example.com',
                      'full_name': 'User 1',
                      'id': '5efzuNRpQ266E3O11b0h2w',
                      'role': 'user',
                      'role_permissions': ['user'],
                      'tenant': 'lW8-FnZlQYWBimxFknYitw'
                  }
              ]
            }
        """
        url = f"{self.user_api_url}/{self.version}/{self.tenant}/groups"
        data = {"name": name}
        if members is not None:
            data["members"] = _dumps(members)
        res = self._perform_request("post", url, data=data)
        return self._process_response(res, [201])

    def get_group(self, group_id, include_projects=False):
        """Returns details, including the members, of a group.

        :param group_id: Identifier of the group for which the details are
            returned.
        :param include_projects: Include all projects the group has access to.

        Example::

            >>> client.get_group('1jo-WmmyRvC8UYtPMIQaoQ')
            {
                u'id': u'1jo-WmmyRvC8UYtPMIQaoQ',
                u'name': 'Team East',
                u'members': [
                    {
                        u'email': u'user01@example.com',
                        u'full_name': u'User 1',
                        u'id': u'H5Qv-WhgSBGW0WL8xolSCQ',
                        u'role': u'user',
                        u'role_permissions': [u'user'],
                        u'tenant': 'lW8-FnZlQYWBimxFknYitw'
                    }
                ]
            }
        """
        url = f"{self.user_api_url}/{self.version}/{self.tenant}/groups/{group_id}"
        res = self._perform_request(
            "get", url, params={"include_projects": include_projects}
        )
        return self._process_response(res, [200])

    def update_group(self, group_id, name, members=None, projects=None):
        """Modify a group's attributes.

        :param group_id: Identifier of the group to modify.
        :param name: New name of the group.
        :param members: List of members that should be added to the group.
            This is a list of dictionaries, where only the `id` field is used
            for each entry.
        :param projects: List of projects which this group should have access
            to.

        Example::

            >>> client.update_group('1jo-WmmyRvC8UYtPMIQaoQ', 'Team West')
            {
                u'id': u'1jo-WmmyRvC8UYtPMIQaoQ',
                u'name': 'Team West',
                u'members': [
                    {
                        u'email': u'user01@example.com',
                        u'full_name': u'User 1',
                        u'id': u'H5Qv-WhgSBGW0WL8xolSCQ',
                        u'role': u'user',
                        u'role_permissions': [u'user'],
                        u'tenant': 'lW8-FnZlQYWBimxFknYitw'
                    }
                ]
            }
        """
        url = f"{self.user_api_url}/{self.version}/{self.tenant}/groups/{group_id}"
        data = {"name": name}
        if members is not None:
            data["members"] = _dumps(members)
        if projects is not None:
            data["projects"] = _dumps(projects)
        res = self._perform_request("put", url, data=data)
        return self._process_response(res, [200])

    def delete_group(self, group_id):
        """Delete a group.

        :param group_id: Identifier of the group to delete.

        Example::

            >>> client.delete_group('1jo-WmmyRvC8UYtPMIQaoQ')
        """
        url = f"{self.user_api_url}/{self.version}/{self.tenant}/groups/{group_id}"
        res = self._perform_request("delete", url)
        return self._process_response(res, [204])

    def add_group_member(self, group_id, user_id):
        """Adds a user to the group.

        :param group_id: Identifier of the group to add the user to.
        :param user_id: Identifier of the user to add to the group.

        Example::

            >>> client.add_group_member('1jo-WmmyRvC8UYtPMIQaoQ',
                                        'H5Qv-WhgSBGW0WL8xolSCQ')
            {
                u'email': u'user01@example.com',
                u'full_name': u'User 1',
                u'id': u'H5Qv-WhgSBGW0WL8xolSCQ',
                u'role': u'user',
                u'role_permissions': [u'user'],
                u'tenant': 'lW8-FnZlQYWBimxFknYitw'
            }
        """
        url = f"{self.user_api_url}/{self.version}/{self.tenant}/groups/{group_id}"
        res = self._perform_request("post", url, data={"user_id": user_id})
        return self._process_response(res, [200])

    def delete_group_member(self, group_id, user_id):
        """Removes a user from the group.

        :param group_id: Identifier of the group from which to remove the user.
        :param user_id: Identifier of the user to remove from the group.

        Example::

            >>> client.delete_group_member('1jo-WmmyRvC8UYtPMIQaoQ',
                                           'H5Qv-WhgSBGW0WL8xolSCQ')
        """
        url = (
            f"{self.user_api_url}/{self.version}/{self.tenant}/"
            f"groups/{group_id}/members/{user_id}"
        )
        res = self._perform_request("delete", url)
        return self._process_response(res, [204])

    def signup(self, email, password, full_name=None):
        """
        Create the first user on the cluster or create a new workspace.

        This implements two different cases depending on the cluster
        configuration:

        - With workspaces enabled, the user is created in the global workspace,
          but only if no existing user exists there. If a user has already
          been created in the global tenant, signup always fails.
        - Without workspaces, a new tenant is created for that user. This is
          a legacy feature, re-implementing the original multi-tenancy
          approach. This may be changed in the future to only allow a signup
          if no tenant/user has been created yet.

        :param email: Email address for the user.
        :param password: Password for the user.
        :param full_name: Display name for the user.
        :returns: A dictionary which contains the user data.

        Example::

            >>> client.signup(email='foo@example.com', password='aSKJL18274!')
            {'user_id': 'ixLkdYmaQzasRi5_luj7IQ',
             'tenant': 'example'}
        """
        url = f"{self.user_api_url}/v2/signup"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "email": email,
            "password": password,
            "full_name": full_name,
        }
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "post", url, data=_dumps(data), headers=headers, unauthenticated=True
        )
        return self._process_response(res, [201])

    def get_workspaces(self, include_projects=False, admin_only=False):
        """Returns a list of all the workspaces the user can access.

        :param include_projects: Include all projects the user has access to.
        :param admin_only: If set to `True` only return workspaces on which
            the user is an admin.

        Example::

            >>> client.get_workspaces()
            [
                {
                    "domain": "other-project",
                    "title": "Other Project"
                },
                {
                    "domain": "project-1",
                    "title": "Project 1"
                }
            ]
        """
        url = f"{self.user_api_url}/v2/workspaces"
        res = self._perform_request(
            "get",
            url,
            params={"include_projects": include_projects, "admin_only": admin_only},
        )
        return self._process_response(res)

    def create_workspace(self, title):
        """Create a new workspace.

        :param title: Workspace title.

        Example::

            >>> client.create_workspace(title="Project 5")
            {"domain": "project-5", "title": "Project 5"}
        """
        url = f"{self.user_api_url}/v2/workspaces"
        data = {"title": title}
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("post", url, data=_dumps(data), headers=headers)
        return self._process_response(res, [201])

    def delete_workspace(self, workspace_domain):
        """Delete a workspace.

        Example::

            >>> client.delete_workspace("workspace-1")
        """
        url = f"{self.user_api_url}/v2/workspaces/{workspace_domain}"
        res = self._perform_request("delete", url)
        return self._process_response(res, [204])

    def add_workspace_users(self, workspace_domain, emails, role):
        """Adds users to a workspace by email address.

        Example::

            >>> client.add_workspace_users(
            ...     "project-1", ["user@example.com", "foo@example.com"], "reader")
            [
                {"user_id": "wWzKOdx-TiiPV2k7FEu6_w", "workspace": "project-1"},
                {"user_id": "8Mavps2oTSatzomVEEBtVA", "workspace": "project-1"}
            ]
        """
        url = f"{self.user_api_url}/v2/workspaces/{workspace_domain}/users"
        data = {"emails": emails, "role": role}
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("post", url, data=_dumps(data), headers=headers)
        return self._process_response(res, [200, 201])

    def set_workspace_user_role(self, workspace_domain, user_id, role):
        """Adds or edits a user's role in a workspace.

        Example::

            >>> client.set_workspace_user_role(
            ...     "project-1", "wWzKOdx-TiiPV2k7FEu6_w", "admin")
            {"user_id": "wWzKOdx-TiiPV2k7FEu6_w", "workspace": "project-1"}
        """
        url = f"{self.user_api_url}/v2/workspaces/{workspace_domain}/users"
        data = {"user_id": user_id, "role": role}
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("post", url, data=_dumps(data), headers=headers)
        return self._process_response(res, [200, 201])[0]

    def delete_workspace_user(self, workspace_domain, user_id):
        """Delete a user from the workspace.

        Example::

            >>> client.delete_workspace_user("project-1", "wWzKOdx-TiiPV2k7FEu6_w")
            >>>
        """
        url = f"{self.user_api_url}/v2/workspaces/{workspace_domain}/users/{user_id}"
        res = self._perform_request("delete", url)
        return self._process_response(res, [204])

    def get_workspace_users(self, workspace_domain):
        """Returns a list of all users from a workspace.

        Example::

            >>> client.get_workspace_users("project-1")
            [
                {"id": "wWzKOdx-TiiPV2k7FEu6_w",
                 "email": "user@example.com",
                 "role": "admin",
                 "full_name": "User Example"}
            ]
        """
        url = f"{self.user_api_url}/v2/workspaces/{workspace_domain}/users"
        res = self._perform_request("get", url)
        return self._process_response(res, [200])
