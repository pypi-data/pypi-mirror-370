"""LCVQE: Local Constrained Variational Quantum Estimation.

This module implements the LCVQE algorithm, which is a clustering method that
utilizes constraints to guide the clustering process. It is designed to work with
must-link and cannot-link constraints, allowing for a more flexible clustering
approach that respects predefined relationships between data points.

The algorithm iteratively updates cluster centroids while checking and enforcing
constraints, ensuring that the resulting clusters adhere to the specified
relationships.
"""

import logging

import numpy as np

from clustlib.model import BaseEstimator

from ..utils.distance import match_distance

logger = logging.getLogger(__name__)


class LCVQE(BaseEstimator):
    """Local Constrained Variational Quantum Estimation (LCVQE).

    Attributes:
        n_clusters (int, optional): The number of clusters to form as well as the
            number of centroids to generate.
        init (:str, optional): Method for initialization, defaults to 'random' choose
            k observations (rows) at random from data for the initial centroids.
            'custom' use custom_initial_centroids as initial centroids.
        max_iter (int, optional): Maximum number of iterations of the k-means algorithm
            for a single run.
        tol (float, optional): Relative tolerance with regards to Frobenius norm of
            the difference in the cluster centers of two consecutive iterations to
            declare convergence.
        custom_initial_centroids (numpy.ndarray, optional): Custom initial centroids to
            be used in the initialization. Only used if init='custom'.

    """

    def __init__(
        self,
        constraints,
        n_clusters=8,
        init="random",
        distance="euclidean",
        max_iter=300,
        tol=1e-4,
        custom_initial_centroids=None,
    ):
        self.n_clusters = n_clusters
        self.constraints = constraints
        self.distance = match_distance(distance)
        self.init = init

        self._delta_centroid = None
        self._centroids_distance = np.zeros((self.n_clusters, self.n_clusters))
        self.max_iter = max_iter
        self.tol = tol
        self.custom_initial_centroids = custom_initial_centroids
        self.centroids = None

        self._dim = self.constraints.shape[0]

        self.must_link_violations = np.zeros((self.n_clusters, self._dim))
        self.cannot_link_violations = np.zeros((self.n_clusters, self._dim))

    def _get_closest_centroid(self, instance):
        """Get the closest centroid to the instance.

        Args:
            instance (numpy.ndarray): The instance to find the closest centroid.

        Returns:
            Tuple[int, float]: A tuple containing the index of the closest centroid
            and the distance to that centroid.

        """
        distances = np.linalg.norm(self.centroids - instance, axis=1)
        closest_centroid = np.argmin(distances)
        return closest_centroid, distances[closest_centroid]

    def get_ml_constraints(self):
        """Get the must-link cases for the instance.

        Returns:
            ml_cases (List[Tuple[int, int]]): List of tuples where each tuple contains
                the indices of the instances that must be linked.

        """
        ml = np.copy(self.constraints)
        ml = ml - np.diag(np.diag(ml))
        return np.argwhere(ml > 0)

    def get_cl_constraints(self):
        """Get the cannot-link cases for the instance.

        Returns:
        ml_cases (List[Tuple[int, int]]): List of tuples where each tuple contains
            the indices of instances that must be linked.

        """
        cl = np.copy(self.constraints)
        cl = cl - np.diag(np.diag(cl))
        return np.argwhere(cl < 0)

    def _check_ml_cases(self):
        """Check must-link cases.

        This method iterates through the must-link constraints and checks if the
        instances that must be linked are assigned to the same cluster. If they are
        not, it will reassign them to the closest centroid based on the distance
        between the instance and the centroids.

        It updates the `must_link_violations` matrix to indicate which instances
        violate the must-link constraints.

        This method ensures that the must-link constraints are respected by adjusting
        the labels of instances as necessary.
        """
        for i, j in self.get_ml_constraints():
            c_i, distance_c_i = self._get_closest_centroid(self.X[i])
            c_j, distance_c_j = self._get_closest_centroid(self.X[j])

            if c_i == c_j:
                continue

            distance_i_cj = self.distance(self.X[i] - self.centroids[c_j])
            distance_j_ci = self.distance(self.X[j] - self.centroids[c_i])

            case_a = 0.5 * (distance_c_i + distance_c_j) + 0.25 * (
                distance_i_cj + distance_j_ci
            )
            case_b = 0.5 * distance_c_i + 0.5 * distance_j_ci
            case_c = 0.5 * distance_i_cj + 0.5 * distance_c_j

            min_case = np.argmin([case_a, case_b, case_c])

            if min_case == 0:
                self.must_link_violations[c_i, j] = 1
                self.must_link_violations[c_j, i] = 1
            elif min_case == 1:
                self._labels[j] = c_i
            else:
                self._labels[i] = c_j

    def _check_cl_cases(self):
        """Check cannot-link cases.

        This method iterates through the cannot-link constraints and checks if the
        instances that cannot be linked are assigned to the same cluster. If they are
        not, it will reassign them to the closest centroid based on the distance
        between the instance and the centroids.

        It updates the `cannot_link_violations` matrix to indicate which instances
        violate the cannot-link constraints.
        """
        for i, j in self.get_cl_constraints():
            cluster_i = self._labels[i]
            cluster_j = self._labels[j]

            if cluster_i != cluster_j:
                continue

            cluster = cluster_i

            distances_i = self.distance(self.centroids - self.X[i], axis=1)
            distances_j = self.distance(self.centroids - self.X[j], axis=1)

            idx_sorted_i = np.argsort(distances_i)
            idx_sorted_j = np.argsort(distances_j)

            distance_to_cluster = np.array(
                [
                    self.distance(self.centroids[cluster] - self.X[i]),
                    self.distance(self.centroids[cluster] - self.X[j]),
                ]
            )

            if distance_to_cluster[0] <= distance_to_cluster[1]:
                alternative_cluster = np.setdiff1d(idx_sorted_j, np.array([cluster]))[0]
                distance_to_alternative = distances_j[alternative_cluster]
                closest_distance = distances_i[cluster]
                r_i = i
                r_j = j
            else:
                alternative_cluster = np.setdiff1d(idx_sorted_i, np.array([cluster]))[0]
                distance_to_alternative = distances_i[alternative_cluster]
                closest_distance = distances_j[cluster]
                r_i = j
                r_j = i

            A = (
                0.5 * distances_i[cluster]
                + 0.5 * distances_j[cluster]
                + 0.5 * distance_to_alternative
            )
            B = 0.5 * closest_distance + 0.5 * distance_to_alternative

            if A < B:
                self.cannot_link_violations[alternative_cluster, r_j] = 1
            else:
                self._labels[r_i] = cluster
                self._labels[r_j] = alternative_cluster

    def _update(self):
        for c in range(self.n_clusters):
            members = np.argwhere(self._labels == c)
            if len(members) == 0:
                continue

            coords_members = np.sum(self.X[members, :], 0)

            ml_instances = np.where(self.must_link_violations[c] == 1)
            cl_instances = np.where(self.cannot_link_violations[c] == 1)

            coords_GMLV = np.sum(self.X[ml_instances], 0)
            coords_GCLV = np.sum(self.X[cl_instances], 0)
            n_j = len(members) + 0.5 * np.sum(cl_instances) + np.sum(ml_instances)

            self.centroids[c, :] = coords_members + 0.5 * coords_GMLV + coords_GCLV
            self.centroids[c, :] = (
                self.centroids[c, :] / n_j if n_j > 0 else self.centroids[c, :]
            )

    def _convergence(self):
        if self._delta is None:
            logger.debug("Delta is None, convergence cannot be checked.")
            return False

        return np.abs(np.linalg.norm(self._delta)) < self.tol

    def _fit(self):
        """Fit the model to the data."""
        iteration = 0

        logging.debug("Fitting LCVQE model")
        while not self.stop_criteria(iteration):
            logging.debug(f"Iteration {iteration}: Checking constraints")
            self._check_ml_cases()
            self._check_cl_cases()

            logging.debug(f"Iteration {iteration}: Updating centroids")
            self._update()

            logging.debug(f"Iteration {iteration}: Updating labels")
            iteration += 1

        return self.centroids
