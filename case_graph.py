from typing import TypedDict
from langgraph.graph import START,END,StateGraph
from triage_agent import TriageAgent
from a2a import A2ARouter
from case_manager import initialize_db,create_case
class Casestate(TypedDict):
    task_id:str
    description:str
    category:str
    selected_agent:str
    agent_result:dict
    error:str
    case_record:dict

triage_agent=TriageAgent()
a2a_result=A2ARouter()
def triagent_node(state:Casestate)->dict:
    result=triage_agent.classify(state['description'])
    return {
        'category':result['category']
    }
def execute_agent_node(state:Casestate)->dict:
    task={
        'task_id':state['task_id'],
        'description':state['description'],
        'category':state['category']
    }
    result=a2a_result.send_task(task)
    return {'agent_result':result}
def persistent_case_node(state:Casestate)->dict:
    if state['agent_result']['status']!='completed':
        return {}
    case=create_case(state['description'],state['category'])  
    return {'case_record':case}  
builder=StateGraph(Casestate)
builder.add_node('triage',triagent_node)
builder.add_node('execute_agent',execute_agent_node)
builder.add_node('persistent_case',persistent_case_node)
builder.add_edge(START,'triage')
builder.add_edge('triage','execute_agent')
builder.add_edge('execute_agent','persistent_case')
builder.add_edge('persistent_case',END)

case_graph=builder.compile()

if __name__ == "__main__":
    test_cases = [
        "My invoice has an incorrect charge",
        "My internet keeps disconnecting",
        "My application keeps crashing",
    ]

    for i,description in enumerate(test_cases):
        result = case_graph.invoke({"task_id": f"TASK{i:03d}","description": description})
        print(result)


