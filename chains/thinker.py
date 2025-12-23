from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


load_dotenv()
# Instance of the llm used in the thinker chain
llm = ChatGoogleGenerativeAI(model = "gemini-2.0-flash-exp")
# Define the structured output model
class ThinkerOutput(BaseModel):
    clarification_needed: bool = Field(description="True if clarification is still needed")
    output: str = Field(description="Clarification question or project summary")

# Create the chat prompt template with instructions
thinker_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a senior system architect and strategic thinker within an AI-powered code generation pipeline.

Your role: Transform user ideas into comprehensive system blueprints that guide downstream specialized agents who will deep-dive into implementation details.

Clarification round: {clarification_count}/4

CLARIFICATION PHASE (clarification_needed = true):
- Ask ONE strategic question about: system scope, key components, user workflow, data flow, or critical constraints
- Focus on high-level architecture decisions that impact the entire system
- Identify missing pieces that would affect system design

SYSTEM BLUEPRINT PHASE (clarification_needed = false):
Provide a strategic overview covering these key areas (each will be handled by specialized downstream agents):

1. **SYSTEM OVERVIEW**
   - System purpose and main value proposition
   - High-level user workflow
   - Success metrics and constraints

2. **COMPONENT ARCHITECTURE**
   - Major system components/modules
   - Component responsibilities and boundaries
   - Inter-component communication patterns
   - Critical data flows

3. **IMPLEMENTATION DOMAINS**
   - Frontend requirements (UI/UX needs)
   - Backend services (APIs, business logic)
   - Database design considerations
   - External integrations needed

4. **TECHNICAL FOUNDATION**
   - Technology stack recommendations with rationale
   - Scalability and performance considerations
   - Security and compliance requirements
   - Development and testing approach

5. **EXECUTION ROADMAP**
   - Implementation priority order
   - Critical path dependencies
   - Risk areas requiring special attention
   - Validation checkpoints

Your output serves as the master blueprint that specialized coding agents will use to implement each domain.
Be comprehensive but concise - provide enough strategic direction without diving into implementation details.

OUTPUT: Return ONLY JSON with two fields:
- `clarification_needed`: true/false
- `output`: strategic clarification question OR comprehensive system blueprint

{format_instructions}

"""
    ),
    MessagesPlaceholder(variable_name="messages"),
])


# Setup the parser
thinker_parser = JsonOutputParser(pydantic_object=ThinkerOutput)

# Compose the full chain: prompt -> LLM model -> parser
thinker_chain = thinker_prompt | llm | thinker_parser  

# Initialize conversation state
state = {
    "messages": [],
    "clarification_count": 0,
    "clarification_needed": True,
}

def run_thinker(user_input: str):
    # Append new user input to conversation messages
    state["messages"].append({"role": "user", "content": user_input})

    # Call the chain with current state
    response = thinker_chain.invoke({
        "messages": state["messages"],
        "clarification_count": state["clarification_count"],
        "format_instructions": thinker_parser.get_format_instructions(),
    })
    response = ThinkerOutput(**response)
    # Update state based on LLM response
    if response.clarification_needed :
        state["clarification_needed"] = True
        state["clarification_count"] += 1
        # Add assistant's clarification question to messages
        state["messages"].append({"role": "assistant", "content": response.output})
    else:
        state["clarification_needed"] = False
        # Add the final structured summary to messages
        state["messages"].append({"role": "assistant", "content": response.output})

    return response
# print(thinker_parser.get_format_instructions())

# Example usage:
if __name__ == "__main__":

    user_idea = input("Enter the project idea : ")
    result = run_thinker(user_idea)
    print(result.output)
