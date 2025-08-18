
from typer.testing import CliRunner
from agentik.cli import app

runner = CliRunner()

def test_version():
    result = runner.invoke(app, ["version"]) 
    assert result.exit_code == 0
    assert "Agentik" in result.stdout

def test_self_test():
    result = runner.invoke(app, ["self-test"]) 
    assert result.exit_code == 0
