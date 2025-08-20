import numpy as np
from scipy.optimize import minimize
try:
    from multinomial_logit import*
except ImportError:
    from .multinomial_logit import *
    
class NestedLogit(MultinomialLogit):
    """
    Nested Logit Model (inherits from MultinomialLogit).
    Handles nested structure of alternatives.
    """

    def __init__(self):
        super(NestedLogit, self).__init__()
        self.descr = "Nested Logit"

    def setup(self, X, y, varnames=None, isvars=None, alts=None, ids=None,
              nests=None, lambdas=None, fit_intercept=False, **kwargs):
        """
        Setup the Nested Logit model.
        """
        super().setup(X, y, varnames=varnames, isvars=isvars, alts=alts, ids=ids,
                      fit_intercept=fit_intercept, **kwargs)



        if not nests or not isinstance(nests, dict):
            raise ValueError("`nests` must be a dictionary with nest names as keys and alternatives as values.")
        self.nests = nests
        self.nest_names = list(nests.keys())  # Keep the order of nests

        if lambdas is None:
            self.lambdas = {nest: 1.0 for nest in nests}  # Default lambdas = 1.0
        else:
            if set(lambdas.keys()) != set(nests.keys()):
                raise ValueError("`lambdas` must have the same keys as `nests`.")
            self.lambdas = lambdas

        self.num_nests = len(nests)  # Number of nests
        extra_betas = np.ones(self.num_nests)  # Initialize extra betas (default: zeros)
        self.betas = np.concatenate([self.betas, extra_betas])

        #print(f"Initial betas (including nest-specific): {self.betas}")

    def compute_probabilities(self, betas, X, avail):
        """
        Compute choice probabilities for a 3D feature matrix (N, J, K).
        """
        # Ensure X is 3D: (N, J, K)



        if len(X.shape) != 3:
            raise ValueError(f"X must be 3D (N, J, K). Got shape: {X.shape}")

        N, J, K = X.shape  # Extract dimensions




        num_features = K
        lambdas = betas[num_features:]  # Extract lambda coefficients for nests
        betas_X = betas[:num_features]  # Extract coefficients for features

        # Compute utilities: U = X @ betas (broadcast dot product over alternatives)
        utilities = np.einsum('njk,k->nj', X, betas_X)  # Shape: (N, J)

        # Initialize inclusive values for each nest
        inclusive_values = []
        for nest, lambd in zip(self.nests.values(), lambdas):


            # Validate indices
            if any(idx >= utilities.shape[1] for idx in nest):
                raise ValueError(f"Invalid indices in nest {nest}. Utilities shape: {utilities.shape}")

            # Compute utilities for the current nest
            utilities_nest = utilities[:, nest] / lambd

            # Apply log-sum-exp trick
            max_utilities_nest = np.max(utilities_nest, axis=1, keepdims=True)  # Shape: (N, 1)
            log_sum_exp = max_utilities_nest + \
                          np.log(np.sum(np.exp(utilities_nest - max_utilities_nest), axis=1, keepdims=True))
            inclusive_value = (1 / lambd) * log_sum_exp.squeeze()  # Remove extra dimension
            inclusive_values.append(inclusive_value)

        # Ensure inclusive_values is not empty
        if not inclusive_values:
            print("No inclusive values were calculated. Check the following:")
            print(f"Nests: {self.nests}")
            print(f"Utilities shape: {utilities.shape}")
            print(f"Lambdas: {lambdas}")
            raise ValueError("No inclusive values were calculated. Check nest definitions and utilities.")
        inclusive_values = np.column_stack(inclusive_values)  # Shape: (N, num_nests)

        # Compute upper-level probabilities
        scaled_inclusive_values = inclusive_values * lambdas  # Element-wise multiplication
        max_scaled_inclusive_values = np.max(scaled_inclusive_values, axis=1, keepdims=True)
        upper_probs = np.exp(scaled_inclusive_values - max_scaled_inclusive_values) / np.sum(
            np.exp(scaled_inclusive_values - max_scaled_inclusive_values), axis=1, keepdims=True
        )  # Shape: (N, num_nests)

        # Compute lower-level probabilities
        lower_probs = np.zeros_like(utilities)  # Shape: (N, J)
        for nest, lambd, upper_prob in zip(self.nests.values(), lambdas, upper_probs.T):
            utilities_nest = utilities[:, nest] / lambd

            # Apply log-sum-exp trick in the exponentiation step
            max_utilities_nest = np.max(utilities_nest, axis=1, keepdims=True)
            exp_utilities = np.exp(utilities_nest - max_utilities_nest)
            nest_probs = exp_utilities / np.sum(exp_utilities, axis=1, keepdims=True)

            lower_probs[:, nest] = nest_probs * upper_prob[:, np.newaxis]

        # Apply availability masks if provided
        if avail is not None:
            lower_probs *= avail

        return lower_probs


    def summarise(self, file=None):
        # Append nest-specific coefficient names
        if hasattr(self, 'nests') and isinstance(self.nests, dict):
            nest_coeffs = [f"lambda_{nest}" for nest in self.nests.keys()]
            self.coeff_names = np.concatenate([self.coeff_names, nest_coeffs])

        super().summarise(file = file)

    def get_loglik_and_gradient(self, betas, X, y, weights, avail):
        """
        Compute log-likelihood and gradient for a 3D feature matrix (N, J, K).

        Parameters:
            betas: np.ndarray
                Coefficients for features and lambda values (size: K + num_nests).
            X: np.ndarray
                Feature matrix of shape (N, J, K).
            y: np.ndarray
                Binary choice matrix of shape (N, J).
            weights: np.ndarray or None
                Optional weights for observations (size: N).
            avail: np.ndarray or None
                Availability mask of shape (N, J).

        Returns:
            Tuple: (negative log-likelihood, negative gradient)
        """
        N, J, K = X.shape  # Extract dimensions
        num_features = K
        lambdas = betas[num_features:]  # Extract lambda coefficients (size: num_nests)

        # Compute probabilities using all betas
        p = self.compute_probabilities(betas, X, avail)  # Shape: (N, J)

        # Compute log-likelihood
        chosen_probs = np.sum(y * p, axis=1)  # Select probabilities for chosen alternatives
        chosen_probs = np.clip(chosen_probs, 1e-10, None)  # Avoid log(0)
        loglik = np.sum(np.log(chosen_probs))  # Sum over all observations

        # Apply weights (if provided)
        if weights is not None:
            loglik = np.sum(weights[:, 0] * np.log(chosen_probs))  # Weighted log-likelihood

        # Initialize gradient computation
        grad = None
        if self.return_grad:
            # Residuals (observed - predicted probabilities)
            ymp = y - p  # Shape: (N, J)

            # Gradient for feature coefficients (betas_X)
            grad_X = np.einsum('njk,nj->k', X, ymp)  # Shape: (K)

            # Gradient for lambda coefficients
            grad_lambdas = []  # Will store gradients for each lambda
            for nest, lambd in zip(self.nests.values(), lambdas):
                # Compute utilities for the current nest using full betas
                utilities_nest = np.einsum('njk,k->nj', X[:, nest, :], betas[:K]) / lambd

                # Apply log-sum-exp trick
                max_utilities_nest = np.max(utilities_nest, axis=1, keepdims=True)  # Shape: (N, 1)
                exp_utilities = np.exp(utilities_nest - max_utilities_nest)  # Shape: (N, |nest|)
                log_sum_exp = max_utilities_nest + np.log(
                    np.sum(exp_utilities, axis=1, keepdims=True)
                )  # Shape: (N, 1)

                # Inclusive value
                inclusive_value = log_sum_exp.squeeze()  # Shape: (N,)

                # Gradient of inclusive value with respect to lambda
                d_inclusive_value_d_lambda = (
                                                     -inclusive_value / lambd
                                                     + np.sum(
                                                 (exp_utilities * utilities_nest) / np.sum(exp_utilities, axis=1,
                                                                                           keepdims=True), axis=1)
                                             ) / lambd

                # Gradient for lambda: combine residuals with inclusive value term
                grad_lambda = np.sum(
                    np.sum(ymp[:, nest], axis=1) * d_inclusive_value_d_lambda
                )
                grad_lambdas.append(grad_lambda)

            # Combine gradients for feature coefficients and lambda coefficients
            grad_lambdas = np.array(grad_lambdas)  # Shape: (num_nests)
            grad = np.concatenate([grad_X, grad_lambdas])  # Shape: (K + num_nests)

        # Return negative log-likelihood and gradient
        return (-loglik, -grad) if self.return_grad else (-loglik,)


