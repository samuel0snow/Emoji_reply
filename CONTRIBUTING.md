# 开发指南

Python 3.10+。规则测试不需要模型、GPU或网络。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[slang]"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

修改回应时检查：角色是否正确、是否新增未知事实、补充问题是否必要、表情是否符合语气。添加合成案例到 `examples/`，不要提交真实聊天、私人图片、权重或完整日志。新增第三方数据需标明来源和许可证。

密度与词库修改须保留每段至少一个颜文字、已有表情不重复追加、引用和数字不被改写的行为。

构建wheel：

```powershell
.\.venv\Scripts\python.exe -m pip install wheel
.\.venv\Scripts\python.exe -m pip wheel . --no-deps --no-build-isolation --wheel-dir dist
```

发布前确认wheel含词库和第三方许可证，不含模型、环境和私人资料。完整模型实测按 `docs/setup.md` 准备依赖。CI只跑规则测试，不把它当成生成质量保证。
