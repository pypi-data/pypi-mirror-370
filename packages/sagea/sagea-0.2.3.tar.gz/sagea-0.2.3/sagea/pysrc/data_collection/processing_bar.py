#!/use/bin/env python
# coding=utf-8
# @Author  : Shuhao Liu
# @Time    : 2025/6/16 21:03 
# @File    : processing_bar.py

def bar(current, total, width):
    progress = current / total
    wid = 30
    bar_style = '#' * (int(wid * progress) + 1) + '-' * (wid - int(wid * progress) - 1)

    print(f'\r|{bar_style}| {"%.2f" % (current / total * 100)}%', end='')
