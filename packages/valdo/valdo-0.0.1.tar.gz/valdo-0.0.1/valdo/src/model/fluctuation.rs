/// Fluctuation estimator: takes a window of residuals and produces a single fluctuation estimate  
pub trait FluctuationEstimator {
    /// Apply estimation to produce a fluctuation value from a window of residuals
    fn estimate(&self, window: &[f64]) -> f64;
}

/// Standard deviation fluctuation estimator
#[derive(Debug)]
pub struct StdDevDiff {}

impl StdDevDiff {
    pub fn new() -> Self {
        Self {}
    }
}

impl Default for StdDevDiff {
    fn default() -> Self {
        Self::new()
    }
}

impl FluctuationEstimator for StdDevDiff {
    fn estimate(&self, window: &[f64]) -> f64 {
        if window.len() < 2 {
            return 0.0;
        }

        let mean = window.iter().sum::<f64>() / window.len() as f64;
        let variance = window
            .iter()
            .map(|&value| (value - mean).powi(2))
            .sum::<f64>()
            / window.len() as f64;
        variance.sqrt()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_std_dev_estimator() {
        let estimator = StdDevDiff::new();

        // Test with residuals [1.0, 1.0, 10.0]
        let residuals = vec![1.0, 1.0, 10.0];
        let fluctuation = estimator.estimate(&residuals);
        // std([1.0, 1.0, 10.0]) ≈ 4.242
        assert!((fluctuation - 4.242640687119285).abs() < 1e-10);

        // Test with insufficient data
        let small_window = vec![1.0];
        assert_eq!(estimator.estimate(&small_window), 0.0);
    }
}
