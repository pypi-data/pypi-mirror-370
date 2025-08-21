# Cerry Test Project

A well-structured Celery project with Redis backend and Flower monitoring.

## Prerequisites

- Python 3.8+
- Redis server
- Poetry (recommended) or pip

## Installation

1. Install dependencies:

```bash
# Using pip
pip install -e .

# Or using Poetry
poetry install
```

2. Start Redis server:

```bash
redis-server
```

## Running the Project

1. Start Celery worker:

```bash
celery -A cerry_test worker --loglevel=info
```

2. Start Celery beat (for periodic tasks):

```bash
celery -A cerry_test beat --loglevel=info
```

3. Start Flower monitoring:

```bash
celery -A cerry_test flower
```

4. Run the example:

```bash
python main.py
```

## Project Structure

```
cerry_test/
├── cerry_test/
│   ├── __init__.py        # Celery app initialization
│   ├── config/
│   │   └── celeryconfig.py # Celery configuration
│   ├── tasks/
│   │   └── example.py     # Example tasks
│   └── logs/              # Log files
├── main.py                # Example usage
├── pyproject.toml         # Project dependencies
└── README.md             # This file
```

## Features

- Redis as message broker and result backend
- Task progress tracking
- Periodic tasks with Celery Beat
- Task chains
- Flower monitoring interface
- Structured logging

## Monitoring

Access Flower monitoring interface at: http://localhost:5555

## Task Examples

1. Simple addition task:

```python
from cerry_test.tasks.example import add
result = add.delay(4, 4)
```

2. Progress tracking task:

```python
from cerry_test.tasks.example import process_data
result = process_data.delay([1, 2, 3, 4, 5])
```

3. Task chain:

```python
from cerry_test.tasks.example import create_processing_chain
chain = create_processing_chain([1, 2, 3])
result = chain()
```

4. Send message to queue:

```python
import asyncio
from task_dispatcher.mq_v1.sender import MessageSender

async def send_example():
    # 初始化消息发送器
    sender = MessageSender()

    # 准备消息数据
    message_data = {
        "user_id": "12345",
        "action": "user_login",
        "timestamp": "2024-01-20 10:30:00"
    }
    queue_name = "user_events"

    # 发送消息
    success = await sender.send_message(message_data, queue_name)
    if success:
        print("Message sent successfully")
    else:
        print("Failed to send message")

    # 完成后关闭连接
    await sender.close()

# 运行异步函数
if __name__ == "__main__":
    asyncio.run(send_example())
```

主要特点：

- 异步操作支持
- 类型安全的消息发送
- 自动错误处理和日志记录
- 连接自动管理
- 返回发送状态
