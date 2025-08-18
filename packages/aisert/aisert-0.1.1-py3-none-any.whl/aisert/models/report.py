class AisertReport:
    """
    Final validation report containing overall status and detailed results.
    
    Returned by Aisert.collect() to provide comprehensive validation outcomes.
    Contains both high-level pass/fail status and granular per-validation details.
    
    Attributes:
        status: True if all validations passed, False if any failed
        rules: Dictionary mapping execution order to validation results
               Format: {1: {'validator': 'ContainsValidator', 'status': True, 'reason': '...'}}
    
    Example:
        report = Aisert("Hello world").assert_contains(["Hello"]).collect()
        if report.status:
            print("All validations passed!")
        for order, result in report.rules.items():
            print(f"{order}: {result['validator']} - {result['status']}")
    """

    def __init__(self, status: bool, rules: dict):
        """
        Create a new validation report.
        
        Args:
            status: Overall validation status (True if all passed)
            rules: Dictionary of validation results keyed by execution order
        """
        self.status = status
        self.rules = rules

    def __str__(self) -> str:
        """
        Human-readable string representation of the validation report.
        
        Returns:
            Formatted string showing status and rules summary
        """
        return f"Status: {self.status} \n Rules: {self.rules}"
