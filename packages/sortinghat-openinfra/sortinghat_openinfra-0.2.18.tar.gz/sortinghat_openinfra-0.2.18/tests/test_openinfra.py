# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Jose Javier Merchante <jjmerchante@bitergia.com>
#

import datetime
import json
import os

import httpretty
from dateutil.tz import tzutc
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model

from sortinghat.core.context import SortingHatContext
from sortinghat.core.importer.backends.openinfra import OpenInfraIDImporter, OpenInfraIDParser

OPENINFRA_URL = 'https://openstackid-resources.openstack.org'
OPENINFRA_PRIVATE_MEMBERS_URL = OPENINFRA_URL + '/api/v1/members'
OPENINFRA_PUBLIC_MEMBERS_URL = OPENINFRA_URL + '/api/public/v1/members'

ERROR_OPENINFRA_NOT_CONFIGURED = 'Client ID or Secret are not defined in settings for OpenInfraIDParser'


def read_file(filename, mode='r'):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), mode) as f:
        content = f.read()
    return content


def setup_mock_server(public):
    """Configure a Mock server"""

    def request_callback(request, uri, headers):
        page = int(request.querystring.get('page', [1])[0])
        body = bodies[page - 1]
        requests.append(httpretty.last_request())
        return [200, headers, body]

    requests = []
    if public:
        members_url = OPENINFRA_PUBLIC_MEMBERS_URL
        bodies = [read_file('data/openinfra_page_1.json'),
                  read_file('data/openinfra_page_2.json')]
    else:
        members_url = OPENINFRA_PRIVATE_MEMBERS_URL
        bodies = [read_file('data/openinfra_private.json')]

    httpretty.register_uri(httpretty.GET,
                           members_url,
                           responses=[
                               httpretty.Response(body=request_callback)
                               for _ in bodies
                           ])
    return requests, bodies


class TestOpenInfraImporter(TestCase):
    """OpenInfraIDImporter tests"""

    def setUp(self):
        """Initialize variables"""

        self.user = get_user_model().objects.create(username='test')
        self.ctx = SortingHatContext(self.user)

    def test_initialization(self):
        """Test whether attributes are initialized"""

        url = "https://test-url.com/"

        importer = OpenInfraIDImporter(ctx=self.ctx,
                                       url=url)

        self.assertEqual(importer.url, url)
        self.assertEqual(importer.ctx, self.ctx)
        self.assertEqual(importer.NAME, "OpenInfraID")
        self.assertIsNone(importer.from_date)

        # Check from_date is parsed correctly
        importer = OpenInfraIDImporter(ctx=self.ctx,
                                       url=url,
                                       from_date="2023-12-01")
        self.assertEqual(importer.from_date, datetime.datetime(year=2023,
                                                               month=12,
                                                               day=1,
                                                               tzinfo=tzutc()))

    def test_backend_name(self):
        """Test whether the NAME of the backend is right"""

        self.assertEqual(OpenInfraIDImporter.NAME, "OpenInfraID")


