def internal_division(
    x1: float,
    y1: float,
    z1: float,
    x2: float,
    y2: float,
    z2: float,
    m: float,
    n: float,
):
    """
    두 점을 내분하는 점의 좌표를 계산하는 함수

    Parameters:
        m (float): 첫 번째 점에서의 비율
        n (float): 두 번째 점에서의 비율

    Returns:
        tuple: 내분점의 (x, y) 좌표
    """
    x = (m * x2 + n * x1) / (m + n)
    y = (m * y2 + n * y1) / (m + n)
    z = (m * z2 + n * z1) / (m + n)
    return x, y, z
