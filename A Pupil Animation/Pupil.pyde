# Blink: A Pupil Animation with light
# keys: 1=Calm, 2=Focused, 3=Nervous, G=debug

# --- basic setup ---
W, H = 720, 540        # canvas width and height
cx, cy = W/2, H/2      # center of the eye

EYE_R = 180            # Radius of sclera size
IRIS_R = 95            # Radius of iris size

pupilSize = 30.0       # current pupil size
pupilTarget = 30.0     # where pupil should move to
ease = 0.12            # how fast pupil reacts
t = 0.0                # time seed for noise
noiseSpeed = 0.01      # noise speed

# light stuff
lightPos = PVector(W*0.75, H*0.3)   # light starts top right
lightPower = 120000.0               # brightness of light
falloff = 1400.0                    # makes brightness curve softer
showLight = True

# toggles
showDebug = False
presetName = "Calm"

# presets (min/max pupil + ease/jitter settings)
presets = {
    "Calm":    {"min": 26, "max": 58, "ease": 0.10, "jitter": 0.9},
    "Focused": {"min": 20, "max": 46, "ease": 0.14, "jitter": 0.8},
    "Nervous": {"min": 16, "max": 40, "ease": 0.20, "jitter": 1.4}
}

# start with calm
pmin, pmax, jitter = presets["Calm"]["min"], presets["Calm"]["max"], presets["Calm"]["jitter"]

def setup():
    size(W, H)
    frameRate(60)
    colorMode(HSB, 360, 100, 100, 100)
    noStroke()

def draw():
    global pupilSize, pupilTarget, t
    background(0, 0, 10)  # dark bg

    # figure out brightness based on distance to light
    dx, dy = lightPos.x - cx, lightPos.y - cy
    bright = lightPower / (dx*dx + dy*dy + falloff)
    bright = constrain(bright, 0, 1)

    # map brightness to pupil target size
    t += noiseSpeed
    base = lerp(pmax, pmin, bright)   # brighter light = smaller pupil
    j = map(noise(t), 0, 1, -1.2, 1.2) * jitter
    pupilTarget = constrain(base + j, pmin, pmax)
    pupilSize += (pupilTarget - pupilSize) * ease

    # draw everything
    pushMatrix()
    translate(cx, cy)
    drawSclera()
    drawIris(IRIS_R)
    drawPupil(pupilSize)
    drawHighlight(dx, dy, bright)
    popMatrix()

    if showLight: drawLight()
    if showDebug: drawDebug(bright)

# --- drawing bits ---
def drawSclera():
    fill(0, 0, 100)   # white
    ellipse(0, 0, EYE_R*2, EYE_R*2)

def drawIris(r):
    # quick hack: just draw rings with lerpColor
    for i in range(24, 0, -1):
        rr = r * i/24.0
        col = lerpColor(color(210, 60, 40), color(210, 40, 80), i/24.0)
        fill(col)
        ellipse(0, 0, rr*2, rr*2)

def drawPupil(r):
    fill(0, 0, 0)
    ellipse(0, 0, r*2, r*2)

def drawHighlight(dx, dy, b):
    # highlight roughly opposite the light source
    v = PVector(dx, dy)
    if v.mag() > 0: v.normalize()
    px, py = -v.x*20, -v.y*20
    fill(0, 0, 100, 80); ellipse(px, py, 26+10*b, 18+8*b)
    fill(0, 0, 100, 25); ellipse(px+6, py+4, 46+20*b, 34+12*b)

def drawLight():
    # glow effect around the light point
    noStroke()
    for i in range(12, 0, -1):
        fill(50, 10, 100, map(i,1,12,10,70))
        ellipse(lightPos.x, lightPos.y, i*8, i*8)
    fill(0,0,100); ellipse(lightPos.x, lightPos.y, 10, 10)

def drawDebug(b):
    # simple debug text
    msg = "FPS:%d  Pupil:%.1f/%.1f  Bright:%.2f  Preset:%s" % (
        int(frameRate), pupilSize, pupilTarget, b, presetName)
    fill(0,0,100); textAlign(LEFT, TOP); text(msg, 12, 12)

# --- interactions ---
def mouseDragged():
    # move light with mouse
    lightPos.x, lightPos.y = mouseX, mouseY

def keyPressed():
    global pmin, pmax, ease, jitter, presetName, showDebug, showLight, lightPower
    if key == '1':
        applyPreset("Calm")       # Key 1 → Calm
    elif key == '2':
        applyPreset("Focused")    # Key 2 → Focused
    elif key == '3':
        applyPreset("Nervous")    # Key 3 → Nervous
    elif key in ['g','G']:
        showDebug = not showDebug   # toggle debug info
    elif key in ['l','L']:
        showLight = not showLight   # toggle light visualization
    elif key in ['d','D']:          # D → increase light intensity
        lightPower = min(lightPower*1.15, 240000.0)
    elif key in ['a','A']:          # A → decrease light intensity
        lightPower = max(lightPower/1.15, 40000.0)


def applyPreset(name):
    # load preset settings
    global pmin, pmax, ease, jitter, presetName
    preset = presets[name]
    pmin, pmax = preset["min"], preset["max"]
    ease, jitter = preset["ease"], preset["jitter"]
    presetName = name
