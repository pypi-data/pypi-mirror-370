import random
import json

# Sample input data (replace this with your actual _input.all())
sample_input = [
    {"id": 1, "name": "Item 1", "value": 100},
    {"id": 2, "name": "Item 2", "value": 200},
    {"id": 3, "name": "Item 3", "value": 300},
    {"id": 4, "name": "Item 4", "value": 400},
    {"id": 5, "name": "Item 5", "value": 500}
]

def process_items(input_items):
    """
    Loop over input items and add a new field called 'myNewField' to each one
    """
    processed_items = []
    
    for item in input_items:
        # Create a copy of the item to avoid modifying the original
        new_item = item.copy()
        
        # Add the new field - you can customize this logic
        new_item['myNewField'] = f"New value for {item.get('name', 'unknown')}"
        
        # Alternatively, you could add other types of data:
        # new_item['myNewField'] = random.randint(1, 1000)  # Random number
        # new_item['myNewField'] = "default_value"  # Static value
        
        processed_items.append(new_item)
    
    return processed_items

def randomly_output_item(items):
    """
    Randomly select and output one item from the list
    """
    if not items:
        print("No items to select from!")
        return None
    
    random_item = random.choice(items)
    print("Randomly selected item:")
    print(json.dumps(random_item, indent=2))
    return random_item

# Main execution
if __name__ == "__main__":
    print("Original items:")
    for item in sample_input:
        print(json.dumps(item, indent=2))
    
    print("\n" + "="*50 + "\n")
    
    # Process all items (equivalent to your loop)
    processed_items = process_items(sample_input)
    
    print("Processed items with 'myNewField':")
    for item in processed_items:
        print(json.dumps(item, indent=2))
    
    print("\n" + "="*50 + "\n")
    
    # Randomly output one item
    randomly_output_item(processed_items)
    
    print("\n" + "="*50 + "\n")
    
    print(f"Total items processed: {len(processed_items)}") 