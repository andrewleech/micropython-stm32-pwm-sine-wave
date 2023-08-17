import uctypes
from micropython import const

from typing import Any, Optional

__all__ = [
    "TIM1",
    "TIM2",
    "TIM16",
    "DMA1_Channel1",
    "DMA1_Channel2",
    "DMA2_Channel1",
    "DMA2_Channel2",
]


class Register:
    def __init__(self, addr) -> None:
        if not hasattr(self.__class__, "__regs__"):
            # We have register definitions defined on Register subclasses, which are used
            # to create the uctypes.struct instances.
            # These attributes get in the way of reading the struct attrs though, so move
            # them to an class.__regs__ dict for referencing and delete from the class itself.
            __regs__ = {k: v for k, v in self.__class__.__dict__.items() if not k.startswith("_")}
            setattr(self.__class__, "__regs__", __regs__)
            for k in __regs__:
                delattr(self.__class__, k)

        self.__addr__ = addr

        descriptor = {
            k: (v | uctypes.UINT32) for k, v in self.__class__.__regs__.items()  # type: ignore
        }
        self.__struct__ = uctypes.struct(addr, descriptor)

    def __reg_addr__(self, register: str):
        return self.__addr__ + self.__regs__[register]

    def __repr__(self):
        return f"<{self.__class__.__name__} 0x{self.__addr__:x}>"

    def __dir__(self):
        return [k for k in self.__regs__]

    def __inspect__(self):
        print(self.__class__.__name__)
        struct = self.__struct__
        for k, v in sorted(self.__regs__.items(), key=lambda t: t[1]):
            val = getattr(struct, k)
            print(f"{k : 10} (0x{v:04x}):  0x{val:04x}")

    def __getattr__(self, __name: str) -> Any:
        if __name.startswith("_"):
            raise AttributeError(__name)

        v = getattr(self.__struct__, __name)
        return v

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name.startswith("_"):
            object.__setattr__(self, __name, __value)
        else:
            setattr(self.__struct__, __name, __value)


try:
    from ._stm_registers import *

except ImportError:
    print("ERROR: Register definitions missing")
    print("Generate these for your cpu like:")
    print(
        f"python stm_register_builder.py micropython/lib/stm32lib/CMSIS/STM32WBxx/Include/stm32wb55xx.h"
    )
    raise RuntimeError()


# DMA_request DMA request
# From stm32wbxx_hal_driver/Inc/stm32wbxx_hal_dma.h

DMA_REQUEST_MEM2MEM = LL_DMAMUX_REQ_MEM2MEM  # memory to memory transfer

DMA_REQUEST_GENERATOR0 = LL_DMAMUX_REQ_GENERATOR0  # DMAMUX request generator 0
DMA_REQUEST_GENERATOR1 = LL_DMAMUX_REQ_GENERATOR1  # DMAMUX request generator 1
DMA_REQUEST_GENERATOR2 = LL_DMAMUX_REQ_GENERATOR2  # DMAMUX request generator 2
DMA_REQUEST_GENERATOR3 = LL_DMAMUX_REQ_GENERATOR3  # DMAMUX request generator 3

DMA_REQUEST_SAI1_A = LL_DMAMUX_REQ_SAI1_A  # DMAMUX SAI1 A request
DMA_REQUEST_SAI1_B = LL_DMAMUX_REQ_SAI1_B  # DMAMUX SAI1 B request

DMA_REQUEST_TIM1_CH1 = LL_DMAMUX_REQ_TIM1_CH1  # DMAMUX TIM1 CH1 request
DMA_REQUEST_TIM1_CH2 = LL_DMAMUX_REQ_TIM1_CH2  # DMAMUX TIM1 CH2 request
DMA_REQUEST_TIM1_CH3 = LL_DMAMUX_REQ_TIM1_CH3  # DMAMUX TIM1 CH3 request
DMA_REQUEST_TIM1_CH4 = LL_DMAMUX_REQ_TIM1_CH4  # DMAMUX TIM1 CH4 request
DMA_REQUEST_TIM1_UP = LL_DMAMUX_REQ_TIM1_UP  # DMAMUX TIM1 UP  request
DMA_REQUEST_TIM1_TRIG = LL_DMAMUX_REQ_TIM1_TRIG  # DMAMUX TIM1 TRIG request
DMA_REQUEST_TIM1_COM = LL_DMAMUX_REQ_TIM1_COM  # DMAMUX TIM1 COM request

