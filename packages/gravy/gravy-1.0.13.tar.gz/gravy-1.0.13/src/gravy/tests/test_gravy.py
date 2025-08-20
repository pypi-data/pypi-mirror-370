import math
import unittest

from gravy import score


class TestScoreFunction(unittest.TestCase):

    def test_valid_sequence(self):
        """Test a valid sequence with known values."""
        seq = "ACDEFGHIKLMNPQRSTVWY"
        expected_score = (
            1.8
            + 2.5
            - 3.5
            - 3.5
            + 2.8
            - 0.4
            - 3.2
            + 4.5
            - 3.9
            + 3.8
            + 1.9
            - 3.5
            - 1.6
            - 3.5
            - 4.5
            - 0.8
            - 0.7
            + 4.2
            - 0.9
            - 1.3
        ) / 20
        self.assertAlmostEqual(score(seq), expected_score)

    def test_sequence_with_gap(self):
        """Test a sequence with gaps ('-')."""
        seq = "ACDEFGHI-KLMNPQRSTVWY"
        expected_score = (
            1.8
            + 2.5
            - 3.5
            - 3.5
            + 2.8
            - 0.4
            - 3.2
            + 4.5
            - 3.9
            + 3.8
            + 1.9
            - 3.5
            - 1.6
            - 3.5
            - 4.5
            - 0.8
            - 0.7
            + 4.2
            - 0.9
            - 1.3
        ) / 20
        self.assertAlmostEqual(score(seq), expected_score)

    def test_sequence_with_unknown_values(self):
        """Test a sequence with unknown or unsupported values ('X')."""
        seq = "ACDEXFGHIKLMNPQRSTVWY"
        expected_score = (
            1.8
            + 2.5
            - 3.5
            - 3.5
            + 2.8
            - 0.4
            - 3.2
            + 4.5
            - 3.9
            + 3.8
            + 1.9
            - 3.5
            - 1.6
            - 3.5
            - 4.5
            - 0.8
            - 0.7
            + 4.2
            - 0.9
            - 1.3
        ) / 20
        self.assertAlmostEqual(score(seq), expected_score)

    def test_sequence_with_only_gaps(self):
        """Test a sequence with only gaps ('-'), which should return NaN."""
        seq = "---"
        result = score(seq)
        self.assertTrue(math.isnan(result))

    def test_sequence_with_only_unknown_values(self):
        """Test a sequence with only unknown values ('X'), which should return NaN."""
        seq = "XXX"
        result = score(seq)
        self.assertTrue(math.isnan(result))

    def test_empty_sequence(self):
        """Test an empty sequence, which should return NaN."""
        seq = ""
        result = score(seq)
        self.assertTrue(math.isnan(result))

    def test_single_known_value(self):
        """Test a sequence with a single known value."""
        seq = "A"
        self.assertAlmostEqual(score(seq), 1.8)

    def test_single_unknown_value(self):
        """Test a sequence with a single unknown value ('X'), which should return NaN."""
        seq = "X"
        result = score(seq)
        self.assertTrue(math.isnan(result))


if __name__ == "__main__":
    unittest.main()
