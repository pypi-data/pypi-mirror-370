import threading
import time
from typing import Any, List


class MultiConsumerManager:
    """多消费者管理器"""

    def __init__(self):
        self.consumers: List[threading.Thread] = []
        self.running = False

    def add_consumer(self, consumer):
        """添加消费者"""

        def run_consumer():
            print(f"启动消费者: {threading.current_thread().name}")
            try:
                consumer.start()
            except Exception as e:
                print(f"消费者 {threading.current_thread().name} 发生错误: {e}")

        thread = threading.Thread(target=run_consumer, daemon=True)
        self.consumers.append(thread)
        return thread

    def start_all(self):
        """启动所有消费者"""
        self.running = True
        print(f"启动 {len(self.consumers)} 个消费者...")

        for thread in self.consumers:
            thread.start()

        print("所有消费者已启动")

    def wait_for_all(self):
        """等待所有消费者完成"""
        try:
            while self.running:
                alive_threads = [t for t in self.consumers if t.is_alive()]
                if not alive_threads:
                    print("所有消费者已停止")
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            print("收到中断信号，正在停止...")
            self.running = False

    def stop_all(self):
        """停止所有消费者"""
        self.running = False
        print("正在停止所有消费者...")


def create_multi_consumer_manager():
    return MultiConsumerManager()


def start_multiple_consumers(consumers: List[Any], wait: bool = True):
    """
    启动多个消费者

    Args:
        consumers: 消费者列表
        wait: 是否等待消费者运行
    """
    manager = MultiConsumerManager()

    for consumer in consumers:
        manager.add_consumer(consumer)

    manager.start_all()

    if wait:
        manager.wait_for_all()

    return manager
