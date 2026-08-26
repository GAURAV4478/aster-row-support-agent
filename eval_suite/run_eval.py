"""
eval_suite/run_eval.py
Automated evaluation script for the Aster Row Support Agent.
Tests official visible cases and custom cases deterministically.
"""

import os
import json
import sys

# Ensure root directory is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent import run_chat_turn, get_order_status

# Track tool execution status globally for the test turn
LAST_TOOL_CALLED = False
LAST_TOOL_ARGS = {}

# Monkey-patch get_order_status to track when it's invoked by the agent
original_get_order_status = get_order_status
def tracked_get_order_status(order_id: str) -> str:
    global LAST_TOOL_CALLED, LAST_TOOL_ARGS
    LAST_TOOL_CALLED = True
    LAST_TOOL_ARGS = {"order_id": order_id}
    return original_get_order_status(order_id)

# Temporarily replace tool in agent module
import src.agent
src.agent.get_order_status = tracked_get_order_status


def load_json_file(filepath):
    if not os.path.exists(filepath):
        print(f"[!] Warning: Could not find {filepath}")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_case(case):
    global LAST_TOOL_CALLED, LAST_TOOL_ARGS
    
    case_id = case.get("id", "unknown")
    category = case.get("category", "general")
    messages = case.get("messages", [])
    expect = case.get("expect", {})
    
    # 1. Reset conversation history and tool flags for a fresh session
    conversation_history = []
    final_response = ""
    
    # 2. Run multi-turn conversation sequence
    for msg in messages:
        LAST_TOOL_CALLED = False
        LAST_TOOL_ARGS = {}
        
        role = msg["role"]
        content = msg["content"]
        
        if role == "user":
            try:
                final_response = run_chat_turn(content, conversation_history)
                # Append to history for multi-turn tracking
                conversation_history.append({"role": "user", "content": content})
                conversation_history.append({"role": "assistant", "content": final_response})
            except Exception as e:
                return False, f"Exception raised during execution: {e}"

    # 3. Evaluate expectations against final response & tool state
    failures = []
    
    # Check must_include exact substrings
    for sub in expect.get("must_include", []):
        if sub.lower() not in final_response.lower():
            failures.append(f"Missing required substring: '{sub}'")
            
    # Check must_not_include substrings
    for sub in expect.get("must_not_include", []):
        if sub.lower() in final_response.lower():
            failures.append(f"Contains forbidden substring: '{sub}'")

    # Check must_not_follow (prompt injection defenses)
    for sub in expect.get("must_not_follow", []):
        if sub.lower() in final_response.lower():
            failures.append(f"Failed prompt injection defense (followed/included): '{sub}'")

    # Check must_ask_for
    for sub in expect.get("must_ask_for", []):
        if sub.lower() not in final_response.lower():
            failures.append(f"Failed to prompt user for required info: '{sub}'")

    # Check tool expectations
    tool_expectation = expect.get("tool")
    if tool_expectation == "called" or tool_expectation == "order_lookup":
        if not LAST_TOOL_CALLED:
            failures.append("Expected order lookup tool to be called, but it was not.")
    elif tool_expectation == "not_called" or tool_expectation == "not_called_without_id":
        if LAST_TOOL_CALLED:
            failures.append("Tool was called unexpectedly when it should not have been.")

    # Check tool arguments if specified
    expected_args = expect.get("tool_arguments")
    if expected_args and LAST_TOOL_CALLED:
        for key, val in expected_args.items():
            if LAST_TOOL_ARGS.get(key, "").upper() != str(val).upper():
                failures.append(f"Expected tool arg {key}={val}, got {LAST_TOOL_ARGS.get(key)}")

    if failures:
        return False, "; ".join(failures)
    return True, "Passed all checks"


def main():
    print("🚀 Starting Automated Aster Row Agent Evaluation...\n")
    
    visible_cases_path = os.path.join("evaluation", "visible-cases.json")
    custom_cases_path = os.path.join("eval_suite", "custom_cases.json")
    
    raw_visible = load_json_file(visible_cases_path)
    custom_cases = load_json_file(custom_cases_path)
    
    # Normalize visible cases whether they are stored as a list or inside a dictionary key (like {"cases": [...]})
    if isinstance(raw_visible, dict):
        # Look for common keys where test cases might be stored
        cases = raw_visible.get("cases", raw_visible.get("test_cases", []))
        if not cases:
            # If it's a dict of cases keyed by ID
            cases = list(raw_visible.values())
    else:
        cases = raw_visible
        
    all_cases = cases + custom_cases
    if not all_cases:
        print("[!] No test cases found. Check your JSON file formats.")
        return

    results_by_category = {}
    total_passed = 0
    total_cases = len(all_cases)

    import time  # Make sure time is imported at the top of the file

    for case in all_cases:
        case_id = case.get("id", "unnamed")
        category = case.get("category", "general")
        
        if category not in results_by_category:
            results_by_category[category] = {"passed": 0, "total": 0}
            
        results_by_category[category]["total"] += 1
        
        passed, reason = evaluate_case(case)
        
        if passed:
            results_by_category[category]["passed"] += 1
            total_passed += 1
            print(f"✅ [{category.upper()}] {case_id}: PASSED")
        else:
            print(f"❌ [{category.upper()}] {case_id}: FAILED -> {reason}")
            
        # Pause for 12 seconds between test cases to respect Gemini Free Tier rate limits (5 RPM)
        time.sleep(12)

    # Print Category Summary Table
    print("\n" + "="*50)
    print("📊 EVALUATION SUMMARY REPORT")
    print("="*50)
    print(f"{'Category':<20} | {'Passed / Total':<15} | {'Success Rate':<10}")
    print("-" * 50)
    
    for cat, stats in results_by_category.items():
        p = stats["passed"]
        t = stats["total"]
        rate = f"{(p/t)*100:.1f}%" if t > 0 else "0.0%"
        print(f"{cat:<20} | {p} / {t:<13} | {rate:<10}")
        
    print("-" * 50)
    overall_rate = f"{(total_passed/total_cases)*100:.1f}%" if total_cases > 0 else "0.0%"
    print(f"OVERALL: {total_passed} / {total_cases} passed ({overall_rate})\n")


if __name__ == "__main__":
    main()