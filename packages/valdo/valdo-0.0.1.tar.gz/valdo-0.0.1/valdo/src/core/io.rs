use std::fs::File;
use std::io::{BufRead, BufReader, Write};
use std::path::Path;

use crate::{Error, Point, Series};

impl Series {
    /// Import a Series from a CSV file
    ///
    /// The CSV file should have two columns: timestamp and value.
    /// If a header row is present (contains "timestamp" text), it will be automatically skipped.
    ///
    /// # Arguments
    ///
    /// * `path` - Path to the CSV file
    ///
    /// # Examples
    ///
    /// ```no_run
    /// use valdo::Series;
    ///
    /// let series = Series::from_csv("data.csv")?;
    /// println!("Loaded {} points", series.len());
    /// # Ok::<(), Box<dyn std::error::Error>>(())
    /// ```
    ///
    /// # Errors
    ///
    /// Returns `Error` if:
    /// - File cannot be opened (IO error)
    /// - File contains invalid timestamp or value data (Parse error)
    /// - File format is incorrect
    pub fn from_csv<P: AsRef<Path>>(path: P) -> Result<Series, Error> {
        let file = File::open(path.as_ref()).map_err(Error::from)?;
        let reader = BufReader::new(file);
        let mut points = Vec::new();

        for (line_num, line) in reader.lines().enumerate() {
            let line = line.map_err(Error::from)?;

            // Skip header if present (check if first column is exactly "timestamp")
            if line_num == 0 {
                let parts: Vec<&str> = line.split(',').collect();
                if !parts.is_empty() && parts[0].trim().to_lowercase() == "timestamp" {
                    continue;
                }
            }

            // Skip empty lines
            if line.trim().is_empty() {
                continue;
            }

            let parts: Vec<&str> = line.split(',').collect();
            if parts.len() < 2 {
                return Err(Error::invalid_format(&format!(
                    "Line {} has insufficient columns (expected at least 2, got {})",
                    line_num + 1,
                    parts.len()
                )));
            }

            let timestamp_str = parts[0].trim();
            let value_str = parts[1].trim();

            let timestamp = timestamp_str
                .parse::<i64>()
                .map_err(|_| Error::invalid_timestamp(timestamp_str))?;

            let value = value_str
                .parse::<f64>()
                .map_err(|_| Error::invalid_value(value_str))?;

            points.push(Point::new(timestamp, value));
        }

        Ok(Series::new(points))
    }

