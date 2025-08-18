#pragma once

#include "autograd/function.hpp"

class AddBackward : public Function {
    public:
        AddBackward(Tensor& a, Tensor& b);
        void apply(std::shared_ptr<Tensor> incoming_gradient) override;
};

class SubBackward : public Function {
    public:
        SubBackward(Tensor& a, Tensor& b);
        void apply(std::shared_ptr<Tensor> incoming_gradient) override;
};

class MulBackward : public Function {
    public:
        MulBackward(Tensor& a, Tensor& b);
        void apply(std::shared_ptr<Tensor> incoming_gradient) override;
};

class DivBackward : public Function {
    public:
        DivBackward(Tensor& a, Tensor& b);
        void apply(std::shared_ptr<Tensor> incoming_gradient) override;
};