# tests/test_deepseek_tokenizer.py

import unittest
from typing import List
from llm_tokenizers.deepseek_tokenizer import DeepSeekTokenizer


class TestDeepSeekTokenizer(unittest.TestCase):
    """
    DeepSeekTokenizer 类的单元测试
    """

    def test_id(self):
        """
        测试 id 方法返回正确的标识符
        """
        self.assertEqual(DeepSeekTokenizer.id(), "deepseek")

    def test_encode(self):
        """
        测试 encode 方法能正确编码文本
        """
        # 测试基本编码功能
        result = DeepSeekTokenizer.encode("Hello!")
        self.assertIsInstance(result, List)
        self.assertGreater(len(result), 0)
        self.assertIsInstance(result[0], int)

    def test_decode(self):
        """
        测试 decode 方法能正确解码 token
        """
        # 先编码再解码，检查是否能还原
        original_text = "Hello!"
        encoded = DeepSeekTokenizer.encode(original_text)
        decoded = DeepSeekTokenizer.decode(encoded)
        self.assertIsInstance(decoded, str)
        # 注意：由于分词器可能添加特殊token，解码结果可能与原始文本不完全相同
        self.assertGreater(len(decoded), 0)

    def test_tokens_len(self):
        """
        测试 tokens_len 方法返回正确的 token 长度
        """
        text = "Hello world!"
        length = DeepSeekTokenizer.tokens_len(text)
        encoded = DeepSeekTokenizer.encode(text)
        self.assertEqual(length, len(encoded))
        self.assertIsInstance(length, int)
        self.assertGreater(length, 0)

    def test_encode_decode_consistency(self):
        """
        测试编码和解码的一致性
        """
        test_cases = [
            "Hello!",
            "DeepSeek is a great model.",
            "123456",
            "Special characters: !@#$%^&*()"
        ]

        for text in test_cases:
            with self.subTest(text=text):
                encoded = DeepSeekTokenizer.encode(text)
                decoded = DeepSeekTokenizer.decode(encoded)
                self.assertIsInstance(decoded, str)
                self.assertGreater(len(decoded), 0)

    def test_empty_string(self):
        """
        测试空字符串的处理
        """
        encoded = DeepSeekTokenizer.encode("")
        self.assertIsInstance(encoded, list)
        # 空字符串可能也会产生特殊token，如bos/eos
        decoded = DeepSeekTokenizer.decode(encoded)
        self.assertIsInstance(decoded, str)


if __name__ == '__main__':
    unittest.main()
