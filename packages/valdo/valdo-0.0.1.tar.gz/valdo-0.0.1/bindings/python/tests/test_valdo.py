from valdo import Detector, AnomalyStatus
import pytest
import random

class TestValdo:
    def test_detector_minimal_construction(self):
        detector = Detector(window_size=5)
        assert isinstance(detector, Detector)

    def test_detector_full_construction(self):
        detector = Detector(window_size=5, quantile=0.001, level=0.99, max_excess=10)
        assert isinstance(detector, Detector)

    def test_detector_missing_window_size(self):
        with pytest.raises(TypeError):
            Detector()

    def test_detector_train_and_detect(self):
        detector = Detector(window_size=10)
        # Small training set
        n = 100
        training_data = [(i, random.random()) for i in range(n)]
        detector.train(training_data)
        # Normal point
        status = detector.detect(n, 0.5)
        # Note: we can't use `is` here
        assert status == AnomalyStatus.Normal
        # Anomalous point (large jump)
        status2 = detector.detect(n + 1, 10)
        assert status2 == AnomalyStatus.Anomaly

    def test_anomaly_status_enum(self):
        assert str(AnomalyStatus.Normal) == "Normal"
        assert str(AnomalyStatus.Anomaly) == "Anomaly"
        assert repr(AnomalyStatus.Normal).startswith("AnomalyStatus.Normal")
        assert repr(AnomalyStatus.Anomaly).startswith("AnomalyStatus.Anomaly")
