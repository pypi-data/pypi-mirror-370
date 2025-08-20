from dataclasses import dataclass, field
from itertools import combinations
from typing import Any, Literal
import numpy as np
from scipy import stats
import factorial2kr.factorial_data as fd


@dataclass(slots=True)
class Factorial:
    """Class representing a generic factorial experiment design."""

    data: fd.FactorialData = field(default_factory=fd.FactorialData)

    # ====================
    # Magic methods
    # ====================
    def __repr__(self) -> str:
        return repr(self.data)

    def __str__(self) -> str:
        return str(self.data)

    def _get_reshaped_responses(self) -> np.ndarray:
        """Helper method to get properly reshaped response data"""
        return (
            self.data._reshape_responses()
        )  # shape: (levels..., n_replicates, n_responses)

    # ====================
    # Private methods
    # ====================
    def _calculate_means(self, dimensions_to_reduce: tuple) -> np.ndarray:
        """Calculate means reducing specified dimensions."""
        return np.mean(self._get_reshaped_responses(), axis=dimensions_to_reduce)

    def _calculate_ss(self, means: np.ndarray, grand_mean: np.ndarray, n_obs: int) -> np.ndarray:
        """Calculate sum of squares given level means."""
        return np.sum(n_obs * (means - grand_mean) ** 2)

    def _get_interaction_name(self, combo: tuple) -> str:
        """Convert factor indices combo to interaction name (e.g., (0,1) -> 'A,B')."""
        return ",".join(self.data.factor_names[i] for i in combo)

    def get_interactions(self) -> dict[str, np.ndarray]:
        """
        Gera todas as interações possíveis entre os fatores.

        Retorna:
            Dict[str, np.ndarray]: Dicionário onde:
                - Chave: nome da interação (ex: 'AB', 'ACD')
                - Valor: vetor de contraste da interação (array numpy)
        """
        if len(self.data.factor_names) < 2:
            return {}

        interactions: dict[str, np.ndarray] = {}

        # Gera interações de ordem 2 até n_factors
        for order in range(2, len(self.data.factor_names) + 1):
            for factor_indices in combinations(
                range(len(self.data.factor_names)), order
            ):
                # Nome da interação (ex: 'AB' para fatores A e B)
                interaction_name = "".join(
                    [self.data.factor_names[i] for i in factor_indices]
                )

                # Calcula o vetor de contraste (produto elemento a elemento)
                contrast = np.ones(self.data.factors.shape[0])
                for i in factor_indices:
                    contrast *= self.data.factors[:, i]

                interactions[interaction_name] = contrast

        return interactions

    # ====================
    # Public methods
    # ====================
    def ssy(self) -> dict[str, np.ndarray]:
        """
        Sum of squares of the measured values (SSY) for each response.
        """
        result = {}
        n_responses = len(self.data.response_names)
        for i, resp_name in enumerate(self.data.response_names):
            y = self.data.responses[:, i::n_responses]
            result[resp_name] = np.sum(y**2)
        return result

    def ss0(self) -> dict[str, np.ndarray]:
        """
        Sum of squares of the mean (SS0) for each response.
        """
        result = {}
        n_responses = len(self.data.response_names)
        for i, resp_name in enumerate(self.data.response_names):
            y = self.data.responses[:, i::n_responses]
            mean_y = np.mean(y)
            n_obs = y.size
            result[resp_name] = n_obs * mean_y**2
        return result

    def sst(self) -> dict[str, np.ndarray]:
        """
        Total sum of squares around the mean (SST) for each response.
        """
        ssy_vals = self.ssy()
        ss0_vals = self.ss0()
        return {
            resp: ssy_vals[resp] - ss0_vals[resp] for resp in self.data.response_names
        }

    def sse(self) -> dict[str, np.ndarray]:
        """
        Sum of squares due to error (SSE) for each response.
        """
        result = {}
        y_reshaped = (
            self._get_reshaped_responses()
        )  # shape: (2,2,2,2,n_replicates,n_responses)

        for i, resp_name in enumerate(self.data.response_names):
            y = y_reshaped[..., i]  # shape: (2,2,2,2,n_replicates)
            mean_per_comb = np.mean(y, axis=-1, keepdims=True)  # média por run
            result[resp_name] = np.sum((y - mean_per_comb) ** 2)

        return result

    def ssf(self) -> dict[str, dict[str, np.ndarray]]:
        """Compute SS for main effects."""
        result: dict[str, dict[str, np.ndarray]] = {}
        y = self._get_reshaped_responses()
        n_factors = len(self.data.factor_names)
        n_replicates = y.shape[-2]
        grand_means = self._calculate_means(tuple(range(n_factors)) + (-2,))

        for factor_idx, factor in enumerate(self.data.factor_names):
            result[factor] = {}
            other_dims = tuple(d for d in range(n_factors) if d != factor_idx) + (-2,)
            level_means = self._calculate_means(other_dims)
            n_obs = 2 ** (n_factors - 1) * n_replicates

            for resp_idx, resp_name in enumerate(self.data.response_names):
                ss = self._calculate_ss(
                    level_means[:, resp_idx], grand_means[resp_idx], n_obs
                )
                result[factor][resp_name] = ss

        return result

    def ssi(self) -> dict[str, dict[str, np.ndarray]]:
        """Compute SS for interactions."""
        result: dict[str, dict[str, np.ndarray]] = {}
        y = self._get_reshaped_responses()
        n_factors = len(self.data.factor_names)
        grand_means = self._calculate_means(tuple(range(n_factors)) + (-2,))
        main_effects = self.ssf()

        for order in range(2, n_factors + 1):
            for combo in combinations(range(n_factors), order):
                interaction_name = self._get_interaction_name(combo)
                result[interaction_name] = {}

                other_dims = tuple(d for d in range(n_factors) if d not in combo) + (
                    -2,
                )
                int_means = self._calculate_means(other_dims)
                n_obs = 2 ** (n_factors - order) * y.shape[-2]

                for resp_idx, resp_name in enumerate(self.data.response_names):
                    ss = self._calculate_ss(
                        int_means[..., resp_idx], grand_means[resp_idx], n_obs
                    )

                    # Subtract lower-order effects
                    for k in range(1, order):
                        for sub_combo in combinations(combo, k):
                            sub_name = self._get_interaction_name(sub_combo)
                            ss -= main_effects.get(sub_name, {resp_name: 0})[resp_name]

                    result[interaction_name][resp_name] = ss

        return result

    def variance_explained(self) -> dict[str, dict[str, np.ndarray]]:
        """Variance decomposition."""
        sst = self.sst()
        components = {**self.ssf(), **self.ssi()}
        result: dict[str, dict[str, np.ndarray]] = {}

        for component, resp_dict in components.items():
            result[component] = {
                resp: (ss / sst[resp]) * 100 for resp, ss in resp_dict.items()
            }

        # Add residual variance
        sse = self.sse()
        result["residual"] = {
            resp: (sse[resp] / sst[resp]) * 100 for resp in self.data.response_names
        }

        return result

    def get_replications(self) -> int:
        return self.data.get_n_replicates()

    def get_n(self) -> int:
        return 2 ** len(self.data.factor_names)

    def degree_freedom(self) -> int:
        """# Degrees of freedom for the t-distribution"""
        replications = self.get_replications()
        n = self.get_n()
        f = n * (replications - 1)
        return f

    def se(self) -> dict[str, np.ndarray]:
        """Standard error of effects for each response

        Returns:
            dict[str, float]: Dictionary with standard error for each response
        """
        sse_dict = self.sse()
        n = self.get_n()
        replications = self.get_replications()

        denominator = n * (replications - 1)
        se_dict = {}

        for response, sse in sse_dict.items():
            se_dict[response] = np.sqrt(sse / denominator)

        return se_dict

    def sq_i(self) -> dict[str, np.ndarray]:
        """Variance of the effects for each response

        Returns:
            dict[str, float]: Dictionary with variance of effects for each response
        """
        se_dict = self.se()  # Get standard errors for each response
        n = self.get_n()
        reps = self.get_replications()

        denominator = n * reps

        s_qi_dict = {}
        for response, se in se_dict.items():
            s_qi_dict[response] = se / np.sqrt(denominator)

        return s_qi_dict

    def mean_responses(self) -> list[np.ndarray]:
        """Mean responses for each combination"""

        means = []
        responses = self.data.reshape_per_response()
        for resp in responses:
            mean = np.mean(resp, axis=1)
            means.append(mean)

        return means

    def distribution(
        self, confidence_level: float = 0.95
    ) -> tuple[float, Literal["z-distribution", "t-distribution"]]:
        replications = self.get_replications()
        df = self.get_n() * (replications - 1)

        # Automatically select t or z for the mean effect q_0 based on the number of replications
        if replications >= 30:
            # Use z-distribution for large sample sizes
            alpha_q0 = stats.norm.ppf(1 - (1 - confidence_level) / 2)
            distribution_type: Literal["z-distribution", "t-distribution"] = (
                "z-distribution"
            )
        else:
            # Use t-distribution for smaller sample sizes
            alpha_q0 = stats.t.ppf(1 - (1 - confidence_level) / 2, df)
            distribution_type = "t-distribution"

        return alpha_q0, distribution_type
    
    def ci(self, confidence_level: float = 0.95) -> dict[str, dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]]]:
        """
        Calcula intervalos de confiança para o efeito médio e todos os efeitos fatoriais,
        retornando para cada resposta em formato (lower, estimate, upper).
        """

        alpha, _ = self.distribution(confidence_level)  # valor crítico (z ou t)
        s_q0_dict = self.sq_i()  # dict com erros padrão para cada efeito
        
        ci_dict = {}

        # 1. Efeito médio
        q_0 = np.mean(self.mean_responses())
        s_q0 = self.sq_i()
        s_qi = self.sq_i()


        mean_ci = {}
        for i, resp_name in enumerate(self.data.response_names):
            lower = round(q_0 - alpha * s_q0[resp_name], 2)
            estimate = q_0
            upper = round(q_0 + alpha * s_q0[resp_name], 2)
            mean_ci[resp_name] = (lower, estimate, upper)
        ci_dict["mean"] = mean_ci

        # 2. Efeitos fatoriais
        effects = self.effects()  # dict: efeito -> array de valores por resposta

        for effect_name, effect_values in effects.items():
            effect_ci = {}
            for i, resp_name in enumerate(self.data.response_names):
                lower = round(effect_values[i] - alpha * s_qi[resp_name], 2)
                estimate = effect_values[i]
                upper = round(effect_values[i] + alpha * s_qi[resp_name], 2)
                effect_ci[resp_name] = (lower, estimate, upper)

            ci_dict[effect_name] = effect_ci

        return ci_dict


    def effects(self) -> dict[str, np.ndarray]:
        """
        Calcula os efeitos para todos os fatores e interações para cada resposta.

        Returns:
            Dict[str, np.ndarray]: Dicionário onde:
                - Chaves são nomes de efeitos (ex: 'A', 'B', 'AB')
                - Valores são arrays de efeitos para cada resposta
        """
        mean_resps = np.array(self.mean_responses())  # shape (n_responses, n_runs)
        factors = self.data.factors                   # shape (n_runs, n_factors)
        interactions = self.get_interactions()

        n_runs = factors.shape[0]

        effects = {}

        # Para cada fator
        for i, factor_name in enumerate(self.data.factor_names):
            contrast = factors[:, i]               # shape (n_runs,)
            # Multiplica: (n_responses, n_runs) * (n_runs,) → broadcasting
            # Soma ao longo dos runs (axis=1) → vetor (n_responses,)
            effect = np.sum(mean_resps * contrast, axis=1) / n_runs
            effects[factor_name] = effect          # array com efeito por resposta

        # Para cada interação
        for interaction_name, contrast in interactions.items():
            # contrast: shape (n_runs,)
            effect = np.sum(mean_resps * contrast, axis=1) / n_runs
            effects[interaction_name] = effect    # array com efeito por resposta

        return effects

    def anova(self) -> dict:
        """
        Generate a complete ANOVA table for all responses.

        Returns:
            dict: Dictionary containing ANOVA components:
                - 'factors': Sum of squares for main effects, mapping factor names
                            to a list of SS values per response.
                - 'interactions': Sum of squares for interactions, mapping
                                factor tuples to a list of SS values per response.
                - 'responses': Total sum of squares for each response (SSY), as a list.
                - 'ss0': Sum of squares of the mean (SS0) for each response, as a list.
                - 'sse': Sum of squares due to error (SSE) for each response, as a list.
                - 'sst': Total sum of squares (SST) for each response, as a list.
        """
        return {
            "factors": self.ssf(),
            "interactions": self.ssi(),
            "responses": self.ssy(),
            "ss0": self.ss0(),
            "sse": self.sse(),
            "sst": self.sst(),
        }
    
    def sumarry(self, confidence_level: float = 0.95) -> None:
        # Sum of Squares (Factorial)
        print("=== Sum of Squares (Factorial) ===")
        for factor, values in self.ssf().items():
            print(f"{factor}:")
            for key, value in values.items():
                print(f"  {key}: {value:.2f}")

        # Sum of Squares (Interactions)
        print("\n=== Sum of Squares (Interactions) ===")
        for interaction, values in self.ssi().items():
            print(f"{interaction}:")
            for key, value in values.items():
                print(f"  {key}: {value:.2f}")

        # Grand Mean Sum of Squares
        print("\n=== SS0 (Sum of Squares of the Grand Mean) ===")
        for key, value in self.ss0().items():
            print(f"{key}: {value:.2f}")

        # Error Sum of Squares
        print("\n=== SSE (Sum of Squares for Errors) ===")
        for key, value in self.sse().items():
            print(f"{key}: {value:.2f}")

        # Total Sum of Squares
        print("\n=== SST (Total Sum of Squares) ===")
        for key, value in self.sst().items():
            print(f"{key}: {value:.2f}")

        # Confidence Intervals
        CI = self.ci(confidence_level)
        conf_percent = int(confidence_level * 100)
        _, dist_type = self.distribution(confidence_level)

        print(f"\n=== {conf_percent}% Confidence Intervals (using {dist_type}) ===")

        for effect_name, resp_dict in CI.items():
            print(f"\nEffect: {effect_name}")
            for resp_name, (lower, estimate, upper) in resp_dict.items():
                print(f"  Response '{resp_name}': [{lower}, {estimate}, {upper}]")

        # Variance Explained
        print("\n=== Variance Explained (%) ===")
        for source, values in self.variance_explained().items():
            print(f"{source}:")
            for key, value in values.items():
                print(f"  {key}: {value:.2f}%")


# ====================
# Factory Functions
# ====================
def read_csv(file_path: str, separator: str | None = None) -> Factorial:
    """
    Factory function: create Factorial from CSV file.

    Args:
        file_path: Path to CSV file
        separator: Column separator (autodetected if None)

    Returns:
        Factorial instance with loaded data
    """
    data = fd.read_csv(file_path, separator)
    return from_factorial_data(data)


def from_factorial_data(data: fd.FactorialData) -> Factorial:
    """
    Factory function: wrap an existing FactorialData into a Factorial.

    Args:
        data: Prepared FactorialData object

    Returns:
        New Factorial instance
    """
    return Factorial(data)
