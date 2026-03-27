from __future__ import annotations

import unittest

from backend.core.decision_engine import HiringDecisionEngine
from backend.core.interview_engine import InterviewEngine


RESUME_TEXT = (
    "Backend engineer with 5 years of experience building Python and FastAPI "
    "microservices on AWS with Docker and CI/CD. Led API design, testing, "
    "monitoring, and stakeholder delivery across multiple releases."
)

JD_TEXT = (
    "Required: 3+ years of experience in Python, FastAPI, AWS, Docker, and "
    "microservices. Preferred: CI/CD and strong API testing practices."
)


class HiringPipelineTests(unittest.TestCase):
    def test_decision_engine_evaluate_shape(self) -> None:
        engine = HiringDecisionEngine()
        output = engine.evaluate(RESUME_TEXT, JD_TEXT)

        self.assertIn("pipeline", output)
        self.assertIn("agent_reviews", output)
        self.assertIn("debate", output)
        self.assertIn("supervisor_review", output)
        self.assertIn("final_decision", output)
        self.assertIn(output["final_decision"]["decision"], {"strong_hire", "hire", "hold", "reject"})

    def test_interview_flow_single_round(self) -> None:
        engine = InterviewEngine()
        start = engine.start_interview(RESUME_TEXT, JD_TEXT, candidate_name="Test", max_rounds=1)

        self.assertIn("session_id", start)
        self.assertEqual(start["current_round"], 1)
        self.assertEqual(len(start["questions"]), 3)

        session_id = start["session_id"]
        answers = [
            {"agent": "tech", "answer_text": "I designed scalable FastAPI services with tests and monitoring in AWS."},
            {"agent": "manager", "answer_text": "I led planning, prioritized risks, and aligned stakeholders to deliver on time."},
            {"agent": "hr", "answer_text": "I resolve conflicts through listening, collaboration, and clear feedback loops."},
        ]
        result = engine.submit_round_answers(session_id, answers)
        self.assertEqual(result["status"], "finished")
        self.assertIn("final_result", result)
        self.assertIn(result["final_result"]["final_decision"]["decision"], {"strong_hire", "hire", "hold", "reject"})


if __name__ == "__main__":
    unittest.main()
