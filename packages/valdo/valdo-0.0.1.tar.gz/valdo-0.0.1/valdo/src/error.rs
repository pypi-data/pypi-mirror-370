use libspot_rs::SpotError;
use std::fmt;
use std::io;

/// Main error type for valdo-core operations
#[derive(Debug)]
pub enum Error {
    /// IO operation failed
    Io(io::Error),
    /// Parse errors
    Parse(ParseError),
    /// Validation errors
    Validation(ValidationError),
    /// Overflow errors
    Overflow(OverflowError),
    /// Spot errors
    Spot(SpotError),
}

/// Errors that occur during data parsing
#[derive(Debug)]
pub enum ParseError {
    InvalidTimestamp(String),
    InvalidValue(String),
    InvalidFormat(String),
    MissingData(String),
}

/// Errors that occur during data validation
#[derive(Debug)]
pub enum ValidationError {
    NegativeTimestamp(i64),
    NonFiniteValue(f64),
    DuplicateTimestamp(i64),
    EmptyData,
    MissingParameter(String),
}

/// Errors that occur due to overflow conditions
#[derive(Debug)]
pub enum OverflowError {
    TimestampOverflow(String),
    IndexOverflow(String),
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::Io(err) => write!(f, "IO error: {}", err),
            Error::Parse(err) => write!(f, "Parse error: {}", err),
            Error::Validation(err) => write!(f, "Validation error: {}", err),
            Error::Overflow(err) => write!(f, "Overflow error: {}", err),
            Error::Spot(err) => write!(f, "Spot error: {}", err),
        }
    }
}

impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ParseError::InvalidTimestamp(value) => write!(f, "Invalid timestamp: {}", value),
            ParseError::InvalidValue(value) => write!(f, "Invalid value: {}", value),
            ParseError::InvalidFormat(msg) => write!(f, "Invalid format: {}", msg),
            ParseError::MissingData(msg) => write!(f, "Missing data: {}", msg),
        }
    }
}

impl fmt::Display for ValidationError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ValidationError::NegativeTimestamp(ts) => write!(f, "Negative timestamp: {}", ts),
            ValidationError::NonFiniteValue(val) => write!(f, "Non-finite value: {}", val),
            ValidationError::DuplicateTimestamp(ts) => write!(f, "Duplicate timestamp: {}", ts),
            ValidationError::EmptyData => write!(f, "Empty data provided"),
            ValidationError::MissingParameter(param) => write!(f, "Missing parameter: {}", param),
        }
    }
}

impl fmt::Display for OverflowError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            OverflowError::TimestampOverflow(msg) => write!(f, "Timestamp overflow: {}", msg),
            OverflowError::IndexOverflow(msg) => write!(f, "Index overflow: {}", msg),
        }
    }
}

impl std::error::Error for Error {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            Error::Io(err) => Some(err),
            _ => None,
        }
    }
}

impl std::error::Error for ParseError {}
impl std::error::Error for ValidationError {}
impl std::error::Error for OverflowError {}

impl From<io::Error> for Error {
    fn from(err: io::Error) -> Self {
        Error::Io(err)
    }
}

impl From<ParseError> for Error {
    fn from(err: ParseError) -> Self {
        Error::Parse(err)
    }
}

impl From<ValidationError> for Error {
    fn from(err: ValidationError) -> Self {
        Error::Validation(err)
    }
}

impl From<OverflowError> for Error {
    fn from(err: OverflowError) -> Self {
        Error::Overflow(err)
    }
}

impl From<SpotError> for Error {
    fn from(err: SpotError) -> Self {
        Error::Spot(err)
    }
}

impl Error {
    /// Create a parse error for invalid timestamp
    pub fn invalid_timestamp(value: &str) -> Self {
        Error::Parse(ParseError::InvalidTimestamp(value.to_string()))
    }

    /// Create a parse error for invalid value
    pub fn invalid_value(value: &str) -> Self {
        Error::Parse(ParseError::InvalidValue(value.to_string()))
    }

    /// Create a parse error for invalid format
    pub fn invalid_format(msg: &str) -> Self {
        Error::Parse(ParseError::InvalidFormat(msg.to_string()))
    }

    /// Create a parse error for missing data
    pub fn missing_data(msg: &str) -> Self {
        Error::Parse(ParseError::MissingData(msg.to_string()))
    }

    /// Create a validation error for negative timestamp
    pub fn negative_timestamp(timestamp: i64) -> Self {
        Error::Validation(ValidationError::NegativeTimestamp(timestamp))
    }

    /// Create a validation error for non-finite value
    pub fn non_finite_value(value: f64) -> Self {
        Error::Validation(ValidationError::NonFiniteValue(value))
    }

    /// Create a validation error for duplicate timestamp
    pub fn duplicate_timestamp(timestamp: i64) -> Self {
        Error::Validation(ValidationError::DuplicateTimestamp(timestamp))
    }

