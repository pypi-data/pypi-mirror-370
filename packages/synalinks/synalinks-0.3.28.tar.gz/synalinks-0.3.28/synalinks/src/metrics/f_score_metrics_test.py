# License Apache 2.0: (c) 2025 Yoan Sallami (Synalinks Team)

import json

from synalinks.src import backend
from synalinks.src import testing
from synalinks.src.backend import DataModel
from synalinks.src.metrics.f_score_metrics import BinaryF1Score
from synalinks.src.metrics.f_score_metrics import BinaryFBetaScore
from synalinks.src.metrics.f_score_metrics import F1Score
from synalinks.src.metrics.f_score_metrics import FBetaScore


class FBetaScoreTest(testing.TestCase):
    async def test_same_field(self):
        class Answer(DataModel):
            answer: str

        y_pred = Answer(answer="Toulouse is the French city of aeronautics and space.")
        y_true = Answer(answer="Toulouse is the French city of aeronautics and space.")

        metric = FBetaScore()
        score = await metric(y_true, y_pred)
        self.assertAlmostEqual(score, 1.0, delta=3 * backend.epsilon())

    async def test_different_field(self):
        class Answer(DataModel):
            answer: str

        y_pred = Answer(answer="Toulouse is the French city of aeronautics and space.")
        y_true = Answer(answer="Paris is the capital of France.")

        metric = FBetaScore()
        score = await metric(y_true, y_pred)
        self.assertAlmostEqual(score, 0.0, delta=3 * backend.epsilon())


class F1ScoreTest(testing.TestCase):
    async def test_same_field(self):
        class Answer(DataModel):
            answer: str

        y_pred = Answer(answer="Toulouse is the French city of aeronautics and space.")
        y_true = Answer(answer="Toulouse is the French city of aeronautics and space.")

        metric = F1Score(average="weighted")
        score = await metric(y_true, y_pred)
        self.assertAlmostEqual(score, 1.0, delta=3 * backend.epsilon())

    async def test_different_field(self):
        class Answer(DataModel):
            answer: str

        y_pred = Answer(answer="Toulouse is the French city of aeronautics and space.")
        y_true = Answer(answer="Paris is the capital of France.")

        metric = F1Score(average="weighted")
        score = await metric(y_true, y_pred)
        self.assertAlmostEqual(score, 0.0, delta=3 * backend.epsilon())


class BinaryFBetaScoreTest(testing.TestCase):
    async def test_same_boolean_fields(self):
        class MultiLabels(DataModel):
            label: bool
            label_1: bool
            label_2: bool

        y_pred = MultiLabels(label=False, label_1=True, label_2=True)
        y_true = MultiLabels(label=False, label_1=True, label_2=True)

        metric = BinaryFBetaScore(average="weighted")
        score = await metric(y_true, y_pred)
        self.assertAlmostEqual(score, 1.0, delta=3 * backend.epsilon())

    async def test_different_boolean_fields(self):
        class MultiLabels(DataModel):
            label: bool
            label_1: bool
            label_2: bool

        y_pred = MultiLabels(label=True, label_1=True, label_2=False)
        y_true = MultiLabels(label=False, label_1=False, label_2=True)

        metric = BinaryFBetaScore(average="weighted")
        score = await metric(y_true, y_pred)
        self.assertAlmostEqual(score, 0.0, delta=3 * backend.epsilon())


class BinaryF1ScoreTest(testing.TestCase):
    async def test_same_boolean_fields(self):
        class MultiLabels(DataModel):
            label: bool
            label_1: bool
            label_2: bool

        y_pred = MultiLabels(label=False, label_1=True, label_2=True)
        y_true = MultiLabels(label=False, label_1=True, label_2=True)

        metric = BinaryF1Score(average="weighted")
        score = await metric(y_true, y_pred)
        self.assertAlmostEqual(score, 1.0, delta=3 * backend.epsilon())

    async def test_different_boolean_fields(self):
        class MultiLabels(DataModel):
            label: bool
            label_1: bool
            label_2: bool

        y_pred = MultiLabels(label=True, label_1=True, label_2=False)
        y_true = MultiLabels(label=False, label_1=False, label_2=True)

        metric = BinaryF1Score(average="weighted")
        score = await metric(y_true, y_pred)
        self.assertAlmostEqual(score, 0.0, delta=3 * backend.epsilon())

    async def test_reset_state(self):
        class MultiLabels(DataModel):
            label: bool
            label_1: bool
            label_2: bool

        y_pred = MultiLabels(label=False, label_1=True, label_2=True)
        y_true = MultiLabels(label=False, label_1=True, label_2=True)

        metric = BinaryF1Score(average="weighted")
        score = await metric(y_true, y_pred)
        self.assertAlmostEqual(score, 1.0, delta=3 * backend.epsilon())
        metric.reset_state()
        score = metric.result()
        self.assertEqual(score, 0.0)

    async def test_variable_serialization(self):
        class MultiLabels(DataModel):
            label: bool
            label_1: bool
            label_2: bool

        y_pred = MultiLabels(label=False, label_1=True, label_2=True)
        y_true = MultiLabels(label=False, label_1=True, label_2=True)
        metric = BinaryF1Score(average="weighted")
        score = await metric(y_true, y_pred)
        self.assertAlmostEqual(score, 1.0, delta=3 * backend.epsilon())
        state = metric.variables[0]
        # Try to dump it so we can test if the state is serializable
        _ = json.dumps(state.get_json())
