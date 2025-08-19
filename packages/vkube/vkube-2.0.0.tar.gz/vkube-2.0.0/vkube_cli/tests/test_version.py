import unittest
from vkube_cli.utils.version import check_version
class TestVersion(unittest.TestCase):
    def test_suitable_version(self):
        """test a valid string"""
        curVersion = "1.2.4"
        self.assertTrue(check_version(curVersion),"The vkube-cli version must be greater than minimum need version")
    def test_unsuitable_version(self):
        curVersion = "1.0.4"
        self.assertFalse(check_version(curVersion),"Your vkube-cli version is valid")
    
if __name__ == "__main__":
    unittest.main()