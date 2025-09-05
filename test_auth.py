import unittest
from app import app

class BasicAppTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SpamWatch AI', response.data)

    def test_tools_page(self):
        response = self.app.get('/tools')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Our Tools', response.data)

    def test_spam_text_get(self):
        response = self.app.get('/spam_text')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Spam Text Detection', response.data)

    def test_deepfake_image_get(self):
        response = self.app.get('/deepfake_image')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Deepfake Image Detection', response.data)

    def test_deepfake_video_get(self):
        response = self.app.get('/deepfake_video')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Deepfake Video Detection', response.data)

if __name__ == '__main__':
    unittest.main()
