#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def main():
    print("欢迎使用加减法计算器！")
    while True:
        try:
            expr = input("请输入加减表达式（如 3+5 或 10-2），或输入 q 退出: ")
            if expr.strip().lower() == 'q':
                print("退出计算器。")
                break
            if '+' in expr:
                parts = expr.split('+')
                result = float(parts[0]) + float(parts[1])
            elif '-' in expr:
                parts = expr.split('-')
                result = float(parts[0]) - float(parts[1])
            else:
                print("仅支持加法和减法。")
                continue
            print(f"结果: {result}")
        except Exception as e:
            print(f"输入有误: {e}")

if __name__ == "__main__":
    main()
