import contextlib
import copy
import io
import unittest
from unittest.mock import Mock, patch

import lesson05_agent_state

from requests.exceptions import Timeout

class TestAgentToolRoundtrip(unittest.TestCase):
    def test_tool_result_is_returned_to_model(self):
        tool_call_id = "call_search_001"

        assistant_tool_message = {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": tool_call_id,
                    "type": "function",
                    "function": {
                        "name": "search_knowledge_base",
                        "arguments": (
                            '{"query": "Stage 4 学什么？"}'
                        ),
                    },
                }
            ],
        }

        final_message = {
            "role": "assistant",
            "content": "Stage 4 学习 Agent。[chunk-001]",
        }

        replies = iter([
            assistant_tool_message,
            final_message,
        ])
        model_requests = []

        def fake_call_chat_model(messages, api_key, tool_choice, api_tools=None):
            model_requests.append({
                "messages": copy.deepcopy(messages),
                "tool_choice": tool_choice,
                "api_tools": api_tools,
            })
            return next(replies)

        tool_result = {
            "query": "Stage 4 学什么？",
            "matches": [
                {
                    "id": "chunk-001",
                    "text": "Stage 4 学习 Agent。",
                    "source": "learning_path.md",
                    "chunk_index": 0,
                    "score": 0.8,
                }
            ],
        }
        search_tool = Mock(return_value=tool_result)

        api_tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                },
            }
        ]

        with patch.object(
            lesson05_agent_state,
            "call_chat_model",
            side_effect=fake_call_chat_model,
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                result = lesson05_agent_state.run_agent(
                    user_prompt="Stage 4 学什么？",
                    api_key="mock-key",
                    api_tools=api_tools,
                    tools={
                        "search_knowledge_base": search_tool,
                    },
                )

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["answer"], final_message["content"])
        search_tool.assert_called_once_with(
            query="Stage 4 学什么？"
        )

        self.assertEqual(len(model_requests), 2)
        self.assertEqual(
            model_requests[0]["api_tools"],
            api_tools,
        )

        second_request_messages = model_requests[1]["messages"]

        self.assertEqual(
            [message["role"] for message in second_request_messages],
            ["system", "user", "assistant", "tool"],
        )
        self.assertEqual(
            second_request_messages[-1]["tool_call_id"],
            tool_call_id,
        )
        self.assertEqual(
            second_request_messages[-1]["content"],
            '{"query": "Stage 4 学什么？", "matches": '
            '[{"id": "chunk-001", "text": "Stage 4 学习 Agent。", '
            '"source": "learning_path.md", "chunk_index": 0, '
            '"score": 0.8}]}',
        )

    def test_stops_at_step_limit(self):
        model_replies = [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": call_id,
                        "type": "function",
                        "function": {
                            "name": "search_knowledge_base",
                            "arguments": '{"query": "Stage 4"}',
                        },
                    }
                ],
            }
            for call_id in ("call_001", "call_002")
        ]

        mock_model = Mock(side_effect=model_replies)
        search_tool = Mock(return_value={
            "query": "Stage 4",
            "matches": [],
        })

        with patch.object(
            lesson05_agent_state,
            "call_chat_model",
            mock_model,
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                result = lesson05_agent_state.run_agent(
                    user_prompt="查询 Stage 4",
                    api_key="mock-key",
                    max_steps=2,
                    tools={
                        "search_knowledge_base": search_tool,
                    },
                )

        self.assertEqual(result["status"], "step_limit")
        self.assertEqual(result["steps"], 2)
        self.assertIsNone(result["answer"])
        self.assertEqual(mock_model.call_count, 2)
        self.assertEqual(search_tool.call_count, 2)

        events = [
            record["event"]
            for record in result["trace"]
        ]
        self.assertNotIn("final_answer", events)

    def test_model_timeout_stops_agent(self):
        mock_model = Mock(
            side_effect=Timeout("mock model timeout")
        )
        search_tool = Mock()

        with patch.object(
            lesson05_agent_state,
            "call_chat_model",
            mock_model,
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                result = lesson05_agent_state.run_agent(
                    user_prompt="Stage 4 学什么？",
                    api_key="mock-key",
                    tools={
                        "search_knowledge_base": search_tool,
                    },
                )

        self.assertEqual(result["status"], "api_error")
        self.assertEqual(result["steps"], 1)
        self.assertIsNone(result["answer"])
        self.assertIn("mock model timeout", result["reason"])

        mock_model.assert_called_once()
        search_tool.assert_not_called()

        self.assertEqual(
            [record["event"] for record in result["trace"]],
            ["model_request", "api_error"],
        )
        self.assertEqual(
            result["trace"][-1]["error"],
            "mock model timeout",
        )

    def test_tool_timeout_stops_agent(self):
        assistant_tool_message = {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_search_001",
                    "type": "function",
                    "function": {
                        "name": "search_knowledge_base",
                        "arguments": '{"query": "Stage 4"}',
                    },
                }
            ],
        }

        mock_model = Mock(
            return_value=assistant_tool_message
        )
        search_tool = Mock(
            side_effect=Timeout("mock embedding timeout")
        )

        with patch.object(
            lesson05_agent_state,
            "call_chat_model",
            mock_model,
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                result = lesson05_agent_state.run_agent(
                    user_prompt="查询 Stage 4",
                    api_key="mock-key",
                    tools={
                        "search_knowledge_base": search_tool,
                    },
                )

        self.assertEqual(result["status"], "tool_error")
        self.assertEqual(result["steps"], 1)
        self.assertIsNone(result["answer"])
        self.assertIn(
            "mock embedding timeout",
            result["reason"],
        )

        mock_model.assert_called_once()
        search_tool.assert_called_once_with(
            query="Stage 4"
        )

        self.assertEqual(
            [record["event"] for record in result["trace"]],
            ["model_request", "tool_error"],
        )
        self.assertEqual(
            result["trace"][-1]["tool"],
            "search_knowledge_base",
        )
        self.assertEqual(
            result["trace"][-1]["error"],
            "mock embedding timeout",
        ) 
if __name__ == "__main__":
    unittest.main()