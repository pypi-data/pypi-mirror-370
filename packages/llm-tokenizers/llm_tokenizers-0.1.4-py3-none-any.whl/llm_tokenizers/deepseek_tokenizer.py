from typing import Union, List

import transformers
from importlib import resources

from llm_tokenizers.abstract_tokenizer import AbstractTokenizer

"""
DeepSeek Tokenizer 的工具类
"""
class DeepSeekTokenizer(AbstractTokenizer):

        with resources.path("llm_tokenizers.resources", "deepseek_tokenizer") as chat_tokenizer_dir:
                tokenizer = transformers.AutoTokenizer.from_pretrained(chat_tokenizer_dir, trust_remote_code=True)

        @classmethod
        def id(cls) -> str:
                return "deepseek"

        @classmethod
        def demo(cls):
                result: str = cls.tokenizer.encode("Hello!")
                print(result)

        @classmethod
        def encode(cls, text: str) -> List[int]:
                return cls.tokenizer.encode(text)

        @classmethod
        def decode(cls, data: Union[int, List[int], "np.ndarray", "torch.Tensor", "tf.Tensor"]) -> str:
                return cls.tokenizer.decode(data)

        @classmethod
        def tokens_len(cls, text: str):
                return len(cls.tokenizer.encode(text))

if __name__ == '__main__':
        DeepSeekTokenizer.demo()
