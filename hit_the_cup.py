"""
=====================================================================
  HIT THE CUP!  -  Projectile Motion Simulator
=====================================================================
HOW TO RUN
  Open this file in IDLE or Thonny and press F5 (Run).
  Nothing to install - it only uses Python's built-in turtle module.

TWO MODES (chosen from a pop-up when the program starts)
  1. LAB SIMULATOR
     Pop-up boxes ask for the measurements from the real experiment.
     The simulator predicts where the marble will land, shows the
     flight in slow motion, and tells you where to put the cup.
     After the real launch, type where the marble actually landed and
     the simulator says HIT or MISS and gives your percent error.
  2. TARGET GAME
     The cup moves to a new spot each level (3 levels). Students
     calculate the launch speed that lands the bird in the cup:
         time in air:  t = sqrt(2 x fall height / g)
         speed:        v = distance / t
     Hit it and the bird explodes in a burst of feathers. 3 tries per
     level: 3 points on the first try, 2 on the second, 1 on the third.

  Every distance is in CENTIMETERS. Every time is in SECONDS.
  Each run is also printed in the Shell window so you can copy it
  into a data table.
=====================================================================
"""

import math
import random
import time
import turtle

# ------------------------- TEACHER SETTINGS -------------------------
G = 980.0                  # gravity in cm/s^2
CUP_DIAMETER = 8.0         # width across the top of YOUR cup in cm - measure it!
CUP_PICTURE_HEIGHT = 10    # only used to draw the cup on screen
SLOW_MOTION_SECONDS = 2.5  # how long the on-screen flight takes

# Target game levels: (name, closest cup distance, farthest cup distance, cup-top height)
#   cup-top height None = cup sitting on the floor; a number = cup up on a stool
GAME_LEVELS = [
    ("Cup on the floor", 35, 60, None),
    ("Cup farther away", 70, 120, None),
    ("Cup on a stool", 40, 80, 45),
]
TRIES_PER_LEVEL = 3
# ---------------------------------------------------------------------

WINDOW_W, WINDOW_H = 1100, 700
FLOOR_PX = 75          # pixels of space under the floor for the ruler labels
TEXT_TOP_SHARE = 0.38  # top part of the window kept clear for the text panel

screen = pen = trail = ball = fx = None
view = {}
text_y = 0
run_number = 0


# ===================== window and drawing helpers =====================

def setup_window():
    global screen, pen, trail, ball, fx
    screen = turtle.Screen()
    screen.setup(WINDOW_W, WINDOW_H)
    screen.title("Hit the Cup! - Projectile Motion Simulator")
    screen.bgcolor("#eef6fb")
    screen.tracer(0)
    register_bird()
    pen, trail, ball, fx = turtle.Turtle(), turtle.Turtle(), turtle.Turtle(), turtle.Turtle()
    prep_turtles()
    screen.update()
    cw, ch = canvas_size()
    view.update(xmin=-cw / 2, xmax=cw / 2, ymin=-ch / 2, ymax=ch / 2, wpp=1.0)


# ---------------------- the red bird projectile ----------------------
# Drawn with the bird facing right: X = forward, Y = up (in pixels).

def bird_circle(cx, cy, r, n=18):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n))
            for i in range(n)]


def bird_ellipse(cx, cy, rx, ry, n=16):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n))
            for i in range(n)]


def bird_parts():
    return [
        ([(-9, 3), (-21, 9), (-23, 2), (-20, -5), (-9, -3)], "#9d0208", "#6a040f"),  # tail
        ([(-2, 10), (5, 10), (-4, 17), (-9, 21), (-6, 15)], "#d62828", "#6a040f"),   # crest
        (bird_circle(0, 0, 11.5), "#e5383b", "#6a040f"),                             # body
        (bird_ellipse(-3, -2, 7, 4.5), "#a4161a", "#6a040f"),                        # wing
        (bird_ellipse(9, 1, 4.5, 5.5), "#1b1b1b", "#1b1b1b"),                        # face mask
        ([(10, 4), (19, 0.5), (10, -2.5)], "#f4a261", "#9c4a1a"),                    # beak
        (bird_circle(6.5, 4.5, 2.3, 10), "#ffffff", "#1b1b1b"),                      # eye
        (bird_circle(7.2, 4.5, 1.1, 8), "#000000", "#000000"),                       # pupil
    ]


