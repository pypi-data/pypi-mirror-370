# llm_tokenizers

Language: [English](https://gitee.com/sky_flash/llm_tokenizers/blob/master/README_en.md) [中文](README.md)

#### 介绍
收集llm的各种 tokenizer

#### 软件架构
软件架构说明


#### 项目安装教程

1.  克隆项目到本地：
```bash
git clone https://gitee.com/sky_flash/llm_tokenizers.git
``` 
2. 进入项目目录：
```bash
cd llm_tokenizers
```
3. 使用 pip 安装依赖：
```bash
pip install -r requirements.txt
```

#### 软件包安装程

#### 使用说明

1.  使用 pip 安装
```bash
pip install llm_tokenizers 
```

#### 项目打包

1.  确保已安装构建工具：
```bash
pip install build
```
 
2. 在项目根目录下执行打包命令：
```bash
python -m build
```
打包完成后，生成的 `.whl` 和 `.tar.gz` 文件会保存在 `dist/` 目录下。

3. 安装打包好的 `.whl` 文件（以生成的文件名为例）：
```bash
pip install dist/llm_tokenizers-0.1.0-py3-none-any.whl
```

#### API 调用说明

你可以通过导入 `DeepSeekTokenizer` 类来直接使用它提供的功能。以下是完整的使用教程。

```python
from llm_tokenizers.deepseek_tokenizer import DeepSeekTokenizer
```

##### 1. 获取 Tokenizer 标识

```python
print(DeepSeekTokenizer.id())  # 输出: deepseek
```


> `id()` 方法返回该 Tokenizer 的唯一标识符，可用于程序中识别当前使用的是哪个 Tokenizer。

---

##### 2. 编码文本为 token ID 列表

```python
text = "Hello, world!"
token_ids = DeepSeekTokenizer.encode(text)
print(token_ids)  # 输出: [列表形式的 token IDs]
```


> `encode(text: str) -> List[int]`  
> 将输入的字符串文本编码为对应的 token 编码列表。

---

##### 3. 解码 token ID 为原始文本

```python
decoded_text = DeepSeekTokenizer.decode(token_ids)
print(decoded_text)  # 输出: Hello, world!
```


> `decode(data: Union[int, List[int], np.ndarray, torch.Tensor, tf.Tensor]) -> str`  
> 支持多种数据类型输入，返回解码后的字符串。

---

##### 4. 统计 token 数量

```python
token_count = DeepSeekTokenizer.tokens_len(text)
print(f"Token count: {token_count}")  # 示例输出: Token count: 5
```


> `tokens_len(text: str)`  
> 返回输入文本被编码后的 token 数量。

---

##### ✅ 使用示例汇总

```python
from llm_tokenizers.deepseek_tokenizer import DeepSeekTokenizer

# 获取标识
print("Tokenizer ID:", DeepSeekTokenizer.id())

# 编码文本
text = "Hello, deepseek tokenizer!"
token_ids = DeepSeekTokenizer.encode(text)
print("Encoded tokens:", token_ids)

# 解码 token
decoded = DeepSeekTokenizer.decode(token_ids)
print("Decoded text:", decoded)

# 统计 token 数量
print("Token count:", DeepSeekTokenizer.tokens_len(text))
```
---

##### 📌 注意事项：

- `DeepSeekTokenizer` 是一个 **类方法驱动** 的工具类，所有方法均为 `@classmethod`，无需实例化即可调用。
- 依赖的 `transformers` 模型文件应放在 `resources/deepseek_tokenizer/` 目录下。
- 若使用 `np.ndarray`, `torch.Tensor`, `tf.Tensor` 类型的数据，需确保已安装对应库（如 `numpy`, `torch`, `tensorflow`）。


#### 命令行调用

在完成项目安装后，如 `whl`安装后，执行 `llm-token` 命令

```bash
llm-token [选项]
```
##### 命令行参数说明

| 参数 | 全称 | 说明 | 示例 |
|------|------|------|------|
| `-t` | `--tokenizer` | 指定要使用的 tokenizer 类型 | `llm-token -t deepseek -i "Hello"` |
| `-f` | `--file` | 指定输入文件路径 | `llm-token -f ./input.txt` |
| `-u` | `--url` | 指定输入 URL 路径 | `llm-token -u https://example.com/text` |
| `-o` | `--output` | 指定输出文件路径 | `llm-token -i "Hello" -o ./output.txt` |
| `-c` | `--count` | 统计 tokens 长度 | `llm-token -c -i "Hello world"` |
| `-i` | `--input` | 直接输入文本内容 | `llm-token -i "Hello world"` |
| `--read-charset` |  | 指定读取文件的字符集 | `llm-token -f ./input.txt --read-charset gbk` |

##### 使用示例

1. **直接输入文本进行编码**：
   ```bash
   llm-token -i "Hello, world!"
   ```
2. **统计文本的 token 数量**：
   ```bash
   llm-token -c -i "Hello, world!"
   # 输出示例: tokens count: 5
   ```
3. **从文件读取内容进行编码**：
   ```bash
   llm-token -f ./input.txt
   ```
4. **从 URL 获取内容进行编码**：
   ```bash
   llm-token -u https://example.com/sample.txt
   ```
5. **指定 tokenizer 类型**：
   ```bash
   llm-token -t deepseek -i "Hello, world!"
   ```
6. **将结果输出到文件**：
   ```bash
   llm-token -i "Hello, world!" -o ./encoded_output.txt
   ```
7. **指定文件读取字符集**：
   ```bash
   llm-token -f ./chinese_text.txt --read-charset gbk
   ```
##### 优先级说明

当同时指定多种输入方式时，程序按照以下优先级处理：
1. `-i` / `--input` (直接输入文本)
2. `-f` / `--file` (文件输入)
3. `-u` / `--url` (URL输入)

##### 注意事项

- 至少需要指定一种输入方式（`-i`、`-f` 或 `-u`）
- 使用 `-c` 参数时，只会输出 token 数量，不会输出编码结果
- 输出默认打印到控制台，使用 `-o` 参数可指定输出文件

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request