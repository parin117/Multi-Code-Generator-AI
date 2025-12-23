# from graph.main_graph import run_graph

# def main():
#     print("🔷 Welcome to the Web Project Idea Assistant!")
#     user_prompt = input("💬 Please enter your project idea or prompt:\n> ")
#     output = run_graph(user_prompt)
#     print("\n--- Thinker Agent Output ---\n")
#     print(output)

# if __name__ == "__main__":
#     main()

from graph.main_graph import get_idea
from system.workflow_orchestrator import generate_project_with_graph

if __name__ == "__main__":
    user_idea = input("Enter your project idea: ")
    result = get_idea(user_idea)
    
    # Get the variables
    flow = result["flow"]
    design_config = result["design_config"]
    project_name = result["project_name"]
    
    # Print to ensure correctness
    print(f"Flow: {flow}")
    print(f"Design Config: {design_config}")
    print(f"Project Name: {project_name}")
    print("\n--- Generating project with LangGraph workflow system ---\n")
    
    # Run the modularized workflow system
    project_result = generate_project_with_graph(project_name, flow, design_config)
    print("\n--- Project Generation Result ---\n")
    print(project_result)

