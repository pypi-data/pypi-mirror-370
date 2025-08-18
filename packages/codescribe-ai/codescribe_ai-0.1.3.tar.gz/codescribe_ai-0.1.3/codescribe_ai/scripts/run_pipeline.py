# scripts/run_pipeline.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from core.parser import parse_repo_structure
# from core.tokenizer import chunk_code
# from core.token_manager import TokenManager
# from core.summarizer import summarize_code
# from core.doc_generator import generate_readme
# from core.environment_config import detect_environment
# from core.dependency_parser import extract_all_dependencies
# from core.env_var_parser import extract_env_variables
# from core.usage_instruction_builder import generate_usage_instruction
# from core.formatter import collapse_long_sections
# from core.summarizer import summarize_file_from_chunks
# from core.import_graph import build_import_graph
# from core.call_graph import build_project_call_graph


# # === Config ===
# SOURCE_DIR = "examples/sample_project"
# MAX_TOKENS = 16000  # Global token budget
# OUTPUT_PATH = "docs/README.md"

# # === Setup ===
# token_manager = TokenManager(max_tokens_global=MAX_TOKENS)
# token_manager.set_token_estimator(lambda text: len(text) // 4)  # For Groq-style estimation

# env = detect_environment(SOURCE_DIR)
# dependencies = extract_all_dependencies(SOURCE_DIR)

# summary_dict = {}
# files = parse_repo_structure(SOURCE_DIR)

# env_vars = extract_env_variables(SOURCE_DIR)

# usage = generate_usage_instruction(SOURCE_DIR, environment=env)

# import_graph = build_import_graph(SOURCE_DIR)

# project_call_graph = build_project_call_graph(SOURCE_DIR)


# # === Main Pipeline ===
# print(f"🔍 Scanning source: {SOURCE_DIR}")
# print(f"📦 Detected environment: {env}")
# if dependencies:
#     print("📚 Dependencies found:")
#     for lang, deps in dependencies.items():
#         if deps:
#             print(f"  - {lang}: {', '.join(deps)}")

# for file_path in files:
#     full_path = os.path.join(SOURCE_DIR, file_path)

#     with open(full_path, "r", encoding="utf-8") as f:
#         code = f.read()

#     chunks = chunk_code(code, max_tokens=512)  # chunking
#     all_summaries = []

#     for i, chunk in enumerate(chunks):
#         if not token_manager.can_process(len(chunk) // 4):
#             print(f"⛔ Skipping chunk {i} of {file_path} (token budget exceeded)")
#             continue

#         try:
#             summary = summarize_code(chunk, file_path=file_path, environment=env)
#             token_manager.add_usage(f"{file_path}::chunk_{i}", chunk)
#             all_summaries.append(summary.strip())
#         except Exception as e:
#             print(f"❌ Failed to summarize {file_path} chunk {i}: {e}")
#             continue
    
#     related = import_graph.get(file_path.replace(".py", "").split("/")[-1], [])

#     context_note = f"\n\nThis file depends on: {', '.join(related)}." if related else ""

#     summary_dict[file_path] = summarize_file_from_chunks(
#         all_summaries + ([context_note] if context_note else []),
#         file_path=file_path,
#         environment=env
# )

# summary_dict = collapse_long_sections(summary_dict)

# # === Output ===
# readme_content = generate_readme(summary_dict, dependencies=dependencies,env_vars=env_vars, usage=usage)

# os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
# with open(OUTPUT_PATH, "w", encoding="utf-8") as out:
#     out.write(readme_content)

# print(f"\n✅ README generated at: {OUTPUT_PATH}")
# print(f"📊 Total tokens used: {token_manager.get_total_used()}")




# scripts/run_pipeline.py

import os
from core.parser import parse_repo_structure
from core.tokenizer import chunk_code
from core.token_manager import TokenManager
from core.summarizer import summarize_code, summarize_file_from_chunks
from core.doc_generator import generate_readme
from core.environment_config import detect_environment
from core.dependency_parser import extract_all_dependencies
from core.env_var_parser import extract_env_variables
from core.usage_instruction_builder import generate_usage_instruction
from core.formatter import collapse_long_sections
from core.import_graph import build_import_graph
# from core.call_graph import build_project_call_graph
from core.lang_detector import detect_language_from_extension

def run_codescribe_pipeline(src_dir, output_file):
    """
    Executes the full documentation pipeline on a given code repository.
    """
    token_manager = TokenManager(max_tokens_global=16000)
    token_manager.set_token_estimator(lambda text: len(text) // 4)

    env = detect_environment(src_dir)
    dependencies = extract_all_dependencies(src_dir)
    env_vars = extract_env_variables(src_dir)
    usage = generate_usage_instruction(src_dir, environment=env)

    summary_dict = {}
    files = parse_repo_structure(src_dir)

    import_graph = build_import_graph(src_dir)
    # project_call_graph = build_project_call_graph(src_dir)

    for file_path in files:
        full_path = os.path.join(src_dir, file_path)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            print(f"⚠️ Skipping unreadable file: {file_path} — {e}")
            continue

        lang = detect_language_from_extension(file_path)
        chunks = chunk_code(code, max_tokens=512)
        all_summaries = []

        for i, chunk in enumerate(chunks):
            if not token_manager.can_process(len(chunk) // 4):
                print(f"⛔ Skipping chunk {i} of {file_path} (token budget exceeded)")
                continue
            try:
                summary = summarize_code(chunk, file_path=file_path, environment=env)
                token_manager.add_usage(f"{file_path}::chunk_{i}", chunk)
                all_summaries.append(summary.strip())
            except Exception as e:
                print(f"❌ Failed to summarize {file_path} chunk {i}: {e}")
                continue

        related = import_graph.get(file_path.replace(".py", "").split("/")[-1], [])
        context_note = f"\n\nThis file depends on: {', '.join(related)}." if related else ""

        summary_dict[file_path] = summarize_file_from_chunks(
            all_summaries + ([context_note] if context_note else []),
            file_path=file_path,
            environment=env,
        )

    summary_dict = collapse_long_sections(summary_dict)

    readme_content = generate_readme(
        summary_dict=summary_dict,
        dependencies=dependencies,
        env_vars=env_vars,
        usage=usage,
        environment=env,
        project_name=os.path.basename(src_dir) or "Codebase"
    )

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as out:
        out.write(readme_content)

    print(f"\n✅ README generated at: {output_file}")
    print(f"📊 Total tokens used: {token_manager.get_total_used()}")

if __name__ == "__main__":
    run_codescribe_pipeline("examples/sample_project", "docs/README.md")


# if __name__ == "__main__":
#     SOURCE_DIR = "examples/sample_project"
#     OUTPUT_PATH = "docs/README.md"
    
#     run_codescribe_pipeline(SOURCE_DIR, OUTPUT_PATH)
#     print(f"✅ README generated at: {OUTPUT_PATH}")