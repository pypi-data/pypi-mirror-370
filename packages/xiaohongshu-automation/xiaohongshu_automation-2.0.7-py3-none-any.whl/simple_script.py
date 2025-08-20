import random

# Simulating _input.all() - replace this with your actual input source
class MockInput:
    def __init__(self, items):
        self.items = items
    
    def all(self):
        return self.items

# Sample data - replace with your actual input
_input = MockInput([
    {"id": 1, "name": "Item 1", "value": 100},
    {"id": 2, "name": "Item 2", "value": 200},
    {"id": 3, "name": "Item 3", "value": 300},
    {"id": 4, "name": "Item 4", "value": 400},
    {"id": 5, "name": "Item 5", "value": 500}
])

# Loop over input items and add a new field called 'myNewField' to the JSON of each one
for item in _input.all():
    item['myNewField'] = f"Generated value for {item.get('name', 'item')}"
    # You can also use:
    # item['myNewField'] = random.randint(1, 1000)  # Random number
    # item['myNewField'] = "some default value"     # Static value

# Randomly select and output one item
all_items = _input.all()
random_item = random.choice(all_items)

print("Randomly selected item:")
print(random_item)

# Return all items (as in your original code)
result = _input.all()
print(f"\nTotal items: {len(result)}") 