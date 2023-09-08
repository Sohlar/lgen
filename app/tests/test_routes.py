import unittest
from flask import url_for
from app import create_app, db


class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_home_page(self):
        response = self.client.get(url_for("main.home"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome to the Home Page", response.data)


if __name__ == "__main__":
    unittest.main()
