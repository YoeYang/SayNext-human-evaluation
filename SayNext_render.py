#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate forms for human evaluation (MC from JSON)."""

from jinja2 import FileSystemLoader, Environment, select_autoescape
import json
import random
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json",
        required=True,
        help="包含 Ground Truth, Answer 1/2/3 的 JSON 路径",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="渲染后的 HTML 输出路径",
    )
    parser.add_argument(
        "--google_script_url",
        required=True,
        help="Google Apps Script Web App 的表单提交地址（action）",
    )
    parser.add_argument(
        "--page_title",
        default="SayNext Human Evaluation",
        help="页面标题（可选）",
    )
    args = parser.parse_args()

    # 读取 JSON
    with open(args.json, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # 组装题目数据：随机显示顺序，但单选 value = 原始编号（1/2/3）
    problems = []
    for idx, item in enumerate(raw, start=1):
        qid = item.get("qid", idx)  # 没有 qid 就用顺序号
        gt = item["Ground Truth"]

        triples = [
            ("1", item["Answer 1"]),
            ("2", item["Answer 2"]),
            ("3", item["Answer 3"]),
        ]
        random.shuffle(triples)  # 打乱显示顺序

        order_str = ",".join(t[0] for t in triples)  # 例如 "2,1,3"
        answers = [{"orig": t[0], "text": t[1]} for t in triples]

        problems.append(
            {
                "id": qid,
                "gt": gt,
                "answers": answers,
                "order_str": order_str,
            }
        )

    # Jinja 环境
    loader = FileSystemLoader(searchpath="./templates")
    env = Environment(
        loader=loader,
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # 使用我们新的模板
    template = env.get_template("mc_from_json.html.jinja2")

    html = template.render(
        page_title=args.page_title,
        google_script_url=args.google_script_url,
        problems=problems,
        form_type="mc_from_json_v1",
    )

    # 写文件
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"✅ 渲染完成: {out_path}")


if __name__ == "__main__":
    main()
