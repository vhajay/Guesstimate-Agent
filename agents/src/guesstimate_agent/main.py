"""Main entry point for the guesstimate agent"""

import asyncio
import os
from dotenv import load_dotenv
from .agent import GuesstimateSolver

load_dotenv()

async def main():
    """Run the guesstimate solver"""
    
    # Example problems
    problems = [
        "How many piano tuners are there in New York City?",
        "What's the market size for coffee shops in San Francisco?",
        "How many smartphones are sold globally per year?"
    ]
    
    solver = GuesstimateSolver()
    
    print("Guesstimate Agent - LangGraph Solver")
    print("=" * 50)
    
    # Interactive mode
    while True:
        print("\nOptions:")
        print("1. Use example problems")
        print("2. Enter custom problem")
        print("3. Exit")
        
        choice = input("\nChoose option (1-3): ").strip()
        
        if choice == "1":
            print("\nExample Problems:")
            for i, problem in enumerate(problems, 1):
                print(f"{i}. {problem}")
            
            try:
                prob_choice = int(input("\nSelect problem (1-3): ")) - 1
                if 0 <= prob_choice < len(problems):
                    problem = problems[prob_choice]
                    print(f"\nSolving: {problem}")
                    result = await solver.solve(problem)
                    print("\n" + result)
                else:
                    print("Invalid selection")
            except ValueError:
                print("Invalid input")
        
        elif choice == "2":
            problem = input("\nEnter your guesstimate problem: ").strip()
            if problem:
                print(f"\nSolving: {problem}")
                result = await solver.solve(problem)
                print("\n" + result)
        
        elif choice == "3":
            print("Goodbye!")
            break
        
        else:
            print("Invalid option")

if __name__ == "__main__":
    asyncio.run(main())