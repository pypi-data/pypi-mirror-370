"""
Basic example: Using bot-vision-suite for simple automation tasks.

This example demonstrates:
1. Basic package usage
2. Simple task execution
3. Finding and clicking text elements
"""

from _bot_vision import BotVision, execute_tasks, find_text, click_text
from bot_vision.utils.config import BotVisionConfig

def main():
    print("Bot Vision Suite - Basic Example")
    print("=" * 40)
    
    # Example 1: Using convenience functions
    print("\n1. Using convenience functions:")
    
    # Find text on screen
    print("Looking for 'Start' button...")
    if find_text("Start"):
        print("✓ Found 'Start' button!")
    else:
        print("✗ 'Start' button not found")
    
    # Click a button
    print("Trying to click 'OK' button...")
    if click_text("OK"):
        print("✓ Successfully clicked 'OK' button!")
    else:
        print("✗ Could not click 'OK' button")
    
    # Example 2: Using task configuration
    print("\n2. Using task-based approach:")
    
    # Define tasks
    tasks = [
        {
            "task_name": "find_login",
            "description": "Find login elements",
            "steps": [
                {
                    "action": "find_text",
                    "text": "Login",
                    "region": [0, 0, 500, 300]  # x, y, width, height
                },
                {
                    "action": "find_text",
                    "text": "Username",
                    "region": [0, 0, 500, 300]
                }
            ]
        },
        {
            "task_name": "click_buttons",
            "description": "Click various buttons",
            "steps": [
                {
                    "action": "click_text",
                    "text": "Submit",
                    "region": [100, 200, 400, 400]
                }
            ]
        }
    ]
    
    # Execute tasks
    results = execute_tasks(tasks)
    
    # Display results
    for result in results:
        task_name = result['task_name']
        success = result['success']
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"Task '{task_name}': {status}")
        
        if not success and 'error' in result:
            print(f"  Error: {result['error']}")
    
    # Example 3: Using BotVision class with custom configuration
    print("\n3. Using BotVision class with custom config:")
    
    # Create custom configuration
    config = BotVisionConfig(
        confidence_threshold=0.9,  # Higher confidence requirement
        max_retries=5,             # More retries
        debug_mode=True            # Enable debug output
    )
    
    # Create BotVision instance
    bot = BotVision(config=config)
    
    # Define a simple task
    simple_task = {
        "task_name": "demo_task",
        "description": "Demonstration task",
        "steps": [
            {
                "action": "find_text",
                "text": "Desktop",
                "region": None  # Search entire screen
            }
        ]
    }
    
    # Execute task
    results = bot.execute_tasks([simple_task])
    
    for result in results:
        print(f"Demo task result: {result}")

if __name__ == "__main__":
    main()
