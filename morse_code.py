# CS 350 Milestone Three - Input With Buttons
# Red LED (GPIO 18): Morse dots (500 ms)
# Blue LED (GPIO 23): Morse dashes (1500 ms)
# Button (GPIO 24): select the next SOS/OK message
# 16x2 LCD: RS=17, E=27, D4=22, D5=5, D6=6, D7=13
# Adapted from the SNHU Milestone3.py state-machine template.

from threading import Lock, Thread
from time import sleep

import RPi.GPIO as GPIO
from RPLCD.gpio import CharLCD
from gpiozero import Button, LED
from statemachine import State, StateMachine

DEBUG = True


class ManagedDisplay:
    """Handle the 16x2 LCD using the GPIO pins wired in this project."""

    def __init__(self):
        self.lcd = CharLCD(
            numbering_mode=GPIO.BCM,
            cols=16,
            rows=2,
            pin_rs=17,
            pin_e=27,
            pins_data=[22, 5, 6, 13],
            charmap="A00",
        )
        self.lcd.clear()

    def updateScreen(self, message):
        self.lcd.clear()
        self.lcd.write_string("Sending:")
        self.lcd.cursor_pos = (1, 0)
        self.lcd.write_string(message[:16])

    def clear(self):
        self.lcd.clear()

    def cleanupDisplay(self):
        self.lcd.clear()
        self.lcd.close()


class CWMachine(StateMachine):
    """Use state transitions to send Morse code on the two LEDs."""

    message1 = "SOS"
    message2 = "OK"

    # Each symbol or pause returns to the off state when completed.
    off = State(initial=True)
    dot = State()
    dash = State()
    dotDashPause = State()
    letterPause = State()
    wordPause = State()

    doDot = off.to(dot) | dot.to(off)
    doDash = off.to(dash) | dash.to(off)
    doDDP = off.to(dotDashPause) | dotDashPause.to(off)
    doLP = off.to(letterPause) | letterPause.to(off)
    doWP = off.to(wordPause) | wordPause.to(off)

    morseDict = {
        "A" : ".-", "B" : "-...", "C" : "-.-.", "D" : "-..",
        "E" : ".", "F" : "..-.", "G" : "--.", "H" : "....",
        "I" : "..", "J" : ".---", "K" : "-.-", "L" : ".-..",
        "M" : "--", "N" : "-.", "O" : "---", "P" : ".--.",
        "Q" : "--.-", "R" : ".-.", "S" : "...", "T" : "-",
        "U" : "..-", "V" : "...-", "W" : ".--", "X" : "-..-",
        "Y" : "-.--", "Z" : "--..", "0" : "-----", "1" : ".----",
        "2" : "..---", "3" : "...--", "4" : "....-", "5" : ".....",
        "6" : "-....", "7" : "--...", "8" : "---..", "9" : "----.",
        "+" : ".-.-.", "-" : "-....-", "/" : "-..-.", "=" : "-...-",
        ":" : "---...", "." : ".-.-.-", "$" : "...-..-", "?" : "..--..",
        "@" : ".--.-.", "&" : ".-...", "\"" : ".-..-.", "_" : "..--.-",
        "|" : "--...-", "(" : "-.--.-", ")" : "-.--.-"
    }

    def __init__(self):
        super().__init__()
        self.redLight = LED(18)
        self.blueLight = LED(23)
        try:
            self.screen = ManagedDisplay()
        except Exception:
            self.redLight.close()
            self.blueLight.close()
            raise
        self.activeMessage = self.message1
        self._message_lock = Lock()
        self.endTransmission = False
        self.thread = None

    def on_enter_dot(self):
        if DEBUG:
            print("* Red dot (500 ms)")
        # Blocking blink keeps the symbol timed in the transmission thread.
        self.redLight.blink(on_time=0.5, off_time=0, n=1, background=False)

    def on_exit_dot(self):
        self.redLight.off()

    def on_enter_dash(self):
        if DEBUG:
            print("* Blue dash (1500 ms)")
        self.blueLight.blink(on_time=1.5, off_time=0, n=1, background=False)

    def on_exit_dash(self):
        self.blueLight.off()

    def on_enter_dotDashPause(self):
        if DEBUG:
            print("* Between symbols (250 ms)")
        sleep(0.25)

    def on_enter_letterPause(self):
        if DEBUG:
            print("* Between letters (750 ms)")
        sleep(0.75)

    def on_enter_wordPause(self):
        if DEBUG:
            print("* Between words/messages (3000 ms)")
        sleep(3.0)

    def toggleMessage(self):
        # Only select the NEXT message. An ongoing transmission uses
        # a snapshot of the previously selected message.
        with self._message_lock:
            if self.activeMessage == self.message1:
                self.activeMessage = self.message2
            else:
                self.activeMessage = self.message1
            selection = self.activeMessage
        if DEBUG:
            print(f"* Next message: {selection}")

    def processButton(self):
        self.toggleMessage()

    def run(self):
        self.thread = Thread(target=self.transmit, name="MorseTransmit")
        self.thread.start()

    def transmit(self):
        try:
            while not self.endTransmission:
                # Capture at the start so a button press won't interrupt
                # or change the message already being transmitted.
                with self._message_lock:
                    current_message = self.activeMessage

                self.screen.updateScreen(current_message)
                if DEBUG:
                    print(f"Sending: {current_message}")

                words = current_message.upper().split()
                for word_index, word in enumerate(words):
                    for letter_index, char in enumerate(word):
                        morse = self.morseDict.get(char, "")
                        for symbol_index, symbol in enumerate(morse):
                            if symbol == ".":
                                self.doDot()     # off -> dot
                                self.doDot()     # dot -> off
                            elif symbol == "-":
                                self.doDash()    # off -> dash
                                self.doDash()    # dash -> off

                            if symbol_index < len(morse) - 1:
                                self.doDDP()     # off -> dotDashPause
                                self.doDDP()     # dotDashPause -> off

                        if letter_index < len(word) - 1:
                            self.doLP()          # off -> letterPause
                            self.doLP()          # letterPause -> off

                    if word_index < len(words) - 1:
                        self.doWP()              # off -> wordPause
                        self.doWP()              # wordPause -> off

                # Separate repeated messages with a 3-second pause.
                # Ctrl+C waits for the CURRENT message to finish.
                if not self.endTransmission:
                    self.doWP()
                    self.doWP()

        finally:
            self.redLight.off()
            self.blueLight.off()
            self.screen.cleanupDisplay()


def main():
    machine = CWMachine()
    try:
        button = Button(24, pull_up=True, bounce_time=0.1)
    except Exception:
        machine.redLight.close()
        machine.blueLight.close()
        machine.screen.cleanupDisplay()
        raise
    try:
        button.when_pressed = machine.processButton
        machine.run()
        print("Morse code is running. Press the button to choose SOS/OK.")
        print("Press Ctrl+C to stop safely.")
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("Finishing current message and cleaning up...")
    finally:
        machine.endTransmission = True
        # Do not destroy the LCD/GPIO while the transmit thread uses them.
        if machine.thread is not None:
            machine.thread.join()
        button.close()
        machine.redLight.close()
        machine.blueLight.close()
        print("Cleanup complete.")


if __name__ == "__main__":
    main()
