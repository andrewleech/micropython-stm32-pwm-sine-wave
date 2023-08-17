# Micropython stm32 pwm sine wave generator

This pure-(micro)python library presents an example of using the STM32 Timers and DMA to generate
a PWM/fake-dac sine wave output with no ongoing CPU involvement.

* Generates a Sine Wave look-up-table (LUT)
* Configures one timer/pin for PWM output
* Configures DMA to transfer sine value values from LUT to pwm level register
* Uses second timer to trigger DMA automatically at required rate

The PWM output can be fed through a low pass filter (eg. series resister then capacitor to ground)
to filter out the pwm "carrier" frequency leaving just a sine wave analog signal.

