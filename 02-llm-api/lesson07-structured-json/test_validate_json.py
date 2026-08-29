import unittest

from validate_json import validate_learning_result
from json_api_basic import parse_learning_result

class TestValidateLearningResult(unittest.TestCase):

    def test_valid_data(self):
        data = {
            "topic": "LLM API",
            "level": "beginner",
            "next_step": "学习 API",
        }

        result = validate_learning_result(data)

        self.assertEqual(result, data)

    def test_missing_field(self):
        data = {
            "topic": "LLM API",
            "level": "beginner",
        }

        with self.assertRaises(ValueError):
            validate_learning_result(data)

    def test_wrong_type(self):
        data = {
            "topic": "LLM API",
            "level": 1,
            "next_step": "学习 API",
        }

        with self.assertRaises(TypeError):
            validate_learning_result(data)

    def test_invalid_json(self):
        answer_text = """
            {
            "topic": "LLM API",
            "level": "beginner",
            }
            """

        with self.assertRaises(ValueError) as context:
            parse_learning_result(answer_text)

        self.assertIn(
            "不是合法 JSON",
            str(context.exception),
        )

if __name__ == "__main__":
    unittest.main()