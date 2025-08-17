import copy
import numpy       as np
import scipy.stats as stats

def CLSPCanonicalForm(
    self, problem:        str  = "",   C: np.ndarray | None = None,
          S: np.ndarray | None = None, M: np.ndarray | None = None,
          Q: np.ndarray | None = None, b: np.ndarray | None = None,
          m: int        | None = None, p: int        | None = None,
          i: int               = 1,    j: int               = 1,
          zero_diagonal:  bool = False
) -> None:
    """
    Construct the canonical design matrix A = [C | S; M | Q] for CLSP.

    This method assembles the constraint matrix A from user-supplied or
    internally generated components — C, S, M, and Q — and assigns the
    corresponding right-hand side vector b. It is a required pre-step
    before solving a Convex Least Squares Programming (CLSP) problem.

    Depending on the specified problem type, it can generate allocation,
    transaction, or modular constraints and enforce optional diagonal
    exclusions. All missing blocks are padded to ensure conformability.

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

    Q : np.ndarray or None
        Externally supplied residual slack matrix used to adjust inequality
        constraints in M. Required only when r > 1. Encodes the sign pattern
        of residuals from the previous iteration and is used to construct the
        [C | S; M | Q] canonical form. Defaults to a conformable zero matrix
        on the first iteration.

    b : np.ndarray or None
        Right-hand side vector. Must have as many rows as A. Required.

    m, p : int or None
        Dimensions of X ∈ ℝ^{m×p}, relevant for allocation problems ('ap').

    i, j : int, default = 1
        Grouping sizes for row and column sum constraints in AP problems.

    zero_diagonal : bool, default = False
        If True, enforces structural zero diagonals via identity truncation.

    Attributes Set
    ---------------
    self.A : np.ndarray
        Canonical design matrix constructed from (C, S, M, Q).

    self.C_idx : tuple
        Tuple (rows, cols) indicating the size of the C block.

    self.b : np.ndarray
        Conformable right-hand side vector.

    Raises
    ------
    CLSPError
        If the design matrix A or right-hand side b is malformed, inconsistent,
        or incompatible with the structural assumptions of the problem.
    """
    # (b) Ensure the right-hand side is defined and set `self.b`
    if b is None:
        raise self.error("Right-hand side vector b must be provided.")
    self.b = b

    # (A) Option 1. AP (TM) problems with an optional zero diagonal
    if 'ap' in problem.lower() or 'tm' in problem.lower():
        if m is None or p is None:
            raise self.error("Both m and p must be specified.")
        if m % i != 0:
            raise self.error(f"m = {m} must be divisible by i = {i}")
        if p % j != 0:
            raise self.error(f"p = {p} must be divisible by j = {j}")
        # construct the C block using Kronecker product
        row_groups = np.kron(np.kron(np.eye(m // i), np.ones((1, i))),
                             np.ones((1, p)))
        col_groups = np.kron(np.ones((1, m)), np.kron(np.eye(p // j),
                                                      np.ones((1, j))))
        C = np.vstack([row_groups, col_groups])
        # append an optional identity matrix to M, remove duplicates
        if zero_diagonal:
            M_diag = np.hstack([np.diagflat(np.eye(1, m, k))
                                for k in range(p)])
            M = (M_diag.copy() if M is None or M.size == 0 else
                 np.unique(np.vstack([M, M_diag]),  axis=0))
            b = np.vstack([b, np.zeros((m, 1))])
            del M_diag

    # (A) Option 2. CMLS and RP problems
    if 'cmls' in problem.lower() or 'rp' in problem.lower():
        if C is None or M is None:
            raise self.error("Both C and M must be provided.")
        if C.shape[0] % M.shape[0] != 0:
            raise self.error(f"Row mismatch: rows(C) = {C.shape[0]} must be "
                             f"divisible by rows(M) = {M.shape[0]}")

    # (A) Option 3. General problems
    if C is None and M is None:
        raise self.error("At least one of C or M must be provided.")

    # (A) Convert missing blocks to conformable zero matrices
    n_col = C.shape[1] if C is not None else M.shape[1]
    C     = C          if C is not None else np.zeros((0, n_col))
    M     = M          if M is not None else np.zeros((0, n_col))
    S     = S          if S is not None else np.zeros((C.shape[0], 0))
    Q     = Q          if Q is not None else np.zeros((M.shape[0], 0))
    if C.shape[0] != S.shape[0]:
        raise self.error(f"C and S must have the same number of rows: "
                         f"{C.shape[0]} vs {S.shape[0]}")
    if C.shape[1] != M.shape[1]:
        raise self.error(f"C and M must have the same number of columns: "
                         f"{C.shape[1]} vs {M.shape[1]}")

    # (A) Pad C and Q with zeros and set `self.A` and `self.C_idx`
    self.A     = np.vstack([
        np.hstack([C, S, np.zeros((C.shape[0], Q.shape[1]))]),
        np.hstack([M,    np.zeros((M.shape[0], S.shape[1])),   Q])
    ])
    self.C_idx = C.shape

def CLSPCorrelogram(
    self, reset:       bool = False,       threshold:    float = 0,
) -> dict[str, list[float]]:
    """
    Compute the structural correlogram of the CLSP constraint system.

    This method performs a row-deletion sensitivity analysis on the canonical
    constraint matrix [C | S], denoted as C_canon, and evaluates the marginal
    effect of each constraint row on numerical stability, angular alignment,
    and estimator sensitivity.

    For each row i in C_canon, it computes:
    - The Root Mean Square Alignment (RMSA_i) with all other rows j ≠ i.
    - The change in condition numbers κ(C), κ(B), and κ(A) when row i is
      deleted.
    - The effect on estimation quality: changes in NRMSE, zhat, z, and x.

    Additionally, it computes the total RMSA statistic across all rows,
    summarizing the overall angular alignment of the constraint block.

    Parameters
    ----------
    reset : bool, default = False
        If True, forces recomputation of all diagnostic values.

    threshold : float, default = 0
        If positive, limits the output to constraints with RMSA_i ≥ threshold.

    Returns
    -------
    dict of list
        A dictionary containing per-row diagnostic values:
        {
            "constraint"   : [1, 2, ..., k],  # 1-based indices
            "rmsa_i"       : list of RMSA_i values,
            "rmsa_dkappaC" : list of Δκ(C) after deleting row i,
            "rmsa_dkappaB" : list of Δκ(B) after deleting row i,
            "rmsa_dkappaA" : list of Δκ(A) after deleting row i,
            "rmsa_dnrmse"  : list of ΔNRMSE after deleting row i,
            "rmsa_dzhat"   : list of Δzhat after deleting row i,
            "rmsa_dz"      : list of Δz after deleting row i,
            "rmsa_dx"      : list of Δx after deleting row i,
        }
    """
    # (RMSA) Total RMSA
    if self.rmsa        == None          or reset:
        k                        = self.C_idx[0]
        p                        = self.C_idx[1]
        C_canon                  = self.A[:k]
        norms                    = np.linalg.norm(C_canon, axis=1)
        self.rmsa                = (lambda C:     np.sqrt(np.sum([(np.dot(
                                           C[i] / norms[i], C[j] / norms[j])
                                    ) ** 2 for i  in range(0,     k - 1)
                                           for j  in range(i + 1, k    )
                                   ]) * 2 / k / (k - 1)))(C_canon)

    # (RMSA) Constraint-wise RMSA, changes in condition numbers, and GoF
    if len(self.rmsa_i) != self.C_idx[0] or reset:
        tmp                      = copy.deepcopy(self)
        k                        = self.C_idx[0]
        p                        = self.C_idx[1]
        C_canon                  = self.A[:k]
        norms                    = np.linalg.norm(C_canon, axis=1)
        self.rmsa_i              = [None] * k
        self.rmsa_dkappaC        = [None] * k
        self.rmsa_dkappaB        = [None] * k
        self.rmsa_dkappaA        = [None] * k
        self.rmsa_dnrmse         = [None] * k
        self.rmsa_dzhat          = [None] * k
        self.rmsa_dz             = [None] * k
        self.rmsa_dx             = [None] * k
        for i in range(k):
            tmp.A                = np.delete(self.A, i, axis=0)
            tmp.b                = np.delete(self.b, i, axis=0)
            tmp.C_idx            = (k - 1, p)
            tmp.solve()
            self.rmsa_i[i]       = (lambda C,  i: np.sqrt(np.sum([(np.dot(
                                           C[i] / norms[i], C[j] / norms[j])
                                    ) ** 2 for j  in range(k) if j != i
                                   ]) / (k - 1)))(C_canon, i)
            self.rmsa_dkappaC[i] = tmp.kappaC - self.kappaC
            self.rmsa_dkappaB[i] = tmp.kappaB - self.kappaB
            self.rmsa_dkappaA[i] = tmp.kappaA - self.kappaA
            self.rmsa_dnrmse[i]  = tmp.nrmse  - self.nrmse
            self.rmsa_dzhat[i]   = tmp.zhat   - self.zhat
            self.rmsa_dz[i]      = tmp.z      - self.z
            self.rmsa_dx[i]      = tmp.x      - self.x

    # Return the correlogram
    indices = [i for i, r in enumerate(self.rmsa_i) if r >= threshold]
    return {
        "constraint"  : [i + 1 for i in indices],      # 1-based indexing
        "rmsa_i"      : [self.rmsa_i[i]       for i in indices],
        "rmsa_dkappaC": [self.rmsa_dkappaC[i] for i in indices],
        "rmsa_dkappaB": [self.rmsa_dkappaB[i] for i in indices],
        "rmsa_dkappaA": [self.rmsa_dkappaA[i] for i in indices],
        "rmsa_dnrmse" : [self.rmsa_dnrmse[i]  for i in indices],
        "rmsa_dzhat"  : [self.rmsa_dzhat[i]   for i in indices],
        "rmsa_dz"     : [self.rmsa_dz[i]      for i in indices],
        "rmsa_dx"     : [self.rmsa_dx[i]      for i in indices],
    }

def CLSPTTest(
    self, reset:       bool = False,       sample_size:  int   = 50,
          seed:        int  | None = None, distribution: str   | None = None
) -> dict[str, float]:
    """
    Perform Monte Carlo t-tests on the NRMSE statistic from the CLSP estimator.

    This function generates synthetic right-hand side vectors `b` using a 
    user-defined or default distribution and recomputes the estimator. It 
    tests whether the observed NRMSE significantly deviates from the null 
    distribution of simulated NRMSE values.

    Parameters
    ----------
    reset : bool, default = False
        If True, forces recomputation of the NRMSE null distribution.

    sample_size : int, default = 50
        Size of the Monte Carlo simulated sample under H₀.

    seed : int or None, optional
        Optional random seed to override the default.

    distribution : str or None
        Distribution for generating synthetic b vectors. One of:
        'normal', 'uniform', 'laplace'. Defaults to standard normal.

    Returns
    -------
    dict
        Dictionary with test results and null distribution statistics:
        {
            'p_one_left'  : P(nrmse ≤ null mean),
            'p_one_right' : P(nrmse ≥ null mean),
            'p_two_sided' : 2-sided t-test p-value,
            'nrmse'       : observed value,
            'mean_null'   : mean of null distribution,
            'std_null'    : std of null distribution
        }
    """
    # Set the seed, RNG configuration, and distribution
    if seed is not None:
        self.seed = seed
        self.rng  = np.random.default_rng(self.seed)
    if distribution is not None:
        dist_fn   = {
            "normal":  lambda n: self.rng.normal(loc=0, scale=1, size=(n, 1)),
            "uniform": lambda n: self.rng.uniform(-1, 1, size=(n, 1)),
            "laplace": lambda n: self.rng.laplace(loc=0, scale=1, size=(n, 1))
        }.get(distribution.lower())
        if dist_fn is None:
            raise self.error(f"Unsupported distribution: {distribution}")

    # (t-test) Simulated NRMSE distribution under H0
    if len(self.nrmse_ttest) != sample_size or reset:
        tmp = copy.deepcopy(self)
        self.nrmse_ttest        = [None] * sample_size
        for i in range(sample_size):
            tmp.b               = dist_fn(self.b.shape[0])
            tmp.solve()
            self.nrmse_ttest[i] = tmp.nrmse

    # Return the t-test
    nrmse_null = np.array(self.nrmse_ttest)
    mean_null  = np.mean(nrmse_null)
    std_null   = np.std(nrmse_null, ddof=1)
    t_stat     = (self.nrmse - mean_null) / (std_null / np.sqrt(sample_size))
    p_left     = stats.t.cdf(t_stat, df=sample_size - 1)
    p_right    = 1 - p_left
    p_two      = stats.t.sf(abs(t_stat), df=sample_size - 1) * 2
    return {
        "p_one_left" : p_left,
        "p_one_right": p_right,
        "p_two_sided": p_two,
        "nrmse"      : self.nrmse,
        "mean_null"  : mean_null,
        "std_null"   : std_null
    }
