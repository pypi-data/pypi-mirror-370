# 🧰 drq – 多功能娱乐工具箱

> “小而常新” 的 Python 小玩具合集：文艺句子、毒鸡汤、成语接龙、天气查询、小游戏…… 一行命令即可拥有全部乐趣！

## 🚀 安装
```bash
pip install drq
```

## 使用方法
```python
import drq

# 帮助
drq.help()

# 随机一句文艺句子
print(drq.get_sentence())

# 成语接龙
print(drq.idiom_chain("画龙点睛"))

# 查天气
print(drq.weather("上海"))

# 随机废话(彩蛋)
print(drq.nonsense())

# 父母性别查询器(彩蛋)
drq.p_x()
```

## 许可证
[MIT](./LICENSE)