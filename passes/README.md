# llvm-pass-skeleton

A completely useless LLVM pass.
It's for LLVM 17.

Build:

    $ cd llvm-pass-skeleton
    $ mkdir build
    $ cd build
    $ cmake ..
    $ make
    $ cd ..

Run:

    $ clang -fpass-plugin=`echo build/hello/HelloPass.*` something.c

SAMPLE FROM: [sampsyo llvm-pass-skeleton](https://github.com/sampsyo/llvm-pass-skeleton)

## Currently

Currently it is a simple function printing pass. 