"""Tests for model classes."""
import pytest

from aisert.models.report import AisertReport
from aisert.models.result import Result, AisertStatus


class TestResult:
    """Test Result model functionality."""

    def test_result_creation(self):
        """Test Result creation with validator, status and reason."""
        result = Result("TestValidator", True, "Success message")
        assert result.validator == "TestValidator"
        assert result.status is True
        assert result.reason == "Success message"

    def test_result_to_dict(self):
        """Test Result to_dict conversion."""
        result = Result("ErrorValidator", False, "Error message")
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict['validator'] == "ErrorValidator"
        assert result_dict['status'] is False
        assert result_dict['reason'] == "Error message"


class TestAisertStatus:
    """Test AisertStatus functionality."""

    def test_aisert_status_creation(self):
        """Test AisertStatus initialization."""
        status = AisertStatus()
        assert isinstance(status.validators, dict)
        assert len(status.validators) == 0
        assert status._order == 1

    def test_update_status(self):
        """Test updating status with validator results."""
        status = AisertStatus()
        result = Result("TestValidator", True, "Success")
        
        status.update(result)
        assert 1 in status.validators
        assert status.validators[1] == result
        assert status._order == 2

    def test_multiple_updates_ordered(self):
        """Test multiple updates maintain order."""
        status = AisertStatus()
        result1 = Result("Validator1", True, "Success 1")
        result2 = Result("Validator2", False, "Error 2")
        
        status.update(result1)
        status.update(result2)
        
        assert len(status.validators) == 2
        assert status.validators[1] == result1
        assert status.validators[2] == result2
        assert status._order == 3

    def test_same_validator_multiple_times(self):
        """Test same validator can be added multiple times with different orders."""
        status = AisertStatus()
        result1 = Result("TestValidator", True, "First")
        result2 = Result("TestValidator", False, "Second")
        
        status.update(result1)
        status.update(result2)
        
        assert len(status.validators) == 2
        assert status.validators[1].reason == "First"
        assert status.validators[2].reason == "Second"


class TestAisertReport:
    """Test AisertReport functionality."""

    def test_report_creation(self):
        """Test AisertReport creation."""
        rules = {
            1: {"validator": "Validator1", "status": True, "reason": "Success"},
            2: {"validator": "Validator2", "status": False, "reason": "Error"}
        }
        report = AisertReport(status=False, rules=rules)
        
        assert report.status is False
        assert report.rules == rules

    def test_report_str_representation(self):
        """Test AisertReport string representation."""
        rules = {"TestValidator": {"status": True, "reason": "OK"}}
        report = AisertReport(status=True, rules=rules)
        
        str_repr = str(report)
        assert "Status: True" in str_repr
        assert "Rules:" in str_repr

    def test_report_with_empty_rules(self):
        """Test AisertReport with empty rules."""
        report = AisertReport(status=True, rules={})
        assert report.status is True
        assert report.rules == {}

    def test_report_attributes_access(self):
        """Test direct attribute access on AisertReport."""
        rules = {"Validator": {"status": True, "reason": "Good"}}
        report = AisertReport(status=True, rules=rules)
        
        # Test direct attribute access
        assert hasattr(report, 'status')
        assert hasattr(report, 'rules')
        assert report.status is True
        assert report.rules == rules

    def test_report_with_complex_rules(self):
        """Test AisertReport with complex nested rules."""
        rules = {
            "SchemaValidator": {
                "status": True,
                "reason": "Schema validation passed",
                "details": {"fields_validated": ["name", "age"]}
            },
            "ContainsValidator": {
                "status": False,
                "reason": "Missing items: ['required_field']",
                "missing_items": ["required_field"]
            }
        }
        
        report = AisertReport(status=False, rules=rules)
        assert report.status is False
        assert len(report.rules) == 2
        assert report.rules["SchemaValidator"]["status"] is True
        assert report.rules["ContainsValidator"]["status"] is False