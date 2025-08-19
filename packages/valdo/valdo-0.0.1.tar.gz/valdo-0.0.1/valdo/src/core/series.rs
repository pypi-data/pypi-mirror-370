use crate::{Point, PointType};
use chrono::prelude::*;
use std::ops::{Index, Range};

#[derive(Debug, Clone)]
pub struct Series {
    pub points: Vec<Point>,
}

impl Series {
    pub fn new(points: Vec<Point>) -> Series {
        Series { points }
    }

    pub fn from_vec(
        vec: Vec<f64>,
        start_timestamp: Option<i64>,
        interval_seconds: Option<i64>,
    ) -> Series {
        let start_ts = start_timestamp.unwrap_or(Utc::now().timestamp());
        let interval = interval_seconds.unwrap_or(1);

        Series {
            points: vec
                .iter()
                .enumerate()
                .filter_map(|(i, v)| {
                    // Safely calculate timestamp to avoid overflow
                    let index_offset: i64 = (i as i64).checked_mul(interval)?;
                    let timestamp = start_ts.checked_add(index_offset)?;
                    Some(Point::new(timestamp, *v))
                })
                .collect(),
        }
    }

    pub fn len(&self) -> usize {
        self.points.len()
    }

    /// Check if the series is empty
    pub fn is_empty(&self) -> bool {
        self.points.is_empty()
    }

    /// Add a single point to the series
    pub fn push(&mut self, point: Point) {
        self.points.push(point);
    }

    /// Get a point at the specified index safely
    pub fn get(&self, index: usize) -> Option<&Point> {
        self.points.get(index)
    }

    /// Get aggregated validation results for all points in the series
    ///
    /// # Examples
    ///
    /// ```
    /// use valdo::{Point, Series, PointType};
    ///
    /// let points = vec![
    ///     Point::new(1000, 42.0),      // Valid
    ///     Point::new(-100, 1.0),       // NegativeTimestamp
    ///     Point::new(2000, f64::NAN),  // NanValue
    ///     Point::new(3000, f64::INFINITY), // InfinityValue
    /// ];
    /// let series = Series::new(points);
    ///
    /// let validation = series.validation_summary();
    /// assert_eq!(validation.get(&PointType::Valid), Some(&1));
    /// assert_eq!(validation.get(&PointType::NegativeTimestamp), Some(&1));
    /// assert_eq!(validation.get(&PointType::NanValue), Some(&1));
    /// assert_eq!(validation.get(&PointType::InfinityValue), Some(&1));
    /// ```
    pub fn validation_summary(&self) -> std::collections::HashMap<PointType, u32> {
        let mut total_counts = std::collections::HashMap::new();
        for point in &self.points {
            let validation = point.validation();
            for (point_type, count) in validation {
                *total_counts.entry(point_type).or_insert(0) += count;
            }
        }
        total_counts
    }

    /// Validate the entire series and return warnings
    ///
    /// This method checks for data quality issues across the entire series including:
    /// - Point-level validation issues (negative timestamps, NaN/infinite values)
    /// - Duplicate timestamps
    ///
    /// # Examples
    ///
    /// ```
    /// use valdo::{Point, Series};
    ///
    /// let series = Series::new(vec![
    ///     Point::new(1000, 42.0),      // Valid
    ///     Point::new(-100, 1.0),       // Negative timestamp
    ///     Point::new(2000, f64::NAN),  // NaN value
    ///     Point::new(1000, 10.0),      // Duplicate timestamp
    /// ]);
    ///
    /// let warnings = series.validate();
    /// // Will contain warnings about negative timestamp, NaN value, and duplicate timestamp
    /// assert!(!warnings.is_empty());
    /// ```
    pub fn validate(&self) -> Vec<String> {
        let mut warnings = Vec::new();

        // Check for point-level validation issues
        for (i, point) in self.points.iter().enumerate() {
            let point_warnings = point.validation_warnings();
            for warning in point_warnings {
                warnings.push(format!("Point {}: {}", i, warning));
            }
        }

        // Check for duplicate timestamps
        let mut timestamps = std::collections::HashSet::new();
        for (i, point) in self.points.iter().enumerate() {
            if !timestamps.insert(point.timestamp) {
                warnings.push(format!(
                    "Duplicate timestamp {} at index {}",
                    point.timestamp, i
                ));
            }
        }

        warnings
    }

