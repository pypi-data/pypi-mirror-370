use std::collections::HashMap;
use std::io::Write;
use tempfile::NamedTempFile;
use valdo::{Error, Point, PointType, Series};

#[test]
fn test_complete_workflow_csv_to_analysis() {
    // Test complete workflow: CSV import -> validation -> analysis -> export

    // Create test CSV data with various issues
    let mut temp_file = NamedTempFile::new().unwrap();
    writeln!(temp_file, "timestamp,value").unwrap();
    writeln!(temp_file, "1000,42.0").unwrap(); // Valid
    writeln!(temp_file, "-100,10.0").unwrap(); // Negative timestamp
    writeln!(temp_file, "2000,NaN").unwrap(); // NaN value
    writeln!(temp_file, "3000,inf").unwrap(); // Infinity
    writeln!(temp_file, "4000,25.5").unwrap(); // Valid
    writeln!(temp_file, "1000,30.0").unwrap(); // Duplicate timestamp
    writeln!(temp_file, "5000,-15.2").unwrap(); // Valid negative value
    temp_file.flush().unwrap();

    // Step 1: Import from CSV
    let series = Series::from_csv(temp_file.path()).unwrap();
    assert_eq!(series.len(), 7);

    // Step 2: Validation
    let warnings = series.validate();
    assert!(!warnings.is_empty());

    // Check specific validation issues
    assert!(warnings
        .iter()
        .any(|w| w.contains("Point 1") && w.contains("Negative timestamp")));
    assert!(warnings
        .iter()
        .any(|w| w.contains("Point 2") && w.contains("NaN")));
    assert!(warnings
        .iter()
        .any(|w| w.contains("Point 3") && w.contains("infinity")));
    assert!(warnings
        .iter()
        .any(|w| w.contains("Duplicate timestamp 1000")));

    // Step 3: Validation summary
    let validation_summary = series.validation_summary();
    assert_eq!(validation_summary.get(&PointType::Valid), Some(&4)); // 4 valid points
    assert_eq!(
        validation_summary.get(&PointType::NegativeTimestamp),
        Some(&1)
    );
    assert_eq!(validation_summary.get(&PointType::NanValue), Some(&1));
    assert_eq!(validation_summary.get(&PointType::InfinityValue), Some(&1));

    // Step 4: Time range analysis
    let time_range = series.time_range();
    assert_eq!(time_range, Some((-100, 5000)));

    // Step 5: Statistical analysis (should filter out non-finite values)
    let mean = series.mean();
    assert!(mean.is_some());
    // Mean should be calculated from: 42.0, 10.0, 25.5, 30.0, -15.2
    // (42.0 + 10.0 + 25.5 + 30.0 - 15.2) / 5 = 92.3 / 5 = 18.46
    assert!((mean.unwrap() - 18.46).abs() < 0.01);

    // Step 6: Export to new CSV
    let output_file = NamedTempFile::new().unwrap();
    series.to_csv(output_file.path()).unwrap();

    // Step 7: Re-import and verify roundtrip
    let reimported = Series::from_csv(output_file.path()).unwrap();
    assert_eq!(reimported.len(), series.len());

    // Verify data integrity (accounting for NaN comparison)
    for (original, reimported) in series.points.iter().zip(reimported.points.iter()) {
        assert_eq!(original.timestamp, reimported.timestamp);
        if original.value.is_nan() {
            assert!(reimported.value.is_nan());
        } else {
            assert_eq!(original.value, reimported.value);
        }
    }
}

#[test]
fn test_real_world_scenario_sensor_data() {
    // Simulate real-world sensor data with common issues
    let sensor_data = vec![
        Point::new(1640995200, 23.5),          // Normal temperature reading
        Point::new(1640995260, 23.7),          // 60 seconds later
        Point::new(1640995320, 24.1),          // Normal progression
        Point::new(-1, 0.0),                   // Invalid timestamp (sensor error)
        Point::new(1640995380, f64::NAN),      // Sensor malfunction
        Point::new(1640995440, 156.8),         // Sensor spike (probably invalid but finite)
        Point::new(1640995500, 24.3),          // Back to normal
        Point::new(1640995500, 24.2),          // Duplicate timestamp (sensor double-read)
        Point::new(1640995560, f64::INFINITY), // Sensor overflow
        Point::new(1640995620, 23.9),          // Normal reading
        Point::new(1640995680, 23.6),          // Normal reading
    ];

    let series = Series::new(sensor_data);

    // Validation should catch problematic data
    let warnings = series.validate();
    assert!(warnings.len() >= 3); // At least negative timestamp, NaN, infinity, duplicate

    // Statistical analysis should handle problematic data gracefully
    let mean = series.mean();
    assert!(mean.is_some());

    // Should calculate mean from valid finite values only
    // Valid values: 23.5, 23.7, 24.1, 0.0, 156.8, 24.3, 24.2, 23.9, 23.6
    let valid_values = vec![23.5, 23.7, 24.1, 0.0, 156.8, 24.3, 24.2, 23.9, 23.6];
    let expected_mean = valid_values.iter().sum::<f64>() / valid_values.len() as f64;
    assert!((mean.unwrap() - expected_mean).abs() < 0.01);

    // Time range should work despite invalid timestamps
    let time_range = series.time_range();
    assert_eq!(time_range, Some((-1, 1640995680)));

    // Series operations should work
    assert_eq!(series.len(), 11);
    assert!(!series.is_empty());
    assert!(series.get(0).is_some());
    assert!(series.get(20).is_none());
}

