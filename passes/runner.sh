clang++ -S -O3 -emit-llvm tests/test.cc -o tests/test.ll
opt -load-pass-plugin `echo build/hello/HelloPass.*` -passes="hello-fn" -disable-output tests/test.ll