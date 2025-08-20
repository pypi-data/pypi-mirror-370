# Linear Programming via Pseudoinverse Estimation

The **Linear Programming via Pseudoinverse Estimation (LPPinv)** is a two-stage estimation method that reformulates linear programs as structured least-squares problems. Based on the [Convex Least Squares Programming (CLSP)](https://pypi.org/project/pyclsp/ "Convex Least Squares Programming") framework, LPPinv solves linear inequality, equality, and bound constraints by (1) constructing a canonical constraint system and computing a pseudoinverse projection, followed by (2) a convex-programming correction stage to refine the solution under additional regularization (e.g., Lasso, Ridge, or Elastic Net).  
LPPinv is intended for **underdetermined** and **ill-posed** linear problems, for which standard solvers fail.

## Installation

```bash
pip install lppinv
```

## Quick Example

```python
from lppinv import lppinv
import numpy as np

# Define inequality constraints A_ub @ x <= b_ub
A_ub = [
    [1, 1],
    [2, 1]
]
b_ub = [5, 8]

# Define equality constraints A_eq @ x = b_eq
A_eq = [
    [1, -1]
]
b_eq = [1]

# Define bounds for x1 and x2
bounds = [(0, 5), (0, None)]

# Run the LP via CLSP
result = lppinv(
    c      = [1, 1],  # not used in CLSP but included for compatibility
    A_ub   = A_ub,
    b_ub   = b_ub,
    A_eq   = A_eq,
    b_eq   = b_eq,
    bounds = bounds
)

# Output solution
print("Solution vector (x):")
print(result.x.flatten())
```

## User Reference

For comprehensive information on the estimator’s capabilities, advanced configuration options, and implementation details, please refer to the [pyclsp module](https://pypi.org/project/pyclsp/ "Convex Least Squares Programming"), on which LPPinv is based.

**LPPINV Parameters:**

`c` : *array_like* of shape *(p,)*, optional  
Objective function coefficients. Accepted for API parity; not used by CLSP.

`A_ub` : *array_like* of shape *(i, p)*, optional  
Matrix for inequality constraints `A_ub @ x <= b_ub`.

`b_ub` : *array_like* of shape *(i,)*, optional  
Right-hand side vector for inequality constraints.

`A_eq` : *array_like* of shape *(j, p)*, optional  
Matrix for equality constraints `A_eq @ x = b_eq`.

`b_eq` : *array_like* of shape *(j,)*, optional  
Right-hand side vector for equality constraints.

`bounds` : *sequence* of *(low, high)*, optional  
Bounds on variables. If a single tuple **(low, high)** is given, it is applied to all variables. If None, defaults to *(0, None)* for each variable (non-negativity).

Please note that either `A_ub` and `b_ub` or `A_eq` and `b_eq` must be provided.

**CLSP Parameters:**  

`r` : *int*, default = *1*  
Number of refinement iterations for the pseudoinverse-based estimator.

`Z` : *np.ndarray* or *None*  
A symmetric idempotent matrix (projector) defining the subspace for Bott–Duffin pseudoinversion. If *None*, the identity matrix is used, reducing the Bott–Duffin inverse to the Moore–Penrose case.

`tolerance` : *float*, default = *square root of machine epsilon*  
Convergence tolerance for NRMSE change between refinement iterations.

`iteration_limit` : *int*, default = *50*  
Maximum number of iterations allowed in the refinement loop.

`final` : *bool*, default = *True*  
If *True*, a convex programming problem is solved to refine `zhat`. The resulting solution `z` minimizes a weighted L1/L2 norm around `zhat` subject to `Az = b`.

`alpha` : *float*, default = *1.0*  
Regularization parameter (weight) in the final convex program:  
- `α = 0`: Lasso (L1 norm)  
- `α = 1`: Tikhonov Regularization/Ridge (L2 norm)  
- `0 < α < 1`: Elastic Net

`*args`, `**kwargs` : optional  
CVXPY arguments passed to the CVXPY solver.

**Returns:**  
*self*

`self.A`             : *np.ndarray*  
Design matrix `A` = [`C` | `S`; `M` | `Q`], where `Q` is either a zero matrix or *S_residual*.

`self.b`             : *np.ndarray*  
Vector of the right-hand side.

`self.zhat`          : *np.ndarray*  
Vector of the first-step estimate.

`self.r`             : *int*  
Number of refinement iterations performed in the first step.

`self.z`             : *np.ndarray*  
Vector of the final solution. If the second step is disabled, it equals `self.zhat`.

`self.x`             : *np.ndarray*  
`m × p` matrix or vector containing the variable component of `z`.

`self.y`             : *np.ndarray*  
Vector containing the slack component of `z`.

`self.kappaC`        : *float*  
Spectral κ() for *C_canon*.

`self.kappaB`        : *float*  
Spectral κ() for *B* = *C_canon^+ A*.

`self.kappaA`        : *float*  
Spectral κ() for `A`.

`self.rmsa`          : *float*  
Total root mean square alignment (RMSA).

`self.r2_partial`    : *float*  
R² for the `M` block in `A`.

`self.nrmse`         : *float*  
Mean square error calculated from `A` and normalized by standard deviation (NRMSE).

`self.nrmse_partial` : *float*  
Mean square error from the `M` block in `A` and normalized by standard deviation (NRMSE).

`self.z_lower`       : *np.ndarray*  
Lower bound of the diagnostic interval (confidence band) based on κ(`A`).

`self.z_upper`       : *np.ndarray*  
Upper bound of the diagnostic interval (confidence band) based on κ(`A`).

`self.x_lower`       : *np.ndarray*  
Lower bound of the diagnostic interval (confidence band) based on κ(`A`).

`self.x_upper`       : *np.ndarray*  
Upper bound of the diagnostic interval (confidence band) based on κ(`A`).

`self.y_lower`       : *np.ndarray*  
Lower bound of the diagnostic interval (confidence band) based on κ(`A`).

`self.y_upper`       : *np.ndarray*  
Upper bound of the diagnostic interval (confidence band) based on κ(`A`).

## Bibliography

To be added.

## License

MIT License — see the [LICENSE](LICENSE) file.
