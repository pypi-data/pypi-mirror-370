//! Valdo Anomaly Detection Demo
//!
//! This example demonstrates how to use the Valdo algorithm for real-time
//! time series anomaly detection. It shows:
//!
//! 1. Training Valdo on a dataset of normal behavior
//! 2. Processing new data points in real-time
//! 3. Detecting anomalies as they occur
//!
//! Run with: `cargo run --example valdo_demo`

use valdo::{AnomalyStatus, Detector, Series};

fn run_valdo() -> Result<(), Box<dyn std::error::Error>> {
    let start_time = std::time::Instant::now();

    let mut detector = Detector::builder().window_size(10).build()?;
    let training_data: Vec<f64> = (0..1000000).map(|_| rand::random::<f64>()).collect();

    // Use series with stable values to train on normal behavior
    // println!("training_data: {:?}", training_data);
    let series = Series::from_vec(training_data, None, None);

    println!("🚀 Fitting Valdo with cascaded smoothing...");
    detector.train(&series)?;

    println!("✅ Valdo fitted successfully!");

    let new_data_points = vec![
        (1000, 1.0),
        (1001, 10.0), // This should definitely be an anomaly
    ];

    for (timestamp, value) in new_data_points {
        match detector.detect(timestamp, value)? {
            AnomalyStatus::Normal => println!("   Point {}: {} → Normal", timestamp, value),
            AnomalyStatus::Anomaly => {
                println!("   Point {}: {} → 🚨 ANOMALY DETECTED!", timestamp, value)
            }
        }
    }

    println!("Time taken: {:?}", start_time.elapsed());

    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    run_valdo()
}