    /// Get the time range (min and max timestamps) of the series
    ///
    /// Returns None if the series is empty, otherwise returns Some((min_timestamp, max_timestamp))
    ///
    /// # Examples
    ///
    /// ```
    /// use valdo::{Point, Series};
    ///
    /// let series = Series::new(vec![
    ///     Point::new(1000, 42.0),
    ///     Point::new(500, 84.0),   // Earlier timestamp
    ///     Point::new(2000, 126.0), // Later timestamp
    /// ]);
    ///
    /// let range = series.time_range();
    /// assert_eq!(range, Some((500, 2000)));
    ///
    /// // Empty series returns None
    /// let empty_series = Series::new(vec![]);
    /// assert_eq!(empty_series.time_range(), None);
    /// ```
    pub fn time_range(&self) -> Option<(i64, i64)> {
        if self.is_empty() {
            return None;
        }

        let min_ts = self.points.iter().map(|p| p.timestamp).min().unwrap();
        let max_ts = self.points.iter().map(|p| p.timestamp).max().unwrap();
        Some((min_ts, max_ts))
    }

    /// Calculate the mean of all finite values in the series
    ///
    /// Automatically filters out NaN and infinite values. Returns None if the series
    /// is empty or contains no finite values.
    ///
    /// # Examples
    ///
    /// ```
    /// use valdo::{Point, Series};
    ///
    /// let series = Series::new(vec![
    ///     Point::new(1000, 10.0),
    ///     Point::new(2000, 20.0),
    ///     Point::new(3000, f64::NAN),     // Filtered out
    ///     Point::new(4000, 30.0),
    ///     Point::new(5000, f64::INFINITY), // Filtered out
    /// ]);
    ///
    /// let mean = series.mean();
    /// assert_eq!(mean, Some(20.0)); // (10 + 20 + 30) / 3 = 20
    ///
    /// // Series with no finite values
    /// let nan_series = Series::new(vec![
    ///     Point::new(1000, f64::NAN),
    ///     Point::new(2000, f64::INFINITY),
    /// ]);
    /// assert_eq!(nan_series.mean(), None);
    ///
    /// // Empty series
    /// let empty_series = Series::new(vec![]);
    /// assert_eq!(empty_series.mean(), None);
    /// ```
    pub fn mean(&self) -> Option<f64> {
        if self.is_empty() {
            return None;
        }

        let finite_values: Vec<f64> = self
            .points
            .iter()
            .map(|p| p.value)
            .filter(|v| v.is_finite())
            .collect();

        if finite_values.is_empty() {
            return None;
        }

        let sum: f64 = finite_values.iter().sum();
        Some(sum / finite_values.len() as f64)
    }
}

// Make Series indexable with usize
impl Index<usize> for Series {
    type Output = Point;

    fn index(&self, index: usize) -> &Self::Output {
        &self.points[index]
    }
}

// Make Series sliceable with Range<usize>
impl Index<Range<usize>> for Series {
    type Output = [Point];

