from dataclasses import dataclass, field
from itertools import product
import numpy as np
import csv


# =========
# I/O Utils
# =========
def _detect_separator(path: str) -> str:
    """Try to automatically detect CSV separator by reading the first line."""
    with open(path, "r") as f:
        first_line = f.readline()
    for sep in [",", ";", "\t"]:
        if sep in first_line:
            return sep
    return ","  # default fallback


@dataclass(slots=True)
class FactorialData:
    """
    A class representing factorial experiment data with multiple responses and replicates.
    """

    factors: np.ndarray = field(default_factory=lambda: np.array([]))
    responses: np.ndarray = field(default_factory=lambda: np.array([]))
    factor_names: list[str] = field(default_factory=list)
    response_names: list[str] = field(default_factory=list)

    # ====================
    # Magic methods
    # ====================
    def __str__(self) -> str:
        # Header
        header = ";".join([f"factor: {name}" for name in self.factor_names])
        header += ";" + ";".join([f"resp: {name}" for name in self.response_names])

        lines = [header]
        n_runs = self.factors.shape[0]

        for run_idx in range(n_runs):
            factor_values = ";".join(str(int(val)) for val in self.factors[run_idx])
            response_values = []
            for resp_name in self.response_names:
                replicates = self.get_run(resp_name, run_idx)
                replicates_str = "[" + ", ".join(f"{r:.2f}" for r in replicates) + "]"
                response_values.append(replicates_str)
            line = factor_values + ";" + ";".join(response_values)
            lines.append(line)

        return "\n".join(lines)

    def __repr__(self) -> str:
        """Official string representation showing dimensions"""
        return (
            f"FactorialData(factors={self.factors.shape}, "
            f"responses={self.responses.shape}, "
            f"factors={self.factor_names}, "
            f"responses={self.response_names})"
        )

    # ====================
    # Private methods
    # ====================
    def _get_base_interaction_combinations(
        self, factor_subset: list[str]
    ) -> list[tuple[int, ...]]:
        """Base method to get factor level combinations (private)."""
        if not factor_subset:
            raise ValueError("factor_subset cannot be empty.")

        factor_indices = [self.factor_names.index(f) for f in factor_subset]
        relevant_levels = self.factors[:, factor_indices]
        unique_levels = [
            np.unique(relevant_levels[:, i]) for i in range(len(factor_subset))
        ]
        return list(product(*unique_levels))

    def _reshape_response(self, response_name: str) -> np.ndarray:
        """
        Reshape a specific response's data into factorial structure with replicates.

        Args:
            response_name: Name of the response to reshape ('Tempo' or 'Performance')

        Returns:
            Array of shape (2, 2, 2, 2, n_replicates) for a 2^4 design
            where the last dimension contains all replicates

        Raises:
            ValueError: If invalid response name
        """
        if response_name not in self.response_names:
            raise ValueError(f"Invalid response name. Available: {self.response_names}")

        # Get all replicates for this response across all runs
        n_responses = len(self.response_names)
        resp_idx = self.response_names.index(response_name)
        n_replicates = self.responses.shape[1] // n_responses
        response_data = self.responses[
            :, resp_idx * n_replicates : (resp_idx + 1) * n_replicates
        ]

        # Reshape to factorial structure
        factorial_shape = tuple([2] * len(self.factor_names)) + (n_replicates,)
        return response_data.reshape(factorial_shape)

    def _reshape_responses(self) -> np.ndarray:
        """
        Reshape all responses into factorial structure with replicates.
        Returns an array of shape (2, 2, 2, 2, n_replicates, n_responses)
        """
        n_replicates = self.responses.shape[1] // len(self.response_names)
        n_factors = len(self.factor_names)
        n_responses = len(self.response_names)

        # Cria array final
        final_shape = tuple([2] * n_factors) + (n_replicates, n_responses)
        reshaped_all = np.zeros(final_shape)

        for resp_idx, resp_name in enumerate(self.response_names):
            reshaped_single = self._reshape_response(
                resp_name
            )  # (2,2,2,2,n_replicates)
            reshaped_all[..., :, resp_idx] = reshaped_single  # insert o col

        return reshaped_all

    # ====================
    # Public methods
    # ====================
    def get_interaction_combinations(
        self, factor_subset: list[str]
    ) -> list[tuple[int, ...]]:
        """Get unique factor level combinations."""
        return self._get_base_interaction_combinations(factor_subset)

    def get_interaction_combinations_with_replicates(
        self, factor_subset: list[str], n_replicates: int | None = None
    ) -> list[tuple[int, ...]]:
        """Get factor level combinations expanded for replicates."""
        base_combinations = self._get_base_interaction_combinations(factor_subset)
        n_replicates = n_replicates or self.get_n_replicates()
        return [comb for comb in base_combinations for _ in range(n_replicates)]

    def get_response_data(self, response_name: str) -> np.ndarray:
        """
        Get all data for a specific response across all runs and replicates.

        Args:
            response_name: Name of the response variable

        Returns:
            Flat array of all values for this response (n_runs × n_replicates)
        """
        resp_idx = self.response_names.index(response_name)
        n_replicates = self.get_n_replicates()
        return self.responses[
            :, resp_idx * n_replicates : (resp_idx + 1) * n_replicates
        ]

    def get_factor_levels(self, factor_name: str) -> np.ndarray:
        """
        Get all levels of a factor across runs.

        Args:
            factor_name: Name of the factor

        Returns:
            Array of factor levels (n_runs,)
        """
        factor_idx = self.factor_names.index(factor_name)
        return self.factors[:, factor_idx]

    def get_run_factors(self, run_index: int) -> dict[str, int]:
        """
        Get factor levels for a specific run.

        Args:
            run_index: Index of the experimental run

        Returns:
            Dictionary mapping factor names to their levels in this run
        """
        return {
            name: int(self.factors[run_index, i])
            for i, name in enumerate(self.factor_names)
        }

    def get_all_response_values(self) -> dict[str, np.ndarray]:
        """
        Get all response values organized by response name.

        Returns:
            Dictionary mapping each response name to its data array
            (n_runs × n_replicates)
        """
        return {name: self.get_response_data(name) for name in self.response_names}

    def get_response_stats(self, response_name: str) -> dict[str, float]:
        """
        Calculate basic statistics for a response variable.

        Args:
            response_name: Name of the response variable

        Returns:
            Dictionary with:
            - 'mean': overall mean
            - 'std': standard deviation
            - 'min': minimum value
            - 'max': maximum value
        """
        data = self.get_response_data(response_name)
        return {
            "mean": float(np.mean(data)),
            "std": float(np.std(data)),
            "min": float(np.min(data)),
            "max": float(np.max(data)),
        }

    def filter_by_factor_level(
        self, factor_name: str, level: int
    ) -> dict[str, np.ndarray | dict[str, np.ndarray]]:
        """
        Filter runs by a specific factor level.

        Args:
            factor_name: Factor to filter by
            level: Level value to filter for

        Returns:
            Dictionary with:
            - 'runs': array of run indices matching the criteria
            - 'responses': dictionary of response arrays for these runs
        """
        factor_idx = self.factor_names.index(factor_name)
        mask = self.factors[:, factor_idx] == level
        run_indices = np.where(mask)[0]

        result: dict[str, np.ndarray | dict[str, np.ndarray]] = {
            "runs": run_indices,
            "responses": {},
        }

        for name in self.response_names:
            data = self.get_response_data(name)
            result["responses"][name] = data[mask, :]  # type: ignore

        return result

    def get_condition_averages(self) -> dict[str, dict[tuple, float]]:
        """
        Calculate average response values for each experimental condition.

        Returns:
            Dictionary mapping response names to dictionaries where:
            - Key: tuple of factor levels (A_level, B_level, ...)
            - Value: average response for that condition
        """
        averages: dict[str, dict[tuple, float]] = {}
        y_reshaped = self._reshape_responses()

        for resp_idx, resp_name in enumerate(self.response_names):
            averages[resp_name] = {}
            resp_data = y_reshaped[..., resp_idx]

            # Iterate through all possible factor combinations
            for indices in np.ndindex(resp_data.shape[:-1]):
                condition = tuple(
                    self.factors[indices, i] for i in range(len(self.factor_names))
                )
                avg = np.mean(resp_data[indices])
                averages[resp_name][condition] = float(avg)

        return averages

    def get_n_replicates(self) -> int:
        """
        Returns the number of replicates for each response in each experimental run.

        Returns:
            Integer representing the number of replicates

        Example:
            If your data has 3 replicates for each response in each run,
            this will return 3
        """
        return self.responses.shape[1] // len(self.response_names)

    def get_run(self, response_name: str, run_index: int) -> list[float]:
        """
        Get all replicate values for a specific response at a specific experimental run.

        Args:
            response_name: Name of the response ('Tempo' or 'Performance')
            run_index: Index of the experimental run (0 to 15 for a 2^4 design)

        Returns:
            List of replicate values for the requested response at the specified run

        Raises:
            ValueError: If invalid response name or run index
        """
        # Validate inputs
        if response_name not in self.response_names:
            raise ValueError(f"Invalid response name. Available: {self.response_names}")

        if not 0 <= run_index < self.factors.shape[0]:
            raise ValueError(
                f"Run index must be between 0 and {self.factors.shape[0]-1}"
            )

        # Get response index and number of replicates
        resp_idx = self.response_names.index(response_name)
        n_responses = len(self.response_names)
        n_replicates = self.responses.shape[1] // n_responses

        # Calculate start and end columns for this response
        start_col = resp_idx * n_replicates
        end_col = start_col + n_replicates

        # Extract and return the replicates
        return list(self.responses[run_index, start_col:end_col])

    def reshape_per_response(self) -> list[np.ndarray]:
        """
        Transforma o array flat de responses em uma lista de arrays com a estrutura dimensional correta.

        Retorna:
            List[np.ndarray]: Lista contendo um array por resposta, cada um com shape
                            (n_runs, n_replicates) ou similar, conforme a estrutura experimental
        """
        if len(self.responses) == 0:
            return []

        n_runs = self.factors.shape[0]
        n_responses = len(self.response_names)
        total_columns = (
            self.responses.shape[1]
            if self.responses.ndim > 1
            else self.responses.shape[0]
        )

        # Calcula o número de réplicas por resposta
        n_replicates = total_columns // n_responses

        # Divide o array flat em arrays separados para cada resposta
        reshaped = []
        for i in range(n_responses):
            start_col = i * n_replicates
            end_col = start_col + n_replicates

            # Extrai e remodela os dados para esta resposta
            resp_data = (
                self.responses[:, start_col:end_col]
                if self.responses.ndim > 1
                else self.responses[start_col:end_col]
            )

            # Redimensiona para (n_runs, n_replicates) ou outra estrutura conforme necessário
            resp_array = np.array(resp_data).reshape(n_runs, n_replicates)
            reshaped.append(resp_array)

        return reshaped


