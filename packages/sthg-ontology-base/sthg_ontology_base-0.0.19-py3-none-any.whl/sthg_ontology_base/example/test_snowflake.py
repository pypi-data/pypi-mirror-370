"""
@Author  ：duomei
@File    ：test_snowflake.py
@Time    ：2025/8/12 12:50
"""

import os
import unittest
import threading

from sthg_ontology_base.utils.snowflake_generator import SnowflakeIdGenerator


class TestSnowflakeIdGenerator(unittest.TestCase):
    """雪花算法ID生成器测试类"""

    @classmethod
    def setUpClass(cls):
        """初始化测试环境"""
        # 设置环境变量为测试环境，避免要求配置MACHINE_ID
        os.environ["ENVIRONMENT"] = "test"
        # 创建生成器实例，指定worker_id确保可重复性
        cls.generator = SnowflakeIdGenerator(worker_id=1)

    def test_single_thread_unique_ids(self):
        """测试单线程下生成的ID唯一性"""
        count = 10000
        generated_ids = set()

        for _ in range(count):
            snowflake_id = self.generator.generate_id()
            # 检查ID是否已存在
            self.assertNotIn(snowflake_id, generated_ids, f"发现重复ID: {snowflake_id}")
            generated_ids.add(snowflake_id)

        # 验证生成的ID数量与预期一致
        self.assertEqual(len(generated_ids), count,
                         f"ID数量不匹配，预期{count}个，实际{len(generated_ids)}个")

    def test_multi_thread_unique_ids(self):
        """测试多线程下生成的ID唯一性"""
        total_count = 100000
        thread_count = 100  # 10个线程
        ids_per_thread = total_count // thread_count
        generated_ids = set()
        lock = threading.Lock()  # 用于安全操作共享集合

        def generate_in_thread():
            """线程执行的生成ID函数"""
            nonlocal generated_ids
            for _ in range(ids_per_thread):
                snowflake_id = self.generator.generate_id()
                with lock:
                    if snowflake_id in generated_ids:
                        # 发现重复ID时记录并抛出异常
                        raise ValueError(f"多线程环境下发现重复ID: {snowflake_id}")
                    generated_ids.add(snowflake_id)

        # 创建并启动线程
        threads = []
        for _ in range(thread_count):
            thread = threading.Thread(target=generate_in_thread)
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证最终ID数量
        self.assertEqual(len(generated_ids), total_count,
                         f"多线程ID数量不匹配，预期{total_count}个，实际{len(generated_ids)}个")


if __name__ == "__main__":
    unittest.main(verbosity=2)
