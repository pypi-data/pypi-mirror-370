use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq, Hash, Eq)]
pub enum PointType {
    Valid,
    NegativeTimestamp,
    NanValue,
    InfinityValue,
    Mixed(Vec<PointType>),
}

#[derive(Debug, Clone)]
pub struct Point {
    pub timestamp: i64,
    pub value: f64,
}

impl Point {
    pub fn new(timestamp: i64, value: f64) -> Point {
        Point { timestamp, value }
    }

    /// Check if the timestamp is non-negative (valid)
    pub fn has_valid_timestamp(&self) -> bool {
        self.timestamp >= 0
    }

    /// Check if the value is finite (not NaN or infinity)
    pub fn has_finite_value(&self) -> bool {
        self.value.is_finite()
    }

    /// Get the point type based on validation criteria
    pub fn point_type(&self) -> PointType {
        let mut issues = Vec::new();

        if !self.has_valid_timestamp() {
            issues.push(PointType::NegativeTimestamp);
        }

        if !self.has_finite_value() {
            if self.value.is_nan() {
                issues.push(PointType::NanValue);
            } else if self.value.is_infinite() {
                issues.push(PointType::InfinityValue);
            }
        }

        match issues.len() {
            0 => PointType::Valid,
            1 => issues.into_iter().next().unwrap(),
            _ => PointType::Mixed(issues),
        }
    }

    /// Get validation result as a count map for easy aggregation
    ///
    /// # Examples
    ///
    /// ```
    /// use valdo::{Point, PointType};
    /// use std::collections::HashMap;
    ///
    /// // Valid point
    /// let point = Point::new(1000, 42.0);
    /// let validation = point.validation();
    /// assert_eq!(validation.get(&PointType::Valid), Some(&1));
    ///
    /// // Point with issues
    /// let point = Point::new(-100, f64::NAN);
    /// let validation = point.validation();
    /// assert_eq!(validation.get(&PointType::NegativeTimestamp), Some(&1));
    /// assert_eq!(validation.get(&PointType::NanValue), Some(&1));
    ///
    /// // Aggregate multiple points
    /// let points = vec![
    ///     Point::new(1000, 42.0),      // Valid
    ///     Point::new(-100, 1.0),       // NegativeTimestamp
    ///     Point::new(2000, f64::NAN),  // NanValue
    /// ];
    ///
    /// let mut total_counts: HashMap<PointType, u32> = HashMap::new();
    /// for point in &points {
    ///     let validation = point.validation();
    ///     for (point_type, count) in validation {
    ///         *total_counts.entry(point_type).or_insert(0) += count;
    ///     }
    /// }
    ///
    /// assert_eq!(total_counts.get(&PointType::Valid), Some(&1));
    /// assert_eq!(total_counts.get(&PointType::NegativeTimestamp), Some(&1));
    /// assert_eq!(total_counts.get(&PointType::NanValue), Some(&1));
    /// ```
    pub fn validation(&self) -> HashMap<PointType, u32> {
        let mut counts = HashMap::new();

        match self.point_type() {
            PointType::Valid => {
                counts.insert(PointType::Valid, 1);
            }
            PointType::Mixed(ref types) => {
                for point_type in types {
                    *counts.entry(point_type.clone()).or_insert(0) += 1;
                }
            }
            single_type => {
                counts.insert(single_type, 1);
            }
        }

        counts
    }

