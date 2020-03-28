import svgwrite
import math
from colour import Color
import progressbar

def logistic_map(x_start, r, max_iterations, tolerance):

    fixed_points = {}

    burn_in = max_iterations / 2

    x = x_start
    for i in range(0, max_iterations):
        x = logistic_func(x, r)
        if i > burn_in:
            keys = [*fixed_points]
            if len(keys) == 0:
                fixed_points[x] = 1
            else:
                closest = closest_value(keys, x)
                if equals_under_tolerance(closest, x, tolerance):
                    fixed_points[closest] = fixed_points[closest] + 1
                else:
                    fixed_points[x] = 1

    return fixed_points


def logistic_func(x, r):
    return r*x*(1.0-x)


def equals_under_tolerance(a, b, tol):
    return abs(a-b) <= tol


def closest_value(values, value):
    closest = values[0]
    closest_dist = abs(closest - value)
    for v in values:
        dist = abs(v - value)
        if dist < closest_dist:
            closest = v
            closest_dist = dist

    return closest


def make_svg(name, r_min, r_max, steps, x_start, max_iterations, tolerance, stroke_width, opacity_factor):

    svg = svgwrite.Drawing(name, viewBox=('%f 0 %f %f' % (r_min, r_max, 1)))

    fixed_points_prev = None
    r_prev = 0

    for s in range(0, steps):
        r = r_min + (r_max-r_min) * s / steps
        fixed_points = logistic_map(x_start, r, max_iterations, tolerance)

        if fixed_points_prev is None:
            fixed_points_prev = fixed_points
            continue

        keys = [*fixed_points]
        weight = 0
        for key in keys:
            weight = weight + fixed_points[key]

        keys_prev = [*fixed_points_prev]

        for key in keys:
            fixed_point_strength = fixed_points[key]
            closest = closest_value(keys_prev, key)

            opacity =  min(1.0 , opacity_factor * fixed_point_strength / weight)

            svg.add(svgwrite.shapes.Line(start=[r_prev, 1-closest], end=[r, 1-key], stroke='black', fill='none', stroke_opacity = str(opacity), stroke_width=str(stroke_width)))

        fixed_points_prev = fixed_points
        r_prev = r

    svg.save()


def make_svg_polyline(name, r_min, r_max, steps, x_start, max_iterations, tolerance, stroke_width, opacity):

    svg = svgwrite.Drawing(name, viewBox=('%f 0 %f %f' % (r_min, r_max-r_min, 1)))

    col_0 = Color("black")
    col_1 = Color("red")
    col_2 = Color("purple")
    gradient = list(col_0.range_to(col_1, int(steps / 2))) + list(col_1.range_to(col_2, int(steps / 2)))


    lines_prev = None
    r_prev = 0
    print("creating logistic map")
    for s in progressbar.progressbar(range(0, steps)):
        r = r_min + (r_max-r_min) * s / steps
        fixed_points = logistic_map(x_start, r, max_iterations, tolerance)

        keys = [*fixed_points]
        if lines_prev is None:
            lines_prev = {}
            for key in keys:
                lines_prev[key] = [[rescale_r(r, r_min, r_max, lambda x: math.exp(x)), 1-key]]
            continue

        keys_prev = [*lines_prev]
        lines = {}
        keys_prev_used = {}
        for key in keys:
            closest = closest_value(keys_prev, key)
            keys_prev_used[closest] = True
            line_new = lines_prev[closest].copy()
            line_new.append([rescale_r(r, r_min, r_max, lambda x: math.exp(x)), 1-key])
            lines[key] = line_new

        colour_bin = int(steps * (rescale_r(r, r_min, r_max, lambda x: math.exp(x)) - r_min) / r_max) - 1

        for key in keys_prev:
            if not key in keys_prev_used:
                draw_line(svg, lines_prev[key], 1.0 / len(keys_prev), stroke_width, gradient[colour_bin].hex)

        lines_prev = lines

    keys = [*lines_prev]

    for key in keys:
        draw_line(svg, lines_prev[key], 1.0/len(keys), stroke_width, gradient[steps-1].hex)

    print("writing svg")
    svg.save()

def draw_line(svg, line, weight, stroke_width, col):
    opacity = max(0.1, weight)
    svg.add(svgwrite.shapes.Polyline(line, stroke=col, fill='none', stroke_opacity=str(opacity),
                                     stroke_width=str(stroke_width)))

def rescale_r(r, r_min, r_max, func):
    return r_min + (r_max-r_min) * (func(r - r_min) - func(0)) / (func(r_max - r_min) - func(0))



#print(logistic_map(0.5, 3.9, 1000, 0.001))


make_svg_polyline("log_test_3.svg", 1.0, 4.0, 2000, 0.1, 1000, 0.001, 0.0025, 0.03)

