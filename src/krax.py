from pyplc.platform import plc
from sys import platform
from concrete import Factory,Motor,MSGate,Container,Dosator,Weight,Mixer,Readiness,Loaded,Manager,Lock, Transport
from concrete.vibrator import Vibrator
from concrete.container import Retarder
from concrete.imitation import iGATE,iVALVE,iMOTOR,iWEIGHT
from collections import namedtuple
from pyplc.utils.misc import TOF,TON, BLINK
from pyplc.utils.trig import RTRIG
from pyplc.utils.latch import RS
from pyplc.pou import POU

if platform=='vscode':
    PLC = namedtuple('PLC', ('WATER_M', 'HD_M', 'CEMENT_M', 'CONV_M', 'I_MIXER', 'WATER_OPEN', 'HD_OPEN', 'CEMENT_OPEN', 'WATER_GATE', 'HD1_GATE', 'HD2_GATE', 'CEMENT_GATE', 'BUNKER1_OPEN', 'BUNKER2_OPEN', 'AIR1_ON', 'AIR2_ON', 'VIB1_ON', 'VIB2_ON', 'VIB3_ON', 'VIB4_ON', 'VIB5_ON', 'VIB6_ON', 'MIXER_ON', 'MIXER_OFF', 'PUMP1_ON', 'PUMP2_ON', 'MIXER_OPEN', 'CONV1_ON', 'CONV2_ON', 'CALL_ON', 'PUMPWATER_ON', 'AUGER1_ON', 'AUGER2_ON', 'WATER_CLOSED', 'HD_CLOSED', 'CEMENT_CLOSED', 'CONV1_ISON', 'CONV2_ISON', 'WATER_GATECLOSE', 'HD_GATECLOSE', 'CEMENT_GATECLOSE', 'BUNKER1_GATECLOSE', 'BUNKER2_GATECLOSE', 'MIXER_ISON', 'MIXER_CLOSED', 'MIXER_OPENED', 'MIN1', 'MAX1', 'MIN2', 'MAX2', 'AUGER1_ISON', 'AUGER2_ISON', 'PUMP1_ISON', 'PUMP2_ISON', 'BELT1', 'BELT2', 'WATERPUMP_ISON', 'SUPPLY_FAIL', 'EMERGENCY'))
    plc = PLC()

factory_1 = Factory( )
motor_1 = Motor(ison=plc.MIXER_ISON,powered=plc.MIXER_ON)
gate_1 = MSGate(closed = plc.MIXER_CLOSED, opened=plc.MIXER_OPENED,open=plc.MIXER_OPEN)

cement_m_1 = Weight(raw = plc.CEMENT_M,mmax=1500)
water_m_1 = Weight(raw = plc.WATER_M, mmax=500)
hd_m_1 = Weight(raw = plc.HD_M, mmax=15)
conv_m_1 = Weight(raw=plc.CONV_M,mmax=8000)

silage_1 = Container(m=lambda: cement_m_1.m, closed=~plc.AUGER1_ISON,out=plc.AUGER1_ON, lock=Lock(key=~plc.CEMENT_GATECLOSE), max_sp=500 )
silage_2 = Container(m=lambda: cement_m_1.m, closed=~plc.AUGER2_ISON,out=plc.AUGER2_ON, lock=Lock(key=~plc.CEMENT_GATECLOSE), max_sp=500 )
dcement_1 = Dosator(m=lambda: cement_m_1.m,closed=plc.CEMENT_GATECLOSE,out=plc.CEMENT_OPEN,containers=(silage_1, silage_2),lock=Lock(key=lambda: plc.AUGER1_ON or plc.AUGER2_ON or not plc.MIXER_ISON ) )

water_1 = Container(m=lambda: water_m_1.m,closed=~plc.WATER_OPEN,out=plc.WATER_OPEN,lock=Lock(key=lambda: plc.HD_OPEN or not plc.WATER_CLOSED),max_sp=300)
addition_1 = Container(m=lambda: hd_m_1.m,closed=plc.HD_CLOSED,out = plc.HD_OPEN,lock=Lock(key=lambda: plc.WATER_OPEN or not plc.WATER_CLOSED),max_sp=50)
apump_1 = TOF(clk:=plc.HD_OPEN,q=plc.PUMP1_ON,pt=3000)
apump_2 = TOF(clk:=plc.HD_OPEN,q=plc.PUMP2_ON,pt=3000)
dwater_1 = Dosator(m=lambda: water_m_1.m, out=plc.WATER_OPEN, closed=plc.WATER_CLOSED,containers=(water_1,addition_1),lock=Lock(key=lambda: plc.WATER_OPEN or plc.HD_OPEN or not plc.MIXER_ISON))