DMA_REQUEST_TIM2_CH1 = LL_DMAMUX_REQ_TIM2_CH1  # DMAMUX TIM2 CH1 request
DMA_REQUEST_TIM2_CH2 = LL_DMAMUX_REQ_TIM2_CH2  # DMAMUX TIM2 CH2 request
DMA_REQUEST_TIM2_CH3 = LL_DMAMUX_REQ_TIM2_CH3  # DMAMUX TIM2 CH3 request
DMA_REQUEST_TIM2_CH4 = LL_DMAMUX_REQ_TIM2_CH4  # DMAMUX TIM2 CH4 request
DMA_REQUEST_TIM2_UP = LL_DMAMUX_REQ_TIM2_UP  # DMAMUX TIM2 UP  request

DMA_REQUEST_TIM16_CH1 = LL_DMAMUX_REQ_TIM16_CH1  # DMAMUX TIM16 CH1 request
DMA_REQUEST_TIM16_UP = LL_DMAMUX_REQ_TIM16_UP  # DMAMUX TIM16 UP  request

DMA_REQUEST_TIM17_CH1 = LL_DMAMUX_REQ_TIM17_CH1  # DMAMUX TIM17 CH1 request
DMA_REQUEST_TIM17_UP = LL_DMAMUX_REQ_TIM17_UP  # DMAMUX TIM17 UP  request

# DMA_Data_transfer_direction DMA Data transfer direction
DMA_PERIPH_TO_MEMORY = LL_DMA_DIRECTION_PERIPH_TO_MEMORY  # Peripheral to memory direction
DMA_MEMORY_TO_PERIPH = LL_DMA_DIRECTION_MEMORY_TO_PERIPH  # Memory to peripheral direction
DMA_MEMORY_TO_MEMORY = LL_DMA_DIRECTION_MEMORY_TO_MEMORY  # Memory to memory direction

# DMA_Peripheral_incremented_mode DMA Peripheral incremented mode
DMA_PINC_ENABLE = LL_DMA_PERIPH_INCREMENT  # Peripheral increment mode Enable
DMA_PINC_DISABLE = LL_DMA_PERIPH_NOINCREMENT  # Peripheral increment mode Disable

# DMA_Memory_incremented_mode DMA Memory incremented mode
DMA_MINC_ENABLE = LL_DMA_MEMORY_INCREMENT  # Memory increment mode Enable
DMA_MINC_DISABLE = LL_DMA_MEMORY_NOINCREMENT  # Memory increment mode Disable

# DMA_Peripheral_data_size DMA Peripheral data size
DMA_PDATAALIGN_BYTE = LL_DMA_PDATAALIGN_BYTE  # Peripheral data alignment : Byte
DMA_PDATAALIGN_HALFWORD = LL_DMA_PDATAALIGN_HALFWORD  # Peripheral data alignment : HalfWord
DMA_PDATAALIGN_WORD = LL_DMA_PDATAALIGN_WORD  # Peripheral data alignment : Word

# DMA_Memory_data_size DMA Memory data size
DMA_MDATAALIGN_BYTE = LL_DMA_MDATAALIGN_BYTE  # Memory data alignment : Byte
DMA_MDATAALIGN_HALFWORD = LL_DMA_MDATAALIGN_HALFWORD  # Memory data alignment : HalfWord
DMA_MDATAALIGN_WORD = LL_DMA_MDATAALIGN_WORD  # Memory data alignment : Word

# DMA_mode DMA mode
DMA_NORMAL = LL_DMA_MODE_NORMAL  # Normal mode
DMA_CIRCULAR = LL_DMA_MODE_CIRCULAR  # Circular mode

# DMA_Priority_level DMA Priority level
DMA_PRIORITY_LOW = LL_DMA_PRIORITY_LOW  # Priority level : Low
DMA_PRIORITY_MEDIUM = LL_DMA_PRIORITY_MEDIUM  # Priority level : Medium
DMA_PRIORITY_HIGH = LL_DMA_PRIORITY_HIGH  # Priority level : High
DMA_PRIORITY_VERY_HIGH = LL_DMA_PRIORITY_VERYHIGH  # Priority level : Very_High

# DMA_interrupt_enable_definitions DMA interrupt enable definitions
DMA_IT_TC = LL_DMA_CCR_TCIE  # Transfer complete interrupt
DMA_IT_HT = LL_DMA_CCR_HTIE  # Half Transfer interrupt
DMA_IT_TE = LL_DMA_CCR_TEIE  # Transfer error interrupt

# From STM32WBxx_HAL_Driver/Inc/stm32wbxx_ll_bus.h
LL_AHB1_GRP1_PERIPH_DMA1 = RCC_AHB1ENR_DMA1EN
LL_AHB1_GRP1_PERIPH_DMA2 = RCC_AHB1ENR_DMA2EN
LL_AHB1_GRP1_PERIPH_DMAMUX1 = RCC_AHB1ENR_DMAMUX1EN


# stm32wbxx_hal_driver/Inc/stm32wbxx_hal_tim.h

