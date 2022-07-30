# Original Posting

Markdown is not enough? Integrated MathJax is buggy? Want literate programming? We have ALL IN ONE, and more!

## Usage

1. Installation: `pip install git+https://github.com/thautwarm/original-posting`.
2. Moving files in `./scripts` to your `$HOME/.original-posting/`.
3. Rendering `.op`: `op example.op --out example.html --force [--extra_search_path="./scripts"]`

**NOTE**: the `math` command is using MathJax, which requires you to install `nodejs` in PATH with `mathjax-node` installed.

## Demo
```julia
@begin md
## What is OP?!

OP is an all-in-one markup language！

[Link](https://github.com/mathjax/MathJax-node)！
Inline math like Lua comments: @math|\oplus|，inline math@math||\oplus||！
@begin py
    o = object();p = print
    for i in range(1, 4):
        p("#" * i, "Object Printing!", hash(o))
        o = object()
    x = 5
@end py
@begin math svg
    x = 5 \\
    1 + x^2 = @py|1 + x**2|
@end math
@begin comment
command statement:
    @begin name argument1 argument2...
        block
    @end name
inline命令: @name + |||... + code + ...|||
@end comment
@end md
```

![demo](static/demo.png)

## Commands

Under construction but it's damn simple.

A command in OP is a Python file found in `$HOME/.original-posting/`. They are implemented in very short lines, check out `./scripts` for examples!
