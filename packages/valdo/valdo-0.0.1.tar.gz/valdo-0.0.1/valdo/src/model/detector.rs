use crate::model::fluctuation::{FluctuationEstimator, StdDevDiff};
use crate::model::residual::{EWMA, ResidualPredictor};
use crate::error::Error;
use crate::{Point, Series};
use libspot_rs::{SpotConfig, SpotDetector};
use std::collections::VecDeque;


pub enum AnomalyStatus {
    Normal,
    Anomaly,
}

impl From<libspot_rs::SpotStatus> for AnomalyStatus {
    fn from(status: libspot_rs::SpotStatus) -> Self {
        match status {
            libspot_rs::SpotStatus::Normal => AnomalyStatus::Normal,
            libspot_rs::SpotStatus::Excess => AnomalyStatus::Normal,
            libspot_rs::SpotStatus::Anomaly => AnomalyStatus::Anomaly,
        }
    }
}

/// Builder for creating a Detector with a fluent API
pub struct DetectorBuilder {
    s: Option<u64>,
    q: Option<f64>,
    level: Option<f64>,
    max_excess: Option<usize>,
    residual_predictor: Option<EWMA>,
    fluctuation_estimator: Option<StdDevDiff>,
}

impl DetectorBuilder {
    /// Create a new DetectorBuilder
    pub fn new() -> Self {
        Self {
            s: None,
            q: None,
            level: None,
            max_excess: None,
            residual_predictor: None,
            fluctuation_estimator: None,
        }
    }

    /// Set the smooth window size (required)
    pub fn window_size(mut self, s: u64) -> Self {
        self.s = Some(s);
        self
    }

    /// Set the quantile parameter for the SPOT detector
    pub fn quantile(mut self, q: f64) -> Self {
        self.q = Some(q);
        self
    }

    /// Set the level for the SPOT detector
    pub fn level(mut self, level: f64) -> Self {
        self.level = Some(level);
        self
    }

    /// Set the maximum number of excesses for the SPOT detector
    pub fn max_excess(mut self, max_excess: usize) -> Self {
        self.max_excess = Some(max_excess);
        self
    }

    /// Set a custom residual predictor
    pub fn residual_predictor(mut self, predictor: EWMA) -> Self {
        self.residual_predictor = Some(predictor);
        self
    }

    /// Set a custom fluctuation estimator
    pub fn fluctuation_estimator(mut self, estimator: StdDevDiff) -> Self {
        self.fluctuation_estimator = Some(estimator);
        self
    }

    /// Build the Detector with the configured parameters
    pub fn build(self) -> Result<Detector, Error> {
        let s = self.s.ok_or_else(|| Error::missing_parameter("window size (s)"))?;
        let q = self.q.unwrap_or(0.0001);
        let level = self.level.unwrap_or(0.998);
        let max_excess = self.max_excess.unwrap_or(200);
        let residual_predictor = self.residual_predictor.unwrap_or_else(|| EWMA::new(0.0));
        let fluctuation_estimator = self.fluctuation_estimator.unwrap_or_else(|| StdDevDiff::new());

        let spot_config = SpotConfig {
            q,
            level,
            max_excess,
            low_tail: false,
            ..SpotConfig::default()
        };

        let spot = SpotDetector::new(spot_config)?;

        Ok(Detector {
            s,
            xs_window: VecDeque::with_capacity(s as usize),
            residuals_window: VecDeque::with_capacity(s as usize),
            residual_predictor,
            fluctuation_estimator,
            spot,
        })
    }
}

impl Default for DetectorBuilder {
    fn default() -> Self {
        Self::new()
    }
}

/// Valdo Detector
#[derive(Debug)]
pub struct Detector {
    // smooth window size
    s: u64,

    // Sliding window states for real-time processing
    /// Window of latest s original points for calculating residuals
    xs_window: VecDeque<Point>,
    /// Window of latest s residual values for calculating fluctuations
    residuals_window: VecDeque<f64>,

    // EWMA predictor for calculating residuals
    residual_predictor: EWMA,
    // StdDev estimator for calculating fluctuations
    fluctuation_estimator: StdDevDiff,
    // spot detector
    spot: SpotDetector,
}


impl Detector {
    /// Create a new DetectorBuilder for fluent configuration
    pub fn builder() -> DetectorBuilder {
        DetectorBuilder::new()
    }

    /// Create a new Detector with the specified parameters (legacy method)
    pub fn new(
        s: u64,
        q: Option<f64>,
        level: Option<f64>,
        max_excess: Option<usize>,
        residual_predictor: Option<EWMA>,
        fluctuation_estimator: Option<StdDevDiff>,
    ) -> Result<Detector, Error> {
        let mut builder = Self::builder().window_size(s);
        
        if let Some(q) = q {
            builder = builder.quantile(q);
        }
        if let Some(level) = level {
            builder = builder.level(level);
        }
        if let Some(max_excess) = max_excess {
            builder = builder.max_excess(max_excess);
        }
        if let Some(predictor) = residual_predictor {
            builder = builder.residual_predictor(predictor);
        }
        if let Some(estimator) = fluctuation_estimator {
            builder = builder.fluctuation_estimator(estimator);
        }
        
        builder.build()
    }
}

