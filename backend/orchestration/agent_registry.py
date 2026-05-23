class AgentRegistry:
    """Manages modular forensic agents."""
    def __init__(self):
        self._agents = {}

    def register(self, name, agent_instance):
        """Registers a forensic agent."""
        if name in self._agents:
            raise ValueError(f"Agent {name} is already registered.")
        self._agents[name] = agent_instance

    def get_agent(self, name):
        """Retrieves a registered agent by name."""
        if name not in self._agents:
            raise ValueError(f"Agent {name} not found in registry.")
        return self._agents[name]
    
    def get_all_agents(self):
        """Returns a list of all registered agents."""
        return list(self._agents.values())
        
    def get_agent_names(self):
        return list(self._agents.keys())

agent_registry = AgentRegistry()
