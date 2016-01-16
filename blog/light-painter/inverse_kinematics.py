#!/usr/bin/env python3

import math

def inverse_kinematics(end_position, actuator_arm_length, end_arm_length):
    """Computes the angles of the three actuators in a delta robot given the end effector position `end_position`, actuator arm length `actuator_arm_length`, and end arm length `end_arm_length`."""
    # check inputs
    assert len(end_position) == 3, "End effector position must be a 3-tuple of numbers"
    float(end_position[0]), float(end_position[1]), float(end_position[2])
    assert actuator_arm_length > 0, "Actuator arm length must be a positive number"
    assert end_arm_length > 0, "End arm length must be a positive number"

    arm_1 = inverse_solve_actuator(end_position, (1, 0, 0), actuator_arm_length, end_arm_length)
    if arm_1 is None: return None
    arm_2 = inverse_solve_actuator(end_position, (-1 / 2, -math.sqrt(3) / 2, 0), actuator_arm_length, end_arm_length)
    if arm_2 is None: return None
    arm_3 = inverse_solve_actuator(end_position, (-1 / 2, math.sqrt(3) / 2, 0), actuator_arm_length, end_arm_length)
    if arm_3 is None: return None
    return (arm_1, arm_2, arm_3)

def inverse_solve_actuator(end_position, actuator_normal, actuator_arm_length, end_arm_length):
    # compute constants
    x = (end_arm_length ** 2 - actuator_arm_length ** 2 - end_position[0] ** 2 - end_position[1] ** 2 - end_position[2] ** 2) / (2 * actuator_arm_length)
    y = actuator_normal[1] * end_position[0] - actuator_normal[0] * end_position[1]
    z = end_position[2]

    # solve for possible values of sine theta
    determinant = y ** 2 * (y ** 2 + z ** 2 - x ** 2)
    if determinant < 0: # no solution exists
        return None
    denominator = y ** 2 + z ** 2
    if denominator == 0: # arm lock, don't allow moving here to avoid getting stuck
        return None
    sin_theta_A = (-x * z + math.sqrt(determinant)) / denominator
    sin_theta_B = (-x * z - math.sqrt(determinant)) / denominator

    # choose the value that is a solution
    # since we're using floats, we choose the sine theta value with the smaller error
    error_sin_theta_A = abs(x + z * sin_theta_A - y * math.sqrt(1 - sin_theta_A ** 2))
    error_sin_theta_B = abs(x + z * sin_theta_B - y * math.sqrt(1 - sin_theta_B ** 2))
    theta = math.asin(sin_theta_A if error_sin_theta_A < error_sin_theta_B else sin_theta_B)

    # check the solution to make sure it's actually in the envelope
    # since we're using floats, we check if it's close to being a zero
    epsilon = 1e-10
    if abs(y * math.cos(theta) - z * math.sin(theta) - x) > epsilon:
        return None

    # (OPTIONAL) verify that theta actually satisfies the delta robot arm constraints
    #from vectr import Vector # get this from http://anthony-zhang.me/blog/light-painter/vectr.py
    #arm = Vector(actuator_normal[0], actuator_normal[1]).rotated2D(-math.pi / 2)
    #joint = actuator_arm_length * Vector(arm[0] * math.cos(theta), arm[1] * math.cos(theta), math.sin(theta))
    #assert abs((Vector(*actuator_normal) * joint)) < 0.00001, "joint on circle constraint violated for position {}".format(end_position)
    #assert joint.magnitude() - actuator_arm_length < 0.00001, "actuator-joint distance constraint violated for position {}".format(end_position)
    #assert abs((Vector(*end_position) - joint).magnitude() - end_arm_length) < 0.00001, "joint-end effector distance constraint violated for position {}".format(end_position)

    return theta

if __name__ == "__main__":
    # delta robot properties
    ACTUATOR_ARM_LENGTH, END_ARM_LENGTH = 1, math.sqrt(2)

    # actuator angles needed to move the arm to `(0, 0, math.sqrt(3))`
    angles = inverse_kinematics((0, 0, math.sqrt(3)), ACTUATOR_ARM_LENGTH, END_ARM_LENGTH)
    print([math.degrees(x) for x in angles]) # convert radians to degrees for display

    # actuator angles needed to move the arm to `(1, 1, 1)`
    angles = inverse_kinematics((1, 1, 1), ACTUATOR_ARM_LENGTH, END_ARM_LENGTH)
    print([math.degrees(x) for x in angles]) # covnert radians to degrees for display

    # impossible position, returns `None`
    angles = inverse_kinematics((0, -10, 0), ACTUATOR_ARM_LENGTH, END_ARM_LENGTH)
    print(angles)