class MultiLayerNestedLogit(MultinomialLogit):
    """
    Multi-Layer Nested Logit Model (inherits from MultinomialLogit).
    Handles hierarchical nested structure of alternatives.
    """

    def __init__(self):
        super(MultiLayerNestedLogit, self).__init__()
        self.descr = "Multi-Layer Nested Logit"

    def _assign_lambda_indices(self, nests, index=0, nest_list=None):
        """
        Recursively assign indices to each nest in the hierarchy and populate the nest list.
        """
        if nest_list is None:
            nest_list = []

        for nest_name, nest in nests.items():
            # Assign index for the current nest
            self.lambda_mapping[nest_name] = index
            nest_list.append(nest_name)
            index += 1

            # Recurse into sub-nests if they exist
            if "sub_nests" in nest:
                index = self._assign_lambda_indices(nest["sub_nests"], index, nest_list)

        return index

    def setup(self, X, y, varnames=None, isvars=None, alts=None, ids=None,
              nests=None, lambdas=None, fit_intercept=False, **kwargs):
        """
        Setup the Multi-Layer Nested Logit model.
        """

        filtered_kwargs = {key: value for key, value in kwargs.items() if key not in ['lambda_mapping']}

        # Call the parent class setup method with filtered kwargs
        super().setup(X, y, varnames=varnames, isvars=isvars, alts=alts, ids=ids,
                      fit_intercept=fit_intercept, **filtered_kwargs)
        # Call the parent class setup method
        # Validate nests
        if not nests or not isinstance(nests, dict):
            raise ValueError("`nests` must be a nested dictionary representing the hierarchy of alternatives.")

        self.nests = nests

        # Initialize lambda_mapping and nest_list
        self.lambda_mapping = {}
        self.nest_list = []
        self._assign_lambda_indices(nests, nest_list=self.nest_list)

        # Ensure lambdas are provided or initialize them to default values (e.g., 1.0)
        num_nests = len(self.lambda_mapping)
        if lambdas is None:
            lambdas = np.ones(num_nests)  # Default value for lambdas
        elif isinstance(lambdas, dict):
            # Convert lambdas dictionary to a flat array using the mapping
            lambdas = np.array([lambdas.get(nest_name, 1.0) for nest_name in self.lambda_mapping])

        self.lambdas = lambdas  # Store lambdas as a flat array

        # Add lambdas to the betas array (treated as extra coefficients)
        self.betas = np.concatenate([self.betas, lambdas])
        print('lenght of betas:',len(self.betas))
        # Update coefficient names to include lambda parameters
        if varnames is None:
            varnames = []
        self.coeff_names = [self.coeff_names] + [f"lambda_{nest}" for nest in self.nest_list]
        print(self.coeff_names)
        print(
            f"Setup complete. Total nests: {num_nests}, Lambda mapping: {self.lambda_mapping}, Nest list: {self.nest_list}")

    def _initialize_lambdas(self, nests):
        """Recursively initialize lambda values for all nests."""
        for key, value in nests.items():
            if key not in self.lambdas:
                self.lambdas[key] = 1.0  # Default lambda value
            if isinstance(value, dict):
                self._initialize_lambdas(value)

    def _flatten_nests(self, nests):
        """
        Recursively flatten the nested dictionary to extract all nest names.
        """
        nest_list = []
        for key, value in nests.items():
            nest_list.append(key)
            if isinstance(value, dict):
                nest_list.extend(self._flatten_nests(value))
        return nest_list

    def compute_probabilities(self, betas, X, avail):
        """
        Compute choice probabilities for a hierarchical structure of nests.
        Handles both flat and multi-hierarchical nest structures.

        Parameters:
            betas: np.ndarray
                Coefficients for features and nest lambdas (size: K + num_nests).
            X: np.ndarray
                Feature matrix of shape (N, J, K).
            avail: np.ndarray or None
                Availability mask of shape (N, J).

        Returns:
            np.ndarray: Choice probabilities of shape (N, J).
        """
        print('lenth of b', len(betas))
        if len(X.shape) != 3:
            raise ValueError(f"X must be 3D (N, J, K). Got shape: {X.shape}")

        N, J, K = X.shape
        num_features = K

        # Separate betas for features and lambdas
        lambdas = betas[num_features:]  # Lambda coefficients for nests
        betas_X = betas[:num_features]  # Coefficients for features

        # Compute utilities: U = X @ betas
        utilities = np.einsum('njk,k->nj', X, betas_X)  # Shape: (N, J)

        def _compute_probs_recursive(nests, lambda_mapping, current_nest=None):
            """
            Recursively compute probabilities for each level of the hierarchy.
            """
            if current_nest is None:
                # Top-level nests: combine probabilities from all nests
                final_probs = np.zeros_like(utilities)  # Initialize probability array (N, J)
                inclusive_values = []  # Store inclusive values for all top-level nests

                for nest_name, nest in nests.items():
                    # Compute probabilities for each top-level nest
                    nest_probs, inclusive_value = _compute_probs_recursive(
                        nest, lambda_mapping, current_nest=nest_name
                    )
                    final_probs += nest_probs  # Add probabilities for this nest
                    inclusive_values.append(inclusive_value)

                # Compute top-level probabilities using inclusive values
                inclusive_values = np.column_stack(inclusive_values)  # Shape: (N, num_nests)
                top_lambdas = np.array([lambdas[lambda_mapping[nest_name]] for nest_name in nests.keys()])
                scaled_inclusive_values = inclusive_values * top_lambdas  # Scale inclusive values by lambda

                # Apply log-sum-exp trick for numerical stability
                max_scaled = np.max(scaled_inclusive_values, axis=1, keepdims=True)
                top_probs = np.exp(scaled_inclusive_values - max_scaled) / np.sum(
                    np.exp(scaled_inclusive_values - max_scaled), axis=1, keepdims=True
                )  # Shape: (N, num_nests)

                # Combine top-level and lower-level probabilities
                final_probs_weighted = np.zeros_like(utilities)
                for i, nest_name in enumerate(nests.keys()):
                    nest_probs, _ = _compute_probs_recursive(nests[nest_name], lambda_mapping, current_nest=nest_name)
                    final_probs_weighted += top_probs[:, i, np.newaxis] * nest_probs

                return final_probs_weighted

            if "alternatives" in nests:
                # Leaf node: compute probabilities for alternatives in the current nest
                alternatives = nests["alternatives"]
                lambda_value = lambdas[lambda_mapping[current_nest]]

                # Compute utilities for the alternatives in the current nest
                utilities_nest = utilities[:, alternatives] / lambda_value

                # Apply log-sum-exp trick for numerical stability
                max_utilities = np.max(utilities_nest, axis=1, keepdims=True)
                exp_utilities = np.exp(utilities_nest - max_utilities)
                nest_probs = exp_utilities / np.sum(exp_utilities, axis=1, keepdims=True)

                # Apply availability mask (if provided)
                if avail is not None:
                    nest_probs *= avail[:, alternatives]

                # Compute inclusive value for the current nest
                inclusive_value = max_utilities.squeeze() + np.log(np.sum(exp_utilities, axis=1))

                # Create a full probability array with zeros for unused alternatives
                full_probs = np.zeros_like(utilities)
                full_probs[:, alternatives] = nest_probs  # Assign nest probabilities to the relevant alternatives

                return full_probs, inclusive_value

            elif "sub_nests" in nests:
                # Parent node: compute probabilities for sub-nests
                lambda_value = lambdas[lambda_mapping[current_nest]]
                sub_nests = nests["sub_nests"]

                inclusive_values = []  # Store inclusive values for all sub-nests
                sub_probs = []  # Store probabilities for all sub-nests

                for sub_nest_name, sub_nest in sub_nests.items():
                    # Compute probabilities recursively for the sub-nest
                    sub_nest_probs, inclusive_value = _compute_probs_recursive(
                        sub_nest, lambda_mapping, current_nest=sub_nest_name
                    )
                    sub_probs.append(sub_nest_probs)
                    inclusive_values.append(inclusive_value)

                # Compute upper-level probabilities using inclusive values
                inclusive_values = np.column_stack(inclusive_values)  # Shape: (N, num_sub_nests)
                scaled_inclusive_values = inclusive_values * lambda_value  # Scale by lambda
                max_scaled = np.max(scaled_inclusive_values, axis=1, keepdims=True)
                upper_probs = np.exp(scaled_inclusive_values - max_scaled) / np.sum(
                    np.exp(scaled_inclusive_values - max_scaled), axis=1, keepdims=True
                )  # Shape: (N, num_sub_nests)

                # Combine upper-level and lower-level probabilities
                final_probs = np.zeros_like(utilities)
                for i, sub_prob in enumerate(sub_probs):
                    final_probs += upper_probs[:, i, np.newaxis] * sub_prob

                # Compute inclusive value for the parent nest
                inclusive_value = max_scaled.squeeze() + np.log(
                    np.sum(np.exp(scaled_inclusive_values - max_scaled), axis=1))

                return final_probs, inclusive_value

            else:
                raise ValueError(f"Invalid nest structure: {nests}")

        # Compute probabilities starting from the top-level nests
        final_probs = _compute_probs_recursive(self.nests, self.lambda_mapping)
        return final_probs


    def summarise(self, file=None):
        """
        Summarize the model results, including multi-layer nests.
        """




        # Append nest-specific coefficient names
        if hasattr(self, 'lambda_mapping') and isinstance(self.lambda_mapping, dict):
            nest_coeffs = [f"lambda_{nest}" for nest in self.lambda_mapping.keys()]
            self.coeff_names = np.concatenate([self.coeff_names, nest_coeffs])
            print(self.coeff_names)

        super().summarise(file=file)


