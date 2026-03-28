from __future__ import annotations

import unittest

from backend.utils.parser import extract_resume_text_from_file


class ResumeParserTests(unittest.TestCase):
    def test_extract_plain_text_resume(self) -> None:
        content = (
            b"Backend engineer with 5 years of experience in Python, FastAPI, AWS, Docker, "
            b"and CI/CD delivery."
        )
        text = extract_resume_text_from_file("resume.txt", content)
        self.assertIn("Backend engineer", text)
        self.assertIn("FastAPI", text)

    def test_reject_unsupported_extension(self) -> None:
        with self.assertRaises(ValueError):
            extract_resume_text_from_file("resume.exe", b"not allowed")

    def test_reject_empty_upload(self) -> None:
        with self.assertRaises(ValueError):
            extract_resume_text_from_file("resume.pdf", b"")


if __name__ == "__main__":
    unittest.main()
