import unittest
from vkube_cli.utils.image import check_single_image, check_images_exist
DOCKER_TOKEN = "" # your dockerhub docker PAT
GITHUB_TOKEN = "" # your github PAT
class TestImageIntegration(unittest.TestCase):
    def setUp(self):
        # 设置测试环境
        self.tokens = {
            "docker": DOCKER_TOKEN,
            "ghcr": GITHUB_TOKEN
        }
        
    def test_real_docker_image_exists(self):
        """测试 Docker Hub 上确实存在的镜像"""
        image_path = "nginx:1.27.5"
        result, exists, error = check_single_image(image_path,self.tokens)
        self.assertTrue(exists)
        self.assertNotEqual(result,"")
        self.assertEqual(error, "")

    def test_real_docker_image_not_exists(self):
        """测试 Docker Hub 上不存在的镜像"""
        image_path = "nonexistent/nonexistent:latest"
        result, exists, error = check_single_image(image_path,self.tokens)
        self.assertFalse(exists)
        self.assertNotEqual(result,"")
        self.assertNotEqual(error,"")


    def test_real_ghcr_image_exists(self):
        """测试 GHCR 上的镜像（需要 GITHUB_TOKEN）"""
        
        # 替换为实际存在的 GHCR 镜像
        image_path = "ghcr.io/certram/redis:7.0.13"
        result, exists, error = check_single_image(image_path, self.tokens)
        # 根据实际情况断言
        self.assertEqual(error,"")
        self.assertNotEqual(result,"")
        self.assertTrue(exists)

    def test_multiple_real_images(self):
        """test multiple images"""
        tokens = self.tokens
        exist_image_list= [
            "mysql:5.7",
            "nginx:1.27.5",
            "nginx:latest",
            "redis:alpine",
            "ghcr.io/certram/redis:7.0.13" # exist
        ]
        not_exist_image_list= [
            "ghcr.io/certram/redis:9.1.13" # exist
        ]
        exist_results = check_images_exist(exist_image_list, tokens)
        for image_path, (exists, error) in exist_results.items():
            self.assertTrue(exists, f"Image {image_path} should exist")
            self.assertEqual(error, "")
        not_exist_results = check_images_exist(not_exist_image_list, tokens)
        for image_path, (exists, error) in not_exist_results.items():
            self.assertFalse(exists, f"Image {image_path} should not exist")
            self.assertNotEqual(error, "")
        

if __name__ == '__main__':
    unittest.main()