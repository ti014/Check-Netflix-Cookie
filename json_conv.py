import os
import shutil
import json
import random

def get_folder_path():
    if os.name == "posix":
        return "cookies"
    else:
        while True:
            import tkinter
            from tkinter import filedialog

            print("\n<<< Select Netscape cookies folder >>>\n\n")
            tkinter.Tk().withdraw()
            folder_path = filedialog.askdirectory()
            if folder_path == "":
                print("Trying to use default folder 'cookies'\n")
                return "cookies"
            else:
                return folder_path

def process_cookies(source_folder, output_folder):
    for root, _, files in os.walk(source_folder):
        for filename in files:
            filepath = os.path.join(root, filename)
            if filename.endswith(".txt"):
                with open(filepath, "r", encoding="utf-8") as file:
                    content = file.read()

                json_data = json.loads(content)

                output_file = os.path.join(output_folder, f"{filename}.json")
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(json.dumps(json_data, indent=4))
                    print(f"{output_file} - DONE!")

def main():
    folder_path = get_folder_path()
    output_folder = "json_cookies"
    temp_folder = f"temp_{random.randint(1, 99999)}"

    try:
        os.mkdir(output_folder)
        print(f"Folder {output_folder} created!\n")
    except FileExistsError:
        remove_old = input(
            "Do you want to remove old cookies folder? (y/n)\n [y] Recommended \n > : "
        )
        if remove_old.lower() == "y":
            shutil.rmtree(output_folder)
            os.mkdir(output_folder)
        else:
            os.mkdir(temp_folder)

    try:
        process_cookies(folder_path, output_folder)
    except FileNotFoundError:
        print(f"Error Occurred: Default '{folder_path}' folder not found, please select a valid folder")
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
    except Exception as e:
        print(f"Error occurred: {str(e)}")

    if os.path.exists(temp_folder):
        print(f"\n\nSaved cookies to the temp folder - {temp_folder}")
        shutil.rmtree(temp_folder)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram Interrupted by user")
