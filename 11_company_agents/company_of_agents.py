# pip install anthropic python-dotenv
#
# Company of Agents using Anthropic Claude API
#
# Hierarchy:
#   CEO
#   ├── CTO  → Tech Lead, Security Analyst, Product Manager
#   ├── CFO  → Budget Analyst, Risk Analyst, Financial Controller
#   ├── HRM  → Recruiter, Training Manager, HR Compliance Officer
#   └── COO  → Process Manager, Quality Manager, Logistics Coordinator

import json
import anthropic
from dotenv import load_dotenv

load_dotenv(override=True)

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-6"


# ---------------------------------------------------------------------------
# Core agentic loop
# ---------------------------------------------------------------------------

class CompanyAgent:
    """An agent with a role, system prompt, and optional sub-agent tools."""

    def __init__(self, name: str, system_prompt: str, tools: list = None, sub_agents: dict = None):
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.sub_agents = sub_agents or {}  # tool_name -> CompanyAgent

    def run(self, task: str, depth: int = 0) -> str:
        indent = "  " * depth
        print(f"{indent}[{self.name}] received task: {task[:120]}{'...' if len(task) > 120 else ''}")

        messages = [{"role": "user", "content": task}]

        while True:
            kwargs = {
                "model": MODEL,
                "max_tokens": 4096,
                "system": self.system_prompt,
                "messages": messages,
            }
            if self.tools:
                kwargs["tools"] = self.tools

            response = client.messages.create(**kwargs)

            # Collect text and tool_use blocks
            text_parts = []
            tool_use_blocks = []
            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)
                elif block.type == "tool_use":
                    tool_use_blocks.append(block)

            if response.stop_reason == "end_turn" or not tool_use_blocks:
                result = "\n".join(text_parts).strip()
                print(f"{indent}[{self.name}] completed.")
                return result

            # Execute each tool call (delegation to sub-agent)
            tool_results = []
            for block in tool_use_blocks:
                agent_name = block.name
                sub_task = block.input.get("task", json.dumps(block.input))
                print(f"{indent}[{self.name}] → delegating to [{agent_name}]")

                if agent_name in self.sub_agents:
                    result = self.sub_agents[agent_name].run(sub_task, depth + 1)
                else:
                    result = f"[ERROR] No sub-agent registered for tool '{agent_name}'"

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})


# ---------------------------------------------------------------------------
# Tool schema helpers
# ---------------------------------------------------------------------------

def delegation_tool(name: str, description: str) -> dict:
    return {
        "name": name,
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The specific task or question to delegate.",
                }
            },
            "required": ["task"],
        },
    }


# ===========================================================================
# SUB-AGENTS (leaf nodes — no further delegation)
# ===========================================================================

# --- CTO sub-agents ---

tech_lead = CompanyAgent(
    name="Tech Lead",
    system_prompt="""You are the Tech Lead of the company.
Your responsibilities:
- Architecture design and technical decisions
- Code quality standards and engineering best practices
- Sprint planning, technical debt management
- Mentoring the engineering team

Provide clear, actionable technical guidance. Be concise.""",
)

security_analyst = CompanyAgent(
    name="Security Analyst",
    system_prompt="""You are the Security Analyst of the company.
Your responsibilities:
- Identifying cybersecurity risks and vulnerabilities
- Recommending security controls and policies
- Compliance with security standards (ISO 27001, SOC 2, GDPR)
- Incident response planning

Provide concise, prioritised security guidance.""",
)

product_manager = CompanyAgent(
    name="Product Manager",
    system_prompt="""You are the Product Manager of the company.
Your responsibilities:
- Defining product roadmap and feature priorities
- Gathering and translating user requirements
- Coordinating between engineering and business stakeholders
- Tracking KPIs and product metrics

Provide structured, user-centric product recommendations.""",
)

# --- CFO sub-agents ---

budget_analyst = CompanyAgent(
    name="Budget Analyst",
    system_prompt="""You are the Budget Analyst of the company.
Your responsibilities:
- Preparing and monitoring departmental budgets
- Cost-benefit analysis for investments
- Variance analysis (actual vs planned spend)
- Financial forecasting support

Provide data-driven budget recommendations.""",
)

risk_analyst = CompanyAgent(
    name="Risk Analyst",
    system_prompt="""You are the Risk Analyst of the company.
Your responsibilities:
- Identifying and assessing financial and operational risks
- Recommending mitigation strategies
- Maintaining the risk register
- Stress-testing financial scenarios

Provide clear risk ratings (High / Medium / Low) with recommended actions.""",
)

financial_controller = CompanyAgent(
    name="Financial Controller",
    system_prompt="""You are the Financial Controller of the company.
Your responsibilities:
- Overseeing accounting operations and month-end close
- Ensuring GAAP / IFRS compliance
- Internal controls and audit readiness
- Financial reporting accuracy

Provide precise financial guidance and compliance advice.""",
)

