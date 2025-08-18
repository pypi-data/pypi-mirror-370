import unittest
import numpy as np

from small_text.classifiers import ConfidenceEnhancedLinearSVC
from small_text.data.datasets import SklearnDataset
from small_text.query_strategies import (
    EmptyPoolException,
    greedy_coreset,
    GreedyCoreset,
    lightweight_coreset,
    LightweightCoreset
)

from tests.unit.small_text.query_strategies.test_strategies import (
    DEFAULT_QUERY_SIZE,
    SamplingStrategiesTests,
    query_random_data
)


class _GreedyCoresetFunctionTest(object):

    def test_query(self, num_samples=20, num_features=100):
        x = np.random.rand(num_samples, num_features)
        indices = np.arange(num_samples)
        indices_mid = int(num_samples / 2)

        coreset = greedy_coreset(x, indices[:indices_mid], indices[indices_mid:], num_samples,
                                 distance_metric=self.distance_metric)

        self.assertEqual(coreset.shape, (num_samples,))

    def test_query_with_invalid_distance_metric(self, num_samples=20, num_features=100):
        x = np.random.rand(num_samples, num_features)
        indices = np.arange(num_samples)
        indices_mid = int(num_samples / 2)
        with self.assertRaisesRegex(ValueError, 'Invalid distance metric:'):
            greedy_coreset(x, indices[:indices_mid], indices[indices_mid:], num_samples,
                           distance_metric='non-existent-metric')

    # see https://github.com/webis-de/small-text/issues/50
    def test_query_with_num_unlabeled_smaller_than_num_batches(self, num_samples=200, num_features=100):
        x = np.random.rand(num_samples, num_features)

        indices = np.arange(num_samples)
        indices_mid = num_samples - 180

        coreset = greedy_coreset(x, indices[:indices_mid], indices[indices_mid:], num_samples,
                                 distance_metric=self.distance_metric, batch_size=5)

        self.assertEqual(coreset.shape, (num_samples,))

    def test_query_with_overlarge_n(self, num_samples=20, num_features=100):
        x = np.random.rand(num_samples, num_features)
        indices = np.arange(num_samples)
        indices_mid = int(num_samples / 2)
        with self.assertRaises(ValueError):
            greedy_coreset(x, indices[:indices_mid], indices[indices_mid:], num_samples+1,
                           distance_metric=self.distance_metric)


class GreedyCoresetWithCosineDistanceMetricFunctionTest(_GreedyCoresetFunctionTest, unittest.TestCase):

    def setUp(self):
        self.distance_metric = 'cosine'


class GreedyCoresetWithEuclideanDistanceMetricFunctionTest(_GreedyCoresetFunctionTest, unittest.TestCase):

    def setUp(self):
        self.distance_metric = 'euclidean'


class _CoresetSamplingStrategyTest(SamplingStrategiesTests):

    def setUp(self):
        # must set self.normalize (bool)
        raise NotImplementedError

    def _get_clf(self):
        raise NotImplementedError

    def _get_query_strategy(self):
        raise NotImplementedError

    def test_init_with_invalid_distance_metric(self):
        with self.assertRaisesRegex(ValueError, 'Invalid distance metric:'):
            GreedyCoreset(distance_metric='non-existent-metric')

    # overrides test from SamplingStrategiesTests (to use embeddings)
    def test_simple_query(self, embedding_dim=100):
        embeddings = np.random.rand(SamplingStrategiesTests.DEFAULT_NUM_SAMPLES, embedding_dim)
        indices = self._query(self._get_query_strategy(),
                              num_samples=self.DEFAULT_NUM_SAMPLES,
                              n=5,
                              embeddings=embeddings)
        self.assertEqual(5, len(indices))

    # overrides test from SamplingStrategiesTests (to use embeddings)
    def test_default_query(self, embedding_dim=100):
        embeddings = np.random.rand(SamplingStrategiesTests.DEFAULT_NUM_SAMPLES, embedding_dim)
        indices = self._query(self._get_query_strategy(), num_samples=100, embeddings=embeddings)
        self.assertEqual(DEFAULT_QUERY_SIZE, len(indices))

    # overrides test from SamplingStrategiesTests (to use embeddings)
    def test_query_takes_remaining_pool(self, embedding_dim=100):
        embeddings = np.random.rand(SamplingStrategiesTests.DEFAULT_NUM_SAMPLES, embedding_dim)
        indices = self._query(self._get_query_strategy(),
                              num_samples=self.DEFAULT_NUM_SAMPLES,
                              n=10,
                              embeddings=embeddings)
        self.assertEqual(DEFAULT_QUERY_SIZE, len(indices))

    def test_str(self):
        strategy = self._get_query_strategy()
        expected_str = f'GreedyCoreset(distance_metric=euclidean, normalize={str(self.normalize)}, ' \
                       f'batch_size=100)'
        self.assertEqual(expected_str, str(strategy))

    def test_query_default(self):
        indices = query_random_data(self._get_query_strategy(), use_embeddings=True)
        self.assertEqual(10, len(indices))

    def test_query_empty_pool(self, num_samples=20, n=10):
        strategy = self._get_query_strategy()

        dataset = SklearnDataset(np.random.rand(num_samples, 10),
                                 np.random.randint(0, high=2, size=num_samples))

        indices_labeled = np.random.choice(np.arange(100), size=10, replace=False)
        indices_unlabeled = []
        y = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])

        with self.assertRaises(EmptyPoolException):
            strategy.query(None, dataset, indices_unlabeled, indices_labeled, y, n=n)


