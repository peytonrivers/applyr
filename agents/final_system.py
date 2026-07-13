# trying to not use AI as much as humanly possivle
"""
    1. we are going to start the browser
    2. we are going to go to the page
    3. we are going to look through all the links and find the one with apply
    4. click the link
    5. we are going to wait for everything to load
    6. after everything loads we are going to look for apply manually link
    7. once we click the apply manually we are going to again wait for the new page to load
    8. after everything loads we are going to click the sign in button
    9. that will be the same exact page and now we are going to try to print the spam content
    10. we are going to fill out the email and password and the click sign in
"""

import asyncio
from playwright.async_api import async_playwright, Playwright
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from playwright.sync_api import TimeoutError
import random
import json
import time
import base64
from datetime import datetime
from state import ApplicationState, MiddlePageDecision, ClickAction, MultipleQuestionItem, MultipleQuestionGrouping, MultipleQuestion, AllElementsItem, AllElementsGrouping, AllElements, CurrentPage, CookiesProcess, DecidePage, ApplyProcess, SignupProcess, FormsAction, PageAction, PageDecision, NewCookiesProcess

from langchain_openai import ChatOpenAI

import time
import os
from dotenv import load_dotenv
load_dotenv()



openai_key = os.getenv("OPENAI_KEY")
MODEL_NAME = "gpt-5.4-nano"
llm = ChatOpenAI(model=MODEL_NAME, temperature = 0.3, api_key=openai_key)
structured_llm = llm.with_structured_output(ClickAction, include_raw=True)
multiple_question_llm = llm.with_structured_output(MultipleQuestion, include_raw=True)
all_elements_llm = llm.with_structured_output(AllElements, include_raw=True)
new_cookies_process_llm = llm.with_structured_output(NewCookiesProcess, include_raw=True)
cookies_process_llm = llm.with_structured_output(CookiesProcess, include_raw=True)
decide_page_llm = llm.with_structured_output(DecidePage, include_raw=True)
apply_process_llm = llm.with_structured_output(ApplyProcess, include_raw=True)
signup_process_llm = llm.with_structured_output(SignupProcess, include_raw=True)
forms_action_llm = llm.with_structured_output(FormsAction, include_raw=True)

url = "https://www.allstate.jobs/job/23310874/software-engineer-product-security/"

# =========================
# COST TRACKER
# =========================

MODEL_PRICES = {
    "gpt-5-nano": {
        "input": 0.05 / 1_000_000,
        "cached_input": 0.005 / 1_000_000,
        "output": 0.40 / 1_000_000,
    },
    "gpt-5.4-nano": {
        "input": 0.20 / 1_000_000,
        "cached_input": 0.02 / 1_000_000,
        "output": 1.20 / 1_000_000,
    },
    "gpt-4.1-nano": {
        "input": 0.10 / 1_000_000,
        "cached_input": 0.025 / 1_000_000,
        "output": 0.40 / 1_000_000,
    },
}


def setup_cost_tracker(state):
    if "cost_tracker" not in state:
        state["cost_tracker"] = {
            "calls": 0,
            "prompt_tokens": 0,
            "cached_prompt_tokens": 0,
            "completion_tokens": 0,
            "reasoning_tokens": 0,
            "visible_output_tokens": 0,
            "total_tokens": 0,
            "input_cost": 0.0,
            "cached_input_cost": 0.0,
            "output_cost": 0.0,
            "total_cost": 0.0,
            "history": [],
            "nodes": {},
        }
    return state


def get_token_usage(raw):
    if raw is None:
        return {}

    if hasattr(raw, "response_metadata") and raw.response_metadata:
        return raw.response_metadata.get("token_usage", {}) or {}

    if hasattr(raw, "usage_metadata") and raw.usage_metadata:
        usage = raw.usage_metadata
        return {
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }

    return {}


def get_token_details(usage):
    prompt_details = usage.get("prompt_tokens_details", {}) or {}
    completion_details = usage.get("completion_tokens_details", {}) or {}

    return {
        "cached_prompt_tokens": prompt_details.get("cached_tokens", 0) or 0,
        "reasoning_tokens": completion_details.get("reasoning_tokens", 0) or 0,
    }