# TIM_DMA_sources TIM DMA Sources
TIM_DMA_UPDATE = TIM_DIER_UDE  # DMA triggered by update event
TIM_DMA_CC1 = TIM_DIER_CC1DE  # DMA triggered by capture/compare match 1 event
TIM_DMA_CC2 = TIM_DIER_CC2DE  # DMA triggered by capture/compare match 2 event
TIM_DMA_CC3 = TIM_DIER_CC3DE  # DMA triggered by capture/compare match 3 event
TIM_DMA_CC4 = TIM_DIER_CC4DE  # DMA triggered by capture/compare match 4 event
TIM_DMA_COM = TIM_DIER_COMDE  # DMA triggered by commutation event
TIM_DMA_TRIGGER = TIM_DIER_TDE  # DMA triggered by trigger event


class DMA_HandleTypeDef:
    Instance: DMA_Channel_TypeDef
    DmaBaseAddress: DMA_TypeDef  # DMA Channel Base Address
    ChannelIndex: int = -1  # DMA Channel Index
    DMAmuxChannel: DMAMUX_Channel_TypeDef  # Register base address
    DMAmuxChannelStatus: DMAMUX_ChannelStatus_TypeDef  # DMAMUX Channels Status Base Address
    DMAmuxChannelStatusMask: int
    DMAmuxRequestGen: Optional[DMAMUX_RequestGen_TypeDef]  # DMAMUX request generator Base Address
    DMAmuxRequestGenStatus: Optional[
        DMAMUX_RequestGenStatus_TypeDef
    ]  # DMAMUX request generator Address
    DMAmuxRequestGenStatusMask: int


def LL_AHB1_GRP1_EnableClock(Periphs):
    # SET_BIT(RCC_BASE + RCC_TypeDef.AHB1ENR, Periphs)
    RCC.AHB1ENR |= Periphs


# stm32wbxx_hal_driver/Inc/stm32wbxx_hal_rcc.h

def __HAL_RCC_DMAMUX1_CLK_ENABLE__():
    LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_DMAMUX1)


def __HAL_RCC_DMA1_CLK_ENABLE__():
    LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_DMA1)


def __HAL_RCC_DMA2_CLK_ENABLE__():
    LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_DMA2)


def __HAL_TIM_ENABLE_DMA__(TIMER, TIM_DMA_source):
    # ((__HANDLE__)->Instance->DIER |= (__DMA__))
    # print("TIMER.DIER", TIMER, TIM_DMA_source, TIMER.DIER)
    TIMER.DIER |= TIM_DMA_source


def DMA_CalcDMAMUXChannelBaseAndMask(hdma: DMA_HandleTypeDef):
    if hdma.DmaBaseAddress is DMA1:
        # print(f"DMAmuxChannel: {DMAMUX1_Channel0_BASE + (hdma.ChannelIndex >> 2)}")
        hdma.DMAmuxChannel = DMAMUX_Channel_TypeDef(
            DMAMUX1_Channel0_BASE + (hdma.ChannelIndex >> 2)
        )
    else:
        hdma.DMAmuxChannel = DMAMUX_Channel_TypeDef(
            DMAMUX1_Channel7_BASE + (hdma.ChannelIndex >> 2)
        )

    channel_number = ((hdma.Instance.__addr__ & 0xFF) - 8) // 20
    hdma.DMAmuxChannelStatus = DMAMUX1_ChannelStatus
    hdma.DMAmuxChannelStatusMask = 1 << (channel_number & 0x1C)


def DMA_CalcDMAMUXRequestGenBaseAndMask(hdma: DMA_HandleTypeDef, Request):
    request = Request & DMAMUX_CxCR_DMAREQ_ID

    # DMA Channels are connected to DMAMUX1 request generator blocks
    hdma.DMAmuxRequestGen = DMAMUX_RequestGen_TypeDef(
        (DMAMUX1_RequestGenerator0_BASE + ((request - 1) * 4))
    )

    hdma.DMAmuxRequestGenStatus = DMAMUX1_RequestGenStatus

    # here "Request" is either DMA_REQUEST_GENERATOR0 to DMA_REQUEST_GENERATOR3, i.e. <= 4
    hdma.DMAmuxRequestGenStatusMask = 1 << ((request - 1) & 0x3)


