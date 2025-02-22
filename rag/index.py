from llama_index.core import (
    Document,
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.node_parser import (
    SentenceSplitter,
    CodeSplitter,
    MarkdownNodeParser,
    JSONNodeParser,
)
from llama_index.vector_stores.elasticsearch import ElasticsearchStore
from dotenv import load_dotenv
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.ingestion import IngestionPipeline
import tree_sitter_python as tspython
from tree_sitter_languages import get_parser, get_language
from tree_sitter import Parser, Language
import logging
import nest_asyncio
import elastic_transport
import sys
import subprocess
import shutil
import time
import glob
import os
import re
import argparse


nest_asyncio.apply()

load_dotenv(".env")

Settings.embed_model = HuggingFaceEmbedding(
    model_name="codesage/codesage-small-v2",
    trust_remote_code=True
)
Settings.chunk_lines = 1024
Settings.chunk_size = 1024
Settings.chunk_lines_overlap = 20
Settings.max_chars = 1500



def parse_repo_url(url):
    pattern = r"https?://github\.com/([^/]+)/([^/]+)"
    match = re.match(pattern, url)
    if match:
        owner, repo_name = match.groups()
        repo_name = repo_name.rstrip('.git')
        return owner, repo_name
    raise ValueError(f"Invalid GitHub URL: {url}")

def clone_repository(owner, repo, base_path="/tmp"):
    local_repo_path = os.path.join(base_path, owner, repo)
    clone_url = f"https://github.com/{owner}/{repo}.git"

    if os.path.exists(local_repo_path):
        print(f"Repository already exists at {local_repo_path}. Skipping clone.")
        return local_repo_path

    attempts = 3

    for attempt in range(attempts):
        try:
            os.makedirs(local_repo_path, exist_ok=True)
            print(f"Attempting to clone repository... Attempt {attempt + 1}")
            subprocess.run(
                ["git", "clone", clone_url, local_repo_path], check=True
            )
            print(f"Repository cloned into {local_repo_path}.")
            return local_repo_path
        except subprocess.CalledProcessError:
            print(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(10)
            if attempt < attempts - 1:
                continue
            else:
                raise Exception("Failed to clone repository after multiple attempts")


def print_docs_and_nodes(docs, nodes):
    print("\n=== Documents ===\n")
    for doc in docs:
        print(f"Document ID: {doc.doc_id}")
        print(f"Document Content:\n{doc.text}\n\n---\n")

    print("\n=== Nodes ===\n")
    for node in nodes:
        print(f"Node ID: {node.id_}")
        print(f"Node Content:\n{node.text}\n\branchn---\n")


def collect_and_print_file_summary(file_summary):
    print("\n=== File Summary ===\n")
    for summary in file_summary:
        print(summary)


def parse_documents(args):
    [owner, repo] = parse_repo_url(args.url)
    base_path = os.getenv("BASE_PATH", "/tmp")

    if not owner or not repo:
        raise ValueError(
            "GITHUB_OWNER and GITHUB_REPO environment variables must be set."
        )

    local_repo_path = clone_repository(owner, repo, base_path)

    nodes = []
    file_summary = []

    ts_parser = get_parser("typescript")
    py_parser = get_parser("python")
    go_parser = get_parser("go")
    js_parser = get_parser("javascript")
    bash_parser = get_parser("bash")
    yaml_parser = get_parser("yaml")
    cpp_parser = get_parser("cpp")
    java_parser = get_parser("java")
    c_parser = get_parser("c")
    rust_parser = get_parser("rust")
    php_parser = get_parser("php")
    kotlin_parser = get_parser("kotlin")
    ruby_parser = get_parser("ruby")
    perl_parser = get_parser("perl")
    html_parser = get_parser("html")
    css_parser = get_parser("css")
    sql_parser = get_parser("sql")
    r_parser = get_parser("r")
    lua_parser = get_parser("lua")
    scala_parser = get_parser("scala")

    parsers_and_extensions = [
        (SentenceSplitter(), [".md"]),
        (CodeSplitter(language="python", parser=py_parser), [".py", ".ipynb"]),
        (CodeSplitter(language="typescript", parser=ts_parser), [".ts"]),
        (CodeSplitter(language="go", parser=go_parser), [".go"]),
        (CodeSplitter(language="javascript", parser=js_parser), [".js", ".jsx"]),
        (CodeSplitter(language="bash", parser=bash_parser), [".bash", ".sh"]),
        (CodeSplitter(language="yaml", parser=yaml_parser), [".yaml", ".yml"]),
        (JSONNodeParser(), [".json"]),
        (CodeSplitter(language="cpp", parser=cpp_parser), [".cpp", ".hpp", ".cxx", ".hxx", ".cc", ".hh"]),
        (CodeSplitter(language="java", parser=java_parser), [".java"]),
        (CodeSplitter(language="c", parser=c_parser), [".c", ".h"]),
        (CodeSplitter(language="rust", parser=rust_parser), [".rs"]),
        (CodeSplitter(language="php", parser=php_parser), [".php"]),
        (CodeSplitter(language="kotlin", parser=kotlin_parser), [".kt", ".kts"]),
        (CodeSplitter(language="ruby", parser=ruby_parser), [".rb"]),
        (CodeSplitter(language="perl", parser=perl_parser), [".pl", ".pm"]),
        (CodeSplitter(language="html", parser=html_parser), [".html", ".htm"]),
        (CodeSplitter(language="css", parser=css_parser), [".css"]),
        (CodeSplitter(language="sql", parser=sql_parser), [".sql"]),
        (CodeSplitter(language="r", parser=r_parser), [".r"]),
        (CodeSplitter(language="lua", parser=lua_parser), [".lua"]),
        (CodeSplitter(language="scala", parser=scala_parser), [".scala"]),
    ]
    
    for parser, extensions in parsers_and_extensions:
        matching_files = []
        for ext in extensions:
            matching_files.extend(
                glob.glob(f"{local_repo_path}/**/*{ext}", recursive=True)
            )

        if len(matching_files) > 0:
            extension_list = ", ".join(extensions)
            file_summary.append(
                f"Found {len(matching_files)} {extension_list} files in the repository."
            )

            loader = SimpleDirectoryReader(
                input_dir=local_repo_path, required_exts=extensions, recursive=True
            )
            docs = loader.load_data()
            parsed_nodes = parser.get_nodes_from_documents(docs)

            print_docs_and_nodes(docs, parsed_nodes)

            nodes.extend(parsed_nodes)
        else:
            extension_list = ", ".join(extensions)
            file_summary.append(f"No {extension_list} files found in the repository.")

    collect_and_print_file_summary(file_summary)
    print("\n")
    return nodes


def get_es_vector_store():
    print("Initializing Elasticsearch store...")
    index_name = os.getenv("ELASTIC_INDEX", "default_index")  # Используем значение по умолчанию, если переменная не установлена
    host = os.getenv("ELASTIC_HOST", "localhost")  # Локальный хост для Elasticsearch
    port = os.getenv("ELASTIC_PORT", 9200)         # Порт по умолчанию для Elasticsearch
    elasticsearch_url = f"http://{host}:{port}"
    retries = 20

    for attempt in range(retries):
        try:
            es_vector_store = ElasticsearchStore(
                index_name=index_name,
                es_url=elasticsearch_url,  # Указание URL для Elasticsearch
                batch_size=100,
            )
            print("Elasticsearch store initialized.")
            return es_vector_store
        except elastic_transport.ConnectionTimeout:
            print(f"Connection attempt {attempt + 1}/{retries} timed out. Retrying...")
            time.sleep(10)
    raise Exception("Failed to initialize Elasticsearch store after multiple attempts")


def main():
    cli = argparse.ArgumentParser(description="Run the ingestion pipeline with a specified URL.")
    cli.add_argument("--url", type=str, required=True, help="The URL of the data source")
    args = cli.parse_args()
    nodes = parse_documents(args)
    es_vector_store = get_es_vector_store()

    try:
        pipeline = IngestionPipeline(
            vector_store=es_vector_store,
        )

        pipeline.run(documents=nodes, show_progress=True)
    finally:
        if hasattr(es_vector_store, "close"):
            es_vector_store.close()
        print("Elasticsearch connection closed.")


if __name__ == "__main__":
    main()
