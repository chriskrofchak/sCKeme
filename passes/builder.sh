cd build
cmake ..
make 
cd ..

# clang++ -fpass-plugin=`echo build/hello/HelloPass.*` test.cc