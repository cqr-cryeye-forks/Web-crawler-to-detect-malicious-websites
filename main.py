import argparse
import ast
import json
import subprocess
import pathlib


def run_python_script(script_name, target):
    try:
        if script_name == "crawl.py":
            result = subprocess.run(['python', script_name, "--target", target], capture_output=True, text=True, check=True)
        elif script_name == "yara_demo.py":
            result = subprocess.run(['python', script_name, "myrule"], capture_output=True, text=True, check=True)
        else:
            result = subprocess.run(['python', script_name, "--target", target], capture_output=True, text=True, check=True)
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": e.stderr}


def parse_dict(output):
    try:
        parsed_dict = ast.literal_eval(output)
        if isinstance(parsed_dict, dict):
            return parsed_dict
        else:
            return None
    except (SyntaxError, ValueError):
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Python scripts with a target argument and save the output to a JSON file.")
    parser.add_argument('--target', required=True, help='The target argument to pass to the scripts (e.g., a domain or URL).')
    parser.add_argument('--output', required=True, help='The JSON file to save the output.')

    args = parser.parse_args()

    OUTPUT: pathlib.Path = pathlib.Path(__file__).parent / args.output

    scripts = ['crawl.py', 'yara_demo.py', 'phish.py']

    all_outputs = {}
    data_list = []

    for script in scripts:
        script_output = run_python_script(script, args.target)
        all_outputs[script] = script_output
        if script == "crawl.py" and all_outputs[script]["status"] == "success":
            all_outputs[script]["output"] = parse_dict(all_outputs[script]["output"])

        if script == "phish.py" and all_outputs[script]["status"] == "success":
            all_outputs[script]["output"] = parse_dict(all_outputs[script]["output"])

    with open(OUTPUT, "w") as jf:
        json.dump(all_outputs, jf, indent=2)

    print(f"Output has been written to {args.output}")
























