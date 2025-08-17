#include <Python.h>
#include <vector>
#include <algorithm>
using namespace std;

// Recursive fast power function
static long long fast_power(long long a, long long b, long long k) {
    if (b == 0) return 1 % k;
    long long temp = fast_power(a, b / 2, k) % k;
    if (b % 2 == 0) return (temp * temp) % k;
    else return (a * temp * temp) % k;
}

// Bubble sort
static vector<int> bubble_sort(vector<int> arr) {
    int n = static_cast<int>(arr.size()); // Fix size_t to int conversion
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                swap(arr[j], arr[j + 1]);
            }
        }
    }
    return arr;
}

// Insertion sort
static vector<int> insertion_sort(vector<int> arr) {
    int n = static_cast<int>(arr.size()); // Fix size_t to int conversion
    for (int i = 1; i < n; i++) {
        int key = arr[i];
        int j = i - 1;
        while (j >= 0 && key < arr[j]) {
            arr[j + 1] = arr[j];
            j -= 1;
        }
        arr[j + 1] = key;
    }
    return arr;
}

// Selection sort
static vector<int> selection_sort(vector<int> arr) {
    int n = static_cast<int>(arr.size()); // Fix size_t to int conversion
    for (int i = 0; i < n; i++) {
        int minI = i;
        for (int j = i + 1; j < n; j++) {
            if (arr[j] < arr[minI]) {
                minI = j;
            }
        }
        swap(arr[i], arr[minI]);
    }
    return arr;
}

// Merge sort helper function
static vector<int> merge(const vector<int>& left, const vector<int>& right) {
    vector<int> result;
    result.reserve(static_cast<int>(left.size() + right.size())); // Fix size_t to int conversion

    auto left_it = left.begin();
    auto right_it = right.begin();

    while (left_it != left.end() && right_it != right.end()) {
        if (*left_it <= *right_it) {
            result.push_back(*left_it++);
        } else {
            result.push_back(*right_it++);
        }
    }

    result.insert(result.end(), left_it, left.end());
    result.insert(result.end(), right_it, right.end());

    return result;
}

// Merge sort
static vector<int> merge_sort(const vector<int>& arr) {
    if (arr.size() <= 1) return arr;

    int mid = static_cast<int>(arr.size() / 2); // Fix size_t to int conversion
    vector<int> left(arr.begin(), arr.begin() + mid);
    vector<int> right(arr.begin() + mid, arr.end());

    left = merge_sort(left);
    right = merge_sort(right);

    return merge(left, right);
}

// Convert Python list to C++ vector
static vector<int> list_to_vector(PyObject* list_obj) {
    if (!PyList_Check(list_obj)) {
        PyErr_SetString(PyExc_TypeError, "Argument must be a list");
        return {};
    }
    Py_ssize_t size = PyList_Size(list_obj);
    vector<int> result;
    result.reserve(static_cast<int>(size)); // Fix size_t to int conversion

    for (Py_ssize_t i = 0; i < size; i++) {
        PyObject* item = PyList_GetItem(list_obj, i);  // Borrow reference
        if (!PyLong_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "List elements must be integers");
            return {};
        }

        long value = PyLong_AsLong(item);
        if (PyErr_Occurred()) {
            return {};
        }

        result.push_back(value);
    }

    return result;
}

// Convert C++ vector to Python list
static PyObject* vector_to_list(const vector<int>& vec) {
    PyObject* list_obj = PyList_New(static_cast<int>(vec.size())); // Fix size_t to int conversion
    if (!list_obj) {
        return NULL;
    }

    for (size_t i = 0; i < vec.size(); i++) {
        PyObject* num_obj = PyLong_FromLong(vec[i]);
        if (!num_obj) {
            Py_DECREF(list_obj);
            return NULL;
        }

        if (PyList_SetItem(list_obj, static_cast<int>(i), num_obj) < 0) { // Fix size_t to int conversion
            Py_DECREF(num_obj);
            Py_DECREF(list_obj);
            return NULL;
        }
        // PyList_SetItem transfers ownership, no need to Py_DECREF(num_obj)
    }

    return list_obj;
}