def calculate_call_cost(model_name, prompt_tokens, cached_prompt_tokens, completion_tokens):
    prices = MODEL_PRICES.get(model_name)

    if prices is None:
        raise ValueError(f"Model price not found for: {model_name}")

    normal_prompt_tokens = max(prompt_tokens - cached_prompt_tokens, 0)

    input_cost = normal_prompt_tokens * prices["input"]
    cached_input_cost = cached_prompt_tokens * prices["cached_input"]
    output_cost = completion_tokens * prices["output"]
    total_cost = input_cost + cached_input_cost + output_cost

    return input_cost, cached_input_cost, output_cost, total_cost


def update_node_stats(state, node_name, call_cost, prompt_tokens, completion_tokens, reasoning_tokens):
    nodes = state["cost_tracker"]["nodes"]

    if node_name not in nodes:
        nodes[node_name] = {
            "calls": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "reasoning_tokens": 0,
            "total_cost": 0.0,
        }

    nodes[node_name]["calls"] += 1
    nodes[node_name]["prompt_tokens"] += prompt_tokens
    nodes[node_name]["completion_tokens"] += completion_tokens
    nodes[node_name]["reasoning_tokens"] += reasoning_tokens
    nodes[node_name]["total_cost"] += call_cost


def print_call_cost(
    state,
    node_name,
    model_name,
    prompt_tokens,
    cached_prompt_tokens,
    completion_tokens,
    reasoning_tokens,
    total_tokens,
    input_cost,
    cached_input_cost,
    output_cost,
    total_cost,
):
    visible_output_tokens = max(completion_tokens - reasoning_tokens, 0)

    print("\n" + "=" * 70)
    print(f"LLM CALL #{state['cost_tracker']['calls']}")
    print(f"Node: {node_name}")
    print(f"Model: {model_name}")
    print("=" * 70)
    print("THIS CALL")
    print(f"Prompt Tokens          : {prompt_tokens:,}")
    print(f"Cached Prompt Tokens   : {cached_prompt_tokens:,}")
    print(f"Completion Tokens      : {completion_tokens:,}")
    print(f"Reasoning Tokens       : {reasoning_tokens:,}")
    print(f"Visible Output Tokens  : {visible_output_tokens:,}")
    print(f"Total Tokens           : {total_tokens:,}")
    print("-" * 70)
    print(f"Input Cost             : ${input_cost:.6f}")
    print(f"Cached Input Cost      : ${cached_input_cost:.6f}")
    print(f"Output Cost            : ${output_cost:.6f}")
    print(f"Total Call Cost        : ${total_cost:.6f}")
    print("-" * 70)
    print("RUNNING TOTAL")
    print(f"Total Calls            : {state['cost_tracker']['calls']:,}")
    print(f"Prompt Tokens          : {state['cost_tracker']['prompt_tokens']:,}")
    print(f"Cached Prompt Tokens   : {state['cost_tracker']['cached_prompt_tokens']:,}")
    print(f"Completion Tokens      : {state['cost_tracker']['completion_tokens']:,}")
    print(f"Reasoning Tokens       : {state['cost_tracker']['reasoning_tokens']:,}")
    print(f"Total Tokens           : {state['cost_tracker']['total_tokens']:,}")
    print(f"Total Cost             : ${state['cost_tracker']['total_cost']:.6f}")
    print("=" * 70 + "\n")


