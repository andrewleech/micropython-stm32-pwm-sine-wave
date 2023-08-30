import math
from pyb import Timer

from machine import Pin

from signal_gen.stm_dma_timer import (
    __HAL_RCC_DMAMUX1_CLK_ENABLE__,
    __HAL_RCC_DMA1_CLK_ENABLE__,
    __HAL_RCC_DMA2_CLK_ENABLE__,
    __HAL_TIM_ENABLE_DMA__,
    HAL_DMA_Init,
    HAL_DMA_Start,
    TIM_DMA_CC1,
    TIM1,
    TIM16,
    DMA_REQUEST_TIM16_CH1,
    DMA_MEMORY_TO_PERIPH,
    DMA_PINC_DISABLE,
    DMA_MINC_ENABLE,
    DMA_PDATAALIGN_WORD,
    DMA_MDATAALIGN_BYTE,
    DMA_CIRCULAR,
    DMA_PRIORITY_HIGH,
)

SINE_FREQ = 40_000  # sine wave frequency in HZ
SINE_SAMPLES = 25  # number of sample points in time domain
SINE_MAX_LEVEL = 64  # number of aplitude / volts levels.

# For PWM, the pin, timer and channel number must all match,
# eg pin PA10 has an Alternate Function of TIM1_CH3
PWM_PIN = Pin("A10", Pin.OUT)
PWM_TIMER = Timer(1, freq=1_000_000)
PWM_TIMER_CH = PWM_TIMER.channel(3, Timer.PWM, pin=PWM_PIN, pulse_width_percent=0)

# This is the register for the timer/channel above which the DMA will transfer
# pwm levels to from the look up table.
DMA_DESTINATION_ADDR = TIM1.__reg_addr__("CCR3")

# This DMA timer is used to trigger the regular dma transfers at required
# rate to clock out each individual SINE_SAMPLE point to make up the desired
# final SINE_FREQ
DMA_TIMER = Timer(16, freq=SINE_FREQ * SINE_SAMPLES)
DMA_TIMER_CH = DMA_TIMER.channel(1, Timer.OC_TIMING, pulse_width=1)


# Generate the look up table of sine wave sample values.
SINE_HALF_LEVEL = SINE_MAX_LEVEL // 2
Wave_LUT = bytearray(
    [
        int(
            (SINE_HALF_LEVEL - 1) * math.sin(i * 2 * math.pi / SINE_SAMPLES)
            + SINE_HALF_LEVEL
            + 0.5
        )
        for i in range(SINE_SAMPLES)
    ]
)

# Configure and start the DMA

__HAL_RCC_DMAMUX1_CLK_ENABLE__()
__HAL_RCC_DMA1_CLK_ENABLE__()

dma_timer = HAL_DMA_Init(
    DMA=1,
    Channel=1,
    Request=DMA_REQUEST_TIM16_CH1,  # Needs to match settings of DMA_TIMER above.
    Direction=DMA_MEMORY_TO_PERIPH,
    PeriphInc=DMA_PINC_DISABLE,
    MemInc=DMA_MINC_ENABLE,
    PeriphDataAlignment=DMA_PDATAALIGN_WORD,
    MemDataAlignment=DMA_MDATAALIGN_BYTE,
    Mode=DMA_CIRCULAR,
    Priority=DMA_PRIORITY_HIGH,
)

HAL_DMA_Start(dma_timer, DMA_MEMORY_TO_PERIPH, Wave_LUT, DMA_DESTINATION_ADDR, SINE_SAMPLES)

# Needs to match settings of DMA_TIMER above.
__HAL_TIM_ENABLE_DMA__(TIM16, TIM_DMA_CC1)
