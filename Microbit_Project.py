#--SETUP--------------------------------------------------------------------------
valves = [DigitalPin.P8, DigitalPin.P12, DigitalPin.P16]    # List of valve pin objects
sensors = [AnalogPin.P0, AnalogPin.P1, AnalogPin.P2]        # List of sensor pin objects
sensorVal = [0, 0, 0]                                       # List of sensor values
currentShow = 1                                             # The pot currently being displayed on LCD
manualMode = False                                          # Whether the system is in manual mode or not
manualModeTimeElapsed = 0                                   # How many seconds the system has been in manual mode (refreshes after any user input)
manualModeTimeWindow = 10                                   # How many seconds the system can be in manual mode
settingThreshold = False
MAX_VAL = 800
MIN_VAL = 300
THRESHOLD = 430                                             # The value after which the valve will open

# Initialize I2C adress of LCD
makerbit.connect_lcd(39)
makerbit.clear_lcd1602()

# Custom characters for LCD display 
makerbit.lcd_make_character(LcdChar.C1,
    makerbit.lcd_character_pixels("""
        # # # # #
            . . . . .
            # # # # #
            # # # # #
            # # # # #
            # # # # #
            . . . . .
            # # # # #
    """))
makerbit.lcd_make_character(LcdChar.C2,
    makerbit.lcd_character_pixels("""
        # # # # #
            . . . . .
            . . . . .
            . . . . .
            . . . . .
            . . . . .
            . . . . .
            # # # # #
    """))
makerbit.lcd_make_character(LcdChar.C3,
    makerbit.lcd_character_pixels("""
        . . # # #
            . # . . .
            # . # # #
            # . # # #
            # . # # #
            # . # # #
            . # . . .
            . . # # #
    """))
makerbit.lcd_make_character(LcdChar.C4,
    makerbit.lcd_character_pixels("""
        # # # . .
            . . . # .
            . . . . #
            . . . . #
            . . . . #
            . . . . #
            . . . # .
            # # # . .
    """))
makerbit.lcd_make_character(LcdChar.C5,
    makerbit.lcd_character_pixels("""
        # # # . .
            . . . # .
            # # # . #
            # # # . #
            # # # . #
            # # # . #
            . . . # .
            # # # . .
    """))

# List of LCD position (for progress bar display)
lcdPos = [LcdPosition1602.POS17,
    LcdPosition1602.POS18,
    LcdPosition1602.POS19,
    LcdPosition1602.POS20,
    LcdPosition1602.POS21,
    LcdPosition1602.POS22,
    LcdPosition1602.POS23,
    LcdPosition1602.POS24,
    LcdPosition1602.POS25,
    LcdPosition1602.POS26,
    LcdPosition1602.POS27,
    LcdPosition1602.POS28,
    LcdPosition1602.POS29,
    LcdPosition1602.POS30,
    LcdPosition1602.POS31,
    LcdPosition1602.POS32]

#-------------------------------------------------------------------------------------------

#--MAIN-LOOP--------------------------------------------------------------------------------

def on_forever():
    # Update values of sensors
    updatePins()

    if settingThreshold == True:
        setThresholdWindow()
    else:
        if manualMode == False:
            for i in range(len(sensors)):
                # Check moisture, if too low then open valve
                if sensorVal[i] >= THRESHOLD:
                    openValve(i)
                else:
                    closeValve(i)

        #LCD Control
        showStats(currentShow)

basic.forever(on_forever)

#---------------------------------------------------------------------------------------------------------

#-OTHER-FUNCIONS------------------------------------------------------------------------------------------

def updatePins():
    for i in range(len(sensors)):
        sensorVal[i] = pins.analog_read_pin(sensors[i])

def calculatePercent(val):
    return Math.ceil(Math.map(val, MAX_VAL, MIN_VAL, 0, 100))

def setThresholdWindow():
    makerbit.clear_lcd1602()
    makerbit.show_string_on_lcd1602("Set Threshold:", makerbit.position1602(LcdPosition1602.POS1), 16)
    makerbit.show_string_on_lcd1602(str(THRESHOLD) + " (" + str(calculatePercent(THRESHOLD)) + "%)", makerbit.position1602(LcdPosition1602.POS17), 16)

