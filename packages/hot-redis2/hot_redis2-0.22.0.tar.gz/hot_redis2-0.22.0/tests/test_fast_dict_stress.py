#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stress tests for DelayButFastDict

import time
import unittest
import threading
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

from hot_redis.fast_dict import DelayButFastDict
from redis import Redis


class TestFastDictStress(unittest.TestCase):
    """压力测试和边界情况测试"""

    def setUp(self):
        self.redis_client = Redis(decode_responses=True)
        self.redis_client.delete("stress_dict:value")
        self.redis_client.delete("stress_dict:version")

    def tearDown(self):
        self.redis_client.delete("stress_dict:value")
        self.redis_client.delete("stress_dict:version")

    def test_large_data_set(self):
        """测试大数据集性能"""
        test_dict = DelayButFastDict[str, str](
            redis_client=self.redis_client,
            key="stress_dict",
            timeout=5
        )

        # 插入大量数据
        start_time = time.time()
        for i in range(1000):
            test_dict[f"key_{i:04d}"] = f"value_{i:04d}"
        
        insert_time = time.time() - start_time
        print(f"插入1000条数据耗时: {insert_time:.3f}秒")

        # 读取性能测试
        start_time = time.time()
        for i in range(1000):
            _ = test_dict[f"key_{i:04d}"]
        
        read_time = time.time() - start_time
        print(f"读取1000条数据耗时: {read_time:.3f}秒")

        # 验证数据正确性
        self.assertEqual(len(test_dict), 1000)
        self.assertEqual(test_dict["key_0000"], "value_0000")
        self.assertEqual(test_dict["key_0999"], "value_0999")

    def test_frequent_refresh(self):
        """测试频繁刷新的性能"""
        test_dict = DelayButFastDict[str, str](
            redis_client=self.redis_client,
            key="stress_dict",
            timeout=0.1  # 很短的超时时间
        )

        # 添加一些初始数据
        for i in range(100):
            test_dict[f"key_{i}"] = f"value_{i}"

        # 频繁访问触发刷新
        start_time = time.time()
        for i in range(500):
            if i % 50 == 0:
                time.sleep(0.11)  # 触发超时刷新
            _ = test_dict.get(f"key_{i % 100}")
        
        access_time = time.time() - start_time
        print(f"500次频繁访问(含刷新)耗时: {access_time:.3f}秒")

    def test_memory_usage_large_keys_values(self):
        """测试大键值对的内存使用"""
        test_dict = DelayButFastDict[str, str](
            redis_client=self.redis_client,
            key="stress_dict",
            timeout=10
        )

        # 创建大键值对
        large_key = "k" * 1000  # 1KB key
        large_value = "v" * 10000  # 10KB value

        test_dict[large_key] = large_value
        
        # 验证存储和读取
        self.assertEqual(test_dict[large_key], large_value)
        self.assertTrue(large_key in test_dict)

    def test_rapid_updates(self):
        """测试快速更新同一键"""
        test_dict = DelayButFastDict[str, str](
            redis_client=self.redis_client,
            key="stress_dict",
            timeout=5
        )

        key = "rapid_update_key"
        
        # 快速更新同一键
        for i in range(100):
            test_dict[key] = f"value_{i}"
            if i % 10 == 0:
                self.assertEqual(test_dict[key], f"value_{i}")

        # 验证最终值
        self.assertEqual(test_dict[key], "value_99")

    def test_random_operations(self):
        """测试随机操作混合"""
        test_dict = DelayButFastDict[str, str](
            redis_client=self.redis_client,
            key="stress_dict",
            timeout=2
        )

        operations = ['set', 'get', 'delete', 'update']
        keys = [f"key_{i}" for i in range(50)]
        
        # 执行随机操作
        for _ in range(500):
            op = random.choice(operations)
            key = random.choice(keys)
            
            if op == 'set':
                value = f"value_{random.randint(1, 1000)}"
                test_dict[key] = value
            elif op == 'get':
                try:
                    _ = test_dict[key]
                except KeyError:
                    pass  # 正常情况
            elif op == 'delete':
                try:
                    del test_dict[key]
                except KeyError:
                    pass  # 键可能不存在
            elif op == 'update':
                update_data = {f"key_{i}": f"batch_value_{i}" for i in range(5)}
                test_dict.update(update_data)

        # 操作完成，验证字典仍然可用
        test_dict["final_test"] = "final_value"
        self.assertEqual(test_dict["final_test"], "final_value")

    def test_version_race_condition(self):
        """测试版本竞争条件"""
        dict1 = DelayButFastDict[str, str](
            redis_client=self.redis_client,
            key="stress_dict",
            timeout=10  # 长超时，避免自动刷新干扰
        )
        
        dict2 = DelayButFastDict[str, str](
            redis_client=self.redis_client,
            key="stress_dict", 
            timeout=10
        )

        # 初始化数据
        dict1["initial"] = "value"
        
        def worker1():
            for i in range(50):
                dict1[f"worker1_key_{i}"] = f"worker1_value_{i}"
                time.sleep(0.01)

        def worker2():
            for i in range(50):
                dict2[f"worker2_key_{i}"] = f"worker2_value_{i}"
                time.sleep(0.01)

        # 并发执行
        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(worker1)
            future2 = executor.submit(worker2)
            
            future1.result()
            future2.result()

        # 刷新两个实例并验证数据一致性
        dict1.refresh()
        dict2.refresh()
        
        # 验证两个实例看到相同的数据
        self.assertEqual(len(dict1), len(dict2))
        
        for key in dict1.keys():
            self.assertTrue(key in dict2)
            self.assertEqual(dict1[key], dict2[key])

    def test_timeout_edge_cases(self):
        """测试超时边界情况"""
        # 测试极短超时
        short_timeout_dict = DelayButFastDict[str, str](
            redis_client=self.redis_client,
            key="stress_dict",
            timeout=0.01  # 10ms 超时
        )
        
        short_timeout_dict["test"] = "value"
        time.sleep(0.02)  # 等待超时
        self.assertEqual(short_timeout_dict["test"], "value")  # 应该触发刷新

        # 测试长超时
        self.redis_client.delete("stress_dict:value", "stress_dict:version")
        long_timeout_dict = DelayButFastDict[str, str](
            redis_client=self.redis_client,
            key="stress_dict", 
            timeout=3600  # 1小时超时
        )
        
        long_timeout_dict["test"] = "value"
        
        # 确保初始状态
        self.assertFalse("external" in long_timeout_dict)
        
        # 创建另一个实例来模拟外部修改
        external_dict = DelayButFastDict[str, str](
            redis_client=self.redis_client,
            key="stress_dict",
            timeout=1
        )
        external_dict["external"] = "external_value"
        
        # 短时间内第一个实例不应该看到外部修改（因为超时很长）
        # 注意：由于版本机制，实际上可能会看到，这是正常的
        # 我们测试强制刷新后一定能看到
        long_timeout_dict.refresh()
        self.assertTrue("external" in long_timeout_dict)

    def test_unicode_keys_values(self):
        """测试Unicode键值"""
        test_dict = DelayButFastDict[str, str](
            redis_client=self.redis_client,
            key="stress_dict",
            timeout=5
        )

        # 测试各种Unicode字符
        unicode_data = {
            "中文键": "中文值",
            "日本語": "こんにちは",
            "العربية": "مرحبا",
            "русский": "Привет",
            "emoji_😀": "emoji_😀_value",
            "数字_123": "值_456"
        }

        # 插入Unicode数据
        for key, value in unicode_data.items():
            test_dict[key] = value

        # 验证Unicode数据
        for key, value in unicode_data.items():
            self.assertTrue(key in test_dict)
            self.assertEqual(test_dict[key], value)

        # 测试Unicode操作
        self.assertEqual(len(test_dict), len(unicode_data))
        
        # 测试Unicode键的迭代
        keys = list(test_dict.keys())
        for key in unicode_data.keys():
            self.assertIn(key, keys)


if __name__ == "__main__":
    unittest.main(verbosity=2)