    fn index(&self, range: Range<usize>) -> &Self::Output {
        &self.points[range]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_series() {
        let points = vec![Point::new(1, 1.0), Point::new(2, f64::NAN)];
        let series = Series::new(points);

        assert_eq!(series.points.len(), 2);
    }

    #[test]
    fn test_series_indexing() {
        let series = Series::from_vec(vec![1.0, 2.0, 3.0, 4.0, 5.0], Some(0), Some(1));

        // Test single index
        assert_eq!(series[0].value, 1.0);
        assert_eq!(series[2].value, 3.0);

        // Test slice - returns &[Point]
        let slice = &series[1..4];
        assert_eq!(slice.len(), 3);
        assert_eq!(slice[0].value, 2.0);
        assert_eq!(slice[2].value, 4.0);
    }

    #[test]
    fn test_from_vec_with_timestamps() {
        // Test with custom start timestamp and interval
        let series = Series::from_vec(vec![10.0, 20.0, 30.0], Some(1000), Some(5));

        assert_eq!(series.len(), 3);
        assert_eq!(series[0].timestamp, 1000);
        assert_eq!(series[0].value, 10.0);
        assert_eq!(series[1].timestamp, 1005);
        assert_eq!(series[1].value, 20.0);
        assert_eq!(series[2].timestamp, 1010);
        assert_eq!(series[2].value, 30.0);
    }

    #[test]
    fn test_from_vec_with_defaults() {
        // Test with default values (None, None)
        let now_before = Utc::now().timestamp();
        let series = Series::from_vec(vec![1.0, 2.0, 3.0], None, None);
        let now_after = Utc::now().timestamp();

        assert_eq!(series.len(), 3);
        // Timestamp should be within a reasonable range of current time
        assert!(series[0].timestamp >= now_before);
        assert!(series[0].timestamp <= now_after);
        // Check interval is 1 second
        assert_eq!(series[1].timestamp - series[0].timestamp, 1);
        assert_eq!(series[2].timestamp - series[1].timestamp, 1);
    }

    #[test]
    fn test_from_vec_with_partial_defaults() {
        // Test with custom start time but default interval
        let series = Series::from_vec(vec![1.0, 2.0, 3.0], Some(2000), None);

        assert_eq!(series[0].timestamp, 2000);
        assert_eq!(series[1].timestamp, 2001);
        assert_eq!(series[2].timestamp, 2002);

        // Test with default start time but custom interval
        let now_before = Utc::now().timestamp();
        let series = Series::from_vec(vec![1.0, 2.0], None, Some(10));
        let now_after = Utc::now().timestamp();

        assert!(series[0].timestamp >= now_before);
        assert!(series[0].timestamp <= now_after);
        assert_eq!(series[1].timestamp - series[0].timestamp, 10);
    }

    #[test]
    fn test_from_vec_overflow_handling() {
        // Test that overflow conditions are handled gracefully
        let values = vec![1.0, 2.0, 3.0];

        // Case 1: Large start timestamp near i64::MAX
        let large_start = i64::MAX - 10;
        let series = Series::from_vec(values.clone(), Some(large_start), Some(1));
        // Should only include points that don't overflow
        assert!(!series.points.is_empty());
        assert!(series.len() <= values.len());

        // Case 2: Large interval that would cause overflow
        let series = Series::from_vec(values.clone(), Some(1000), Some(i64::MAX));
        // Should only include the first point (index 0) since others would overflow
        assert_eq!(series.len(), 1);
        assert_eq!(series[0].timestamp, 1000);
        assert_eq!(series[0].value, 1.0);

        // Case 3: Normal case should include all points
        let series = Series::from_vec(values.clone(), Some(1000), Some(1));
        assert_eq!(series.len(), values.len());
    }

    #[test]
    fn test_series_validation_summary() {
        let points = vec![
            Point::new(1000, 42.0),              // Valid
            Point::new(-100, 1.0),               // NegativeTimestamp
            Point::new(2000, f64::NAN),          // NanValue
            Point::new(3000, f64::INFINITY),     // InfinityValue
            Point::new(-200, f64::NEG_INFINITY), // Mixed: NegativeTimestamp + InfinityValue
            Point::new(4000, 123.45),            // Valid
        ];
        let series = Series::new(points);

        let validation = series.validation_summary();

        // Verify aggregated counts
        assert_eq!(validation.get(&PointType::Valid), Some(&2));
        assert_eq!(validation.get(&PointType::NegativeTimestamp), Some(&2));
        assert_eq!(validation.get(&PointType::NanValue), Some(&1));
        assert_eq!(validation.get(&PointType::InfinityValue), Some(&2));
    }

    #[test]
    fn test_series_convenience_methods() {
        // Test is_empty
        let empty_series = Series::new(vec![]);
        assert!(empty_series.is_empty());
        assert_eq!(empty_series.len(), 0);

        let non_empty_series = Series::new(vec![Point::new(1, 1.0)]);
        assert!(!non_empty_series.is_empty());
        assert_eq!(non_empty_series.len(), 1);

        // Test push
        let mut series = Series::new(vec![]);
        assert!(series.is_empty());

        series.push(Point::new(1000, 42.0));
        assert!(!series.is_empty());
        assert_eq!(series.len(), 1);
        assert_eq!(series[0].timestamp, 1000);
        assert_eq!(series[0].value, 42.0);

        series.push(Point::new(2000, 84.0));
        assert_eq!(series.len(), 2);
        assert_eq!(series[1].timestamp, 2000);
        assert_eq!(series[1].value, 84.0);

        // Test get method
        let series = Series::new(vec![
            Point::new(1000, 10.0),
            Point::new(2000, 20.0),
            Point::new(3000, 30.0),
        ]);

        // Valid indices
        assert_eq!(series.get(0).unwrap().timestamp, 1000);
        assert_eq!(series.get(0).unwrap().value, 10.0);
        assert_eq!(series.get(1).unwrap().timestamp, 2000);
        assert_eq!(series.get(1).unwrap().value, 20.0);
        assert_eq!(series.get(2).unwrap().timestamp, 3000);
        assert_eq!(series.get(2).unwrap().value, 30.0);

        // Invalid indices
        assert!(series.get(3).is_none());
        assert!(series.get(100).is_none());

        // Test get on empty series
        let empty_series = Series::new(vec![]);
        assert!(empty_series.get(0).is_none());
    }

    #[test]
    fn test_series_validate() {
        // Test valid series - no warnings
        let valid_series = Series::new(vec![
            Point::new(1000, 42.0),
            Point::new(2000, 84.0),
            Point::new(3000, 126.0),
        ]);
        let warnings = valid_series.validate();
        assert!(warnings.is_empty());

        // Test series with point-level validation issues
        let series_with_issues = Series::new(vec![
            Point::new(1000, 42.0),              // Valid
            Point::new(-100, 1.0),               // Negative timestamp
            Point::new(2000, f64::NAN),          // NaN value
            Point::new(3000, f64::INFINITY),     // Infinity value
            Point::new(-200, f64::NEG_INFINITY), // Mixed: negative timestamp + negative infinity
        ]);
        let warnings = series_with_issues.validate();

        // Should have warnings for each problematic point
        assert!(!warnings.is_empty());
        assert!(warnings.iter().any(|w| w.contains("Point 1")
            && w.contains("Negative timestamp")
            && w.contains("-100")));
        assert!(warnings
            .iter()
            .any(|w| w.contains("Point 2") && w.contains("NaN")));
        assert!(warnings
            .iter()
            .any(|w| w.contains("Point 3") && w.contains("positive infinity")));
        assert!(warnings.iter().any(|w| w.contains("Point 4")
            && w.contains("Negative timestamp")
            && w.contains("-200")));
        assert!(warnings
            .iter()
            .any(|w| w.contains("Point 4") && w.contains("negative infinity")));

        // Test series with duplicate timestamps
        let series_with_duplicates = Series::new(vec![
            Point::new(1000, 42.0),
            Point::new(2000, 84.0),
            Point::new(1000, 126.0), // Duplicate timestamp
            Point::new(3000, 168.0),
            Point::new(2000, 210.0), // Another duplicate
        ]);
        let warnings = series_with_duplicates.validate();

        // Should have warnings for duplicate timestamps
        assert!(!warnings.is_empty());
        assert!(warnings
            .iter()
            .any(|w| w.contains("Duplicate timestamp 1000 at index 2")));
        assert!(warnings
            .iter()
            .any(|w| w.contains("Duplicate timestamp 2000 at index 4")));

        // Test series with both point issues and duplicate timestamps
        let complex_series = Series::new(vec![
            Point::new(1000, 42.0),          // Valid
            Point::new(-100, f64::NAN),      // Negative timestamp + NaN
            Point::new(1000, 84.0),          // Duplicate timestamp
            Point::new(2000, f64::INFINITY), // Infinity
        ]);
        let warnings = complex_series.validate();

        // Should have warnings for all issues
        assert!(!warnings.is_empty());
        assert!(warnings
            .iter()
            .any(|w| w.contains("Point 1") && w.contains("Negative timestamp")));
        assert!(warnings
            .iter()
            .any(|w| w.contains("Point 1") && w.contains("NaN")));
        assert!(warnings
            .iter()
            .any(|w| w.contains("Duplicate timestamp 1000 at index 2")));
        assert!(warnings
            .iter()
            .any(|w| w.contains("Point 3") && w.contains("positive infinity")));

        // Test empty series - no warnings
        let empty_series = Series::new(vec![]);
        let warnings = empty_series.validate();
        assert!(warnings.is_empty());

        // Test series with many duplicate timestamps
        let many_duplicates = Series::new(vec![
            Point::new(1000, 1.0),
            Point::new(1000, 2.0), // First duplicate
            Point::new(1000, 3.0), // Second duplicate
            Point::new(2000, 4.0),
            Point::new(2000, 5.0), // First duplicate of 2000
        ]);
        let warnings = many_duplicates.validate();

        // Should detect all duplicates
        assert_eq!(warnings.len(), 3); // 2 duplicates of 1000, 1 duplicate of 2000
        assert!(warnings
            .iter()
            .any(|w| w.contains("Duplicate timestamp 1000 at index 1")));
        assert!(warnings
            .iter()
            .any(|w| w.contains("Duplicate timestamp 1000 at index 2")));
        assert!(warnings
            .iter()
            .any(|w| w.contains("Duplicate timestamp 2000 at index 4")));
    }

    #[test]
    fn test_series_time_range() {
        // Test normal series with mixed order timestamps
        let series = Series::new(vec![
            Point::new(1000, 42.0),
            Point::new(500, 84.0),   // Earlier timestamp
            Point::new(2000, 126.0), // Later timestamp
            Point::new(1500, 168.0),
        ]);
        let range = series.time_range();
        assert_eq!(range, Some((500, 2000)));

        // Test series with single point
        let single_point = Series::new(vec![Point::new(1000, 42.0)]);
        let range = single_point.time_range();
        assert_eq!(range, Some((1000, 1000)));

        // Test empty series
        let empty_series = Series::new(vec![]);
        let range = empty_series.time_range();
        assert_eq!(range, None);

        // Test series with negative timestamps
        let negative_series = Series::new(vec![
            Point::new(-1000, 10.0),
            Point::new(-500, 20.0),
            Point::new(-2000, 30.0),
        ]);
        let range = negative_series.time_range();
        assert_eq!(range, Some((-2000, -500)));

        // Test series with mix of positive and negative timestamps
        let mixed_series = Series::new(vec![
            Point::new(-100, 10.0),
            Point::new(100, 20.0),
            Point::new(0, 30.0),
        ]);
        let range = mixed_series.time_range();
        assert_eq!(range, Some((-100, 100)));

        // Test series with extreme values
        let extreme_series = Series::new(vec![
            Point::new(i64::MIN, 10.0),
            Point::new(i64::MAX, 20.0),
            Point::new(0, 30.0),
        ]);
        let range = extreme_series.time_range();
        assert_eq!(range, Some((i64::MIN, i64::MAX)));
    }

    #[test]
    fn test_series_mean() {
        // Test normal series with finite values
        let series = Series::new(vec![
            Point::new(1000, 10.0),
            Point::new(2000, 20.0),
            Point::new(3000, 30.0),
        ]);
        let mean = series.mean();
        assert_eq!(mean, Some(20.0));

        // Test series with mixed finite and non-finite values
        let mixed_series = Series::new(vec![
            Point::new(1000, 10.0),
            Point::new(2000, 20.0),
            Point::new(3000, f64::NAN), // Filtered out
            Point::new(4000, 30.0),
            Point::new(5000, f64::INFINITY),     // Filtered out
            Point::new(6000, f64::NEG_INFINITY), // Filtered out
        ]);
        let mean = mixed_series.mean();
        assert_eq!(mean, Some(20.0)); // (10 + 20 + 30) / 3 = 20

        // Test series with only non-finite values
        let nan_series = Series::new(vec![
            Point::new(1000, f64::NAN),
            Point::new(2000, f64::INFINITY),
            Point::new(3000, f64::NEG_INFINITY),
        ]);
        let mean = nan_series.mean();
        assert_eq!(mean, None);

        // Test empty series
        let empty_series = Series::new(vec![]);
        let mean = empty_series.mean();
        assert_eq!(mean, None);

        // Test series with single finite value
        let single_series = Series::new(vec![Point::new(1000, 42.0)]);
        let mean = single_series.mean();
        assert_eq!(mean, Some(42.0));

        // Test series with single non-finite value
        let single_nan = Series::new(vec![Point::new(1000, f64::NAN)]);
        let mean = single_nan.mean();
        assert_eq!(mean, None);

        // Test series with zero values
        let zero_series = Series::new(vec![
            Point::new(1000, 0.0),
            Point::new(2000, 10.0),
            Point::new(3000, -10.0),
        ]);
        let mean = zero_series.mean();
        assert_eq!(mean, Some(0.0)); // (0 + 10 + (-10)) / 3 = 0

        // Test series with negative values
        let negative_series = Series::new(vec![
            Point::new(1000, -10.0),
            Point::new(2000, -20.0),
            Point::new(3000, -30.0),
        ]);
        let mean = negative_series.mean();
        assert_eq!(mean, Some(-20.0));

        // Test series with very small and very large finite values
        let extreme_series = Series::new(vec![
            Point::new(1000, f64::MIN),
            Point::new(2000, f64::MAX),
            Point::new(3000, 0.0),
        ]);
        let mean = extreme_series.mean();
        // Due to floating point precision, we check that it's finite
        assert!(mean.is_some());
        assert!(mean.unwrap().is_finite());
    }
}
