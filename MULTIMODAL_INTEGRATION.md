# 多模态集成指南

## 🎯 原则
当 PPT 项目需要多模态能力（图像理解、分析、评分）时，**直接调用 tmux 中的 Gemini 进程**，而不是调用外部 API。

---

## 📡 通信机制

### 方式 1：tmux 消息传递（推荐）
```python
import subprocess

def call_gemini_multimodal(image_path, prompt):
    """通过 tmux 向 Gemini 发送请求"""
    
    # 1. 将请求写入临时文件
    request = {
        "image": image_path,
        "prompt": prompt,
        "timestamp": time.time()
    }
    
    # 2. 向 tmux:gemini 发送消息
    subprocess.run([
        "tmux", "send-keys", "-t", "ai-team-allaccess2:1.3",
        f"python3 -c \"process_image('{image_path}', '{prompt}')\"",
        "Enter"
    ])
    
    # 3. 等待并读取结果
    result = read_from_shared_file()
    return result
```

### 方式 2：本地共享文件（稳定）
```python
import json

def call_gemini_via_file(image_path, prompt):
    """通过共享文件与 tmux:gemini 通信"""
    
    # 写入请求
    request_file = "/tmp/gemini_request.json"
    with open(request_file, "w") as f:
        json.dump({
            "image": image_path,
            "prompt": prompt,
            "mode": "multimodal"
        }, f)
    
    # 通知 Gemini 处理
    subprocess.run([
        "tmux", "send-keys", "-t", "ai-team-allaccess2:1.3",
        f"python3 process_gemini_request.py {request_file}",
        "Enter"
    ])
    
    # 等待结果
    result_file = "/tmp/gemini_result.json"
    while not Path(result_file).exists():
        time.sleep(0.5)
    
    with open(result_file) as f:
        return json.load(f)
```

---

## 🖼️ 多模态使用场景

### 1. 图像布局分析
```python
def analyze_layout(image_path):
    """用 Gemini 分析幻灯片布局"""
    result = call_gemini_multimodal(
        image_path,
        "分析这个幻灯片的布局：文本框位置、对齐度、重叠情况、留白评分"
    )
    return parse_layout_analysis(result)
```

### 2. 视觉对齐评分
```python
def score_alignment(original_image, generated_image):
    """用 Gemini 评估两张图的视觉对齐度"""
    result = call_gemini_multimodal(
        [original_image, generated_image],
        "比较这两张图：文字位置对齐度、色差、整体美观度。给出 0-100 的分数"
    )
    return parse_score(result)
```

### 3. 元素检测
```python
def detect_elements(image_path):
    """用 Gemini 识别幻灯片中的所有元素"""
    result = call_gemini_multimodal(
        image_path,
        "识别这个幻灯片的所有元素：标题、副标题、内容文本、图片、装饰元素、背景。返回坐标和类型"
    )
    return parse_elements(result)
```

---

## ⚙️ tmux:gemini 进程配置

当 PPT 项目需要调用 Gemini 时，确保 tmux 中有运行的 Gemini 窗口：

```bash
# 检查状态
tmux list-panes -t ai-team-allaccess2

# 应该看到：
# 0.0: ... (GPT)
# 0.1: ... 
# 0.2: ... (Claude)
# 0.3: ... (Gemini) ← 需要这个

# 如果没有，创建：
tmux new-window -t ai-team-allaccess2 -n gemini "gemini"
```

---

## 📋 集成检查清单

在 PPT 项目中使用多模态前，确认：

- [ ] tmux 中有活跃的 Gemini 窗口
- [ ] `/tmp/gemini_request.json` 和 `/tmp/gemini_result.json` 路径可写
- [ ] GPT 脚本中有 `call_gemini_multimodal()` 函数
- [ ] 请求和响应格式已定义
- [ ] 超时机制已实现（防止无限等待）

---

## 🚨 注意事项

1. **不要直接调用 API**：所有多模态请求都应通过 tmux:gemini
2. **文件清理**：处理完毕后删除 `/tmp/gemini_request.json` 和 `/tmp/gemini_result.json`
3. **错误处理**：如果 Gemini 未响应，自动降级到本地启发式方法
4. **性能**：tmux 通信有延迟，考虑批量处理请求

---

## 示例集成

```python
# core/multimodal_engine.py
import json
import subprocess
import time
from pathlib import Path

class GeminiMultimodalBridge:
    """GPT ↔ tmux:Gemini 通信桥接"""
    
    def __init__(self):
        self.request_file = Path("/tmp/gemini_request.json")
        self.result_file = Path("/tmp/gemini_result.json")
        self.timeout = 30
    
    def call(self, image_path, prompt):
        """发送多模态请求到 Gemini"""
        
        # 清理旧结果
        self.result_file.unlink(missing_ok=True)
        
        # 写入请求
        self.request_file.write_text(json.dumps({
            "image": str(image_path),
            "prompt": prompt,
            "timestamp": time.time()
        }))
        
        # 通知 Gemini
        subprocess.run([
            "tmux", "send-keys", "-t", "ai-team-allaccess2:1.3",
            f"python3 process_request.py {self.request_file}",
            "Enter"
        ])
        
        # 等待结果（最多 30 秒）
        start = time.time()
        while not self.result_file.exists():
            if time.time() - start > self.timeout:
                return {"error": "Timeout waiting for Gemini"}
            time.sleep(0.1)
        
        # 读取并返回结果
        return json.loads(self.result_file.read_text())
```