#[test]
fn test_empty_and_edge_cases() {
    // Test empty series
    let empty_series = Series::new(vec![]);
    assert!(empty_series.is_empty());
    assert_eq!(empty_series.len(), 0);
    assert!(empty_series.validate().is_empty());
    assert_eq!(empty_series.mean(), None);
    assert_eq!(empty_series.time_range(), None);
    assert!(empty_series.get(0).is_none());

    // Test series with only invalid data
    let invalid_series = Series::new(vec![
        Point::new(-1, f64::NAN),
        Point::new(-2, f64::INFINITY),
        Point::new(-3, f64::NEG_INFINITY),
    ]);

    let warnings = invalid_series.validate();
    assert!(warnings.len() >= 6); // 3 negative timestamps + 3 non-finite values

    assert_eq!(invalid_series.mean(), None); // No finite values
    assert_eq!(invalid_series.time_range(), Some((-3, -1)));

    // Test series with single point
    let single_series = Series::new(vec![Point::new(1000, 42.0)]);
    assert_eq!(single_series.len(), 1);
    assert!(single_series.validate().is_empty());
    assert_eq!(single_series.mean(), Some(42.0));
    assert_eq!(single_series.time_range(), Some((1000, 1000)));
}

#[test]
fn test_backward_compatibility() {
    // Test that existing APIs continue to work

    // Original Point constructor should accept anything
    let point1 = Point::new(-1, f64::NAN);
    assert_eq!(point1.timestamp, -1);
    assert!(point1.value.is_nan());

    // Original Series constructor should accept anything
    let series = Series::new(vec![
        Point::new(1, 1.0),
        Point::new(-1, f64::NAN),
        Point::new(2, f64::INFINITY),
    ]);
    assert_eq!(series.len(), 3);

    // from_vec should still work
    let vec_series = Series::from_vec(vec![1.0, 2.0, 3.0], Some(1000), Some(1));
    assert_eq!(vec_series.len(), 3);
    assert_eq!(vec_series[0].timestamp, 1000);
    assert_eq!(vec_series[1].timestamp, 1001);

    // Indexing should still work
    assert_eq!(series[0].timestamp, 1);
    assert_eq!(series[0].value, 1.0);

    // Slice indexing should still work
    let slice = &series[0..2];
    assert_eq!(slice.len(), 2);

    // All new methods should be optional to use
    assert!(series.get(0).is_some());
    assert!(!series.is_empty());
    assert!(series.mean().is_some());
    assert!(series.time_range().is_some());
    assert!(!series.validate().is_empty());
}

#[test]
fn test_performance_with_large_dataset() {
    // Test with reasonably large dataset (10,000 points)
    let large_dataset: Vec<Point> = (0..10_000)
        .map(|i| {
            let timestamp = 1640995200 + i * 60; // One point per minute
            let value = 20.0 + (i as f64 * 0.1) % 10.0; // Varying values
            Point::new(timestamp, value)
        })
        .collect();

    let start = std::time::Instant::now();
    let series = Series::new(large_dataset);
    let construction_time = start.elapsed();

    // Construction should be fast
    assert!(
        construction_time.as_millis() < 100,
        "Construction took too long: {:?}",
        construction_time
    );

    // Validation should be reasonably fast
    let start = std::time::Instant::now();
    let warnings = series.validate();
    let validation_time = start.elapsed();

    assert!(warnings.is_empty()); // Should be no warnings for this clean dataset
    assert!(
        validation_time.as_millis() < 100,
        "Validation took too long: {:?}",
        validation_time
    );

    // Statistical operations should be fast
    let start = std::time::Instant::now();
    let mean = series.mean();
    let stats_time = start.elapsed();

    assert!(mean.is_some());
    assert!(
        stats_time.as_millis() < 50,
        "Stats calculation took too long: {:?}",
        stats_time
    );

    // Time range should be fast
    let start = std::time::Instant::now();
    let time_range = series.time_range();
    let range_time = start.elapsed();

    assert_eq!(time_range, Some((1640995200, 1640995200 + 9999 * 60)));
    assert!(
        range_time.as_millis() < 50,
        "Time range took too long: {:?}",
        range_time
    );

    // CSV export should be reasonably fast
    let temp_file = NamedTempFile::new().unwrap();
    let start = std::time::Instant::now();
    series.to_csv(temp_file.path()).unwrap();
    let export_time = start.elapsed();

    assert!(
        export_time.as_millis() < 500,
        "CSV export took too long: {:?}",
        export_time
    );

    // CSV import should be reasonably fast
    let start = std::time::Instant::now();
    let imported = Series::from_csv(temp_file.path()).unwrap();
    let import_time = start.elapsed();

    assert_eq!(imported.len(), series.len());
    assert!(
        import_time.as_millis() < 1000,
        "CSV import took too long: {:?}",
        import_time
    );
}

