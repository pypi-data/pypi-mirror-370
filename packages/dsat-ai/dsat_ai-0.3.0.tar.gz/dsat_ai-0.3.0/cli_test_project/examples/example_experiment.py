"""
Example scryptorum experiment using decorators.
"""

from scryptorum import experiment, metric, timer, llm_call


@experiment(name="example_experiment")
def run_example_experiment():
    """Simple example experiment."""
    
    # Your experiment logic here
    data = prepare_data()
    results = process_data(data)
    accuracy = evaluate_results(results)
    
    return accuracy


@timer("data_preparation")
def prepare_data():
    """Prepare experimental data."""
    # Simulate data preparation
    import time
    time.sleep(0.1)
    return list(range(100))


@timer("data_processing")
def process_data(data):
    """Process the data."""
    return [x * 2 for x in data]


@llm_call(model="gpt-4")
def call_llm(prompt: str) -> str:
    """Example LLM call (replace with actual implementation)."""
    # This would be your actual LLM call
    return f"Response to: {prompt}"


@metric(name="accuracy", metric_type="accuracy")
def evaluate_results(results):
    """Evaluate experiment results."""
    # Simulate evaluation
    return 0.95


if __name__ == "__main__":
    # Run the experiment
    result = run_example_experiment()
    print(f"Experiment completed with accuracy: {result}")
