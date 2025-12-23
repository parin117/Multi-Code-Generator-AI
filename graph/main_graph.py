import uuid
import operator
from typing import Annotated, List, TypedDict
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver
from chains.thinker import thinker_chain, thinker_parser
from chains.design_config import design_chain
from langgraph.graph import StateGraph
from chains.flow import flow_chain

class State(TypedDict):
    messages: Annotated[List[dict], operator.concat]  # Changed from operator.concat
    clarification_count: Annotated[int, operator.add]
    clarification_needed: bool
    flow: str  # Store the implementation flow
    design_config: str  # Store the design configuration
    project_name: str  # Store the project name

def Thinker_Agent(state: State) -> Command:
    response = thinker_chain.invoke({
        "messages": state["messages"],
        "clarification_count": state["clarification_count"],
        "format_instructions": thinker_parser.get_format_instructions(),
    })
    # print(f"""This is just before the thinker agent: {state["clarification_count"]}""")
    assistant_message = {"role": "assistant", "content": response["output"]}

    if response['clarification_needed'] == True and state["clarification_count"] < 3:
        return Command(
            update={"messages": [assistant_message], "clarification_needed": True},
            goto="User_Node"
        )
    else:
        return Command(
            update={"messages": [assistant_message], "clarification_needed": False},
            goto="Flow_Node"
        )

def User_Node(state: State):
    """This is the user get back node actually"""
    question = state["messages"][-1]["content"]
    # print(f"Thinker Agent: {question}")
    # print("This is for debug: ",state["messages"])
    # The interrupt will pause execution here
    user_clarification = interrupt(
        {
            "question": question,
            "awaiting": "user_clarification"
        }
    )
    # print(f"Received Human Feedback: {user_clarification}")
    user_message = {"role": "user", "content": user_clarification}
    
    return Command(
        update={
            "messages": [user_message],
            "clarification_count": 1,
            "clarification_needed": False
        },
        goto="Thinker_Agent"
    )

def Implementation_Flow(thinker_output: str):
    response = flow_chain.invoke({"thinker_output": thinker_output})
    return response.content

def Flow_Node(state: State) -> Command:
    """Generate implementation flow from thinker output and assign to state"""
    thinker_output = state["messages"][-1]["content"]
    implementation_flow = Implementation_Flow(thinker_output)
    
    return Command(
        update={"flow": implementation_flow},
        goto="Design_Config_Node"
    )

def Design_Config_Node(state: State) -> Command:
    """Generate design configuration from flow and assign to state"""
    design_output = design_chain.invoke({"flow": state["flow"]})
    
    return Command(
        update={"design_config": design_output.content},
        goto="Project_Name_Node"
    )

def Project_Name_Node(state: State) -> Command:
    """Ask user for project name"""
    # Use interrupt to get project name from user
    project_name = interrupt(
        {
            "question": "Please enter a name for your project:",
            "awaiting": "project_name"
        }
    )
    
    return Command(
        update={"project_name": project_name},
        goto="end_node"
    )

def end_node(state: State):     
    """Final Node"""     
    print(f"The Flow: {state['flow']}")
    print(f"The Design: {state['design_config']}")
    print(f"Project Name: {state['project_name']}")
    return state

# Build the graph
graph = StateGraph(State)
graph.add_node("Thinker_Agent", Thinker_Agent)
graph.add_node("Flow_Node", Flow_Node)
graph.add_node("Design_Config_Node", Design_Config_Node)
graph.add_node("Project_Name_Node", Project_Name_Node)
# graph.add_node("Flow_Node", Flow_Node)
graph.add_node("User_Node", User_Node)
graph.add_node("end_node", end_node)

# Set entry point and edges
graph.set_entry_point("Thinker_Agent")
graph.set_finish_point("end_node")

def get_idea(user_input: str):
    checkpointer = MemorySaver()
    app = graph.compile(checkpointer=checkpointer)

    thread_config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    user_message = {"role": "user", "content": user_input}
    initial_state = {
        "messages": [user_message],
        "clarification_count": 0,
        "clarification_needed": False,
        "flow": "",
        "design_config": "",
        "project_name": ""
    }

    # Initialize the stream
    stream = app.stream(initial_state, config=thread_config)

    while True:
        for chunk in stream:
            for node_id, value in chunk.items():
                # print(f"Node ID: {node_id}")

                if node_id == "__interrupt__":
                    # Extract the question from the interrupt payload
                    question = value[0].value.get("question", "Please provide input:")
                    print(f"Thinker Agent: {question}")
                    # Prompt the user for input
                    user_feedback = input("Your response: ")
                    # Resume the graph with the user's input using stream
                    stream = app.stream(Command(resume=user_feedback), config=thread_config)
                    # print(thread_config)
                    break  # Exit the inner loop to process the resumed stream
                elif node_id == "end_node":
                    initial_state = value
            else:
                continue  # Continue if the inner loop wasn't broken
            break  # Break the outer loop if the inner loop was broken
        else:
            break  
    
    # Return only flow and design_config
    return {
        "flow": initial_state["flow"],
        "design_config": initial_state["design_config"],
        "project_name": initial_state["project_name"]
    }

