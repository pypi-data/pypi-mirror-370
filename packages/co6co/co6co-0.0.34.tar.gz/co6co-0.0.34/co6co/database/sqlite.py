import sqlite3
import threading


class ThreadSafeConnection:
    """
    sqlite3 线程安全连接 
    """

    def __init__(self, db_path,autoCommit=True):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.lock = threading.Lock()
        self.autoCommit=autoCommit

    def __enter__(self):
        # 获取锁并返回游标
        self.lock.acquire()
        return self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 提交事务并释放锁
        if self.autoCommit:
            self.conn.commit()
        self.lock.release()

    def close(self):
        self.conn.close()


'''
使用示例：
'''
"""
# 使用封装的连接对象
def worker(thread_name, db):
    with db as cursor:
        print(f"{thread_name} is executing query.")
        cursor.execute("SELECT * FROM my_table")
        results = cursor.fetchall()
        print(f"{thread_name} fetched: {results}")

# 创建线程安全的数据库连接
db = ThreadSafeConnection('example.db') 
# 创建多个线程
threads = []
for i in range(5):
    t = threading.Thread(target=worker, args=(f"Thread-{i+1}", db))
    threads.append(t)
    t.start()

# 等待所有线程完成
for t in threads:
    t.join()

# 关闭数据库连接
db.close()
"""