def register_bird():
    bird = turtle.Shape("compound")
    for points, fill, outline in bird_parts():
        # turtle shapes use their own axes: (x, y) -> (-up, forward)
        bird.addcomponent(tuple((-y, x) for x, y in points), fill, outline)
    screen.register_shape("bird", bird)


def canvas_size():
    w, h = screen.window_width(), screen.window_height()
    if w < 300 or h < 300:          # window not drawn yet - use the planned size
        w, h = WINDOW_W, WINDOW_H
    return w - 20, h - 20


def prep_turtles():
    for t in (pen, trail, ball, fx):
        t.hideturtle()
        t.penup()
        t.speed(0)
    pen.pensize(2)
    ball.shape("bird")
    ball.shapesize(1.1)
    ball.setheading(0)


def set_view(span, scene_top):
    """Pick world coordinates (in cm) so the scene fits with equal x/y scale."""
    cw, ch = canvas_size()
    xmin = -0.35 * span
    width = 1.12 * span - xmin
    scene_px = ch * (1 - TEXT_TOP_SHARE) - FLOOR_PX
    wpp = max(width / cw, (scene_top * 1.08) / scene_px)   # cm per pixel
    mid = xmin + width / 2                    # center the scene left-to-right
    xmin = min(xmin, mid - cw * wpp / 2)
    ymin = -FLOOR_PX * wpp
    ymax = ymin + ch * wpp
    xmax = xmin + cw * wpp
    screen.setworldcoordinates(xmin, ymin, xmax, ymax)
    prep_turtles()
    pen.clear()
    trail.clear()
    fx.clear()
    view.update(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, wpp=wpp)


def move(t, x, y):
    t.penup()
    t.goto(x, y)


def shape(points, fill, outline="#333333"):
    pen.color(outline, fill)
    move(pen, *points[0])
    pen.begin_fill()
    pen.pendown()
    for p in points[1:] + points[:1]:
        pen.goto(p)
    pen.end_fill()
    pen.penup()


def rect(x1, y1, x2, y2, fill, outline="#333333"):
    shape([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], fill, outline)


def line(x1, y1, x2, y2, color="#333333", width=2):
    pen.pensize(width)
    pen.color(color)
    move(pen, x1, y1)
    pen.pendown()
    pen.goto(x2, y2)
    pen.penup()
    pen.pensize(2)


def label(x, y, text, size=12, color="#222222", align="center", bold=False):
    pen.color(color)
    move(pen, x, y)
    pen.write(text, align=align, font=("Arial", size, "bold" if bold else "normal"))


def start_panel():
    global text_y
    text_y = view["ymax"] - 38 * view["wpp"]


def panel(text, size=14, color="#222222", bold=False):
    """Write the next line of the text panel in the top-left corner."""
    global text_y
    label(view["xmin"] + 18 * view["wpp"], text_y, text, size, color, "left", bold)
    text_y -= (size + 13) * view["wpp"]


def center():
    return (view["xmin"] + view["xmax"]) / 2, (view["ymin"] + view["ymax"]) / 2


def show_message(text, color="#d62828"):
    pen.clear()
    trail.clear()
    fx.clear()
    ball.hideturtle()
    cx, cy = center()
    label(cx, cy, text, 18, color, bold=True)
    screen.update()


def nice_step(max_distance):
    raw = max_distance / 10
    for s in (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000):
        if s >= raw:
            return s
    return 2000


# ============================ physics ============================

def predict(v, h, angle_deg, cup_top):
    """Return (landing distance, time in air, vx, vy), or None if the cup can't be reached."""
    a = math.radians(angle_deg)
    vx, vy = v * math.cos(a), v * math.sin(a)
    disc = vy * vy + 2 * G * (h - cup_top)
    if vx <= 0 or disc < 0:
        return None
    t = (vy + math.sqrt(disc)) / G
    if t <= 0:
        return None
    return vx * t, t, vx, vy


# ============================ questions ============================

def ask(title, prompt, default, minval=None, maxval=None):
    value = screen.numinput(title, prompt, default, minval=minval, maxval=maxval)
    if value is None:            # the Cancel button quits
        raise SystemExit
    return value


