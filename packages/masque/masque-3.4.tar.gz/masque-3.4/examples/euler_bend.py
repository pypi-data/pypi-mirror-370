import numpy
from numpy import pi


def centerline(switchover_angle: float):
    theta_max = numpy.sqrt(2 * switchover_angle)

    def gen_curve(theta_max: float):
        xx = []
        yy = []
        for theta in numpy.linspace(0, theta_max, 100):
            qq = numpy.linspace(0, theta, 1000)
            xx.append(numpy.trapz( cos(qq * qq / 2), qq))
            yy.append(numpy.trapz(-sin(qq * qq / 2), qq))
        xy_part = numpy.stack((xx, yy), axis=1)
        return xy_part

    AA = 1
    xy_part = AA * gen_curve(theta_max)
    rmin = AA / theta_max

    xy = [xy_part]
    if switchover_angle < pi / 4:
        half_angle = pi / 4 - switchover_angle
        qq = numpy.linspace(half_angle * 2, 0, 10) + switchover_angle
        xc = rmin * numpy.cos(qq)
        yc = rmin * numpy.sin(qq) + xy_part[-1, 1]
        xc += xy_part[-1, 0] - xc[0]
        yc += xy_part[-1, 1] - yc[0]
        xy.append(numpy.stack((xy, yc), axis=1))

    endpoint_xy = xy[-1][-1, :]
    second_curve = xy_part[:, ::-1] + endpoint_xy - xy_part[-1, ::-1]

    # Remove 2x-duplicate points
    xy = xy[(numpy.circshift(xy, 1, axis=0) != xy).any(axis=1)]

    return xy
