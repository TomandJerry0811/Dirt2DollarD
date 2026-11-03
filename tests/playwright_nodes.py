"""CLI-only adapter for the sheet's 189 Playwright node contracts.

Runs real node constructors and execute/validate/process methods. Only external
provider/repository constructors are replaced. No application methods or expected
results are patched. Each CLI invocation is a fresh process with outbound network
connections disabled. This module is never imported by src.main.
"""
import contextlib
import copy
import importlib
import json
import logging
import socket
import sys
from pathlib import Path
from unittest.mock import patch

CASES = Path(__file__).with_name('playwright_node_cases.json')
ALLOWED_NODES = {
    'client_data_retrieval_node': 'ClientDataRetrievalNode',
    'client_name_extraction_node': 'ClientNameExtractionNode',
    'final_churn_probability_node': 'FinalChurnProbabilityNode',
    'final_client_summary_node': 'FinalClientSummaryNode',
    'result_persistence_node': 'ResultPersistenceNode',
    'historical_kpi_match_node': 'HistoricalKPIMatchNode',
    'historical_update_match_node': 'HistoricalUpdateMatchNode',
    'kpi_analysis_node': 'KPIAnalysisNode',
    'kpi_churn_analysis_node': 'KPIChurnAnalysisNode',
    'kpi_data_node': 'KPIDataNode',
    'kpi_embedding_node': 'KPIEmbeddingNode',
    'summary_batch_preparation_node': 'SummaryBatchPreparationNode',
    'summary_churn_analysis_node': 'SummaryChurnAnalysisNode',
    'summary_embedding_node': 'SummaryEmbeddingNode',
    'summary_generation_node': 'SummaryGenerationNode',
    'updates_data_node': 'UpdatesDataNode',
}
ALLOWED_DEPENDENCIES = {
    'GoogleSheetsProvider', 'GroqProvider', 'HuggingFaceProvider',
    'ClientRepository', 'CampaignStageRepository', 'KPIEmbeddingRepository',
    'ClientUpdateEmbeddingRepository', 'PatternRepository', 'KPIRepository',
    'SummaryEmbeddingRepository',
}


def expand(value):
    """Compact deterministic fixture literals, not application calculations."""
    if isinstance(value, list):
        return [expand(v) for v in value]
    if not isinstance(value, dict):
        return value
    if set(value) == {'$vector'}:
        spec = value['$vector']
        return [spec['value']] * spec['length']
    if set(value) == {'$text'}:
        return value['$text']['value'] * value['$text']['count']
    return {k: expand(v) for k, v in value.items()}


class Dependency:
    def __init__(self, name, methods, calls):
        self.name, self.methods, self.calls = name, methods, calls

    def __getattr__(self, method):
        if method not in self.methods:
            raise AssertionError(f'Unconfigured dependency call: {self.name}.{method}')

        def invoke(*args, **kwargs):
            records = self.calls[self.name].setdefault(method, [])
            records.append({'args': copy.deepcopy(args), 'kwargs': copy.deepcopy(kwargs)})
            rule = self.methods[method]
            if 'raise' in rule:
                kind = rule['raise']['type']
                if kind not in ('RuntimeError', 'ValueError'):
                    raise AssertionError(f'Unsupported fixture exception: {kind}')
                exception = RuntimeError if kind == 'RuntimeError' else ValueError
                raise exception(rule['raise']['message'])
            if 'sequence' in rule:
                index = len(records) - 1
                if index >= len(rule['sequence']):
                    raise AssertionError(f'Fixture exhausted: {self.name}.{method}')
                return copy.deepcopy(rule['sequence'][index])
            if 'lookup' in rule:
                return copy.deepcopy(rule['lookup'].get(str(args[0])))
            if 'return' not in rule:
                raise AssertionError(f'Missing fixture return: {self.name}.{method}')
            return copy.deepcopy(rule['return'])
        return invoke


def run(case):
    from src.domain.entities.workflow_context import WorkflowContext
    module_name = case['node']
    if module_name not in ALLOWED_NODES:
        raise AssertionError('Node is not allowlisted')
    module = importlib.import_module('src.nodes.' + module_name)
    inputs = expand(case['input'])
    context = None if inputs.get('null_context') else WorkflowContext()
    if context is not None:
        for key, value in inputs['context'].items():
            setattr(context, key, copy.deepcopy(value))
    calls = {name: {} for name in inputs['dependencies']}
    with contextlib.ExitStack() as stack:
        for name, methods in inputs['dependencies'].items():
            if name not in ALLOWED_DEPENDENCIES:
                raise AssertionError('Only external dependency constructors may be replaced')
            fake = Dependency(name, methods, calls)
            stack.enter_context(patch.object(module, name, return_value=fake))
        for name, value in inputs.get('constants', {}).items():
            if name != 'SUMMARY_BATCH_SIZE':
                raise AssertionError('Only the batching configuration can be overridden')
            stack.enter_context(patch.object(module, name, value))
        node = getattr(module, ALLOWED_NODES[module_name])(**inputs.get('node_options', {}))
        error = None
        try:
            result = node.execute(context)
        except Exception as exc:
            error = {'type': type(exc).__name__, 'message': str(exc)}
            result = context
        return {'case_id': case['id'], 'node': module_name, 'error': error,
                'context': vars(result) if result is not None else None,
                'calls': calls, 'execution_status': node.status.value}


def no_network(*_args, **_kwargs):
    raise RuntimeError('Outbound network is disabled in node-contract tests')


def main():
    logging.disable(logging.CRITICAL)
    try:
        catalog = json.loads(CASES.read_text(encoding='utf-8'))
        matches = [c for c in catalog['cases'] if c['id'] == sys.argv[1]]
        if len(matches) != 1:
            raise ValueError('Provide exactly one listed TC ID')
        # stdout is a strict JSON protocol. Incidental application prints go to stderr.
        with patch.object(socket.socket, 'connect', no_network), patch.object(socket.socket, 'connect_ex', no_network), contextlib.redirect_stdout(sys.stderr):
            observed = run(matches[0])
        print(json.dumps(observed, ensure_ascii=False, default=str))
    except Exception as exc:
        print(json.dumps({'adapter_error': {'type': type(exc).__name__, 'message': str(exc)}}))
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
