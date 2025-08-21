import numpy as np


class LinearMap:
    @staticmethod
    def get_transform_matrix(
        src_points: list[list[float]],
        dst_points: list[list[float]],
    ):
        src = np.array(src_points)
        dst = np.array(dst_points)

        # 4x4 transformation matrix를 구하기 위해 homogeneous 좌표계를 이용
        src_hom = np.hstack((src, np.ones((4, 1))))
        dst_hom = np.hstack((dst, np.ones((4, 1))))

        # Least-squares solution을 이용하여 transformation matrix 계산
        transform_matrix, _ = np.linalg.lstsq(src_hom, dst_hom, rcond=None)[:2]
        return transform_matrix

    @staticmethod
    def transform(
        transform_matrix,
        src_points: list[float],
    ) -> list[float]:
        src = np.array(src_points)

        # homogeneous 좌표계로 변환한 뒤, transformation matrix를 곱함
        new_hom = np.hstack((src, 1))
        transformed_hom = np.dot(new_hom, transform_matrix)

        # homogeneous 좌표계에서 일반 좌표계로 변환
        dst = transformed_hom[:3] / transformed_hom[3]
        dst_points = list(dst)
        return dst_points
