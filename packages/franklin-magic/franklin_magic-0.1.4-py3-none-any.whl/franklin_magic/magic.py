from IPython.core.magic import register_line_magic
import subprocess

def load_ipython_extension(ipython):
    """This function is called when `%load_ext franklin_magic` is run in IPython."""
    @register_line_magic
    def franklin_install(line):
        package = line.strip()
        if not package:
            print("Usage: %franklin_install <package-name>")
            return
        print(f"Installing Pixi package: {package}")
        try:
            result = subprocess.run(["pixi", "add", package], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Package '{package}' installed successfully.")
            else:
                print(f"Error installing '{package}':\n{result.stderr}")
        except Exception as e:
            print(f"Exception occurred while running pixi: {e}")