retarder_1 = Retarder(m = lambda: conv_m_1.m, outs=(plc.BUNKER1_OPEN,plc.BUNKER2_OPEN),sts=(plc.BUNKER1_GATECLOSE,plc.BUNKER2_GATECLOSE))
filler_1 = Container(m = lambda: conv_m_1.m, out=retarder_1.out(0),closed=retarder_1.closed(0),lock=Lock(key=lambda: retarder_1.lock(0)))
filler_2 = Container(m = lambda: conv_m_1.m, out=retarder_1.out(1),closed=retarder_1.closed(1),lock=Lock(key=lambda: retarder_1.lock(1)))
vibrator_1 = Vibrator(q=plc.VIB1_ON,containers=(plc.BUNKER1_OPEN,),weight=conv_m_1)
vibrator_2 = Vibrator(q=plc.VIB2_ON,containers=(plc.BUNKER2_OPEN,),weight=conv_m_1)
conveyor_1 = Dosator(m = lambda: conv_m_1.m, out=plc.CONV1_ON,closed=~plc.CONV1_ISON,containers=(filler_1,filler_2),lock=Lock(key=lambda: not plc.BUNKER1_GATECLOSE or not plc.BUNKER2_GATECLOSE))

conveyor_2 = Transport(ison=plc.CONV2_ISON, out=plc.CONV2_ON, pt=3000, power=plc.CONV2_ON)

air1 = BLINK(enable=plc.AUGER1_ON, q=plc.AIR1_ON)
air2 = BLINK(enable=plc.AUGER2_ON, q=plc.AIR2_ON)

ready_1 = Readiness( (dcement_1,dwater_1) )
loaded_1= Loaded( (dcement_1,dwater_1) )
mixer_1 = Mixer(gate=gate_1,motor=motor_1,flows=(x.q for x in (silage_1,silage_2,water_1,addition_1) ) )

manager_1 = Manager( collected=ready_1, loaded=loaded_1,mixer=mixer_1,dosators=(dcement_1,dwater_1,conveyor_1))

factory_1.on_mode = tuple(x.switch_mode for x in (silage_1,water_1,addition_1,filler_1,filler_2,dcement_1,dwater_1,conveyor_1))
factory_1.on_emergency = tuple(x.emergency for x in (dcement_1,dwater_1,conveyor_1,mixer_1,manager_1))

instances = (factory_1,motor_1,gate_1,mixer_1,cement_m_1,water_m_1,silage_1,silage_2,water_1,addition_1,filler_1,filler_2,dcement_1,dwater_1,conveyor_1,ready_1,loaded_1,manager_1,vibrator_1,vibrator_2,retarder_1,apump_1, apump_2, air1, air2 )

if platform=='linux':
  imotor_1 = iMOTOR(simple=True,on=plc.MIXER_ON,ison=plc.MIXER_ISON)
  igate_1 = iGATE(open=plc.MIXER_OPEN,opened=plc.MIXER_OPENED,closed=plc.MIXER_CLOSED,simple=True)
  idcement_1 = iVALVE(open=plc.CEMENT_OPEN,closed=plc.CEMENT_CLOSED)
  idwater_1 = iVALVE(open=plc.WATER_OPEN,closed=plc.WATER_CLOSED)
  iconveyor_1 = iMOTOR(simple=True,on=plc.CONV1_ON,ison=plc.CONV1_ISON)
  iauger_1 = iMOTOR(simple=True,on=plc.AUGER1_ON,ison=plc.AUGER1_ISON)
  iapump_1 = iMOTOR(simple=True,on=plc.PUMP1_ON,ison=plc.PUMP1_ISON)
  iapump_2 = iMOTOR(simple=True,on=plc.PUMP2_ON,ison=plc.PUMP2_ISON)
  iaddition_1 = iVALVE(open=plc.HD_OPEN,closed=plc.HD_CLOSED)
  ifiller_1 = iVALVE(open=plc.BUNKER1_OPEN,closed=plc.BUNKER1_GATECLOSE)
  ifiller_2 = iVALVE(open=plc.BUNKER2_OPEN,closed=plc.BUNKER2_GATECLOSE)
  icement_m_1 = iWEIGHT(speed=100, loading=plc.AUGER1_ON,unloading=plc.CEMENT_OPEN,q=plc.CEMENT_M)
  iwater_m_1 = iWEIGHT(speed=100, loading=lambda: plc.WATER_OPEN or plc.HD_OPEN,unloading=plc.WATER_OPEN,q=plc.WATER_M)
  ifillers_m_1 = iWEIGHT(speed=100, loading=lambda : plc.BUNKER1_OPEN or plc.BUNKER2_OPEN,unloading=plc.CONV1_ON,q=plc.CONV_M)
    
  instances += (imotor_1,igate_1,idcement_1,idwater_1,iconveyor_1,iauger_1,iapump_1,iaddition_1,ifiller_1,ifiller_2,icement_m_1,iwater_m_1,ifillers_m_1,iapump_2)

plc.run( instances=instances, ctx=globals() )