    /// Export the Series to a CSV file
    ///
    /// Creates a CSV file with a header row and two columns: timestamp and value.
    ///
    /// # Arguments
    ///
    /// * `path` - Path where the CSV file should be created
    ///
    /// # Examples
    ///
    /// ```no_run
    /// use valdo::{Point, Series};
    ///
    /// let series = Series::new(vec![
    ///     Point::new(1000, 42.0),
    ///     Point::new(2000, 84.0),
    /// ]);
    ///
    /// series.to_csv("output.csv")?;
    /// # Ok::<(), Box<dyn std::error::Error>>(())
    /// ```
    ///
    /// # Errors
    ///
    /// Returns `Error` if file cannot be created or written to (IO error)
    pub fn to_csv<P: AsRef<Path>>(&self, path: P) -> Result<(), Error> {
        let mut file = File::create(path.as_ref()).map_err(Error::from)?;

        // Write header
        writeln!(file, "timestamp,value").map_err(Error::from)?;

        // Write data points
        for point in &self.points {
            writeln!(file, "{},{}", point.timestamp, point.value).map_err(Error::from)?;
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    #[test]
    fn test_csv_roundtrip() {
        let original_series = Series::new(vec![
            Point::new(1000, 42.0),
            Point::new(2000, 84.0),
            Point::new(3000, 126.0),
        ]);

        // Create temporary file
        let temp_file = NamedTempFile::new().unwrap();
        let temp_path = temp_file.path();

        // Export to CSV
        original_series.to_csv(temp_path).unwrap();

        // Import from CSV
        let imported_series = Series::from_csv(temp_path).unwrap();

        // Verify data matches
        assert_eq!(imported_series.len(), original_series.len());
        for (original, imported) in original_series
            .points
            .iter()
            .zip(imported_series.points.iter())
        {
            assert_eq!(original.timestamp, imported.timestamp);
            assert_eq!(original.value, imported.value);
        }
    }

    #[test]
    fn test_csv_with_header() {
        let mut temp_file = NamedTempFile::new().unwrap();

        // Write CSV with header
        writeln!(temp_file, "timestamp,value").unwrap();
        writeln!(temp_file, "1000,42.0").unwrap();
        writeln!(temp_file, "2000,84.0").unwrap();
        temp_file.flush().unwrap();

        let series = Series::from_csv(temp_file.path()).unwrap();

        assert_eq!(series.len(), 2);
        assert_eq!(series[0].timestamp, 1000);
        assert_eq!(series[0].value, 42.0);
        assert_eq!(series[1].timestamp, 2000);
        assert_eq!(series[1].value, 84.0);
    }

    #[test]
    fn test_csv_without_header() {
        let mut temp_file = NamedTempFile::new().unwrap();

        // Write CSV without header
        writeln!(temp_file, "1000,42.0").unwrap();
        writeln!(temp_file, "2000,84.0").unwrap();
        temp_file.flush().unwrap();

        let series = Series::from_csv(temp_file.path()).unwrap();

        assert_eq!(series.len(), 2);
        assert_eq!(series[0].timestamp, 1000);
        assert_eq!(series[0].value, 42.0);
        assert_eq!(series[1].timestamp, 2000);
        assert_eq!(series[1].value, 84.0);
    }

    #[test]
    fn test_csv_with_special_values() {
        let original_series = Series::new(vec![
            Point::new(1000, 42.0),
            Point::new(-1000, -42.0),            // Negative values
            Point::new(2000, 0.0),               // Zero
            Point::new(3000, f64::NAN),          // NaN
            Point::new(4000, f64::INFINITY),     // Infinity
            Point::new(5000, f64::NEG_INFINITY), // Negative infinity
        ]);

        let temp_file = NamedTempFile::new().unwrap();
        let temp_path = temp_file.path();

        // Export to CSV
        original_series.to_csv(temp_path).unwrap();

        // Import from CSV
        let imported_series = Series::from_csv(temp_path).unwrap();

        // Verify data matches
        assert_eq!(imported_series.len(), original_series.len());
        for (original, imported) in original_series
            .points
            .iter()
            .zip(imported_series.points.iter())
        {
            assert_eq!(original.timestamp, imported.timestamp);
            if original.value.is_nan() {
                assert!(imported.value.is_nan());
            } else {
                assert_eq!(original.value, imported.value);
            }
        }
    }

    #[test]
    fn test_csv_with_empty_lines() {
        let mut temp_file = NamedTempFile::new().unwrap();

        // Write CSV with empty lines
        writeln!(temp_file, "timestamp,value").unwrap();
        writeln!(temp_file, "1000,42.0").unwrap();
        writeln!(temp_file, "").unwrap(); // Empty line
        writeln!(temp_file, "2000,84.0").unwrap();
        writeln!(temp_file, "   ").unwrap(); // Whitespace only
        writeln!(temp_file, "3000,126.0").unwrap();
        temp_file.flush().unwrap();

        let series = Series::from_csv(temp_file.path()).unwrap();

        assert_eq!(series.len(), 3);
        assert_eq!(series[0].timestamp, 1000);
        assert_eq!(series[1].timestamp, 2000);
        assert_eq!(series[2].timestamp, 3000);
    }

    #[test]
    fn test_csv_parse_errors() {
        // Test invalid timestamp
        let mut temp_file = NamedTempFile::new().unwrap();
        writeln!(temp_file, "invalid_timestamp,42.0").unwrap();
        temp_file.flush().unwrap();

        let result = Series::from_csv(temp_file.path());
        assert!(result.is_err());
        assert!(matches!(result.unwrap_err(), Error::Parse(_)));

        // Test invalid value
        let mut temp_file = NamedTempFile::new().unwrap();
        writeln!(temp_file, "1000,invalid_value").unwrap();
        temp_file.flush().unwrap();

        let result = Series::from_csv(temp_file.path());
        assert!(result.is_err());
        assert!(matches!(result.unwrap_err(), Error::Parse(_)));

        // Test insufficient columns
        let mut temp_file = NamedTempFile::new().unwrap();
        writeln!(temp_file, "1000").unwrap(); // Only one column
        temp_file.flush().unwrap();

        let result = Series::from_csv(temp_file.path());
        assert!(result.is_err());
        assert!(matches!(result.unwrap_err(), Error::Parse(_)));
    }

    #[test]
    fn test_csv_io_errors() {
        // Test reading from non-existent file
        let result = Series::from_csv("/path/that/does/not/exist.csv");
        assert!(result.is_err());
        assert!(matches!(result.unwrap_err(), Error::Io(_)));

        // Test writing to invalid path (directory that doesn't exist)
        let series = Series::new(vec![Point::new(1000, 42.0)]);
        let result = series.to_csv("/path/that/does/not/exist/output.csv");
        assert!(result.is_err());
        assert!(matches!(result.unwrap_err(), Error::Io(_)));
    }

    #[test]
    fn test_empty_series_export() {
        let empty_series = Series::new(vec![]);

        let temp_file = NamedTempFile::new().unwrap();
        let temp_path = temp_file.path();

        // Should successfully export empty series
        empty_series.to_csv(temp_path).unwrap();

        // Should import as empty series
        let imported = Series::from_csv(temp_path).unwrap();
        assert!(imported.is_empty());
    }
}
