#!/usr/bin/env python3
"""Seed AutoDOC's reference catalogs. Do not renumber existing IDs after publication."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
DOMAINS = [
('PRODUCT', 'Product strategy and vision', 'Product vision|Business case|Product requirements|Roadmap|Scope statement|Stakeholder RACI'),
('REQUIREMENTS', 'Requirements engineering', 'SRS|NFR catalog|Use case|User story|Acceptance criteria|Traceability matrix|Requirements change log'),
('ARCHITECTURE', 'Systems architecture', 'C4 context|C4 container|C4 component|C4 code|ADR|Quality attribute scenarios|Deployment view|Data flow|Network topology|Trust boundaries|Integration landscape'),
('DESIGN', 'Detailed technical design', 'Component design|State machine|Algorithm design|Authentication design|Authorization design|Session design|Database design|Caching design|Queue worker design|Retry circuit breaker|Feature flag design|Migration design'),
('DATA', 'Data and information management', 'Data model|Database schema|Data dictionary|Data lineage|Data classification|Retention policy|ETL specification|Data quality|PII inventory|Disposal procedure'),
('SECURITY', 'Security engineering', 'Threat model|Security architecture|Security requirements|Cryptography specification|Key management|Secret management|Access control matrix|Vulnerability management|Penetration test report|Incident response plan'),
('PRIVACY', 'Privacy and compliance', 'ROPA|DPIA|Consent management|Data processing agreement|Subprocessor inventory|Regulatory control mapping|Privacy request log'),
('APIS', 'APIs and interfaces', 'OpenAPI|GraphQL schema|Protobuf contract|AsyncAPI|Webhook contract|Error catalog|Rate limits|SDK guide|Integration guide|Compatibility matrix'),
('DEVELOPMENT', 'Development process', 'Coding standard|Git workflow|Pull request guide|Code review policy|Contributing guide|Dependency policy|RFC|Technical debt register'),
('BUILD', 'Build and supply chain', 'Pipeline architecture|SBOM|Build provenance|SLSA assessment|Artifact signing|License inventory|Quality gates'),
('TESTING', 'Testing and quality', 'Test strategy|Test plan|Unit test specification|Integration test specification|End to end test specification|Contract test specification|Security test specification|Chaos test specification|Performance test plan|Accessibility test plan|Migration test plan|UAT plan|Defect taxonomy'),
('PERFORMANCE', 'Performance and reliability', 'SLI SLO SLA|Error budget policy|Capacity model|Scaling policy|Load shedding|Latency budget|Cost model'),
('INFRASTRUCTURE', 'Infrastructure and environments', 'Infrastructure as code guide|Network design|Kubernetes architecture|DNS certificate inventory|Environment matrix|Golden image|Platform catalog'),
('CONFIGURATION', 'Configuration and change', 'Configuration item register|CMDB|Change advisory record|RFC process|Environment variable schema|Drift detection'),
('RELEASE', 'Release and deployment', 'Release plan|Release manifest|Changelog|Release notes|Deployment runbook|Rollback procedure|Canary analysis|Operational readiness review|Go no go record'),
('OPERATIONS', 'Operations and observability', 'Operations manual|Service catalog|Runbook|Playbook|On call policy|Escalation tree|Observability strategy|Metric catalog|Log standard|Alert catalog|Synthetic monitoring'),
('INCIDENTS', 'Incident and problem management', 'Incident response|Severity matrix|Incident timeline|Postmortem|Root cause analysis|CAPA register|Known error database'),
('DISASTER-RECOVERY', 'Disaster recovery and continuity', 'DR plan|Business continuity plan|RTO RPO|Backup strategy|Restore procedure|Failover runbook|DR test record|Cyber recovery'),
('VENDORS', 'Vendor and third party', 'Vendor inventory|SLA register|Concentration risk|Vendor offboarding|Integration failure modes'),
('GOVERNANCE', 'Governance risk and compliance', 'Risk register|Control catalog|Control evidence|Audit pack|Policy exception|Governance RACI|Board report'),
('AI-ML', 'AI ML and agents', 'Model card|Model registry|Prompt registry|Tool authorization matrix|Agent behavior specification|AI safety policy|Sandbox specification|Autonomy levels|AI incident log|Evaluation gate|RAG architecture|Human in the loop'),
('USER-SUPPORT', 'User and support', 'User guide|Admin guide|Operator manual|API quickstart|Troubleshooting guide|Help center|Support playbook|FAQ'),
('LIFECYCLE', 'Lifecycle management', 'Deprecation policy|Version support matrix|Migration guide|Data export import|Retirement runbook|Destruction record|Tombstone page'),
('EVIDENCE', 'Evidence packs', 'Build evidence|Release evidence|Access review evidence|Backup evidence|DR test evidence|Pen test evidence|Training evidence|Incident evidence|Privacy request evidence|Model evaluation evidence'),
]
PHASES = [
('FOUNDATION','Context and goals','Problem statement|Goals and non goals|Scope|Stakeholder map|Success metrics'),
('RESEARCH','Discovery and exploration','Research notes|Competitive analysis|Spike|Assumption log'),
('PLANNING','Planning and delivery','Milestones|Task backlog|Risks and dependencies|Delivery plan'),
('ARCHITECTURE','Early architecture','System overview|ADR|C4 sketch|Threat model'),
('CONTRACTS','Implementation contracts','Module contract|Type definitions|Error handling|API contract'),
('IMPLEMENTATION','Implementation guidance','Coding plan|Implementation log|Debugging notes|Migration plan'),
('TESTING','Validation','Test strategy|Acceptance criteria|Test results|UAT'),
('TRACKING','Handoff and tracking','Current state|Next action|Recent changes|Handoff notes'),
('AGENT-CONTEXT','AI agent context','AGENTS.md|CLAUDE.md|Cursor rules|AI-CONTEXT.md|SYSTEM-PROMPT-FOR-CODING-AGENT.md|AGENT-WORKFLOW.md|CURRENT-STATE.md|NEXT-ACTION.md|RECENT-CHANGES.md|AGENT-MEMORY.md|CONTEXT-SNAPSHOT.md|TASK-FOR-AGENT.md|TOOL-USAGE-GUIDE-FOR-AGENT.md|ANTI-PATTERNS-FOR-AGENT.md'),
('SETUP','Project setup','Local setup|Environment matrix|Dependency setup|Developer onboarding'),
('META','Documentation governance','Documentation index|Ownership matrix|Freshness policy|Document control procedure'),
]

TEMPLATE_DIR = {'SPEC':'SPECIFICATIONS','DEC':'DECISIONS','DES':'ARCHITECTURE',
                'PROC':'PROCEDURES','POL':'POLICIES','REF':'REFERENCES',
                'REC':'RECORDS','EVD':'EVIDENCE','TPL':'AGENT-CONTEXT'}

def entries(items, prefix):
    result = []
    for i, (slug, purpose, names) in enumerate(items, 1):
        domain = f'{prefix}{i:02d}-{slug}'
        docs = []
        for n, name in enumerate(names.split('|'), 1):
            doc_id = f'{"DOC" if prefix == "A" else "DEV"}-{prefix}{i:02d}-{n:03d}'
            kind = ('EVD' if 'evidence' in name.lower() or 'SBOM' in name else
                    'DEC' if 'ADR' in name or 'decision' in name.lower() else
                    'PROC' if 'runbook' in name.lower() or 'procedure' in name.lower() else
                    'POL' if 'policy' in name.lower() else
                    'REC' if any(word in name.lower() for word in ('record', 'log', 'report', 'postmortem')) else 'SPEC')
            if (domain.startswith(('A03-', 'A04-', 'B04-')) or name in ('Threat model', 'Data flow')) and kind == 'SPEC':
                kind = 'DES'
            template_dir = 'AGENT-CONTEXT' if domain.startswith('B09-') else TEMPLATE_DIR[kind]
            phase = ('active development' if prefix == 'B' or i in (2, 3, 4, 9, 11) else
                     'pre-release' if i in (1, 5, 6, 7, 8, 10, 12, 13, 14, 21) else 'post-release')
            maturity = 'Project-Phase' if prefix == 'B' else ('Hardened' if phase != 'post-release' else 'Product-Grade')
            required = (['ai-agent'] if domain.startswith(('A21-', 'B09-')) else
                        ['api', 'web', 'saas'] if domain.startswith('A08-') else
                        ['general'] if domain.startswith(('B01-', 'B04-', 'B07-')) else [])
            priority = 'Core' if required == ['general'] else 'Recommended' if required else 'Contextual'
            docs.append({'id': doc_id, 'name': name, 'type': kind, 'audience': 'project team',
                         'owner': '@project-owner', 'owner_type': 'project owner',
                         'purpose': f'Record {name.lower()} for {purpose.lower()}.',
                         'when': phase, 'maturity': maturity, 'priority': priority,
                         'required_for': required, 'required_content': ['Purpose and scope', 'Details and decisions', 'Verification and references'],
                         'related': [], 'mode': 'human-review' if kind not in ('EVD',) else 'source-dependent',
                         'template': f'TEMPLATES/{template_dir}/{doc_id}.md'})
        result.append({'domain': domain, 'purpose': purpose, 'documents': docs})
    return {'version': 1, 'note': 'Inventory of possible documents. Applicability labels are suggestions, not a mandate or evidence of adoption.', 'domains': result}

if __name__ == '__main__':
    for directory, data in [('CATALOG-A', entries(DOMAINS, 'A')), ('CATALOG-B', entries(PHASES, 'B'))]:
        (ROOT / directory / 'INDEX.yaml').write_text(json.dumps(data, indent=2) + '\n')
