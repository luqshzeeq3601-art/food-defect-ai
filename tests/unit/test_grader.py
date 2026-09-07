"""Unit tests for the AOI Grader Rule Engine."""

import unittest

from src.core.grader import InspectionGrade, InspectionGrader


class TestInspectionGrader(unittest.TestCase):
    def setUp(self) -> None:
        self.grader = InspectionGrader(grade_a_threshold=1.0, grade_b_threshold=5.0)

    def test_no_object_detected(self) -> None:
        grade, ratio, reason = self.grader.evaluate(
            fruit_pixels=0, defect_pixels=0, defect_types=[]
        )
        self.assertEqual(grade, InspectionGrade.NO_OBJECT)
        self.assertEqual(ratio, 0.0)
        self.assertIsNotNone(reason)

    def test_grade_a_pass(self) -> None:
        # 500 defect pixels out of 100,000 fruit pixels = 0.5%
        grade, ratio, reason = self.grader.evaluate(
            fruit_pixels=100000,
            defect_pixels=500,
            defect_types=["bruise"],
        )
        self.assertEqual(grade, InspectionGrade.GRADE_A)
        self.assertEqual(ratio, 0.5)
        self.assertIsNone(reason)

    def test_grade_b_pass(self) -> None:
        # 2500 defect pixels out of 100,000 fruit pixels = 2.5%
        grade, ratio, reason = self.grader.evaluate(
            fruit_pixels=100000,
            defect_pixels=2500,
            defect_types=["scratch"],
        )
        self.assertEqual(grade, InspectionGrade.GRADE_B)
        self.assertEqual(ratio, 2.5)
        self.assertIsNone(reason)

    def test_defect_ratio_exceeds_threshold_reject(self) -> None:
        # 6000 defect pixels out of 100,000 fruit pixels = 6.0% (limit is 5.0%)
        grade, ratio, reason = self.grader.evaluate(
            fruit_pixels=100000,
            defect_pixels=6000,
            defect_types=["bruise", "scab"],
        )
        self.assertEqual(grade, InspectionGrade.REJECT)
        self.assertEqual(ratio, 6.0)
        self.assertIn("exceeds threshold", reason)

    def test_zero_tolerance_rot_reject(self) -> None:
        # Even with tiny defect ratio 0.1%, rot causes immediate rejection
        grade, ratio, reason = self.grader.evaluate(
            fruit_pixels=100000,
            defect_pixels=100,
            defect_types=["rot"],
        )
        self.assertEqual(grade, InspectionGrade.REJECT)
        self.assertEqual(ratio, 0.1)
        self.assertIn("rot detected", reason.lower())


if __name__ == "__main__":
    unittest.main()
