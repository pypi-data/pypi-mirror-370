import cv2
import numpy as np


class QrCodeVisualizer:
    def __init__(self, image, expected_modules=None):
        """
        image: OpenCV图像（BGR 或 灰度）
        expected_modules: 若已知二维码模块数（如21、25、29），可指定
        """
        if len(image.shape) == 3:
            self._raw_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif len(image.shape) == 2:
            self._raw_gray = image
        else:
            raise ValueError("图像必须是BGR或灰度格式")

        self._qr_gray = QrCodeVisualizer._extract_qrcode(self._raw_gray)

        self._modules = expected_modules or QrCodeVisualizer._estimate_modules(self._qr_gray)

        self._blocks = QrCodeVisualizer._get_blocks(self._qr_gray, self._modules)

    @staticmethod
    def _extract_qrcode(raw_gray):
        """
        检测二维码四角并进行透视变换，返回标准化并增强后的二维码区域。
        """
        detector = cv2.QRCodeDetector()
        retval, points = detector.detect(raw_gray)
        if not retval or points is None:
            raise ValueError("未能检测到二维码")

        pts = points[0].astype(np.float32)
        side1 = np.linalg.norm(pts[0] - pts[1])
        side2 = np.linalg.norm(pts[1] - pts[2])
        side3 = np.linalg.norm(pts[2] - pts[3])
        side4 = np.linalg.norm(pts[3] - pts[0])
        side = int(np.mean((side1, side2, side3, side4)))

        dst = np.array([[0, 0], [side - 1, 0], [side - 1, side - 1], [0, side - 1]], dtype=np.float32)
        mat = cv2.getPerspectiveTransform(pts, dst)
        qr_gray = cv2.warpPerspective(raw_gray, mat, (side, side))

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        qr_gray = clahe.apply(qr_gray)

        return qr_gray

    @staticmethod
    def _estimate_axis_size(qr_gray, axis):
        """
        计算二维码在指定轴（0=列，1=行）上的模块尺寸。
        """
        means = np.mean(qr_gray, axis=axis)
        diffs = np.abs(np.diff(means))
        threshold = np.mean(diffs) + np.std(diffs)
        significant_diffs = np.where(diffs > threshold)[0]
        if len(significant_diffs) < 2:
            raise ValueError("未能检测到足够的模块边界，可能二维码图像有问题")
        distances = np.diff(significant_diffs)
        return np.median(distances)

    @staticmethod
    def _estimate_modules(qr_gray):
        """
        通过检测行列的差异估算二维码的模块数量。
        """
        height, width = qr_gray.shape
        row_height = QrCodeVisualizer._estimate_axis_size(qr_gray, 1)
        col_width = QrCodeVisualizer._estimate_axis_size(qr_gray, 0)

        rows = round(height / row_height)
        cols = round(width / col_width)

        if rows != cols:
            raise ValueError("行数和列数不匹配，可能二维码图像有问题")

        return int(rows)

    @staticmethod
    def _get_blocks(qr_gray, modules):
        """
        获取二维码布尔数组（True = 黑模块，False = 白模块）
        """
        downsampled = cv2.resize(qr_gray, (modules, modules), interpolation=cv2.INTER_AREA)
        blocks = np.array(downsampled) < 128
        return blocks

    def get_blocks(self):
        """
        返回二维码的布尔数组表示。
        """
        return self._blocks

    def to_string(self, positive_char="██", negative_char="  "):
        self._blocks: np.ndarray
        lines = []
        for row in self._blocks:
            row: np.ndarray
            line = "".join([positive_char if cell else negative_char for cell in row])
            lines.append(line)
        return "\n".join(lines)


if __name__ == "__main__":
    # 测试代码
    img = cv2.imread("ustb-sso-py/qr.png")  # 替换为你的二维码图像路径
    visualizer = QrCodeVisualizer(img)

    print("二维码模块数:", visualizer._modules)
    print("二维码布尔数组:")
    print(visualizer.get_blocks())
    print("二维码字符串表示:")
    print(visualizer.to_string())
