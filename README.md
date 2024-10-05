# 项目名称

URL-to-播客-to-小宇宙

中文版NotebookLM 最好用的平替

## 项目简介

把任意url转成播客，然后推送到小宇宙平台

## 体验地址

http://podlm.ai/

http://boke.tingwu.co/

## 文件结构

项目主要包含以下文件:

- `server.py`: 合成任务后端服务，长时间运行多线程执行合成任务
- `server_pro.py`: 所有功能与server.py一致，但多了小宇宙自动发布逻辑
- `api.py`: web及api等服务实现，需要长时间运行
- `task_list.json`: 用于储存所有合成记录
- `del.html`: 删除合成记录ui
- `list.html`: 所有合成记录ui
- `index.html`: 首页ui
- `resources`: 资源文件夹，包含css和js

## 安装和运行

1. 确保您的系统已安装 Python (推荐使用 Python 3.11.5 版本)。
2. 克隆或下载本项目到本地。
3. 在命令行中进入项目目录。
4. 运行以下命令启动程序:

   ```python
   python api.py
   python server_pro.py # 或者 server.py 差异在于server_pro.py多了小宇宙自动发布逻辑
   ```

## 访问

访问 http://127.0.0.1:8811/ 首页

访问 http://127.0.0.1:8811/list.html 所有合成记录

访问 http://127.0.0.1:8811/del.html 可以删除合成记录

## 大语言模型配置

server.py 和 server_pro.py 中的llm需要配置自己的

有3处

api_url = ''

api_key = ''

请自行查找替换

## TTS服务配置

server_pro.py 第330行

server.py 第169行

url = f"http://abc.com/tts?text={text}&language=中英混合&anchor_type={anchor_type}"

abc.com 请替换为您的TTS服务地址


## 联系方式

妙云 ceo@tingwu.co https://tingwu.co