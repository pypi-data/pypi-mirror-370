#!/usr/bin/env python3
"""
Test environment validation using mock solvers.
This tests the environment's ability to validate different solution types.
"""

import sys
import os
import unittest

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tests.mock_data import create_mock_environment
from tests.mock_solvers import MOCK_SOLVERS


class TestEnvironmentValidation(unittest.TestCase):
    """Test environment validation with various mock solver outputs."""
    
    def setUp(self):
        """Set up test environment."""
        self.env = create_mock_environment()
    
    def test_valid_solution_acceptance(self):
        """Test that valid solutions are accepted."""
        solver = MOCK_SOLVERS['valid']
        solution = solver(self.env)
        
        is_valid, message = self.env.validate_solution_complete(solution)
        self.assertTrue(is_valid, f"Valid solution rejected: {message}")
        
        # Should be able to calculate metrics without errors
        stats = self.env.get_solution_statistics(solution)
        self.assertIsInstance(stats, dict)
        self.assertIn('total_cost', stats)
        
    def test_invalid_route_rejection(self):
        """Test that solutions with invalid routes are rejected."""
        solver = MOCK_SOLVERS['invalid_route']
        solution = solver(self.env)
        
        is_valid, message = self.env.validate_solution_complete(solution)
        self.assertFalse(is_valid, "Invalid route solution was accepted")
        self.assertIn("route", message.lower())
        
    def test_capacity_violation_rejection(self):
        """Test that solutions violating capacity are rejected."""
        solver = MOCK_SOLVERS['capacity_violation']
        solution = solver(self.env)
        
        is_valid, message = self.env.validate_solution_complete(solution)
        self.assertFalse(is_valid, "Capacity violation solution was accepted")
        
    def test_wrong_warehouse_rejection(self):
        """Test that routes not starting/ending at home warehouse are rejected."""
        solver = MOCK_SOLVERS['wrong_warehouse']
        solution = solver(self.env)
        
        is_valid, message = self.env.validate_solution_complete(solution)
        self.assertFalse(is_valid, "Wrong warehouse solution was accepted")
        self.assertIn("warehouse", message.lower())
        
    def test_empty_solution_handling(self):
        """Test that empty solutions are handled gracefully."""
        solver = MOCK_SOLVERS['empty_solution']
        solution = solver(self.env)
        
        is_valid, message = self.env.validate_solution_complete(solution)
        self.assertTrue(is_valid, "Empty solution should be valid")
        
        # Empty solution should have zero metrics
        stats = self.env.get_solution_statistics(solution)
        self.assertEqual(stats['total_cost'], 0)
        self.assertEqual(stats['total_distance'], 0)
        
    def test_malformed_solution_rejection(self):
        """Test that malformed solutions are rejected."""
        solver = MOCK_SOLVERS['malformed_solution']
        solution = solver(self.env)
        
        is_valid, message = self.env.validate_solution_complete(solution)
        self.assertFalse(is_valid, "Malformed solution was accepted")
        
    def test_partial_fulfillment_tracking(self):
        """Test partial fulfillment tracking with detailed operations."""
        solver = MOCK_SOLVERS['partial_fulfillment']
        solution = solver(self.env)
        
        # Should be valid even with partial fulfillment
        is_valid, message = self.env.validate_solution_complete(solution)
        self.assertTrue(is_valid, f"Partial fulfillment solution rejected: {message}")
        
        # Should track fulfillment correctly
        fulfillment = self.env.get_solution_fulfillment_summary(solution)
        self.assertIn('order_fulfillment_details', fulfillment)
        self.assertGreater(fulfillment['orders_served'], 0)
        
    def test_metrics_consistency(self):
        """Test that metrics are consistent across multiple calls."""
        solver = MOCK_SOLVERS['valid']
        solution = solver(self.env)
        
        # Calculate metrics multiple times
        stats1 = self.env.get_solution_statistics(solution)
        stats2 = self.env.get_solution_statistics(solution)
        
        # Should be identical
        self.assertEqual(stats1['total_cost'], stats2['total_cost'])
        self.assertEqual(stats1['total_distance'], stats2['total_distance'])
        
    def test_distance_calculation_accuracy(self):
        """Test that distance calculations are accurate."""
        solver = MOCK_SOLVERS['valid']
        solution = solver(self.env)
        
        for route in solution['routes']:
            route_path = route.get('route', [])
            if route_path:
                # Calculate distance using environment
                env_distance = self.env.get_route_distance(route_path)
                
                # Should be non-negative
                self.assertGreaterEqual(env_distance, 0)
                
                # If solution includes distance, should match
                if 'distance' in route:
                    solution_distance = route['distance']
                    self.assertAlmostEqual(env_distance, solution_distance, places=1)


def run_environment_tests():
    """Run all environment validation tests."""
    print("=" * 60)
    print("ENVIRONMENT VALIDATION TESTING")
    print("=" * 60)
    
    # Run unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEnvironmentValidation)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n" + "=" * 60)
        print("ALL ENVIRONMENT TESTS PASSED!")
        print("Environment validation is working correctly.")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("SOME ENVIRONMENT TESTS FAILED!")
        print("Check environment validation logic.")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = run_environment_tests()
    sys.exit(0 if success else 1)
