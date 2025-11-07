from pyplc.platform import plc
from sys import platform
from concrete import Factory,Motor,MSGate as Gate,Container,Dosator,Weight,Mixer,Readiness,Loaded,Manager,Lock, Transport
from concrete.vibrator import Vibrator, UnloadHelper
from concrete.container import Retarder
from concrete.imitation import iGATE,iVALVE,iMOTOR,iWEIGHT
from collections import namedtuple
from pyplc.utils.misc import TOF,TON, BLINK
from pyplc.utils.trig import RTRIG
from pyplc.utils.latch import RS
from pyplc.pou import POU

if platform=='vscode':
    PLC = namedtuple('PLC', ('WATER_M', 'HD_M', 'CEMENT_M', 'CONV_M', 'I_MIXER', 'BUNK_M_1', 'BUNK_M_2', 'WATER_OPEN_1', 'HD_OPEN_1', 'CEMENT_OPEN_1', 'WATER_GATE_1', 'HD_GATE_1', 'HD_GATE_2', 'CEMENT_GATE_1', 'BUNKER_OPEN_1', 'BUNKER_OPEN_2', 'AIR_ON_1', 'AIR_ON_2', 'VIB_ON_1', 'VIB_ON_2', 'VIB_ON_3', 'VIB_ON_4', 'VIB_ON_5', 'VIB_ON_6', 'MIXER_ON_1', 'MIXER_OFF_1', 'PUMP_ON_1', 'PUMP_ON_2', 'MIXER_OPEN_1', 'CONV_ON_1', 'CONV_ON_2', 'CALL_ON_1', 'PUMPWATER_ON', 'AUGER_ON_1', 'AUGER_ON_2', 'WATER_CLOSED_1', 'HD_CLOSED_1', 'CEMENT_CLOSED_1', 'CONV_ISON_1', 'CONV_ISON_2', 'WATER_GATECLOSE_1', 'HD_GATECLOSE_1', 'CEMENT_GATECLOSE_1', 'BUNKER_GATECLOSE_1', 'BUNKER_GATECLOSE_2', 'MIXER_ISON_1', 'MIXER_CLOSED_1', 'MIXER_OPENED_1', 'MIN1', 'MAX1', 'MIN2', 'MAX2', 'AUGER_ISON_1', 'AUGER_ISON_2', 'PUMP_ISON_1', 'PUMP_ISON_2', 'BELT1', 'BELT2', 'WATERPUMP_ISON', 'SUPPLY_FAIL', 'EMERGENCY'))
    plc = PLC()

factory_1 = Factory()

# цементное
cement_m_1 = Weight(raw=plc.CEMENT_M, mmax=1500)
auger_1 = Container(m = cement_m_1.get_m, out = plc.AUGER_ON_1, lock=Lock(key=~plc.CEMENT_CLOSED_1),closed=~plc.AUGER_ON_1,max_sp=1000)
auger_2 = Container(m = cement_m_1.get_m, out = plc.AUGER_ON_2, lock=Lock(key=~plc.CEMENT_CLOSED_1),closed=~plc.AUGER_ON_2,max_sp=1000)
dcement_1 = Dosator(m = cement_m_1.get_m, closed = plc.CEMENT_CLOSED_1, out = plc.CEMENT_OPEN_1, lock=Lock(key=plc.AUGER_ON_1 or plc.AUGER_ON_2), containers=(auger_1, auger_2))
aerator_1 = BLINK(enable=plc.AUGER_ON_1,q=plc.AIR_ON_1)
aerator_2 = BLINK(enable=plc.AUGER_ON_2,q=plc.AIR_ON_2)
dc_vibrator_1 = UnloadHelper(q=plc.VIB_ON_1,dosator=dcement_1,weight=cement_m_1)

# вода
water_m_1 = Weight(raw=plc.WATER_M, mmax=500)
water_1 = Container(m = water_m_1.get_m, out = plc.PUMPWATER_ON, lock=Lock(key=~plc.WATER_CLOSED_1 or plc.PUMPWATER_ON),closed=~plc.PUMPWATER_ON,max_sp=500)
dwater_1 = Dosator(m = water_m_1.get_m, closed = plc.WATER_CLOSED_1, out = plc.WATER_OPEN_1, lock=Lock(key=plc.PUMPWATER_ON), containers=(water_1,))

# 2 дозатора хим добавки
additions_m_1 = Weight(raw=plc.HD_M, mmax=500)
addition_1 = Container(m = additions_m_1.get_m, out = plc.PUMP_ON_1, lock=Lock(key=lambda: not plc.HD_CLOSED_1 or plc.PUMP_ON_1),closed=~plc.PUMP_ON_1,max_sp=50)
addition_2 = Container(m = additions_m_1.get_m, out = plc.PUMP_ON_2, lock=Lock(key=lambda: not plc.HD_CLOSED_1 or plc.PUMP_ON_2),closed=~plc.PUMP_ON_2,max_sp=50)
dadditions_1 = Dosator(m = additions_m_1.get_m, closed = plc.HD_CLOSED_1, out = plc.HD_OPEN_1, lock=Lock(key=lambda: plc.PUMP_ON_1 or plc.PUMP_ON_2), containers=(addition_1,addition_2))

