from core.agents.state.chatbot_state import ChatBotState
from core.agents.supervisor.agent_supervisor import supervisor, supervisor_output_router
from core.agents.product_agent.product_supervisor import product_supervisor, product_supervisor_output_router
from core.agents.order_agent.order_agent import order_inquiry_agent, order_agent_output_router, order_agent_tool_node
from core.agents.utility_nodes.nodes import fallback_node, exit_node, ask_human_node
from core.agents.product_agent.product_comparison_agent import product_comparison_agent, product_comparison_agent_output_router, product_comparison_agent_tool_node
from core.agents.product_agent.product_attribute_agent import product_attributes_agent, product_attributes_agent_output_router, product_attributes_agent_tool_node
from core.agents.product_agent.product_statistics_agent import product_statistics_agent, product_statistics_agent_output_router, product_statistics_agent_tool_node
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
import nest_asyncio
nest_asyncio.apply()

# Define a graph
workflow = StateGraph(ChatBotState)

# Add nodes
workflow.add_node("supervisor", supervisor)
workflow.add_node("order_inquiry_agent", order_inquiry_agent)
workflow.add_node("product_supervisor", product_supervisor)
workflow.add_node("product_comparison_agent", product_comparison_agent)
workflow.add_node("product_attributes_agent", product_attributes_agent)
workflow.add_node("product_statistics_agent", product_statistics_agent)
workflow.add_node("fallback", fallback_node)
workflow.add_node("order_agent_tool_node", order_agent_tool_node)
workflow.add_node("product_comparison_agent_tool_node", product_comparison_agent_tool_node)
workflow.add_node("product_attributes_agent_tool_node", product_attributes_agent_tool_node)
workflow.add_node("product_statistics_agent_tool_node", product_statistics_agent_tool_node)
workflow.add_node("ask_human", ask_human_node)
workflow.add_node("exit", exit_node)

# Set the entrypoint as route_query
workflow.set_entry_point("supervisor")

# Determine graph edges
workflow.add_conditional_edges(
    "supervisor",
    supervisor_output_router,
)
workflow.add_conditional_edges(
    "order_inquiry_agent",
    order_agent_output_router,
)
workflow.add_conditional_edges(
    "product_supervisor",
    product_supervisor_output_router,
)
workflow.add_conditional_edges(
    "product_comparison_agent",
    product_comparison_agent_output_router,
)
workflow.add_conditional_edges(
    "product_attributes_agent",
    product_attributes_agent_output_router,
)
workflow.add_conditional_edges(
    "product_statistics_agent",
    product_statistics_agent_output_router,
)
workflow.add_edge("order_agent_tool_node", "order_inquiry_agent") 
workflow.add_edge("product_comparison_agent_tool_node", "product_comparison_agent")
workflow.add_edge("product_attributes_agent_tool_node", "product_attributes_agent")
workflow.add_edge("product_statistics_agent_tool_node", "product_statistics_agent")
workflow.add_edge("exit", END)

# The checkpointer lets the graph persist its state
memory = MemorySaver()
app = workflow.compile(checkpointer=memory, interrupt_before=["ask_human"], interrupt_after=["fallback", "exit"])
