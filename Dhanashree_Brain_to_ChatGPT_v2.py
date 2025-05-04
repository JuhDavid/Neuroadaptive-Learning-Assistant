# -*- coding: utf-8 -*-
"""
Created on Sat May  3 23:10:50 2025

@author: Dhanashree
"""



import os
import requests
import json
from dotenv import load_dotenv
from openai import OpenAI

# Initialize environment variables
load_dotenv()

def initialize_openai_client():
    """Initialize OpenAI client with proper API key handling"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables.\n"
            "1. Create a .env file in your project root\n"
            "2. Add: OPENAI_API_KEY='your-api-key-here'\n"
            "3. Get your API key from https://platform.openai.com/account/api-keys"
        )
    return OpenAI(api_key=api_key)

# Initialize client
client = initialize_openai_client()

def solve_with_r1_1776(problem):
    """Formal algebraic solution using R1 1776 approach"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a math expert specializing in formal algebraic solutions. Provide step-by-step explanations using mathematical notation."},
                {"role": "user", "content": f"Solve: {problem}"}
            ],
            temperature=0.2
        )
        return {
            "model": "R1 1776",
            "solution": response.choices[0].message.content
        }
    except Exception as e:
        return {"error": f"R1 1776 Error: {str(e)}"}

def solve_with_sonar_llm(problem):
    """Visual/intuitive solution using Sonar LLM approach"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a visual math educator. Explain solutions using diagrams, analogies, and real-world examples."},
                {"role": "user", "content": f"Explain how to solve: {problem}"}
            ],
            temperature=0.3
        )
        return {
            "model": "Sonar LLM",
            "solution": response.choices[0].message.content
        }
    except Exception as e:
        return {"error": f"Sonar LLM Error: {str(e)}"}

def create_adaptive_solution(r1_result, sonar_result):
    """Combine solutions into neuroadaptive explanation"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Combine these approaches into a comprehensive lesson:\n"
                 f"Formal Method: {r1_result.get('solution', '')}\n"
                 f"Visual Method: {sonar_result.get('solution', '')}"},
                {"role": "user", "content": "Create integrated explanation"}
            ]
        )
        return {
            "adaptive_solution": response.choices[0].message.content,
            "components": {
                "formal": r1_result.get("solution"),
                "visual": sonar_result.get("solution")
            }
        }
    except Exception as e:
        return {"error": f"Adaptation Error: {str(e)}"}

def main():
    """Main execution flow"""
    problem = "Solve the quadratic equation: 2x² - 5x - 3 = 0"
    
    print(f"\n{' Math Problem Solver ':=^40}")
    print(f"Problem: {problem}\n")
    
    # Get solutions
    r1_result = solve_with_r1_1776(problem)
    sonar_result = solve_with_sonar_llm(problem)
    
    # Display results
    print("\n=== Formal Solution ===")
    print(r1_result.get("solution", r1_result.get("error", "Unknown error")))
    
    print("\n=== Visual Solution ===")
    print(sonar_result.get("solution", sonar_result.get("error", "Unknown error")))
    
    # Create adaptive solution
    if "solution" in r1_result and "solution" in sonar_result:
        adaptive_result = create_adaptive_solution(r1_result, sonar_result)
        print("\n=== Adaptive Solution ===")
        print(adaptive_result.get("adaptive_solution", adaptive_result.get("error", "Adaptation failed")))
        
        # Save results
        with open("math_solution.json", "w") as f:
            json.dump({
                "problem": problem,
                "solutions": {
                    "formal": r1_result["solution"],
                    "visual": sonar_result["solution"],
                    "adaptive": adaptive_result.get("adaptive_solution")
                }
            }, f, indent=2)
        print("\nSolutions saved to math_solution.json")

if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"\nError: {str(e)}")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
