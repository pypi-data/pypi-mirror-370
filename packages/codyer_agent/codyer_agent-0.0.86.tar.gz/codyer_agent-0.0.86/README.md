# codyer_agent
codyer agent

# 发布pip库
在 ～/.pypirc 中配置 username password 之后，poetry config http-basic.pypi __token__ {password}
```shell
poetry build -f sdist
poetry publish
```

# 测试
```shell
# 安装并行测试的插件: 使用进程并行，防止测试用例之间的影响
pip install pytest-xdist

cd test
pytest -s -v -n auto
```