class GreedyCoresetSamplingStrategyNormalizedTest(unittest.TestCase,
                                                  _CoresetSamplingStrategyTest):

    def setUp(self):
        self.normalize = True

    def _get_clf(self):
        return ConfidenceEnhancedLinearSVC()

    def _get_query_strategy(self):
        return GreedyCoreset(normalize=self.normalize)


class GreedyCoresetSamplingStrategyUnnormalizedTest(unittest.TestCase,
                                                    _CoresetSamplingStrategyTest):

    def setUp(self):
        self.normalize = False

    def _get_clf(self):
        return ConfidenceEnhancedLinearSVC()

    def _get_query_strategy(self):
        return GreedyCoreset(normalize=self.normalize)


class _LightweightCoresetFunctionTest(object):

    def test_query(self, num_samples=20, num_features=100):
        x = np.random.rand(num_samples, num_features)
        coreset = lightweight_coreset(x, np.mean(x, axis=0), num_samples, distance_metric=self.distance_metric)
        self.assertEqual(coreset.shape, (num_samples,))

    def test_query_with_invalid_distance_metric(self, num_samples=20, num_features=100):
        x = np.random.rand(num_samples, num_features)
        with self.assertRaisesRegex(ValueError, 'Invalid distance metric:'):
            lightweight_coreset(x, np.mean(x, axis=0), 10, distance_metric='non-existent-metric')

    def test_query_with_overlarge_n(self, num_samples=20, num_features=100):
        x = np.random.rand(num_samples, num_features)
        with self.assertRaises(ValueError):
            lightweight_coreset(x, np.mean(x, axis=0), num_samples+1)


class LightweightCoresetWitdhCodineDistanceMetricFunctionTest(_LightweightCoresetFunctionTest, unittest.TestCase):

    def setUp(self):
        self.distance_metric = 'cosine'


class LightweightCoresetWithEuclideanDistanceMetricFunctionTest(_LightweightCoresetFunctionTest, unittest.TestCase):

    def setUp(self):
        self.distance_metric = 'euclidean'


class _LightweightCoresetSamplingStrategyTest(SamplingStrategiesTests):

    def setUp(self):
        # must set self.normalize (bool)
        raise NotImplementedError

    def _get_clf(self):
        raise NotImplementedError

    def _get_query_strategy(self):
        raise NotImplementedError

    # overrides test from SamplingStrategiesTests (to use embeddings)
    def test_simple_query(self, embedding_dim=100):
        embeddings = np.random.rand(SamplingStrategiesTests.DEFAULT_NUM_SAMPLES, embedding_dim)
        indices = self._query(self._get_query_strategy(),
                              num_samples=self.DEFAULT_NUM_SAMPLES,
                              n=5,
                              embeddings=embeddings)
        self.assertEqual(5, len(indices))

    # overrides test from SamplingStrategiesTests (to use embeddings)
    def test_default_query(self, embedding_dim=100):
        embeddings = np.random.rand(SamplingStrategiesTests.DEFAULT_NUM_SAMPLES, embedding_dim)
        indices = self._query(self._get_query_strategy(), num_samples=100, embeddings=embeddings)
        self.assertEqual(DEFAULT_QUERY_SIZE, len(indices))

    # overrides test from SamplingStrategiesTests (to use embeddings)
    def test_query_takes_remaining_pool(self, embedding_dim=100):
        embeddings = np.random.rand(SamplingStrategiesTests.DEFAULT_NUM_SAMPLES, embedding_dim)
        indices = self._query(self._get_query_strategy(),
                              num_samples=self.DEFAULT_NUM_SAMPLES,
                              n=10,
                              embeddings=embeddings)
        self.assertEqual(DEFAULT_QUERY_SIZE, len(indices))

    def test_lightweight_coreset_str(self):
        strategy = self._get_query_strategy()
        expected_str = f'LightweightCoreset(distance_metric={str(self.distance_metric)}, normalize={str(self.normalize)})'
        self.assertEqual(expected_str, str(strategy))

    def test_lightweight_coreset_query_default(self):
        indices = query_random_data(self._get_query_strategy(), use_embeddings=True)
        self.assertEqual(10, len(indices))

    def test_lightweight_coreset_empty_pool(self, num_samples=20, n=10):
        strategy = self._get_query_strategy()

        dataset = SklearnDataset(np.random.rand(num_samples, 10),
                                 np.random.randint(0, high=2, size=num_samples))

        indices_labeled = np.random.choice(np.arange(100), size=10, replace=False)
        indices_unlabeled = []
        y = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])

        with self.assertRaises(EmptyPoolException):
            strategy.query(None, dataset, indices_unlabeled, indices_labeled, y, n=n)


class LightweightCoresetSamplingStrategyNormalizedTest(_LightweightCoresetSamplingStrategyTest,
                                                       unittest.TestCase):

    def setUp(self):
        self.distance_metric = 'cosine'
        self.normalize = True

    def _get_clf(self):
        return ConfidenceEnhancedLinearSVC()

    def _get_query_strategy(self):
        return LightweightCoreset(distance_metric=self.distance_metric,
                                  normalize=self.normalize)


class LightweightCoresetSamplingStrategyUnnormalizedTest(_LightweightCoresetSamplingStrategyTest,
                                                         unittest.TestCase):

    def setUp(self):
        self.distance_metric = 'cosine'
        self.normalize = True

    def _get_clf(self):
        return ConfidenceEnhancedLinearSVC()

    def _get_query_strategy(self):
        return LightweightCoreset(distance_metric=self.distance_metric, 
                                  normalize=self.normalize)
