document.addEventListener('DOMContentLoaded', () => {
    fetchTasks();
});

async function fetchTasks() {
    try {
        const response = await fetch('/get_list');
        const tasks = await response.json();
        displayTasks(tasks);
    } catch (error) {
        console.error('获取任务列表失败:', error);
    }
}

function displayTasks(tasks) {
    const taskList = document.getElementById('taskList');
    taskList.innerHTML = '';

    tasks.forEach(task => {
        const taskElement = document.createElement('div');
        taskElement.className = 'task-item';
        taskElement.innerHTML = `
            <h3>${task.title || '无标题'}</h3>
            <p>任务ID: ${task.taskId}</p>
            <p>创建时间: ${new Date(task.createdAt).toLocaleString()}</p>
            <button onclick="deleteTask('${task.taskId}')">删除</button>
        `;
        taskList.appendChild(taskElement);
    });
}

async function deleteTask(taskId) {
    if (confirm('确定要删除这个播客吗？此操作不可撤销。')) {
        try {
            const response = await fetch(`/delete_task/${taskId}`, {
                method: 'DELETE'
            });
            if (response.ok) {
                alert('播客已成功删除');
                fetchTasks(); // 重新加载任务列表
            } else {
                alert('删除播客失败');
            }
        } catch (error) {
            console.error('删除任务时出错:', error);
            alert('删除播客时发生错误');
        }
    }
}