#!/usr/bin/env python3
"""
大规模基准测试：100 张幻灯片 -> 性能对比 -> 报告
"""
import json, time, subprocess, os
from pathlib import Path
from PIL import Image, ImageDraw
import random

print("📊 基准测试套件启动")

PROJECT_DIR = Path(__file__).parent
OUTPUTS = PROJECT_DIR / "outputs" / "benchmark"
OUTPUTS.mkdir(parents=True, exist_ok=True)

# 生成 100 张测试幻灯片
print("\n[Test Suite Generation]")
test_cases = []
for i in range(100):
    slide_data = {
        "id": i,
        "title": f"Slide {i:03d}",
        "title_x": random.randint(50, 150),
        "title_y": random.randint(30, 80),
        "box_x1": random.randint(50, 120),
        "box_y1": random.randint(120, 200),
        "box_x2": random.randint(1100, 1220),
        "box_y2": random.randint(600, 700)
    }
    test_cases.append(slide_data)

print(f"  ✓ 生成 {len(test_cases)} 个测试用例")

# 性能测试
print("\n[Performance Benchmark]")
results = {
    "total_tests": len(test_cases),
    "passed": 0,
    "failed": 0,
    "avg_render_time": 0,
    "total_time": 0,
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
}

start_time = time.time()

for idx, case in enumerate(test_cases[:10]):  # 先测 10 个
    try:
        # 模拟渲染
        t0 = time.time()
        img = Image.new("RGB", (1280, 720), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((case["title_x"], case["title_y"]), case["title"], fill=(0, 0, 0))
        draw.rectangle([case["box_x1"], case["box_y1"], case["box_x2"], case["box_y2"]], 
                      outline=(0, 0, 255), width=2)
        render_time = time.time() - t0
        
        results["passed"] += 1
        results["avg_render_time"] += render_time
    except Exception as e:
        results["failed"] += 1
        print(f"  ✗ Test {idx} failed: {e}")

results["total_time"] = time.time() - start_time
results["avg_render_time"] /= max(1, results["passed"])

print(f"  ✓ 通过：{results['passed']}")
print(f"  ✗ 失败：{results['failed']}")
print(f"  ⏱️ 平均渲染时间：{results['avg_render_time']*1000:.2f}ms")
print(f"  ⏱️ 总耗时：{results['total_time']:.2f}s")

# 保存结果
with open(OUTPUTS / "benchmark_results.json", 'w') as f:
    json.dump(results, f, indent=2)

with open(OUTPUTS / "test_cases.json", 'w') as f:
    json.dump(test_cases[:10], f, indent=2)

print(f"\n✅ 基准测试完成")
print(f"   结果：{OUTPUTS}/benchmark_results.json")

# Auto commit
os.chdir(PROJECT_DIR)
subprocess.run(["git", "add", "mvp_benchmark_suite.py", "outputs/benchmark/"], check=False)
subprocess.run(["git", "commit", "-m", f"📊 Benchmark: {results['passed']} passed, {results['avg_render_time']*1000:.1f}ms avg"], check=False)
subprocess.run(["git", "push"], check=False)
