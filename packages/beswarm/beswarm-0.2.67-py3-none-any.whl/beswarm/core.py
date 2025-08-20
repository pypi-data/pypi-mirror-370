from .broker import MessageBroker
from .bemcp.bemcp import MCPManager
from .taskmanager import TaskManager
from .knowledge_graph import KnowledgeGraphManager

"""
全局共享实例
"""

broker = MessageBroker()
mcp_manager = MCPManager()
task_manager = TaskManager()
kgm = KnowledgeGraphManager(broker=broker)