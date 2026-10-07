# 流程与结果

`__main__.py` 校验输入并写入结果；`model.py` 管理本地服务与生成；`information.py` 评估信息并校正常见误判；`quality.py` 修正已知失败；`engine.py` 执行网络词替换、表情选择和密度限制。

场景 → 信息评估 → 生成或临时回应 → 正文检查 → 点缀 → 单独显示补充建议。

| JSON字段 | 含义 |
| --- | --- |
| `case` | 输入场景和名称 |
| `plain_reply` | 未点缀正文 |
| `decorated_reply` | 可复制的颜文字版本 |
| `information` | 状态、理由、补充建议和可选临时回应 |
| `faces`、`changes` | 改动及来源 |
| `metrics` | 数量、预算和最低数量兜底标记 |
| `placement_decisions` | 每句表达信号和位置判断 |
| `trace` | 原始生成与评估，以及质量修正 |
| `variants` | 开启四档对照后的版本 |

信息状态是sufficient、provisional或insufficient。建议给工具使用者，不应作为消息发送。临时回应不代表用户已决定态度。

`suppressed` 表示已有颜文字而不追加；`normal_placement_suppressed` 表示常规位置受限，最低数量仍可在严肃语境补中性表情。`plain_reply` 不承诺含表情，`decorated_reply` 才遵守最低数量。
