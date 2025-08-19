"""Tests for scoring functionality."""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import gpu_benchmark
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gpu_benchmark.scoring import score_gpu_health


class TestScoring(unittest.TestCase):
    """Test GPU health scoring functionality."""

    def test_score_gpu_health_basic(self):
        """Test basic GPU health scoring."""
        result = score_gpu_health(
            baseline_temp=45,
            max_temp=75,
            power_draw=150,
            utilization=95
        )

        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 4)
        
        score, status, recommendation, details = result
        
        self.assertIsInstance(score, int)
        self.assertIsInstance(status, str)
        self.assertIsInstance(recommendation, str)
        self.assertIsInstance(details, dict)
        
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        self.assertIn(status, ["healthy", "good", "degraded", "warning", "critical"])

    def test_score_gpu_health_healthy_gpu(self):
        """Test scoring for a healthy GPU."""
        result = score_gpu_health(
            baseline_temp=40,
            max_temp=70,
            power_draw=120,
            utilization=99,
            throttled=False,
            errors=False
        )

        score, status, recommendation, details = result
        
        # Should be healthy with good scores
        self.assertGreaterEqual(score, 80)
        self.assertIn(status, ["healthy", "good"])

    def test_score_gpu_health_critical_gpu(self):
        """Test scoring for a critical GPU."""
        result = score_gpu_health(
            baseline_temp=60,
            max_temp=95,
            power_draw=200,
            utilization=50,
            throttled=True,
            errors=True
        )

        score, status, recommendation, details = result
        
        # Should be critical with poor scores
        self.assertLessEqual(score, 50)
        self.assertIn(status, ["warning", "critical"])

    def test_score_gpu_health_temperature_scoring(self):
        """Test temperature-based scoring."""
        # Test excellent temperature
        result = score_gpu_health(
            baseline_temp=35,
            max_temp=65,
            power_draw=100,
            utilization=90
        )
        score1, _, _, details1 = result
        
        # Test poor temperature
        result = score_gpu_health(
            baseline_temp=55,
            max_temp=90,
            power_draw=100,
            utilization=90
        )
        score2, _, _, details2 = result
        
        # First should score higher than second
        self.assertGreater(score1, score2)
        
        # Check temperature breakdown
        self.assertIn("temperature", details1["breakdown"])
        self.assertIn("baseline_temp", details1["breakdown"])

    def test_score_gpu_health_power_scoring(self):
        """Test power-based scoring."""
        # Test good power efficiency
        result = score_gpu_health(
            baseline_temp=45,
            max_temp=75,
            power_draw=65,
            utilization=95
        )
        score1, _, _, details1 = result
        
        # Test poor power efficiency
        result = score_gpu_health(
            baseline_temp=45,
            max_temp=75,
            power_draw=85,
            utilization=95
        )
        score2, _, _, details2 = result
        
        # First should score higher than second
        self.assertGreater(score1, score2)
        
        # Check power breakdown
        self.assertIn("power_efficiency", details1["breakdown"])

    def test_score_gpu_health_utilization_scoring(self):
        """Test utilization-based scoring."""
        # Test high utilization
        result = score_gpu_health(
            baseline_temp=45,
            max_temp=75,
            power_draw=150,
            utilization=99
        )
        score1, _, _, details1 = result
        
        # Test low utilization
        result = score_gpu_health(
            baseline_temp=45,
            max_temp=75,
            power_draw=150,
            utilization=70
        )
        score2, _, _, details2 = result
        
        # High utilization should score higher
        self.assertGreater(score1, score2)
        
        # Check utilization breakdown
        self.assertIn("utilization", details1["breakdown"])

    def test_score_gpu_health_throttling_scoring(self):
        """Test throttling-based scoring."""
        # Test no throttling
        result = score_gpu_health(
            baseline_temp=45,
            max_temp=75,
            power_draw=150,
            utilization=95,
            throttled=False
        )
        score1, _, _, details1 = result
        
        # Test with throttling
        result = score_gpu_health(
            baseline_temp=45,
            max_temp=75,
            power_draw=150,
            utilization=95,
            throttled=True
        )
        score2, _, _, details2 = result
        
        # No throttling should score higher
        self.assertGreater(score1, score2)
        
        # Check throttling breakdown
        self.assertIn("throttling", details1["breakdown"])

    def test_score_gpu_health_error_scoring(self):
        """Test error-based scoring."""
        # Test no errors
        result = score_gpu_health(
            baseline_temp=45,
            max_temp=75,
            power_draw=150,
            utilization=95,
            errors=False
        )
        score1, _, _, details1 = result
        
        # Test with errors
        result = score_gpu_health(
            baseline_temp=45,
            max_temp=75,
            power_draw=150,
            utilization=95,
            errors=True
        )
        score2, _, _, details2 = result
        
        # No errors should score higher
        self.assertGreater(score1, score2)
        
        # Check error breakdown
        self.assertIn("errors", details1["breakdown"])

    def test_score_gpu_health_enhanced_metrics(self):
        """Test scoring with enhanced metrics."""
        temperature_stability = {
            "stability_score": 85,
            "std_dev": 2.5,
            "max_delta": 10,
            "avg_rate_of_change": 0.5
        }
        
        throttle_events = [
            {"timestamp": 10, "reasons": ["Thermal limit"]},
            {"timestamp": 20, "reasons": ["Power limit"]}
        ]
        
        result = score_gpu_health(
            baseline_temp=45,
            max_temp=75,
            power_draw=150,
            utilization=95,
            throttled=False,
            errors=False,
            throttle_events=throttle_events,
            temperature_stability=temperature_stability
        )

        score, status, recommendation, details = result
        
        self.assertIsInstance(score, int)
        self.assertIsInstance(status, str)
        self.assertIsInstance(recommendation, str)
        self.assertIsInstance(details, dict)
        
        # Check enhanced breakdown
        breakdown = details["breakdown"]
        self.assertIn("temperature_stability", breakdown)
        
        # Check specific recommendations
        self.assertIn("specific_recommendations", details)
        self.assertIsInstance(details["specific_recommendations"], list)

    def test_score_gpu_health_missing_metrics(self):
        """Test scoring with missing metrics."""
        result = score_gpu_health(
            baseline_temp=-1,
            max_temp=-1,
            power_draw=-1,
            utilization=-1
        )

        score, status, recommendation, details = result
        
        # Should handle missing metrics gracefully
        self.assertIsInstance(score, int)
        self.assertIsInstance(status, str)
        self.assertIsInstance(recommendation, str)

    def test_score_gpu_health_status_ranges(self):
        """Test status ranges for different scores."""
        # Test healthy range (85-100)
        result = score_gpu_health(
            baseline_temp=35,
            max_temp=65,
            power_draw=65,
            utilization=99,
            throttled=False,
            errors=False
        )
        score, status, _, _ = result
        if score >= 85:
            self.assertEqual(status, "healthy")

        # Test good range (70-84)
        result = score_gpu_health(
            baseline_temp=45,
            max_temp=75,
            power_draw=75,
            utilization=90,
            throttled=False,
            errors=False
        )
        score, status, _, _ = result
        if 70 <= score < 85:
            self.assertEqual(status, "good")

        # Test degraded range (55-69)
        result = score_gpu_health(
            baseline_temp=50,
            max_temp=80,
            power_draw=85,
            utilization=80,
            throttled=False,
            errors=False
        )
        score, status, _, _ = result
        if 55 <= score < 70:
            self.assertEqual(status, "degraded")

        # Test warning range (40-54)
        result = score_gpu_health(
            baseline_temp=55,
            max_temp=85,
            power_draw=95,
            utilization=70,
            throttled=True,
            errors=False
        )
        score, status, _, _ = result
        if 40 <= score < 55:
            self.assertEqual(status, "warning")

        # Test critical range (0-39)
        result = score_gpu_health(
            baseline_temp=60,
            max_temp=95,
            power_draw=200,
            utilization=50,
            throttled=True,
            errors=True
        )
        score, status, _, _ = result
        if score < 40:
            self.assertEqual(status, "critical")

    def test_score_gpu_health_specific_recommendations(self):
        """Test specific recommendations generation."""
        # Test high temperature recommendation
        result = score_gpu_health(
            baseline_temp=60,
            max_temp=90,
            power_draw=150,
            utilization=95,
            throttled=False,
            errors=False
        )
        _, _, _, details = result
        
        recommendations = details["specific_recommendations"]
        self.assertIsInstance(recommendations, list)
        
        # Should have temperature recommendation
        temp_recs = [rec for rec in recommendations if "temperature" in rec.lower()]
        self.assertGreater(len(temp_recs), 0)

        # Test throttling recommendation
        result = score_gpu_health(
            baseline_temp=45,
            max_temp=75,
            power_draw=150,
            utilization=95,
            throttled=True,
            errors=False
        )
        _, _, _, details = result
        
        recommendations = details["specific_recommendations"]
        throttle_recs = [rec for rec in recommendations if "throttl" in rec.lower()]
        self.assertGreater(len(throttle_recs), 0)

    def test_score_gpu_health_max_score(self):
        """Test maximum possible score."""
        result = score_gpu_health(
            baseline_temp=35,
            max_temp=65,
            power_draw=65,
            utilization=99,
            throttled=False,
            errors=False,
            temperature_stability={"stability_score": 95}
        )

        score, status, _, details = result
        
        # Check max score in details
        self.assertIn("max_score", details)
        self.assertEqual(details["max_score"], 100)
        
        # Score should not exceed max
        self.assertLessEqual(score, 100)


if __name__ == '__main__':
    unittest.main() 