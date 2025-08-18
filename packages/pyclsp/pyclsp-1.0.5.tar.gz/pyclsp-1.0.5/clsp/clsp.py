import warnings
import copy
import numpy        as np
import scipy.linalg as la
import scipy.stats  as stats
import cvxpy        as cp
from types          import MethodType
from .errors        import CLSPError
from .utils         import CLSPCanonicalForm, CLSPCorrelogram, CLSPTTest
from .solver        import CLSPSolve

class CLSP:
    def __init__(self):
        """
        Instantiate a CLSP (Convex Least Squares Programming) object.

        This class initiates and stores the results of a two-stage estimation
        process for constrained least-squares problems under a canonical matrix
        structure. The approach is designed for underdetermined, ill-posed, or
        structurally constrained systems.

        Stage 1 estimates the solution z from the system A·z = b using a
        pseudoinverse method. Depending on the projection matrix Z, this may
        be the Moore–Penrose inverse (Z = I) or the Bott–Duffin inverse (Z ≠ I).
        If r > 1, the pseudoinverse solution is iteratively refined using an
        updated slack matrix Q to improve numerical stability and feasibility.

        Stage 2 optionally refines the estimate using a convex optimization
        step centered around the pseudoinverse estimate ẑ. Regularization is
        governed by the user-specified parameter α:
            • α = 0      → Lasso (ℓ₁ norm),
            • α = 1      → Ridge (ℓ₂ norm),
            • 0 < α < 1  → Elastic Net (ℓ₁ and ℓ₂ combined).

        The class also supports diagnostic routines such as Monte Carlo
        hypothesis testing and row-wise deletion sensitivity analysis.

        Attributes
        ----------
        A : np.ndarray or None
            Canonical design matrix with block structure A = [C | S; M | Q].

        C_idx : tuple
            Pair of integers defining the row and column ranges of the
            C block inside A. Used for matrix slicing and partitioning.

        b : np.ndarray or None
            Right-hand side vector for the linear system A·z = b.

        Z : np.ndarray or None
            Projection matrix for Bott–Duffin inversion. Must be symmetric
            and idempotent. Defaults to identity for Moore–Penrose.

        zhat : np.ndarray or None
            Unregularized pseudoinverse estimate of z from Step 1.

        final : bool
            Whether to run the second-stage convex refinement. If True,
            the estimate is regularized via convex programming.

        alpha : float
            Regularization parameter:
            - α = 0: Lasso (L1 penalty),
            - α = 1: Ridge (L2 penalty),
            - 0 < α < 1: Elastic Net combination.

        z : np.ndarray or None
            Final estimate of z after regularization (if final is True).
            If skipped, z = zhat.

        x : np.ndarray or None
            Variable component extracted from z, reshaped into m × p.

        y : np.ndarray or None
            Slack component of z representing inequality residuals.

        r : int
            Number of refinement iterations performed during Step 1.
            Iteration stops when NRMSE stabilizes or exceeds the limit.

        kappaC : float or None
            Condition number of the constraint block C (upper-left block
            in A).

        kappaB : float or None
            Condition number of the projected estimator B^(r) = pinv(C)·A,
            calculated during refinement.

        kappaA : float or None
            Condition number of the full canonical matrix A^(r) after
            refinement step r.

        rmsa : float or None
            Total RMSA (Root Mean Square Adjustment) over all rows.

        rmsa_i : list of float
            Change in RMSA caused by removing each row from [C | S]
            and re-estimating the CLSP solution.

        rmsa_dkappaC : list of float
            Change in κ(C) caused by removing each row from [C | S]
            and re-estimating the CLSP solution.

        rmsa_dkappaB : list of float
            Change in κ(B) caused by removing each row from [C | S]
            and re-estimating the CLSP solution.

        rmsa_dkappaA : list of float
            Change in κ(A) caused by removing each row from [C | S]
            and re-estimating the CLSP solution.

        rmsa_dnrmse : list of float
            Change in NRMSE caused by removing each row from [C | S]
            and re-estimating the CLSP solution.

        rmsa_dzhat : list of float
            Change in zhat caused by removing each row from [C | S]
            and re-estimating the CLSP solution.

        rmsa_dz : list of float
            Change in z caused by removing each row from [C | S]
            and re-estimating the CLSP solution.

        rmsa_dx : list of float
            Change in x caused by removing each row from [C | S]
            and re-estimating the CLSP solution.

        r2_partial : float or None
            R² statistic computed over the M block. Reflects partial
            goodness-of-fit in structured systems.

        nrmse : float or None
            Normalized RMSE between A·z and b, computed over full system.

        nrmse_partial : float or None
            NRMSE computed only over M block rows.

        nrmse_ttest : list of float
            NRMSE samples generated via simulation under the null, used
            for empirical t-testing.

        z_lower : np.ndarray or None
            Lower bound of confidence band on z. Computed from κ(A) and
            residual norm.

        z_upper : np.ndarray or None
            Upper bound of confidence band on z. Symmetric to z_lower.

        seed : int
            Random seed used for reproducible Monte Carlo diagnostics.

        rng : np.random.Generator
            Random number generator initialized using `seed`.

        distribution : callable
            Function that generates random samples for simulation.
            Must accept a single integer argument `n`.

        Methods
        -------
        error : method
            Raise a CLSPError with optional diagnostics or contextual details.
        
        canonize : method
            Construct matrix A = [C | S; M | Q] and define constraint partitions.
        
        solve : method
            Main estimation routine performing pseudoinverse and convex steps.
        
        corr : method
            Compute RMSA and condition diagnostics via leave-one-out row deletion
            on [C | S]. Populates all `self.rmsa_*` lists. Output is external.
        
        ttest : method
            Monte Carlo t-test for NRMSE using user-defined distribution. Returns
            one-sided and two-sided p-values based on simulated means.
        """
        # Variables
        self.A             : np.ndarray | None = None # design matrix, [C|S;M|Q]
        self.C_idx         : tuple[int  | None,  int  | None]                  \
                            = (None, None)            # indices of the C block
        self.b             : np.ndarray | None = None # right-hand side
        self.Z             : np.ndarray | None = None # B-D subspace matrix
        self.r             : int               = 0    # number of iterations
        self.zhat          : np.ndarray | None = None # first-step estimate
        self.final         : bool              = True # inclusion of second step
        self.alpha         : float             = 1.0  # regularization parameter
        self.z             : np.ndarray | None = None # final solution
        self.x             : np.ndarray | None = None # variable component of z
        self.y             : np.ndarray | None = None # slack component of z
        self.kappaC        : float      | None = None # spectral κ() for C_canon
        self.kappaB        : float      | None = None # spectral κ() for B^(r)
        self.kappaA        : float      | None = None # spectral κ() for A^(r)
        self.rmsa          : float      | None = None # total RMSA
        self.rmsa_i        : list[float]       = []   # list of row RMSA
        self.rmsa_dkappaC  : list[float]       = []   # list of Δκ(C)
        self.rmsa_dkappaB  : list[float]       = []   # list of Δκ(B)
        self.rmsa_dkappaA  : list[float]       = []   # list of Δκ(A)
        self.rmsa_dnrmse   : list[float]       = []   # list of ΔNRMSE
        self.rmsa_dzhat    : list[float]       = []   # list of Δzhat
        self.rmsa_dz       : list[float]       = []   # list of Δz
        self.rmsa_dx       : list[float]       = []   # list of Δx
        self.r2_partial    : float      | None = None # R^2   for the M block
        self.nrmse         : float      | None = None # NRMSE for A
        self.nrmse_partial : float      | None = None # NRMSE for the M block
        self.nrmse_ttest   : list[float]       = []   # list of NRMSE
        self.z_lower       : np.ndarray | None = None # lower confidence band
        self.z_upper       : np.ndarray | None = None # upper confidence band
        self.seed          : int               = 123456789    # Monte Carlo
        self.rng           = np.random.default_rng(self.seed)
        self.distribution  = lambda n: self.rng.normal(loc=0, scale=1, size=n)

        # Methods
        self.error         = CLSPError
        self.canonize      = MethodType(CLSPCanonicalForm, self)
        self.solve         = MethodType(CLSPSolve,         self)
        self.corr          = MethodType(CLSPCorrelogram,   self)
        self.ttest         = MethodType(CLSPTTest,         self)

    def __repr__(self):
        """
        Return a formatted string representation of the CLSP object
        """
        if self.z is None:
            return "<CLSP: z=None, x=None, y=None>"

        z_str = (np.array2string(self.z, max_line_width=80))
        x_str = (np.array2string(self.x, max_line_width=80)
                 if self.x is not None else "None")
        y_str = (np.array2string(self.y, max_line_width=80)
                 if self.y is not None else "None")
        return f"<CLSP:\n z={z_str},\n x={x_str},\n y={y_str}>"
