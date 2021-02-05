from structures import ApiTestCase


class LoginTest(ApiTestCase):
    def test_login(self):
        response = self.login('user123@gmail.com', 'pass123')
        self.assert200(response)
        self.assertEqual(response.json.get('email'), 'user123@gmail.com')

    def test_missing_credentials(self):
        response = self.client.post('/login')
        self.assert400(response)

    def test_invalid_header(self):
        response = self.login('user123@gmail.com')
        self.assert400(response)

    def test_invalid_credentials(self):
        response = self.login('user123@gmail.com', 'secret456')
        self.assert401(response)

    def test_user_not_found(self):
        response = self.login('user234@gmail.com', 'pass123')
        self.assert404(response)