def HAL_DMA_Init(
    DMA: int,
    Channel: int,
    Request,
    Direction,
    PeriphInc,
    MemInc,
    PeriphDataAlignment,
    MemDataAlignment,
    Mode,
    Priority,
):

    dma_obj_name = f"DMA{DMA}_Channel{Channel}"
    Instance = globals().get(dma_obj_name)
    if not isinstance(Instance, DMA_Channel_TypeDef):
        raise AttributeError(f"Cannot find: {dma_obj_name}")

    hdma = DMA_HandleTypeDef()
    hdma.Instance = Instance

    if DMA == 1:
        hdma.DmaBaseAddress = DMA1
    elif DMA == 2:
        hdma.DmaBaseAddress = DMA2
    else:
        raise ValueError(f"Don't know DMA base for: {DMA}")

    hdma.ChannelIndex = Channel - 1

    # Get the CR register value
    tmp = hdma.Instance.CCR

    # Clear PL, MSIZE, PSIZE, MINC, PINC, CIRC, DIR and MEM2MEM bits
    tmp &= ~(
        DMA_CCR_PL
        | DMA_CCR_MSIZE
        | DMA_CCR_PSIZE
        | DMA_CCR_MINC
        | DMA_CCR_PINC
        | DMA_CCR_CIRC
        | DMA_CCR_DIR
        | DMA_CCR_MEM2MEM
    )

    # Prepare the DMA Channel configuration
    tmp |= (
        Direction | PeriphInc | MemInc | PeriphDataAlignment | MemDataAlignment | Mode | Priority
    )

    # print(f"0. hdma.Instance.CCR = 0x{tmp:x}")

    hdma.Instance.CCR = tmp

    # print(f"1. hdma.Instance.CCR = 0x{hdma.Instance.CCR:x}")

    DMA_CalcDMAMUXChannelBaseAndMask(hdma)

    if Direction == DMA_MEMORY_TO_MEMORY:
        Request = DMA_REQUEST_MEM2MEM

    # Set peripheral request to DMAMUX channel
    hdma.DMAmuxChannel.CCR = Request & DMAMUX_CxCR_DMAREQ_ID

    # Clear the DMAMUX synchro overrun flag
    hdma.DMAmuxChannelStatus.CFR = hdma.DMAmuxChannelStatusMask

    if Request > 0 and Request <= DMA_REQUEST_GENERATOR3:
        # Initialize parameters for DMAMUX request generator :
        # DMAmuxRequestGen, DMAmuxRequestGenStatus and DMAmuxRequestGenStatusMask
        DMA_CalcDMAMUXRequestGenBaseAndMask(hdma, Request=Request)

        if not hdma.DMAmuxRequestGen or not hdma.DMAmuxRequestGenStatus:
            raise NotImplementedError()

        # Reset the DMAMUX request generator register
        hdma.DMAmuxRequestGen.RGCR = 0

        # Clear the DMAMUX request generator overrun flag
        hdma.DMAmuxRequestGenStatus.RGCFR = hdma.DMAmuxRequestGenStatusMask
    else:
        hdma.DMAmuxRequestGen = None
        hdma.DMAmuxRequestGenStatus = None
        hdma.DMAmuxRequestGenStatusMask = 0

    return hdma


def DMA_SetConfig(hdma: DMA_HandleTypeDef, Direction, SrcAddress, DstAddress, DataLength):
    # Clear the DMAMUX synchro overrun flag
    hdma.DMAmuxChannelStatus.CFR = hdma.DMAmuxChannelStatusMask

    if hdma.DMAmuxRequestGenStatus:
        # Clear the DMAMUX request generator overrun flag
        hdma.DMAmuxRequestGenStatus.RGCFR = hdma.DMAmuxRequestGenStatusMask

    # Clear all flags
    hdma.DmaBaseAddress.IFCR = DMA_ISR_GIF1 << (hdma.ChannelIndex & 0x1C)

    # Configure DMA Channel data length
    hdma.Instance.CNDTR = DataLength

    # Memory to Peripheral
    if Direction == DMA_MEMORY_TO_PERIPH:
        # Configure DMA Channel destination address
        hdma.Instance.CPAR = DstAddress

        # Configure DMA Channel source address
        hdma.Instance.CMAR = SrcAddress

    # Peripheral to Memory
    else:
        # Configure DMA Channel source address
        hdma.Instance.CPAR = SrcAddress

        # Configure DMA Channel destination address
        hdma.Instance.CMAR = DstAddress


def HAL_DMA_Start(hdma: DMA_HandleTypeDef, Direction, SrcAddress, DstAddress, DataLength):

    if not isinstance(SrcAddress, int):
        SrcAddress = uctypes.addressof(SrcAddress)

    # __HAL_DMA_DISABLE(hdma)  ((__HANDLE__)->Instance->CCR &=  ~DMA_CCR_EN)
    hdma.Instance.CCR &= ~DMA_CCR_EN
    # print(f"2. hdma.Instance.CCR = 0x{hdma.Instance.CCR:x}")

    DMA_SetConfig(hdma, Direction, SrcAddress, DstAddress, DataLength)

    # __HAL_DMA_ENABLE(hdma) ((__HANDLE__)->Instance->CCR |=  DMA_CCR_EN)
    hdma.Instance.CCR |= DMA_CCR_EN
    # print(f"3. hdma.Instance.CCR = 0x{hdma.Instance.CCR:x}")
