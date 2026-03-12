from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.agents.state import AgentState
from app.agents.tools import assign_task, share_document, check_progress, get_performance_insights, set_reminder, create_team, add_team_member, research_technical_question, delete_team, remove_team_member, delete_task
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
import datetime

# Initialize the model
# Note: For GitHub Models, you might need to adjust the base_url and api_key
llm = ChatOpenAI(
    model=settings.MODEL_NAME,
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_API_BASE,
    temperature=0
)

tools = [assign_task, share_document, check_progress, get_performance_insights, set_reminder, create_team, add_team_member, research_technical_question, delete_team, remove_team_member, delete_task]
llm_with_tools = llm.bind_tools(tools)

def agent_node(state: AgentState):
    messages = state['messages']
    # Inject current date into system prompt if not present
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    system_prompt = f"You are TrackUp Buddy, an intelligent project management assistant. Today's date is {current_date}. When assigning tasks, use this date as reference. When asked about team status, provide detailed breakdowns."
    
    # Check if the first message is a SystemMessage, if so replace/update it, else prepend
    if isinstance(messages[0], SystemMessage):
        messages[0] = SystemMessage(content=system_prompt)
    else:
        messages.insert(0, SystemMessage(content=system_prompt))
        
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

from langgraph.prebuilt import ToolNode
tool_node = ToolNode(tools)

workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
)

workflow.add_edge("tools", "agent")

checkpointer = MemorySaver()
app_graph = workflow.compile(checkpointer=checkpointer)
