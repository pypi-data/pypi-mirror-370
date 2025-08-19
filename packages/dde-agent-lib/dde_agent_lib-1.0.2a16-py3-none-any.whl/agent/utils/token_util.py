from transformers import AutoTokenizer

# 全局变量：标识 tokenizer 是否已初始化，以及存储 tokenizer 实例
_tokenizer = None  # 存储 tokenizer 实例
_tokenizer_initialized = False  # 初始化状态标识（False：未初始化；True：已初始化）

def count_tokens(text, model_name="bert-base-uncased"):
    global _tokenizer, _tokenizer_initialized  # 声明使用全局变量

    # 仅在未初始化时执行一次 tokenizer 加载
    if not _tokenizer_initialized:
        try:
            # 首次调用时加载 tokenizer（从缓存或网络）
            _tokenizer = AutoTokenizer.from_pretrained(model_name)
            _tokenizer_initialized = True  # 标记为已初始化
            print("Tokenizer 初始化成功")
        except Exception as e:
            print(f"Tokenizer 初始化失败: {e}")
            raise  # 传递异常，避免后续调用出错

    # 复用已初始化的 tokenizer 进行编码
    encoded_input = _tokenizer(text, return_tensors="np")
    token_ids = encoded_input["input_ids"].squeeze().tolist()
    return len(token_ids)
