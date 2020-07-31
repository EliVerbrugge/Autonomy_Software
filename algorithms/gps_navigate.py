import algorithms.geomath as geomath
import algorithms.heading_hold as hh
import core.constants as constants
from core.constants import ApproachState
import math

def get_approach_status(goal, location, start):
    (s_bearing, s_distance) = geomath.haversine(start.lat, start.lon, goal.lat, goal.lon)
    (c_bearing, c_distance) = geomath.haversine(location.lat, location.lon, goal.lat, goal.lon)

    distanceMeters = c_distance * 1000.0
    close_enough = distanceMeters < constants.WAYPOINT_DISTANCE_THRESHOLD

    bearing_diff = (s_bearing - c_bearing) % 360.0
    past_goal = 180 - constants.BEARING_FLIP_THRESHOLD <= bearing_diff <= 180 + constants.BEARING_FLIP_THRESHOLD

    if past_goal:
        print("PAST GOAL!")
        return ApproachState.PAST_GOAL

    if close_enough:
        print("CLOSE ENOUGH!")
        return ApproachState.CLOSE_ENOUGH

    return ApproachState.ON_COURSE


def calculate_move(goal, location, start, drive_board, nav_board, speed):

    (target_heading, target_distance) = geomath.haversine(location.lat, location.lon, goal.lat, goal.lon)
    print(target_distance)
    if target_distance < 0.01:
        speed = 100
    goal_heading = target_heading
    print("Current heading: " + str(nav_board.heading()) + ", Goal:" + str(goal_heading))
    return hh.get_motor_power_from_heading(speed, goal_heading, drive_board, nav_board)


class GPSData:

    def __int__(self, goal, start):
        self.goal = goal
        self.start = start

    def data(self):
        return self.goal, self.start
