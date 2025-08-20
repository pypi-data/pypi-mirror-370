import argparse
import sys
import requests

from llm_tokenizers.deepseek_tokenizer import DeepSeekTokenizer
from typing import List, Optional
from argparse import Namespace


def main():
    # 加载tokenizer
    tokenizers: dict = {DeepSeekTokenizer.id(): DeepSeekTokenizer}

    # 分析参数
    parser = argparse.ArgumentParser(description='Some llm tokenizers.')

    # 参数：模型类型
    parser.add_argument('-t', '--tokenizer',
                        type=str, help='enter llm\'s name', choices=tokenizers, default='deepseek')

    # 参数：输入的文件路径 -f
    parser.add_argument('-f', '--file', type=str, help='enter file path')

    # 参数：url 路径 -u
    parser.add_argument('-u', '--url', type=str, help='enter url path')

    # 参数：输出路径 -o
    parser.add_argument('-o', '--output', type=str, help='enter output path')

    # 参数：进行tocker长度统计并返回长度 -c
    parser.add_argument('-c', '--count', action='store_true', help='count tokens')

    # 参数: 指定需要处理的文本作为参数 -i
    parser.add_argument('-i', '--input', type=str, help='enter input text')

    # 参数：指定读取的字符集 --read-charset
    parser.add_argument('--read-charset', type=str, help='enter read charset', default='utf-8')

    parsed_args: Namespace = Optional[Namespace]

    try:
        # 解析传入的参数
        parsed_args = parser.parse_args(args=sys.argv[1:])
    except SystemExit:  # 防止argparse自动退出
        print("parameters error")
        exit(1)
    
    input_text: str = ""

    # 如果指定 -i 则优先使用
    if parsed_args.input:
        input_text = parsed_args.input

    # 如果指定 -f 则优先使用
    elif parsed_args.file:
        with open(parsed_args.file, 'r', encoding=parsed_args.read_charset) as f:
            input_text = f.read()

    # 如果指定 -u 则使用 http 请求获取相应的资源内容
    elif parsed_args.url:
        response = requests.get(parsed_args.url)
        input_text = response.text
    else:
        print("please enter input text or file path or url")
        exit(1)

    # 根据指定的tokenizer进行tokenize
    tokenizer = tokenizers[parsed_args.tokenizer]
    output_text: list[int] = tokenizer.encode(input_text)

    # 如果是进行tokenizer计数
    if parsed_args.count:

        # 使用千分位表示长度数值
        print(f"tokens count: {len(output_text):,}")
    else:
        # 如果指定 -o 则输出到文件
        if parsed_args.output:
            with open(parsed_args.output, 'w', encoding=parsed_args.read_charset) as f:
                f.write(str(output_text))
        else:
            print(output_text)


if __name__ == "__main__":

    main()
