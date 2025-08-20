#!/usr/bin/env python
# update_medicafe.py
# Script Version: 2.0.0 (clean 3-try updater)
# Target environment: Windows XP SP3 + Python 3.4.4 (ASCII-only)

import sys, os, time, subprocess, platform

try:
    import requests
except Exception:
    requests = None

try:
    import pkg_resources
except Exception:
    pkg_resources = None


SCRIPT_NAME = "update_medicafe.py"
SCRIPT_VERSION = "2.0.0"
PACKAGE_NAME = "medicafe"


# ---------- UI helpers (ASCII-only) ----------
def _line(char, width):
    try:
        return char * width
    except Exception:
        return char * 60


def print_banner(title):
    width = 60
    print(_line("=", width))
    print(title)
    print(_line("=", width))


def print_section(title):
    width = 60
    print("\n" + _line("-", width))
    print(title)
    print(_line("-", width))


def print_status(kind, message):
    label = "[{}]".format(kind)
    print("{} {}".format(label, message))


# ---------- Version utilities ----------
def compare_versions(version1, version2):
    try:
        v1_parts = list(map(int, version1.split(".")))
        v2_parts = list(map(int, version2.split(".")))
        return (v1_parts > v2_parts) - (v1_parts < v2_parts)
    except Exception:
        # Fall back to string compare if unexpected formats
        return (version1 > version2) - (version1 < version2)


def get_installed_version(package):
    try:
        proc = subprocess.Popen([sys.executable, '-m', 'pip', 'show', package],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if proc.returncode == 0:
            for line in out.decode().splitlines():
                if line.startswith("Version:"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass

    if pkg_resources:
        try:
            return pkg_resources.get_distribution(package).version
        except Exception:
            return None
    return None


def get_latest_version(package, retries):
    if not requests:
        return None

    headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        'User-Agent': 'MediCafe-Updater/2.0.0'
    }

    last = None
    for attempt in range(1, retries + 1):
        try:
            url = "https://pypi.org/pypi/{}/json?t={}".format(package, int(time.time()))
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            latest = data.get('info', {}).get('version')
            if not latest:
                raise Exception("Malformed PyPI response")

            # Pragmatic double-fetch-if-equal to mitigate CDN staleness
            if last and latest == last:
                return latest
            last = latest
            if attempt == retries:
                return latest
            # If we just fetched same as before and it's equal to current installed, refetch once more quickly
            time.sleep(1)
        except Exception:
            if attempt == retries:
                return None
            time.sleep(1)

    return last


def check_internet_connection():
    if not requests:
        return False
    try:
        requests.get("http://www.google.com", timeout=5)
        return True
    except Exception:
        return False


# ---------- Upgrade logic (3 attempts, minimal delays) ----------
def run_pip_install(args):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    return proc.returncode, out.decode(), err.decode()


def verify_post_install(package, expected_version):
    # Try quick reads with minimal backoff to avoid unnecessary slowness
    for _ in range(3):
        installed = get_installed_version(package)
        if installed:
            # Re-fetch latest once to avoid stale latest
            latest_again = get_latest_version(package, retries=1) or expected_version
            if compare_versions(installed, latest_again) >= 0:
                return True, installed
        time.sleep(1)
    return False, get_installed_version(package)


def upgrade_package(package):
    strategies = [
        ['install', '--upgrade', package, '--no-cache-dir', '--disable-pip-version-check'],
        ['install', '--upgrade', '--force-reinstall', package, '--no-cache-dir', '--disable-pip-version-check'],
        ['install', '--upgrade', '--force-reinstall', '--ignore-installed', '--user', package, '--no-cache-dir', '--disable-pip-version-check']
    ]

    latest_before = get_latest_version(package, retries=2)
    if not latest_before:
        print_status('ERROR', 'Unable to determine latest version from PyPI')
        return False

    for idx, parts in enumerate(strategies):
        attempt = idx + 1
        print_section("Attempt {}/3".format(attempt))
        cmd = [sys.executable, '-m', 'pip'] + parts
        print_status('INFO', 'Running: {} -m pip {}'.format(sys.executable, ' '.join(parts)))
        code, out, err = run_pip_install(cmd)
        if code == 0:
            ok, installed = verify_post_install(package, latest_before)
            if ok:
                print_status('SUCCESS', 'Installed version: {}'.format(installed))
                return True
            else:
                print_status('WARNING', 'Install returned success but version not updated yet{}'.format(
                    '' if not installed else ' (detected {})'.format(installed)))
        else:
            # Show error output concisely
            if err:
                print(err.strip())
            print_status('WARNING', 'pip returned non-zero exit code ({})'.format(code))

    return False


# ---------- Main ----------
def main():
    print_banner("MediCafe Updater ({} v{})".format(SCRIPT_NAME, SCRIPT_VERSION))
    print_status('INFO', 'Python: {}'.format(sys.version.split(" ")[0]))
    print_status('INFO', 'Platform: {}'.format(platform.platform()))

    if not check_internet_connection():
        print_section('Network check')
        print_status('ERROR', 'No internet connection detected')
        sys.exit(1)

    print_section('Environment')
    current = get_installed_version(PACKAGE_NAME)
    if current:
        print_status('INFO', 'Installed {}: {}'.format(PACKAGE_NAME, current))
    else:
        print_status('WARNING', '{} is not currently installed'.format(PACKAGE_NAME))

    latest = get_latest_version(PACKAGE_NAME, retries=3)
    if not latest:
        print_status('ERROR', 'Could not fetch latest version information from PyPI')
        sys.exit(1)
    print_status('INFO', 'Latest {} on PyPI: {}'.format(PACKAGE_NAME, latest))

    if current and compare_versions(latest, current) <= 0:
        print_section('Status')
        print_status('SUCCESS', 'Already up to date')
        sys.exit(0)

    print_section('Upgrade')
    print_status('INFO', 'Upgrading {} to {} (up to 3 attempts)'.format(PACKAGE_NAME, latest))
    success = upgrade_package(PACKAGE_NAME)

    print_section('Result')
    final_version = get_installed_version(PACKAGE_NAME)
    if success:
        print_status('SUCCESS', 'Update completed. {} is now at {}'.format(PACKAGE_NAME, final_version or '(unknown)'))
        print_status('INFO', 'This updater script: v{}'.format(SCRIPT_VERSION))
        sys.exit(0)
    else:
        print_status('ERROR', 'Update failed.')
        if final_version and current and compare_versions(final_version, current) > 0:
            print_status('WARNING', 'Partial success: detected {} after failures'.format(final_version))
        print_status('INFO', 'This updater script: v{}'.format(SCRIPT_VERSION))
        sys.exit(1)


if __name__ == '__main__':
    # Optional quick mode: --check-only prints machine-friendly status
    if len(sys.argv) > 1 and sys.argv[1] == '--check-only':
        if not check_internet_connection():
            print('ERROR')
            sys.exit(1)
        cur = get_installed_version(PACKAGE_NAME)
        lat = get_latest_version(PACKAGE_NAME, retries=2)
        if not cur or not lat:
            print('ERROR')
            sys.exit(1)
        print('UPDATE_AVAILABLE:' + lat if compare_versions(lat, cur) > 0 else 'UP_TO_DATE')
        sys.exit(0)
    main()
