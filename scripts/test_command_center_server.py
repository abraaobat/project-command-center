#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from command_center_server import build_prompt, parse_agent_result


class ActionRunnerTests(unittest.TestCase):
    def test_done_marker(self):
        status, summary, user_action = parse_agent_result(
            "PCC_STATUS: DONE\nPCC_USER_ACTION: NONE\nPCC_SUMMARY: testes verdes\n",
            0,
        )
        self.assertEqual(status, "done")
        self.assertEqual(summary, "testes verdes")
        self.assertEqual(user_action, "")

    def test_needs_user_marker(self):
        status, summary, user_action = parse_agent_result(
            "PCC_STATUS: NEEDS_USER\n"
            "PCC_USER_ACTION: conecte o cabo USB de dados\n"
            "PCC_SUMMARY: preparação concluída\n",
            0,
        )
        self.assertEqual(status, "needs_user")
        self.assertEqual(user_action, "conecte o cabo USB de dados")
        self.assertEqual(summary, "preparação concluída")

    def test_nonzero_without_marker_is_failure(self):
        status, summary, user_action = parse_agent_result("falha de execução", 2)
        self.assertEqual(status, "failed")
        self.assertTrue(summary)
        self.assertTrue(user_action)

    def test_prompt_requires_machine_readable_footer(self):
        prompt = build_prompt(
            {
                "id": "demo",
                "name": "Demo",
                "current": "F1",
                "next": "Executar teste",
                "action": "Rodar a suíte",
            },
            {"path": "project-status.json"},
        )
        self.assertIn("PCC_STATUS: DONE|NEEDS_USER|BLOCKED|FAILED", prompt)
        self.assertIn("Não faça push", prompt)
        self.assertIn("project-status.json", prompt)


if __name__ == "__main__":
    unittest.main()
