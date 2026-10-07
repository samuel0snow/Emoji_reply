# 本地模型安装

完整生成目前支持Windows，使用llama.cpp Vulkan与Qwen3-1.7B Q8_0。包不含权重和推理工具。

1. 从 [llama.cpp Releases](https://github.com/ggml-org/llama.cpp/releases) 下载Windows Vulkan二进制，完整解压到 `.local/runtime/llama/`，保留DLL及许可文件。
2. 从 [Qwen官方仓库](https://huggingface.co/Qwen/Qwen3-1.7B-GGUF) 下载 `Qwen3-1.7B-Q8_0.gguf` 到 `.local/models/`。
3. 从项目根目录运行README中的命令。

```text
.local/
  models/Qwen3-1.7B-Q8_0.gguf
  runtime/llama/llama-server.exe
  runtime/llama/配套DLL和许可文件
```

验证过的版本是llama.cpp b11429，其他版本未逐一验证。模型约1.83GB，SHA256：

```text
061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a
```

可用 `Get-FileHash -Algorithm SHA256 .local/models/Qwen3-1.7B-Q8_0.gguf` 校验。程序不每次重复校验。

服务监听 `127.0.0.1:18770`，命令结束自动关闭。失败时查看 `outputs/server.log`，检查端口、DLL和Vulkan驱动。

从其他目录运行，设置本地资源根目录：

```powershell
$env:KAOMOJI_REPLY_HOME = "D:\path\to\Emoji_reply"
python -m kaomoji_reply "朋友说晚安，请回复。"
```

输入和输出相对路径仍相对于当前工作目录。移动项目后建议重建虚拟环境，避免旧启动器引用原路径。
