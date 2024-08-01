# Bili Dynamic Spy
一个简易B站动态爬虫.
爬取用户动态, 并解析动态内容. 为后续数据分析提供基础服务.
感谢 [bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect) 收集整理的API.

## 功能
- [x] 爬取用户动态
- [ ] 解析动态内容
    - [x] 发布时间
    - [x] 动态类型
    - [x] 动态Plain Text内容
    - [x] 动态为转发/更新投稿
    - [x] 转发/投稿的引用主体类型
    - [ ] 转发/投稿的引用主体源标题(仍有Bug)
- [x] 保存动态内容到本地`.csv`文件
- [ ] 更多数据清洗与处理

## 使用方法
1. 创建并激活依赖环境
```
conda create --name <env> --file requirements.txt
conda activate <env>
```

2. 配置文件
```
cp config.example.json config.json
```
修改 `config.json` 中的配置信息
- `tar_uid` 是要爬取动态的用户UID.
- `crawl_deepth` 是爬取动态的深度，即爬取多少页动态, 应是一个整数.
- `cookies` 是登录 B 站后获取的 cookies. 其中包含了 `buvid3` `b_nut` `_uuid` `buvid4`.

3. 运行程序
```
python main.py
```

## 注意事项
- 脚本会自动保存动态内容到`./saved/xxx的成分表.csv`，日期格式为 `YYYY-MM-DD hh:mm:ss`。
- 由于B站动态页面采用懒加载技术, 所以需要在配置文件中指定允许懒加载的次数, 默认为10次.
- **请勿滥用, 本项目仅用于学习和测试! 请勿滥用, 本项目仅用于学习和测试! 请勿滥用, 本项目仅用于学习和测试!**
- **尽管已经主动降低爬取频率, 但是**<span style="color: red; font-weight: bold;">仍然无法保证使用本脚本不会导致B站账号被限制</span>.