# ====================
# Factory Functions
# ====================
def read_csv(file_path: str, separator: str | None = None) -> FactorialData:
    """
    Load factorial data from CSV supporting:
    - Multiple factors/responses
    - Replicates in square brackets or single values
    - -1/+1 factor level coding
    - Flexible separators (autodetected)

    Supported formats:
    1. With replicates:
       factor:A;factor:B;resp:Y;resp:Z
       -1;-1;[1.1,2.2,3.3];[4.4,5.5,6.6]

    2. Single responses:
       factor:A,factor:B,resp:Y
       -1,-1,820
    """

    def parse_value(val: str) -> list[float]:
        """Parse single float or bracketed replicates"""
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            return [float(x.strip()) for x in val[1:-1].split(",")]
        return [float(val)]  # Single value as 1-item list

    # Detect separator if not provided
    sep = separator or _detect_separator(file_path)

    factors = []
    responses = []
    factor_names = []
    response_names = []

    with open(file_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=sep)
        headers = [h.strip() for h in next(reader)]

        # Parse headers
        for header in headers:
            if "factor:" in header.lower():
                factor_names.append(header.split(":")[-1].strip())
            elif "resp:" in header.lower():
                response_names.append(header.split(":")[-1].strip())

        # Parse data rows
        for row in reader:
            if not row:
                continue

            n_factors = len(factor_names)
            row_factors = [float(row[i].strip()) for i in range(n_factors)]

            # Process responses (single or multiple with replicates)
            row_responses = []
            for val in row[n_factors:]:
                row_responses.extend(parse_value(val))

            factors.append(row_factors)
            responses.append(row_responses)

    # Convert to numpy arrays
    factors_array = np.array(factors)
    responses_array = np.array(responses)

    # Reshape responses if replicates exist
    if responses_array.shape[1] > len(response_names):
        n_replicates = responses_array.shape[1] // len(response_names)
        responses_array = responses_array.reshape(
            -1, len(response_names) * n_replicates
        )

    return FactorialData(
        factors=factors_array,
        responses=responses_array,
        factor_names=factor_names,
        response_names=response_names,
    )
