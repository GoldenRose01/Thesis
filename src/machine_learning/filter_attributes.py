from settings import excluded_attributes
from src.machine_learning.encoding.Encoding_setting import trace_attributes, resource_attributes

def get_attributes_by_dataset(dataset_name):
    """
    Retrieves attributes relevant to the given dataset name.

    Args:
        dataset_name: Name of the dataset (without the .csv extension).

    Returns:
        tuple: A tuple of lists containing trace attributes and resource attributes for the specified dataset.
    """
    # Ensure the input is stripped of potential whitespace and converted to lowercase for consistency
    dataset_name = dataset_name.strip().lower()

    # Filter resource attributes based on dataset
    resource_dataset_attributes = resource_attributes.get(dataset_name, [])
    trace_dataset_attributes = trace_attributes.get(dataset_name, [])

    # Optional: Exclude certain attributes if necessary
    if excluded_attributes:
        resource_dataset_attributes = [attr for attr in resource_dataset_attributes if attr not in excluded_attributes]
        trace_dataset_attributes = [attr for attr in trace_dataset_attributes if attr not in excluded_attributes]

    return trace_dataset_attributes, resource_dataset_attributes