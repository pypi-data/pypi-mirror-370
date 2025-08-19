import numpy as np

from dataclasses import dataclass, field
from loguru import logger
from scipy.interpolate import splprep, splev


@dataclass
class Centerline:
    """
    Class representing a centerline for a vessel.
    """

    label: int
    vessel: str
    coordinates: np.ndarray
    _differences: np.ndarray = field(init=False, repr=False, default=None)
    _segment_lengths: np.ndarray = field(init=False, repr=False, default=None)
    _cumulative_lengths: np.ndarray = field(init=False, repr=False, default=None)
    _length: float = field(init=False, repr=False, default=None)
    u: np.ndarray = field(init=True, repr=False, default=None)
    tck: np.ndarray = field(init=True, repr=False, default=None)
    inflection_points: np.ndarray = field(init=True, repr=False, default=None)

    def __call__(self):
        """
        Return the centerline coordinates.
        """
        return self.coordinates

    def __len__(self):
        """
        Return the number of points in the centerline.
        """
        return len(self.coordinates)

    def len(self) -> int:
        return len(self.coordinates)

    @property
    def differences(self) -> float:
        if self._differences is None:
            self._differences = np.diff(self.coordinates, axis=0)
        return self._differences

    @property
    def segment_lengths(self) -> np.ndarray:
        if self._segment_lengths is None:
            self._segment_lengths = np.sqrt(np.sum(self.differences**2, axis=1))
        return self._segment_lengths

    @property
    def cumulative_lengths(self) -> np.ndarray:
        if self._cumulative_lengths is None:
            self._cumulative_lengths = np.concatenate(
                ([0], np.cumsum(self.segment_lengths))
            )
        return self._cumulative_lengths

    @property
    def length(self) -> float:
        # This is the length in voxel space - not in physical space. Need to adjust for spacing if physical length is desired.
        if self._length is None:
            self._length = self.cumulative_lengths[-1]
        return self._length

    def _reset_properties(self):
        """
        Reset all cached properties to force recalculation.
        """
        self._differences = None
        self._segment_lengths = None
        self._cumulative_lengths = None
        self._length = None

    def resample_with_spline(
        self, target_points: int, smoothing: float = 1.0, degree: int = 3
    ):
        """
        Resample centerline using B-spline interpolation for smoother results.

        Args:
            target_points: Number of points in resampled centerline
            smoothing: Smoothing factor (0 = interpolation, >0 = approximation)
            degree: Spline degree (1=linear, 2=quadratic, 3=cubic)
        """
        if target_points <= 0:
            raise ValueError("Target number of points must be greater than zero.")

        if len(self.coordinates) < degree + 1:
            raise ValueError(
                f"Need at least {degree + 1} points for degree {degree} spline"
            )

        # Prepare coordinates for splprep (transpose for per-dimension arrays)
        centerline = self.coordinates
        coords_t = centerline.T
        # Get the u parameter
        dists = np.linalg.norm(np.diff(centerline, axis=0), axis=1)
        u = np.concatenate(([0], np.cumsum(dists)))
        u /= u[-1]
        # Fit B-spline to the centerline
        # u is the parameter array, automatically computed based on chord length
        m = len(centerline)
        min_s = m - np.sqrt(2 * m)
        max_s = m + np.sqrt(2 * m)
        s = smoothing * len(centerline)
        if s < min_s:
            logger.warning("spline smoothing factor `s` is smaller than recommended")
        elif s > max_s:
            logger.warning("spline smoothing factor `s` is greater than recommended!")
        tck, u = splprep(coords_t, u=u, s=s, k=degree)
        # Generate new parameter values for resampling
        u_new = np.linspace(0, 1, target_points)
        # Evaluate spline at new parameter values
        resampled_coords = splev(u_new, tck)
        resampled_coords = np.array(resampled_coords).T.round().astype(int)
        # Update the centerline coordinates
        self.coordinates = resampled_coords
        self.u = u_new
        self.tck = tck
        self._reset_properties()
        return self

    def calculate_tangent_vectors(self):
        """
        Calculate tangent vectors, normals, and binormals for the centerline.
        Returns:
            tangents: Tangent vectors at each point
            normals: Normal vectors at each point
            binormals: Binormal vectors at each point
        """
        if self.tck is None:
            raise ValueError(
                "Centerline must be resampled with a spline before calculating tangent vectors."
            )
        # Evaluate the spline to get the tangent vectors
        tangents = np.array(splev(self.u, self.tck, der=1)).T
        tangents /= np.linalg.norm(tangents, axis=1, keepdims=True)
        self.tangents = tangents
        return self

    def get_indices_within_dimensional_coordinates(
        self, start: int = None, end: int = None, dim: int = 0
    ) -> list[int]:
        """
        Method to extract a specific range of indices of a centerline from a start and end coordinate in a specific dimension.

        Parameters:
            start: int - the starting coordinate in the specified dimension (inclusive). If None - assumes the start of the dimension (0)
            end: int - the ending coordinate in the specified dimension (inclusive). If None - will be set to self.coordinates.max(dim) + 1
            dim: int - the dimension to match indices to the centerline is. Default is 0, which is z-dimension in mircat-v2
        Returns:
            a list containing the indices of the centerline that are within the range in the specified dimension.

        The start and end coordinates are ***inclusive*** in this method, example:
        If you had a coordinate in the centerline with the value of 5, and a start or end coordinate of 5, that point would be considered valid
        """
        if start is None:
            start = 0
        if end is None:
            end = self.coordinates.max(dim)
        assert start < end
        valid_indicies: list[int] = []
        for idx, coordinate in enumerate(self.coordinates):
            if start <= coordinate[dim] < end:
                valid_indicies.append(idx)
        return valid_indicies

    def calculate_tortuosity(self, start_idx=None, end_idx=None) -> dict:
        """
        Caclulate the totuosity index of the centerline, optionally from a specific start and end index

        Parameters:
            start_idx: The index of the centerline to start from (inclusive). Defaults to 0
            end_idx: The index of the centerline to end on (non-inclusive). Defaults to entire centerline
        Returns:
            A dictionary containing the measured tortuosity metrics.
        """
        if self.inflection_points is None:
            self.calculate_inflection_points()
        if start_idx is None:
            start_idx = 0
        if end_idx is None:
            end_idx = len(self.coordinates)
        tortuosity_coords = self.coordinates[start_idx:end_idx]
        inflection_points_in_range = np.array(
            [
                x
                for x in set(tuple(x) for x in tortuosity_coords)
                & set(tuple(x) for x in self.inflection_points)
            ]
        )
        # This the direct distance between the start and end coordinates
        # we don't have to worry about units because we will be dividing by the same unit
        euclidean_distance = np.linalg.norm(
            tortuosity_coords[-1] - tortuosity_coords[0]
        )
        # We shift the cumulative lengths by the length already traveled to the start index
        cumulative_lengths = (
            self.cumulative_lengths[start_idx:end_idx]
            - self.cumulative_lengths[start_idx]
        )[-1]
        # Calculate the two metrics
        tortuosity_index = round(cumulative_lengths / euclidean_distance, 3)
        icm = round((len(inflection_points_in_range) + 1) * tortuosity_index, 3)
        return {
            "tortuosity_index": tortuosity_index,
            "icm": icm,
            "n_inflections": len(inflection_points_in_range),
            # 'inflection_coords': inflection_points_in_range.tolist()
        }

    def calculate_inflection_points(self):
        """
        Internal method to calculate the coordinates of the inflection points along the centerline.

        An inflection point occurs where the curve changes from being concave to convex or vice versa.

        Returns:
            dict: A dictionary containing:
                - 'count': The number of inflection points
                - 'indices': List of indices of the inflection points
                - 'coordinates': List of coordinates of the inflection points
        """
        if self.tck is None:
            raise ValueError(
                "Centerline must be resampled with a spline before calculating inflection points."
            )

        # Calculate first and second derivatives
        first_derivatives = np.array(splev(self.u, self.tck, der=1)).T
        second_derivatives = np.array(splev(self.u, self.tck, der=2)).T

        # Normalize tangents
        tangents = first_derivatives / np.linalg.norm(
            first_derivatives, axis=1, keepdims=True
        )

        # Calculate curvature magnitudes
        curvature = np.zeros(len(self.u))
        for i in range(len(tangents)):
            # Remove tangential component from second derivative
            normal_component = (
                second_derivatives[i]
                - np.dot(second_derivatives[i], tangents[i]) * tangents[i]
            )
            curvature[i] = np.linalg.norm(normal_component)

        # Find local minima in the curvature
        local_min_indices = []
        for i in range(1, len(curvature) - 1):
            if curvature[i] < curvature[i - 1] and curvature[i] < curvature[i + 1]:
                local_min_indices.append(i)

        # Filter out minima that aren't close to zero (true inflection points have near-zero curvature)
        threshold = np.mean(curvature) * 0.3  # 30% of mean curvature as threshold
        inflection_indices = [
            idx for idx in local_min_indices if curvature[idx] < threshold
        ]

        # Get the coordinates of the inflection points
        inflection_points = (
            self.coordinates[inflection_indices] if inflection_indices else np.array([])
        )
        self.inflection_points = inflection_points
