# Emoji Reply

输入需要回应的中文场景，生成可发送的回应，再按语气加入颜文字。关键背景不足时，先给保守的临时回应，随后单独建议用户补充信息。

```text
场景：有人约我出去，帮我回。
回应：谢谢邀请，我考虑一下再回复你。 (*´꒳`*)
补充建议：你想接受、婉拒，还是暂时待定？
```

目前是本地命令行原型，支持文字输入，不读取图片、不自动发送消息。小模型仍可能误解场景，生成结果供用户选择和修改。

## 功能

- 根据场景生成1—3句中文回应，区分朋友、同事和一般关系。
- 判断信息是否足够，最多给3项补充建议及其作用，建议不混入可发送正文。
- 每段点缀后的回应至少含一个颜文字，已有表情不重复追加。
- 四档密度和少量网络替换语，保护数字、引用和链接。
- 同一正文比较四档，JSON保留模型响应、规则修正和插入位置。

## 快速开始

需要 Python 3.10+。完整生成目前支持 **Windows 本地 llama.cpp**；包安装和规则测试不需要模型或GPU。在项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

按 [模型安装说明](docs/setup.md)准备模型与推理程序，再运行：

```powershell
.\.venv\Scripts\python.exe -m kaomoji_reply "有人约我出去，帮我回。"
```

安装后的命令行入口：

```powershell
.\.venv\Scripts\kaomoji-reply.exe "朋友感谢我帮忙，请回复。"
```

`requirements.txt` 安装项目本身和网络词替换所需的jieba，依赖版本统一维护在 `pyproject.toml`。如果不需要网络词替换，可以使用 `pip install .`，仍可生成回应和颜文字。模型权重和llama.cpp不属于Python依赖，需按上述说明单独准备。结果默认写入 `outputs/latest/结果.md` 和 `results.json`。程序启动本地服务，结束时关闭。

## 使用

```powershell
# 同一正文四档对照
.\.venv\Scripts\python.exe -m kaomoji_reply --batch examples/scenarios.json --all-densities
# UTF-8文件，同事关系
.\.venv\Scripts\python.exe -m kaomoji_reply --input scenario.txt --relationship colleague --density light
# 批量信息检查
.\.venv\Scripts\python.exe -m kaomoji_reply --batch examples/information_scenarios.json --output outputs/demo
```

输入方式三选一：位置参数、`--input` 或 `--batch`。批量JSON：

```json
[{"name":"回应邀请","context":"有人约我出去，帮我回。","relationship":"friend"}]
```

`relationship` 可省略，使用命令行设置，默认 `friend`。

| 参数 | 用途 |
| --- | --- |
| `--relationship friend/colleague/neutral` | 关系背景 |
| `--density none/light/medium/high` | 密度；`--strength`为兼容别名 |
| `--all-densities` | 同正文四档结果 |
| `--variant 2` | 同类表情备选序号，非负整数 |
| `--output outputs/latest` | 结果目录 |

### 密度

| 档位 | 新增表情上限 | 网络词替换上限 |
| --- | ---: | ---: |
| none 最少点缀 | 1 | 0 |
| light 轻点缀 | 1 | 1 |
| medium 适中 | 2 | 2 |
| high 活泼 | 3 | 3 |

每段回应至少含一个颜文字，包括临时回应。已有表情时不追加。无合适位置时在段末补一个：普通或待确认用微笑，安慰用温和支持表情，严肃提醒用中性表情 `(・_・)`。

上限受长度、关系和位置限制，短回应各档可能相同。同事或一般关系最多新增一个表情，不替换网络词。`none` 保留字词和换行，只补最低数量；`plain_reply` 始终保存未点缀正文。

### 补充建议

信息状态为 `sufficient`（足够）、`provisional`（可先保守回应）或 `insufficient`（缺少基本场景）。邀请态度不明时不替用户答应；明确说尚未确认有空时可以回应待确认，不反复追问。仅回应对方心情时不要求图片。用户补充后重新输入完整场景即可，目前没有多轮会话记忆。

## 结构与开发

```text
kaomoji_reply/     程序与小型词库
tests/            不需要模型的规则测试
examples/         合成场景JSON
docs/             安装、架构和实验结论
.github/          自动测试和问题模板
.local/           本地模型与工具，不发布
.venv/            本地Python环境，不发布
outputs/          运行时生成，不发布
```

见 [开发指南](CONTRIBUTING.md)、[架构与结果字段](docs/architecture.md)、[实验结论](docs/experiments.md)。

## 已知限制

小模型可能给出泛泛回应、混淆角色或新增事实。质量检查与信息判断是有限规则和模型结合，不能覆盖所有场景。没有可靠的风格相似度评分；密度控制数量，不代表回应质量等级。

## 许可证

原创代码采用 [MIT](LICENSE)。颜文字来自 [kaomoji-collection](https://github.com/kaomojiya-collection/kaomoji-collection)，其许可证单独保留。模型和推理程序不随Python包分发，见 [第三方声明](THIRD_PARTY_NOTICES.md)。
