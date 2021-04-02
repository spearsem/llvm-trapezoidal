# llvm-trapezoidal

This is a reference project to demonstrate writing a non-trivial algorithm directly in LLVM IR and through
the Python interface to LLVM, `llvmlite`.

Projects such as `numba` (an advanced just-in-time compiler for Python) create user-friendly interfaces that
automatically convert Python bytecode into llvm representations such as found in this project. It can be
helpful to create a more concrete mental model of what `numba` is doing and how llvm really works by
hand-writing an algorithm in llvm IR directly. In this repository I consider doing that for the trapezoidal
rule, a popular algorithm for approximate numerical integration of functions.

To compile the plain llvm implementation you can follow these instructions with a suitable llvm compiler installed
(such as clang):

- `llvm-link -S -v trapezoidal_rule.ll llvm_main.ll -o single.ll`
- `llc single.ll -o single.s`
- `clang single.s -o single`
- `./single`

I have also included a Makefile to make this easier, just use `make run` and `make clean`. Note that this uses
the GNU `time` command to print timing info, but it is not very useful for the execution of the llvm binary, which
has a runtime significantly less than a tenth of a second.

To try out the Python-based version of the same implementation, you'll need to install the Python package
`llvmlite`, for example by creating a `conda` environment with the provided `environment.yml` file. From
within a suitable Python environment, simply run:

- `python trapezoidal_rule.py`

and the intermediate llvm IR of the dynamically generated llvm function will be printed along with timing and
result information.

Compare the generated llvm IR from `trapezoidal_rule.py` with the hand-made llvm implementation in `trapezoidal_rule.ll`,
and compare the runtime and result precision. You may also execute a pure Python implemention with the same timing and
result printed by running `python reference.py` to note how much faster the llvm implementations are than pure Python.
