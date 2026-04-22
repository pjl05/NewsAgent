#!/usr/bin/env python3
"""
Phase Status Monitor - 检查 Phase 文档与实际实现的匹配状态
"""
import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
PHASE_DOCS_DIR = PROJECT_ROOT / "docs" / "superpowers" / "phase-docs"
SRC_DIR = PROJECT_ROOT / "src"

# Phase 文档与对应的实现检查项
PHASE_CHECKLIST = {
    "Phase1": {
        "doc": "Phase1-基础设施搭建-设计文档.md",
        "modules": [
            "config.py",
            "models/user.py",
            "models/content.py",
            "models/interaction.py",
            "db/database.py",
            "db/redis.py",
            "db/milvus.py",
            "services/minimax.py",
            "agent/tools.py",
            "agent/graph.py",
            "main.py",
        ],
        "docker_files": ["docker-compose.yml", "Dockerfile"],
    },
    "Phase2": {
        "doc": "Phase2-内容采集-设计文档.md",
        "modules": [
            "services/content_collector.py",
            "services/rss_parser.py",
        ],
    },
    "Phase3": {
        "doc": "Phase3-个性化推荐-设计文档.md",
        "modules": [
            "services/recommender.py",
            "services/embedding.py",
        ],
    },
    "Phase4": {
        "doc": "Phase4-内容生成-设计文档.md",
        "modules": [
            "services/generator.py",
            "services/tts.py",
        ],
    },
    "Phase5": {
        "doc": "Phase5-WeChat集成-设计文档.md",
        "modules": [
            "services/wechat.py",
        ],
    },
    "Phase6": {
        "doc": "Phase6-定时任务与可视化-设计文档.md",
        "modules": [
            "services/scheduler.py",
            "services/visualizer.py",
        ],
    },
}


def get_git_changes(path: Path) -> List[str]:
    """获取 git 中已修改的文件"""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", str(path)],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except Exception:
        return []


def check_module_exists(module_path: Path) -> Tuple[bool, str]:
    """检查模块是否存在"""
    full_path = SRC_DIR / module_path
    if full_path.exists():
        return True, f"[OK] {module_path}"
    return False, f"[MISSING] {module_path}"


def generate_report() -> str:
    """生成状态报告"""
    report_lines = [
        f"# Phase 实现状态报告",
        f"",
        f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**项目根目录:** {PROJECT_ROOT}",
        f"",
    ]

    # 检查 git 变化
    changed_files = get_git_changes(PHASE_DOCS_DIR)
    if changed_files:
        report_lines.append("## Recent Doc Changes")
        for f in changed_files:
            report_lines.append(f"- {f}")
        report_lines.append("")

    # 检查每个 Phase 的实现状态
    report_lines.append("## Phase Implementation Status")
    report_lines.append("")
    report_lines.append("| Phase | 文档 | 状态 | 实现模块 |")
    report_lines.append("|-------|------|------|----------|")

    for phase_name, phase_info in PHASE_CHECKLIST.items():
        doc_path = PHASE_DOCS_DIR / phase_info["doc"]
        doc_exists = "[OK]" if doc_path.exists() else "[MISSING]"

        module_status = []
        for module in phase_info["modules"]:
            exists, _ = check_module_exists(Path(module))
            module_status.append("[OK]" if exists else "[MISSING]")

        all_exist = all(s == "[OK]" for s in module_status)
        status = "[COMPLETE]" if all_exist else "[PARTIAL]" if any(s == "[OK]" for s in module_status) else "[NOT_STARTED]"

        modules_str = ", ".join([f"`{m}`" for m in phase_info["modules"]])
        report_lines.append(
            f"| {phase_name} | {doc_exists} {phase_info['doc']} | {status} | {modules_str} |"
        )

    report_lines.append("")
    report_lines.append("## Detailed Check")
    for phase_name, phase_info in PHASE_CHECKLIST.items():
        report_lines.append(f"### {phase_name}: {phase_info['doc']}")
        for module in phase_info["modules"]:
            exists, msg = check_module_exists(Path(module))
            report_lines.append(f"- {msg}")
        report_lines.append("")

    return "\n".join(report_lines)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print(generate_report())