# YUT-轻量GUI应用系统框架库
YUT是一个用于构建简单的GUI应用系统的轻量框架库，可以实现基于数据库的两层架构的应用系统。
## 介绍
1. 前端基于(Qt)PySide编写，包括GUI主窗口、导航框架、通用表单、列表、统计组件等；
2. 后端目前只实现了基于SqlAlchemy扩展的数据库组件。利用SqlAlchemy反射机制构建数据集，生成的数据集封装为Pandas Dataframe，并以JSON方式传递给GUI。可轻松扩展到任何web端框架。
3. 前后端使用统一的数据字段定义，在业务级别动态决定数据项的输入和展示方式，并允许开发者进一步控制细节。后端生成的Pandas Dataframe作为Model/View机制的基础，并在此基础上实现通用统计功能，包括分组统计、交叉统计，绘制相应的统计图表。
## 目录结构
```
yut-proj/
├── src/                        # 核心代码
├── examples/                   # 示例
├── example_package_yours/      # 完整的应用系统框架示例
└── templates/                  # 模板
```