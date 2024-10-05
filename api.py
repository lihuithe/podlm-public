import uuid
import json
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil

app = FastAPI()

class TaskCreate(BaseModel):
    url: str

class Task(BaseModel):
    taskId: str
    url: str
    status: str
    progress: str
    createdAt: str
    updatedAt: str
    audioUrl: Optional[str] = None
    title: Optional[str] = None
    dialogue: Optional[List[dict]] = None
    status_details: Optional[dict] = None

def log(message):
    print(f"[{datetime.now().isoformat()}] [API] {message}")

def read_tasks():
    try:
        with open('task_list.json', 'r') as f:
            content = f.read()
            if not content:
                return []
            return json.loads(content)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        log("task_list.json 文件格式错误，重置为空列表")
        return []

def write_tasks(tasks):
    with open('task_list.json', 'w') as f:
        json.dump(tasks, f)

@app.post("/post_task")
async def post_task(task: TaskCreate):
    log(f"收到新任务请求: {task.url}")
    task_id = str(uuid.uuid4())
    log(f"生成任务ID: {task_id}")
    
    # 创建任务文件夹
    os.makedirs(task_id, exist_ok=True)
    log(f"创建任务文件夹: {task_id}")
    
    # 添加任务到 task_list.json
    new_task = Task(
        taskId=task_id,
        url=task.url,
        status="pending",
        progress="等待处理",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    )
    
    tasks = read_tasks()
    tasks.append(new_task.dict())
    write_tasks(tasks)
    log(f"成功将新任务添加到 task_list.json")
    
    log(f"任务创建成功，返回任务ID: {task_id}")
    return {"taskId": task_id}

@app.get("/get_task")
async def get_task(taskId: str):
    log(f"收到获取任务状态请求，任务ID: {taskId}")
    tasks = read_tasks()
    
    task = next((t for t in tasks if t['taskId'] == taskId), None)
    
    if not task:
        log(f"未找到任务，任务ID: {taskId}")
        raise HTTPException(status_code=404, detail="Task not found")
    
    log(f"找到任务，任务ID: {taskId}")
    wav_file = os.path.join(taskId, f"{taskId}.wav")
    if os.path.exists(wav_file):
        log(f"音频文件已存在，任务ID: {taskId}")
        task['status'] = 'completed'
        task['audioUrl'] = f"/audio/{taskId}/{taskId}.wav"
    else:
        log(f"音频文件不存在，任务ID: {taskId}")
    
    # 检查并读取title.txt文件
    title_file = os.path.join(taskId, "title.txt")
    if os.path.exists(title_file):
        with open(title_file, 'r', encoding='utf-8') as f:
            task['title'] = f.read().strip()
    else:
        task['title'] = None
    
    # 检查并读取dialogue.json文件
    dialogue_file = os.path.join(taskId, "dialogue.json")
    if os.path.exists(dialogue_file):
        with open(dialogue_file, 'r', encoding='utf-8') as f:
            task['dialogue'] = json.load(f)
    else:
        task['dialogue'] = None
    
    # 检查并读取status.json文件
    status_file = os.path.join(taskId, "status.json")
    if os.path.exists(status_file):
        with open(status_file, 'r', encoding='utf-8') as f:
            task['status_details'] = json.load(f)
    else:
        task['status_details'] = None
    
    log(f"返回任务信息，任务ID: {taskId}")
    return Task(**task)

@app.get("/get_list")
async def get_list():
    log("收到获取已完成任务列表请求")
    tasks = read_tasks()
    
    completed_tasks = []
    for task in reversed(tasks):
        if task['status'] == 'completed':
            # 检查并读取title.txt文件
            title_file = os.path.join(task['taskId'], "title.txt")
            if os.path.exists(title_file):
                with open(title_file, 'r', encoding='utf-8') as f:
                    task['title'] = f.read().strip()
            else:
                task['title'] = None
            
            # 检查并读取dialogue.json文件
            dialogue_file = os.path.join(task['taskId'], "dialogue.json")
            if os.path.exists(dialogue_file):
                with open(dialogue_file, 'r', encoding='utf-8') as f:
                    task['dialogue'] = json.load(f)
            else:
                task['dialogue'] = None
            
            # 检查音频文件是否存在
            wav_file = os.path.join(task['taskId'], f"{task['taskId']}.wav")
            if os.path.exists(wav_file):
                task['audioUrl'] = f"/audio/{task['taskId']}/{task['taskId']}.wav"
            else:
                task['audioUrl'] = None
            
            completed_tasks.append(Task(**task))
    
    log(f"返回已完成任务列表，共 {len(completed_tasks)} 个任务")
    return completed_tasks

@app.get("/audio/{taskId}/{filename}")
async def get_audio(taskId: str, filename: str):
    log(f"收到获取音频文件请求，任务ID: {taskId}，文件名: {filename}")
    file_path = os.path.join(taskId, filename)
    if not os.path.exists(file_path):
        log(f"音频文件不存在，路径: {file_path}")
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path)

@app.get("/")
async def root():
    log("收到根路由请求，返回 index.html")
    return FileResponse("index.html")

@app.get("/list.html")
async def list_html():
    log("收到 list.html 请求，返回 list.html")
    return FileResponse("list.html")

@app.get("/resources/{file_path:path}")
async def serve_static(file_path: str):
    log(f"收到静态资源请求，文件路径: {file_path}")
    static_dir = "resources"
    full_path = os.path.join(static_dir, file_path)
    if not os.path.exists(full_path):
        log(f"静态资源文件不存在，路径: {full_path}")
        raise HTTPException(status_code=404, detail="静态资源文件未找到")
    return FileResponse(full_path)

from fastapi.staticfiles import StaticFiles
# 将静态资源目录挂载到应用
app.mount("/resources", StaticFiles(directory="resources"), name="resources")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，您可以根据需要限制
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

@app.delete("/delete_task/{taskId}")
async def delete_task(taskId: str):
    log(f"收到删除任务请求，任务ID: {taskId}")
    tasks = read_tasks()
    
    # 从任务列表中删除任务
    tasks = [t for t in tasks if t['taskId'] != taskId]
    write_tasks(tasks)
    
    # 删除任务目录
    task_dir = os.path.join(os.getcwd(), taskId)
    if os.path.exists(task_dir):
        shutil.rmtree(task_dir)
        log(f"已删除任务目录: {task_dir}")
    
    log(f"成功删除任务，任务ID: {taskId}")
    return {"message": "任务已成功删除"}

@app.get("/del.html")
async def manage_html():
    log("收到 del.html 请求，返回 del.html")
    return FileResponse("del.html")

if __name__ == '__main__':
    import uvicorn
    log("启动 API 服务器...")
    uvicorn.run(app, host="0.0.0.0", port=8811)
