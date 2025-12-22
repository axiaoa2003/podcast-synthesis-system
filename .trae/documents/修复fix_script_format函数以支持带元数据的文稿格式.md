# 修复fix_script_format函数以支持带元数据的文稿格式

## 问题分析

**核心问题**: `fix_script_format`函数无法识别格式 `[A](happy,1,0): 文本内容` 为有效格式，错误地将其转换为 `[A]: (happy,1,0): 文本内容`，导致元数据被包含在对话内容中。

**具体表现**: 
- 函数只检查 `[A]: 文本` 格式
- 不识别 `[A](happy,1,0): 文本` 格式
- 将带元数据的格式误判为缺少冒号的格式
- 错误添加冒号，破坏了正确格式

## 修复方案

### 1. 增强fix_script_format函数

**修改点**: 更新`fix_script_format`函数，使其能够识别并保留带元数据的格式

**具体修改**: 
- 更新正则表达式，同时支持两种格式：
  - `[A](happy,1,0): 文本`（带元数据）
  - `[A]: 文本`（普通格式）
- 确保不修改已符合格式的行
- 添加详细日志，记录每一行的处理情况

### 2. 验证功能增强

**修改点**: 更新验证逻辑，确保两种格式都能被正确验证

**具体修改**: 
- 确保`validate_script`函数能够验证两种格式
- 提供明确的格式错误信息
- 增强日志记录

## 实施步骤

### 步骤1: 修改fix_script_format函数

**文件**: `podcast_utils.py`
**函数**: `fix_script_format`

```python
def fix_script_format(script):
    """
    修复文稿格式，确保符合正则表达式规范
    
    参数:
    - script: 播客文稿文本
    
    返回:
    - 修复后的文稿文本
    """
    fixed_lines = []
    lines = script.split('\n')
    
    for line in lines:
        original_line = line.strip()
        line = original_line.strip()
        if not line:
            fixed_lines.append('')
            continue
        
        print(f"修复格式 - 原行: {original_line}")
        
        # 检查是否已经符合格式（包括带元数据和普通格式）
        # 支持: [A](happy,1,0): 文本 和 [A]: 文本
        if re.match(r'^\[([AB])\](\([^)]+\))?\s*[:：]\s*(.*)$', line):
            fixed_lines.append(line)
            print(f"  ✅ 格式正确，无需修复")
            continue
        
        # 尝试修复格式问题
        # 1. 检查是否缺少冒号
        match = re.match(r'^\[([AB])\]\s*(.*)$', line)
        if match:
            role = match.group(1)
            text = match.group(2).strip()
            if text:
                fixed_line = f"[{role}]: {text}"
                fixed_lines.append(fixed_line)
                print(f"  🛠️  修复缺少冒号: {fixed_line}")
                continue
        
        # 2. 检查是否缺少括号
        match = re.match(r'^([AB])\s*[:：]\s*(.*)$', line)
        if match:
            role = match.group(1)
            text = match.group(2).strip()
            if text:
                fixed_line = f"[{role}]: {text}"
                fixed_lines.append(fixed_line)
                print(f"  🛠️  修复缺少括号: {fixed_line}")
                continue
        
        # 3. 检查是否有其他格式问题，尝试提取角色和文本
        # 简单的启发式方法：查找第一个A或B，假设后面是文本
        match = re.search(r'[AB]', line)
        if match:
            role = match.group(0)
            text = line[match.end():].strip()
            # 移除文本中的特殊标记
            text = re.sub(r'[\[\](){}]', '', text)
            if text:
                fixed_line = f"[{role}]: {text}"
                fixed_lines.append(fixed_line)
                print(f"  🛠️  修复其他格式问题: {fixed_line}")
                continue
        
        # 如果无法修复，保留原行
        fixed_lines.append(line)
        print(f"  ❌ 无法修复，保留原行")
    
    result = '\n'.join(fixed_lines)
    print(f"修复完成，共处理 {len(lines)} 行")
    return result
```

### 步骤2: 验证修复效果

**测试用例**: 
```
[A](happy,1,0): 额，圣诞节有啥活动吗？
[B](surprised,1,10): 还没想好。你呢？
[A](happy,1,0): 好久没玩Apex了，想打几把Apex放松一下，一起吗？。
[B](disgusted,1,-7): 跟你打纯折磨，能不玩电脑吗？干点别的？
```

**预期结果**: 
- 所有行都被识别为正确格式
- 未添加额外冒号
- 格式保持不变

### 步骤3: 增强日志记录

在`fix_script_format`函数中添加详细日志，便于调试和监控。

### 步骤4: 测试验证功能

确保`validate_script`函数能够正确验证两种格式：
- 验证带元数据的格式
- 验证普通格式
- 提供明确的错误信息

## 验证方法

1. **单元测试**: 编写测试用例，验证修复后的函数能够正确处理两种格式
2. **集成测试**: 在实际应用环境中测试，验证：
   - 带元数据的文稿格式不被错误转换
   - 元数据被正确提取
   - 音频生成使用了正确的参数
3. **日志验证**: 查看终端日志，确认格式修复过程正常

## 预期效果

1. **正确识别格式**: 函数能够识别并保留带元数据的格式
2. **不破坏正确格式**: 不再错误添加冒号
3. **增强的日志**: 详细记录每一行的处理情况
4. **提高稳定性**: 减少格式转换带来的错误
5. **更好的用户体验**: 用户输入的带元数据格式能够被正确处理

## 风险评估

1. **正则表达式性能**: 增强的正则表达式可能略微影响性能，但在实际应用中可忽略
2. **格式兼容性**: 确保修复后的函数兼容所有现有格式
3. **测试覆盖**: 需确保测试用例覆盖所有格式变体

## 后续优化建议

1. **前端格式统一**: 协调前端开发，确保生成的文稿格式一致
2. **API文档更新**: 明确文档中支持的格式
3. **格式转换工具**: 添加格式转换功能，支持多种格式之间的转换
4. **增强错误提示**: 当检测到格式问题时，提供明确的错误提示和修复建议

## 实施时间

- **代码修改**: 30分钟
- **测试验证**: 15分钟
- **部署应用**: 10分钟

## 结论

通过修复`fix_script_format`函数，使其能够识别并保留带元数据的格式，能够有效解决文稿格式被错误转换的问题。这是一个根本的解决方案，能够确保在实际应用环境中稳定读取文稿数据，提高系统的可靠性和用户体验。