# Validation Improvements Checklist

This document tracks planned improvements to the `validate_performance` tool and related validation logic.

## ✅ Completed

- [x] **Parse vCPUs from node type** - Updated `current_vcpus` to parse from node type string (e.g., "Standard_E8s_v3" → 8 vCPUs) instead of using hardcoded default
  - Created `parse_vcpus_from_node_type()` utility function
  - Updated `cluster_config_agent.py` to use the parser
  - Supports Standard_D, Standard_E, and Standard_F node families

---

## 🔄 Pending - Requires Metrics Data

### 1. Consider Resource Utilization Metrics

**Current State:**
- `validate_performance` receives `current_peak_cpu` and `current_peak_memory` but doesn't use them in calculations
- Only compares capacity (vCPUs × workers) without considering actual utilization

**Proposed Improvement:**
- Factor in actual CPU and memory utilization percentages when determining safe capacity reduction
- If peak CPU is 50%, we can safely reduce capacity more than if it's 90%
- Use utilization metrics to adjust the 80% threshold dynamically

**Required Information:**
- [ ] Sample resource utilization metrics from Databricks delta table
- [ ] Attributes/columns available in the metrics data
- [ ] Typical utilization ranges for different workload types
- [ ] Historical utilization patterns

**Implementation Notes:**
```python
# Example logic (to be refined with actual data):
if current_peak_cpu < 50:
    safe_reduction_threshold = 0.5  # Can reduce to 50% of current
elif current_peak_cpu < 70:
    safe_reduction_threshold = 0.7  # Can reduce to 70% of current
else:
    safe_reduction_threshold = 0.8  # Conservative 80% threshold
```

**Files to Update:**
- `AI/src/tools/validation_tools.py` - `validate_performance()` function
- May need to update `cluster_config_agent.py` to pass additional metrics

---

### 2. Conservative Approach Enhancement

**Current State:**
- Uses fixed 80% capacity threshold for all scenarios
- Risk levels based on reduction percentage (>20% = HIGH, >10% = MEDIUM, else LOW)
- Doesn't consider workload characteristics or historical patterns

**Proposed Improvements:**
- **Workload-specific thresholds:** Different thresholds for ETL vs ML training vs streaming
- **Historical pattern consideration:** Use historical utilization data to inform thresholds
- **Time-based patterns:** Consider peak vs off-peak utilization
- **Confidence scoring:** Factor in data quality and sample size

**Required Information:**
- [ ] Workload type classifications and their typical utilization patterns
- [ ] Historical utilization data structure from delta table
- [ ] Time-based patterns (hourly, daily, weekly variations)
- [ ] Sample data showing different workload types and their utilization characteristics

**Implementation Notes:**
```python
# Example logic (to be refined with actual data):
workload_thresholds = {
    "ETL": 0.7,           # ETL can handle more reduction
    "ML_Training": 0.85,  # ML needs more headroom
    "Streaming": 0.9,     # Streaming needs high capacity
    "Balanced": 0.8       # Default
}

# Consider historical patterns
if has_consistent_low_utilization:
    threshold = 0.6
elif has_variable_utilization:
    threshold = 0.85
```

**Files to Update:**
- `AI/src/tools/validation_tools.py` - `validate_performance()` function
- May need to update `RecommendationState` to include workload type
- May need to update data collection to include historical patterns

---

## 📋 Data Requirements Checklist

To implement the above improvements, we need:

### Resource Utilization Metrics
- [ ] **CPU Metrics:**
  - [ ] Peak CPU utilization percentage
  - [ ] Average CPU utilization percentage
  - [ ] P95/P99 CPU utilization
  - [ ] CPU utilization over time (time series data)

- [ ] **Memory Metrics:**
  - [ ] Peak memory utilization percentage
  - [ ] Average memory utilization percentage
  - [ ] P95/P99 memory utilization
  - [ ] Memory utilization over time

- [ ] **Workload Characteristics:**
  - [ ] Workload type classification
  - [ ] Execution time patterns (consistent vs variable)
  - [ ] Resource consumption patterns
  - [ ] Time-based patterns (hourly/daily/weekly)

- [ ] **Historical Data:**
  - [ ] Sample size (number of runs)
  - [ ] Date range of data
  - [ ] Data quality indicators
  - [ ] Outlier information

### Sample Data Format
Please provide:
- [ ] Sample rows from the Databricks delta table
- [ ] Column names and data types
- [ ] Example values for each metric
- [ ] Any aggregations or transformations applied

---

## 🎯 Next Steps

1. **Review this checklist** with the team
2. **Provide sample data** from Databricks delta table with:
   - Resource utilization metrics structure
   - Sample rows showing different workload types
   - Historical utilization patterns
3. **Define thresholds** based on actual data analysis
4. **Implement improvements** once data is available
5. **Test with real data** to validate improvements

---

## 📝 Notes

- Current implementation is conservative and safe (80% threshold)
- Improvements should maintain or improve safety while allowing more accurate recommendations
- All changes should be backward compatible
- Consider A/B testing improvements before full rollout

---

**Last Updated:** 2024-01-31
**Status:** Waiting for metrics data and sample data from Databricks delta table

