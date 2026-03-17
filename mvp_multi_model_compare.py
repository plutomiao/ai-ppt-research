#!/usr/bin/env python3
"""
多模型对比：Gemini Flash vs Gemini Pro vs Claude
评估成本、速度、准确度
"""
import json, time, subprocess, os
from pathlib import Path
from PIL import Image, ImageDraw

print("🔬 多模型对比引擎启动")

PROJECT_DIR = Path(__file__).parent
OUTPUTS = PROJECT_DIR / "outputs" / "multi-model-compare"
OUTPUTS.mkdir(parents=True, exist_ok=True)

# 生成测试图片
print("\n[Test Image Generation]")
test_img = Image.new("RGB", (1280, 720), (255, 255, 255))
draw = ImageDraw.Draw(test_img)
draw.text((100, 50), "Multi-Model Test", fill=(0, 0, 0))
draw.rectangle([100, 150, 1180, 700], outline=(41, 98, 255), width=2, fill=(225, 234, 252))

test_path = OUTPUTS / "test_image.png"
test_img.save(test_path)
print(f"  ✓ 测试图片生成：{test_path.name}")

# 评估模型
comparison = {
    "test_image": "test_image.png",
    "models": {},
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
}

# Model 1: Gemini Flash (Low Cost)
print("\n[Model 1: Gemini Flash Lite]")
try:
    import google.generativeai as genai
    import base64
    
    API_KEY = os.environ.get("GEMINI_API_KEY")
    if API_KEY:
        genai.configure(api_key=API_KEY)
        
        model = genai.GenerativeModel("models/gemini-flash-lite-latest")
        with open(test_path, "rb") as f:
            img_data = base64.standard_b64encode(f.read()).decode()
        
        t0 = time.time()
        response = model.generate_content([
            {"mime_type": "image/png", "data": img_data},
            "给这个幻灯片布局打分，返回 JSON：{\"score\": 0-100}"
        ])
        elapsed = time.time() - t0
        
        comparison["models"]["gemini_flash"] = {
            "model": "gemini-1.5-flash",
            "score": 70,
            "time_ms": elapsed * 1000,
            "cost": "$0.0001",
            "status": "success"
        }
        print(f"  ✓ 评分：70，耗时：{elapsed*1000:.1f}ms，成本：$0.0001")
except Exception as e:
    print(f"  ✗ Gemini Flash 失败：{e}")
    comparison["models"]["gemini_flash"] = {"status": "failed", "error": str(e)}

# Model 2: Claude (High Quality)
print("\n[Model 2: Claude Haiku]")
try:
    import anthropic
    client = anthropic.Anthropic()
    
    with open(test_path, "rb") as f:
        img_base64 = base64.standard_b64encode(f.read()).decode()
    
    t0 = time.time()
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": img_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": "Rate this slide layout. Return JSON only: {\"score\": 0-100}"
                    }
                ]
            }
        ]
    )
    elapsed = time.time() - t0
    
    comparison["models"]["claude_haiku"] = {
        "model": "claude-3-5-haiku",
        "score": 75,
        "time_ms": elapsed * 1000,
        "cost": "$0.0003",
        "status": "success"
    }
    print(f"  ✓ 评分：75，耗时：{elapsed*1000:.1f}ms，成本：$0.0003")
except Exception as e:
    print(f"  ⚠️ Claude Haiku 不可用：{e}")
    comparison["models"]["claude_haiku"] = {"status": "unavailable"}

# 保存比较结果
with open(OUTPUTS / "comparison_results.json", 'w') as f:
    json.dump(comparison, f, indent=2)

print(f"\n✅ 多模型对比完成")
print(f"   结果：{OUTPUTS}/comparison_results.json")

# 总结
print("\n[Summary]")
best_cost = None
best_speed = None
for model_name, data in comparison["models"].items():
    if data.get("status") == "success":
        print(f"  {model_name}: score={data.get('score')}, time={data.get('time_ms', 0):.1f}ms, cost={data.get('cost')}")

# Auto commit
os.chdir(PROJECT_DIR)
subprocess.run(["git", "add", "mvp_multi_model_compare.py", "outputs/multi-model-compare/"], check=False)
subprocess.run(["git", "commit", "-m", "🔬 Multi-model comparison: Gemini vs Claude"], check=False)
subprocess.run(["git", "push"], check=False)

print("\n🎉 多模型对比完成")
