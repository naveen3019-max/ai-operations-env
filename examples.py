"""
Example: Using the AI Operations Assistant Environment

This script demonstrates how to:
1. Create and interact with the environment
2. Classify emails
3. Handle support tickets
4. Schedule meetings
5. Evaluate performance
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta

from env.environment import AIOperationsEnvironment
from env.models import (
    ClassifyEmailAction,
    ReplyEmailAction,
    EscalateTicketAction,
    CloseTicketAction,
    ScheduleMeetingAction,
    DeleteSpamAction,
    EmailCategory,
)
from tasks.easy import EasyEmailClassificationTask
from tasks.medium import MediumSupportHandlingTask
from tasks.hard import HardFullOperationsTask
from baseline.agent import BaselineAgent


def example_1_basic_environment():
    """Example 1: Basic environment interaction"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Environment Interaction")
    print("=" * 70)

    # Create environment
    env = AIOperationsEnvironment(seed=42, max_steps=50)

    # Populate with sample data
    env.populate_with_emails(count=3)
    env.populate_with_tickets(count=1)

    # Reset environment
    observation = env.reset()

    print(f"\nInitial Observation:")
    print(f"  Emails: {len(observation.emails)}")
    print(f"  Tickets: {len(observation.tickets)}")
    print(f"  Step: {observation.step}")

    # Take an action - classify first email
    if observation.emails:
        email = observation.emails[0]
        print(f"\nClassifying email from: {email.sender}")
        print(f"  Subject: {email.subject}")

        action = ClassifyEmailAction(
            email_id=email.id,
            category=EmailCategory.PRODUCT_INQUIRY,
        )

        observation, reward, done, info = env.step(action)

        print(f"\nAction Result:")
        print(f"  Reward: {reward:.3f}")
        print(f"  Done: {done}")
        print(f"  Reward Explanation: {info['reward_explanation']}")

    # Get complete state
    state = env.state()
    print(f"\nEnvironment State:")
    print(f"  Total Steps: {state['step']}")
    print(f"  Episode Reward: {state['episode_reward']:.3f}")
    print(f"  Action History Length: {len(state['action_history'])}")


def example_2_email_classification_task():
    """Example 2: Run the Easy task (email classification)"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Easy Task - Email Classification")
    print("=" * 70)

    # Create task
    task = EasyEmailClassificationTask(max_steps=50)

    # Run baseline agent
    env = task.setup_environment()
    agent = BaselineAgent(seed=42)

    print(f"\nTask: {task.name}")
    print(f"Difficulty: {task.difficulty}")
    print(f"Max Steps: {task.max_steps}")
    print(f"Emails to classify: {len(env.state.emails)}")

    # Run episode
    total_reward, final_obs = agent.run_episode(env, verbose=False)

    # Evaluate
    result = task.evaluate(env)

    print(f"\nResults:")
    print(f"  Total Reward: {total_reward:.3f}")
    print(f"  Final Score: {result.final_score:.3f}")
    print(f"  Steps Taken: {result.steps_taken}")
    print(f"  Success: {result.success}")
    print(f"  Actions: {result.action_counts}")


def example_3_medium_task():
    """Example 3: Run the Medium task (support handling)"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Medium Task - Support Handling")
    print("=" * 70)

    task = MediumSupportHandlingTask(max_steps=75)
    env = task.setup_environment()
    agent = BaselineAgent(seed=42)

    print(f"\nTask: {task.name}")
    print(f"Difficulty: {task.difficulty}")
    print(f"Environment:")
    print(f"  Emails: {len(env.state.emails)}")
    print(f"  Tickets: {len(env.state.tickets)}")

    total_reward, _ = agent.run_episode(env, verbose=False)
    result = task.evaluate(env)

    print(f"\nResults:")
    print(f"  Final Score: {result.final_score:.3f}")
    print(f"  Components: {result.details}")


