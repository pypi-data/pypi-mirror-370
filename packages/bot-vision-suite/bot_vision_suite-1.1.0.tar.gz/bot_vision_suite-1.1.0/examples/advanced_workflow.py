"""
Advanced example: Complex automation workflow using bot-vision-suite.

This example demonstrates:
1. Multi-step workflows
2. Error handling and retries
3. Custom configuration
4. Region-based searching
5. Conditional task execution
"""

import time
from _bot_vision import BotVision
from bot_vision.utils.config import BotVisionConfig
from bot_vision.exceptions import TaskExecutionError, ElementNotFoundError

def create_web_login_workflow():
    """Create a workflow for web application login."""
    return [
        {
            "task_name": "navigate_to_login",
            "description": "Navigate to login page",
            "steps": [
                {
                    "action": "find_text",
                    "text": "Sign In",
                    "region": [0, 0, 1920, 200]  # Top banner area
                },
                {
                    "action": "click_text",
                    "text": "Sign In",
                    "region": [0, 0, 1920, 200]
                }
            ]
        },
        {
            "task_name": "enter_credentials",
            "description": "Enter login credentials",
            "steps": [
                {
                    "action": "find_text",
                    "text": "Username",
                    "region": [400, 200, 1120, 600]  # Center area
                },
                {
                    "action": "click_text",
                    "text": "Username",
                    "region": [400, 200, 1120, 600]
                },
                # Note: In real automation, you'd add typing steps here
                {
                    "action": "find_text",
                    "text": "Password",
                    "region": [400, 200, 1120, 600]
                },
                {
                    "action": "click_text",
                    "text": "Password",
                    "region": [400, 200, 1120, 600]
                }
            ]
        },
        {
            "task_name": "submit_login",
            "description": "Submit login form",
            "steps": [
                {
                    "action": "find_text",
                    "text": "Log In",
                    "region": [400, 400, 1120, 800]  # Lower center
                },
                {
                    "action": "click_text",
                    "text": "Log In",
                    "region": [400, 400, 1120, 800]
                }
            ]
        },
        {
            "task_name": "verify_login",
            "description": "Verify successful login",
            "steps": [
                {
                    "action": "find_text",
                    "text": "Dashboard",
                    "region": [0, 0, 1920, 1080]  # Full screen
                }
            ]
        }
    ]

def create_form_filling_workflow():
    """Create a workflow for filling out a form."""
    return [
        {
            "task_name": "locate_form",
            "description": "Locate the form on page",
            "steps": [
                {
                    "action": "find_text",
                    "text": "Contact Form",
                    "region": [0, 0, 1920, 400]
                }
            ]
        },
        {
            "task_name": "fill_name_field",
            "description": "Fill in name field",
            "steps": [
                {
                    "action": "find_text",
                    "text": "Full Name",
                    "region": [200, 200, 1720, 800]
                },
                {
                    "action": "click_text",
                    "text": "Full Name",
                    "region": [200, 200, 1720, 800]
                }
            ]
        },
        {
            "task_name": "fill_email_field",
            "description": "Fill in email field",
            "steps": [
                {
                    "action": "find_text",
                    "text": "Email",
                    "region": [200, 200, 1720, 800]
                },
                {
                    "action": "click_text",
                    "text": "Email",
                    "region": [200, 200, 1720, 800]
                }
            ]
        },
        {
            "task_name": "submit_form",
            "description": "Submit the form",
            "steps": [
                {
                    "action": "find_text",
                    "text": "Submit",
                    "region": [200, 600, 1720, 1000]
                },
                {
                    "action": "click_text",
                    "text": "Submit",
                    "region": [200, 600, 1720, 1000]
                }
            ]
        }
    ]

