import json
import uuid
from typing import Dict, List, Any, Optional, Union, Tuple
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, when, lit, coalesce
from pyspark.sql.types import BooleanType
try:
    from .rule_processor import RuleProcessor
except ImportError:
    from rule_processor import RuleProcessor


class DQFramework:
    """
    Data Quality Framework that filters DataFrames based on Great Expectations rules.
    
    Takes quality rules, columns, and a DataFrame as input.
    Returns qualified rows and bad rows as separate DataFrames.
    """
    
    def __init__(self):
        """
        Initialize the DQ Framework.
        """
        self.rule_processor = RuleProcessor()
    
    def filter_dataframe(
        self,
        dataframe: DataFrame,
        quality_rules: Union[str, Dict, List[Dict]],
        columns: Optional[List[str]] = None,
        include_validation_details: bool = False
    ) -> Tuple[DataFrame, DataFrame]:
        """
        Filter a DataFrame based on quality rules, returning qualified and bad rows.
        
        Args:
            dataframe: The Spark DataFrame to filter
            quality_rules: Quality rules as JSON string, dict, or list of expectations
            columns: Optional list of columns to focus validation on. If None, uses all columns
            include_validation_details: If True, adds validation detail columns to output
            
        Returns:
            Tuple of (qualified_df, bad_df) - DataFrames with qualified and bad rows
        """
        # Parse quality rules
        parsed_rules = self._parse_quality_rules(quality_rules)
        
        # Filter columns if specified
        if columns:
            dataframe = dataframe.select(*columns)
        
        # Create row-level validation flags
        validation_df = self._create_validation_flags(dataframe, parsed_rules)
        
        # Split into qualified and bad rows
        qualified_df, bad_df = self._split_dataframe(
            validation_df, 
            include_validation_details
        )
        
        return qualified_df, bad_df
    
    def validate_and_filter(
        self,
        dataframe: DataFrame,
        quality_rules: Union[str, Dict, List[Dict]],
        columns: Optional[List[str]] = None,
        return_validation_summary: bool = True
    ) -> Dict[str, Any]:
        """
        Validate and filter a DataFrame, returning detailed results.
        
        Args:
            dataframe: The Spark DataFrame to validate and filter
            quality_rules: Quality rules as JSON string, dict, or list of expectations
            columns: Optional list of columns to focus validation on
            return_validation_summary: If True, includes detailed validation summary
            
        Returns:
            Dictionary containing qualified_df, bad_df, and optional validation summary
        """
        qualified_df, bad_df = self.filter_dataframe(
            dataframe, quality_rules, columns, include_validation_details=True
        )
        
        result = {
            "qualified_df": qualified_df,
            "bad_df": bad_df,
            "qualified_count": qualified_df.count(),
            "bad_count": bad_df.count(),
            "total_count": dataframe.count()
        }
        
        if return_validation_summary:
            result["validation_summary"] = self._create_validation_summary(
                dataframe, qualified_df, bad_df, quality_rules
            )
        
        return result
    
    def _parse_quality_rules(self, quality_rules: Union[str, Dict, List[Dict]]) -> List[Dict]:
        """Parse quality rules into a standardized list format."""
        if isinstance(quality_rules, str):
            quality_rules = json.loads(quality_rules)
        
        if isinstance(quality_rules, dict):
            if "expectations" in quality_rules:
                return quality_rules["expectations"]
            else:
                return [quality_rules]
        
        return quality_rules
    
    def _create_validation_flags(self, dataframe: DataFrame, rules: List[Dict]) -> DataFrame:
        """Create boolean validation flags for each rule and combine them."""
        validation_df = dataframe
        rule_columns = []
        
        for i, rule in enumerate(rules):
            rule_name = f"rule_{i}_{rule.get('expectation_type', 'unknown')}"
            rule_columns.append(rule_name)
            
            # Create validation condition for this rule
            condition = self.rule_processor.create_validation_condition(rule, dataframe)
            validation_df = validation_df.withColumn(rule_name, condition)
        
        # Create overall validation flag (all rules must pass)
        if rule_columns:
            overall_condition = col(rule_columns[0])
            for rule_col in rule_columns[1:]:
                overall_condition = overall_condition & col(rule_col)
            
            validation_df = validation_df.withColumn("_dq_is_valid", overall_condition)
        else:
            # No rules means all rows are valid
            validation_df = validation_df.withColumn("_dq_is_valid", lit(True))
        
        # Add individual rule results as metadata
        validation_df = validation_df.withColumn(
            "_dq_rule_results", 
            lit(",".join([f"{col}:" for col in rule_columns]))
        )
        
        return validation_df
    
    def _split_dataframe(
        self, 
        validation_df: DataFrame, 
        include_validation_details: bool
    ) -> Tuple[DataFrame, DataFrame]:
        """Split the dataframe into qualified and bad rows based on validation flags."""
        
        # Get original columns (exclude our DQ columns)
        original_columns = [col_name for col_name in validation_df.columns 
                          if not col_name.startswith("_dq_") and not col_name.startswith("rule_")]
        
        if include_validation_details:
            # Include validation details in output
            qualified_df = validation_df.filter(col("_dq_is_valid") == True)
            bad_df = validation_df.filter(col("_dq_is_valid") == False)
        else:
            # Only return original columns
            qualified_df = validation_df.filter(col("_dq_is_valid") == True).select(*original_columns)
            bad_df = validation_df.filter(col("_dq_is_valid") == False).select(*original_columns)
        
        return qualified_df, bad_df
    
    def _create_validation_summary(
        self, 
        original_df: DataFrame, 
        qualified_df: DataFrame, 
        bad_df: DataFrame,
        quality_rules: Union[str, Dict, List[Dict]]
    ) -> Dict[str, Any]:
        """Create a comprehensive validation summary."""
        total_count = original_df.count()
        qualified_count = qualified_df.count()
        bad_count = bad_df.count()
        
        return {
            "total_rows": total_count,
            "qualified_rows": qualified_count,
            "bad_rows": bad_count,
            "qualified_percentage": round((qualified_count / total_count * 100), 2) if total_count > 0 else 0,
            "bad_percentage": round((bad_count / total_count * 100), 2) if total_count > 0 else 0,
            "total_rules": len(self._parse_quality_rules(quality_rules)),
            "rules_applied": len(self._parse_quality_rules(quality_rules)),
            "validation_timestamp": str(uuid.uuid4())
        } 