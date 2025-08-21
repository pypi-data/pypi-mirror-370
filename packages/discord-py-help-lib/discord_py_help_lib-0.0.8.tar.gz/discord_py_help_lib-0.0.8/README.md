# help for discord.py Library

![PyPI version](https://img.shields.io/pypi/v/discord-py-help-lib.svg)
![Python version](https://img.shields.io/pypi/pyversions/discord-py-help-lib.svg)
![License](https://img.shields.io/pypi/l/discord-py-help-lib.svg)

---

## 📦 概要

`discord-py-help-lib` は、discord.pyで役職パネルを簡単に実装するための Python ライブラリです。

主な機能は以下のとおりです：

- 後日更新

---

## ✨ 特徴

- ✅ 簡単に使用が可能

---

## 🔧 インストール

### PyPIからインストール：
```bash
pip install discord-py-help-lib
```
### githubからインストール：
```bash
pip install git+https://github.com/hashimotok-ecsv/discord_py_help_lib.git
```
## 使い方
```python
# 後日更新
```
## 管理者用
### 更新方法
```bash
Remove-Item -Recurse -Force .\dist\
py setup.py sdist
py setup.py bdist_wheel
py -m twine upload --repository testpypi dist/*
py -m twine upload --repository pypi dist/*
```