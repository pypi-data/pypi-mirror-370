# src/codegraphcontext/tools/graph_builder.py
import asyncio
import ast
import logging
import os
import importlib
from pathlib import Path
from typing import Any, Coroutine, Dict, Optional, Tuple
from datetime import datetime

from ..core.database import DatabaseManager
from ..core.jobs import JobManager, JobStatus

logger = logging.getLogger(__name__)


def debug_log(message):
    """Write debug message to a file"""
    debug_file = os.path.expanduser("~/mcp_debug.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(debug_file, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
        f.flush()


class CyclomaticComplexityVisitor(ast.NodeVisitor):
    """Calculates cyclomatic complexity for a given AST node."""
    def __init__(self):
        self.complexity = 1

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_With(self, node):
        self.complexity += len(node.items)
        self.generic_visit(node)

    def visit_AsyncFor(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_AsyncWith(self, node):
        self.complexity += len(node.items)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_ListComp(self, node):
        self.complexity += len(node.generators)
        self.generic_visit(node)

    def visit_SetComp(self, node):
        self.complexity += len(node.generators)
        self.generic_visit(node)

    def visit_DictComp(self, node):
        self.complexity += len(node.generators)
        self.generic_visit(node)

    def visit_GeneratorExp(self, node):
        self.complexity += len(node.generators)
        self.generic_visit(node)

    def visit_IfExp(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_match_case(self, node):
        self.complexity += 1
        self.generic_visit(node)


class CodeVisitor(ast.NodeVisitor):
    """Enhanced AST visitor to extract code elements with better function call detection"""

    def __init__(self, file_path: str, is_dependency: bool = False):
        self.file_path = file_path
        self.is_dependency = is_dependency
        self.functions = []
        self.classes = []
        self.variables = []
        self.imports = []
        self.function_calls = []
        self.current_context = None
        self.current_class = None
        self.context_stack = []

    def _push_context(self, name: str, node_type: str, line_number: int):
        """Push a new context onto the stack"""
        self.context_stack.append(
            {
                "name": name,
                "type": node_type,
                "line_number": line_number,
                "previous_context": self.current_context,
                "previous_class": self.current_class,
            }
        )
        self.current_context = name
        if node_type == "class":
            self.current_class = name

    def _pop_context(self):
        """Pop the current context from the stack"""
        if self.context_stack:
            prev_context = self.context_stack.pop()
            self.current_context = prev_context["previous_context"]
            self.current_class = prev_context["previous_class"]

    def visit_FunctionDef(self, node):
        """Visit function definitions"""
        complexity_visitor = CyclomaticComplexityVisitor()
        complexity_visitor.visit(node)
        
        func_data = {
            "name": node.name,
            "line_number": node.lineno,
            "end_line": node.end_lineno if hasattr(node, "end_lineno") else None,
            "args": [arg.arg for arg in node.args.args],
            "source": ast.unparse(node) if hasattr(ast, "unparse") else "",
            "context": self.current_context,
            "class_context": self.current_class,
            "is_dependency": self.is_dependency,
            "docstring": ast.get_docstring(node),
            "decorators": [
                ast.unparse(dec) if hasattr(ast, "unparse") else ""
                for dec in node.decorator_list
            ],
            "cyclomatic_complexity": complexity_visitor.complexity,
        }
        self.functions.append(func_data)
        self._push_context(node.name, "function", node.lineno)
        self.generic_visit(node)
        self._pop_context()

    def visit_AsyncFunctionDef(self, node):
        """Visit async function definitions"""
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):
        """Visit class definitions"""
        class_data = {
            "name": node.name,
            "line_number": node.lineno,
            "end_line": node.end_lineno if hasattr(node, "end_lineno") else None,
            "bases": [
                ast.unparse(base) if hasattr(ast, "unparse") else ""
                for base in node.bases
            ],
            "source": ast.unparse(node) if hasattr(ast, "unparse") else "",
            "context": self.current_context,
            "is_dependency": self.is_dependency,
            "docstring": ast.get_docstring(node),
            "decorators": [
                ast.unparse(dec) if hasattr(ast, "unparse") else ""
                for dec in node.decorator_list
            ],
        }
        self.classes.append(class_data)
        self._push_context(node.name, "class", node.lineno)
        self.generic_visit(node)
        self._pop_context()

    def visit_Assign(self, node):
        """Visit variable assignments"""
        parent_line = None
        if self.context_stack:
            parent_line = self.context_stack[-1].get("line_number")

        for target in node.targets:
            if isinstance(target, ast.Name):
                var_data = {
                    "name": target.id,
                    "line_number": node.lineno,
                    "value": ast.unparse(node.value) if hasattr(ast, "unparse") else "",
                    "context": self.current_context,
                    "class_context": self.current_class,
                    "is_dependency": self.is_dependency,
                    "parent_line": parent_line,
                }
                self.variables.append(var_data)
            elif isinstance(target, ast.Attribute):
                var_data = {
                    "name": target.attr,
                    "line_number": node.lineno,
                    "value": ast.unparse(node.value) if hasattr(ast, "unparse") else "",
                    "context": self.current_context,
                    "class_context": self.current_class,
                    "is_dependency": self.is_dependency,
                    "parent_line": parent_line,
                }
                self.variables.append(var_data)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        """Visit annotated assignments (type hints)"""
        if isinstance(node.target, ast.Name):
            var_data = {
                "name": node.target.id,
                "line_number": node.lineno,
                "value": (
                    ast.unparse(node.value)
                    if node.value and hasattr(ast, "unparse")
                    else ""
                ),
                "context": self.current_context,
                "class_context": self.current_class,
                "is_dependency": self.is_dependency,
            }
            self.variables.append(var_data)
        self.generic_visit(node)

    def visit_Import(self, node):
        """Visit import statements"""
        for name in node.names:
            import_data = {
                "name": name.name,
                "line_number": node.lineno,
                "alias": name.asname,
                "context": self.current_context,
                "is_dependency": self.is_dependency,
            }
            self.imports.append(import_data)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Visit from-import statements"""
        for name in node.names:
            import_data = {
                "name": f"{node.module}.{name.name}" if node.module else name.name,
                "line_number": node.lineno,
                "alias": name.asname,
                "context": self.current_context,
                "is_dependency": self.is_dependency,
            }
            self.imports.append(import_data)
        self.generic_visit(node)

    def visit_Call(self, node):
        """Visit function calls with enhanced detection"""
        call_name = None
        full_call_name = None
        try:
            call_args = [
                ast.unparse(arg) if hasattr(ast, "unparse") else "" for arg in node.args
            ]
        except:
            call_args = []

        if isinstance(node.func, ast.Name):
            call_name = node.func.id
            full_call_name = call_name
        elif isinstance(node.func, ast.Attribute):
            call_name = node.func.attr
            try:
                full_call_name = ast.unparse(node.func)
            except:
                full_call_name = call_name

        if call_name and call_name not in __builtins__:
            call_data = {
                "name": call_name,
                "full_name": full_call_name,
                "line_number": node.lineno,
                "args": call_args,
                "context": self.current_context,
                "class_context": self.current_class,
                "is_dependency": self.is_dependency,
            }
            self.function_calls.append(call_data)
        self.generic_visit(node)


class GraphBuilder:
    """Module for building and managing the Neo4j code graph."""

    def __init__(self, db_manager: DatabaseManager, job_manager: JobManager, loop: asyncio.AbstractEventLoop):
        self.db_manager = db_manager
        self.job_manager = job_manager
        self.loop = loop  # Store the main event loop
        self.driver = self.db_manager.get_driver()
        self.create_schema()

    def create_schema(self):
        """Create constraints and indexes in Neo4j."""
        with self.driver.session() as session:
            try:
                session.run("CREATE CONSTRAINT repository_path IF NOT EXISTS FOR (r:Repository) REQUIRE r.path IS UNIQUE")
                session.run("CREATE CONSTRAINT file_path IF NOT EXISTS FOR (f:File) REQUIRE f.path IS UNIQUE")
                session.run("CREATE CONSTRAINT directory_path IF NOT EXISTS FOR (d:Directory) REQUIRE d.path IS UNIQUE")
                session.run("CREATE CONSTRAINT function_unique IF NOT EXISTS FOR (f:Function) REQUIRE (f.name, f.file_path, f.line_number) IS UNIQUE")
                session.run("CREATE CONSTRAINT class_unique IF NOT EXISTS FOR (c:Class) REQUIRE (c.name, c.file_path, c.line_number) IS UNIQUE")
                session.run("CREATE CONSTRAINT variable_unique IF NOT EXISTS FOR (v:Variable) REQUIRE (v.name, v.file_path, v.line_number) IS UNIQUE")
                session.run("CREATE CONSTRAINT module_name IF NOT EXISTS FOR (m:Module) REQUIRE m.name IS UNIQUE")
                
                # Create a full-text search index for code search
                session.run("""
                    CREATE FULLTEXT INDEX code_search_index IF NOT EXISTS 
                    FOR (n:Function|Class|Variable) 
                    ON EACH [n.name, n.source, n.docstring]
                """)
                
                logger.info("Database schema verified/created successfully")
            except Exception as e:
                logger.warning(f"Schema creation warning: {e}")

    def add_repository_to_graph(self, repo_path: Path, is_dependency: bool = False):
        """Adds a repository node using its absolute path as the unique key."""
        repo_name = repo_path.name
        repo_path_str = str(repo_path.resolve())
        with self.driver.session() as session:
            session.run(
                """
                MERGE (r:Repository {path: $path})
                SET r.name = $name, r.is_dependency = $is_dependency
                """,
                path=repo_path_str,
                name=repo_name,
                is_dependency=is_dependency,
            )

    def add_file_to_graph(self, file_data: Dict, repo_name: str):
        """Adds a file and its contents within a single, unified session."""
        file_path_str = str(Path(file_data['file_path']).resolve())
        file_name = Path(file_path_str).name
        is_dependency = file_data.get('is_dependency', False)

        with self.driver.session() as session:
            try:
                repo_result = session.run("MATCH (r:Repository {name: $repo_name}) RETURN r.path as path", repo_name=repo_name).single()
                relative_path = str(Path(file_path_str).relative_to(Path(repo_result['path']))) if repo_result else file_name
            except ValueError:
                relative_path = file_name

            # Create/Merge the file node
            session.run("""
                MERGE (f:File {path: $path})
                SET f.name = $name, f.relative_path = $relative_path, f.is_dependency = $is_dependency
            """, path=file_path_str, name=file_name, relative_path=relative_path, is_dependency=is_dependency)

            # Create directory structure and link it
            file_path_obj = Path(file_path_str)
            repo_path_obj = Path(repo_result['path'])
            
            relative_path_to_file = file_path_obj.relative_to(repo_path_obj)
            
            parent_path = str(repo_path_obj)
            parent_label = 'Repository'

            # Create nodes for each directory part of the path
            for part in relative_path_to_file.parts[:-1]: # For each directory in the path
                current_path = Path(parent_path) / part
                current_path_str = str(current_path)
                
                session.run(f"""
                    MATCH (p:{parent_label} {{path: $parent_path}})
                    MERGE (d:Directory {{path: $current_path}})
                    SET d.name = $part
                    MERGE (p)-[:CONTAINS]->(d)
                """, parent_path=parent_path, current_path=current_path_str, part=part)

                parent_path = current_path_str
                parent_label = 'Directory'

            # Link the last directory/repository to the file
            session.run(f"""
                MATCH (p:{parent_label} {{path: $parent_path}})
                MATCH (f:File {{path: $file_path}})
                MERGE (p)-[:CONTAINS]->(f)
            """, parent_path=parent_path, file_path=file_path_str)

            for item_data, label in [(file_data['functions'], 'Function'), (file_data['classes'], 'Class'), (file_data['variables'], 'Variable')]:
                for item in item_data:
                    query = f"""
                        MATCH (f:File {{path: $file_path}})
                        MERGE (n:{label} {{name: $name, file_path: $file_path, line_number: $line_number}})
                        SET n += $props
                        MERGE (f)-[:CONTAINS]->(n)
                    """
                    session.run(query, file_path=file_path_str, name=item['name'], line_number=item['line_number'], props=item)

            for imp in file_data['imports']:
                session.run("""
                    MATCH (f:File {path: $file_path})
                    MERGE (m:Module {name: $name})
                    SET m.alias = $alias
                    MERGE (f)-[:IMPORTS]->(m)
                """, file_path=file_path_str, **imp)

            for class_item in file_data.get('classes', []):
                if class_item.get('bases'):
                    for base_class_name in class_item['bases']:
                        session.run("""
                            MATCH (child:Class {name: $child_name, file_path: $file_path})
                            MATCH (parent:Class {name: $parent_name})
                            MERGE (child)-[:INHERITS_FROM]->(parent)
                        """, 
                        child_name=class_item['name'], 
                        file_path=file_path_str, 
                        parent_name=base_class_name)

            self._create_function_calls(session, file_data)
            self._create_class_method_relationships(session, file_data)
            self._create_contextual_relationships(session, file_data)
    
    def _create_contextual_relationships(self, session, file_data: Dict):
        """Create CONTAINS relationships from functions/classes to their children."""
        file_path = str(Path(file_data['file_path']).resolve())
        
        for func in file_data.get('functions', []):
            if func.get('class_context'):
                session.run("""
                    MATCH (c:Class {name: $class_name, file_path: $file_path})
                    MATCH (fn:Function {name: $func_name, file_path: $file_path, line_number: $func_line})
                    MERGE (c)-[:CONTAINS]->(fn)
                """, 
                class_name=func['class_context'],
                file_path=file_path,
                func_name=func['name'],
                func_line=func['line_number'])

        for var in file_data.get('variables', []):
            context = var.get('context')
            parent_line = var.get('parent_line')
            
            if context and parent_line:
                parent_label = "Function"
                parent_node_data = None
                
                for class_data in file_data.get('classes', []):
                    if class_data['name'] == context and class_data['line_number'] == parent_line:
                        parent_label = "Class"
                        parent_node_data = class_data
                        break
                
                if not parent_node_data:
                    for func_data in file_data.get('functions', []):
                        if func_data['name'] == context and func_data['line_number'] == parent_line:
                            parent_label = "Function"
                            parent_node_data = func_data
                            break
                
                if parent_node_data:
                    session.run(f"""
                        MATCH (p:{parent_label} {{name: $parent_name, file_path: $file_path, line_number: $parent_line}})
                        MATCH (v:Variable {{name: $var_name, file_path: $file_path, line_number: $var_line}})
                        MERGE (p)-[:CONTAINS]->(v)
                    """,
                    parent_name=context,
                    file_path=file_path,
                    parent_line=parent_line,
                    var_name=var['name'],
                    var_line=var['line_number'])
            else:
                session.run("""
                    MATCH (f:File {path: $file_path})
                    MATCH (v:Variable {name: $var_name, file_path: $file_path, line_number: $var_line})
                    MERGE (f)-[:CONTAINS]->(v)
                """,
                file_path=file_path,
                var_name=var['name'],
                var_line=var['line_number'])

    def _create_function_calls(self, session, file_data: Dict):
        """Create CALLS relationships between functions based on function_calls data with improved matching"""
        file_path = str(Path(file_data['file_path']).resolve())

        for call in file_data.get('function_calls', []):
            caller_context = call.get('context')
            called_name = call['name']
            full_call_name = call.get('full_name', called_name)
            line_number = call['line_number']
            
            if called_name in ['print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple']:
                continue
                
            if caller_context:
                session.run("""
                    MATCH (caller:Function {name: $caller_name, file_path: $file_path})
                    MATCH (called:Function {name: $called_name})
                    MERGE (caller)-[:CALLS {line_number: $line_number, args: $args, full_call_name: $full_call_name}]->(called)
                """, 
                caller_name=caller_context,
                file_path=file_path,
                called_name=called_name,
                line_number=line_number,
                args=call.get('args', []),
                full_call_name=full_call_name)
                
                if '.' in full_call_name:
                    parts = full_call_name.split('.')
                    if len(parts) >= 2:
                        method_name = parts[-1]
                        
                        session.run("""
                            MATCH (caller:Function {name: $caller_name, file_path: $file_path})
                            MATCH (called:Function {name: $method_name})
                            WHERE called.name = $method_name
                            MERGE (caller)-[:CALLS {line_number: $line_number, args: $args, full_call_name: $full_call_name, call_type: 'method'}]->(called)
                        """, 
                        caller_name=caller_context,
                        file_path=file_path,
                        method_name=method_name,
                        line_number=line_number,
                        args=call.get('args', []),
                        full_call_name=full_call_name)
    
    def _create_class_method_relationships(self, session, file_data: Dict):
        """Create CONTAINS relationships from classes to their methods"""
        file_path = str(Path(file_data['file_path']).resolve())
        
        for func in file_data.get('functions', []):
            class_context = func.get('class_context')
            if class_context:
                session.run("""
                    MATCH (c:Class {name: $class_name, file_path: $file_path})
                    MATCH (fn:Function {name: $func_name, file_path: $file_path, line_number: $func_line})
                    MERGE (c)-[:CONTAINS]->(fn)
                """, 
                class_name=class_context,
                file_path=file_path,
                func_name=func['name'],
                func_line=func['line_number'])
                
    def delete_file_from_graph(self, file_path: str):
        """Deletes a file and all its contained elements and relationships."""
        file_path_str = str(Path(file_path).resolve())
        with self.driver.session() as session:
            # Get parent directories
            parents_res = session.run("""
                MATCH (f:File {path: $path})<-[:CONTAINS*]-(d:Directory)
                RETURN d.path as path ORDER BY length(d.path) DESC
            """, path=file_path_str)
            parent_paths = [record["path"] for record in parents_res]

            # Delete the file and its contents
            session.run(
                """
                MATCH (f:File {path: $path})
                OPTIONAL MATCH (f)-[:CONTAINS]->(element)
                DETACH DELETE f, element
                """,
                path=file_path_str,
            )
            logger.info(f"Deleted file and its elements from graph: {file_path_str}")

            # Clean up empty parent directories, starting from the deepest
            for path in parent_paths:
                session.run("""
                    MATCH (d:Directory {path: $path})
                    WHERE NOT (d)-[:CONTAINS]->()
                    DETACH DELETE d
                """, path=path)

    def delete_repository_from_graph(self, repo_path: str):
        """Deletes a repository and all its contents from the graph."""
        repo_path_str = str(Path(repo_path).resolve())
        with self.driver.session() as session:
            session.run("""
                MATCH (r:Repository {path: $path})
                OPTIONAL MATCH (r)-[:CONTAINS*]->(e)
                DETACH DELETE r, e
            """, path=repo_path_str)
            logger.info(f"Deleted repository and its contents from graph: {repo_path_str}")

    def update_file_in_graph(self, file_path: Path):
        """Updates a file by deleting and re-adding it."""
        file_path_str = str(file_path.resolve())
        repo_name = None
        try:
            with self.driver.session() as session:
                result = session.run(
                    "MATCH (r:Repository)-[:CONTAINS]->(f:File {path: $path}) RETURN r.name as name LIMIT 1",
                    path=file_path_str
                ).single()
                if result:
                    repo_name = result["name"]
        except Exception as e:
            logger.error(f"Failed to find repository for {file_path_str}: {e}")
            return

        if not repo_name:
            logger.warning(f"Could not find repository for {file_path_str}. Aborting update.")
            return

        self.delete_file_from_graph(file_path_str)
        if file_path.exists():
            file_data = self.parse_python_file(file_path)
            if "error" not in file_data:
                self.add_file_to_graph(file_data, repo_name)
            else:
                logger.error(f"Skipping graph add for {file_path_str} due to parsing error: {file_data['error']}")
    
    def parse_python_file(self, file_path: Path, is_dependency: bool = False) -> Dict:
        """Parse a Python file and extract code elements"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
            tree = ast.parse(source_code)
            visitor = CodeVisitor(str(file_path), is_dependency)
            visitor.visit(tree)
            return {
                "file_path": str(file_path),
                "functions": visitor.functions,
                "classes": visitor.classes,
                "variables": visitor.variables,
                "imports": visitor.imports,
                "function_calls": visitor.function_calls,
                "is_dependency": is_dependency,
            }
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return {"file_path": str(file_path), "error": str(e)}

    def estimate_processing_time(self, path: Path) -> Optional[Tuple[int, float]]:
        """Estimate processing time and file count"""
        try:
            if path.is_file():
                files = [path]
            else:
                files = list(path.rglob("*.py"))
            
            total_files = len(files)
            # Simple heuristic: 0.1 seconds per file
            estimated_time = total_files * 0.1
            return total_files, estimated_time
        except Exception as e:
            logger.error(f"Could not estimate processing time for {path}: {e}")
            return None

    async def build_graph_from_path_async(
        self, path: Path, is_dependency: bool = False, job_id: str = None
    ):
        """Builds graph from a directory or file path."""
        try:
            if job_id:
                self.job_manager.update_job(job_id, status=JobStatus.RUNNING)
            
            self.add_repository_to_graph(path, is_dependency)
            repo_name = path.name

            files = list(path.rglob("*.py")) if path.is_dir() else [path]
            if job_id:
                self.job_manager.update_job(job_id, total_files=len(files))

            processed_count = 0
            for file in files:
                if file.is_file():
                    if job_id:
                        self.job_manager.update_job(job_id, current_file=str(file))
                    file_data = self.parse_python_file(file, is_dependency)
                    if "error" not in file_data:
                        self.add_file_to_graph(file_data, repo_name)
                    processed_count += 1
                    if job_id:
                        self.job_manager.update_job(job_id, processed_files=processed_count)
                    await asyncio.sleep(0.01)

            if job_id:
                self.job_manager.update_job(job_id, status=JobStatus.COMPLETED, end_time=datetime.now())
        except Exception as e:
            logger.error(f"Failed to build graph for path {path}: {e}", exc_info=True)
            if job_id:
                self.job_manager.update_job(
                    job_id, status=JobStatus.FAILED, end_time=datetime.now(), errors=[str(e)]
                )

    

    def add_code_to_graph_tool(
        self, path: str, is_dependency: bool = False
    ) -> Dict[str, Any]:
        """Tool to add code to Neo4j graph with background processing"""
        try:
            path_obj = Path(path).resolve()
            if not path_obj.exists():
                return {"error": f"Path {path} does not exist"}

            estimation = self.estimate_processing_time(path_obj)
            if estimation is None:
                return {"error": f"Could not analyze path {path}."}
            total_files, estimated_time = estimation

            job_id = self.job_manager.create_job(str(path_obj), is_dependency)
            self.job_manager.update_job(
                job_id, total_files=total_files, estimated_duration=estimated_time
            )

            # Create the coroutine for the background task
            coro = self.build_graph_from_path_async(path_obj, is_dependency, job_id)
            
            # Safely schedule the coroutine to run on the main event loop from this thread
            asyncio.run_coroutine_threadsafe(coro, self.loop)

            debug_log(f"Started background job {job_id} for path: {str(path_obj)}")

            return {
                "success": True,
                "job_id": job_id,
                "message": f"Background processing started for {path_obj}",
                "estimated_files": total_files,
                "estimated_duration_seconds": round(estimated_time, 2),
            }
        except Exception as e:
            debug_log(f"Error creating background job: {str(e)}")
            return {
                "error": f"Failed to start background processing: {e.__class__.__name__}: {e}"
            }

    def add_package_to_graph_tool(
        self, package_name: str, is_dependency: bool = True
    ) -> Dict[str, Any]:
        """Tool to add a Python package to Neo4j graph"""
        package_path = self.get_local_package_path(package_name)
        if not package_path:
            return {"error": f"Could not find package '{package_name}'."}
        return self.add_code_to_graph_tool(path=package_path, is_dependency=is_dependency)