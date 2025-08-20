#!/usr/bin/env python3
"""
Integration Tests - Complete End-to-End Pipeline
================================================

This file contains comprehensive integration tests that verify the complete
user workflows from start to finish. These tests ensure that all components
work together correctly in real-world usage scenarios.
"""

import pytest
import pandas as pd
import tempfile
import os
import csv
from pathlib import Path

from funputer.preflight import run_preflight
from funputer.metadata_inference import infer_metadata_from_dataframe
from funputer.analyzer import analyze_imputation_requirements, analyze_dataframe
from funputer.cli import cli
from funputer.models import ColumnMetadata
from click.testing import CliRunner


class TestEndToEndPipeline:
    """Test complete end-to-end workflows that users actually perform."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        
        # Create realistic test data
        self.test_data = pd.DataFrame({
            'customer_id': [1001, 1002, 1003, 1004, 1005],
            'age': [25, None, 35, 42, 28],
            'income': [50000, 65000, None, 78000, 52000],
            'category': ['Premium', 'Standard', 'Premium', None, 'Basic'],
            'is_active': [True, False, True, True, False],
            'registration_date': ['2023-01-15', '2023-02-20', None, '2023-01-08', '2023-03-10'],
            'rating': [4.2, 3.8, 4.5, None, 3.9]
        })
    
    def test_complete_auto_inference_pipeline(self):
        """
        Test complete pipeline with auto-inference (most common user workflow).
        
        Flow: Data → Auto-inference → Analysis → Results
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 1: Create data file
            data_path = os.path.join(temp_dir, "test_data.csv")
            self.test_data.to_csv(data_path, index=False)
            
            # Step 2: Run complete auto-inference analysis
            suggestions = analyze_imputation_requirements(data_path)
            
            # Verify results
            assert len(suggestions) == 7  # All columns analyzed
            
            # Verify suggestions exist for columns with missing data
            columns_with_missing = ['age', 'income', 'category', 'registration_date', 'rating']
            suggestion_columns = [s.column_name for s in suggestions if s.missing_count > 0]
            
            for col in columns_with_missing:
                assert col in suggestion_columns, f"Missing suggestion for column with nulls: {col}"
            
            # Verify confidence scores are reasonable
            confidences = [s.confidence_score for s in suggestions]
            assert all(0.0 <= c <= 1.0 for c in confidences), "Confidence scores should be between 0 and 1"
            assert any(c > 0.5 for c in confidences), "Should have some high-confidence suggestions"
    
    def test_complete_metadata_driven_pipeline(self):
        """
        Test complete pipeline with explicit metadata (production workflow).
        
        Flow: Data → Metadata Creation → Analysis → Results
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 1: Create data file
            data_path = os.path.join(temp_dir, "test_data.csv")
            self.test_data.to_csv(data_path, index=False)
            
            # Step 2: Create metadata
            metadata = [
                ColumnMetadata(column_name="customer_id", data_type="integer", unique_flag=True, do_not_impute=True),
                ColumnMetadata(column_name="age", data_type="integer", min_value=18, max_value=120),
                ColumnMetadata(column_name="income", data_type="float", min_value=0),
                ColumnMetadata(column_name="category", data_type="categorical", allowed_values="Premium,Standard,Basic"),
                ColumnMetadata(column_name="is_active", data_type="boolean"),
                ColumnMetadata(column_name="registration_date", data_type="datetime"),
                ColumnMetadata(column_name="rating", data_type="float", min_value=1.0, max_value=5.0)
            ]
            
            # Step 3: Run analysis with metadata
            suggestions = analyze_dataframe(self.test_data, metadata)
            
            # Verify customer_id still appears but with "No action needed" due to do_not_impute=True
            suggestion_columns = {s.column_name for s in suggestions}
            assert "customer_id" in suggestion_columns
            
            customer_id_suggestion = next(s for s in suggestions if s.column_name == "customer_id")
            assert customer_id_suggestion.proposed_method == "No action needed"
            
            # Should have suggestions for all columns
            assert len(suggestions) == 7
            
            # Verify constraint-aware suggestions
            income_suggestion = next(s for s in suggestions if s.column_name == "income")
            assert income_suggestion.proposed_method in ["Mean", "Median", "kNN"], "Income should use numeric method"
            
            category_suggestion = next(s for s in suggestions if s.column_name == "category")
            assert "Premium,Standard,Basic" in str(category_suggestion) or category_suggestion.proposed_method in ["Mode", "kNN"]
    
    def test_complete_cli_workflow_init_analyze(self):
        """
        Test complete CLI workflow: init → analyze.
        
        Flow: funputer init → funputer analyze
        """
        with self.runner.isolated_filesystem():
            # Step 1: Create test data file
            self.test_data.to_csv("data.csv", index=False)
            
            # Step 2: Run init command to generate metadata template
            init_result = self.runner.invoke(cli, ['init', '-d', 'data.csv', '-o', 'metadata.csv'])
            assert init_result.exit_code == 0, f"Init failed: {init_result.output}"
            assert os.path.exists("metadata.csv"), "Metadata template should be created"
            
            # Step 3: Verify metadata template structure
            with open("metadata.csv", 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 7, "Should have metadata for all columns"
                assert all(row['column_name'] for row in rows), "All rows should have column names"
            
            # Step 4: Run analyze command with generated metadata
            analyze_result = self.runner.invoke(cli, ['analyze', '-m', 'metadata.csv', '-d', 'data.csv', '-o', 'results.csv'])
            assert analyze_result.exit_code == 0, f"Analyze failed: {analyze_result.output}"
            assert "Analysis complete!" in analyze_result.output
            
            # Step 5: Verify results file
            assert os.path.exists("results.csv"), "Results file should be created"
            results_df = pd.read_csv("results.csv")
            assert len(results_df) > 0, "Should have imputation suggestions"
            
            # Verify required columns in results
            required_cols = ['Column', 'Proposed_Method', 'Confidence_Score', 'Missing_Count']
            for col in required_cols:
                assert col in results_df.columns, f"Results should contain {col} column"
    
    def test_preflight_to_analysis_workflow(self):
        """
        Test workflow with preflight checks.
        
        Flow: preflight → analysis based on recommendation
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 1: Create data file
            data_path = os.path.join(temp_dir, "test_data.csv")
            self.test_data.to_csv(data_path, index=False)
            
            # Step 2: Run preflight check
            preflight_report = run_preflight(data_path)
            assert preflight_report['status'] in ['ok', 'ok_with_warnings'], "Preflight should pass"
            
            # Step 3: Follow preflight recommendation
            recommendation = preflight_report['recommendation']['action']
            
            if recommendation == 'analyze_infer_only':
                # Direct analysis with auto-inference
                suggestions = analyze_imputation_requirements(data_path)
                assert len(suggestions) > 0, "Should get suggestions from auto-inference"
                
            elif recommendation == 'generate_metadata':
                # Should generate metadata first, then analyze
                # This would be the CLI workflow tested above
                pass
                
            # Verify preflight data matches analysis
            structure_info = preflight_report['checks']['A5_structure']
            suggestions = analyze_imputation_requirements(data_path)
            
            assert structure_info['total_columns'] == len(self.test_data.columns)
            assert len(suggestions) == len(self.test_data.columns)
    
    def test_error_handling_integration(self):
        """Test integrated error handling across the pipeline."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test 1: Missing data file
            with pytest.raises(FileNotFoundError):
                analyze_imputation_requirements("nonexistent_file.csv")
            
            # Test 2: Invalid metadata
            data_path = os.path.join(temp_dir, "data.csv")
            self.test_data.to_csv(data_path, index=False)
            
            bad_metadata_path = os.path.join(temp_dir, "bad_metadata.csv")
            with open(bad_metadata_path, 'w') as f:
                f.write("invalid,header\n1,2")  # Wrong structure
            
            with self.runner.isolated_filesystem():
                self.test_data.to_csv("data.csv", index=False)
                with open("bad_metadata.csv", 'w') as f:
                    f.write("invalid,header\n1,2")
                
                result = self.runner.invoke(cli, ['analyze', '-m', 'bad_metadata.csv', '-d', 'data.csv'])
                assert result.exit_code != 0, "Should fail with invalid metadata"
    
    def test_performance_integration(self):
        """Test that the complete pipeline performs reasonably on larger data."""
        import time
        
        # Create larger dataset
        large_data = pd.concat([self.test_data] * 100, ignore_index=True)  # 500 rows
        
        with tempfile.TemporaryDirectory() as temp_dir:
            data_path = os.path.join(temp_dir, "large_data.csv")
            large_data.to_csv(data_path, index=False)
            
            # Time the complete pipeline
            start_time = time.time()
            suggestions = analyze_imputation_requirements(data_path)
            end_time = time.time()
            
            # Verify results
            assert len(suggestions) == 7, "Should analyze all columns"
            
            # Verify reasonable performance (should complete in under 10 seconds)
            execution_time = end_time - start_time
            assert execution_time < 10.0, f"Pipeline took too long: {execution_time:.2f}s"
    
    def test_data_types_integration(self):
        """Test pipeline handles various data types correctly."""
        complex_data = pd.DataFrame({
            'int_col': [10, 20, None, 20, 30],  # Avoid unique values that trigger ID detection
            'float_col': [1.1, 2.2, None, 2.2, 3.3],  # Avoid unique values
            'str_col': ['a', 'b', None, 'b', 'c'],  # Avoid unique values
            'bool_col': [True, False, None, True, False],
            'datetime_col': pd.to_datetime(['2023-01-01', '2023-01-02', None, '2023-01-04', '2023-01-05']),
            'categorical_col': pd.Categorical(['X', 'Y', None, 'X', 'Y'])
        })
        
        with tempfile.TemporaryDirectory() as temp_dir:
            data_path = os.path.join(temp_dir, "complex_data.csv")
            complex_data.to_csv(data_path, index=False)
            
            # Test auto-inference handles all types
            suggestions = analyze_imputation_requirements(data_path)
            assert len(suggestions) == 6, "Should handle all data types"
            
            # Verify appropriate methods for each type
            suggestion_dict = {s.column_name: s for s in suggestions}
            
            # Numeric columns should get numeric methods
            assert suggestion_dict['int_col'].proposed_method in ['Mean', 'Median', 'kNN']
            assert suggestion_dict['float_col'].proposed_method in ['Mean', 'Median', 'kNN']
            
            # Categorical columns should get categorical methods
            assert suggestion_dict['str_col'].proposed_method in ['Mode', 'kNN']
            assert suggestion_dict['bool_col'].proposed_method in ['Mode', 'kNN']


class TestRegressionPrevention:
    """Tests to prevent regression of key functionality."""
    
    def test_backward_compatibility_api(self):
        """Ensure backward compatibility of main API functions."""
        # Create simple test data
        data = pd.DataFrame({
            'col1': [1, 2, None, 4],
            'col2': ['a', 'b', None, 'd']
        })
        
        # Test 1: DataFrame API (direct)
        suggestions = analyze_dataframe(data)
        assert len(suggestions) == 2
        
        # Test 2: Auto-inference from metadata
        metadata = infer_metadata_from_dataframe(data, warn_user=False)
        assert len(metadata) == 2
        assert all(hasattr(m, 'column_name') for m in metadata)
        
        # Test 3: Analysis with inferred metadata
        suggestions2 = analyze_dataframe(data, metadata)
        assert len(suggestions2) == 2
        assert suggestions2[0].column_name in ['col1', 'col2']
    
    def test_cli_commands_exist(self):
        """Ensure all expected CLI commands exist and are accessible."""
        runner = CliRunner()
        
        # Test help command
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'FunPuter' in result.output
        
        # Test subcommands exist
        assert 'init' in result.output
        assert 'analyze' in result.output
        assert 'preflight' in result.output
    
    def test_essential_imports_work(self):
        """Test that all essential imports work as expected."""
        # Test main package imports
        import funputer
        from funputer import analyze_imputation_requirements
        from funputer.models import ColumnMetadata, AnalysisConfig
        from funputer.preflight import run_preflight
        from funputer.metadata_inference import infer_metadata_from_dataframe
        
        # Verify functions are callable
        assert callable(analyze_imputation_requirements)
        assert callable(run_preflight)
        assert callable(infer_metadata_from_dataframe)
        
        # Verify classes can be instantiated
        metadata = ColumnMetadata(column_name="test", data_type="string")
        assert metadata.column_name == "test"
        
        config = AnalysisConfig()
        assert hasattr(config, 'iqr_multiplier')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])