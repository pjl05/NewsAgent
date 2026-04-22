# Project Phase Monitor Skill

## 触发条件
当用户要求检查以下任何一项时自动调用：
- "检查 Phase 状态"
- "查看实现进度"
- "文档有没有更新"
- "对比 Phase 文档"
- 项目启动时自动检查

## 使用方法
```bash
python scripts/check_phase_status.py
```

## 输出
- 终端输出：简洁的状态概览
- 文件输出：`docs/superpowers/phase-status/latest.md`（详细报告）

## 检查内容
1. Git 中 phase-docs 目录的变化
2. 每个 Phase 文档是否存在
3. 对应的 src 目录下的模块是否已实现
4. Docker 相关文件是否存在

## 后续动作
根据报告：
- 如果有 Phase 文档被修改，提醒用户可能需要同步更新代码
- 如果有 Phase 的所有模块都已实现，标记为完成
- 如果有 Phase 有模块缺失，列出缺失的模块