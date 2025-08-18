# sif2jax

![Progress](https://img.shields.io/badge/CUTEst%20Problems-702%2F1539%20(45.6%25)-brightgreen)

Functionally pure definitions of optimisation problems extracted from Standard Input Format (SIF), written in [JAX](https://github.com/jax-ml/jax).

This is for you if you write optimisation software in JAX (or Python) and want to stress-test it on the CUTEst set of benchmark problems. Features include 

- all JAX everything: no Fortran backends
- full support for autodiff, batching, and JIT compilation
- more JAX benefits: run on CPU/GPU/TPU
- clear and human-readable problem definitions, no decoder required
- lean API - no specific problem interface required

## Installation

```bash
pip install sif2jax
```
Requires TODO fix

## Getting started

We recommend running the benchmarks with [pytest-benchmark](https://pytest-benchmark.readthedocs.io/en/latest/) - use the familiar testing infrastructure to run your benchmarks:

```python
import sif2jax

benchmark_problems = sif2jax.bounded_minimisation_problems

@pytest.mark.benchmark
@pytest.mark.parametrize("problem", sif2jax.unconstrained_minimisation_problems)
def test_lbfgs(benchmark, problem):
    ...
```

Alternatively, you can run any arbitrary benchmark problem by passing an index, or directly import a problem by name

```python
import sif2jax

problem = sif2jax.problems[42]
another_problem = sif2jax.cutest.get_problem("ROSENBR")
```

The problems all have the following methods:

- `objective` - a callable with signature `f(y, args)`, where `y` is the optimisation variable
- `y0` - returns the initial guess provided by the SIF file
- `args` - returns any arguments (frequently none)

bounded problems also have a `bounds` method, and constrained problems additionally include a `constraint` method.