def get_launch_speed():
    title = "Step 1 of 4: Launch speed"
    method = ask(title,
                 "How did you measure the launch speed?\n\n"
                 "1 = Timed the marble rolling across the desk\n"
                 "2 = Did one practice launch and measured where it landed\n\n"
                 "Type 1 or 2:", 1, 1, 2)
    if round(method) == 1:
        d = ask(title, "How far did the marble roll across the desk? (cm)", 50, 1)
        t = ask(title, "How many seconds did that take?", 0.5, 0.01)
        return d / t, f"{d:g} cm / {t:g} s"
    h = ask(title, "How high was the desk for the PRACTICE launch? (cm)", 76, 1)
    r = ask(title, "How far from the edge of the desk did it land? (cm)\n"
                   "(Measure along the floor.)", 40, 1)
    fall_time = math.sqrt(2 * h / G)
    return r / fall_time, f"practice: {r:g} cm in {fall_time:.3f} s of falling"


# ============================ the scene ============================

def draw_scene(h, angle, x_pred, cup_top, span):
    wpp, xmin, xmax, ymin = view["wpp"], view["xmin"], view["xmax"], view["ymin"]

    # floor and ruler
    rect(xmin, ymin, xmax, 0, "#e3d5b8", "#e3d5b8")
    line(xmin, 0, xmax, 0, "#7f5539", 3)
    step = nice_step(xmax)
    d = 0
    while d <= xmax:
        line(d, 0, d, -8 * wpp, "#7f5539", 2)
        label(d, -28 * wpp, f"{d:g}", 10, "#5c3d2e")
        d += step
    label(xmax - 12 * wpp, -64 * wpp, "distance from the edge of the desk (cm)",
          10, "#5c3d2e", "right")

    # desk
    desk_left = -0.3 * span
    top_th = max(2.0, 7 * wpp)
    leg_w = max(1.5, 6 * wpp)
    rect(-3 * leg_w, 0, -2 * leg_w, h - top_th, "#8b5e34")
    rect(desk_left + leg_w, 0, desk_left + 2 * leg_w, h - top_th, "#8b5e34")
    rect(desk_left, h - top_th, 0, h, "#b07d4f")
    label(-3.6 * leg_w, h / 2, f"{h:g} cm", 11, "#5c3d2e", "right", True)

    if angle == 0:   # ramp on the desk
        ramp_h = max(3.0, min(0.3 * h, 0.1 * span))
        shape([(desk_left + 0.04 * span, h), (-0.1 * span, h),
               (desk_left + 0.04 * span, h + ramp_h)], "#adb5bd")
    else:            # launcher arm for an angled (catapult) launch
        a = math.radians(angle)
        arm = 0.08 * span
        line(-arm * math.cos(a), h - arm * math.sin(a), 0, h, "#495057", 6)

    # stool (if the cup is raised) and cup
    r_top = CUP_DIAMETER / 2
    cup_bottom = max(0.0, cup_top - CUP_PICTURE_HEIGHT)
    if cup_bottom > 0:
        half = stool_half_width()
        rect(x_pred - half, 0, x_pred + half, cup_bottom, "#9c6644")
    shape([(x_pred - 0.75 * r_top, cup_bottom), (x_pred + 0.75 * r_top, cup_bottom),
           (x_pred + r_top, cup_top), (x_pred - r_top, cup_top)], "#ffffff", "#1d3557")


def stool_half_width():
    return max(3 * CUP_DIAMETER, 30 * view["wpp"]) / 2


def fly_path(vx, vy, h, t0, t1, seconds):
    """Move the bird along its path from time t0 to t1. Returns False if it leaves the screen."""
    frames = max(2, int(120 * seconds / SLOW_MOTION_SECONDS))
    for i in range(frames + 1):
        t = t0 + (t1 - t0) * i / frames
        x = vx * t
        y = h + vy * t - 0.5 * G * t * t
        if x > view["xmax"]:
            ball.hideturtle()
            screen.update()
            return False
        ball.goto(x, y)
        ball.setheading(math.degrees(math.atan2(vy - G * t, vx)))   # point along the flight path
        if i % 3 == 0:
            move(trail, x, y)
            trail.dot(5, "#495057")
        screen.update()
        time.sleep(seconds / frames)
    return True


