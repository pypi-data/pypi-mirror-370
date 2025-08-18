#include "tensor.hpp"
#include "autograd/graph/backward.hpp"
#include "utils/metadata.hpp"

namespace py = pybind11;

Tensor::Tensor(py::list& data, bool requires_grad) {
    this->_data = utils::metadata::flatten_nested_pylist(data);
    this->shape = utils::metadata::get_shape(data);
    this->ndim = utils::metadata::get_ndim(this->shape);
    this->size = utils::metadata::get_size(this->shape);
    this->strides = utils::metadata::get_strides(this->shape);

    this->requires_grad = requires_grad;
    this->grad_fn = nullptr;
    if (this->requires_grad) {
        this->grad = std::shared_ptr<Tensor>();
        assign_basic_metadata(*this->grad, this->shape);
        this->grad->requires_grad = false;
    } else {
        this->grad = nullptr;
    }

    this->is_contiguous = true;
    this->is_leaf = true;
}

Tensor::Tensor(const float data, bool requires_grad) {
    this->_data = std::shared_ptr<float[]>(new float[1]);
    this->_data[0] = data;
    this->shape = {};
    this->ndim = 0;
    this-> size = 1;
    this->strides = {};

    this->requires_grad = requires_grad;
    this->grad_fn = nullptr;
    this->grad = nullptr;

    this->is_contiguous = true;
    this->is_leaf = true;
}

Tensor::Tensor() {
    this->_data = nullptr;
    this->grad_fn = nullptr;
    this->grad = nullptr;
    this->is_contiguous = true;
    this->is_leaf = false;
};

Tensor Tensor::copy() {
    Tensor result_tensor = Tensor();

    result_tensor._data = std::make_shared<float[]>(this->size);
    std::copy(this->_data.get(), this->_data.get() + this->size, result_tensor._data.get());
    
    assign_basic_metadata(result_tensor, this->shape);

    result_tensor.requires_grad = false;

    return result_tensor;
}   

void Tensor::backward(Tensor& input_grad) {
    this->grad = std::shared_ptr<Tensor>(&input_grad);
    std::vector<std::shared_ptr<Function>> result_graph = topological_sort(this->grad_fn);
    for (std::shared_ptr<Function>& fn : result_graph) {
        NULL;
    }
}

void assign_basic_metadata(Tensor& mutable_tensor, const std::vector<int>& shape) {
    mutable_tensor.shape = shape;
    mutable_tensor.ndim = utils::metadata::get_ndim(shape);
    mutable_tensor.size = utils::metadata::get_size(shape);
    mutable_tensor.strides = utils::metadata::get_strides(shape);
}