import unittest

import pytest
import numpy as np

from small_text.integrations.pytorch.exceptions import PytorchNotFoundError

try:
    from small_text.integrations.pytorch.query_strategies import (
        BADGE,
        DiscriminativeRepresentationLearning,
        ExpectedGradientLength,
        ExpectedGradientLengthMaxWord
    )
    from small_text.integrations.pytorch.classifiers.kimcnn import KimCNNClassifier

    from tests.utils.datasets import random_text_classification_dataset
except PytorchNotFoundError:
    pass


@pytest.mark.pytorch
class BADGETest(unittest.TestCase):

    def test_init_default(self):
        strategy = BADGE(2)
        self.assertEqual(2, strategy.num_classes)

    def test_init(self):
        strategy = BADGE(4)
        self.assertEqual(4, strategy.num_classes)

    def test_badge_str(self):
        strategy = BADGE(2)
        expected_str = 'BADGE(num_classes=2)'
        self.assertEqual(expected_str, str(strategy))


@pytest.mark.pytorch
class ExpectedGradientLengthTest(unittest.TestCase):

    def test_init_default(self):
        strategy = ExpectedGradientLength(2)

        self.assertEqual(2, strategy.num_classes)
        self.assertEqual(50, strategy.batch_size)
        self.assertEqual('cuda', strategy.device)

    def test_init(self):
        strategy = ExpectedGradientLength(4, batch_size=100, device='cpu')

        self.assertEqual(4, strategy.num_classes)
        self.assertEqual(100, strategy.batch_size)
        self.assertEqual('cpu', strategy.device)

    def test_expected_gradient_length_str(self):
        strategy = ExpectedGradientLength(2)
        expected_str = 'ExpectedGradientLength()'
        self.assertEqual(expected_str, str(strategy))


@pytest.mark.pytorch
class ExpectedGradientLengthMaxWordTest(unittest.TestCase):

    def test_init_default(self):
        strategy = ExpectedGradientLengthMaxWord(2, 'embedding')

        self.assertEqual(2, strategy.num_classes)
        self.assertEqual(50, strategy.batch_size)
        self.assertEqual('cuda', strategy.device)
        self.assertEqual('embedding', strategy.layer_name)

    def test_init(self):
        strategy = ExpectedGradientLengthMaxWord(4, 'embedding', batch_size=100, device='cpu')

        self.assertEqual(4, strategy.num_classes)
        self.assertEqual(100, strategy.batch_size)
        self.assertEqual('cpu', strategy.device)
        self.assertEqual('embedding', strategy.layer_name)

    def test_query_with_initial_model_untrained(self, num_samples=100):
        strategy = ExpectedGradientLengthMaxWord(4, 'fc', batch_size=100, device='cpu')

        clf = KimCNNClassifier(2, embedding_matrix=np.random.rand(num_samples, 5))
        dataset = random_text_classification_dataset(num_samples=num_samples)

        indices_labeled = np.random.choice(np.arange(num_samples), size=10, replace=False)
        indices_unlabeled = np.array([i for i in range(len(dataset))
                                      if i not in set(indices_labeled)])
        y = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])

        with self.assertRaisesRegex(ValueError, 'Initial model must be trained'):
            strategy.query(clf, dataset, indices_labeled, indices_unlabeled, y)


@pytest.mark.pytorch
class DiscriminativeRepresentationLearningTest(unittest.TestCase):

    def test_init_default(self):
        strategy = DiscriminativeRepresentationLearning()

        self.assertEqual(10, strategy.num_iterations)
        self.assertEqual(10, strategy.unlabeled_factor)
        self.assertEqual(32, strategy.mini_batch_size)
        self.assertIsNone(strategy._amp_args)
        self.assertIsNotNone(strategy.embed_kwargs)
        self.assertEqual(0, len(strategy.embed_kwargs))
        self.assertEqual('tqdm', strategy.pbar)

    def test_init_with_invalid_selection_strategy(self):
        with self.assertRaisesRegex(ValueError, 'Invalid selection strategy: does-not-exist'):
            DiscriminativeRepresentationLearning(selection='does-not-exist')

    def test_init_with_invalid_temperature(self):
        with self.assertRaisesRegex(ValueError, 'Invalid temperature: temperature must be greater zero'):
            DiscriminativeRepresentationLearning(temperature=0)
        with self.assertRaisesRegex(ValueError, 'Invalid temperature: temperature must be greater zero'):
            DiscriminativeRepresentationLearning(temperature=-1)

    def test_discriminative_active_learning_str(self):
        strategy = DiscriminativeRepresentationLearning()
        expected_str = ('DiscriminativeRepresentationLearning(num_iterations=10, '
                        'selection=stochastic, temperature=0.01, unlabeled_factor=10, '
                        'mini_batch_size=32, device=cuda)')
        self.assertEqual(expected_str, str(strategy))
