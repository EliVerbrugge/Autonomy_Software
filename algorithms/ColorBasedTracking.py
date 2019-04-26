import numpy as np
import cv2
import time


class ObjectTracker(object):
    def __init__(self):
        self.GREEN_LOWER = np.array((55, 65, 40))
        self.GREEN_UPPER = np.array((135, 150, 85))
        self.MIN_RADIUS = 10
        self.FRAME_RATE = 10
        self.ball_in_frame = None
        self.center = None
        self.radius = 0
        self.firstRun = 0
        # self.circle = np.array([[[375, 52]], [[232, 84]], [[138, 200]], [[162, 337]], [[226, 403]], [[286, 427]],
                                # [[415, 407]], [[475, 359]], [[511, 293]], [[503, 156]], [[453, 90]]])

        # connects cameras, creates file
        try:
            self.camera = cv2.VideoCapture(1)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        except Exception:
            raise Exception("Could not connect to camera")
        pass
        grabbed, self.framebuffer = self.camera.read()
        if not grabbed:
            print("Frame capture failed")

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_filename = "objtracker" + time.strftime("%Y%m%d-%H%M%S") + ".avi" # save videos to unique files.
        # "'logs/objtracker_%s.avi'" % time.strftime("%Y%m%d-%H%M%S") -- logs name, logs created in main
        print(video_filename)
        self.video_out = cv2.VideoWriter(video_filename, fourcc, self.FRAME_RATE, (640, 480))
        assert(self.video_out.isOpened())

    def __del__(self):
        self.camera.release()
        self.video_out.release()

    def track_ball(self):
        self.ball_in_frame = False

        (grabbed, frame) = self.camera.read()

        if grabbed:
            cv2.waitKey(1)
            self.video_out.write(frame) # write raw video frame to the logging file for later analysis in early testing.
        else:
            print("Frame capture failed")

        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        # cv2.imshow("hsv", hsv)
        hsv = cv2.cvtColor(hsv, cv2.COLOR_RGB2HSV)
        # cv2.imshow("hsv", hsv)
        mask = cv2.inRange(hsv, self.GREEN_LOWER, self.GREEN_UPPER)
        # cv2.imshow("mask", mask)
        mask = cv2.erode(mask, None, None, (-1,-1), iterations=2)
        # cv2.imshow("mask", mask)
        mask = cv2.dilate(mask, None, None, (-1,-1),  iterations=2)
        # cv2.imshow("mask", mask)
        contour = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]


        """canny = cv2.Canny(mask, 20, 200)

        cv2.imshow("Canny", canny)

        ball = []
        score = 1

        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
            area = cv2.contourArea(approx)

            if area > 80 and cv2.matchShapes(approx, self.circle, 1, 0.0) < score:
                ball = approx
                score = cv2.matchShapes(approx, self.circle, 1, 0.0)

        if score < 1:
            self.ball_in_frame = True
            cnt = ball
            epsilon = 0.1 * cv2.arcLength(cnt, False)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            cv2.drawContours(canny, approx, -1, (255, 255, 0), 10)

            ((x, y), self.radius) = cv2.minEnclosingCircle(ball)
            M = cv2.moments(ball)
            self.center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            cv2.circle(frame, (int(x), int(y)), int(self.radius), (0, 255, 255), 2)
            cv2.circle(frame, self.center, 5, (0, 0, 255), -1)"""
        radius = 0
        if len(contour) > 0:
            self.ball_in_frame = True
            largest_contour = max(contour, key=cv2.contourArea)
            ((x, y), self.radius) = cv2.minEnclosingCircle(largest_contour)
            radius = self.radius
            M = cv2.moments(largest_contour)
            self.center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        if radius > self.MIN_RADIUS:
            cv2.circle(frame, (int(x), int(y)), int(self.radius), (0, 255, 255), 2)
            cv2.circle(frame, self.center, 5, (0, 0, 255), -1)


            cv2.imshow("Auto", frame)

            # self.video_out.write(frame) # leave this commented for early testing so we can get the raw video feed to run through later for more testing.

            return self.ball_in_frame, self.center, self.radius
        # if not self.firstRun: # using this to pull a sample image to grab RGB values for the tennis ball from gimp.
            # self.firstRun = 1
            # cv2.imwrite('test.png', frame)
        cv2.imshow("Auto", frame)
        return self.ball_in_frame, (0, 0), 0


if __name__ == '__main__':
    tracker = ObjectTracker()
    while True:
        ball_in_frame, center, radius = tracker.track_ball()
        if (ball_in_frame) and (radius > 0) :
            print("Ball found at %s, distance %s" % (center, 1.0/radius))
        else:
            print("No ball found")