# бункера
fillers_m_1 = Weight(raw=plc.CONV_M, mmax=8000)
filler_1 = Container(m = fillers_m_1.get_m, out = plc.BUNKER_OPEN_1, lock=Lock(key=lambda: plc.CONV_ON_1 or plc.BUNKER_OPEN_2),closed=~plc.BUNKER_OPEN_1,max_sp=3000)
filler_2 = Container(m = fillers_m_1.get_m, out = plc.BUNKER_OPEN_2, lock=Lock(key=lambda: plc.CONV_ON_1 or plc.BUNKER_OPEN_1),closed=~plc.BUNKER_OPEN_2,max_sp=3000)
dfillers_1 = Dosator(m = fillers_m_1.get_m, closed = ~plc.CONV_ON_1, out = plc.CONV_ON_1, lock=Lock(key=lambda: plc.BUNKER_OPEN_1 or plc.BUNKER_OPEN_2 or not plc.CONV_ISON_2), containers=(filler_1,filler_2))

# вибратор конвейерный
vibrator_1 = Vibrator(q=plc.VIB_ON_5,containers=(plc.BUNKER_OPEN_1,plc.BUNKER_OPEN_2),weight=fillers_m_1)

# смеситель
motor_1 = Motor(ison=plc.MIXER_ISON_1,powered = plc.MIXER_ON_1 )
tconveyor_1 = Transport(ison=plc.CONV_ISON_2,power=plc.CONV_ON_2,out=plc.MIXER_OPEN_1)
gate_1 = Gate(closed = plc.MIXER_CLOSED_1,opened=plc.MIXER_OPENED_1,open=tconveyor_1.set_auto  )
mixer_1 = Mixer(gate=gate_1,motor=motor_1,flows=[ x.q for x in [auger_1,water_1,addition_1,addition_2]])

ready_1 = Readiness([dcement_1,dwater_1,dadditions_1,dfillers_1,tconveyor_1])
loaded_1 = Loaded([dcement_1,dwater_1,dadditions_1,tconveyor_1])

def loading():
  tconveyor_1.unload = True
  dadditions_1.unload = True
  while not tconveyor_1.unloaded: yield 
  dcement_1.unload = True
  dwater_1.unload = True

manager_1 = Manager( mixer=mixer_1,collected=ready_1,loaded = loaded_1,dosators=(dcement_1,dwater_1,dadditions_1,dfillers_1,tconveyor_1),loadOrder=loading )

factory_1.on_mode = [ x.switch_mode for x in [dcement_1,dwater_1,dadditions_1,dfillers_1] ]
factory_1.on_emergency = [ x.emergency for x in [dcement_1,dwater_1,dadditions_1,dfillers_1,tconveyor_1,mixer_1,manager_1] ]

instances = (factory_1, motor_1,gate_1,tconveyor_1,
            cement_m_1,auger_1, auger_2, dcement_1,
            water_m_1,water_1,dwater_1,
            additions_m_1,addition_1,addition_2,dadditions_1,
            fillers_m_1,filler_1,filler_2,dfillers_1,
            mixer_1,
            ready_1,loaded_1,manager_1,
            vibrator_1,dc_vibrator_1,aerator_1, aerator_2)

if platform=='linux':
  imotor_1 = iMOTOR(simple=True,on = plc.MIXER_ON_1,ison=plc.MIXER_ISON_1)
  igate_1 = iGATE(open=plc.MIXER_OPEN_1,closed=plc.MIXER_CLOSED_1,opened=plc.MIXER_OPENED_1,simple=True)
  iauger_1 = iMOTOR(simple=True,on = plc.AUGER_ON_1,ison=plc.AUGER_ISON_1)
  iauger_2 = iMOTOR(simple=True,on = plc.AUGER_ON_2,ison=plc.AUGER_ISON_2)
  iwpump_1 = iMOTOR(simple=True,on = plc.PUMPWATER_ON,ison=plc.WATERPUMP_ISON)
  iapump_1 = iMOTOR(simple=True,on = plc.PUMP_ON_1,ison=plc.PUMP_ISON_1)
  iapump_2 = iMOTOR(simple=True,on = plc.PUMP_ON_2,ison=plc.PUMP_ISON_2)
  iconveyor_1 = iMOTOR(simple=True,on = plc.CONV_ON_1,ison=plc.CONV_ISON_1)
  itconveyor_1 = iMOTOR(simple=True,on = plc.CONV_ON_2,ison=plc.CONV_ISON_2)
  idcement_1 = iVALVE(open=plc.CEMENT_OPEN_1,closed=plc.CEMENT_CLOSED_1)
  idwater_1 = iVALVE(open=plc.WATER_OPEN_1,closed=plc.WATER_CLOSED_1)
  idadditions_1 = iVALVE(open=plc.HD_OPEN_1,closed=plc.HD_CLOSED_1)
  
  icement_m_1 = iWEIGHT(speed=100,loading=plc.AUGER_ON_1 or plc.AUGER_ON_2, unloading=plc.CEMENT_OPEN_1, q = plc.CEMENT_M)
  iwater_m_1 = iWEIGHT(speed=100,loading=plc.PUMPWATER_ON, unloading=plc.WATER_OPEN_1, q = plc.WATER_M)
  iadditions_m_1 = iWEIGHT(speed=100,loading=lambda: plc.PUMP_ON_1 or plc.PUMP_ON_2, unloading=plc.HD_OPEN_1, q = plc.HD_M)
  ifillers_m_1 = iWEIGHT(speed=100,loading=lambda: plc.BUNKER_OPEN_1 or plc.BUNKER_OPEN_2, unloading=plc.CONV_ON_1, q = plc.CONV_M)
    
  instances += (imotor_1,igate_1,iauger_1,iwpump_1,iapump_1,iauger_2,iapump_2,iconveyor_1,itconveyor_1,idcement_1,idwater_1,idadditions_1,
                icement_m_1,iwater_m_1,iadditions_m_1,ifillers_m_1)

plc.run( instances=instances, ctx=globals() )
