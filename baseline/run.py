"""
Run baseline agent on all three tasks.
Provides reproducible benchmark results.
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env.environment import AIOperationsEnvironment
from tasks.easy import EasyEmailClassificationTask
from tasks.medium import MediumSupportHandlingTask
from tasks.hard import HardFullOperationsTask
from baseline.agent import BaselineAgent


def run_baseline_on_task(task, num_episodes: int = 3, verbose: bool = True) -> dict:
    """
    Run baseline agent on a task multiple times.
    
    Args:
        task: Task to run
        num_episodes: Number of episodes to run
        verbose: Print progress
    
    Returns:
        Results dictionary
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"Task: {task.name} ({task.difficulty.upper()})")
        print(f"{'='*70}")

    episode_results = []

    for episode in range(num_episodes):
        # Use task's reset which includes population
        task.reset()
        env = task.env
        agent = BaselineAgent(seed=42 + episode)
        
        total_reward, final_obs = agent.run_episode(env, max_steps=task.max_steps, reset_env=False, verbose=verbose)
        
        # Evaluate using task grader
        task_result = task.evaluate(env)

        episode_results.append(
            {
                "episode": episode,
                "total_reward": total_reward,
                "steps": env._state.step,
                "final_score": task_result.final_score,
                "success": task_result.success,
                "action_counts": task_result.action_counts,
                "details": task_result.details,
            }
        )

        if verbose:
            print(
                f"  Episode {episode}: Score={task_result.final_score:.3f}, "
                f"Reward={total_reward:.3f}, Steps={env._state.step}"
            )

    # Aggregate results
    scores = [r["final_score"] for r in episode_results]
    rewards = [r["total_reward"] for r in episode_results]
    avg_score = sum(scores) / len(scores)
    avg_reward = sum(rewards) / len(rewards)
    success_rate = sum(1 for r in episode_results if r["success"]) / len(episode_results)

    if verbose:
        print(f"\n  Average Score: {avg_score:.3f}")
        print(f"  Average Reward: {avg_reward:.3f}")
        print(f"  Success Rate: {success_rate:.1%}")

    return {
        "task_name": task.name,
        "difficulty": task.difficulty,
        "num_episodes": num_episodes,
        "average_score": avg_score,
        "average_reward": avg_reward,
        "success_rate": success_rate,
        "score_std": (
            sum((s - avg_score) ** 2 for s in scores) / len(scores)
        ) ** 0.5,
        "episodes": episode_results,
    }


def main():
    """Run baseline on all tasks."""
    print("="*70)
    print("AI Operations Assistant Environment - Baseline Evaluation")
    print("="*70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Baseline: Rule-based agent with keyword matching")
    print()

    results = {}

    # Easy task
    easy_task = EasyEmailClassificationTask(max_steps=50)
    results["easy"] = run_baseline_on_task(easy_task, num_episodes=3)

    # Medium task
    medium_task = MediumSupportHandlingTask(max_steps=75)
    results["medium"] = run_baseline_on_task(medium_task, num_episodes=3)

    # Hard task
    hard_task = HardFullOperationsTask(max_steps=120)
    results["hard"] = run_baseline_on_task(hard_task, num_episodes=3)

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    for difficulty in ["easy", "medium", "hard"]:
        r = results[difficulty]
        print(f"\n{difficulty.upper()}: {r['task_name']}")
        print(f"  Average Score:  {r['average_score']:.3f} ± {r['score_std']:.3f}")
        print(f"  Average Reward: {r['average_reward']:.3f}")
        print(f"  Success Rate:   {r['success_rate']:.1%}")

    # Save results
    output_file = "baseline_results.json"
    with open(output_file, "w") as f:
        # Convert to JSON-serializable format
        json_results = {}
        for diff, data in results.items():
            json_results[diff] = {
                "task_name": data["task_name"],
                "difficulty": data["difficulty"],
                "average_score": data["average_score"],
                "average_reward": data["average_reward"],
                "success_rate": data["success_rate"],
                "score_std": data["score_std"],
                "episodes": data["episodes"],
            }
        json.dump(json_results, f, indent=2)

    print(f"\n[OK] Results saved to {output_file}")
    print(f"\n[OK] Baseline evaluation complete!")

    return results


def cli_main() -> int:
    """Console-script entrypoint."""
    main()
    return 0


if __name__ == "__main__":
    main()