    /// Get validation warnings for this point (kept for backward compatibility)
    pub fn validation_warnings(&self) -> Vec<String> {
        match self.point_type() {
            PointType::Valid => Vec::new(),
            PointType::NegativeTimestamp => {
                vec![format!("Negative timestamp: {}", self.timestamp)]
            }
            PointType::NanValue => {
                vec!["Value is NaN".to_string()]
            }
            PointType::InfinityValue => {
                if self.value.is_sign_positive() {
                    vec!["Value is positive infinity".to_string()]
                } else {
                    vec!["Value is negative infinity".to_string()]
                }
            }
            PointType::Mixed(ref types) => types
                .iter()
                .flat_map(|t| match t {
                    PointType::NegativeTimestamp => {
                        vec![format!("Negative timestamp: {}", self.timestamp)]
                    }
                    PointType::NanValue => {
                        vec!["Value is NaN".to_string()]
                    }
                    PointType::InfinityValue => {
                        if self.value.is_sign_positive() {
                            vec!["Value is positive infinity".to_string()]
                        } else {
                            vec!["Value is negative infinity".to_string()]
                        }
                    }
                    _ => Vec::new(),
                })
                .collect(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::prelude::*;

    #[test]
    fn test_point() {
        let timestamp = Utc::now().timestamp();
        let point = Point::new(timestamp, 1.0);

        assert_eq!(point.timestamp, timestamp);
        assert_eq!(point.value, 1.0);
    }

    #[test]
    fn test_point_has_valid_timestamp() {
        // Valid timestamps (non-negative)
        let point1 = Point::new(0, 1.0);
        assert!(point1.has_valid_timestamp());

        let point2 = Point::new(1234567890, 2.0);
        assert!(point2.has_valid_timestamp());

        // Invalid timestamps (negative)
        let point3 = Point::new(-1, 3.0);
        assert!(!point3.has_valid_timestamp());

        let point4 = Point::new(-1000, 4.0);
        assert!(!point4.has_valid_timestamp());
    }

    #[test]
    fn test_point_has_finite_value() {
        // Finite values
        let point1 = Point::new(1, 0.0);
        assert!(point1.has_finite_value());

        let point2 = Point::new(2, 123.456);
        assert!(point2.has_finite_value());

        let point3 = Point::new(3, -789.123);
        assert!(point3.has_finite_value());

        let point4 = Point::new(4, f64::MIN);
        assert!(point4.has_finite_value());

        let point5 = Point::new(5, f64::MAX);
        assert!(point5.has_finite_value());

        // Non-finite values
        let point6 = Point::new(6, f64::NAN);
        assert!(!point6.has_finite_value());

        let point7 = Point::new(7, f64::INFINITY);
        assert!(!point7.has_finite_value());

        let point8 = Point::new(8, f64::NEG_INFINITY);
        assert!(!point8.has_finite_value());
    }

    #[test]
    fn test_point_validation_warnings() {
        // Valid point - no warnings
        let point1 = Point::new(1000, 42.0);
        let warnings1 = point1.validation_warnings();
        assert!(warnings1.is_empty());

        // Point with negative timestamp
        let point2 = Point::new(-100, 1.0);
        let warnings2 = point2.validation_warnings();
        assert_eq!(warnings2.len(), 1);
        assert!(warnings2[0].contains("Negative timestamp"));
        assert!(warnings2[0].contains("-100"));

        // Point with NaN value
        let point3 = Point::new(1000, f64::NAN);
        let warnings3 = point3.validation_warnings();
        assert_eq!(warnings3.len(), 1);
        assert!(warnings3[0].contains("NaN"));

        // Point with positive infinity
        let point4 = Point::new(1000, f64::INFINITY);
        let warnings4 = point4.validation_warnings();
        assert_eq!(warnings4.len(), 1);
        assert!(warnings4[0].contains("positive infinity"));

        // Point with negative infinity
        let point5 = Point::new(1000, f64::NEG_INFINITY);
        let warnings5 = point5.validation_warnings();
        assert_eq!(warnings5.len(), 1);
        assert!(warnings5[0].contains("negative infinity"));

        // Point with both negative timestamp and NaN value
        let point6 = Point::new(-50, f64::NAN);
        let warnings6 = point6.validation_warnings();
        assert_eq!(warnings6.len(), 2);
        assert!(warnings6.iter().any(|w| w.contains("Negative timestamp")));
        assert!(warnings6.iter().any(|w| w.contains("NaN")));

        // Point with negative timestamp and positive infinity
        let point7 = Point::new(-25, f64::INFINITY);
        let warnings7 = point7.validation_warnings();
        assert_eq!(warnings7.len(), 2);
        assert!(warnings7.iter().any(|w| w.contains("Negative timestamp")));
        assert!(warnings7.iter().any(|w| w.contains("positive infinity")));

        // Point with negative timestamp and negative infinity
        let point8 = Point::new(-75, f64::NEG_INFINITY);
        let warnings8 = point8.validation_warnings();
        assert_eq!(warnings8.len(), 2);
        assert!(warnings8.iter().any(|w| w.contains("Negative timestamp")));
        assert!(warnings8.iter().any(|w| w.contains("negative infinity")));
    }

    #[test]
    fn test_point_edge_cases() {
        // Test edge case: timestamp at boundary (0)
        let point1 = Point::new(0, 1.0);
        assert!(point1.has_valid_timestamp());
        assert!(point1.validation_warnings().is_empty());

        // Test edge case: very large positive timestamp
        let point2 = Point::new(i64::MAX, 1.0);
        assert!(point2.has_valid_timestamp());
        assert!(point2.validation_warnings().is_empty());

        // Test edge case: very small negative timestamp
        let point3 = Point::new(i64::MIN, 1.0);
        assert!(!point3.has_valid_timestamp());
        let warnings = point3.validation_warnings();
        assert_eq!(warnings.len(), 1);
        assert!(warnings[0].contains("Negative timestamp"));

        // Test edge case: zero value
        let point4 = Point::new(1000, 0.0);
        assert!(point4.has_finite_value());
        assert!(point4.validation_warnings().is_empty());

        // Test edge case: very small positive value
        let point5 = Point::new(1000, f64::MIN_POSITIVE);
        assert!(point5.has_finite_value());
        assert!(point5.validation_warnings().is_empty());

        // Test edge case: very large negative value
        let point6 = Point::new(1000, f64::MIN);
        assert!(point6.has_finite_value());
        assert!(point6.validation_warnings().is_empty());
    }

    #[test]
    fn test_point_constructor_unchanged() {
        // Verify that Point::new still accepts any valid Rust types
        // This ensures backward compatibility

        // Should accept negative timestamps
        let point1 = Point::new(-1, 1.0);
        assert_eq!(point1.timestamp, -1);
        assert_eq!(point1.value, 1.0);

        // Should accept NaN values
        let point2 = Point::new(1, f64::NAN);
        assert_eq!(point2.timestamp, 1);
        assert!(point2.value.is_nan());

        // Should accept infinity values
        let point3 = Point::new(2, f64::INFINITY);
        assert_eq!(point3.timestamp, 2);
        assert!(point3.value.is_infinite() && point3.value.is_sign_positive());

        let point4 = Point::new(3, f64::NEG_INFINITY);
        assert_eq!(point4.timestamp, 3);
        assert!(point4.value.is_infinite() && point4.value.is_sign_negative());

        // Should accept any valid i64 and f64 combinations
        let point5 = Point::new(i64::MAX, f64::MAX);
        assert_eq!(point5.timestamp, i64::MAX);
        assert_eq!(point5.value, f64::MAX);

        let point6 = Point::new(i64::MIN, f64::MIN);
        assert_eq!(point6.timestamp, i64::MIN);
        assert_eq!(point6.value, f64::MIN);
    }

    #[test]
    fn test_point_type_classification() {
        // Valid point
        let point1 = Point::new(1000, 42.0);
        assert_eq!(point1.point_type(), PointType::Valid);

        // Negative timestamp only
        let point2 = Point::new(-100, 1.0);
        assert_eq!(point2.point_type(), PointType::NegativeTimestamp);

        // NaN value only
        let point3 = Point::new(1000, f64::NAN);
        assert_eq!(point3.point_type(), PointType::NanValue);

        // Positive infinity only
        let point4 = Point::new(1000, f64::INFINITY);
        assert_eq!(point4.point_type(), PointType::InfinityValue);

        // Negative infinity only
        let point5 = Point::new(1000, f64::NEG_INFINITY);
        assert_eq!(point5.point_type(), PointType::InfinityValue);

        // Mixed: negative timestamp + NaN
        let point6 = Point::new(-50, f64::NAN);
        match point6.point_type() {
            PointType::Mixed(types) => {
                assert_eq!(types.len(), 2);
                assert!(types.contains(&PointType::NegativeTimestamp));
                assert!(types.contains(&PointType::NanValue));
            }
            _ => panic!("Expected Mixed point type"),
        }

        // Mixed: negative timestamp + positive infinity
        let point7 = Point::new(-25, f64::INFINITY);
        match point7.point_type() {
            PointType::Mixed(types) => {
                assert_eq!(types.len(), 2);
                assert!(types.contains(&PointType::NegativeTimestamp));
                assert!(types.contains(&PointType::InfinityValue));
            }
            _ => panic!("Expected Mixed point type"),
        }

        // Mixed: negative timestamp + negative infinity
        let point8 = Point::new(-75, f64::NEG_INFINITY);
        match point8.point_type() {
            PointType::Mixed(types) => {
                assert_eq!(types.len(), 2);
                assert!(types.contains(&PointType::NegativeTimestamp));
                assert!(types.contains(&PointType::InfinityValue));
            }
            _ => panic!("Expected Mixed point type"),
        }
    }

    #[test]
    fn test_point_type_enum_properties() {
        // Test PartialEq implementation
        assert_eq!(PointType::Valid, PointType::Valid);
        assert_eq!(PointType::NegativeTimestamp, PointType::NegativeTimestamp);
        assert_ne!(PointType::Valid, PointType::NegativeTimestamp);

        // Test Clone implementation
        let point_type = PointType::NanValue;
        let cloned = point_type.clone();
        assert_eq!(point_type, cloned);

        // Test Debug implementation (should not panic)
        let debug_str = format!(
            "{:?}",
            PointType::Mixed(vec![PointType::NegativeTimestamp, PointType::NanValue])
        );
        assert!(debug_str.contains("Mixed"));
    }

    #[test]
    fn test_validation_warnings_with_point_type() {
        // Test that validation_warnings still works correctly with the new point_type method

        // Valid point - no warnings
        let point1 = Point::new(1000, 42.0);
        let warnings1 = point1.validation_warnings();
        assert!(warnings1.is_empty());
        assert_eq!(point1.point_type(), PointType::Valid);

        // Point with negative timestamp
        let point2 = Point::new(-100, 1.0);
        let warnings2 = point2.validation_warnings();
        assert_eq!(warnings2.len(), 1);
        assert!(warnings2[0].contains("Negative timestamp"));
        assert!(warnings2[0].contains("-100"));
        assert_eq!(point2.point_type(), PointType::NegativeTimestamp);

        // Point with NaN value
        let point3 = Point::new(1000, f64::NAN);
        let warnings3 = point3.validation_warnings();
        assert_eq!(warnings3.len(), 1);
        assert!(warnings3[0].contains("NaN"));
        assert_eq!(point3.point_type(), PointType::NanValue);

        // Point with positive infinity
        let point4 = Point::new(1000, f64::INFINITY);
        let warnings4 = point4.validation_warnings();
        assert_eq!(warnings4.len(), 1);
        assert!(warnings4[0].contains("positive infinity"));
        assert_eq!(point4.point_type(), PointType::InfinityValue);

        // Point with negative infinity
        let point5 = Point::new(1000, f64::NEG_INFINITY);
        let warnings5 = point5.validation_warnings();
        assert_eq!(warnings5.len(), 1);
        assert!(warnings5[0].contains("negative infinity"));
        assert_eq!(point5.point_type(), PointType::InfinityValue);

        // Point with mixed issues
        let point6 = Point::new(-50, f64::NAN);
        let warnings6 = point6.validation_warnings();
        assert_eq!(warnings6.len(), 2);
        assert!(warnings6.iter().any(|w| w.contains("Negative timestamp")));
        assert!(warnings6.iter().any(|w| w.contains("NaN")));
        match point6.point_type() {
            PointType::Mixed(_) => {} // Expected
            _ => panic!("Expected Mixed point type"),
        }
    }

    #[test]
    fn test_validation_count_map() {
        // Valid point
        let point1 = Point::new(1000, 42.0);
        let validation1 = point1.validation();
        assert_eq!(validation1.len(), 1);
        assert_eq!(validation1.get(&PointType::Valid), Some(&1));

        // Point with negative timestamp
        let point2 = Point::new(-100, 1.0);
        let validation2 = point2.validation();
        assert_eq!(validation2.len(), 1);
        assert_eq!(validation2.get(&PointType::NegativeTimestamp), Some(&1));

        // Point with NaN value
        let point3 = Point::new(1000, f64::NAN);
        let validation3 = point3.validation();
        assert_eq!(validation3.len(), 1);
        assert_eq!(validation3.get(&PointType::NanValue), Some(&1));

        // Point with infinity value (positive)
        let point4 = Point::new(1000, f64::INFINITY);
        let validation4 = point4.validation();
        assert_eq!(validation4.len(), 1);
        assert_eq!(validation4.get(&PointType::InfinityValue), Some(&1));

        // Point with infinity value (negative)
        let point5 = Point::new(1000, f64::NEG_INFINITY);
        let validation5 = point5.validation();
        assert_eq!(validation5.len(), 1);
        assert_eq!(validation5.get(&PointType::InfinityValue), Some(&1));

        // Point with mixed issues: negative timestamp + NaN
        let point6 = Point::new(-50, f64::NAN);
        let validation6 = point6.validation();
        assert_eq!(validation6.len(), 2);
        assert_eq!(validation6.get(&PointType::NegativeTimestamp), Some(&1));
        assert_eq!(validation6.get(&PointType::NanValue), Some(&1));

        // Point with mixed issues: negative timestamp + infinity
        let point7 = Point::new(-25, f64::INFINITY);
        let validation7 = point7.validation();
        assert_eq!(validation7.len(), 2);
        assert_eq!(validation7.get(&PointType::NegativeTimestamp), Some(&1));
        assert_eq!(validation7.get(&PointType::InfinityValue), Some(&1));
    }

    #[test]
    fn test_validation_aggregation_example() {
        // Example of how validation counts can be aggregated across multiple points
        let points = vec![
            Point::new(1000, 42.0),              // Valid
            Point::new(-100, 1.0),               // NegativeTimestamp
            Point::new(2000, f64::NAN),          // NanValue
            Point::new(3000, f64::INFINITY),     // InfinityValue
            Point::new(-200, f64::NEG_INFINITY), // Mixed: NegativeTimestamp + InfinityValue
            Point::new(4000, 123.45),            // Valid
        ];

        // Aggregate validation results
        let mut total_counts: HashMap<PointType, u32> = HashMap::new();
        for point in &points {
            let validation = point.validation();
            for (point_type, count) in validation {
                *total_counts.entry(point_type).or_insert(0) += count;
            }
        }

        // Verify aggregated counts
        assert_eq!(total_counts.get(&PointType::Valid), Some(&2));
        assert_eq!(total_counts.get(&PointType::NegativeTimestamp), Some(&2));
        assert_eq!(total_counts.get(&PointType::NanValue), Some(&1));
        assert_eq!(total_counts.get(&PointType::InfinityValue), Some(&2));
    }
}
