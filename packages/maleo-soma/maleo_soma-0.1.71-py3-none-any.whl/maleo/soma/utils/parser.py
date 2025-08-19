from user_agents.parsers import parse
from maleo.soma.schemas.user_agent import UserAgent


def parse_user_agent(user_agent_string: str) -> UserAgent:
    parsed_user_agent = parse(user_agent_string)
    return UserAgent.model_validate(parsed_user_agent, from_attributes=True)
