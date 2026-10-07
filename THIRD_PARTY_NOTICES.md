# 第三方来源

## 随Python包分发

颜文字来自 [kaomojiya-collection/kaomoji-collection](https://github.com/kaomojiya-collection/kaomoji-collection)，固定提交 `2ca1b394345a437bbec9e9b9445d1dd75ae3f7d4`。MIT全文保存在 `kaomoji_reply/data/LICENSE-kaomoji-collection.txt`。筛选和来源记录在词库JSON；项目许可证不替代第三方版权声明。

网络替换语使用固定小词表，来源链接见 `style_bank.json`。其中 `original` 是早期人工挑选表达的来源标记，不包含原始图片或完整聊天语料，也不证明作者风格相似度。

## 用户另行安装，不随包分发

- [Qwen3-1.7B-GGUF](https://huggingface.co/Qwen/Qwen3-1.7B-GGUF)：生成模型，使用时查看模型许可证。
- [llama.cpp](https://github.com/ggml-org/llama.cpp)：推理工具，下载的组件保留其许可文件。
- [jieba](https://github.com/fxsjy/jieba)：可选分词依赖，通过pip安装，不复制完整源码进发布包。
