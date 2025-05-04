# -*- coding: utf-8 -*-
"""
Created on Sat May  3 22:45:20 2025

@author: Dhanashree
"""
import os
import requests
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def solve_with_r1_1776(problem):
    """
    Solve a math problem using the R1 1776 model approach
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """You are a mathematical reasoning expert. 
                Solve problems using formal algebraic methods with step-by-step explanations."""},
                {"role": "user", "content": f"Solve: {problem}"}
            ],
            temperature=0.2
        )
        return {
            "model": "R1 1776",
            "problem": problem,
            "solution": response.choices[0].message.content
        }
    except Exception as e:
        return {
            "model": "R1 1776",
            "problem": problem,
            "error": f"API Error: {str(e)}"
        }

def solve_with_sonar_llm(problem):
    """
    Solve a math problem using the Sonar LLM visual approach
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """You are a visual math educator. 
                Explain solutions using diagrams, analogies, and real-world examples."""},
                {"role": "user", "content": f"Explain how to solve: {problem}"}
            ],
            temperature=0.3
        )
        return {
            "model": "Sonar LLM",
            "problem": problem,
            "solution": response.choices[0].message.content
        }
    except Exception as e:
        return {
            "model": "Sonar LLM",
            "problem": problem,
            "error": f"API Error: {str(e)}"
        }

def create_neuroadaptive_solution(r1_solution, sonar_solution, user_profile=None):
    """
    Synthesize solutions from both models into an adaptive learning experience
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"""Combine these mathematical approaches into a personalized lesson:
                - Formal Method: {r1_solution['solution']}
                - Visual Method: {sonar_solution['solution']}
                Adapt for: {user_profile}"""},
                {"role": "user", "content": "Create integrated lesson"}
            ]
        )
        return {
            "problem": r1_solution["problem"],
            "adaptive_solution": response.choices[0].message.content,
            "components": {
                "formal": r1_solution["solution"],
                "visual": sonar_solution["solution"]
            }
        }
    except Exception as e:
        return {"error": str(e)}

def solve_math_problem_neuroadaptively(problem):
    """Main execution flow with enhanced error handling"""
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: Missing OPENAI_API_KEY in environment variables")
        print("1. Create .env file in project root")
        print("2. Add: OPENAI_API_KEY=your_api_key_here")
        return
    
    print(f"\nSolving: {problem}")
    
    # Get solutions
    r1 = solve_with_r1_1776(problem)
    sonar = solve_with_sonar_llm(problem)
    
    # Display solutions
    print("\n=== Formal Algebraic Solution ===")
    print(r1.get("solution", r1["error"]))
    
    print("\n=== Visual Intuitive Solution ===")
    print(sonar.get("solution", sonar["error"]))
    
    # Create adaptive solution
    if "solution" in r1 and "solution" in sonar:
        adaptive = create_neuroadaptive_solution(r1, sonar)
        print("\n=== Neuroadaptive Solution ===")
        print(adaptive.get("adaptive_solution", adaptive["error"]))
        
        # Save results
        with open("solution.json", "w") as f:
            json.dump(adaptive, f, indent=2)
        print("\nSaved to solution.json")

# Example execution
if __name__ == "__main__":
    problem = "Solve the quadratic equation: 2x² - 5x - 3 = 0"
    solve_math_problem_neuroadaptively(problem)