def example_4_hard_task():
    """Example 4: Run the Hard task (full operations)"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Hard Task - Full Operations Management")
    print("=" * 70)

    task = HardFullOperationsTask(max_steps=120)
    env = task.setup_environment()
    agent = BaselineAgent(seed=42)

    print(f"\nTask: {task.name}")
    print(f"Difficulty: {task.difficulty}")
    print(f"Environment:")
    print(f"  Emails: {len(env.state.emails)}")
    print(f"  Tickets: {len(env.state.tickets)}")
    print(f"  Meetings: {len(env.state.meetings)}")

    total_reward, _ = agent.run_episode(env, verbose=False)
    result = task.evaluate(env)

    print(f"\nResults:")
    print(f"  Final Score: {result.final_score:.3f}")
    print(f"  Key Metrics:")
    for key, value in result.details.items():
        if isinstance(value, float):
            print(f"    {key}: {value:.3f}")
        else:
            print(f"    {key}: {value}")


def example_5_custom_agent():
    """Example 5: Implement a simple custom agent"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Custom Agent Implementation")
    print("=" * 70)

    class SimpleCustomAgent:
        """A simple custom agent that classifies by subject length"""

        def select_action(self, observation):
            # 1. Classify emails by subject length heuristic
            for email in observation.emails:
                if not email.handled:
                    # Longer subjects = probably legitimate
                    category = (
                        EmailCategory.PRODUCT_INQUIRY
                        if len(email.subject) > 30
                        else EmailCategory.SPAM
                    )
                    return ClassifyEmailAction(
                        email_id=email.id,
                        category=category,
                    )

            # 2. Reply to support emails
            for email in observation.emails:
                if (
                    email.handled
                    and not email.replied
                    and email.category
                    in [EmailCategory.TECHNICAL_SUPPORT, EmailCategory.BILLING]
                ):
                    return ReplyEmailAction(
                        email_id=email.id,
                        reply_content="Thank you for contacting us!",
                    )

            return None

    # Use custom agent
    task = EasyEmailClassificationTask(max_steps=50)
    env = task.setup_environment()
    agent = SimpleCustomAgent()

    obs = env.reset()
    total_reward = 0.0
    steps = 0

    print("\nRunning custom agent on Easy task...")
    while steps < 50:
        action = agent.select_action(obs)
        if action is None:
            break

        obs, reward, done, info = env.step(action)
        total_reward += reward
        steps += 1

        print(f"  Step {steps}: {action.action_type} -> reward: {reward:.3f}")

        if done:
            break

    print(f"\nCustom Agent Results:")
    print(f"  Total Steps: {steps}")
    print(f"  Total Reward: {total_reward:.3f}")


def example_6_reward_structure():
    """Example 6: Understanding the reward structure"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Reward Structure Explanation")
    print("=" * 70)

    env = AIOperationsEnvironment()
    obs = env.reset()
    env.populate_with_emails(1)
    env.populate_with_tickets(1)

    obs = env._get_observation()

    if obs.emails:
        email = obs.emails[0]
        print(f"\nEmail Classification:")
        print(f"  Subject: {email.subject}")

        # Correct classification
        action = ClassifyEmailAction(
            email_id=email.id,
            category=email.ground_truth_category,
        )

        observation, reward, done, info = env.step(action)

        print(f"  Correct classification reward: {reward:.3f}")
        print(f"  Components: {info['reward_components']}")
        print(f"  Explanation: {info['reward_explanation']}")

    # Reset for ticket example
    env = AIOperationsEnvironment()
    env.populate_with_tickets(1)
    obs = env.reset()

    if obs.tickets:
        ticket = obs.tickets[0]
        print(f"\nTicket Escalation:")
        print(f"  Severity: {ticket.severity.value}")
        print(f"  Issue: {ticket.issue}")

        if ticket.severity.value == "critical":
            action = EscalateTicketAction(
                ticket_id=ticket.id,
                escalation_reason="Critical issue requires expert attention",
            )
        else:
            action = CloseTicketAction(
                ticket_id=ticket.id,
                resolution="Issue resolved",
            )

        observation, reward, done, info = env.step(action)

        print(f"  Action: {action.action_type}")
        print(f"  Reward: {reward:.3f}")
        print(f"  Explanation: {info['reward_explanation']}")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("AI Operations Assistant Environment - Usage Examples")
    print("=" * 70)

    examples = [
        ("1", "Basic Environment Interaction", example_1_basic_environment),
        ("2", "Easy Task (Email Classification)", example_2_email_classification_task),
        ("3", "Medium Task (Support Handling)", example_3_medium_task),
        ("4", "Hard Task (Full Operations)", example_4_hard_task),
        ("5", "Custom Agent Implementation", example_5_custom_agent),
        ("6", "Reward Structure", example_6_reward_structure),
    ]

    print("\nAvailable Examples:")
    for num, name, _ in examples:
        print(f"  {num}. {name}")

    print("\nRunning all examples...")

    for num, name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n❌ Error in Example {num}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print("✓ Examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
