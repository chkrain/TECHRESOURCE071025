from pyplc.platform import plc
from pyplc.utils.misc import BLINK
from concrete import Factory,Motor, Mixer, MSGate as Gate,Lock,Transport,Weight,Container,Dosator,Manager,Readiness,Loaded
from concrete.vibrator import Vibrator,UnloadHelper
from concrete.transport import Gear
from sys import platform
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

# Насосы
pump1 = Transport(ison=plc.PUMP1_ISON, power=plc.PUMP1_ON)
pump2 = Transport(ison=plc.PUMP2_ISON, power=plc.PUMP2_ON)
water_pump = Transport(power=plc.PUMPWATER_ON, ison=plc.WATERPUMP_ISON)

# Шнеки
auger1 = Transport(ison=plc.AUGER1_ISON, power=plc.AUGER1_ON)
auger2 = Transport(ison=plc.AUGER2_ISON, power=plc.AUGER2_ON)

factory.on_emergency = tuple(x.emergency for x in (
    cement_dosator, hd_dosator, water_dosator, mixer, 
    conv1, conv2, bunker1, bunker2,
    water_gate, hd_gate, cement_gate, mixer_gate
))

ready_1 = Readiness(rails=( 
    cement_dosator, hd_dosator, water_dosator,
    bunker1, bunker2
))

loaded_1 = Loaded(rails=(
    cement_dosator, hd_dosator, water_dosator,
    bunker1, bunker2  
))

manager_1 = Manager(
    collected=ready_1,
    loaded=loaded_1, 
    mixer=mixer,
    dosators=(
        cement_dosator, 
        hd_dosator, 
        water_dosator
    )
)

factory.on_emergency += (manager_1.emergency, )

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
    auger2,
    ready_1,
    loaded_1, 
    manager_1
]

if platform == "linux":
    from concrete.imitation import iMOTOR, iGATE, iVALVE, iWEIGHT
    
    # Имитация оборудования
    imotor_1 = iMOTOR(simple=True, on=plc.MIXER_ON, ison=plc.MIXER_ISON)
    igate_1 = iGATE(open=plc.MIXER_OPEN, opened=plc.MIXER_ISOPEN, closed=plc.MIXER_CLOSE)
    icement_valve = iVALVE(open=plc.CEMENT_OPEN, closed=plc.CEMENT_CLOSE)
    ihd_valve = iVALVE(open=plc.HD_OPEN, closed=plc.HD_CLOSE)
    ibelt1 = iMOTOR(simple=True, on=plc.CONV1_ON, ison=plc.BELT1)
    iwater_valve = iVALVE(open=plc.WATER_OPEN, closed=plc.WATER_CLOSE)
    
    # Имитация весов
    icement_weight = iWEIGHT(speed=100, loading=plc.BUNKER1_OPEN, unloading=plc.CEMENT_OPEN, q=plc.CEMENT_WEIGHT)
    ihd_weight = iWEIGHT(speed=100, loading=plc.BUNKER2_OPEN, unloading=plc.HD_OPEN, q=plc.HD_WEIGHT)
    iwater_weight = iWEIGHT(speed=100, loading=lambda: plc.WATER_OPEN, unloading=plc.WATER_OPEN, q=plc.WATER_WEIGHT)
    
    instances += [imotor_1, igate_1, icement_valve, ihd_valve, iwater_valve, 
                  icement_weight, ihd_weight, iwater_weight]

plc.run(instances=instances, ctx=globals())