def fly(vx, vy, h, t_flight):
    ball.setheading(0)
    ball.goto(0, h)
    ball.showturtle()
    screen.update()
    time.sleep(0.6)
    return fly_path(vx, vy, h, 0, t_flight, SLOW_MOTION_SECONDS)


# ============================ one launch ============================

def run_once():
    global run_number
    v, how = get_launch_speed()
    h = ask("Step 2 of 4: Launch height",
            "How high is the launch point above the floor for THIS launch? (cm)\n"
            "(Usually the height of the desk top.)", 76, 1)
    angle = ask("Step 3 of 4: Launch angle",
                "Launch angle in degrees.\n"
                "0 = the marble rolls straight off the desk (flat).", 0, -60, 85)
    cup_top = ask("Step 4 of 4: The cup",
                  "How high is the TOP of the cup above the floor? (cm)\n"
                  "Cup sitting on the floor = just the cup's height.", 10, 0)

    result = predict(v, h, angle, cup_top)
    if result is None:
        show_message("The marble can't reach that cup!\n"
                     "The top of the cup is higher than the marble can go.\n"
                     "Lower the cup or raise the launch point.")
        return
    x_pred, t_flight, vx, vy = result
    apex = h + vy * vy / (2 * G) if vy > 0 else h

    set_view(max(1.25 * x_pred, 60), max(apex, h, cup_top))
    draw_scene(h, angle, x_pred, cup_top, max(1.25 * x_pred, 60))
    start_panel()
    panel("HIT THE CUP!", 20, "#1d3557", True)
    panel(f"Launch speed: {v:.1f} cm/s    ({how})")
    panel(f"Launch height: {h:g} cm     Launch angle: {angle:g}\u00b0     Top of cup: {cup_top:g} cm")
    screen.update()

    fly(vx, vy, h, t_flight)

    wpp = view["wpp"]
    green = "#2b9348"
    panel(f"Time in the air: {t_flight:.3f} s")
    panel(f"PREDICTION: put the CENTER of the cup {x_pred:.1f} cm from the edge of the desk",
          16, green, True)
    line(x_pred, 0, x_pred, -10 * wpp, green, 4)
    label(x_pred + CUP_DIAMETER / 2 + 8 * wpp, cup_top, f"{x_pred:.1f} cm", 13, green, "left", True)
    screen.update()

    run_number += 1
    print(f"Run {run_number}: speed {v:.1f} cm/s, height {h:g} cm, angle {angle:g} deg, "
          f"cup top {cup_top:g} cm -> predicted landing {x_pred:.1f} cm, "
          f"time in air {t_flight:.3f} s")

    real = ask("Now try it for real!",
               "Put the cup where the simulator says and launch the marble.\n\n"
               "Where did the marble ACTUALLY land? (cm from the desk edge)\n"
               "Type -1 to skip.", -1, -1)
    if real < 0:
        return

    diff = real - x_pred
    pct = abs(diff) / x_pred * 100
    hit = abs(diff) <= CUP_DIAMETER / 2
    blue = "#1971c2"
    move(pen, real, 0)
    pen.dot(12, blue)
    label(real, -48 * wpp, "real", 10, blue, bold=True)
    panel(f"REAL landing: {real:g} cm  ->  off by {abs(diff):.1f} cm  ({pct:.1f}% error)",
          14, blue, True)
    if hit:
        panel("HIT!", 26, green, True)
    else:
        panel("MISS - too far" if diff > 0 else "MISS - too short", 26, "#d62828", True)
    screen.update()
    print(f"        real landing {real:g} cm, off by {abs(diff):.1f} cm, "
          f"{pct:.1f}% error, {'HIT' if hit else 'MISS'}")


# ============================ target game ============================

