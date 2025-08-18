def isin(container, value, _visited=None):
    """
    container: dict, list, tuple, set, or any object
    value: 찾고 싶은 값
    _visited: 내부용, 이미 검사한 객체를 저장
    """
    if _visited is None:
        _visited = set()

    # id(container)로 객체 고유 식별, 순환 방지
    obj_id = id(container)
    if obj_id in _visited:
        return False  # 이미 검사한 객체 → 무시
    _visited.add(obj_id)

    if isinstance(container, dict):
        # 키 검사
        if value in container:
            return True
        # 값 재귀 검사
        return any(isin(v, value, _visited) for v in container.values())

    elif isinstance(container, (list, tuple, set)):
        # 각 원소 재귀 검사
        return any(isin(v, value, _visited) for v in container)

    else:
        # 단일 값 비교
        return container == value