// Python wrapper for fast_power
static PyObject* py_fast_power(PyObject* self, PyObject* args) {
    long long a, b, k;

    if (!PyArg_ParseTuple(args, "LLL", &a, &b, &k)) {
        return NULL;
    }

    long long result = fast_power(a, b, k);
    return PyLong_FromLongLong(result);
}

// Python wrapper for bubble_sort
static PyObject* py_bubble_sort(PyObject* self, PyObject* args) {
    PyObject* list_obj;

    if (!PyArg_ParseTuple(args, "O", &list_obj)) {
        return NULL;
    }

    if (!PyList_Check(list_obj)) {
        PyErr_SetString(PyExc_TypeError, "Argument must be a list");
        return NULL;
    }

    vector<int> arr = list_to_vector(list_obj);
    if (PyErr_Occurred()) {
        return NULL;
    }

    vector<int> sorted_arr = bubble_sort(arr);
    return vector_to_list(sorted_arr);
}

// Python wrapper for insertion_sort
static PyObject* py_insertion_sort(PyObject* self, PyObject* args) {
    PyObject* list_obj;

    if (!PyArg_ParseTuple(args, "O", &list_obj)) {
        return NULL;
    }

    if (!PyList_Check(list_obj)) {
        PyErr_SetString(PyExc_TypeError, "Argument must be a list");
        return NULL;
    }

    vector<int> arr = list_to_vector(list_obj);
    if (PyErr_Occurred()) {
        return NULL;
    }

    vector<int> sorted_arr = insertion_sort(arr);
    return vector_to_list(sorted_arr);
}

// Python wrapper for selection_sort
static PyObject* py_selection_sort(PyObject* self, PyObject* args) {
    PyObject* list_obj;

    if (!PyArg_ParseTuple(args, "O", &list_obj)) {
        return NULL;
    }

    if (!PyList_Check(list_obj)) {
        PyErr_SetString(PyExc_TypeError, "Argument must be a list");
        return NULL;
    }

    vector<int> arr = list_to_vector(list_obj);
    if (PyErr_Occurred()) {
        return NULL;
    }

    vector<int> sorted_arr = selection_sort(arr);
    return vector_to_list(sorted_arr);
}

// Python wrapper for merge_sort
static PyObject* py_merge_sort(PyObject* self, PyObject* args) {
    PyObject* list_obj;

    if (!PyArg_ParseTuple(args, "O", &list_obj)) {
        return NULL;
    }

    if (!PyList_Check(list_obj)) {
        PyErr_SetString(PyExc_TypeError, "Argument must be a list");
        return NULL;
    }

    vector<int> arr = list_to_vector(list_obj);
    if (PyErr_Occurred()) {
        return NULL;
    }

    vector<int> sorted_arr = merge_sort(arr);
    return vector_to_list(sorted_arr);
}

// Module method list
static PyMethodDef ExampleMethods[] = {
    {"fast_power", py_fast_power, METH_VARARGS, "Calculate (a^b) % k"},
    {"bubble_sort", py_bubble_sort, METH_VARARGS, "Bubble sort algorithm"},
    {"insertion_sort", py_insertion_sort, METH_VARARGS, "Insertion sort algorithm"},
    {"selection_sort", py_selection_sort, METH_VARARGS, "Selection sort algorithm"},
    {"merge_sort", py_merge_sort, METH_VARARGS, "Merge sort algorithm"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

// Module definition
static struct PyModuleDef examplemodule = {
    PyModuleDef_HEAD_INIT,
    "example",
    "Module containing various algorithm implementations",
    -1,
    ExampleMethods
};

// Module initialization
PyMODINIT_FUNC PyInit_example(void) {
    return PyModule_Create(&examplemodule);
}