def burst(x, y, big=True):
    """Feather explosion for a hit (big=True) or a small dust puff for a miss."""
    ball.hideturtle()
    wpp = view["wpp"]
    if big:
        colors = ["#e5383b", "#d62828", "#9d0208", "#f4a261", "#ffba08", "#ffffff", "#1b1b1b"]
        count, speed, frames = 34, (90, 260), 40
    else:
        colors = ["#b08968", "#ddb892", "#7f5539", "#adb5bd"]
        count, speed, frames = 14, (30, 90), 22
    parts = []
    for _ in range(count):
        a = random.uniform(0, 2 * math.pi)
        s = random.uniform(*speed) * wpp
        parts.append([x, y, s * math.cos(a), s * math.sin(a) + (90 if big else 40) * wpp,
                      random.choice(colors), random.choice((7, 9, 11)) if big else random.choice((4, 6))])
    dt = 1 / 30
    for f in range(frames):
        fx.clear()
        if big and f < 14:                       # flash star that grows and fades
            r = (10 + 6 * f) * wpp
            pts = [(x + (r if k % 2 == 0 else 0.45 * r) * math.cos(math.pi * k / 7 + 0.2),
                    y + (r if k % 2 == 0 else 0.45 * r) * math.sin(math.pi * k / 7 + 0.2))
                   for k in range(14)]
            fx.color("#ffba08" if f < 7 else "#ffe8a3", "#ffba08" if f < 7 else "#ffe8a3")
            move(fx, *pts[0])
            fx.begin_fill()
            for p in pts[1:]:
                fx.goto(p)
            fx.end_fill()
        for p in parts:                          # feathers fly out and fall
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[3] -= 500 * wpp * dt
            move(fx, p[0], p[1])
            fx.dot(max(2, p[5] * (1 - 0.6 * f / frames)), p[4])
        if big and f >= 4:
            move(fx, x, y + 70 * wpp)
            fx.color("#d62828")
            fx.write("BOOM!", align="center", font=("Arial", 30, "bold"))
        screen.update()
        time.sleep(dt)
    fx.clear()
    if big:                                       # a few feathers left floating in the cup
        for k in range(6):
            move(fx, x + random.uniform(-CUP_DIAMETER, CUP_DIAMETER) / 2, y + random.uniform(0, 4) * wpp)
            fx.dot(7, random.choice(colors[:3]))
    screen.update()


def draw_level(level, name, h, cup_x, cup_top, score, attempt, last):
    span = max(1.25 * cup_x, 60)
    set_view(span, max(h, cup_top))
    draw_scene(h, 0, cup_x, cup_top, span)
    wpp = view["wpp"]
    label(cup_x, cup_top + 14 * wpp, f"{cup_x} cm", 12, "#1d3557", bold=True)
    start_panel()
    fall = h - cup_top
    panel(f"TARGET GAME - LEVEL {level} of {len(GAME_LEVELS)}: {name}", 20, "#1d3557", True)
    panel(f"Launch height: {h:g} cm     Top of cup: {cup_top:g} cm     Fall height: {fall:g} cm")
    panel(f"Center of the cup: {cup_x} cm from the edge of the desk     g = 980 cm/s²")
    panel(f"Try {attempt} of {TRIES_PER_LEVEL}     Score: {score}", 14, "#495057", True)
    if last:
        v_last, diff_last = last
        panel(f"Last try: {v_last:g} cm/s  ->  {'too far' if diff_last > 0 else 'too short'} "
              f"by {abs(diff_last):.1f} cm", 14, "#d62828", True)
    screen.update()


def launch_at(v, h, cup_x, cup_top):
    """Fly the bird at speed v (flat launch). Returns (hit, how far off at cup height)."""
    t_cup = math.sqrt(2 * (h - cup_top) / G)
    x_cup = v * t_cup
    diff = x_cup - cup_x
    hit = abs(diff) <= CUP_DIAMETER / 2
    on_screen = fly(v, 0, h, t_cup)
    if hit:
        burst(cup_x, cup_top)
        return True, diff
    if on_screen:                                # keep falling to the stool top or the floor
        cup_bottom = max(0.0, cup_top - CUP_PICTURE_HEIGHT)
        surface = cup_bottom if cup_bottom > 0 and abs(x_cup - cup_x) <= stool_half_width() else 0.0
        t_land = math.sqrt(2 * (h - surface) / G)
        if t_land > t_cup and fly_path(v, 0, h, t_cup, t_land, SLOW_MOTION_SECONDS * (t_land - t_cup) / t_cup):
            burst(v * t_land, surface, big=False)
    return False, diff


