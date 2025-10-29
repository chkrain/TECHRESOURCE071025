from pyplc.platform import plc
from pyplc.utils.misc import BLINK
from concrete import Factory,Motor, Mixer, MSGate as Gate,Lock,Transport,Weight,Container,Dosator,Manager,Readiness,Loaded
from concrete.elevator import ElevatorGeneric as Elevator
from concrete.vibrator import Vibrator,UnloadHelper
from concrete.imitation import iMOTOR,iGATE,iELEVATOR,iVALVE,iWEIGHT
from concrete.transport import Gear
from sys import platform
from pyplc.ld import LD
from collections import namedtuple

factory = Factory()

water_weight = Weight(raw=plc.WATER_WEIGHT, mmax=1000)
hd_weight = Weight(raw=plc.HD_WEIGHT, mmax=1000) 
cement_weight = Weight(raw=plc.CEMENT_WEIGHT, mmax=1000)
conv_weight = Weight(raw=plc.CONV_WEIGHT, mmax=1000)

bunker1 = Container(m=lambda: cement_weight.m, out=plc.BUNKER1_OPEN, closed=plc.BUNKER1_GATECLOSE, max_sp=1000)

bunker2 = Container(m=lambda: hd_weight.m, out=plc.BUNKER2_OPEN, closed=plc.BUNKER2_GATECLOSE, max_sp=1000)

cement_dosator = Dosator( m=cement_weight.m, out=plc.CEMENT_OPEN, closed=plc.CEMENT_CLOSE, containers=[bunker1])

hd_dosator = Dosator( m=hd_weight.m,  out=plc.HD_OPEN, closed=plc.HD_CLOSE, containers=[bunker2])

water_dosator = Dosator( m=water_weight.m, out=plc.WATER_OPEN,  closed=plc.WATER_CLOSE, containers=[] )

vibrator1 = Vibrator(weight=cement_weight,containers=[lambda: bunker1.out], q=plc.VIBRATOR1_ON,auto=True)

vibrator2 = Vibrator( weight=hd_weight, containers=[lambda: bunker2.out],  q=plc.VIBRATOR2_ON, auto=True)

vibrator3 = Vibrator( weight=cement_weight, containers=[lambda: bunker1.out], q=plc.VIBRATOR3_ON, auto=True)

water_gate = Gate( closed=plc.WATER_GATECLOSE, open=plc.WATER_GATE)

hd_gate = Gate( closed=plc.HD_GATECLOSE, open=plc.HD1_GATE )

cement_gate = Gate( closed=plc.CEMENT_GATECLOSE,  open=plc.CEMENT_GATE)

mixer_gate = Gate( closed=plc.MIXER_CLOSE, opened=plc.MIXER_ISOPEN, open=plc.MIXER_OPEN)

mixer_motor = Motor( ison=plc.MIXER_ISON, on=plc.MIXER_ON, off=plc.MIXER_OFF, bell=plc.CALL_ON, powered=plc.MIXER_ON  )

conv1 = Transport( ison=plc.CONV1_ISON, power=plc.CONV1_ON, hold_on=True )

conv2 = Transport( ison=plc.CONV2_ISON, power=plc.CONV2_ON,  hold_on=True )

conv1_gear = Gear(rot=plc.BELT1,remote=True,  out=plc.CONV1_ON)

conv2_gear = Gear(rot=plc.BELT2, remote=True,out=plc.CONV2_ON)

mixer = Mixer( gate=mixer_gate, motor=mixer_motor, go=False, count=1)

# Аэрация
air1 = BLINK(enable=plc.AUGER1_ON, q=plc.AIR1_ON)
air2 = BLINK(enable=plc.AUGER2_ON, q=plc.AIR2_ON)

# Насосы ХД
pump1 = Transport(ison=plc.PUMP1_ISON, power=plc.PUMP1_ON)
pump2 = Transport(ison=plc.PUMP2_ISON, power=plc.PUMP2_ON)

# Насос воды  
water_pump = Transport(power=plc.PUMPWATER_ON)

# Шнеки
auger1 = Transport(ison=plc.AUGER1_ISON, power=plc.AUGER1_ON)
auger2 = Transport(ison=plc.AUGER2_ISON, power=plc.AUGER2_ON)

# # бункер цемента
# bunker1.sp = 100  # доза 100 кг
# bunker1.go = True

# # затвор воды  
# water_gate.simple(pt=5)  # открыть на 5 сек

# # смеситель
# mixer_motor.remote(True)  # включить двигатель

instances = [
    water_weight,
    hd_weight, 
    cement_weight,
    conv_weight,
    bunker1,
    bunker2,
    cement_dosator,
    hd_dosator,
    water_dosator,
    vibrator1,
    vibrator2, 
    vibrator3,
    water_gate,
    hd_gate,
    cement_gate,
    mixer_gate,
    mixer_motor,
    conv1,
    conv2,
    conv1_gear,
    conv2_gear,
    mixer,
    air1,
    air2,
    pump1,
    pump2, 
    water_pump,
    auger1,
    auger2
]

plc.run(instances=instances, ctx=globals())