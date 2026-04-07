"""
Example: Run the environment with real Gmail or Outlook emails

This script shows how to integrate the AI Operations Environment with real email accounts.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_integration import get_email_provider
from env import AIOperationsEnvironment
from baseline import BaselineAgent
import json


def run_with_gmail():
    """Process real Gmail emails with the environment"""
    print("=" * 70)
    print("AI Operations Assistant - Real Gmail Integration")
    print("=" * 70)
    print()

    # Step 1: Initialize Gmail provider
    print("[STEP 1] Authenticating with Gmail...")
    provider = get_email_provider('gmail')
    provider.authenticate()
    print()

    # Step 2: Fetch real emails
    print("[STEP 2] Fetching unread emails from Gmail...")
    real_emails = provider.fetch_emails(limit=10)
    print(f"Found {len(real_emails)} emails")
    print()

    if not real_emails:
        print("[INFO] No unread emails found. Using simulated environment instead.")
        return run_simulated()

    # Step 3: Create environment with real emails
    print("[STEP 3] Loading emails into environment...")
    env = AIOperationsEnvironment()
    
    # Reset with custom configuration
    obs = env.reset()
    
    # Add real emails to environment
    env._emails = real_emails
    print(f"[OK] Loaded {len(real_emails)} real emails into environment")
    print()

    # Step 4: Run agent
    print("[STEP 4] Running AI agent to process emails...")
    print("-" * 70)

    agent = BaselineAgent()
    total_reward = 0
    step_count = 0

    while True:
        state = env.state()
        action = agent.act(state)
        
        if action is None:
            break

        obs, reward, done, info = env.step(action)
        total_reward += reward
        step_count += 1

        action_type = list(action.__dict__.keys())[0]
        print(f"Step {step_count}: {action_type} -> reward: {reward:.3f}")

        if done:
            break

    print("-" * 70)
    print()
    print("[RESULTS]")
    print(f"  Steps taken: {step_count}")
    print(f"  Total reward: {total_reward:.3f}")
    print(f"  Average reward per step: {total_reward/step_count:.3f}")
    print()


def run_with_outlook():
    """Process real Outlook emails with the environment"""
    print("=" * 70)
    print("AI Operations Assistant - Real Outlook Integration")
    print("=" * 70)
    print()

    # Step 1: Initialize Outlook provider
    print("[STEP 1] Authenticating with Outlook...")
    print("(Requires: CLIENT_ID environment variable)")
    
    client_id = os.environ.get('OUTLOOK_CLIENT_ID')
    if not client_id:
        print("[ERROR] OUTLOOK_CLIENT_ID environment variable not set")
        print("Set it with: $env:OUTLOOK_CLIENT_ID='your-client-id'")
        return

    provider = get_email_provider('outlook', client_id=client_id)
    provider.authenticate()
    print()

    # Step 2: Fetch real emails
    print("[STEP 2] Fetching unread emails from Outlook...")
    real_emails = provider.fetch_emails(limit=10)
    print(f"Found {len(real_emails)} emails")
    print()

    if not real_emails:
        print("[INFO] No unread emails found. Using simulated environment instead.")
        return run_simulated()

    # Step 3: Create environment with real emails
    print("[STEP 3] Loading emails into environment...")
    env = AIOperationsEnvironment()
    obs = env.reset()
    env._emails = real_emails
    print(f"[OK] Loaded {len(real_emails)} real emails into environment")
    print()

    # Step 4: Run agent
    print("[STEP 4] Running AI agent to process emails...")
    print("-" * 70)

    agent = BaselineAgent()
    total_reward = 0
    step_count = 0

    while True:
        state = env.state()
        action = agent.act(state)
        
        if action is None:
            break

        obs, reward, done, info = env.step(action)
        total_reward += reward
        step_count += 1

        action_type = list(action.__dict__.keys())[0]
        print(f"Step {step_count}: {action_type} -> reward: {reward:.3f}")

        if done:
            break

    print("-" * 70)
    print()
    print("[RESULTS]")
    print(f"  Steps taken: {step_count}")
    print(f"  Total reward: {total_reward:.3f}")
    print(f"  Average reward per step: {total_reward/step_count:.3f}")
    print()


def run_simulated():
    """Fall back to simulated environment"""
    print("=" * 70)
    print("AI Operations Assistant - Simulated Environment")
    print("=" * 70)
    print()

    env = AIOperationsEnvironment()
    obs = env.reset()

    agent = BaselineAgent()
    total_reward = 0
    step_count = 0

    while True:
        state = env.state()
        action = agent.act(state)
        
        if action is None:
            break

        obs, reward, done, info = env.step(action)
        total_reward += reward
        step_count += 1

        action_type = list(action.__dict__.keys())[0]
        print(f"Step {step_count}: {action_type} -> reward: {reward:.3f}")

        if done:
            break

    print()
    print("[RESULTS]")
    print(f"  Steps taken: {step_count}")
    print(f"  Total reward: {total_reward:.3f}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run AI Operations Environment with real emails")
    parser.add_argument(
        '--provider',
        choices=['gmail', 'outlook', 'simulated'],
        default='simulated',
        help='Email provider to use (default: simulated)'
    )

    args = parser.parse_args()

    if args.provider == 'gmail':
        run_with_gmail()
    elif args.provider == 'outlook':
        run_with_outlook()
    else:
        run_simulated()
