'''
cronpan — cron job monitor for humans.

Usage:
  cronpan (start on default port 7878)
  cronpan 9000 (start on port 9000)
  cronpan --port 9000 (same, explicit flag)
  cronpan --install-service (write a systemd service file and print install instructions)
  cronpan --debug (enable Flask debug mode)
  cronpan --help (show this message)
'''

import os
import sys
import shutil
import getpass
import webbrowser
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

DEFAULT_PORT = 7878


def has_display() -> bool:
    '''Return True if a graphical display is available.'''
    if sys.platform == 'darwin':
        return True
    if sys.platform == 'win32':
        return True
    # Linux: check for DISPLAY (X11) or WAYLAND_DISPLAY
    return bool(os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'))


def install_service(port: int):
    '''Write a systemd unit file and print instructions to install it.'''
    cronpan_bin = shutil.which('cronpan')
    if not cronpan_bin:
        cronpan_bin = f'{sys.executable} -m cronpan'

    user = getpass.getuser()
    service_name = 'cronpan'
    service_path = Path(f'/etc/systemd/system/{service_name}.service')
    tmp_path = Path(f'/tmp/{service_name}.service')

    service_content = f'''\
[Unit]
Description=cronpan cron job monitor
After=network.target

[Service]
Type=simple
User={user}
ExecStart={cronpan_bin} --port {port}
Restart=on-failure
RestartSec=5
Environment=HOME={Path.home()}

[Install]
WantedBy=multi-user.target
'''

    tmp_path.write_text(service_content)

    print()
    print('  ┌─ cronpan systemd service ──────────────────────────────┐')
    print(f'  │  Service file written to: {tmp_path}')
    print(f'  │  Will run as user:        {user}')
    print(f'  │  Will listen on port:     {port}')
    print('  └──────────────────────────────────────────────────────────┘')
    print()
    print('  Run these commands to install and start the service:')
    print()
    print(f'    sudo cp {tmp_path} {service_path}')
    print('    sudo systemctl daemon-reload')
    print(f'    sudo systemctl enable {service_name}')
    print(f'    sudo systemctl start {service_name}')
    print()
    print('  To check status:')
    print(f'    sudo systemctl status {service_name}')
    print()
    print('  To stop and remove:')
    print(f'    sudo systemctl stop {service_name}')
    print(f'    sudo systemctl disable {service_name}')
    print(f'    sudo rm {service_path}')
    print()


def main():
    args = sys.argv[1:]

    if '--help' in args or '-h' in args:
        print(__doc__.strip())
        sys.exit(0)

    # Resolve port
    port = DEFAULT_PORT
    if '--port' in args:
        idx = args.index('--port')
        if idx + 1 < len(args):
            try:
                port = int(args[idx + 1])
            except ValueError:
                print(f'  Error: invalid port "{args[idx + 1]}"')
                sys.exit(1)
    else:
        for arg in args:
            if arg.isdigit():
                port = int(arg)
                break

    debug = '--debug' in args

    if '--install-service' in args:
        install_service(port)
        sys.exit(0)

    # Open browser only when a display is available and not inside Docker
    in_docker = Path('/.dockerenv').exists()
    if not in_docker and has_display():
        def open_browser():
            time.sleep(1.2)
            webbrowser.open(f'http://localhost:{port}')
        threading.Thread(target=open_browser, daemon=True).start()
    elif not in_docker and not has_display():
        print(f'  No display detected. Open http://0.0.0.0:{port} from your browser.')

    from cronpan.server import run
    run(port=port, debug=debug)


if __name__ == '__main__':
    main()