def showStatsDetailed(showNum):
    global manualMode

    percent_val = calculatePercent(sensorVal[showNum-1])
    makerbit.show_string_on_lcd1602("P" + str(showNum), makerbit.position1602(LcdPosition1602.POS1), 2)
    makerbit.show_string_on_lcd1602("" + str(sensorVal[showNum-1]),
        makerbit.position1602(LcdPosition1602.POS4),
        3)
    makerbit.show_string_on_lcd1602(str(percent_val) + "%",
        makerbit.position1602(LcdPosition1602.POS8),
        3)
    progressBar(percent_val)
    if manualMode == True:
        makerbit.show_string_on_lcd1602("MANUAL", makerbit.position1602(LcdPosition1602.POS12), 6)
        
    else:
        makerbit.show_string_on_lcd1602("AUTO", makerbit.position1602(LcdPosition1602.POS12), 4)
        

def showStats(showNum):
    global manualMode

    percent_val = calculatePercent(sensorVal[showNum-1])
    makerbit.show_string_on_lcd1602("Pot" + str(showNum) + ": ", makerbit.position1602(LcdPosition1602.POS1), 6)
    makerbit.show_string_on_lcd1602(str(percent_val) + "% ",
        makerbit.position1602(LcdPosition1602.POS7),
        4)
    progressBar(percent_val)
    if manualMode == True:
        makerbit.show_string_on_lcd1602("Manual", makerbit.position1602(LcdPosition1602.POS11), 6)
    else:
        makerbit.show_string_on_lcd1602("  Auto", makerbit.position1602(LcdPosition1602.POS11), 6)


def progressBar(val: number):
    # First bit of bar
    makerbit.lcd_show_character1602(LcdChar.C3, makerbit.position1602(LcdPosition1602.POS17))
    
    #Middle part of bar
    for j in range(1, 15):
        if j / 16 <= val / 100:
            makerbit.lcd_show_character1602(LcdChar.C1, makerbit.position1602(lcdPos[j]))
        else:
            makerbit.lcd_show_character1602(LcdChar.C2, makerbit.position1602(lcdPos[j]))
    
    # Last bit of bar
    if val >= 100:
        makerbit.lcd_show_character1602(LcdChar.C5, makerbit.position1602(LcdPosition1602.POS32))
    else:
        makerbit.lcd_show_character1602(LcdChar.C4, makerbit.position1602(LcdPosition1602.POS32))


def closeValve(ind: number):
    pins.digital_write_pin(valves[ind], 0)


def openValve(ind: number):
    pins.digital_write_pin(valves[ind], 1)


def showNext():
    if manualMode == False:
        global currentShow
        currentShow += 1
        if currentShow > 3:
            currentShow = 1
loops.every_interval(5000, showNext)

def startManualMode():
    global manualMode
    for i in range(len(sensors)):
        closeValve(i)
    manualMode = True

#--Button-control------------------------------------------------------------

def on_button_pressed_a():
    global currentShow
    global manualMode
    global manualModeTimeElapsed
    global THRESHOLD
    global MIN_VAL

    if settingThreshold:
        THRESHOLD = THRESHOLD - 5
        if THRESHOLD < MIN_VAL:
            THRESHOLD = MIN_VAL
        return

    if manualMode == True:
        currentShow -= 1
        if currentShow < 1:
            currentShow = 3
        manualModeTimeElapsed = 0
    else:
        startManualMode()
input.on_button_pressed(Button.A, on_button_pressed_a)


def on_button_pressed_b():
    global currentShow
    global manualMode
    global manualModeTimeElapsed
    global THRESHOLD
    global MAX_VAL

    if settingThreshold:
        THRESHOLD = THRESHOLD + 5
        if THRESHOLD > MAX_VAL:
            THRESHOLD = MAX_VAL
        return

    if manualMode == True:
        currentShow += 1
        if currentShow > 3:
            currentShow = 1
        manualModeTimeElapsed = 0
    else:
        startManualMode()
input.on_button_pressed(Button.B, on_button_pressed_b)


def on_button_pressed_ab():
    global currentShow
    global manualMode
    global manualModeTimeElapsed
    global settingThreshold

    if manualMode == True:
        openValve(currentShow - 1)
        basic.pause(2000)
        closeValve(currentShow - 1)
        manualModeTimeElapsed = 0
    else:
        if settingThreshold == False:
            settingThreshold = True
        else:
            settingThreshold = False

input.on_button_pressed(Button.AB, on_button_pressed_ab)


def manualModeTimer():
    global manualMode
    global manualModeTimeWindow
    global manualModeTimeElapsed
    if manualMode == True:
        manualModeTimeElapsed = manualModeTimeElapsed + 1
    
    if manualModeTimeElapsed > manualModeTimeWindow:
        manualMode = False
        manualModeTimeElapsed = 0
    
loops.every_interval(1000, manualModeTimer)

#---------------------------------------------------------------------------------------------------------
