import warnings
import numpy        as np
import scipy.linalg as la
import cvxpy        as cp

def CLSPSolve(
    self, problem:         str   = "",   C: np.ndarray |  None  = None,
          S: np.ndarray |  None  = None, M: np.ndarray |  None  = None,
                                         b: np.ndarray |  None  = None,
          m:     int    |  None  = None, p: int        |  None  = None,
          i:     int             = 1,    j: int                 = 1,
          zero_diagonal:   bool  = False,
          r:     int             = 1,    Z: np.ndarray |  None  = None,
          tolerance:       float = np.sqrt(np.finfo(float).eps),
          iteration_limit: int                         |  None  = None,
          final: bool   |  None  = None, alpha: float  |  None  = None,
          *args, **kwargs
) -> "CLSP":
    """
    Solve the Convex Least Squares Programming (CLSP) problem.

    This method performs a two-step estimation:
    (1) a pseudoinverse-based solution using either the Moore–Penrose or
        Bott–Duffin inverse, optionally iterated for convergence;
    (2) a convex-programming correction using Lasso, Ridge, or Elastic Net
        regularization (if enabled).

    Parameters
    ----------
    problem : str, optional
        Structural template for matrix construction. One of:
        - 'ap'   or 'tm' : allocation or transaction matrix problem.
        - 'cmls' or 'rp' : constrained modular least squares or RP-type.
        - ''     or other: General CLSP problems (user-defined C and/or M).

    C, S, M : np.ndarray or None
        Blocks of the constraint matrix A = [C | S; M | Q].
        If `C` and/or `M` are provided, the matrix A is constructed
        accordingly. If both are None and A is not yet defined, an error
        is raised.

    b : np.ndarray or None
        Right-hand side vector. Must have as many rows as A. Required.

    m, p : int or None
        Dimensions of X ∈ ℝ^{m×p}, relevant for allocation problems ('ap').

    i, j : int, default = 1
        Grouping sizes for row and column sum constraints in AP problems.

    zero_diagonal : bool, default = False
        If True, enforces structural zero diagonals via identity truncation.

    r : int, default = 1
        Number of refinement iterations for the pseudoinverse-based estimator.
        When `r > 1`, the slack block Q is updated iteratively to improve
        feasibility in underdetermined or ill-posed systems.

    Z : np.ndarray or None
        A symmetric idempotent matrix (projector) defining the subspace for
        Bott–Duffin pseudoinversion. If None, the identity matrix is used,
        reducing to the Moore–Penrose case.

    tolerance : float, optional
        Convergence tolerance for NRMSE change between iterations. Default is
        the square root of machine epsilon.

    iteration_limit : int, default = 50
        Maximum number of iterations allowed in the refinement loop.

    final : bool, default = True
        If True, a convex programming problem is solved to refine `zhat`.
        The resulting solution `z` minimizes a weighted L1/L2 norm around
        `zhat` subject to Az = b.

    alpha : float, default = 1.0
        Regularization weight in the final convex program:
        - α = 0: Lasso (L1 norm)
        - α = 1: Ridge (L2 norm)
        - 0 < α < 1: Elastic Net

    *args, **kwargs : optional
        Additional arguments passed to the CVXPY solver backend.

    Attributes Set
    ---------------
    self.A : np.ndarray
        Canonical design matrix constructed from (C, S, M, Q).

    self.b : np.ndarray
        Conformable right-hand side vector.

    self.Z : np.ndarray
        Projector matrix used for Bott–Duffin inversion.

    self.zhat : np.ndarray
        First-step solution (unregularized pseudoinverse estimate).

    self.z : np.ndarray
        Final estimate after optional convex refinement.

    self.x, self.y : np.ndarray
        Variable and slack components reshaped from `z`.

    self.nrmse : float
        Normalized root mean squared error over the full system.

    self.r2_partial : float or np.nan
        R² for the M block (if applicable), computed from partial residuals.

    self.nrmse_partial : float
        NRMSE over the M block, if defined.

    self.kappaA, self.kappaB, self.kappaC : float
        Condition numbers for the full, projected, and constrained system.

    self.z_lower, self.z_upper : np.ndarray
        Condition-weighted confidence band for z.

    self.r : int
        Number of refinement iterations performed.

    Raises
    ------
    CLSPError
        If the design matrix A or right-hand side b is malformed, inconsistent,
        or incompatible with the structural assumptions of the problem.
    """
    # (A), (b) Construct a conformable canonical form for the CLSP estimator
    if b is not None:
        self.b = b
    elif self.b is None:
        raise self.error("Right-hand side vector b must be provided.")
    if (C is not None or M is not None) or (m is not None and p is not None):
        self.canonize(problem, C, S, M, None, self.b.reshape(-1, 1),
                               m, p, i, j, zero_diagonal)
    elif self.A is None:
        raise self.error("At least one of C, M, m, or p must be provided.")
    if self.A.shape[0] != self.b.shape[0]:
        raise self.error(f"The matrix A and vector b must have the same "
                         f"number of rows: A has {self.A.shape[0]}, but "
                         f"b has {self.b.shape[0]}")

    # (zhat) (Iterated if r > 1) first-step estimate
    if r < 1:
        raise self.error("Number of refinement iterations r must be ≥ 1.")
    if Z is not None:
        self.Z = Z
    elif self.Z is None:
        self.Z = np.eye(self.A.shape[1])
    if tolerance       is not None:
        self.tolerance       = tolerance
    if iteration_limit is not None:
        self.iteration_limit = iteration_limit
    try:
        if (not np.allclose(self.Z,          self.Z.T, atol=tolerance) or
            not np.allclose(self.Z @ self.Z, self.Z,   atol=tolerance) or
            self.Z.shape[0] != self.A.shape[1]):
            raise ValueError
    except ValueError:
        raise self.error(f"Matrix Z must be symmetric, idempotent and "
                         f"match the number of columns in A: expected "
                         f"({self.A.shape[1]}, {self.A.shape[1]}), "
                         f"got {self.Z.shape}")
    for n_iter in range(1, 1 +
                           (r if self.A.shape[0] > self.C_idx[0] else 1)):
        # save A, zhat, and NRMSE from the previous step, construct Q
        if n_iter > 1:
            A_prev     = self.A.copy()
            zhat_prev  = self.zhat.copy()
            nrmse_prev = (np.linalg.norm(self.b  - self.A @ self.zhat) /
                          np.sqrt(self.b.shape[0]) / np.std(self.b))
            Q          = np.diagflat(-np.sign(self.b -
                                     self.A @ self.zhat)[self.C_idx[0]:])
            self.canonize(problem, C, S, M, Q, b.reshape(-1, 1),
                                   m, p, i, j, zero_diagonal)
        # solve via the Bott–Duffin inverse
        self.zhat      = (la.pinv(self.Z @ (self.A.T @ self.A) @ self.Z) @
                          self.Z @ self.A.T) @ self.b
        self.nrmse     = (lambda residuals, sd:
                          np.linalg.norm(residuals) / np.sqrt(sd.shape[0]) /
                          np.std(sd) if not np.isclose(np.std(sd), 0) else
                          np.inf)(self.b - self.A @ self.zhat, self.b)
        # break on convergence
        self.r         = n_iter
        if n_iter > 1:
            if (abs(self.nrmse - nrmse_prev) < self.tolerance or
                n_iter                       > self.iteration_limit):
                del A_prev, zhat_prev, nrmse_prev, Q
                break
    if not np.all(np.isfinite(self.zhat)):
        self.zhat = np.nan
        raise self.error("Pseudoinverse estimate zhat failed")

    # (z) Final solution (if available), or set self.z = self.zhat
    if final is not None:
        self.final = final
    if alpha is not None:
        self.alpha = alpha
    self.alpha = max(0, min(1, self.alpha))
    if self.final:
        # build a convex problem (p_cvx) and its solver (c_cvx)
        z_cvx = cp.Variable(self.A.shape[1])
        d_cvx = z_cvx - self.zhat.flatten()
        if   np.isclose(self.alpha, 0):                # Lasso
            f_obj = cp.norm1(d_cvx)
            s_cvx = cp.ECOS
        elif np.isclose(self.alpha, 1):                # Ridge
            f_obj = cp.sum_squares(d_cvx)
            s_cvx = cp.OSQP
        else:                                          # Elastic Net
            f_obj = ((1 - self.alpha) * cp.norm1(d_cvx)      +
                     self.alpha       * cp.sum_squares(d_cvx))
            s_cvx = cp.SCS
        c_cvx = [self.A @ z_cvx == self.b.flatten()]
        p_cvx = cp.Problem(cp.Minimize(f_obj), c_cvx)
        # solve
        try:
            p_cvx.solve(solver=s_cvx, verbose=False,
                                      *args, **kwargs) # pass arguments
            if z_cvx.value is None:
                warnings.warn(
                    f"Step 2 infeasible ({p_cvx.status}); falling back to Step 1.",
                    category=RuntimeWarning
                )
                self.z     = self.zhat
            else:
                self.z     = z_cvx.value
                self.nrmse = (lambda residuals, sd:
                          np.linalg.norm(residuals) / np.sqrt(sd.shape[0]) /
                          np.std(sd) if not np.isclose(np.std(sd), 0) else
                          np.inf)(self.b - self.A @ self.z,    self.b)
        except (cp.SolverError, ValueError):
            self.z = self.zhat
    else:
        self.z = self.zhat

    # (x), (y) Variable and slack components of z
    self.x = self.z[:self.C_idx[1]].reshape(m if m is not None else -1,
                                            p if p is not None else  1)
    self.y = self.z[self.C_idx[1]:]

    # (kappaC), (kappaB), (kappaA) Condition numbers
    self.kappaC            = np.linalg.cond(        self.A[:self.C_idx[0], :])
    self.kappaB            = np.linalg.cond(la.pinv(self.A[:self.C_idx[0], :]) @
                                            self.A)
    self.kappaA            = np.linalg.cond(        self.A)

    # (r2_partial), (nrmse_partial) M-block-based statistics
    if self.A.shape[0]     > self.C_idx[0]:
        M                  = self.A[self.C_idx[0]:, :self.C_idx[1]]
        b_M                = self.b[-M.shape[0]:]
        residuals_M        = b_M - M @ self.x.reshape(-1, 1)
        self.r2_partial    = (lambda residuals, sd:
                          1  -  (np.linalg.norm(residuals) ** 2            /
                          np.linalg.norm(sd - np.mean(sd)) ** 2)
                          if not np.isclose(np.std(sd), 0) else
                          np.nan)(residuals_M,                 b_M)
        self.nrmse_partial = (lambda residuals, sd:
                          np.linalg.norm(residuals) / np.sqrt(sd.shape[0]) /
                          np.std(sd) if not np.isclose(np.std(sd), 0) else
                          np.inf)(residuals_M,                 b_M)
        del M, b_M, residuals_M

    # (z_lower), (z_upper) Condition-weighted confidence band
    dz           = (self.kappaA                              * 
                    np.linalg.norm(self.b - self.A @ self.z) /
                    np.linalg.norm(self.b)
                    if not np.isclose(np.linalg.norm(self.b), 0) else
                    np.inf)
    self.z_lower = self.z * (1 - dz)
    self.z_upper = self.z * (1 + dz)

    return self
