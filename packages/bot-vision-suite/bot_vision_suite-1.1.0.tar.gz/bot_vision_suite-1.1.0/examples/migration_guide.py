"""
Migration example: Converting old bot_vision.py script to use the new package.

This example shows how to migrate from the old monolithic script
to the new modular bot-vision-suite package.
"""

# OLD WAY (from original bot_vision.py):
# import tasks_config
# from bot_vision import BotVision
# bot = BotVision()
# bot.run()

# NEW WAY (using bot-vision-suite package):
from _bot_vision import BotVision, execute_tasks
from bot_vision.utils.config import BotVisionConfig

def migrate_tasks_config():
    """
    Convert old tasks_config.py format to new format.
    
    This function shows how to migrate your existing task configurations
    from the old format to the new package format.
    """
    
    # OLD FORMAT (from tasks_config.py):
    old_tasks = [
        {
            "task_name": "lg_login_task",
            "description": "Login to LG system",
            "steps": [
                {
                    "action": "find_text",
                    "text": "Sign in",
                    "region": [643, 345, 634, 290]
                },
                {
                    "action": "click_text", 
                    "text": "Sign in",
                    "region": [643, 345, 634, 290]
                }
            ]
        }
    ]
    
    # NEW FORMAT (compatible with bot-vision-suite):
    # The format is actually the same! Just import and use differently.
    new_tasks = [
        {
            "task_name": "lg_login_task",
            "description": "Login to LG system", 
            "steps": [
                {
                    "action": "find_text",
                    "text": "Sign in",
                    "region": [643, 345, 634, 290]
                },
                {
                    "action": "click_text",
                    "text": "Sign in", 
                    "region": [643, 345, 634, 290]
                }
            ]
        }
    ]
    
    return new_tasks

def old_way_simulation():
    """Simulate how the old script worked."""
    print("OLD WAY (Monolithic Script):")
    print("- Hard-coded import of tasks_config")
    print("- Limited configuration options")
    print("- All code in one file")
    print("- Direct execution without flexibility")
    print()

def new_way_example():
    """Demonstrate the new package approach."""
    print("NEW WAY (Modular Package):")
    
    # 1. Import tasks from any source (not hard-coded)
    tasks = migrate_tasks_config()
    
    # 2. Flexible configuration
    config = BotVisionConfig(
        confidence_threshold=0.85,
        max_retries=3,
        debug_mode=True
    )
    
    # 3. Multiple usage patterns available
    
    # Pattern 1: Simple function call
    print("Pattern 1 - Simple function:")
    results = execute_tasks(tasks, config=config)
    print(f"  Executed {len(results)} tasks")
    
    # Pattern 2: Class-based approach
    print("Pattern 2 - Class-based:")
    bot = BotVision(config=config)
    results = bot.execute_tasks(tasks)
    print(f"  Executed {len(results)} tasks with class instance")
    
    # Pattern 3: Individual task execution
    print("Pattern 3 - Individual tasks:")
    for task in tasks:
        result = bot.execute_tasks([task])
        task_name = result[0]['task_name']
        success = result[0]['success']
        print(f"  Task '{task_name}': {'Success' if success else 'Failed'}")
    
    print()

def migration_checklist():
    """Provide a migration checklist."""
    print("MIGRATION CHECKLIST:")
    print("=" * 40)
    
    checklist_items = [
        "✓ Install bot-vision-suite: pip install bot-vision-suite",
        "✓ Update imports: from bot_vision import BotVision, execute_tasks",
        "✓ Create configuration object (optional): BotVisionConfig(...)",
        "✓ Pass tasks as parameters instead of importing tasks_config",
        "✓ Update task execution: execute_tasks(your_tasks) or bot.execute_tasks(your_tasks)",
        "✓ Handle results: process returned list of task results",
        "✓ Update error handling: catch bot_vision.exceptions.*",
        "✓ Test with debug mode enabled initially",
        "✓ Remove old bot_vision.py file when migration is complete"
    ]
    
    for item in checklist_items:
        print(f"  {item}")
    
    print()

def show_api_comparison():
    """Show side-by-side API comparison."""
    print("API COMPARISON:")
    print("=" * 50)
    
    print("OLD API:")
    print("  # bot_vision.py (monolithic)")
    print("  from bot_vision import BotVision")
    print("  import tasks_config  # Hard-coded import")
    print("  bot = BotVision()")
    print("  bot.run()  # Uses tasks_config.tasks")
    print()
    
    print("NEW API:")
    print("  # bot-vision-suite (modular)")
    print("  from bot_vision import BotVision, execute_tasks")
    print("  from bot_vision.utils.config import BotVisionConfig")
    print("  ")
    print("  # Load tasks from any source")
    print("  tasks = load_your_tasks()  # JSON, database, etc.")
    print("  config = BotVisionConfig(debug_mode=True)")
    print("  ")
    print("  # Option 1: Function")
    print("  results = execute_tasks(tasks, config=config)")
    print("  ")
    print("  # Option 2: Class")
    print("  bot = BotVision(config=config)")
    print("  results = bot.execute_tasks(tasks)")
    print()

def migration_benefits():
    """Explain benefits of migrating."""
    print("MIGRATION BENEFITS:")
    print("=" * 30)
    
    benefits = [
        "🔧 Modular architecture - easier to maintain and extend",
        "⚙️  Flexible configuration - customize behavior easily",
        "📦 Pip installable - standard Python package",
        "🧪 Better testing - unit tests and integration tests included",
        "📚 Better documentation - comprehensive docs and examples",
        "🔄 Multiple usage patterns - function or class-based",
        "🎯 Better error handling - specific exception types",
        "🐛 Debug support - visual overlays and detailed logging",
        "🔌 Extensible - add your own OCR engines and processors",
        "📈 Performance improvements - optimized image processing"
    ]
    
    for benefit in benefits:
        print(f"  {benefit}")
    
    print()

def main():
    """Main migration demonstration."""
    print("Bot Vision Suite - Migration Example")
    print("=" * 45)
    print("This example shows how to migrate from the old")
    print("monolithic script to the new modular package.")
    print()
    
    # Show the old way
    old_way_simulation()
    
    # Demonstrate new way
    new_way_example()
    
    # Show API comparison
    show_api_comparison()
    
    # Show migration benefits
    migration_benefits()
    
    # Provide checklist
    migration_checklist()
    
    print("NEXT STEPS:")
    print("=" * 20)
    print("1. Review your existing tasks_config.py")
    print("2. Install the new package: pip install bot-vision-suite")
    print("3. Start with basic_example.py to get familiar")
    print("4. Gradually migrate your tasks")
    print("5. Test thoroughly with debug_mode=True")
    print("6. Deploy to production")
    print()
    print("Need help? Check the documentation or examples!")

if __name__ == "__main__":
    main()
