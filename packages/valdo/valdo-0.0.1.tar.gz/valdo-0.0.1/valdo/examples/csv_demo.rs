//! CSV Time Series Anomaly Detection with Train/Test Split
//!
//! This example demonstrates how to:
//! 1. Read time series data from a CSV file
//! 2. Split the data into 80% training set and 20% test set
//! 3. Train Valdo on the training data
//! 4. Detect anomalies in the test data
//!
//! CSV Format Expected:
//! - Two columns: timestamp, value
//! - First row can be headers (will be skipped)
//! - Example CSV content:
//!   timestamp,value
//!   1000,1.2
//!   1001,1.5
//!   1002,1.1
//!   ...
//!
//! Run with: `cargo run --example csv_train_test_split -- path/to/your/data.csv`

use csv::ReaderBuilder;
use serde::Deserialize;
use std::env;
use std::error::Error;
use std::fs::File;
use std::io::Write;
use valdo::{AnomalyStatus, Detector, Point, Series};

#[derive(Debug, Deserialize)]
struct DataRow {
    timestamp: i64,
    value: f64,
}

/// Create a sample CSV file for demonstration
fn create_sample_csv(filename: &str) -> Result<(), Box<dyn Error>> {
    let mut file = File::create(filename)?;
    writeln!(file, "timestamp,value")?;

    // Generate sample time series data with some normal patterns and occasional anomalies
    let mut timestamp = 1000i64;
    for i in 0..1000 {
        let base_value = 10.0 + 5.0 * (i as f64 * 0.01).sin(); // Sinusoidal pattern
        let noise = (rand::random::<f64>() - 0.5) * 2.0; // Small random noise

        let value = if i == 800 || i == 850 || i == 900 {
            // Insert some anomalies near the end
            base_value + 20.0 + noise
        } else {
            base_value + noise
        };

        writeln!(file, "{},{:.2}", timestamp, value)?;
        timestamp += 1;
    }

    println!("📄 Created sample CSV file: {}", filename);
    Ok(())
}

/// Read time series data from CSV file
fn read_csv_data(filename: &str) -> Result<Vec<Point>, Box<dyn Error>> {
    let file = File::open(filename)?;
    let mut reader = ReaderBuilder::new().has_headers(true).from_reader(file);

    let mut data_points = Vec::new();

    for result in reader.deserialize() {
        let row: DataRow = result?;
        data_points.push(Point::new(row.timestamp, row.value));
    }

    println!(
        "📊 Read {} data points from {}",
        data_points.len(),
        filename
    );
    Ok(data_points)
}

/// Split data into training and test sets
fn train_test_split(data: Vec<Point>, train_ratio: f64) -> (Vec<Point>, Vec<Point>) {
    let split_index = (data.len() as f64 * train_ratio) as usize;
    let (train_data, test_data) = data.split_at(split_index);

    println!(
        "📈 Training set: {} points ({:.1}%)",
        train_data.len(),
        train_data.len() as f64 / data.len() as f64 * 100.0
    );
    println!(
        "🧪 Test set: {} points ({:.1}%)",
        test_data.len(),
        test_data.len() as f64 / data.len() as f64 * 100.0
    );

    (train_data.to_vec(), test_data.to_vec())
}

fn run_csv_anomaly_detection(csv_filename: &str) -> Result<(), Box<dyn Error>> {
    println!("🚀 Starting CSV Time Series Anomaly Detection Demo");
    println!("================================================");

    // Read data from CSV
    let data_points = read_csv_data(csv_filename)?;

    if data_points.len() < 100 {
        return Err("Need at least 100 data points for meaningful analysis".into());
    }

    // Split into 80% training, 20% test
    let (train_data, test_data) = train_test_split(data_points, 0.8);
    let mut detector = Detector::default();

    // Train on training data
    println!("\n🎯 Training Valdo on training set...");
    let training_series = Series::new(train_data);
    detector.train(&training_series)?;
    println!("✅ Training completed!");

    // Test on test data
    println!("\n🔍 Processing test set for anomaly detection:");
    println!(
        "   {:<12} {:<10} {:<15} {:<10}",
        "Timestamp", "Value", "Status", "Type"
    );
    println!("   {}", "-".repeat(50));

    let mut normal_count = 0;
    let mut anomaly_count = 0;

    for point in &test_data {
        let status = detector.detect(point.timestamp, point.value)?;

        let (status_str, type_str) = match status {
            AnomalyStatus::Normal => {
                normal_count += 1;
                ("Normal", "🟢")
            }
            AnomalyStatus::Anomaly => {
                anomaly_count += 1;
                ("Anomaly", "🔴")
            }
        };

        println!(
            "   {:<12} {:<10.2} {:<15} {:<10}",
            point.timestamp, point.value, status_str, type_str
        );
    }

    // Summary statistics
    println!("\n📊 Detection Summary:");
    println!(
        "   Normal points: {} ({:.1}%)",
        normal_count,
        normal_count as f64 / test_data.len() as f64 * 100.0
    );
    println!(
        "   Anomaly points: {} ({:.1}%)",
        anomaly_count,
        anomaly_count as f64 / test_data.len() as f64 * 100.0
    );

    if anomaly_count > 0 {
        println!("\n🚨 {} anomalies detected in the test set!", anomaly_count);
    } else {
        println!("\n✅ No anomalies detected in the test set.");
    }

    Ok(())
}

fn main() -> Result<(), Box<dyn Error>> {
    let args: Vec<String> = env::args().collect();

    let csv_filename = if args.len() > 1 {
        // Use provided CSV file
        args[1].clone()
    } else {
        // Create and use sample CSV file
        let sample_filename = "sample_timeseries.csv";
        println!("No CSV file provided. Creating sample data...");
        create_sample_csv(sample_filename)?;
        sample_filename.to_string()
    };

    match run_csv_anomaly_detection(&csv_filename) {
        Ok(()) => {
            println!("\n✨ Analysis completed successfully!");
            if csv_filename == "sample_timeseries.csv" {
                println!("💡 You can also run this example with your own CSV file:");
                println!("   cargo run --example csv_train_test_split -- your_data.csv");
            }
        }
        Err(e) => {
            eprintln!("❌ Error: {}", e);
            std::process::exit(1);
        }
    }

    Ok(())
}
