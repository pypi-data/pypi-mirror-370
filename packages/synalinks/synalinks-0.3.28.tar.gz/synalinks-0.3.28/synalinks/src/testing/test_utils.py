# License Apache 2.0: (c) 2025 Yoan Sallami (Synalinks Team)

import numpy as np

from synalinks.src.backend import DataModel


class Query(DataModel):
    query: str


class AnswerWithRationale(DataModel):
    rationale: str
    answer: str


def load_test_data():
    x_train = np.array(
        [
            Query(query="What is the capital of France?"),
            Query(query="What is the French city of aeronautics?"),
        ],
        dtype="object",
    )
    y_train = np.array(
        [
            AnswerWithRationale(
                rationale="""The capital of France is well-known and is the seat of """
                """the French government.""",
                answer="Paris",
            ),
            AnswerWithRationale(
                rationale="""Toulouse is known as the French city of aeronautics due"""
                """ to its significant contributions to the aerospace industry.""",
                answer="Toulouse",
            ),
        ],
        dtype="object",
    )

    x_test = np.array(
        [
            Query(query="What is the largest city in France?"),
            Query(query="What is the capital of Germany?"),
        ],
        dtype="object",
    )
    y_test = np.array(
        [
            AnswerWithRationale(
                rationale="Paris is the largest city in France by population and area.",
                answer="Paris",
            ),
            AnswerWithRationale(
                rationale="The capital of Germany is well-known and is the seat "
                "of the German government.",
                answer="Berlin",
            ),
        ],
        dtype="object",
    )
    return (x_train, y_train), (x_test, y_test)


def mock_completion_data():
    response = (
        """{"rationale":"The capital of France is well-known and is the seat of """
        """the French government.", "answer": "Paris"}"""
    )
    response_1 = (
        """{"rationale":"Toulouse is known as the French city of aeronautics due"""
        """ to its significant contributions to the aerospace industry.", """
        """"answer": "Toulouse"}"""
    )
    return [
        {"choices": [{"message": {"content": response}}]},
        {"choices": [{"message": {"content": response_1}}]},
    ]


def named_product(*args, **kwargs):
    """Utility to generate the cartesian product of parameters values and
    generate a test case names for each combination.

    The result of this function is to be used with the
    `@parameterized.named_parameters` decorator. It is a replacement for
    `@parameterized.product` which adds explicit test case names.

    For example, this code:
    ```
    class NamedExample(parameterized.TestCase):
        @parameterized.named_parameters(
            named_product(
                [
                    {'testcase_name': 'negative', 'x': -1},
                    {'testcase_name': 'positive', 'x': 1},
                    {'testcase_name': 'zero', 'x': 0},
                ],
                numeral_type=[float, int],
            )
        )
        def test_conversion(self, x, numeral_type):
            self.assertEqual(numeral_type(x), x)
    ```
    produces six tests (note that absl will reorder them by name):
    - `NamedExample::test_conversion_negative_float`
    - `NamedExample::test_conversion_positive_float`
    - `NamedExample::test_conversion_zero_float`
    - `NamedExample::test_conversion_negative_int`
    - `NamedExample::test_conversion_positive_int`
    - `NamedExample::test_conversion_zero_int`

    This function is also useful in the case where there is no product to
    generate test case names for one argument:
    ```
    @parameterized.named_parameters(named_product(numeral_type=[float, int]))
    ```

    Args:
        *args: Each positional parameter is a sequence of keyword arg dicts.
            Every test case generated will include exactly one dict from each
            positional parameter. These will then be merged to form an overall
            list of arguments for the test case. Each dict must contain a
            `"testcase_name"` key whose value is combined with others to
            generate the test case name.
        **kwargs: A mapping of parameter names and their possible values.
            Possible values should given as either a list or a tuple. A string
            representation of each value is used to generate the test case name.

    Returns:
        A list of maps for the test parameters combinations to pass to
        `@parameterized.named_parameters`.
    """

    def value_to_str(value):
        if hasattr(value, "__name__"):
            return value.__name__.lower()
        return str(value).lower()

    # Convert the keyword arguments in the same dict format as the args
    all_test_dicts = args + tuple(
        tuple({"testcase_name": value_to_str(v), key: v} for v in values)
        for key, values in kwargs.items()
    )

    # The current list of tests, start with one empty test
    tests = [{}]
    for test_dicts in all_test_dicts:
        new_tests = []
        for test_dict in test_dicts:
            for test in tests:
                # Augment the testcase name by appending
                testcase_name = test.get("testcase_name", "")
                testcase_name += "_" if testcase_name else ""
                testcase_name += test_dict["testcase_name"]
                new_test = test.copy()
                # Augment the test by adding all the parameters
                new_test.update(test_dict)
                new_test["testcase_name"] = testcase_name
                new_tests.append(new_test)
        # Overwrite the list of tests with the product obtained so far
        tests = new_tests

    return tests
