"""AOI Defect Quantification and Quality Grading Engine."""

from enum import Enum


class DefectType(str, Enum):
    ROT = "rot"
    BRUISE = "bruise"
    SCAB = "scab"
    SCRATCH = "scratch"
    CRITICAL_DEFECT = "critical_defect"
    COSMETIC_DEFECT = "cosmetic_defect"


class InspectionGrade(str, Enum):
    GRADE_A = "PASS_GRADE_A"
    GRADE_B = "PASS_GRADE_B"
    REJECT = "REJECT"
    NO_OBJECT = "NO_OBJECT"


class InspectionGrader:
    """Evaluates defect severity and classifies item quality."""

    def __init__(
        self,
        grade_a_threshold: float = 1.0,
        grade_b_threshold: float = 5.0,
    ) -> None:
        """Initialize grading parameters.

        Args:
            grade_a_threshold: Maximum defect ratio (%) for Grade A.
            grade_b_threshold: Maximum defect ratio (%) for Grade B.
        """
        self.grade_a_threshold = grade_a_threshold
        self.grade_b_threshold = grade_b_threshold

    def calculate_defect_ratio(self, fruit_pixels: int, defect_pixels: int) -> float:
        """Compute the defect surface area ratio.

        Args:
            fruit_pixels: Total pixel count of the fruit mask.
            defect_pixels: Total pixel count of defect masks.

        Returns:
            Defect area percentage (0.0 to 100.0).
        """
        if fruit_pixels <= 0:
            return 0.0
        ratio = (defect_pixels / fruit_pixels) * 100.0
        return round(min(100.0, max(0.0, ratio)), 2)

    def evaluate(
        self,
        fruit_pixels: int,
        defect_pixels: int,
        defect_types: list[str],
    ) -> tuple[InspectionGrade, float, str | None]:
        """Evaluate fruit quality grade based on defect area and defect types.

        Args:
            fruit_pixels: Total pixel count of the fruit body.
            defect_pixels: Total pixel count of all defects combined.
            defect_types: List of detected defect class names (e.g., ['rot', 'bruise']).

        Returns:
            Tuple of (Grade, Defect Ratio %, Reject Reason if applicable).
        """
        if fruit_pixels <= 0:
            return InspectionGrade.NO_OBJECT, 0.0, "No valid fruit body detected"

        ratio = self.calculate_defect_ratio(fruit_pixels, defect_pixels)

        # Zero-tolerance check: rot or critical defect immediately rejects
        lower_defects = [d.lower() for d in defect_types]
        if any(
            DefectType.ROT.value in d or DefectType.CRITICAL_DEFECT.value in d
            for d in lower_defects
        ):
            return InspectionGrade.REJECT, ratio, "Active rot detected (zero-tolerance)"

        # Threshold based grading
        if ratio <= self.grade_a_threshold:
            return InspectionGrade.GRADE_A, ratio, None
        elif ratio <= self.grade_b_threshold:
            return InspectionGrade.GRADE_B, ratio, None
        else:
            return (
                InspectionGrade.REJECT,
                ratio,
                f"Defect area ({ratio}%) exceeds threshold ({self.grade_b_threshold}%)",
            )
