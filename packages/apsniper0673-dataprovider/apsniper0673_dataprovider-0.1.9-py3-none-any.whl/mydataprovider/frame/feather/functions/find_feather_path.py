from pathlib import Path

def find_feather_path() -> Path:
    """
    현재 작업 디렉토리(Path.cwd())부터 시작하여,
    'feather'라는 디렉토리를 포함한 경로를 찾는다.
    현재 디렉토리 → 상위 디렉토리 순으로 반복 탐색.
    루트까지 올라가도 찾지 못하면 FileNotFoundError를 발생시킨다.

    Returns:
        Path: 'feather' 디렉토리의 전체 경로.
    Raises:
        FileNotFoundError: 'feather' 디렉토리를 찾지 못한 경우.
    """
    current = Path.cwd().resolve()

    while True:
        target = current / 'feather'
        if target.exists() and target.is_dir():
            return target

        # 루트까지 올라갔는데도 못 찾으면 예외
        if current.parent == current:
            raise FileNotFoundError("'feather' 디렉토리를 찾을 수 없습니다.")

        # 한 단계 위로 이동
        current = current.parent