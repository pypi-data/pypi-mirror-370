import argparse
import os
import shutil
import tempfile

import pyoverleaf

def get_args():
    parser = argparse.ArgumentParser(description="Package an Overleaf project as an arXiv-compatible zip file")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-p", "--project-id", help="The Overleaf project ID (visible in the URL)")
    group.add_argument("-f", "--file", help="The path to the (already downloaded) Overleaf project zip file")

    parser.add_argument("-s", "--subfolder", help="If specified, build the project in this subfolder of the overleaf project")
    parser.add_argument("out_path", help="The path to save the output zip file")
    return parser.parse_args()

def main():
    args = get_args()

    out_path = os.path.abspath(args.out_path)

    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = os.path.join(temp_dir, "project.zip")
        if args.file:
            shutil.copy(args.file, project_path)
        else:
            api = pyoverleaf.Api()
            api.login_from_browser()
            print("Downloading project...")
            api.download_project(args.project_id, project_path)
            print("Done! Now packaging...")

        cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            os.system("unzip project.zip")
            
            # Use a subfolder within the overleaf project
            subfolder = args.subfolder
            if subfolder:
                if os.path.exists(subfolder) and os.path.isdir(subfolder):
                    os.chdir(subfolder)
                else:
                    raise FileNotFoundError(f"The specified subfolder '{subfolder}' does not exist in the unzipped project")
            
            os.system("pdflatex main.tex")
            os.system("bibtex main")
            os.system("pdflatex main.tex")
            os.system("pdflatex main.tex")
            
            # Delete all .bib files. arXiv only requires the compiled .bbl file
            for root, _, files in os.walk("."):
                for file in files:
                    if file.endswith(".bib"):
                        os.remove(os.path.join(root, file))

            # Delete output file if it already exists
            if os.path.exists(out_path):
                os.remove(out_path)
            
            os.system(f"zip -r {out_path} . -x project.zip main.log main.out main.blg main.aux main.pdf")
        except Exception as e:
            print(e)
        finally:
            os.chdir(cwd)

if __name__ == "__main__":
    main()