impl Default for Detector {
    fn default() -> Self {
        Self::builder()
            .window_size(10)
            .quantile(0.0001)
            .level(0.998)
            .max_excess(200)
            .residual_predictor(EWMA::new(0.0))
            .fluctuation_estimator(StdDevDiff::new())
            .build()
            .unwrap()
    }
}

impl Detector {
    /// Fit the Valdo model to the series.
    pub fn train(&mut self, series: &Series) -> Result<(), Error> {
        let window_size = self.s as usize;
        let mut residuals = Vec::new();

        // Calculate residuals using sliding windows
        for window in series.points.windows(window_size + 1) {
            // Get window of previous values for prediction
            let prediction_window: Vec<f64> =
                window[..window_size].iter().map(|p| p.value).collect();
            let predicted_value = self.residual_predictor.predict(&prediction_window);

            match predicted_value.is_nan() {
                true => {
                    println!("Warning: predicted value is nan, skip this point");
                    continue;
                }
                false => {
                    let residual_value = window[window_size].value - predicted_value;
                    residuals.push(residual_value);
                }
            }
        }

        // Calculate fluctuations and deltas using sliding windows on residuals
        let mut fluctuation_delta_series = Vec::new();
        let mut previous_fluctuation: Option<f64> = None;

        for window in residuals.windows(window_size + 1) {
            let fluctuation_value = self.fluctuation_estimator.estimate(&window[..window_size]);

            match fluctuation_value.is_nan() {
                true => {
                    println!("Warning: fluctuation value is nan, skip this point");
                    continue;
                }
                false => {
                    if let Some(prev_fluct) = previous_fluctuation {
                        let delta = (fluctuation_value - prev_fluct).max(0.0);
                        fluctuation_delta_series.push(delta);
                    }
                    previous_fluctuation = Some(fluctuation_value);
                }
            }
        }
        // Fit spot detector with fluctuation values
        if !fluctuation_delta_series.is_empty() {
            self.spot.fit(&fluctuation_delta_series)?;
        }

        // Initialize sliding windows with the last s points
        let window_size = self.s as usize;
        let series_len = series.len();

        if series_len >= window_size {
            // Initialize xs_window with last s points
            self.xs_window.clear();
            for i in (series_len - window_size)..series_len {
                self.xs_window.push_back(series[i].clone());
            }

            // Initialize residuals_window with last s residual values (for StdDevDiff)
            self.residuals_window.clear();
            let residuals_to_take = std::cmp::min(self.s as usize, residuals.len());
            if residuals_to_take > 0 {
                let start_idx = residuals.len() - residuals_to_take;
                for i in start_idx..residuals.len() {
                    if !residuals[i].is_nan() {
                        self.residuals_window.push_back(residuals[i]);
                    }
                }
            }
        }

        Ok(())
    }

    /// Process a new data point in real-time
    pub fn detect(&mut self, timestamp: i64, value: f64) -> Result<AnomalyStatus, Error> {
        let new_point = Point::new(timestamp, value);

        // Step 1: Calculate residual
        let predicted_value = self.residual_predictor.predict(&self.get_xs_window_values());
        let residual = value - predicted_value;

        // Step2: Calculate fluctuation or two residual windows
        let mut new_residual_window = self.residuals_window.clone();
        new_residual_window.push_back(residual);
        new_residual_window.pop_front();

        // residual window original fluctuation
        let original_fluctuation = self
            .fluctuation_estimator
            .estimate(&self.get_residuals_window_values(&self.residuals_window));
        let new_fluctuation = self
            .fluctuation_estimator
            .estimate(&self.get_residuals_window_values(&new_residual_window));
        let fluctuation_delta = new_fluctuation - original_fluctuation;

        // Step 3: Run spot detection
        let spot_result: AnomalyStatus = if !fluctuation_delta.is_nan() {
            self.spot.step(fluctuation_delta)?.into()
        } else {
            AnomalyStatus::Normal // Not enough data for detection yet
        };

        // Step 4: Update window states
        // Update xs_window (maintain size s)
        match spot_result {
            AnomalyStatus::Normal => {
                self.xs_window.push_back(new_point);
                self.xs_window.pop_front();
                self.residuals_window = new_residual_window;
            }
            _ => {}
        }

        Ok(spot_result)
    }

    fn get_xs_window_values(&self) -> Vec<f64> {
        self.xs_window.iter().map(|p| p.value).collect()
    }

