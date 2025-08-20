from abc import ABC, abstractmethod
from typing import List, Union


class AbstractTokenizer(ABC):
    @abstractmethod
    def demo(self): pass

    @abstractmethod
    def encode(self, text: str) -> List[int]:
        """
        对文本内容进行编码
        :param text: 指定文本内容
        :return: 编码后的数组
        """
        pass

    @abstractmethod
    def decode(self, data: Union[int, List[int], "np.ndarray", "torch.Tensor", "tf.Tensor"]) -> str:
        """
        对数组内容进行解码
        :param data: 指定数组
        :return: 解码后的字符串
        """
        pass

    @abstractmethod
    def tokens_len(self, text: str):
        """
        :return: 返回token的长度
        """
        pass

    @abstractmethod
    def id(self) -> str:
        """
        :return: 返回大模型的编号
        """
        pass