# --- HRM sub-agents ---

recruiter = CompanyAgent(
    name="Recruiter",
    system_prompt="""You are the Recruiter of the company.
Your responsibilities:
- Sourcing and screening candidates
- Coordinating interviews and assessments
- Writing job descriptions
- Improving time-to-hire and candidate experience

Provide practical talent-acquisition advice.""",
)

training_manager = CompanyAgent(
    name="Training Manager",
    system_prompt="""You are the Training & Development Manager of the company.
Your responsibilities:
- Designing onboarding and upskilling programmes
- Identifying skill gaps across teams
- Measuring training effectiveness (ROI)
- Managing learning management systems (LMS)

Provide structured learning and development plans.""",
)

hr_compliance = CompanyAgent(
    name="HR Compliance Officer",
    system_prompt="""You are the HR Compliance Officer of the company.
Your responsibilities:
- Ensuring adherence to employment law and regulations
- Maintaining HR policies (anti-discrimination, leave, POSH)
- Conducting HR audits
- Managing employee grievances and disciplinary procedures

Provide clear, legally sound HR compliance guidance.""",
)

# --- COO sub-agents ---

process_manager = CompanyAgent(
    name="Process Manager",
    system_prompt="""You are the Process Manager of the company.
Your responsibilities:
- Mapping, optimising, and documenting business processes (BPM)
- Identifying bottlenecks and inefficiencies
- Implementing lean / Six Sigma improvements
- Change management for process rollouts

Provide actionable process improvement recommendations.""",
)

quality_manager = CompanyAgent(
    name="Quality Manager",
    system_prompt="""You are the Quality Manager of the company.
Your responsibilities:
- Setting and enforcing quality standards (ISO 9001)
- Root-cause analysis for defects and complaints
- Quality audits and supplier evaluations
- Continuous improvement initiatives (Kaizen)

Provide structured quality assurance guidance.""",
)

logistics_coordinator = CompanyAgent(
    name="Logistics Coordinator",
    system_prompt="""You are the Logistics Coordinator of the company.
Your responsibilities:
- Managing supply chain and vendor relationships
- Optimising inventory levels and warehouse operations
- Coordinating shipments and last-mile delivery
- Reducing logistics costs

Provide practical supply-chain and logistics recommendations.""",
)


# ===========================================================================
# C-SUITE AGENTS (mid-tier — delegate to sub-agents)
# ===========================================================================

cto = CompanyAgent(
    name="CTO",
    system_prompt="""You are the Chief Technology Officer (CTO) of the company.
You lead all technology strategy, engineering, product development, and security.

When handling a task:
1. Analyse the technology dimension of the request.
2. Delegate to the appropriate specialist(s) using the available tools.
3. Synthesise their inputs into a coherent technology recommendation.
4. Be concise, strategic, and decisive.

Available specialists:
- tech_lead         → architecture, engineering, code quality
- security_analyst  → cybersecurity, compliance, risk
- product_manager   → roadmap, features, user requirements""",
    tools=[
        delegation_tool("tech_lead",        "Delegate architecture or engineering tasks to the Tech Lead."),
        delegation_tool("security_analyst", "Delegate cybersecurity or compliance tasks to the Security Analyst."),
        delegation_tool("product_manager",  "Delegate product roadmap or feature tasks to the Product Manager."),
    ],
    sub_agents={
        "tech_lead":        tech_lead,
        "security_analyst": security_analyst,
        "product_manager":  product_manager,
    },
)

cfo = CompanyAgent(
    name="CFO",
    system_prompt="""You are the Chief Financial Officer (CFO) of the company.
You oversee all financial strategy, budgeting, risk management, and reporting.

When handling a task:
1. Analyse the financial dimension of the request.
2. Delegate to the appropriate specialist(s) using the available tools.
3. Synthesise their inputs into a coherent financial recommendation.
4. Be concise, strategic, and decisive.

Available specialists:
- budget_analyst         → budgeting, cost analysis, forecasting
- risk_analyst           → financial and operational risk
- financial_controller   → accounting, compliance, reporting""",
    tools=[
        delegation_tool("budget_analyst",       "Delegate budgeting or cost-analysis tasks to the Budget Analyst."),
        delegation_tool("risk_analyst",         "Delegate risk assessment tasks to the Risk Analyst."),
        delegation_tool("financial_controller", "Delegate accounting or compliance tasks to the Financial Controller."),
    ],
    sub_agents={
        "budget_analyst":       budget_analyst,
        "risk_analyst":         risk_analyst,
        "financial_controller": financial_controller,
    },
)

