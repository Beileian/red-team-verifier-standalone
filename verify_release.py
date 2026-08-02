#!/usr/bin/env python3
"""
verify_release.py — red-team-verifier-standalone 发布完整性检查

检查所有 SKILL.md 中引用的 references/ 文件是否真实存在。
在 git push 前运行，防止「引用了不存在的文件」的悬空引用再次发布。

用法:
    python3 verify_release.py            # 检查仓库全部 skill
    python3 verify_release.py --json     # JSON 输出（CI 友好）

返回: exit 0 = 全部通过, 1 = 存在悬空引用
"""
import os, re, sys, json, glob

ROOT = os.path.dirname(os.path.abspath(__file__))

# 引用模式: `references/xxx.md` 或 `references/xxx.md`
REF_PATTERN = re.compile(r'references/([a-zA-Z0-9_\-]+\.md)')


def check_skill(skill_dir: str) -> list:
    """检查单个 skill 目录的引用完整性，返回问题列表"""
    problems = []
    sk_path = os.path.join(ROOT, skill_dir, "SKILL.md")
    if not os.path.exists(sk_path):
        return [f"{skill_dir}: SKILL.md 不存在"]
    with open(sk_path, encoding="utf-8") as f:
        content = f.read()
    refs = sorted(set(REF_PATTERN.findall(content)))
    for ref in refs:
        ref_path = os.path.join(ROOT, skill_dir, "references", ref)
        if not os.path.exists(ref_path):
            problems.append(f"{skill_dir}/SKILL.md → references/{ref} 缺失")
    return problems


def main():
    skills = [
        d for d in os.listdir(ROOT)
        if os.path.isdir(os.path.join(ROOT, d)) and not d.startswith(".")
    ]
    all_problems = []
    for skill in skills:
        all_problems.extend(check_skill(skill))

    # 汇总
    summary = {
        "skills_checked": len(skills),
        "problems": all_problems,
        "pass": len(all_problems) == 0,
    }

    if "--json" in sys.argv:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"📦 检查 {len(skills)} 个 skill 目录")
        if all_problems:
            print(f"❌ 发现 {len(all_problems)} 个悬空引用:")
            for p in all_problems:
                print(f"   - {p}")
        else:
            print("✅ 全部引用完整，可发布")
        print(f"   (exit {0 if summary['pass'] else 1})")

    sys.exit(0 if summary["pass"] else 1)


if __name__ == "__main__":
    main()
