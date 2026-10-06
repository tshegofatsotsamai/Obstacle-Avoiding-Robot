from hub import port
import runloop
import motor
import distance_sensor
import color_sensor
import random

# SETTINGS

FORWARD_SPEED = -350
REVERSE_SPEED = 300

# SMALL steering angles
LEFT = 15
CENTER = 0
RIGHT = 345

STEER_SPEED = 250

OBSTACLE_DISTANCE = 180


async def main():

    # Put steering at center
    await motor.run_to_absolute_position(
        port.A,
        CENTER,
        STEER_SPEED
    )

    current_action = 0
    action_time = 0

    while True:

        # RED FLOOR = STOP

        r, g, b, intensity = color_sensor.rgbi(port.F)

        if r > 50 and r > g * 1.5 and r > b * 1.5:
            motor.stop(port.E)

            await motor.run_to_absolute_position(
                port.A,
                CENTER,
                STEER_SPEED
            )

            await runloop.sleep_ms(100)
            continue

        # READ DISTANCE SENSORS
        # D = LEFT
        # C = RIGHT

        left = distance_sensor.distance(port.D)
        right = distance_sensor.distance(port.C)

        if left == -1:
            left = 999

        if right == -1:
            right = 999

        # OBSTACLE!

        if left < OBSTACLE_DISTANCE or right < OBSTACLE_DISTANCE:

            motor.stop(port.E)

            # Reverse
            await motor.run_for_degrees(
                port.E,
                REVERSE_SPEED,
                300
            )

            # If left is blocked -> go right
            if left < OBSTACLE_DISTANCE and right >= OBSTACLE_DISTANCE:

                await motor.run_to_absolute_position(
                    port.A,
                    RIGHT,
                    STEER_SPEED
                )

            # If right is blocked -> go left
            elif right < OBSTACLE_DISTANCE and left >= OBSTACLE_DISTANCE:

                await motor.run_to_absolute_position(
                    port.A,
                    LEFT,
                    STEER_SPEED
                )

            # Both blocked -> choose a direction
            else:

                if random.randint(0, 1) == 0:
                    await motor.run_to_absolute_position(
                        port.A,
                        LEFT,
                        STEER_SPEED
                    )
                else:
                    await motor.run_to_absolute_position(
                        port.A,
                        RIGHT,
                        STEER_SPEED
                    )

            motor.run(
                port.E,
                FORWARD_SPEED
            )

            # Turn for a short time
            await runloop.sleep_ms(
                random.randint(500, 800)
            )

            await motor.run_to_absolute_position(
                port.A,
                CENTER,
                STEER_SPEED
            )

            action_time = 0

        else:

            # START A NEW WANDERING ACTION

            if action_time <= 0:

                current_action = random.randint(1, 10)

                action_time = random.randint(
                    1000,
                    2200
                )

                if current_action <= 5:

                    # Mostly straight
                    await motor.run_to_absolute_position(
                        port.A,
                        CENTER,
                        STEER_SPEED
                    )

                elif current_action <= 7:

                    # Gentle left
                    await motor.run_to_absolute_position(
                        port.A,
                        LEFT,
                        STEER_SPEED
                    )

                elif current_action <= 9:

                    # Gentle right
                    await motor.run_to_absolute_position(
                        port.A,
                        RIGHT,
                        STEER_SPEED
                    )

                else:

                    # Small reverse
                    motor.stop(port.E)

                    await motor.run_for_degrees(
                        port.E,
                        REVERSE_SPEED,
                        250
                    )

                    await motor.run_to_absolute_position(
                        port.A,
                        CENTER,
                        STEER_SPEED
                    )

            # DRIVE

            if current_action != 10:

                motor.run(
                    port.E,
                    FORWARD_SPEED
                )

            action_time -= 50


        # Check sensors again very soon
        await runloop.sleep_ms(50)


runloop.run(main())