    fn get_residuals_window_values(&self, residual_window: &VecDeque<f64>) -> Vec<f64> {
        residual_window.iter().copied().collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_detector_init() {
        let detector = Detector::new(10, Some(0.0001), Some(0.998), Some(200), Some(EWMA::new(0.0)), Some(StdDevDiff::new())).unwrap();
        assert_eq!(detector.s, 10);

        assert_eq!(detector.spot.config().unwrap().level, 0.998);
        assert_eq!(detector.spot.config().unwrap().max_excess, 200);

        assert!(detector.xs_window.is_empty());
        assert!(detector.residuals_window.is_empty());
    }

    #[test]
    fn test_detector_builder_basic() {
        let detector = Detector::builder()
            .window_size(10)
            .quantile(0.0001)
            .level(0.998)
            .max_excess(200)
            .build()
            .unwrap();
        
        assert_eq!(detector.s, 10);
        assert_eq!(detector.spot.config().unwrap().level, 0.998);
        assert_eq!(detector.spot.config().unwrap().max_excess, 200);
        assert!(detector.xs_window.is_empty());
        assert!(detector.residuals_window.is_empty());
    }

    #[test]
    fn test_detector_builder_minimal() {
        let detector = Detector::builder()
            .window_size(5)
            .build()
            .unwrap();
        
        assert_eq!(detector.s, 5);
        // Should use default values
        assert_eq!(detector.spot.config().unwrap().level, 0.998);
        assert_eq!(detector.spot.config().unwrap().max_excess, 200);
    }

    #[test]
    fn test_detector_builder_missing_window_size() {
        let result = Detector::builder().build();
        assert!(result.is_err());
        
        let error_msg = format!("{}", result.unwrap_err());
        assert!(error_msg.contains("Missing parameter: window size"));
    }

    #[test]
    fn test_detector_builder_custom_predictors() {
        let custom_predictor = EWMA::new(0.5);
        let custom_estimator = StdDevDiff::new();
        
        let detector = Detector::builder()
            .window_size(15)
            .residual_predictor(custom_predictor)
            .fluctuation_estimator(custom_estimator)
            .build()
            .unwrap();
        
        assert_eq!(detector.s, 15);
    }

    #[test]
    fn test_detector_fit() {
        let mut detector = Detector::new(3, Some(0.0001), Some(0.998), Some(200), Some(EWMA::new(0.0)), Some(StdDevDiff::new())).unwrap();
        // Use a series with more variation to ensure we get non-zero fluctuation values
        let series = Series::from_vec(
            vec![
                1.0, 3.0, 2.0, 8.0, 5.0, 12.0, 7.0, 15.0, 9.0, 20.0, 11.0, 25.0, 13.0, 30.0, 15.0,
            ],
            None,
            None,
        );

        detector.train(&series).unwrap();

        // Verify that sliding windows are initialized
        assert_eq!(detector.xs_window.len(), 3);
        assert!(!detector.residuals_window.is_empty());
    }

    #[test]
    fn test_detector_step() {
        let mut detector = Detector::new(3, Some(0.0001), Some(0.998), Some(200), Some(EWMA::new(0.0)), Some(StdDevDiff::new())).unwrap();
        let series = Series::from_vec(
            vec![1.0, 3.0, 2.0, 8.0, 5.0, 12.0, 7.0, 15.0, 9.0, 20.0],
            None,
            None,
        );

        detector.train(&series).unwrap();

        // Store the last value before step
        let last_value_before = detector.xs_window.back().unwrap().value;

        // Test step function
        let status = detector.detect(100, 25.0).unwrap();

        // Should not panic and return some status
        assert!(matches!(
            status,
            AnomalyStatus::Normal | AnomalyStatus::Anomaly
        ));

        // Verify windows are updated only if status is Normal
        assert_eq!(detector.xs_window.len(), 3);
        if matches!(status, AnomalyStatus::Normal) {
            assert_eq!(detector.xs_window.back().unwrap().value, 25.0);
        } else {
            // Window should not be updated if status is not Normal
            assert_eq!(detector.xs_window.back().unwrap().value, last_value_before);
        }
    }

    #[test]
    fn test_sliding_window_maintenance() {
        let mut detector = Detector::new(3, Some(0.0001), Some(0.998), Some(200), Some(EWMA::new(0.0)), Some(StdDevDiff::new())).unwrap();
        // Use a series with variation to ensure non-zero fluctuations
        let series = Series::from_vec(vec![1.0, 5.0, 2.0, 8.0, 3.0, 12.0, 4.0, 15.0], None, None);

        detector.train(&series).unwrap();

        // Initial window should have last 3 points: [12.0, 4.0, 15.0]
        assert_eq!(detector.xs_window.len(), 3);
        assert_eq!(detector.xs_window[0].value, 12.0);
        assert_eq!(detector.xs_window[2].value, 15.0);

        // Store window state before step
        let first_value_before = detector.xs_window[0].value;
        let last_value_before = detector.xs_window[2].value;

        // Add new point - should maintain window size
        let status = detector.detect(10, 20.0).unwrap();
        assert_eq!(detector.xs_window.len(), 3);

        // Verify window update based on spot status
        if matches!(status, AnomalyStatus::Normal) {
            assert_eq!(detector.xs_window[0].value, 4.0); // First element shifted
            assert_eq!(detector.xs_window[2].value, 20.0); // New element added
        } else {
            // Window should not be updated if status is not Normal
            assert_eq!(detector.xs_window[0].value, first_value_before);
            assert_eq!(detector.xs_window[2].value, last_value_before);
        }
    }
}
