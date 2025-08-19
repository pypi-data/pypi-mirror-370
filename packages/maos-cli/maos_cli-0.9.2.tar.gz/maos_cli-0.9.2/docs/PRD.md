Complete Implementation Plan with SQLite Storage                                          │ │
│ │                                                                                           │ │
│ │ Phase 1: Add SQLite Database Backend                                                      │ │
│ │                                                                                           │ │
│ │ 1.1 Create SQLite Persistence Layer (src/maos/interfaces/sqlite_persistence.py)           │ │
│ │                                                                                           │ │
│ │ import sqlite3                                                                            │ │
│ │ import aiosqlite                                                                          │ │
│ │                                                                                           │ │
│ │ class SqlitePersistence(PersistenceInterface):                                            │ │
│ │     def __init__(self, db_path: str = "./maos.db"):                                       │ │
│ │         self.db_path = db_path                                                            │ │
│ │         self._init_database()                                                             │ │
│ │                                                                                           │ │
│ │     def _init_database(self):                                                             │ │
│ │         # Create tables                                                                   │ │
│ │         """                                                                               │ │
│ │         CREATE TABLE IF NOT EXISTS agents (                                               │ │
│ │             id TEXT PRIMARY KEY,                                                          │ │
│ │             name TEXT,                                                                    │ │
│ │             type TEXT,                                                                    │ │
│ │             session_id TEXT,                                                              │ │
│ │             status TEXT,                                                                  │ │
│ │             created_at TIMESTAMP,                                                         │ │
│ │             last_active TIMESTAMP                                                         │ │
│ │         );                                                                                │ │
│ │                                                                                           │ │
│ │         CREATE TABLE IF NOT EXISTS sessions (                                             │ │
│ │             session_id TEXT PRIMARY KEY,                                                  │ │
│ │             agent_id TEXT,                                                                │ │
│ │             conversation_history JSON,                                                    │ │
│ │             turn_count INTEGER,                                                           │ │
│ │             total_cost REAL,                                                              │ │
│ │             created_at TIMESTAMP,                                                         │ │
│ │             FOREIGN KEY (agent_id) REFERENCES agents(id)                                  │ │
│ │         );                                                                                │ │
│ │                                                                                           │ │
│ │         CREATE TABLE IF NOT EXISTS tasks (                                                │ │
│ │             id TEXT PRIMARY KEY,                                                          │ │
│ │             description TEXT,                                                             │ │
│ │             status TEXT,                                                                  │ │
│ │             assigned_agents JSON,                                                         │ │
│ │             subtasks JSON,                                                                │ │
│ │             progress REAL,                                                                │ │
│ │             created_at TIMESTAMP                                                          │ │
│ │         );                                                                                │ │
│ │                                                                                           │ │
│ │         CREATE TABLE IF NOT EXISTS messages (                                             │ │
│ │             id INTEGER PRIMARY KEY AUTOINCREMENT,                                         │ │
│ │             from_agent TEXT,                                                              │ │
│ │             to_agent TEXT,                                                                │ │
│ │             message TEXT,                                                                 │ │
│ │             timestamp TIMESTAMP,                                                          │ │
│ │             FOREIGN KEY (from_agent) REFERENCES agents(id),                               │ │
│ │             FOREIGN KEY (to_agent) REFERENCES agents(id)                                  │ │
│ │         );                                                                                │ │
│ │                                                                                           │ │
│ │         CREATE TABLE IF NOT EXISTS checkpoints (                                          │ │
│ │             id TEXT PRIMARY KEY,                                                          │ │
│ │             name TEXT,                                                                    │ │
│ │             orchestrator_state JSON,                                                      │ │
│ │             agent_sessions JSON,                                                          │ │
│ │             task_states JSON,                                                             │ │
│ │             created_at TIMESTAMP                                                          │ │
│ │         );                                                                                │ │
│ │         """                                                                               │ │
│ │                                                                                           │ │
│ │ Phase 2: Fix Claude Process Management                                                    │ │
│ │                                                                                           │ │
│ │ 2.1 Update ClaudeCodeCLIManager (src/maos/core/claude_cli_manager.py)                     │ │
│ │                                                                                           │ │
│ │ async def spawn_claude_instance(                                                          │ │
│ │     self,                                                                                 │ │
│ │     agent_name: str,                                                                      │ │
│ │     task: str,  # NEW: Actual task to execute                                             │ │
│ │     working_dir: Optional[str] = None,                                                    │ │
│ │     max_turns: int = 10,                                                                  │ │
│ │     output_format: str = "json"                                                           │ │
│ │ ) -> Tuple[str, str]:  # Returns (process_id, session_id)                                 │ │
│ │                                                                                           │ │
│ │     # Build command                                                                       │ │
│ │     cmd = [                                                                               │ │
│ │         self.claude_cli_path,                                                             │ │
│ │         "-p", task,                                                                       │ │
│ │         "--output-format", output_format,                                                 │ │
│ │         "--max-turns", str(max_turns),                                                    │ │
│ │         "--verbose"  # To get session_id in output                                        │ │
│ │     ]                                                                                     │ │
│ │                                                                                           │ │
│ │     # Spawn process                                                                       │ │
│ │     process = subprocess.Popen(cmd, ...)                                                  │ │
│ │                                                                                           │ │
│ │     # Parse first response to get session_id                                              │ │
│ │     first_response = await self._read_json_response(process)                              │ │
│ │     session_id = first_response.get("session_id")                                         │ │
│ │                                                                                           │ │
│ │     # Store in database                                                                   │ │
│ │     await self.db.save_session(agent_name, session_id, task)                              │ │
│ │                                                                                           │ │
│ │     return process_id, session_id                                                         │ │
│ │                                                                                           │ │
│ │ Phase 3: Implement Task Decomposition                                                     │ │
│ │                                                                                           │ │
│ │ 3.1 Create TaskDecomposer (src/maos/core/task_decomposer.py)                              │ │
│ │                                                                                           │ │
│ │ class TaskDecomposer:                                                                     │ │
│ │     def __init__(self, db: SqlitePersistence):                                            │ │
│ │         self.db = db                                                                      │ │
│ │                                                                                           │ │
│ │     async def decompose(self, user_request: str) -> TaskPlan:                             │ │
│ │         """                                                                               │ │
│ │         Break down user request into parallel subtasks                                    │ │
│ │                                                                                           │ │
│ │         Example:                                                                          │ │
│ │         "implement PRD" ->                                                                │ │
│ │         [                                                                                 │ │
│ │             ("Design database schema", "architect"),                                      │ │
│ │             ("Build user authentication", "backend-dev"),                                 │ │
│ │             ("Create UI components", "frontend-dev"),                                     │ │
│ │             ("Write unit tests", "tester"),                                               │ │
│ │             ("Review security", "security-auditor")                                       │ │
│ │         ]                                                                                 │ │
│ │         """                                                                               │ │
│ │                                                                                           │ │
│ │     async def suggest_agents(self, task_plan: TaskPlan) -> AgentProposal:                 │ │
│ │         # Check existing agents in DB                                                     │ │
│ │         existing = await self.db.get_active_agents()                                      │ │
│ │                                                                                           │ │
│ │         # Match tasks to agents                                                           │ │
│ │         proposal = AgentProposal()                                                        │ │
│ │         for subtask in task_plan.subtasks:                                                │ │
│ │             if matching_agent := self._find_matching_agent(existing, subtask):            │ │
│ │                 proposal.reuse_agent(matching_agent, subtask)                             │ │
│ │             else:                                                                         │ │
│ │                 proposal.create_agent(subtask.required_type, subtask)                     │ │
│ │                                                                                           │ │
│ │         return proposal                                                                   │ │
│ │                                                                                           │ │
│ │ Phase 4: Inter-Agent Communication                                                        │ │
│ │                                                                                           │ │
│ │ 4.1 Create AgentMessageBus (src/maos/core/agent_message_bus.py)                           │ │
│ │                                                                                           │ │
│ │ class AgentMessageBus:                                                                    │ │
│ │     def __init__(self, db: SqlitePersistence):                                            │ │
│ │         self.db = db                                                                      │ │
│ │         self.active_connections = {}  # agent_id -> process                               │ │
│ │                                                                                           │ │
│ │     async def send_message(self, from_agent: str, to_agent: str, message: str):           │ │
│ │         # Store in database                                                               │ │
│ │         await self.db.save_message(from_agent, to_agent, message)                         │ │
│ │                                                                                           │ │
│ │         # If target agent is active, inject into their context                            │ │
│ │         if to_process := self.active_connections.get(to_agent):                           │ │
│ │             context_update = f"Message from {from_agent}: {message}"                      │ │
│ │             await self._inject_context(to_process, context_update)                        │ │
│ │                                                                                           │ │
│ │     async def broadcast(self, from_agent: str, message: str):                             │ │
│ │         # Send to all other active agents                                                 │ │
│ │         for agent_id, process in self.active_connections.items():                         │ │
│ │             if agent_id != from_agent:                                                    │ │
│ │                 await self.send_message(from_agent, agent_id, message)                    │ │
│ │                                                                                           │ │
│ │ Phase 5: Session Management                                                               │ │
│ │                                                                                           │ │
│ │ 5.1 Create SessionManager (src/maos/core/session_manager.py)                              │ │
│ │                                                                                           │ │
│ │ class SessionManager:                                                                     │ │
│ │     def __init__(self, db: SqlitePersistence):                                            │ │
│ │         self.db = db                                                                      │ │
│ │                                                                                           │ │
│ │     async def create_session(                                                             │ │
│ │         self, agent_id: str, task: str                                                    │ │
│ │     ) -> Tuple[str, str]:  # (process_id, session_id)                                     │ │
│ │         # Spawn Claude with task                                                          │ │
│ │         process_id, session_id = await self.cli_manager.spawn_claude_instance(            │ │
│ │             agent_name=agent_id,                                                          │ │
│ │             task=task                                                                     │ │
│ │         )                                                                                 │ │
│ │                                                                                           │ │
│ │         # Store in database                                                               │ │
│ │         await self.db.execute("""                                                         │ │
│ │             INSERT INTO sessions (session_id, agent_id, created_at)                       │ │
│ │             VALUES (?, ?, ?)                                                              │ │
│ │         """, (session_id, agent_id, datetime.now()))                                      │ │
│ │                                                                                           │ │
│ │         return process_id, session_id                                                     │ │
│ │                                                                                           │ │
│ │     async def resume_session(self, agent_id: str, session_id: str) -> str:                │ │
│ │         # Resume with: claude --resume {session_id} -p "continue"                         │ │
│ │         cmd = [                                                                           │ │
│ │             "claude",                                                                     │ │
│ │             "--resume", session_id,                                                       │ │
│ │             "-p", "Continue your previous task",                                          │ │
│ │             "--output-format", "json"                                                     │ │
│ │         ]                                                                                 │ │
│ │         # ... spawn and track                                                             │ │
│ │                                                                                           │ │
│ │ Phase 6: Orchestrator Brain                                                               │ │
│ │                                                                                           │ │
│ │ 6.1 Create OrchestratorBrain (src/maos/core/orchestrator_brain.py)                        │ │
│ │                                                                                           │ │
│ │ class OrchestratorBrain:                                                                  │ │
│ │     def __init__(self, db: SqlitePersistence):                                            │ │
│ │         self.db = db                                                                      │ │
│ │         self.task_decomposer = TaskDecomposer(db)                                         │ │
│ │         self.session_manager = SessionManager(db)                                         │ │
│ │         self.message_bus = AgentMessageBus(db)                                            │ │
│ │                                                                                           │ │
│ │     async def process_request(self, user_request: str) -> OrchestrationPlan:              │ │
│ │         # 1. Decompose task                                                               │ │
│ │         task_plan = await self.task_decomposer.decompose(user_request)                    │ │
│ │                                                                                           │ │
│ │         # 2. Propose agents                                                               │ │
│ │         agent_proposal = await self.task_decomposer.suggest_agents(task_plan)             │ │
│ │                                                                                           │ │
│ │         # 3. Get user approval                                                            │ │
│ │         if not await self._get_user_approval(agent_proposal):                             │ │
│ │             return None                                                                   │ │
│ │                                                                                           │ │
│ │         # 4. Spawn/reuse agents in parallel                                               │ │
│ │         tasks = []                                                                        │ │
│ │         for agent, subtask in agent_proposal.assignments:                                 │ │
│ │             if agent.needs_creation:                                                      │ │
│ │                 tasks.append(self._create_and_start_agent(agent, subtask))                │ │
│ │             else:                                                                         │ │
│ │                 tasks.append(self._resume_agent(agent, subtask))                          │ │
│ │                                                                                           │ │
│ │         # Execute all in parallel                                                         │ │
│ │         results = await asyncio.gather(*tasks)                                            │ │
│ │                                                                                           │ │
│ │         return OrchestrationPlan(agents=results, task_plan=task_plan)                     │ │
│ │                                                                                           │ │
│ │ Phase 7: Natural Language Interface Update                                                │ │
│ │                                                                                           │ │
│ │ 7.1 Update NaturalLanguageProcessor (src/maos/cli/natural_language.py)                    │ │
│ │                                                                                           │ │
│ │ async def _handle_spawn_swarm(self, input_lower: str, original_input: str):               │ │
│ │     # Extract task                                                                        │ │
│ │     task_description = self._extract_task(original_input)                                 │ │
│ │                                                                                           │ │
│ │     # Use OrchestratorBrain                                                               │ │
│ │     brain = OrchestratorBrain(self.db)                                                    │ │
│ │     plan = await brain.process_request(task_description)                                  │ │
│ │                                                                                           │ │
│ │     # Show agent proposal                                                                 │ │
│ │     self.console.print("[cyan]Proposed agent allocation:[/cyan]")                         │ │
│ │     for agent, subtask in plan.assignments:                                               │ │
│ │         if agent.is_new:                                                                  │ │
│ │             self.console.print(f"  • NEW: {agent.name} → {subtask}")                      │ │
│ │         else:                                                                             │ │
│ │             self.console.print(f"  • REUSE: {agent.name} (session {agent.session_id[:8]}) │ │
│ │  → {subtask}")                                                                            │ │
│ │                                                                                           │ │
│ │     if Confirm.ask("Proceed with this plan?"):                                            │ │
│ │         # Execute in parallel                                                             │ │
│ │         await brain.execute_plan(plan)                                                    │ │
│ │                                                                                           │ │
│ │         # Monitor progress                                                                │ │
│ │         await self._monitor_execution(plan)                                               │ │
│ │                                                                                           │ │
│ │ Phase 8: Save/Restore Implementation                                                      │ │
│ │                                                                                           │ │
│ │ 8.1 Enhanced Checkpoint System                                                            │ │
│ │                                                                                           │ │
│ │ class EnhancedCheckpoint:                                                                 │ │
│ │     async def save(self, name: str):                                                      │ │
│ │         checkpoint_data = {                                                               │ │
│ │             "name": name,                                                                 │ │
│ │             "timestamp": datetime.now(),                                                  │ │
│ │             "orchestrator_state": await self.brain.get_state(),                           │ │
│ │             "active_agents": [],                                                          │ │
│ │             "sessions": {},                                                               │ │
│ │             "tasks": {},                                                                  │ │
│ │             "messages": []                                                                │ │
│ │         }                                                                                 │ │
│ │                                                                                           │ │
│ │         # Get all active agents and their sessions                                        │ │
│ │         agents = await self.db.query("SELECT * FROM agents WHERE status = 'active'")      │ │
│ │         for agent in agents:                                                              │ │
│ │             session = await self.db.query("SELECT * FROM sessions WHERE agent_id = ?",    │ │
│ │ agent.id)                                                                                 │ │
│ │             checkpoint_data["active_agents"].append(agent)                                │ │
│ │             checkpoint_data["sessions"][agent.id] = session                               │ │
│ │                                                                                           │ │
│ │         # Save to database                                                                │ │
│ │         await self.db.save_checkpoint(checkpoint_data)                                    │ │
│ │                                                                                           │ │
│ │     async def restore(self, name: str):                                                   │ │
│ │         checkpoint = await self.db.load_checkpoint(name)                                  │ │
│ │                                                                                           │ │
│ │         # Restore each agent with their session                                           │ │
│ │         tasks = []                                                                        │ │
│ │         for agent in checkpoint["active_agents"]:                                         │ │
│ │             session = checkpoint["sessions"][agent.id]                                    │ │
│ │             tasks.append(self._restore_agent_session(agent, session))                     │ │
│ │                                                                                           │ │
│ │         # Restore all in parallel                                                         │ │
│ │         await asyncio.gather(*tasks)                                                      │ │
│ │                                                                                           │ │
│ │         # Restore orchestrator state                                                      │ │
│ │         await self.brain.restore_state(checkpoint["orchestrator_state"])                  │ │
│ │                                                                                           │ │
│ │ Phase 9: Files to Create/Modify                                                           │ │
│ │                                                                                           │ │
│ │ New Files:                                                                                │ │
│ │                                                                                           │ │
│ │ 1. src/maos/interfaces/sqlite_persistence.py - SQLite backend                             │ │
│ │ 2. src/maos/core/task_decomposer.py - Task breakdown logic                                │ │
│ │ 3. src/maos/core/session_manager.py - Claude session management                           │ │
│ │ 4. src/maos/core/agent_message_bus.py - Inter-agent communication                         │ │
│ │ 5. src/maos/core/orchestrator_brain.py - Central coordination                             │ │
│ │                                                                                           │ │
│ │ Modified Files:                                                                           │ │
│ │                                                                                           │ │
│ │ 1. src/maos/core/claude_cli_manager.py - Add SDK mode execution                           │ │
│ │ 2. src/maos/cli/natural_language.py - Use new orchestration                               │ │
│ │ 3. src/maos/core/orchestrator.py - Integrate all components                               │ │
│ │ 4. pyproject.toml - Add aiosqlite dependency                                              │ │
│ │                                                                                           │ │
│ │ Expected Result:                                                                          │ │
│ │                                                                                           │ │
│ │ User: "implement the PRD"                                                                 │ │
│ │ MAOS: "I'll use these agents:                                                             │ │
│ │   • NEW: architect → Design system architecture                                           │ │
│ │   • NEW: backend-dev → Build API endpoints                                                │ │
│ │   • NEW: frontend-dev → Create UI components                                              │ │
│ │   • REUSE: tester (session abc123) → Write tests                                          │ │
│ │   Proceed? (y/n)"                                                                         │ │
│ │ User: "y"                                                                                 │ │
│ │ MAOS: [Spawns 4 Claude processes in parallel, all working on different parts]             │ │
│ │       [Agents communicate through message bus]                                            │ │
│ │       [Progress tracked in SQLite]                                                        │ │
│ │       [Can save and resume next day with full context]                                    │ │
│ │                                                                                           │ │
│ │ All data stored in single maos.db file with proper relationships!  