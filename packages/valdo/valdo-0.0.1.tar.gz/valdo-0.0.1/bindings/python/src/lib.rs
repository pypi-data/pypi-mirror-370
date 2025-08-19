use pyo3::prelude::*;
use valdo::{AnomalyStatus as RustAnomalyStatus, Detector as RustDetector, Point, Series};

#[pyclass(eq, eq_int)]
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum AnomalyStatus {
    Normal,
    Anomaly,
}

impl From<RustAnomalyStatus> for AnomalyStatus {
    fn from(status: RustAnomalyStatus) -> Self {
        match status {
            RustAnomalyStatus::Normal => AnomalyStatus::Normal,
            RustAnomalyStatus::Anomaly => AnomalyStatus::Anomaly,
        }
    }
}

#[pymethods]
impl AnomalyStatus {
    fn __str__(&self) -> &'static str {
        match self {
            AnomalyStatus::Normal => "Normal",
            AnomalyStatus::Anomaly => "Anomaly",
        }
    }

    fn __repr__(&self) -> String {
        format!("AnomalyStatus.{}", self.__str__())
    }
}

/// Python wrapper for the Valdo Detector
#[pyclass]
pub struct Detector {
    inner: RustDetector,
}

#[pymethods]
impl Detector {
    /// Create a new Detector with specified window size and optional parameters
    ///
    /// Args:
    ///     window_size (int): Size of the sliding window for processing
    ///     quantile (float, optional): Quantile parameter for SPOT detector (default: 0.0001)
    ///     level (float, optional): Level parameter for SPOT detector (default: 0.998)
    ///     max_excess (int, optional): Maximum excess for SPOT detector (default: 200)
    ///
    /// Returns:
    ///     Detector: A new Detector instance
    #[new]
    #[pyo3(signature = (window_size, quantile=None, level=None, max_excess=None))]
    pub fn new(
        window_size: u64,
        quantile: Option<f64>,
        level: Option<f64>,
        max_excess: Option<usize>,
    ) -> PyResult<Self> {
        let mut builder = RustDetector::builder().window_size(window_size);

        if let Some(q) = quantile {
            builder = builder.quantile(q);
        }
        if let Some(l) = level {
            builder = builder.level(l);
        }
        if let Some(m) = max_excess {
            builder = builder.max_excess(m);
        }

        let detector = builder.build().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Failed to create detector: {}",
                e
            ))
        })?;

        Ok(Detector {
            inner: detector,
        })
    }

    /// Train the detector on historical data
    ///
    /// Args:
    ///     data (List[Tuple[int, float]]): List of (timestamp, value) pairs
    ///
    /// Raises:
    ///     ValueError: If training fails
    pub fn train(&mut self, data: Vec<(i64, f64)>) -> PyResult<()> {
        let points: Vec<Point> = data
            .into_iter()
            .map(|(timestamp, value)| Point::new(timestamp, value))
            .collect();
        let series = Series::new(points);
        self.inner.train(&series).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Training failed: {}", e))
        })?;
        Ok(())
    }

    /// Detect anomalies in a new data point
    ///
    /// Args:
    ///     timestamp (int): Timestamp of the data point
    ///     value (float): Value of the data point
    ///
    /// Returns:
    ///     AnomalyStatus: Normal or Anomaly
    ///
    /// Raises:
    ///     ValueError: If detection fails
    pub fn detect(&mut self, timestamp: i64, value: f64) -> PyResult<AnomalyStatus> {
        let status = self.inner.detect(timestamp, value).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Detection failed: {}", e))
        })?;
        Ok(status.into())
    }
}

/// A Python module implemented in Rust for Valdo anomaly detection.
#[pymodule]
fn _valdo(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add_class::<Detector>()?;
    m.add_class::<AnomalyStatus>()?;
    Ok(())
}
