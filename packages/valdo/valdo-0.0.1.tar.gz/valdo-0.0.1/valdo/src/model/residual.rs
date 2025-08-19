/// Residual predictor: takes a window of values and produces a single predicted value
pub trait ResidualPredictor {
    /// Apply prediction to produce a predicted value from a window of values
    fn predict(&self, window: &[f64]) -> f64;
}

/// EWMA (Exponentially Weighted Moving Average) residual predictor
#[derive(Debug)]
pub struct EWMA {
    pub alpha: f64,
}

impl EWMA {
    pub fn new(alpha: f64) -> Self {
        Self { alpha }
    }
}

impl ResidualPredictor for EWMA {
    fn predict(&self, window: &[f64]) -> f64 {
        if window.is_empty() {
            return f64::NAN;
        }

        let mut numerator = 0.0;
        let mut denominator = 0.0;

        for (j, &value) in window.iter().rev().enumerate() {
            let weight = (1.0 - self.alpha).powi(j as i32);
            numerator += weight * value;
            denominator += weight;
        }

        numerator / denominator
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ewma_predictor() {
        let ewma = EWMA::new(0.0);

        // Test with window [1.0, 2.0, 3.0]
        let window = vec![1.0, 2.0, 3.0];
        let predicted = ewma.predict(&window);
        assert_eq!(predicted, 2.0); // Mean of [1, 2, 3] with alpha=0

        // Test with empty window
        assert!(ewma.predict(&[]).is_nan());
    }
}