def play_game():
    h = ask("Target Game",
            "TARGET GAME\n\nThe cup moves to a new spot each level.\n"
            "Calculate the launch speed that lands the bird in the cup!\n\n"
            "How high is the launch point (desk top) above the floor? (cm)", 76, 20, 300)
    score = 0
    max_score = 3 * len(GAME_LEVELS)
    print(f"\n=== TARGET GAME (launch height {h:g} cm) ===")
    for level, (name, near, far, raised) in enumerate(GAME_LEVELS, 1):
        cup_top = CUP_PICTURE_HEIGHT if raised is None else min(raised, round(0.6 * h))
        cup_x = random.randint(near, far)
        v_needed = cup_x / math.sqrt(2 * (h - cup_top) / G)
        last = None
        guess = 100
        won = False
        for attempt in range(1, TRIES_PER_LEVEL + 1):
            draw_level(level, name, h, cup_x, cup_top, score, attempt, last)
            guess = ask(f"Level {level} - try {attempt} of {TRIES_PER_LEVEL}",
                        f"The cup is {cup_x} cm from the desk. The bird falls {h - cup_top:g} cm.\n\n"
                        "Time in the air:  t = √(2 × fall height ÷ g)\n"
                        "Launch speed:     v = distance ÷ t\n"
                        "(g = 980 cm/s²)\n\n"
                        "What launch speed? (cm/s)", round(guess, 1), 1, 5000)
            hit, diff = launch_at(guess, h, cup_x, cup_top)
            print(f"Level {level}: cup at {cup_x} cm, try {attempt}: {guess:g} cm/s -> "
                  + ("HIT" if hit else f"{'too far' if diff > 0 else 'too short'} by {abs(diff):.1f} cm"))
            if hit:
                points = TRIES_PER_LEVEL + 1 - attempt
                score += points
                panel(f"DIRECT HIT!  +{points} point{'s' if points > 1 else ''}", 24, "#2b9348", True)
                won = True
                break
            panel(f"MISS - {'too far' if diff > 0 else 'too short'} by {abs(diff):.1f} cm",
                  24, "#d62828", True)
            screen.update()
            time.sleep(1.5)
            last = (guess, diff)
        if not won:
            panel(f"Out of tries! The correct speed was {v_needed:.1f} cm/s", 16, "#1d3557", True)
        screen.update()
        if level < len(GAME_LEVELS):
            if screen.textinput("Next level", f"Score so far: {score}\n\nPress OK for level {level + 1}.") is None:
                raise SystemExit
    # final screen
    pen.clear()
    trail.clear()
    fx.clear()
    ball.hideturtle()
    cx, cy = center()
    wpp = view["wpp"]
    stars = 3 if score >= max_score - 1 else 2 if score >= max_score // 2 else 1 if score > 0 else 0
    label(cx, cy + 90 * wpp, "GAME OVER", 34, "#1d3557", bold=True)
    label(cx, cy + 20 * wpp, "★" * stars + "☆" * (3 - stars), 40, "#ffba08", bold=True)
    label(cx, cy - 40 * wpp, f"Score: {score} out of {max_score}", 22, "#222222", bold=True)
    msg = ["Keep practicing - check your fall height and your square root!",
           "Nice work - you're getting the hang of projectile motion.",
           "Great job - solid physics!",
           "PERFECT AIM - physics master!"][stars]
    label(cx, cy - 85 * wpp, msg, 15)
    screen.update()
    print(f"Final score: {score} out of {max_score}")


def welcome():
    cx, cy = center()
    label(cx, cy + 40, "HIT THE CUP!", 36, "#1d3557", bold=True)
    label(cx, cy - 60,
          "LAB SIMULATOR: enter your measurements and predict where the marble lands.\n"
          "TARGET GAME: the cup moves - calculate the speed that lands the bird in it.\n"
          "All distances in centimeters, all times in seconds.", 14)
    screen.update()


def main():
    setup_window()
    welcome()
    try:
        mode = ask("Hit the Cup!", "Choose a mode:\n\n"
                   "1 = Lab simulator (predict where it lands)\n"
                   "2 = Target game (find the speed that hits the cup)\n\n"
                   "Type 1 or 2:", 1, 1, 2)
        while True:
            if round(mode) == 1:
                run_once()
            else:
                play_game()
            mode = ask("What next?", "1 = Lab simulator\n2 = Target game\n0 = Quit", round(mode), 0, 2)
            if round(mode) == 0:
                break
        screen.bye()
    except (SystemExit, turtle.Terminator):
        try:
            screen.bye()
        except Exception:
            pass


if __name__ == "__main__":
    main()
