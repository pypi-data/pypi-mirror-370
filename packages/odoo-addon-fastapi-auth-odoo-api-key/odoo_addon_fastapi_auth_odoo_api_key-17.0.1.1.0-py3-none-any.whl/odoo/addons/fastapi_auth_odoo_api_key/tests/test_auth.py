# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from fastapi.exceptions import HTTPException

from odoo.tests.common import TransactionCase

from ..dependencies import apikey_authenticated_partner_impl


class Te(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.api_user = cls.env.ref("base.user_demo")
        cls.not_auth_user = cls.env["res.users"].create(
            {
                "name": "Test",
                "login": "test",
            }
        )
        cls.demo_endpoint = cls.env["fastapi.endpoint"].create(
            {
                "name": "Test Enpoint",
                "app": "demo",
                "root_path": "/test",
                "demo_auth_method": "api_key",
                "user_id": cls.api_user.id,
            }
        )
        cls.scope1 = "fastapi"
        cls.scope2 = "bad scope"
        cls.apikey1 = (
            cls.env["res.users.apikeys"]
            .with_user(cls.api_user)
            ._generate(cls.scope1, "APIKEY NAME")
        )
        cls.apikey2 = (
            cls.env["res.users.apikeys"]
            .with_user(cls.api_user)
            ._generate(cls.scope2, "APIKEY NAME")
        )

    def test_ok(self):
        partner = apikey_authenticated_partner_impl(
            self.apikey1, self.env, self.demo_endpoint
        )
        self.assertEqual(partner, self.api_user.partner_id)

    def test_apikey_error(self):
        with self.assertRaises(HTTPException):
            apikey_authenticated_partner_impl(
                "BAD APIKEY", self.env, self.demo_endpoint
            )

    def test_scope_error(self):
        with self.assertRaises(HTTPException):
            apikey_authenticated_partner_impl(
                self.apikey2, self.env, self.demo_endpoint
            )
