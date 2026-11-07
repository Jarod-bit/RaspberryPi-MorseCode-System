# Raspberry Pi Morse Code System

A Python-based embedded systems project developed using a Raspberry Pi, GPIO-controlled LEDs, a push button, and a 16x2 LCD display.

The application implements a finite-state machine to transmit Morse code messages, demonstrating hardware/software integration, event-driven programming, multithreading, and embedded system troubleshooting.

## Features

- **Morse Code Transmission:** Transmits SOS and OK using red and blue LEDs.
- **Finite-State Machine:** Controls Morse code symbols and timing through defined states and transitions.
- **Push-Button Input:** Allows the user to switch between messages.
- **LCD Display:** Displays the currently transmitted message.
- **Multithreading:** Runs Morse code transmission on a separate thread.
- **Thread Synchronization:** Uses a lock to protect message selection during button events.
- **Hardware Cleanup:** Releases GPIO and LCD resources during shutdown.

## Technologies Used

- Python 3
- Raspberry Pi
- Raspberry Pi OS / Linux
- GPIO
- RPi.GPIO
- gpiozero
- RPLCD
- python-statemachine
- Python threading

## Hardware Components

- Raspberry Pi
- Breadboard and jumper wires
- Red LED — Morse code dots
- Blue LED — Morse code dashes
- Push button — Message selection
- 16x2 LCD display
- Current-limiting resistors

## GPIO Configuration

| Component | GPIO Pin |
|---|---|
| Red LED | GPIO 18 |
| Blue LED | GPIO 23 |
| Push Button | GPIO 24 |
| LCD RS | GPIO 17 |
| LCD Enable | GPIO 27 |
| LCD D4 | GPIO 22 |
| LCD D5 | GPIO 5 |
| LCD D6 | GPIO 6 |
| LCD D7 | GPIO 13 |

The GPIO assignments correspond to the Python implementation in this repository.

## How the System Works

1. The application initializes the LEDs, LCD, and button.
2. The finite-state machine begins transmitting SOS.
3. Red LED flashes represent dots (500 milliseconds).
4. Blue LED flashes represent dashes (1,500 milliseconds).
5. State transitions control the pauses between symbols, letters, and messages.
6. Pressing the button selects the next message (SOS or OK).
7. The new message begins after the current transmission finishes.
8. The LCD displays the message being transmitted.

## Running the Project

This application requires a compatible Raspberry Pi and connected GPIO hardware.

1. Clone or download the repository onto the Raspberry Pi.
2. Install the required Python libraries for the Raspberry Pi environment.
3. Wire the hardware according to the circuit design.
4. Run `python3 morse_code.py`.
5. Press the push button to switch the selected message.
6. Press Ctrl+C to stop the application safely.

## Engineering Challenges and Solutions

**Hardware Integration**

Configured GPIO connections for LED output, button input, and LCD communication. Troubleshooting hardware connections helped ensure reliable component operation.

**State Machine Implementation**

Implemented a finite-state machine with dedicated states for dots, dashes, and transmission pauses, keeping Morse code behavior organized and predictable.

**Multithreading and Synchronization**

Used Python threading to run transmissions separately from button input handling. Applied a lock to coordinate message selection without altering a transmission already underway.

**Resource Management**

Implemented shutdown logic to finish the current transmission and clean up the LEDs, button, and LCD resources.

## Skills Demonstrated

- Embedded software development
- Python programming
- Linux-based development
- GPIO hardware interfacing
- Finite-state machine design
- Event-driven programming
- Multithreading and synchronization
- Hardware and software debugging
- System testing and troubleshooting

## Future Improvements

- Support additional user-defined Morse code messages.
- Add configurable transmission speeds.
- Improve error reporting and diagnostics.
- Introduce automated tests for Morse code translation and state transitions.
- Expand LCD feedback and user controls.

## Project Background

Developed as part of CS 350: Emerging Systems Architectures & Technologies at Southern New Hampshire University, adapting the provided state-machine starter template and integrating the completed hardware functionality.

## Developer

**Jarod Jecas**

Bachelor of Science in Computer Science — In Progress

Southern New Hampshire University

GitHub: https://github.com/Jarod-bit

## Circuit Diagram

The circuit diagram documents the Raspberry Pi GPIO
connections used for the LEDs, push button, and LCD.

[View the Circuit Diagram](./CS350_Milestone3_State_Machine.drawio%20%281%29.pdf)

