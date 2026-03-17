#!/usr/bin/env python3
"""
自演进 MVP：AI 自动修改排版算法 -> 测试 -> 评分 -> Commit + Push
"""
import os, json, subprocess, random
from pathlib import Path
from PIL import Image, ImageDraw

print("🤖 自演进引擎启动")

PROJECT_DIR = Path(__file__).parent
OUTPUTS = PROJECT_DIR / "outputs" / "autoresearch"
OUTPUTS.mkdir(parents=True, exist_ok=True)

# 初始排版算法（可被优化）
class LayoutEngine:
    def __init__(self):
        self.title_margin_x = 100
        self.title_margin_y = 50
        self.box_margin = 20
    
    def render(self, width=1280, height=720):
        """生成幻灯片"""
        img = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # 标题
        title_x = self.title_margin_x
        title_y = self.title_margin_y
        draw.text((title_x, title_y), "AI PPT", fill=(0, 0, 0))
        
        # 内容框
        box_x1 = self.title_margin_x - self.box_margin
        box_y1 = title_y + 100
        box_x2 = width - self.box_margin
        box_y2 = height - self.box_margin
        draw.rectangle([box_x1, box_y1, box_x2, box_y2], outline=(0, 0, 255), width=2)
        
        return img
    
    def optimize(self, improvement_hint):
        """根据反馈优化参数"""
        if "margin" in improvement_hint.lower():
            self.title_margin_x = max(80, self.title_margin_x - 10)
            self.title_margin_y = max(30, self.title_margin_y - 5)
        elif "box" in improvement_hint.lower():
            self.box_margin = max(10, self.box_margin - 5)
        else:
            # 随机微调
            self.title_margin_x += random.randint(-20, 20)
            self.title_margin_y += random.randint(-10, 10)

# 评分函数（模拟 VLM 评判）
def evaluate_layout(img):
    """评估布局质量（0-100）"""
    # 简单启发式：检查留白和对称性
    pixels = img.tobytes()
    white_count = pixels.count(b'\xff\xff\xff')
    ratio = white_count / len(pixels)
    score = int(50 + (ratio * 50))  # 50-100 分
    return min(100, max(0, score))

# 自演进循环
print("\n[AutoResearch Loop]")
engine = LayoutEngine()
best_score = 0
iterations = 0
max_iterations = 5

for i in range(max_iterations):
    iterations = i + 1
    
    # 1. 渲染
    img = engine.render()
    img_path = OUTPUTS / f"iteration_{i:02d}.png"
    img.save(img_path)
    
    # 2. 评分
    score = evaluate_layout(img)
    
    # 3. 反馈
    hint = "Improve margins and box alignment"
    
    # 4. 优化参数
    engine.optimize(hint)
    
    print(f"  Round {i+1}: score={score}/100, margin_x={engine.title_margin_x}, box_margin={engine.box_margin}")
    
    if score > best_score:
        best_score = score
    
    if score >= 85:
        print(f"  ✓ 达成目标分数 {score}，停止迭代")
        break

# 保存最优版本
final_img = engine.render()
final_path = OUTPUTS / "final_optimized.png"
final_img.save(final_path)

# 生成优化报告
report = {
    "iterations": iterations,
    "best_score": best_score,
    "final_params": {
        "title_margin_x": engine.title_margin_x,
        "title_margin_y": engine.title_margin_y,
        "box_margin": engine.box_margin
    }
}

with open(OUTPUTS / "autoresearch_report.json", 'w') as f:
    json.dump(report, f, indent=2)

print(f"\n✅ 自演进完成")
print(f"   最佳分数：{best_score}/100")
print(f"   迭代次数：{iterations}")
print(f"   结果保存：{OUTPUTS}/")

# 自动 commit 和 push
print("\n[Auto Commit]")
os.chdir(PROJECT_DIR)
subprocess.run(["git", "add", "mvp_autoresearch_loop.py", "outputs/autoresearch/"], check=False)
result = subprocess.run(["git", "commit", "-m", f"🤖 AutoResearch: Score {best_score}/100 after {iterations} iterations"], 
                       capture_output=True, text=True)
if result.returncode == 0:
    subprocess.run(["git", "push"], check=False)
    print("   ✓ Commit 和 Push 完成")
else:
    print("   ℹ️ 无新变更")

print("\n🎉 自演进引擎完全自主运行完成")
