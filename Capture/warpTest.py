import numpy as np
import cv2 as cv


def warp(h, img, name):
    imgReg = cv.warpPerspective(img, h, (400, 300), borderMode=cv.BORDER_CONSTANT)

    text = str(h).replace('[', ' ').replace(']', ' ')
    font = cv.FONT_HERSHEY_PLAIN
    size = 1
    color = (255, 0, 0)
    y0, dy = 30, 15
    for i, line in enumerate(text.split('\n')):
        y = y0 + i * dy
        cv.putText(imgReg, line, (0, y), font, size, color)
    cv.imshow(name, imgReg)
    cv.imwrite("warp/" + name + ".png", imgReg)


if __name__ == '__main__':
    base = np.full((300, 400, 3), (200, 200, 200), np.ubyte)
    base[100:200, 150:250] = np.full((100, 100, 3), (0, 255, 0), np.ubyte)

    cv.imshow("base", base)
    cv.imwrite("warp/base.png", base)

    warp(
        np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]],
            float),
        base,
        "Unitary matrix"
    )

    warp(
        np.array([
            [0.5, 0, 0],
            [0, 1, 0],
            [0, 0, 1]],
            float),
        base,
        "M11eq0_5"
    )

    warp(
        np.array([
            [1, 0, 0],
            [0, 0.5, 0],
            [0, 0, 1]],
            float),
        base,
        "M22eq0_5"
    )

    warp(
        np.array([
            [1, 1, 0],
            [0, 1, 0],
            [0, 0, 1]],
            float),
        base,
        "M12eq1"
    )

    warp(
        np.array([
            [1, 0, 0],
            [1, 1, 0],
            [0, 0, 1]],
            float),
        base,
        "M21eq1"
    )

    warp(
        np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 2]],
            float),
        base,
        "M33eq2"
    )

    warp(
        np.array([
            [1, 0, 200],
            [0, 1, 0],
            [0, 0, 1]],
            float),
        base,
        "M13eq200"
    )

    warp(
        np.array([
            [1, 0, 0],
            [0, 1, 150],
            [0, 0, 1]],
            float),
        base,
        "M23eq150"
    )

    warp(
        np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0.001, 0, 1]],
            float),
        base,
        "M31eq0_001"
    )

    warp(
        np.array([
            [1, 0, 0],
            [0, 1, 0],
            [-0.001, 0, 1]],
            float),
        base,
        "M31eq-0_001"
    )

    warp(
        np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, -0.001, 1]],
            float),
        base,
        "M32eq-0_001"
    )

    warp(
        np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0.001, 1]],
            float),
        base,
        "M32eq0_001"
    )

    warp(
        np.matmul(np.array([
            [0.5, 0, 0],
            [0, 1, 0],
            [0, 0, 1]],
            float),
            np.array([
                [1, 0, 0],
                [0, 0.5, 0],
                [0, 0, 1]],
                float)
        ),
        base,
        "multiplication"
    )

    cv.waitKey(0)
