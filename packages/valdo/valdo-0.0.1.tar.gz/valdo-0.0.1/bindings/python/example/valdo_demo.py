import time
import random
from valdo import Detector


def run_valdo():
    """Run the Valdo anomaly detection demo."""
    start_time = time.time()
    
    # Create a detector with window size 10
    detector = Detector(window_size=10)
    
    # Generate training data with timestamp-value pairs (simulating normal behavior)
    print("🚀 Generating training data...")
    training_data = [(i, random.random()) for i in range(1000000)]
    
    print("🚀 Fitting Valdo with cascaded smoothing...")
    detector.train(training_data)
    
    print("✅ Valdo fitted successfully!")
    
    # Test with new data points
    new_data_points = [
        (1000, 1.0),
        (1001, 10.0),  # This should definitely be an anomaly
    ]
    
    print("\n🔍 Processing new data points:")
    for timestamp, value in new_data_points:
        status = detector.detect(timestamp, value)
        
        if str(status) == "Normal":
            print(f"   Point {timestamp}: {value} → Normal")
        else:
            print(f"   Point {timestamp}: {value} → 🚨 ANOMALY DETECTED!")
    
    elapsed_time = time.time() - start_time
    print(f"\n⏱️  Time taken: {elapsed_time:.4f} seconds")


def main():
    """Main function to run the demos."""
    print("🎯 Valdo Anomaly Detection - Python Demo")
    print("=" * 60)
    
    run_valdo()
        
    print("\n✅ Demo completed successfully!")


if __name__ == "__main__":
    main()