def execute_workflow_with_error_handling(bot, workflow, workflow_name):
    """Execute a workflow with comprehensive error handling."""
    print(f"\n{'=' * 50}")
    print(f"Executing workflow: {workflow_name}")
    print(f"{'=' * 50}")
    
    try:
        results = bot.execute_tasks(workflow)
        
        # Analyze results
        total_tasks = len(results)
        successful_tasks = sum(1 for r in results if r['success'])
        failed_tasks = total_tasks - successful_tasks
        
        print(f"\nWorkflow Summary:")
        print(f"  Total tasks: {total_tasks}")
        print(f"  Successful: {successful_tasks}")
        print(f"  Failed: {failed_tasks}")
        print(f"  Success rate: {(successful_tasks/total_tasks)*100:.1f}%")
        
        # Detailed results
        print(f"\nDetailed Results:")
        for i, result in enumerate(results, 1):
            task_name = result['task_name']
            success = result['success']
            status = "✓ PASSED" if success else "✗ FAILED"
            print(f"  {i}. {task_name}: {status}")
            
            if not success:
                error_msg = result.get('error', 'Unknown error')
                print(f"     Error: {error_msg}")
                
                # Optional: Add retry logic here
                print(f"     Suggestion: Check if UI elements are visible")
        
        return results
        
    except TaskExecutionError as e:
        print(f"Workflow execution failed: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error during workflow execution: {e}")
        return None

def demonstrate_configuration_options():
    """Demonstrate different configuration options."""
    print("\n" + "=" * 50)
    print("Configuration Options Demo")
    print("=" * 50)
    
    # High precision configuration
    high_precision_config = BotVisionConfig(
        confidence_threshold=0.95,
        max_retries=1,
        retry_delay=0.5,
        debug_mode=False
    )
    
    # Robust configuration (more forgiving)
    robust_config = BotVisionConfig(
        confidence_threshold=0.7,
        max_retries=5,
        retry_delay=2.0,
        debug_mode=True
    )
    
    configs = [
        ("High Precision", high_precision_config),
        ("Robust/Forgiving", robust_config)
    ]
    
    for config_name, config in configs:
        print(f"\n{config_name} Configuration:")
        print(f"  Confidence threshold: {config.confidence_threshold}")
        print(f"  Max retries: {config.max_retries}")
        print(f"  Retry delay: {config.retry_delay}s")
        print(f"  Debug mode: {config.debug_mode}")

def main():
    """Main function demonstrating advanced usage."""
    print("Bot Vision Suite - Advanced Example")
    print("This example shows complex workflows and error handling")
    
    # Show configuration options
    demonstrate_configuration_options()
    
    # Create bot with robust configuration for demo
    config = BotVisionConfig(
        confidence_threshold=0.8,
        max_retries=3,
        retry_delay=1.5,
        debug_mode=True
    )
    
    bot = BotVision(config=config)
    
    # Create workflows
    workflows = [
        ("Web Login Workflow", create_web_login_workflow()),
        ("Form Filling Workflow", create_form_filling_workflow())
    ]
    
    # Execute each workflow
    all_results = {}
    
    for workflow_name, workflow in workflows:
        print(f"\n⏳ Preparing to execute: {workflow_name}")
        print("Note: This is a demonstration - actual UI elements may not be present")
        
        # Add a small delay to show workflow execution
        time.sleep(1)
        
        results = execute_workflow_with_error_handling(bot, workflow, workflow_name)
        all_results[workflow_name] = results
        
        # Pause between workflows
        if workflow_name != workflows[-1][0]:  # Not the last workflow
            print("\n⏸️  Pausing before next workflow...")
            time.sleep(2)
    
    # Final summary
    print(f"\n{'=' * 60}")
    print("FINAL EXECUTION SUMMARY")
    print(f"{'=' * 60}")
    
    for workflow_name, results in all_results.items():
        if results:
            success_count = sum(1 for r in results if r['success'])
            total_count = len(results)
            print(f"{workflow_name}: {success_count}/{total_count} tasks successful")
        else:
            print(f"{workflow_name}: Workflow failed to execute")
    
    print("\n💡 Tips for better automation:")
    print("   1. Use specific regions to improve accuracy")
    print("   2. Adjust confidence threshold based on your needs")
    print("   3. Enable debug mode during development")
    print("   4. Handle errors gracefully in production")
    print("   5. Test workflows on consistent UI states")

if __name__ == "__main__":
    main()
