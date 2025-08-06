#include <iostream>


int sq_minus_1(int x) {
    return (x + 1)*(x - 1);
}

template<typename T>
void print_value(T x) {
    std::cout << x << std::endl;
}

int main() {
    // std::cout << "Should print three values,";
    // std::cout << " two of which don't correlate to the computed value..." << std::endl;
    // std::cout << "... or do they." << std::endl;
    print_value<int>(sq_minus_1(4));
}