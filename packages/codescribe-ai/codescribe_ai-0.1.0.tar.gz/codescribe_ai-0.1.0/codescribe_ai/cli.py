import argparse
import os
import tempfile
import shutil
from codescribe_ai.scripts.run_pipeline import run_codescribe_pipeline
from codescribe_ai.core.repo_downloader import download_and_extract_repo

def main():
    parser = argparse.ArgumentParser(description="AI-powered README generator")
    parser.add_argument(
        "source",
        help="Path to local project folder or GitHub repo URL"
    )
    parser.add_argument(
        "-o", "--output",
        default="README.md",
        help="Output README file path"
    )
    args = parser.parse_args()

    # Check if source is GitHub URL
    if args.source.startswith("http://") or args.source.startswith("https://"):
        with tempfile.TemporaryDirectory() as tmpdir:
            print(f"Downloading repository {args.source}...")
            repo_path = download_and_extract_repo(args.source, tmpdir)
            run_codescribe_pipeline(repo_path, args.output)
    else:
        # Local folder
        src_path = os.path.abspath(args.source)
        if not os.path.exists(src_path):
            print(f"❌ Path does not exist: {src_path}")
            return
        run_codescribe_pipeline(src_path, args.output)

    print(f"✅ README generated at: {args.output}")

if __name__ == "__main__":
    main()
