import unittest
import base58
from vkube_cli.utils.decode import decode_token
class TestCrypto(unittest.TestCase):
    def test_valid_input(self):
        """test a valid string"""
        encoded = base58.b58encode(b"https://api.example.com:supersecretpassword").decode("utf-8")
        api_address, secret = decode_token(encoded)
        self.assertEqual(api_address, "https://api.example.com")
        self.assertEqual(secret, "supersecretpassword")
        real_example = "38KZHfS1S5CUr4WJshNJgCvRtmQhoWpdLhpMDhB2mgvqrJTxKpwuXvrEVafmPxfk6DmaDHHehqVFe8ysQ1Sh8NAeQQgJSddK5zbkbA7frDLCSDSqPcS7TCsVDEpvp8aUZU3aRW9Ys4z2Noj5sgHBqpqWh5ortmmWrifbWd8C1ygaHc7RYbxTg2G5dqgkmALxVXSAzFi95G4gcPzReBoUTgZ8CXXUVauJQuLgKbzvqyRkEVHkk9i1hiX7Q6oSJXkRpjrGaVKUYLhfoxBFtgtkX7H1hTqUC5uBjaSTnow5EwLajGFgpQa6nCFJx73YxwRKbhneimJQRxbyBXtBMGG8g9fKiwP8pmkN9Ct1UxFt2pRLzb61cebdJ8hkGbHaPkhNCqeZ7VetoKWz4Q"
        real_api,real_secret = decode_token(real_example)
        print(f'{real_api}:{real_secret}')
        self.assertEqual(real_api,"https://europe.test.vkube.vcloud.systems")
        self.assertEqual(real_secret,"LTdfqwRdHCKzwTMyZRVKHZVUNN5nqtJjoMZtgCkN6v97Ax8CZasjFhY9J5jxfLot2WWFu5yEbSKgUtAoWqA1CWKZ4n42Xi1UHSdpBy4JXrdFxpY6Z323GehfsGnWy8DFpq4yQ65EHNV1j5d7yutzkZm95hVnsRHSRFogzSHHqoDW8bCv3BX1nsc7nYspqxKH9c3EgXZWw1KsLMUhChhrsX2ZZ7UcLN1sDmiVeFJgZf3yS3oon7Avkc3h5q")
        local_example = "3dcmHFBAdLwk6Sc922SmHcaX5mVL2pw18j5oKUE2TiZtuF2U42QjK96cnrfq1g5bw8pLooS8ia8g18t76sV5hpe32xkHS6FS34d9ahcEM6gQjJ4C9JV8iCRAjDtr5mkS788jW6tPfb5KWqLRGFCAacGMdh6VuUBsG5dqZXT9uZNa8dSYwYWLB2SptvjwvD91FdYk6HCciQwUJJAm4pShLMHWfoNB1s4ym1oAZ7WTKSM4ayfCuiRzRvLnehfi8XkfU7f2hsFHi4yKcbPXrWLazZuiQYUR7Dh1gykP9Z7KjQFarCTw45dd6LCLBTPCQ2uSuXuWksnYmujFAB3dtaqywD1LxvhjZYbiKMSueF2vGyAqToqfc9cC"
        local_api,local_secret = decode_token(local_example)
        self.assertEqual(local_api,"http://localhost:3114")

    def test_missing_separator(self):
        """test a string without : delimiter"""
        encoded = base58.b58encode(b"https//api.example.com").decode("utf-8")
        with self.assertRaises(ValueError):
            decode_token(encoded)

    def test_empty_input(self):
        """test empty string"""
        with self.assertRaises(ValueError):
            decode_token("")

    def test_invalid_base58(self):
        """test invalid Base58 string"""
        invalid_encoded = "InvalidBase58@@@"
        with self.assertRaises(ValueError):
            decode_token(invalid_encoded)

    def test_non_utf8_decodable(self):
        """test can't be decoded byte content"""
        non_utf8_encoded = base58.b58encode(b"\xff\xff\xff").decode("utf-8")
        with self.assertRaises(UnicodeDecodeError):
            decode_token(non_utf8_encoded)
if __name__ == "__main__":
    unittest.main()