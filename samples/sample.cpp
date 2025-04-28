#include <iostream>
#include <vector>
using namespace std;

// Simple Rectangle class with area calculation
class Rectangle {
private:
    double width, height;
public:
    Rectangle(double w, double h) : width(w), height(h) {}

    double area() const {
        return width * height;
    }
};