hrm = CompanyAgent(
    name="HRM",
    system_prompt="""You are the Head of Human Resources (HRM) of the company.
You oversee talent acquisition, employee development, and HR compliance.

When handling a task:
1. Analyse the people dimension of the request.
2. Delegate to the appropriate specialist(s) using the available tools.
3. Synthesise their inputs into a coherent HR recommendation.
4. Be concise, strategic, and people-focused.

Available specialists:
- recruiter         → hiring, job descriptions, candidate screening
- training_manager  → onboarding, upskilling, L&D programmes
- hr_compliance     → employment law, policies, grievances""",
    tools=[
        delegation_tool("recruiter",        "Delegate hiring or recruitment tasks to the Recruiter."),
        delegation_tool("training_manager", "Delegate training or development tasks to the Training Manager."),
        delegation_tool("hr_compliance",    "Delegate compliance or policy tasks to the HR Compliance Officer."),
    ],
    sub_agents={
        "recruiter":        recruiter,
        "training_manager": training_manager,
        "hr_compliance":    hr_compliance,
    },
)

coo = CompanyAgent(
    name="COO",
    system_prompt="""You are the Chief Operating Officer (COO) of the company.
You oversee day-to-day operations, process excellence, quality, and logistics.

When handling a task:
1. Analyse the operational dimension of the request.
2. Delegate to the appropriate specialist(s) using the available tools.
3. Synthesise their inputs into a coherent operations recommendation.
4. Be concise, strategic, and execution-focused.

Available specialists:
- process_manager       → BPM, lean, process optimisation
- quality_manager       → quality standards, audits, continuous improvement
- logistics_coordinator → supply chain, inventory, delivery""",
    tools=[
        delegation_tool("process_manager",      "Delegate process optimisation tasks to the Process Manager."),
        delegation_tool("quality_manager",      "Delegate quality assurance tasks to the Quality Manager."),
        delegation_tool("logistics_coordinator","Delegate supply chain or logistics tasks to the Logistics Coordinator."),
    ],
    sub_agents={
        "process_manager":       process_manager,
        "quality_manager":       quality_manager,
        "logistics_coordinator": logistics_coordinator,
    },
)


# ===========================================================================
# CEO (top-level orchestrator)
# ===========================================================================

ceo = CompanyAgent(
    name="CEO",
    system_prompt="""You are the Chief Executive Officer (CEO) of the company.
You set the overall vision, strategy, and direction for the organisation.

When given a business task or challenge:
1. Break it down into functional domains (technology, finance, people, operations).
2. Delegate each domain to the appropriate C-suite executive using the available tools.
3. Synthesise all their responses into a unified executive summary with clear decisions and next steps.
4. Be visionary, decisive, and concise.

Your direct reports and their domains:
- cto → technology strategy, engineering, product, security
- cfo → financial strategy, budgeting, risk, reporting
- hrm → talent, culture, learning & development, HR compliance
- coo → operations, process excellence, quality, supply chain""",
    tools=[
        delegation_tool("cto", "Delegate technology or product tasks to the CTO."),
        delegation_tool("cfo", "Delegate financial or risk tasks to the CFO."),
        delegation_tool("hrm", "Delegate people or HR tasks to the HRM."),
        delegation_tool("coo", "Delegate operational or process tasks to the COO."),
    ],
    sub_agents={
        "cto": cto,
        "cfo": cfo,
        "hrm": hrm,
        "coo": coo,
    },
)


# ===========================================================================
# Interactive CLI
# ===========================================================================

BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║           COMPANY OF AGENTS  —  Powered by Claude               ║
╠══════════════════════════════════════════════════════════════════╣
║  CEO  →  CTO  │  CFO  │  HRM  │  COO                           ║
║         ↓          ↓       ↓       ↓                            ║
║    Tech Lead    Budget  Recruiter Process Mgr                   ║
║    Security     Risk    Training  Quality Mgr                   ║
║    Product Mgr  Ctrl    Compliance Logistics                    ║
╚══════════════════════════════════════════════════════════════════╝
Type your business task and press Enter.  Type 'exit' to quit.
"""

EXAMPLE_TASKS = [
    "We are launching a new SaaS product next quarter. What should each department focus on?",
    "We need to hire 10 software engineers in 3 months while keeping costs under control.",
    "Our cloud infrastructure costs have doubled. Investigate and recommend actions.",
    "We want to expand into Southeast Asia. What are the key operational and financial risks?",
]


def main():
    print(BANNER)
    print("Example tasks:")
    for i, t in enumerate(EXAMPLE_TASKS, 1):
        print(f"  {i}. {t}")
    print()

    while True:
        try:
            task = input("\nYour task > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not task:
            continue
        if task.lower() in {"exit", "quit", "q"}:
            print("Goodbye!")
            break

        # Allow picking an example by number
        if task.isdigit() and 1 <= int(task) <= len(EXAMPLE_TASKS):
            task = EXAMPLE_TASKS[int(task) - 1]
            print(f"Running: {task}\n")

        print("\n" + "=" * 70)
        result = ceo.run(task)
        print("\n" + "=" * 70)
        print("\n[CEO FINAL RESPONSE]\n")
        print(result)
        print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