class TestOpenInfraParser(TestCase):
    """OpenInfraParser tests"""

    def test_initialization(self):
        """Test whether attributes are initialized"""

        parser = OpenInfraIDParser(OPENINFRA_URL)
        self.assertEqual(parser.url, OPENINFRA_URL)
        self.assertEqual(parser.source, 'openinfra')
        self.assertEqual(parser.client_id, None)
        self.assertEqual(parser.client_secret, None)
        self.assertEqual(parser.private_api, False)

    @override_settings(OPENINFRA_CLIENT_ID='id_test', OPENINFRA_CLIENT_SECRET='secret_test')
    def test_private_initialization(self):
        """Test whether attribute are initialized with private API"""

        parser = OpenInfraIDParser(OPENINFRA_URL)
        self.assertEqual(parser.url, OPENINFRA_URL)
        self.assertEqual(parser.source, 'openinfra')
        self.assertEqual(parser.client_id, 'id_test')
        self.assertEqual(parser.client_secret, 'secret_test')
        self.assertEqual(parser.private_api, True)

    @httpretty.activate
    def test_fetch_items(self):
        """Test whether fetch items returns paginated items"""

        # Set up a mock HTTP server
        requests, bodies = setup_mock_server(public=True)

        # Run fetch items
        parser = OpenInfraIDParser(OPENINFRA_URL)
        raw_items = parser.fetch_items(OPENINFRA_PUBLIC_MEMBERS_URL)
        items = [item for item in raw_items]
        self.assertEqual(len(items), 2)
        self.assertDictEqual(items[0], json.loads(bodies[0]))
        self.assertDictEqual(items[1], json.loads(bodies[1]))

        # Check requests
        expected_qs = [
            {},
            {'page': ['2']}
        ]
        self.assertEqual(len(requests), 2)
        for i, req in enumerate(requests):
            self.assertDictEqual(req.querystring, expected_qs[i])
            self.assertEqual(req.url.split('?')[0], OPENINFRA_PUBLIC_MEMBERS_URL)

    @httpretty.activate
    def test_fetch_items_with_payload(self):
        """Test whether fetch items from date returns paginated items"""

        # Set up a mock HTTP server
        requests, bodies = setup_mock_server(public=True)

        # Run fetch items
        payload = {OpenInfraIDParser.PSORT: 'last_edited'}
        parser = OpenInfraIDParser(OPENINFRA_URL)
        raw_items = parser.fetch_items(OPENINFRA_PUBLIC_MEMBERS_URL, payload=payload)

        items = [item for item in raw_items]
        self.assertEqual(len(items), 2)
        self.assertDictEqual(items[0], json.loads(bodies[0]))
        self.assertDictEqual(items[1], json.loads(bodies[1]))

        # Check requests
        expected_qs = [
            {'order': ['last_edited']},
            {'order': ['last_edited'], 'page': ['2']}
        ]
        self.assertEqual(len(requests), 2)
        for i, req in enumerate(requests):
            self.assertDictEqual(req.querystring, expected_qs[i])
            self.assertEqual(req.url.split('?')[0], OPENINFRA_PUBLIC_MEMBERS_URL)

    @httpretty.activate
    def test_fetch_members(self):
        """Test whether fetch_members returns members"""

        # Set up a mock HTTP server
        requests, bodies = setup_mock_server(public=True)

        # Run fetch members
        parser = OpenInfraIDParser(OPENINFRA_URL)
        members = [member for member in parser.fetch_members()]

        self.assertEqual(len(members), 15)

        # Check requests
        expected_qs = [
            {'page': ['1'], 'per_page': ['100'], 'order': ['last_edited']},
            {'page': ['2'], 'per_page': ['100'], 'order': ['last_edited']}
        ]
        self.assertEqual(len(requests), 2)
        for i, req in enumerate(requests):
            self.assertDictEqual(req.querystring, expected_qs[i])
            self.assertEqual(req.url.split('?')[0], OPENINFRA_PUBLIC_MEMBERS_URL)

    @httpretty.activate
    @override_settings(OPENINFRA_CLIENT_ID='id_test', OPENINFRA_CLIENT_SECRET='secret_test')
    def test_fetch_members_private(self):
        """Test whether fetch_members for private API returns members"""

        # Set up a mock HTTP server
        requests, bodies = setup_mock_server(public=False)

        httpretty.register_uri(
            httpretty.POST,
            OpenInfraIDParser.OPENINFRA_TOKEN_URL,
            body='{"access_token":"test_token","expires_in":7200,"token_type":"Bearer"}',
            status=200
        )

        # Run fetch members
        parser = OpenInfraIDParser(OPENINFRA_URL)
        members = [member for member in parser.fetch_members()]

        self.assertEqual(len(members), 3)

        # Check requests
        expected_qs = [
            {'page': ['1'], 'per_page': ['100'], 'order': ['last_edited'], 'access_token': ['test_token']}
        ]
        self.assertEqual(len(requests), 1)
        for i, req in enumerate(requests):
            self.assertDictEqual(req.querystring, expected_qs[i])
            self.assertEqual(req.url.split('?')[0], OPENINFRA_PRIVATE_MEMBERS_URL)

    @httpretty.activate
    def test_fetch_members_from_date(self):
        """Test whether fetch_members returns members from a given date"""

        # Set up a mock HTTP server
        requests, bodies = setup_mock_server(public=True)

        # Run fetch members
        parser = OpenInfraIDParser(OPENINFRA_URL)
        from_date = datetime.datetime(year=2000, month=1, day=1, tzinfo=tzutc())
        members = [member for member in parser.fetch_members(from_date)]

        self.assertEqual(len(members), 15)

        # Check requests
        expected_qs = [
            {
                'page': ['1'],
                'per_page': ['100'],
                'order': ['last_edited'],
                'filter': ['last_edited>946684800']
            },
            {
                'page': ['2'],
                'per_page': ['100'],
                'order': ['last_edited'],
                'filter': ['last_edited>946684800']
            }
        ]
        self.assertEqual(len(requests), 2)
        for i, req in enumerate(requests):
            self.assertDictEqual(req.querystring, expected_qs[i])
            self.assertEqual(req.url.split('?')[0], OPENINFRA_PUBLIC_MEMBERS_URL)

    @httpretty.activate
    @override_settings(OPENINFRA_CLIENT_ID='id_test', OPENINFRA_CLIENT_SECRET='secret_test')
    def test_create_access_token(self):
        """Test if the access token is created"""

        httpretty.register_uri(
            httpretty.POST,
            OpenInfraIDParser.OPENINFRA_TOKEN_URL,
            body='{"access_token":"test_token","expires_in":7200,"token_type":"Bearer"}',
            status=200
        )

        parser = OpenInfraIDParser(OPENINFRA_URL)
        token = parser._create_access_token()

        self.assertEqual(token, "test_token")

        request = httpretty.last_request()
        self.assertEqual(request.body, b'client_id=id_test&client_secret=secret_test')
        self.assertEqual(request.url.split('?')[0], 'https://id.openinfra.dev/oauth2/token')
        expected_qs = {
            'grant_type': ['client_credentials'],
            'scope': ['https://openstackid-resources.openstack.org/members/read']
        }
        self.assertEqual(request.querystring, expected_qs)

    @httpretty.activate
    @override_settings(OPENINFRA_CLIENT_ID='id_test', OPENINFRA_CLIENT_SECRET='secret_test')
    def test_fetch_items_invalid_token(self):
        """Test whether fetch items with invalid token generates a new token"""

        # Set up a mock HTTP server
        body_error = read_file('data/openinfra_token_error.json')
        body_members = read_file('data/openinfra_private.json')

        responses = [
            httpretty.Response(body=body_error,
                               status=401),
            httpretty.Response(body=body_members),
        ]

        httpretty.register_uri(httpretty.GET,
                               OPENINFRA_PRIVATE_MEMBERS_URL,
                               responses=responses)
        httpretty.register_uri(
            httpretty.POST,
            OpenInfraIDParser.OPENINFRA_TOKEN_URL,
            body='{"access_token":"test_token","expires_in":7200,"token_type":"Bearer"}',
            status=200
        )

        # Run fetch items
        parser = OpenInfraIDParser(OPENINFRA_URL)

        payload = {
            OpenInfraIDParser.PPER_PAGE: 100,
            OpenInfraIDParser.PSORT: 'last_edited',
            OpenInfraIDParser.PPAGE: 1,
            OpenInfraIDParser.PTOKEN: 'wrong_token'
        }
        raw_items = parser.fetch_items(OPENINFRA_PRIVATE_MEMBERS_URL, payload=payload)

        items = [item for item in raw_items]
        self.assertEqual(len(items), 1)
        self.assertDictEqual(items[0], json.loads(body_members))

        # Check requests
        requests = httpretty.latest_requests()

        expected_requests = [
            {
                "body": "",
                "querystring": {'access_token': ['wrong_token'], 'order': ['last_edited'],
                            'page': ['1'], 'per_page': ['100']},
                "method": 'GET',
                "url": OPENINFRA_PRIVATE_MEMBERS_URL
            },
            {
                "body": {'client_id': ['id_test'], 'client_secret': ['secret_test']},
                "querystring": {'grant_type': ['client_credentials'],
                            'scope': ['https://openstackid-resources.openstack.org/members/read']},
                "method": 'POST',
                "url": "https://id.openinfra.dev/oauth2/token"
            },
            {
                "body": {'client_id': ['id_test'], 'client_secret': ['secret_test']},
                "querystring": {'grant_type': ['client_credentials'],
                            'scope': ['https://openstackid-resources.openstack.org/members/read']},
                "method": 'POST',
                "url": "https://id.openinfra.dev/oauth2/token"
            },
            {
                "body": "",
                "querystring": {'access_token': ['test_token'], 'order': ['last_edited'],
                                'page': ['1'], 'per_page': ['100']},
                "method": 'GET',
                "url": OPENINFRA_PRIVATE_MEMBERS_URL
            }
        ]
        self.assertEqual(len(requests), 4)
        for i, req in enumerate(requests):
            self.assertDictEqual(req.querystring, expected_requests[i]["querystring"])
            self.assertEqual(req.url.split('?')[0], expected_requests[i]["url"])
            self.assertEqual(req.parsed_body, expected_requests[i]["body"])
            self.assertEqual(req.method, expected_requests[i]["method"])

    @httpretty.activate
    def test_fetch_individuals(self):
        """Test fetch_individuals returns individuals"""

        # Set up a mock HTTP server
        requests, bodies = setup_mock_server(public=True)

        # Run fetch individuals
        parser = OpenInfraIDParser(OPENINFRA_URL)
        individuals = [indiv for indiv in parser.individuals()]

        # Not all individuals have valid information (name or GitHub username)
        self.assertEqual(len(individuals), 5)

        indiv = individuals[0]
        self.assertEqual(indiv.uuid, 136832)
        self.assertEqual(indiv.profile.name, "name surname")
        self.assertEqual(indiv.profile.email, None)
        self.assertEqual(indiv.profile.is_bot, False)
        self.assertEqual(indiv.identities[0].source, "openinfra")
        self.assertEqual(indiv.identities[0].name, "name surname")
        self.assertEqual(indiv.identities[0].email, None)
        self.assertEqual(indiv.identities[0].username, "136832")
        self.assertEqual(indiv.identities[1].source, "github")
        self.assertEqual(indiv.identities[1].name, "name surname")
        self.assertEqual(indiv.identities[1].username, "random-gh-user")
        self.assertEqual(indiv.enrollments[0].organization.name, "MyCompany")

        indiv = individuals[1]
        self.assertEqual(indiv.uuid, 136853)
        self.assertEqual(indiv.profile.name, None)
        self.assertEqual(indiv.profile.email, None)
        self.assertEqual(indiv.profile.is_bot, False)
        self.assertEqual(indiv.identities[0].source, "github")
        self.assertEqual(indiv.identities[0].name, None)
        self.assertEqual(indiv.identities[0].email, None)
        self.assertEqual(indiv.identities[0].username, "random-gh-user-2")

        indiv = individuals[2]
        self.assertEqual(indiv.uuid, 125525)
        self.assertEqual(indiv.profile.name, "name_3 last_name_3")
        self.assertEqual(indiv.profile.email, None)
        self.assertEqual(indiv.profile.gender, None)
        self.assertEqual(indiv.identities[0].source, "openinfra")
        self.assertEqual(indiv.identities[0].name, "name_3 last_name_3")
        self.assertEqual(indiv.identities[0].email, None)
        self.assertEqual(indiv.identities[0].username, "125525")
        self.assertEqual(indiv.enrollments[0].start,
                         datetime.datetime(2020, 9, 1, tzinfo=tzutc()))
        self.assertEqual(indiv.enrollments[0].end, None)
        self.assertEqual(indiv.enrollments[0].organization.name, "Technology Org")

        # Check requests
        expected_qs = [
            {
                'page': ['1'],
                'per_page': ['100'],
                'order': ['last_edited']
            },
            {
                'page': ['2'],
                'per_page': ['100'],
                'order': ['last_edited']
            }
        ]
        self.assertEqual(len(requests), 2)
        for i, req in enumerate(requests):
            self.assertDictEqual(req.querystring, expected_qs[i])
            self.assertEqual(req.url.split('?')[0], OPENINFRA_PUBLIC_MEMBERS_URL)

    @httpretty.activate
    @override_settings(OPENINFRA_CLIENT_ID='id_test', OPENINFRA_CLIENT_SECRET='secret_test')
    def test_fetch_private_individuals(self):
        """Test fetch_individuals returns individuals"""

        # Set up a mock HTTP server
        requests, bodies = setup_mock_server(public=False)

        httpretty.register_uri(
            httpretty.POST,
            OpenInfraIDParser.OPENINFRA_TOKEN_URL,
            body='{"access_token":"test_token","expires_in":7200,"token_type":"Bearer"}',
            status=200
        )

        # Run fetch individuals
        parser = OpenInfraIDParser(OPENINFRA_URL)
        individuals = [indiv for indiv in parser.individuals()]

        # Not all individuals have valid information (name or GitHub username)
        self.assertEqual(len(individuals), 3)

        indiv = individuals[0]
        self.assertEqual(indiv.uuid, 136832)
        self.assertEqual(indiv.profile.name, "name surname")
        self.assertEqual(indiv.profile.email, "email_1@example.com")
        self.assertEqual(indiv.profile.is_bot, False)
        self.assertEqual(len(indiv.identities), 2)
        self.assertEqual(indiv.identities[0].source, "openinfra")
        self.assertEqual(indiv.identities[0].name, "name surname")
        self.assertEqual(indiv.identities[0].email, "email_1@example.com")
        self.assertEqual(indiv.identities[0].username, "136832")
        self.assertEqual(indiv.identities[1].source, "github")
        self.assertEqual(indiv.identities[1].name, "name surname")
        self.assertEqual(indiv.identities[1].email, "email_1@example.com")
        self.assertEqual(indiv.identities[1].username, "random-gh-user")

        indiv = individuals[1]
        self.assertEqual(indiv.uuid, 136853)
        self.assertEqual(indiv.profile.name, None)
        self.assertEqual(indiv.profile.email, "email_2@example.com")
        self.assertEqual(indiv.profile.is_bot, False)
        self.assertEqual(len(indiv.identities), 4)
        self.assertEqual(indiv.identities[0].source, "openinfra")
        self.assertEqual(indiv.identities[0].name, None)
        self.assertEqual(indiv.identities[0].email, "email_2@example.com")
        self.assertEqual(indiv.identities[0].username, "136853")
        self.assertEqual(indiv.identities[1].source, "openinfra")
        self.assertEqual(indiv.identities[1].name, None)
        self.assertEqual(indiv.identities[1].email, "email_2b@example.com")
        self.assertEqual(indiv.identities[1].username, "136853")
        self.assertEqual(indiv.identities[2].source, "openinfra")
        self.assertEqual(indiv.identities[2].name, None)
        self.assertEqual(indiv.identities[2].email, "email_2c@example.com")
        self.assertEqual(indiv.identities[2].username, "136853")
        self.assertEqual(indiv.identities[3].source, "github")
        self.assertEqual(indiv.identities[3].name, None)
        self.assertEqual(indiv.identities[3].email, "email_2@example.com")
        self.assertEqual(indiv.identities[3].username, "random-gh-user-2")

        indiv = individuals[2]
        self.assertEqual(indiv.uuid, 125525)
        self.assertEqual(indiv.profile.name, "name_3 last_name_3")
        self.assertEqual(indiv.profile.email, "email_3@example.com")
        self.assertEqual(indiv.profile.gender, None)
        self.assertEqual(len(indiv.identities), 1)
        self.assertEqual(indiv.identities[0].source, "openinfra")
        self.assertEqual(indiv.identities[0].name, "name_3 last_name_3")
        self.assertEqual(indiv.identities[0].email, "email_3@example.com")
        self.assertEqual(indiv.identities[0].username, "125525")
        self.assertEqual(indiv.enrollments[0].start,
                         datetime.datetime(2020, 9, 1, tzinfo=tzutc()))
        self.assertEqual(indiv.enrollments[0].end, None)
        self.assertEqual(indiv.enrollments[0].organization.name, "Technology Org")

        # Check requests
        expected_qs = [
            {
                'page': ['1'],
                'per_page': ['100'],
                'order': ['last_edited'],
                'access_token': ['test_token']
            }
        ]
        self.assertEqual(len(requests), 1)
        for i, req in enumerate(requests):
            self.assertDictEqual(req.querystring, expected_qs[i])
            self.assertEqual(req.url.split('?')[0], OPENINFRA_PRIVATE_MEMBERS_URL)