def invoke_and_track(llm, prompt, state, node_name, model_name=MODEL_NAME):
    setup_cost_tracker(state)

    response = llm.invoke(prompt)

    raw = None
    parsed = response

    if isinstance(response, dict) and "raw" in response and "parsed" in response:
        raw = response["raw"]
        parsed = response["parsed"]

    usage = get_token_usage(raw)

    prompt_tokens = usage.get("prompt_tokens", 0) or 0
    completion_tokens = usage.get("completion_tokens", 0) or 0
    total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens) or 0

    details = get_token_details(usage)
    cached_prompt_tokens = details["cached_prompt_tokens"]
    reasoning_tokens = details["reasoning_tokens"]
    visible_output_tokens = max(completion_tokens - reasoning_tokens, 0)

    input_cost, cached_input_cost, output_cost, total_cost = calculate_call_cost(
        model_name=model_name,
        prompt_tokens=prompt_tokens,
        cached_prompt_tokens=cached_prompt_tokens,
        completion_tokens=completion_tokens,
    )

    tracker = state["cost_tracker"]

    tracker["calls"] += 1
    tracker["prompt_tokens"] += prompt_tokens
    tracker["cached_prompt_tokens"] += cached_prompt_tokens
    tracker["completion_tokens"] += completion_tokens
    tracker["reasoning_tokens"] += reasoning_tokens
    tracker["visible_output_tokens"] += visible_output_tokens
    tracker["total_tokens"] += total_tokens
    tracker["input_cost"] += input_cost
    tracker["cached_input_cost"] += cached_input_cost
    tracker["output_cost"] += output_cost
    tracker["total_cost"] += total_cost

    update_node_stats(
        state=state,
        node_name=node_name,
        call_cost=total_cost,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        reasoning_tokens=reasoning_tokens,
    )

    tracker["history"].append({
        "time": datetime.now().isoformat(timespec="seconds"),
        "node": node_name,
        "model": model_name,
        "prompt_tokens": prompt_tokens,
        "cached_prompt_tokens": cached_prompt_tokens,
        "completion_tokens": completion_tokens,
        "reasoning_tokens": reasoning_tokens,
        "visible_output_tokens": visible_output_tokens,
        "total_tokens": total_tokens,
        "input_cost": input_cost,
        "cached_input_cost": cached_input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
    })

    print_call_cost(
        state=state,
        node_name=node_name,
        model_name=model_name,
        prompt_tokens=prompt_tokens,
        cached_prompt_tokens=cached_prompt_tokens,
        completion_tokens=completion_tokens,
        reasoning_tokens=reasoning_tokens,
        total_tokens=total_tokens,
        input_cost=input_cost,
        cached_input_cost=cached_input_cost,
        output_cost=output_cost,
        total_cost=total_cost,
    )

    return parsed


def print_final_cost_summary(state):
    setup_cost_tracker(state)
    tracker = state["cost_tracker"]

    print("\n" + "#" * 70)
    print("FINAL APPLICATION COST SUMMARY")
    print("#" * 70)
    print(f"Total LLM Calls        : {tracker['calls']:,}")
    print(f"Prompt Tokens          : {tracker['prompt_tokens']:,}")
    print(f"Cached Prompt Tokens   : {tracker['cached_prompt_tokens']:,}")
    print(f"Completion Tokens      : {tracker['completion_tokens']:,}")
    print(f"Reasoning Tokens       : {tracker['reasoning_tokens']:,}")
    print(f"Visible Output Tokens  : {tracker['visible_output_tokens']:,}")
    print(f"Total Tokens           : {tracker['total_tokens']:,}")
    print("-" * 70)
    print(f"Input Cost             : ${tracker['input_cost']:.6f}")
    print(f"Cached Input Cost      : ${tracker['cached_input_cost']:.6f}")
    print(f"Output Cost            : ${tracker['output_cost']:.6f}")
    print(f"TOTAL COST             : ${tracker['total_cost']:.6f}")

    if tracker["calls"] > 0:
        print(f"Average Cost / Call    : ${tracker['total_cost'] / tracker['calls']:.6f}")

    print("-" * 70)
    print("COST BY NODE")

    for node_name, data in tracker["nodes"].items():
        avg = data["total_cost"] / data["calls"] if data["calls"] else 0
        print(f"\n{node_name}")
        print(f"  Calls           : {data['calls']:,}")
        print(f"  Prompt Tokens   : {data['prompt_tokens']:,}")
        print(f"  Completion      : {data['completion_tokens']:,}")
        print(f"  Reasoning       : {data['reasoning_tokens']:,}")
        print(f"  Total Cost      : ${data['total_cost']:.6f}")
        print(f"  Avg Cost / Call : ${avg:.6f}")

    print("#" * 70 + "\n")