class CrossNestedLogit(MultinomialLogit):
    """
    Cross-Nested Logit Model (inherits from MultinomialLogit).
    Handles overlapping nest structures with membership parameters (ALPHA)
    and nest scaling parameters (MU) to be estimated.
    """

    def __init__(self):
        super(CrossNestedLogit, self).__init__()
        self.descr = "Cross-Nested Logit"
        self.nests = None  # Nest definitions
        self.lambda_mapping = {}  # Mapping for scaling parameters (MU)
        self.alpha_index = None  # Shared alpha parameter index
        self.cross_names = []  # Names for cross-nested parameters

    def setup(self, X, y, varnames=None, alts=None, ids=None, nests=None, fit_intercept=False, **kwargs):
        super().setup(X, y, varnames=varnames, alts=alts, ids=ids, fit_intercept=fit_intercept, **kwargs)

        if not nests or not isinstance(nests, dict):
            raise ValueError("`nests` must be a dictionary representing the nest structure.")

        self.nests = nests

        # Initialize lambda_mapping (one lambda per nest)
        self.lambda_mapping = {nest_name: i +self.Kf for i, nest_name in enumerate(nests.keys())}

        # Initialize alpha index
        self.alpha_index = self.Kf + len(self.lambda_mapping)  # Alpha comes after lambdas

        # Total number of parameters: features + lambdas + alpha
        num_features = self.Kf + self.Kftrans
        num_lambdas = len(self.lambda_mapping)
        num_alphas = 1  # One shared alpha
        for i in range(num_lambdas):
            self.cross_names.append(f'lamba {i}')
        self.cross_names.append('lambda_mu')

        # Initialize betas: features + lambdas + alpha
        self.betas = np.concatenate(
            [
                np.random.random(num_features) * 0.01,  # Small random values for features,  # Feature coefficients (initialized to 0)
                np.ones(num_lambdas)*2,   # Lambdas (initialized to 1)
                [0.5],                  # Shared alpha (initialized to 0.5)
            ]
        )

        # Debugging: Print parameter initialization
        print(f"Initial betas: {self.betas}")
        print(f"Lambda mapping: {self.lambda_mapping}")
        print(f"Alpha index: {self.alpha_index}")

    def compute_probabilities(self, betas, X, avail):
        """
        Compute choice probabilities for each alternative.
        """
        N, J, K = X.shape  # N: observations, J: alternatives, K: features

        # Extract lambdas and alpha
        #print('betas', betas)
        #print(betas[:K])
        # this isnt rightm this should update for next beta forllowing print(betas[:K])
        #poisition should be like betas fixed, then the lamdas then lastly the indce
        #lambdas = {nest_name: betas[idx] for nest_name, idx in self.lambda_mapping.items()}
        lambdas = {name: max(betas[idx], 0.1) for name, idx in self.lambda_mapping.items()}
        #alpha = betas[self.alpha_index]  # Shared alpha
        alpha = max(0.2, min(betas[self.alpha_index], 0.8))
        #print('lambdas', lambdas)
        #print('lamdas', alpha)
        # Compute utilities
        utilities = np.einsum("njk,k->nj", X, betas[:K])
        #print(f"Utilities: {utilities}")  # Check for NaN, inf, or extreme values
        # Compute inclusive values for each nest
        inclusive_values = np.zeros((N, len(self.nests)))
        for nest_idx, (nest_name, nest_info) in enumerate(self.nests.items()):
            #lambda_value = lambdas[nest_name]
            lambda_value = max(lambdas[nest_name], 1e-15)  # Avoid division by zero
            #print(lambda_value)
            scaled_utilities = np.zeros_like(utilities)


            for alt in nest_info["alternatives"]:
                scaled_utilities[:, alt] = utilities[:, alt] * alpha / lambda_value
                scaled_utilities = np.clip(scaled_utilities, -1e10, 1e10)
                # print(f"Scaled utilities for alternative {alt} in nest {nest_name}: {scaled_utilities[:, alt]}")

            max_utilities = np.max(scaled_utilities, axis=1, keepdims=True)
            exp_utilities = np.exp(scaled_utilities - max_utilities)
            #print(f"Exponentiated utilities: {exp_utilities}")
            log_sum_exp = max_utilities.squeeze() + np.log(np.sum(exp_utilities, axis=1))
            inclusive_values[:, nest_idx] = log_sum_exp


        # Compute final probabilities
        final_probs = np.zeros((N, J))
        max_utility = np.max(utilities, axis=1, keepdims=True)  # Stabilize utilities
        utilities -= max_utility  # Subtract max utility for stability

        for j in range(J):
            total_contribution = 0
            for nest_idx, (nest_name, nest_info) in enumerate(self.nests.items()):
                if j in nest_info["alternatives"]:
                    total_contribution += inclusive_values[:, nest_idx] * alpha

            final_probs[:, j] = np.exp(utilities[:, j] + total_contribution)

        # Normalize probabilities
        final_probs /= np.sum(final_probs, axis=1, keepdims=True)

        # Apply availability mask if provided
        if avail is not None:
            final_probs *= avail
        #print(f"Final probabilities: {final_probs}")
        return final_probs

    def get_loglik_and_gradient(self, betas, X, y, weights=None, avail=None):
        self.total_fun_eval += 1

        # Compute probabilities
        p = self.compute_probabilities(betas, X, avail)
        #print(f"Probabilities: {p}")  # Debug probabilities

        # Prevent probabilities from becoming exactly 0
        p = np.maximum(p, 1e-15)

        # Convert y to indices (assuming one-hot encoding for y)
        y = np.argmax(y, axis=1)

        # Compute log-likelihood per observation
        loglik_obs = np.log(p[np.arange(len(y)), y])

        #print(f"loglik_obs: {loglik_obs}")  # Debug log-likelihood per observation

        # Handle weights
        if weights is None:
            weights = np.ones(len(y))
        loglik = np.sum(loglik_obs*weights)
        loglik = np.nan_to_num(loglik, -1000000, -1000000, -1000000)

        # Debugging: Print log-likelihood
        print(f"Total Log-Likelihood: {loglik}")

        # Placeholder for gradient computation (to be implemented)
        grad = None

        return (-loglik, -grad) if self.return_grad else (-loglik,)

    def summarise(self, file=None):
        """
        Summarize the model results, including cross-nested structure.
        """
        print(f"Summary of Cross-Nested Logit Model:")
        print(f"Nests: {self.nests}")
        print(f"Lambda mapping: {self.lambda_mapping}")
        print(f"Alpha index: {self.alpha_index}")
        self.coeff_names = np.concatenate([self.coeff_names, self.cross_names])
        super().summarise(file=file)
'''
    def summarise(self, file=None):
        """
        Summarize the model results, including cross-nested structure.
        """
        print(f"Summary of Cross-Nested Logit Model:")
        print(f"Nests: {self.nests}")
        #print(f"Lambda coefficients (MU): {self.lambdas}")
        #print(f"Nest membership parameters (ALPHA): {self.alphas}")
        print('self')
        #self.Xnames = [self.Xnames, self.nest_names]
        self.coeff_names = np.concatenate([self.coeff_names, self.cross_names])
        super().summarise(file=file)
'''