#[test]
fn test_mixed_data_quality_scenarios() {
    // Test various combinations of data quality issues
    let mixed_data = vec![
        Point::new(1000, 42.0),              // Valid
        Point::new(1001, 43.0),              // Valid
        Point::new(-1, 44.0),                // Negative timestamp
        Point::new(1002, f64::NAN),          // NaN
        Point::new(-2, f64::INFINITY),       // Negative timestamp + infinity
        Point::new(1003, 45.0),              // Valid
        Point::new(1000, 46.0),              // Duplicate timestamp
        Point::new(1004, f64::NEG_INFINITY), // Negative infinity
        Point::new(-3, f64::NAN),            // Negative timestamp + NaN
        Point::new(1005, 47.0),              // Valid
    ];

    let series = Series::new(mixed_data);

    // Comprehensive validation
    let warnings = series.validate();
    let validation_summary = series.validation_summary();

    // Should detect all issues
    assert!(warnings.len() >= 7); // Multiple issues

    // Validation summary should properly count each type
    assert_eq!(validation_summary.get(&PointType::Valid), Some(&5));
    assert_eq!(
        validation_summary.get(&PointType::NegativeTimestamp),
        Some(&3)
    );
    assert_eq!(validation_summary.get(&PointType::NanValue), Some(&2));
    assert_eq!(validation_summary.get(&PointType::InfinityValue), Some(&2));

    // Statistical operations should handle mixed data gracefully
    let mean = series.mean();
    assert!(mean.is_some());

    // Should only include finite values: 42.0, 43.0, 44.0, 45.0, 46.0, 47.0
    let expected_mean = (42.0 + 43.0 + 44.0 + 45.0 + 46.0 + 47.0) / 6.0;
    assert!((mean.unwrap() - expected_mean).abs() < 0.01);

    // Time range should include all timestamps (even negative ones)
    let time_range = series.time_range();
    assert_eq!(time_range, Some((-3, 1005)));

    // Series should remain functional
    assert_eq!(series.len(), 10);
    assert!(!series.is_empty());

    // Push and get operations should work
    let mut mutable_series = series.clone();
    mutable_series.push(Point::new(2000, 50.0));
    assert_eq!(mutable_series.len(), 11);
    assert_eq!(mutable_series.get(10).unwrap().value, 50.0);
}

#[test]
fn test_csv_error_handling() {
    // Test various CSV error scenarios

    // Test malformed CSV
    let mut temp_file = NamedTempFile::new().unwrap();
    writeln!(temp_file, "not_a_timestamp,not_a_value").unwrap();
    temp_file.flush().unwrap();

    let result = Series::from_csv(temp_file.path());
    assert!(result.is_err());
    assert!(matches!(result.unwrap_err(), Error::Parse(_)));

    // Test CSV with insufficient columns
    let mut temp_file = NamedTempFile::new().unwrap();
    writeln!(temp_file, "1000").unwrap(); // Only one column
    temp_file.flush().unwrap();

    let result = Series::from_csv(temp_file.path());
    assert!(result.is_err());

    // Test non-existent file
    let result = Series::from_csv("/path/that/does/not/exist.csv");
    assert!(result.is_err());
    assert!(matches!(result.unwrap_err(), Error::Io(_)));
}

#[test]
fn test_validation_aggregation_efficiency() {
    // Test that validation_summary is efficient and matches individual validations
    let test_data = vec![
        Point::new(1000, 42.0),              // Valid
        Point::new(-100, 1.0),               // NegativeTimestamp
        Point::new(2000, f64::NAN),          // NanValue
        Point::new(3000, f64::INFINITY),     // InfinityValue
        Point::new(-200, f64::NEG_INFINITY), // Mixed: NegativeTimestamp + InfinityValue
        Point::new(4000, 123.45),            // Valid
    ];

    let series = Series::new(test_data);

    // Get validation summary
    let validation_summary = series.validation_summary();

    // Manually aggregate individual point validations
    let mut manual_counts: HashMap<PointType, u32> = HashMap::new();
    for point in &series.points {
        let validation = point.validation();
        for (point_type, count) in validation {
            *manual_counts.entry(point_type).or_insert(0) += count;
        }
    }

    // Should match exactly
    assert_eq!(validation_summary, manual_counts);
    assert_eq!(validation_summary.get(&PointType::Valid), Some(&2));
    assert_eq!(
        validation_summary.get(&PointType::NegativeTimestamp),
        Some(&2)
    );
    assert_eq!(validation_summary.get(&PointType::NanValue), Some(&1));
    assert_eq!(validation_summary.get(&PointType::InfinityValue), Some(&2));
}
