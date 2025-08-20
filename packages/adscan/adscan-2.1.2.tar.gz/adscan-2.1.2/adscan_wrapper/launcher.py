import sys
import os
from importlib.resources import files
import shutil

def main():
    # --- PIPX EXECUTION BLOCK ---
    # This is the most reliable way to prevent usage from a pipx environment.
    # We check at runtime, not during the unpredictable installation process.
    # if 'pipx' in sys.prefix:
    #     try:
    #         from rich.console import Console
    #         console = Console(stderr=True)
    #         console.print("[bold red]Error:[/bold red] Running ADscan from a [bold yellow]pipx[/bold yellow] environment is not supported.")
    #         console.print("This tool requires direct system-level access. Please uninstall the pipx version ('pipx uninstall adscan') and install it globally:")
    #         console.print("  [cyan]sudo pip install adscan[/cyan]")
    #     except ImportError:
    #         print("Error: Running ADscan from a pipx environment is not supported.", file=sys.stderr)
    #         print("Please use 'sudo pip install adscan' instead.", file=sys.stderr)
    #     sys.exit(1)
    # # --- END PIPX EXECUTION BLOCK ---

    """
    This is the entry point for the 'adscan' command.
    It locates the bundled PyInstaller executable and runs it.
    """
    # Auto sudo alias insertion for non-root or sudo invocation
    is_sudo = 'SUDO_USER' in os.environ
    if os.geteuid() != 0:
        original_user = os.environ.get('USER')
    elif is_sudo:
        original_user = os.environ.get('SUDO_USER')
    else:
        original_user = None
    if original_user:
        # Determine rcfile path for alias
        home = os.path.expanduser(f'~{original_user}')
        shell = os.environ.get('SHELL', '')
        if 'zsh' in shell:
            rcfile = os.path.join(home, '.zshrc')
        else:
            rcfile = os.path.join(home, '.bash_aliases')
        bin_path = shutil.which('adscan') or sys.argv[0]
        alias_line = f"alias adscan='sudo -E {bin_path}'"
        try:
            existing = ''
            if os.path.exists(rcfile):
                with open(rcfile) as f:
                    existing = f.read()
            if alias_line + '\n' not in existing:
                with open(rcfile, 'a') as f:
                    f.write('\n# ADscan auto-sudo alias\n' + alias_line + '\n')
                print(f"[+] Added sudo-alias to {rcfile}. Restart your shell or run 'source {rcfile}'")
        except Exception as e:
            print(f"[!] Failed to write alias: {e}")
        if os.geteuid() != 0:
            # Relaunch under sudo
            os.execvp('sudo', ['sudo', '-E', bin_path] + sys.argv[1:])
    # Continue normal execution
    executable_path_str = ""
    try:
        # 'files('adscan_wrapper')' returns a path-like object to our package directory.
        # The 'adscan_bundle' is included as package_data, so it's inside this directory.
        executable_path = files('adscan_wrapper') / 'adscan_bundle' / 'adscan'
        executable_path_str = str(executable_path) # For error message

        # On some systems, the executable permission might be lost. Let's ensure it's set.
        if sys.platform != 'win32' and not os.access(executable_path, os.X_OK):
            os.chmod(executable_path, 0o755)

        # Use execv to replace the current python process with the adscan process.
        # This is efficient and correctly passes signals.
        args = [executable_path_str] + sys.argv[1:]
        os.execv(executable_path_str, args)

    except FileNotFoundError:
        print(f"ADScan Launcher Error: The executable was not found at the expected path:", file=sys.stderr)
        # Ensure executable_path_str has a value even if files() failed early
        if not executable_path_str:
             # Try to construct what it would have been for the error message
            try:
                executable_path_str = str(files('adscan_wrapper') / 'adscan_bundle' / 'adscan')
            except:
                executable_path_str = "adscan_wrapper/adscan_bundle/adscan (path construction failed)"
        print(f"Expected: {executable_path_str}", file=sys.stderr)
        print("This may be due to an installation problem or the adscan_bundle not being correctly packaged.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ADScan Launcher Error: An unexpected error occurred.", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        if executable_path_str:
            print(f"Attempted to execute: {executable_path_str}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