    /// Create a validation error for empty data
    pub fn empty_data() -> Self {
        Error::Validation(ValidationError::EmptyData)
    }

    /// Create a validation error for missing parameter
    pub fn missing_parameter(param: &str) -> Self {
        Error::Validation(ValidationError::MissingParameter(param.to_string()))
    }

    /// Create an overflow error for timestamp overflow
    pub fn timestamp_overflow(msg: &str) -> Self {
        Error::Overflow(OverflowError::TimestampOverflow(msg.to_string()))
    }

    /// Create an overflow error for index overflow
    pub fn index_overflow(msg: &str) -> Self {
        Error::Overflow(OverflowError::IndexOverflow(msg.to_string()))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::{Error as IoError, ErrorKind};

    #[test]
    fn test_io_error_conversion() {
        let io_err = IoError::new(ErrorKind::NotFound, "File not found");
        let error = Error::Io(io_err);

        assert!(matches!(error, Error::Io(_)));
        assert!(error.to_string().contains("File not found"));
    }

    #[test]
    fn test_parse_error_creation() {
        let err = Error::invalid_timestamp("invalid");
        assert!(matches!(err, Error::Parse(ParseError::InvalidTimestamp(_))));
        assert!(err.to_string().contains("invalid"));

        let err = Error::invalid_value("NaN");
        assert!(matches!(err, Error::Parse(ParseError::InvalidValue(_))));
        assert!(err.to_string().contains("NaN"));

        let err = Error::invalid_format("wrong format");
        assert!(matches!(err, Error::Parse(ParseError::InvalidFormat(_))));
        assert!(err.to_string().contains("wrong format"));

        let err = Error::missing_data("no data");
        assert!(matches!(err, Error::Parse(ParseError::MissingData(_))));
        assert!(err.to_string().contains("no data"));
    }

    #[test]
    fn test_validation_error_creation() {
        let err = Error::negative_timestamp(-123);
        assert!(matches!(
            err,
            Error::Validation(ValidationError::NegativeTimestamp(-123))
        ));

        let err = Error::non_finite_value(f64::NAN);
        assert!(matches!(
            err,
            Error::Validation(ValidationError::NonFiniteValue(_))
        ));

        let err = Error::duplicate_timestamp(456);
        assert!(matches!(
            err,
            Error::Validation(ValidationError::DuplicateTimestamp(456))
        ));

        let err = Error::empty_data();
        assert!(matches!(err, Error::Validation(ValidationError::EmptyData)));

        let err = Error::missing_parameter("window_size");
        assert!(matches!(err, Error::Validation(ValidationError::MissingParameter(_))));
    }

    #[test]
    fn test_overflow_error_creation() {
        let err = Error::timestamp_overflow("timestamp too large");
        assert!(matches!(
            err,
            Error::Overflow(OverflowError::TimestampOverflow(_))
        ));
        assert!(err.to_string().contains("timestamp too large"));

        let err = Error::index_overflow("index out of bounds");
        assert!(matches!(
            err,
            Error::Overflow(OverflowError::IndexOverflow(_))
        ));
        assert!(err.to_string().contains("index out of bounds"));
    }

    #[test]
    fn test_error_display() {
        let err = Error::invalid_timestamp("abc");
        let display_str = format!("{}", err);
        assert!(!display_str.is_empty());

        let err = Error::negative_timestamp(-1);
        let display_str = format!("{}", err);
        assert!(!display_str.is_empty());
    }

    #[test]
    fn test_error_debug() {
        let err = Error::invalid_value("test");
        let debug_str = format!("{:?}", err);
        assert!(!debug_str.is_empty());
        assert!(debug_str.contains("Parse"));
    }

    #[test]
    fn test_result_type_alias() {
        fn test_function() -> Result<i32, Error> {
            Ok(42)
        }

        fn test_error_function() -> Result<i32, Error> {
            Err(Error::empty_data())
        }

        assert_eq!(test_function().unwrap(), 42);
        assert!(test_error_function().is_err());
    }

    #[test]
    fn test_error_chaining() {
        // Test that we can chain different error types
        let io_err = IoError::new(ErrorKind::PermissionDenied, "Access denied");
        let error = Error::Io(io_err);

        match error {
            Error::Io(ref e) => {
                assert_eq!(e.kind(), ErrorKind::PermissionDenied);
            }
            _ => panic!("Expected IO error"),
        }
    }

    #[test]
    fn test_error_pattern_matching() {
        let errors = vec![
            Error::invalid_timestamp("test"),
            Error::negative_timestamp(-1),
            Error::empty_data(),
            Error::timestamp_overflow("overflow"),
        ];

        for err in errors {
            match err {
                Error::Parse(_) => println!("Parse error: {}", err),
                Error::Validation(_) => println!("Validation error: {}", err),
                Error::Overflow(_) => println!("Overflow error: {}", err),
                Error::Io(_) => println!("IO error: {}", err),
                Error::Spot(_) => println!("Spot error: {}", err),
            }
        }
    }
}
