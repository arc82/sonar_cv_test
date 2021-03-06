import cv2
import numpy as np

def show_img(img):
    cv2.imshow('image', img)
    cv2.waitKey(0)

def get_dis_to_line(point, line_pt_1, line_pt_2, img):
    line_pt_1.append(0)
    line_pt_2.append(0)
    point.append(0)
    line_vector = np.array(line_pt_2) - np.array(line_pt_1)
    perp_line = np.cross(line_vector, [0, 0, 1])
    unit_perp_line = perp_line / np.linalg.norm(perp_line)
    dis_to_line = np.dot(unit_perp_line, np.array(line_pt_2) - np.array(point))

    perp_line_with_dis = unit_perp_line * dis_to_line
    cv2.line(img, (point[0], point[1]), (point[0] + int(perp_line_with_dis[0]), point[1] + int(perp_line_with_dis[1])), (255, 0, 0), 2)
    return abs(dis_to_line)

def get_grouped_lines(lines):
    if not(lines is None):
        # Group the nearby lines together (execpecting 3 groups)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret, label, grouped_lines = cv2.kmeans(lines, 3,None,  criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        return grouped_lines
    else:
        print "There were no lines found"
        return []

cap = cv2.VideoCapture('./sonar_vid.avi')

while(cap.isOpened()):

    ret, raw_img = cap.read()

    # Threshold the image
    gray_img = cv2.cvtColor(raw_img, cv2.COLOR_BGR2GRAY)
    ret, thresh_img = cv2.threshold(gray_img, 30, 255, cv2.THRESH_BINARY)


    # Find Hough lines
    
    lines = cv2.HoughLines(thresh_img, 1, np.pi/180, threshold = 30)

    # Draw the submarine on the image
    sub_pos = (int(len(raw_img[0])/2), len(raw_img) - 20)
    cv2.circle(raw_img, sub_pos, 5, (100, 255, 0), -1)



    # Draw the lines on the original image and find the distance to the lines from the submarine

    dis_to_lines = []
    text_pos_counter = 0

    for line in lines:
        line = line[0]
        theta = line[1]
        rho = line[0]
        print "theta: ", theta, " rho: ", rho
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        length = 2000
        x1 = int(x0 + length*(-b))
        y1 = int(y0 + length*(a))
        x2 = int(x0 - length*(-b))
        y2 = int(y0 - length*(a))

        cv2.line(raw_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        dis_to_line = get_dis_to_line([sub_pos[0], sub_pos[1]], [x1, y1], [x2, y2], raw_img)
        print "dis_to_line: ", dis_to_line
        # cv2.putText(raw_img, "Line " + str(text_pos_counter) + " dis: " + str(dis_to_line), (100 , 200 + 100 * text_pos_counter), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
        text_pos_counter += 1



    # cv2.imshow('video',cv2.resize(raw_img, ( int(len(raw_img[0]) * 0.5), int(len(raw_img) * 0.5)) ))
    cv2.imshow('video', raw_img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print "Breaking loop"
        break
cap.release()
cv2.destroyAllWindows()


print "End of program"
