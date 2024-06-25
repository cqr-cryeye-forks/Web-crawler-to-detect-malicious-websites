import argparse
import pathlib
import subprocess
from typing import Final


def run_python_script(script_name, target, output):
    try:
        script_name = f"{script_name}.py"
        if script_name == "crawl.py":
            result = subprocess.run(['python', script_name, "--target", target, "--output", output],
                                    capture_output=True, text=True, check=True)
        # elif script_name == "yara_demo.py":
        #     result = subprocess.run(['python', script_name, "myrule"], capture_output=True, text=True, check=True)
        else:
            result = subprocess.run(['python', script_name, "--target", target, "--output", output],
                                    capture_output=True, text=True, check=True)
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": e.stderr}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Python scripts with a target argument and save the output to a JSON file.")
    parser.add_argument('--target', required=True,
                        help='The target argument to pass to the scripts (e.g., a domain or URL).')
    parser.add_argument('--output', required=True, help='The JSON file to save the output.')

    args = parser.parse_args()

    OUTPUT_JSON: Final[pathlib.Path] = pathlib.Path(__file__).parent / args.output
    # scripts = ['crawl.py', 'yara_demo.py', 'phish.py']
    scripts = ['crawl', 'phish']

    for script in scripts:
        script_output = run_python_script(script, args.target, OUTPUT_JSON)

    print(f"Output has been written to {args.output}")
