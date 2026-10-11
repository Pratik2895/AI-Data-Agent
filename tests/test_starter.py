import copy
import json
from pathlib import Path
import sys
import pytest
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from starter.config import validate
from starter.generate import generate
from starter.verify import check_answer

@pytest.fixture
def config():
    return json.loads((Path(__file__).resolve().parents[1]/'examples/sales/project.json').read_text())

def test_generate_standalone_bundle(config, tmp_path):
    out=generate(validate(config),tmp_path/'new')
    bundle=yaml.safe_load((out/'databricks.yml').read_text())
    assert len(bundle['resources']['jobs']['setup']['tasks'])==3
    assert 'apps' not in bundle['resources']  # Endpoint must exist before app binding.
    app=yaml.safe_load((out/'app.resource.yml').read_text())
    assert app['apps']['agent_app']['source_code_path']=='./src/app'
    for file in (out/'notebooks').glob('*.py'):
        source=file.read_text()
        assert 'PROJECT_CONFIG_LITERAL' not in source
        assert 'customer_support' not in source
        compile(source,str(file),'exec')
    with pytest.raises(ValueError,match='already exists'):
        generate(config,out)

@pytest.mark.parametrize('change',[
    {'tables':[{'name':'orders; DROP TABLE x','description':'bad'}]},
    {'tables':[]}, {'agents':[]}, {'agents':['SQL','unknown']},
    {'agents':['ETL'],'allowed_hosts':[]}, {'allowed_hosts':['https://example.com']},
    {'host':'https://name:secret@example.com'}, {'catalog':'${secrets.foo}'},
    {'checks':[]}, {'mode':'overwrite'}, {'token':'secret'},
])
def test_reject_invalid_configuration(config,change):
    config.update(change)
    with pytest.raises(ValueError): validate(config)

def test_sql_allowlist(monkeypatch):
    from src.agents.runtime import validate_sql
    monkeypatch.setenv('AGENT_TABLES','["orders"]')
    validate_sql('SELECT COUNT(*) FROM ai_agent_demo.customer_support.orders')
    with pytest.raises(ValueError,match='allowlist'):
        validate_sql('SELECT * FROM ai_agent_demo.customer_support.secret')

def test_disabled_workflow_never_constructed(monkeypatch):
    import agent
    from types import SimpleNamespace as N
    from langchain_core.messages import HumanMessage
    monkeypatch.setenv('ENABLED_AGENTS','SQL')
    monkeypatch.setattr(agent,'pick_llm',lambda level:N(with_structured_output=lambda schema:N(invoke=lambda prompt:agent.RouterSchema(answer='ETL'))))
    monkeypatch.setattr(agent,'_build_sql_analyst_graph',lambda:N())
    def fail(): raise AssertionError('Disabled workflow was initialized')
    monkeypatch.setattr(agent,'_build_etl_analyst_graph',fail)
    monkeypatch.setattr(agent,'_build_knowledge_search_graph',fail)
    result=agent._build_data_agent_graph().invoke({'messages':[HumanMessage(content='Extract API data')]})
    assert 'not enabled' in result['final_answer']

def test_checks_fail_on_wrong_answer():
    check_answer('There are 5 orders',['5','orders'])
    with pytest.raises(AssertionError): check_answer('Permission denied',['5'])
