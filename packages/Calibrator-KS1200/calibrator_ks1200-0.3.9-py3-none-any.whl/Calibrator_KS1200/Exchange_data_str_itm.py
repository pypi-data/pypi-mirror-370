from  func_lib import *
import time

# import pika # подключение библиотеки для работы с RabbitMQ

# fa=[] # список float array
# for i in  range(50):
#     fa.append([i+0.1]) #список float array
# ia=[] # список integer array
# for i in  range(50):
#     ia.append([i]) #список integer array

def exchange_data_itm(MainWindow, str_received, portname = 'COM5', boud = 19200):
    strout=None
    global ia
    ba2=bytearray(2)
    str_change=str(str_received)

    numzerocalibr=str_change.find('zerocalibr')
    numstartmeas=str_change.find('startmeas')
    numstopmeas=str_change.find('stopmeas')

    numsen1=str_change.find('sen1') # датчик\канал
    numsen2=str_change.find('sen2') # режим работы канала
    numsen3=str_change.find('sen3') # чтение\запись
    numsen4=str_change.find('sen4')
    numsen5=str_change.find('sen5')
    numsen6=str_change.find('sen6')
    numsen7=str_change.find('sen7')
    numsen8=str_change.find('sen8')

    nummc1=str_change.find('mc1') # измерительный ток по каналам (measure current)
    nummc2=str_change.find('mc2') # значения: 1.0, 4.0, 3.0, 2.5, 2.0, 1.5, 0.7, 0.4
    nummc3=str_change.find('mc3')
    nummc4=str_change.find('mc4')
    nummc5=str_change.find('mc5')
    nummc6=str_change.find('mc6')
    nummc7=str_change.find('mc7')
    nummc8=str_change.find('mc8')
     
    numRref1=str_change.find('Rref1') # опорное сопротивление в омах\канал
    numRref2=str_change.find('Rref2') # чтение\запись
    numRref3=str_change.find('Rref3') # значения: R3, R30, R300, Re
    numRref4=str_change.find('Rref4')
    numRref5=str_change.find('Rref5')
    numRref6=str_change.find('Rref6')
    numRref7=str_change.find('Rref7')
    numRref8=str_change.find('Rref8')

    numhk1=str_change.find('hk1') # компенсатор холодных концов\канал
    numhk2=str_change.find('hk2') # значения ON Или OFF
    numhk3=str_change.find('hk3') # чтение\запись
    numhk4=str_change.find('hk4')
    numhk5=str_change.find('hk5')
    numhk6=str_change.find('hk6')
    numhk7=str_change.find('hk7')
    numhk8=str_change.find('hk8')

    numvalch1=str_change.find('valch1') # измеренные значения по параметру
    numvalch2=str_change.find('valch2') # sen (вольт, градус, Ом) 
    numvalch3=str_change.find('valch3') # вещестыенные числа
    numvalch4=str_change.find('valch4') # только чтение
    numvalch5=str_change.find('valch5') # в новой версии теперь тут только градусы
    numvalch6=str_change.find('valch6')
    numvalch7=str_change.find('valch7')
    numvalch8=str_change.find('valch8')

    numdopch1=str_change.find('dopch1') # измеренные значения по каналам
    numdopch2=str_change.find('dopch2') # если термопара, то вольты
    numdopch3=str_change.find('dopch3') # если термосопротивление - омы
    numdopch4=str_change.find('dopch4') # вещестыенные числа
    numdopch5=str_change.find('dopch5') # только чтение
    numdopch6=str_change.find('dopch6')
    numdopch7=str_change.find('dopch7')
    numdopch8=str_change.find('dopch8')

    numvalrefu=str_change.find('valrefu') # опорный источник напряжения,
                                          # вещественное число, милливольты
                                          # чтение\запись

    numRr1=str_change.find('Rr1') # опорные резисторы, в омах
    numRr2=str_change.find('Rr2') # вещественные числа
    numRr3=str_change.find('Rr3') # чтение\запись

    numish1A=str_change.find('ish1A') # коэффициенты МТШ90. Данные свидетельства
    numish1B=str_change.find('ish1B') # вещественные числа
    numish1C=str_change.find('ish1C') # чтение\запись
    numish1D=str_change.find('ish1D')
    numish1Wal=str_change.find('ish1Wal')
    numish1Rttb=str_change.find('ish1Rttb')
    numish1M=str_change.find('ish1M')

    numish4C0=str_change.find('ish4C0') # - полином 9-й степени. Данные свидетельства.
    numish4C1=str_change.find('ish4C1') # вещественные числа
    numish4C2=str_change.find('ish4C2') # чтение\запись
    numish4C3=str_change.find('ish4C3')
    numish4C4=str_change.find('ish4C4')
    numish4C5=str_change.find('ish4C5')
    numish4C6=str_change.find('ish4C6')
    numish4C7=str_change.find('ish4C7')
    numish4C8=str_change.find('ish4C8')
    numish4C9=str_change.find('ish4C9')

    numish3tPPOZn=str_change.find('ish3tPPOZn') # темоЭДС от температуры ППО. 
    numish3tPPOAl=str_change.find('ish3tPPOAl') # Размерность милливольт, градус.
    numish3tPPOCu=str_change.find('ish3tPPOCu') # Данные свидетельства.
    numish3uPPOZn=str_change.find('ish3uPPOZn') # Вещественные числа
    numish3uPPOAl=str_change.find('ish3uPPOAl') # чтение\запись
    numish3uPPOCu=str_change.find('ish3uPPOCu')

    numish2tPROAl=str_change.find('ish2tPROAl') # темоЭДС от температуры ПPО.
    numish2tPROCu=str_change.find('ish2tPROCu') # Размерность миливольт, градус.
    numish2tPROPd=str_change.find('ish2tPROPd') # Данные свидетельства.
    numish2tPROPt=str_change.find('ish2tPROPt') # Вещественные числа
    numish2uPROAl=str_change.find('ish2uPROAl') # чтение\запись
    numish2uPROCu=str_change.find('ish2uPROCu')
    numish2uPROPd=str_change.find('ish2uPROPd')
    numish2uPROPt=str_change.find('ish2uPROPt')

    numrewerseChan=str_change.find('rewerseChan') # чтение запись перебор каналов (0 - прямое, 1 - обратное)
    numrewerseI=str_change.find('rewerseI') # чтение запись режим I (реверс тока 0 - прямое, 1 - обратное)

    numRp1=str_change.find('Rp1') # R выводов
    numRp2=str_change.find('Rp2') # вещественные числа (float)
    numRp3=str_change.find('Rp3') # учитывается при измерении термо-сопротивлений
    numRp4=str_change.find('Rp4')
    numRp5=str_change.find('Rp5')
    numRp6=str_change.find('Rp6')
    numRp7=str_change.find('Rp7')
    numRp8=str_change.find('Rp8')

    if str_change[0]=='R':  #read data
        if nummc1>-1:
            inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x100,1,MainWindow)
            if inbuff:
                par=inbuff[1]&0x0f
                mc1=meascurrentparstr(par)
                str_change=insert_equ_param(str_change,'mc1',mc1)
            else:
                str_change=insert_err_param(str_change,'mc1')    
        if nummc2>-1:
            inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x101,1,MainWindow)
            if inbuff:
                par=inbuff[1]&0x0f
                mc2=meascurrentparstr(par)
                str_change=insert_equ_param(str_change,'mc2',mc2)
            else:
                str_change=insert_err_param(str_change,'mc2')     
        if nummc3>-1:
            inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x102,1,MainWindow)
            if inbuff:
                par=inbuff[1]&0x0f
                mc3=meascurrentparstr(par)
                str_change=insert_equ_param(str_change,'mc3',mc3)
            else:
                str_change=insert_err_param(str_change,'mc3')     
        if nummc4>-1:
            inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x103,1,MainWindow)
            if inbuff:
                par=inbuff[1]&0x0f
                mc4=meascurrentparstr(par)
                str_change=insert_equ_param(str_change,'mc4',mc4)
            else:
                str_change=insert_err_param(str_change,'mc4')     
        if nummc5>-1:
            inbuff==ReadTwoBytesMBus(portname,boud,0x4d,0x104,1,MainWindow)
            if inbuff:
                par=inbuff[1]&0x0f
                mc5=meascurrentparstr(par)
                str_change=insert_equ_param(str_change,'mc5',mc5)
            else:
                str_change=insert_err_param(str_change,'mc5')     
        if nummc6>-1:
            inbuff==ReadTwoBytesMBus(portname,boud,0x4d,0x105,1,MainWindow)
            if inbuff:
                par=inbuff[1]&0x0f
                mc6=meascurrentparstr(par)
                str_change=insert_equ_param(str_change,'mc6',mc6)
            else:
                str_change=insert_err_param(str_change,'mc6')     
        if nummc7>-1:
            inbuff==ReadTwoBytesMBus(portname,boud,0x4d,0x106,1,MainWindow)
            if inbuff:
                par=inbuff[1]&0x0f
                mc7=meascurrentparstr(par)
                str_change=insert_equ_param(str_change,'mc7',mc7)
            else:
                str_change=insert_err_param(str_change,'mc7')     
        if nummc8>-1:
            inbuff==ReadTwoBytesMBus(portname,boud,0x4d,0x107,1,MainWindow)
            if inbuff:
                par=inbuff[1]&0x0f
                mc8=meascurrentparstr(par)
                str_change=insert_equ_param(str_change,'mc8',mc8)
            else:
                str_change=insert_err_param(str_change,'mc8')     
          
        if numRref1>-1:
            inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x100,1,MainWindow)
            if inbuff:
                parRref=inbuff[0]&0xf0
                Rref=Rrefparstr(parRref)
                str_change=insert_equ_param(str_change,'Rref1',Rref)
            else:
                str_change=insert_err_param(str_change,'Rref1')     
        if numRref2>-1:
            inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x101,1,MainWindow)
            if inbuff:
                parRref=inbuff[0]&0xf0
                Rref=Rrefparstr(parRref)
                str_change=insert_equ_param(str_change,'Rref2',Rref)
            else:
                str_change=insert_err_param(str_change,'Rref2')      
        if numRref3>-1:
            inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x102,1,MainWindow)
            if inbuff:
                parRref=inbuff[0]&0xf0
                Rref=Rrefparstr(parRref)
                str_change=insert_equ_param(str_change,'Rref3',Rref)
            else:
                str_change=insert_err_param(str_change,'Rref3')      
        if numRref4>-1:
            inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x103,1,MainWindow)
            if inbuff:
                parRref=inbuff[0]&0xf0
                Rref=Rrefparstr(parRref)
                str_change=insert_equ_param(str_change,'Rref4',Rref)
            else:
                str_change=insert_err_param(str_change,'Rref4')      
        if numRref5>-1:
            inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x104,1,MainWindow)
            if inbuff:
                parRref=inbuff[0]&0xf0
                Rref=Rrefparstr(parRref)
                str_change=insert_equ_param(str_change,'Rref5',Rref)
            else:
                str_change=insert_err_param(str_change,'Rref5')      
        if numRref6>-1:
            inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x105,1,MainWindow)
            if inbuff:
                parRref=inbuff[0]&0xf0
                Rref=Rrefparstr(parRref)
                str_change=insert_equ_param(str_change,'Rref6',Rref)
            else:
                str_change=insert_err_param(str_change,'Rref6')      
        if numRref7>-1:
            inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x106,1,MainWindow)
            if inbuff:
                parRref=inbuff[0]&0xf0
                Rref=Rrefparstr(parRref)
                str_change=insert_equ_param(str_change,'Rref7',Rref)
            else:
                str_change=insert_err_param(str_change,'Rref7')      
        if numRref8>-1:
            inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x107,1,MainWindow)
            if inbuff:
                parRref=inbuff[0]&0xf0
                Rref=Rrefparstr(parRref)
                str_change=insert_equ_param(str_change,'Rref8',Rref)
            else:
                str_change=insert_err_param(str_change,'Rref8')      

        if numsen1>-1:
            inbuff=ReadUShortMBus(portname,boud,0x4d,0x108,1,ia,MainWindow)
            if inbuff:
                sen=inbuff[0]
                sen1=sen[0]
                strvalsen1=strvalsen(sen1)
                str_change=insert_equ_param(str_change,'sen1',strvalsen1)
            else:
                str_change=insert_err_param(str_change,'sen1')      
        if numsen2>-1:
            inbuff=ReadUShortMBus(portname,boud,0x4d,0x109,1,ia,MainWindow)
            if inbuff:
                sen=inbuff[0]
                sen2=sen[0]
                strvalsen2=strvalsen(sen2)
                str_change=insert_equ_param(str_change,'sen2',strvalsen2)
            else:
                str_change=insert_err_param(str_change,'sen2')       
        if numsen3>-1:
            inbuff=ReadUShortMBus(portname,boud,0x4d,0x10a,1,ia,MainWindow)
            if inbuff:
                sen=inbuff[0]
                sen3=sen[0]
                strvalsen3=strvalsen(sen3)
                str_change=insert_equ_param(str_change,'sen3',strvalsen3)
            else:
                str_change=insert_err_param(str_change,'sen3')       
        if numsen4>-1:
            inbuff=ReadUShortMBus(portname,boud,0x4d,0x10b,1,ia,MainWindow)
            if inbuff:
                sen=inbuff[0]
                sen4=sen[0]
                strvalsen4=strvalsen(sen4)
                str_change=insert_equ_param(str_change,'sen4',strvalsen4)
            else:
                str_change=insert_err_param(str_change,'sen4')       
            
        if numsen5>-1:
            inbuff=ReadUShortMBus(portname,boud,0x4d,0x10c,1,ia,MainWindow)
            if inbuff:
                sen=inbuff[0]
                sen5=sen[0]
                strvalsen5=strvalsen(sen5)
                str_change=insert_equ_param(str_change,'sen5',strvalsen5)
            else:
                str_change=insert_err_param(str_change,'sen5')       
            
        if numsen6>-1:
            inbuff=ReadUShortMBus(portname,boud,0x4d,0x10d,1,ia,MainWindow)
            if inbuff:
                sen=inbuff[0]
                sen6=sen[0]
                strvalsen6=strvalsen(sen6)
                str_change=insert_equ_param(str_change,'sen6',strvalsen6)
            else:
                str_change=insert_err_param(str_change,'sen6')       
        if numsen7>-1:
            inbuff=ReadUShortMBus(portname,boud,0x4d,0x10e,1,ia,MainWindow)
            if inbuff:
                sen=inbuff[0]
                sen7=sen[0]
                strvalsen7=strvalsen(sen7)
                str_change=insert_equ_param(str_change,'sen7',strvalsen7)
            else:
                str_change=insert_err_param(str_change,'sen7')       
        if numsen8>-1:
            inbuff=ReadUShortMBus(portname,boud,0x4d,0x10f,1,ia,MainWindow)
            if inbuff:
                sen=inbuff[0]
                sen8=sen[0]
                strvalsen8=strvalsen(sen8)
                str_change=insert_equ_param(str_change,'sen8',strvalsen8)
            else:
                str_change=insert_err_param(str_change,'sen8')       
            
        if numhk1>-1:
            inbuff=ReadUShortMBus(portname,boud,0x4d,0x45,1,ia,MainWindow)
            if inbuff:
                hk=inbuff[0]
                hk1=hk[0]
                if hk1==0: parhk='ON'
                else: parhk='OFF'  
                str_change=insert_equ_param(str_change,'hk1',parhk)
            else:
                str_change=insert_err_param(str_change,'hk1')       
        if numhk2>-1:
            inbuff=ReadUShortMBus(portname,boud,0x4d,0x46,1,ia,MainWindow)
            if inbuff:
                hk=inbuff[0] 
                hk2=hk[0]
                if hk2==0: parhk='ON'
                else: parhk='OFF'   
                str_change=insert_equ_param(str_change,'hk2',parhk)
            else:
                str_change=insert_err_param(str_change,'hk2')        
        if numhk3>-1:
            inbuff=ReadUShortMBus(portname,boud,0x4d,0x47,1,ia,MainWindow)
            if inbuff:
                hk=inbuff[0]   
                hk3=hk[0]
                if hk3==0: parhk='ON'
                else: parhk='OFF'  
                str_change=insert_equ_param(str_change,'hk3',parhk)
            else:
                str_change=insert_err_param(str_change,'hk3')        
        if numhk4>-1:
            inbuff=ReadUShortMBus(portname,boud,0x4d,0x48,1,ia,MainWindow)
            if inbuff:
                hk=inbuff[0]   
                hk4=hk[0]
                if hk4==0: parhk='ON'
                else: parhk='OFF'   
                str_change=insert_equ_param(str_change,'hk4',parhk)
            else:
                str_change=insert_err_param(str_change,'hk4')        
        if numhk5>-1:
            inbuff=ReadUShortMBus(portname,boud,0x4d,0x49,1,ia,MainWindow)
            if inbuff:
                hk=inbuff[0]   
                hk5=hk[0]
                if hk5==0: parhk='ON'
                else: parhk='OFF'   
                str_change=insert_equ_param(str_change,'hk5',parhk)
            else:
                str_change=insert_err_param(str_change,'hk5')        
        if numhk6>-1:
            inbuff=ReadUShortMBus(portname,boud,0x4d,0x4a,1,ia,MainWindow)
            if inbuff:
                hk=inbuff[0]   
                hk6=hk[0]
                if hk6==0: parhk='ON'
                else: parhk='OFF'   
                str_change=insert_equ_param(str_change,'hk6',parhk)
            else:
                str_change=insert_err_param(str_change,'hk6')
        if numhk7>-1:
            inbuff=ReadUShortMBus(portname,boud,0x4d,0x4b,1,ia,MainWindow)
            if inbuff:
                hk=inbuff[0]
                hk7=hk[0]
                if hk7==0: parhk='ON'
                else: parhk='OFF'
                str_change=insert_equ_param(str_change,'hk7',parhk)
            else:
                str_change=insert_err_param(str_change,'hk7')
        if numhk8>-1:
            inbuff=ReadUShortMBus(portname,boud,0x4d,0x4c,1,ia,MainWindow)
            if inbuff:
                hk=inbuff[0]
                hk8=hk[0]
                if hk8==0: parhk='ON'
                else: parhk='OFF'
                str_change=insert_equ_param(str_change,'hk8',parhk)
            else:
                str_change=insert_err_param(str_change,'hk8')
           
        if numvalch1>-1:
            inbuff=ReadIntMBus(portname,boud,0x4d,0x0208,1,ia,MainWindow)
            if inbuff:
                floatch1=TuplToFloat(inbuff[0])
                floatch1/=10000
                str_change=insert_equ_param(str_change,'valch1',floatch1)
            else:
                str_change=insert_err_param(str_change,'valch1')
        if numvalch2>-1:
            inbuff=ReadIntMBus(portname,boud,0x4d,0x0209,1,ia,MainWindow)
            if inbuff:
                floatch2=TuplToFloat(inbuff[0])
                floatch2/=10000
                str_change=insert_equ_param(str_change,'valch2',floatch2)
            else:
                str_change=insert_err_param(str_change,'valch2')
        if numvalch3>-1:
            inbuff=ReadIntMBus(portname,boud,0x4d,0x020a,1,ia,MainWindow)
            if inbuff:
                floatch3=TuplToFloat(inbuff[0])
                floatch3/=10000
                str_change=insert_equ_param(str_change,'valch3',floatch3)
            else:
                str_change=insert_err_param(str_change,'valch3')
        if numvalch4>-1:
            inbuff=ReadIntMBus(portname,boud,0x4d,0x020b,1,ia,MainWindow)
            if inbuff:
                floatch4=TuplToFloat(inbuff[0]) 
                floatch4/=10000
                str_change=insert_equ_param(str_change,'valch4',floatch4)
            else:
                str_change=insert_err_param(str_change,'valch4')
        if numvalch5>-1:
            inbuff=ReadIntMBus(portname,boud,0x4d,0x020c,1,ia,MainWindow)
            if inbuff:
                floatch5=TuplToFloat(inbuff[0]) 
                floatch5/=10000
                str_change=insert_equ_param(str_change,'valch5',floatch5)
            else:
                str_change=insert_err_param(str_change,'valch5')
        if numvalch6>-1:
            inbuff=ReadIntMBus(portname,boud,0x4d,0x020d,1,ia,MainWindow)
            if inbuff:
                floatch6=TuplToFloat(inbuff[0]) 
                floatch6/=10000
                str_change=insert_equ_param(str_change,'valch6',floatch6)
            else:
                str_change=insert_err_param(str_change,'valch6')
        if numvalch7>-1:
            inbuff=ReadIntMBus(portname,boud,0x4d,0x020e,1,ia,MainWindow)
            if inbuff:
                floatch7=TuplToFloat(inbuff[0]) 
                floatch7/=10000
                str_change=insert_equ_param(str_change,'valch7',floatch7)
            else:
                str_change=insert_err_param(str_change,'valch7')
        if numvalch8>-1:
            inbuff=ReadIntMBus(portname,boud,0x4d,0x020f,1,ia,MainWindow)
            if inbuff:
                floatch8=TuplToFloat(inbuff[0]) 
                floatch8/=10000
                str_change=insert_equ_param(str_change,'valch8',floatch8)
            else:
                str_change=insert_err_param(str_change,'valch8')

        if numdopch1>-1:
            inbuff=ReadIntMBus(portname,boud,0x4d,0x0210,1,ia,MainWindow)
            if inbuff:
                floatch1=TuplToFloat(inbuff[0])
                floatch1/=10000
                str_change=insert_equ_param(str_change,'dopch1',floatch1)
            else:
                str_change=insert_err_param(str_change,'dopch1')
        if numdopch2>-1:
            inbuff=ReadIntMBus(portname,boud,0x4d,0x0211,1,ia,MainWindow)
            if inbuff:
                floatch2=TuplToFloat(inbuff[0])
                floatch2/=10000
                str_change=insert_equ_param(str_change,'dopch2',floatch2)
            else:
                str_change=insert_err_param(str_change,'dopch2')
        if numdopch3>-1:
            inbuff=ReadIntMBus(portname,boud,0x4d,0x0212,1,ia,MainWindow)
            if inbuff:
                floatch3=TuplToFloat(inbuff[0])
                floatch3/=10000
                str_change=insert_equ_param(str_change,'dopch3',floatch3)
            else:
                str_change=insert_err_param(str_change,'dopch3')
        if numdopch4>-1:
            inbuff=ReadIntMBus(portname,boud,0x4d,0x0213,1,ia,MainWindow)
            if inbuff:
                floatch4=TuplToFloat(inbuff[0])
                floatch4/=10000
                str_change=insert_equ_param(str_change,'dopch4',floatch4)
            else:
                str_change=insert_err_param(str_change,'dopch4')
        if numdopch5>-1:
            inbuff=ReadIntMBus(portname,boud,0x4d,0x0214,1,ia,MainWindow)
            if inbuff:
                floatch5=TuplToFloat(inbuff[0])
                floatch5/=10000
                str_change=insert_equ_param(str_change,'dopch5',floatch5)
            else:
                str_change=insert_err_param(str_change,'dopch5')
        if numdopch6>-1:
            inbuff=ReadIntMBus(portname,boud,0x4d,0x0215,1,ia,MainWindow)
            if inbuff:
                floatch6=TuplToFloat(inbuff[0])
                floatch6/=10000
                str_change=insert_equ_param(str_change,'dopch6',floatch6)
            else:
                str_change=insert_err_param(str_change,'dopch6')
        if numdopch7>-1:
            inbuff=ReadIntMBus(portname,boud,0x4d,0x0216,1,ia,MainWindow)
            if inbuff:
                floatch7=TuplToFloat(inbuff[0])
                floatch7/=10000
                str_change=insert_equ_param(str_change,'dopch7',floatch7)
            else:
                str_change=insert_err_param(str_change,'dopch7')
        if numdopch8>-1:
            inbuff=ReadIntMBus(portname,boud,0x4d,0x0217,1,ia,MainWindow)
            if inbuff:
                floatch8=TuplToFloat(inbuff[0])
                floatch8/=10000
                str_change=insert_equ_param(str_change,'dopch8',floatch8)
            else:
                str_change=insert_err_param(str_change,'dopch8')

        if numRp1>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x0057,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'Rp1',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'Rp1')
        if numRp2>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x0058,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'Rp2',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'Rp2')
        if numRp3>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x0059,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'Rp3',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'Rp3')
        if numRp4>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x005a,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'Rp4',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'Rp4')
        if numRp5>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x005b,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'Rp5',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'Rp5')
        if numRp6>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x005c,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'Rp6',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'Rp6')
        if numRp7>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x005d,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'Rp7',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'Rp7')
        if numRp8>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x005e,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'Rp8',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'Rp8')

        if numvalrefu>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x44,1,fa,MainWindow)
            if inbuff:
                floatvalrefu=inbuff[0]
                str_change=insert_equ_param(str_change,'valrefu',floatvalrefu)
            else:
                str_change=insert_err_param(str_change,'valrefu')
        if numRr1>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x40,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'Rr1',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'Rr1')
        if numRr2>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x41,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'Rr2',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'Rr2')
        if numRr3>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x42,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'Rr3',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'Rr3')
          
        if numish1A>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x4e,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish1A',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish1A')
        if numish1B>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x4f,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish1B',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish1B')   
        if numish1C>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x50,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish1C',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish1C')   
        if numish1D>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x51,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish1D',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish1D')  
        if numish1Wal>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x52,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish1Wal',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish1Wal')  
        if numish1Rttb>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x53,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish1Rttb',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish1Rttb')  
        if numish1M>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x54,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish1M',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish1M')  
            
        if numish4C0>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x55,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish4C0',inbuff[0]) 
        if numish4C1>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x56,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish4C1',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish4C1')  
        if numish4C2>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x57,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish4C2',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish4C2')  
        if numish4C3>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x58,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish4C3',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish4C3')  
        if numish4C4>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x59,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish4C4',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish4C4')  
        if numish4C5>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x5a,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish4C5',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish4C5')  
        if numish4C6>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x5b,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish4C6',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish4C6')  
        if numish4C7>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x5c,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish4C7',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish4C7')  
        if numish4C8>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x5d,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish4C8',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish4C8')  
        if numish4C9>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x5e,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish4C9',inbuff[0]) 
            else:
                str_change=insert_err_param(str_change,'ish4C9') 
           
        if numish3tPPOZn>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x60,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish3tPPOZn',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish3tPPOZn')
        if numish3tPPOAl>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x61,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish3tPPOAl',inbuff[0]) 
            else:
                str_change=insert_err_param(str_change,'ish3tPPOAl')
        if numish3tPPOCu>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x62,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish3tPPOCu',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish3tPPOCu') 
        if numish3uPPOZn>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x63,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish3uPPOZn',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish3uPPOZn') 
        if numish3uPPOAl>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x64,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish3uPPOAl',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish3uPPOAl')  
        if numish3uPPOCu>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x65,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish3uPPOCu',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish3uPPOCu')   

        if numish2tPROAl>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x66,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish2tPROAl',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish2tPROAl')   
        if numish2tPROCu>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x67,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish2tPROCu',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish2tPROCu')    
        if numish2tPROPd>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x68,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish2tPROPd',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish2tPROPd')     
        if numish2tPROPt>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x69,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish2tPROPt',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish2tPROPt')     
        if numish2uPROAl>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x6a,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish2uPROAl',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish2uPROAl')     
        if numish2uPROCu>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x6b,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish2uPROCu',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish2uPROCu')      
        if numish2uPROPd>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x6c,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish2uPROPd',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish2uPROPd')      
        if numish2uPROPt>-1:
            inbuff=ReadFloatMBus(portname,boud,0x4d,0x6d,1,fa,MainWindow)
            if inbuff:
                str_change=insert_equ_param(str_change,'ish2uPROPt',inbuff[0])
            else:
                str_change=insert_err_param(str_change,'ish2uPROPt')      

        if numrewerseChan>-1:
            inbuff=ReadUShortMBus(portname,boud,0x4d,0x55,1,ia,MainWindow)
            if inbuff:
                rewerseChan=inbuff[0]
                rewerseChan=rewerseChan[0]
                if rewerseChan==0: par='FF'
                else: par='RW'
                str_change=insert_equ_param(str_change,'rewerseChan',par)
            else:
                str_change=insert_err_param(str_change,'rewerseChan')

        if numrewerseI>-1:
            inbuff=ReadUShortMBus(portname,boud,0x4d,0x56,1,ia,MainWindow)
            if inbuff:
                rewerseI=inbuff[0]
                rewerseI=rewerseI[0]
                if rewerseI==0: par='FF'
                else: par='RW'
                str_change=insert_equ_param(str_change,'rewerseI',par)
            else:
                str_change=insert_err_param(str_change,'rewerseI')

        strout=str_change  
        return strout

    elif str_change[0]=='W':  #whrite data
        strout='W'
      
        if numsen1>-1:
            parval=extract_val_param(str_change,'sen1')
            senval=valsenstr(parval)
            if isinstance(senval,str):
                strout+=',sen1-errval'
            else:
                ia[0]=senval
                if WriteUint16_tMBus(portname,boud,0x4d,0x108,1,ia,MainWindow):
                    strout+=',sen1-OK'
                else:
                    strout+=',sen1-Err'

        if numsen2>-1:
            parval=extract_val_param(str_change,'sen2') 
            senval=valsenstr(parval)
            if isinstance(senval,str):
                strout+=',sen2-errval'
            else:
                ia[0]=senval
                if WriteUint16_tMBus(portname,boud,0x4d,0x109,1,ia,MainWindow):
                    strout+=',sen2-OK'
                else:
                    strout+=',sen2-Err'

        if numsen3>-1:
            parval=extract_val_param(str_change,'sen3') 
            senval=valsenstr(parval)
            if isinstance(senval,str):
                strout+=',sen3-errval'
            else:
                ia[0]=senval
                if WriteUint16_tMBus(portname,boud,0x4d,0x10a,1,ia,MainWindow):
                    strout+=',sen3-OK'
                else:
                    strout+=',sen3-Err'

        if numsen4>-1:
            parval=extract_val_param(str_change,'sen4') 
            senval=valsenstr(parval)
            if isinstance(senval,str):
                strout+=',sen4-errval'
            else:
                ia[0]=senval
                if WriteUint16_tMBus(portname,boud,0x4d,0x10b,1,ia,MainWindow):
                    strout+=',sen4-OK'
                else:
                    strout+=',sen4-Err'

        if numsen5>-1:
            parval=extract_val_param(str_change,'sen5') 
            senval=valsenstr(parval)
            if isinstance(senval,str):
                strout+=',sen5-errval'
            else:
                ia[0]=senval
                if WriteUint16_tMBus(portname,boud,0x4d,0x10c,1,ia,MainWindow):
                    strout+=',sen5-OK'
                else:
                    strout+=',sen5-Err'

        if numsen6>-1:
            parval=extract_val_param(str_change,'sen6') 
            senval=valsenstr(parval)
            if isinstance(senval,str):
                strout+=',sen6-errval'
            else:
                ia[0]=senval
                if WriteUint16_tMBus(portname,boud,0x4d,0x10d,1,ia,MainWindow):
                    strout+=',sen6-OK'
                else:
                    strout+=',sen6-Err'

        if numsen7>-1:
            parval=extract_val_param(str_change,'sen7') 
            senval=valsenstr(parval)
            if isinstance(senval,str):
                strout+=',sen7-errval'
            else:
                ia[0]=senval
                if WriteUint16_tMBus(portname,boud,0x4d,0x10e,1,ia,MainWindow):
                    strout+=',sen7-OK'
                else:
                    strout+=',sen7-Err'

        if numsen8>-1:
            parval=extract_val_param(str_change,'sen8') 
            senval=valsenstr(parval)
            if isinstance(senval,str):
                strout+=',sen8-errval'
            else:
                ia[0]=senval
                if WriteUint16_tMBus(portname,boud,0x4d,0x10f,1,ia,MainWindow):
                    strout+=',sen8-OK'
                else:
                    strout+=',sen8-Err'

          
        if numRref1>-1:
            parval=extract_val_param(str_change,'Rref1')
            parRref=Rrefrstrpar(parval)
            if parRref=='errval':
                strout+=',Rref1-errval'
            else:
                inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x100,1,MainWindow)
                if inbuff:
                    inbuff[0]&=0x0f
                    inbuff[0]|=Rrefrstrpar(parval)
                    if WriteTwoBytesMBus(portname,boud,0x4d,0X100,1,inbuff,MainWindow):
                        strout+=',Rref1-OK'
                    else:
                        strout+=',Rref1-Err'
                else:
                    strout+=',Rref1-Err'
        if numRref2>-1:
            parval=extract_val_param(str_change,'Rref2')
            parRref=Rrefrstrpar(parval)
            if parRref=='errval':
                strout+=',Rrer2-errval'
            else:
                inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x101,1,MainWindow)
                if inbuff:
                    inbuff[0]&=0x0f
                    inbuff[0]|=Rrefrstrpar(parval)
                    if WriteTwoBytesMBus(portname,boud,0x4d,0X101,1,inbuff,MainWindow):
                        strout+=',Rref2-OK'
                    else:
                        strout+=',Rref2-Err'
                else:
                    strout+=',Rref2-Err'
        if numRref3>-1:
            parval=extract_val_param(str_change,'Rref3')
            parRref=Rrefrstrpar(parval)
            if parRref=='errval':
                strout+=',Rref3-errval'
            else:
                inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x102,1,MainWindow)
                if inbuff:
                    inbuff[0]&=0x0f
                    inbuff[0]|=Rrefrstrpar(parval)
                    if WriteTwoBytesMBus(portname,boud,0x4d,0X102,1,inbuff,MainWindow):
                        strout+=',Rref3-OK'
                    else:
                        strout+=',Rref3-Err'
                else:
                    strout+=',Rref3-Err'
        if numRref4>-1:
            parval=extract_val_param(str_change,'Rref4')
            parRref=Rrefrstrpar(parval)
            if parRref=='errval':
                strout+=',Rref4-errval'
            else:
                inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x103,1,MainWindow)
                if inbuff:
                    inbuff[0]&=0x0f
                    inbuff[0]|=Rrefrstrpar(parval)
                    if WriteTwoBytesMBus(portname,boud,0x4d,0X103,1,inbuff,MainWindow):
                        strout+=',Rref4-OK'
                    else:
                        strout+=',Rref4-Err'
                else:
                    strout+=',Rref4-Err'
        if numRref5>-1:
            parval=extract_val_param(str_change,'Rref5')
            parRref=Rrefrstrpar(parval)
            if parRref=='errval':
                strout+=',Rref5-errval'
            else:
                inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x104,1,MainWindow)
                if inbuff:
                    inbuff[0]&=0x0f
                    inbuff[0]|=Rrefrstrpar(parval)
                    if WriteTwoBytesMBus(portname,boud,0x4d,0X104,1,inbuff,MainWindow):
                        strout+=',Rref5-OK'
                    else:
                        strout+=',Rref5-Err'
                else:
                    strout+=',Rref5-Err'
        if numRref6>-1:
            parval=extract_val_param(str_change,'Rref6')
            parRref=Rrefrstrpar(parval)
            if parRref=='errval':
                strout+=',Rref6-errval'
            else:
                inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x105,1,MainWindow)
                if inbuff:
                    inbuff[0]&=0x0f
                    inbuff[0]|=Rrefrstrpar(parval)
                    if WriteTwoBytesMBus(portname,boud,0x4d,0X105,1,inbuff,MainWindow):
                        strout+=',Rref6-OK'
                    else:
                        strout+=',Rref6-Err'
                else:
                    strout+=',Rref6-Err'
        if numRref7>-1:
            parval=extract_val_param(str_change,'Rref7')
            parRref=Rrefrstrpar(parval)
            if parRref=='errval':
                strout+=',Rref7-errval'
            else:
                inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x106,1,MainWindow)
                if inbuff:
                    inbuff[0]&=0x0f
                    inbuff[0]|=Rrefrstrpar(parval)
                    if WriteTwoBytesMBus(portname,boud,0x4d,0X106,1,inbuff,MainWindow):
                        strout+=',Rref7-OK'
                    else:
                        strout+=',Rref7-Err'
                else:
                    strout+=',Rref7-Err'
        if numRref8>-1:
            parval=extract_val_param(str_change,'Rref8')
            parRref=Rrefrstrpar(parval)
            if parRref=='errval':
                strout+=',Rref8-errval'
            else:
                inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x107,1,MainWindow)
                if inbuff:
                    inbuff[0]&=0x0f
                    inbuff[0]|=Rrefrstrpar(parval)
                    if WriteTwoBytesMBus(portname,boud,0x4d,0X107,1,inbuff,MainWindow):
                        strout+=',Rref8-OK'
                    else:
                        strout+=',Rref8-Err'
                else:
                    strout+=',Rref8-Err'
              
        if nummc1>-1:
            parval=extract_val_param(str_change,'mc1')
            parmc=meascurrentstrpar(parval)
            if parmc=='errval':
                strout+=',mc1-errval'
            else:
                inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x100,1,MainWindow)
                if inbuff:
                    inbuff[1]&=0xf0
                    inbuff[1]|=parmc
                    if WriteTwoBytesMBus(portname,boud,0x4d,0X100,1,inbuff,MainWindow):
                        strout+=',mc1-OK'
                    else:
                        strout+=',mc1-Err'
                else:
                    strout+=',mc1-Err'
           
        if nummc2>-1:
            parval=extract_val_param(str_change,'mc2')
            parmc= meascurrentstrpar (parval)
            if parmc=='errval':
                strout+=',mc2-errval'
            else:
                inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x101,1,MainWindow)
                if inbuff:
                    inbuff[1]&=0xf0
                    inbuff[1]|=parmc
                    if WriteTwoBytesMBus(portname,boud,0x4d,0X101,1,inbuff,MainWindow):
                        strout+=',mc2-OK'
                    else:
                        strout+=',mc2-Err'
                else:
                    strout+=',mc2-Err'
        if nummc3>-1:
            parval=extract_val_param(str_change,'mc3')
            parmc= meascurrentstrpar (parval)
            if parmc=='errval':
                strout+=',mc3-errval'
            else: 
                inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x102,1,MainWindow)
                if inbuff:
                    inbuff[1]&=0xf0
                    inbuff[1]|=parmc
                    if WriteTwoBytesMBus(portname,boud,0x4d,0X102,1,inbuff,MainWindow):
                        strout+=',mc3-OK'
                    else:
                        strout+=',mc3-Err'
                else:
                    strout+=',mc3-Err'
        if nummc4>-1:
            parval=extract_val_param(str_change,'mc4')
            parmc= meascurrentstrpar (parval)
            if parmc=='errval':
                strout+=',mc4-errval'
            else:
                inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x103,1,MainWindow)
                if inbuff:
                    inbuff[1]&=0xf0
                    inbuff[1]|=parmc
                    if WriteTwoBytesMBus(portname,boud,0x4d,0X103,1,inbuff,MainWindow):
                        strout+=',mc4-OK'
                    else:
                        strout+=',mc4-Err'
                else:
                    strout+=',mc4-Err'
           
        if nummc5>-1:
            parval=extract_val_param(str_change,'mc5')
            parmc= meascurrentstrpar (parval)
            if parmc=='errval':
                strout+=',mc5-errval'
            else:
                inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x104,1,MainWindow)
                if inbuff:
                    inbuff[1]&=0xf0
                    inbuff[1]|=parmc
                    if WriteTwoBytesMBus(portname,boud,0x4d,0X104,1,inbuff,MainWindow):
                        strout+=',mc5-OK'
                    else:
                        strout+=',mc5-Err'
                else:
                    strout+=',mc5-Err'
        if nummc6>-1:
            parval=extract_val_param(str_change,'mc6')
            parmc= meascurrentstrpar (parval)
            if parmc=='errval':
                strout+=',mc6-errval'
            else:
                inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x105,1,MainWindow)
                if inbuff:
                    inbuff[1]&=0xf0
                    inbuff[1]|=parmc
                    if WriteTwoBytesMBus(portname,boud,0x4d,0X105,1,inbuff,MainWindow):
                        strout+=',mc6-OK'
                    else:
                        strout+=',mc6-Err'
                else:
                    strout+=',mc6-Err'
          
        if nummc7>-1:
            parval=extract_val_param(str_change,'mc7')
            parmc= meascurrentstrpar (parval)
            if parmc=='errval':
                strout+=',mc7-errval'
            else:
                inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x106,1,MainWindow)
                if inbuff:
                    inbuff[1]&=0xf0
                    inbuff[1]|=parmc
                    if WriteTwoBytesMBus(portname,boud,0x4d,0X106,1,inbuff,MainWindow):
                        strout+=',mc7-OK'
                    else:
                        strout+=',mc7-Err'
                else:
                    strout+=',mc7-Err'
           
        if nummc8>-1:
            parval=extract_val_param(str_change,'mc8')
            parmc= meascurrentstrpar (parval)
            if parmc=='errval':
                strout+=',mc8-errval'
            else:
                inbuff=ReadTwoBytesMBus(portname,boud,0x4d,0x107,1,MainWindow)
                if inbuff:
                    inbuff[1]&=0xf0
                    inbuff[1]|=parmc
                    if WriteTwoBytesMBus(portname,boud,0x4d,0X107,1,inbuff,MainWindow):
                        strout+=',mc8-OK'
                    else:
                        strout+=',mc8-Err'
                else:
                    strout+=',mc8-Err'

        if numhk1>-1:
            parval=extract_val_param(str_change,'hk1') 
            if parval=='ON':
                ba2[0]=0
                ba2[1]=0
                if WriteTwoBytesMBus(portname,boud,0x4d,0X45,1,ba2,MainWindow):
                    strout+=',hk1-ON'
                else: strout+=',hk1-Err'
            elif parval=='OFF':
                ba2[0]=0xff
                ba2[1]=0xff
                if WriteTwoBytesMBus(portname,boud,0x4d,0X45,1,ba2,MainWindow):
                    strout+=',hk1-OFF'
                else: strout+=',hk1-Err'
            else: strout+=',hk1-errval'
        if numhk2>-1:
            parval=extract_val_param(str_change,'hk2')
            if parval=='ON':
                ba2[0]=0
                ba2[1]=0
                if WriteTwoBytesMBus(portname,boud,0x4d,0X46,1,ba2,MainWindow):
                    strout+=',hk2-ON'
                else: strout+=',hk2-Err'
            elif parval=='OFF':
                ba2[0]=0xff
                ba2[1]=0xff
                if WriteTwoBytesMBus(portname,boud,0x4d,0X46,1,ba2,MainWindow):
                    strout+=',hk2-OFF'
                else: strout+=',hk2-Err'
            else: strout+=',hk2-errval'
           
        if numhk3>-1:
            parval=extract_val_param(str_change,'hk3')
            if parval=='ON':
                ba2[0]=0
                ba2[1]=0
                if WriteTwoBytesMBus(portname,boud,0x4d,0X47,1,ba2,MainWindow):
                    strout+=',hk3-ON'
                else: strout+=',hk3-Err'
            elif parval=='OFF':
                ba2[0]=0xff
                ba2[1]=0xff
                if WriteTwoBytesMBus(portname,boud,0x4d,0X47,1,ba2,MainWindow):
                    strout+=',hk3-OFF'
                else: strout+=',hk3-Err'
            else: strout+=',hk3-errval'
            
        if numhk4>-1:
            parval=extract_val_param(str_change,'hk4')
            if parval=='ON':
                ba2[0]=0
                ba2[1]=0
                if WriteTwoBytesMBus(portname,boud,0x4d,0X48,1,ba2,MainWindow):
                    strout+=',hk4-ON'
                else: strout+=',hk4-Err'
            elif parval=='OFF':
                ba2[0]=0xff
                ba2[1]=0xff
                if WriteTwoBytesMBus(portname,boud,0x4d,0X48,1,ba2,MainWindow):
                    strout+=',hk4-OFF'
                else: strout+=',hk4-Err'
            else: strout+=',hk4-errval'
            
        if numhk5>-1:
            parval=extract_val_param(str_change,'hk5')
            if parval=='ON':
                ba2[0]=0
                ba2[1]=0
                if WriteTwoBytesMBus(portname,boud,0x4d,0X49,1,ba2,MainWindow):
                    strout+=',hk5-ON'
                else: strout+=',hk5-Err'
            elif parval=='OFF':
                ba2[0]=0xff
                ba2[1]=0xff
                if WriteTwoBytesMBus(portname,boud,0x4d,0X49,1,ba2,MainWindow):
                    strout+=',hk5-OFF'
                else: strout+=',hk5-Err'
            else: strout+=',hk5-errval'
            
        if numhk6>-1:
            parval=extract_val_param(str_change,'hk6')
            if parval=='ON':
                ba2[0]=0
                ba2[1]=0
                if WriteTwoBytesMBus(portname,boud,0x4d,0X4a,1,ba2,MainWindow):
                    strout+=',hk6-ON'
                else: strout+=',hk6-Err'
            elif parval=='OFF':
                ba2[0]=0xff
                ba2[1]=0xff
                if WriteTwoBytesMBus(portname,boud,0x4d,0X4a,1,ba2,MainWindow):
                    strout+=',hk6-OFF'
                else: strout+=',hk6-Err'
            else: strout+=',hk6-errval'
            
        if numhk7>-1:
            parval=extract_val_param(str_change,'hk7')
            if parval=='ON':
                ba2[0]=0
                ba2[1]=0
                if WriteTwoBytesMBus(portname,boud,0x4d,0X4b,1,ba2,MainWindow):
                    strout+=',hk7-ON'
                else: strout+=',hk1-Err'
            elif parval=='OFF':
                ba2[0]=0xff
                ba2[1]=0xff
                if WriteTwoBytesMBus(portname,boud,0x4d,0X4b,1,ba2,MainWindow):
                    strout+=',hk7-OFF'
                else: strout+=',hk7-Err'
            else: strout+=',hk7-errval'
            
        if numhk8>-1:
            parval=extract_val_param(str_change,'hk8')
            if parval=='ON':
                ba2[0]=0
                ba2[1]=0
                if WriteTwoBytesMBus(portname,boud,0x4d,0X4c,1,ba2,MainWindow):
                    strout+=',hk8-ON'
                else: strout+=',hk8-Err'
            elif parval=='OFF':
                ba2[0]=0xff
                ba2[1]=0xff
                if WriteTwoBytesMBus(portname,boud,0x4d,0X4c,1,ba2,MainWindow):
                    strout+=',hk8-OFF'
                else: strout+=',hk8-Err'
            else: strout+=',hk8-errval'

        if numrewerseChan>-1:
            parval=extract_val_param(str_change,'rewerseChan')
            if parval=='FF':
                ba2[0]=0
                ba2[1]=0
                if WriteTwoBytesMBus(portname,boud,0x4d,0X55,1,ba2,MainWindow):
                    strout+=',rewerseChan-FF'
                else: strout+=',rewerseChan-Err'
            elif parval=='RW':
                ba2[0]=0x00
                ba2[1]=0x01
                if WriteTwoBytesMBus(portname,boud,0x4d,0X55,1,ba2,MainWindow):
                    strout+=',rewerseChan-RW'
                else: strout+=',rewerseChan-Err'
            else: strout+=',rewerseChan-errval'
            
        if numrewerseI>-1:
            parval=extract_val_param(str_change,'rewerseI')
            if parval=='FF':
                ba2[0]=0
                ba2[1]=0
                if WriteTwoBytesMBus(portname,boud,0x4d,0X56,1,ba2,MainWindow):
                    strout+=',rewerseI-FF'
                else: strout+=',rewerseI-Err'
            elif parval=='RW':
                ba2[0]=0x00
                ba2[1]=0x01
                if WriteTwoBytesMBus(portname,boud,0x4d,0X56,1,ba2,MainWindow):
                    strout+=',rewerseI-RW'
                else: strout+=',rewerseI-Err'
            else: strout+=',rewerseI-errval'

        if numRr1>-1:
            parval=str_par_ToFloat(str_change,'Rr1')
            if isinstance(parval,str):
                strout+=',Rr1-'
                strout+=parval
            else: 
                fa[0]=parval
                wrf=WriteFloatMBus(portname,boud,0x4d,0x40,1,fa,MainWindow)
                if wrf:
                    strout+=',Rr1-OK'
                else:
                    strout+=',Rr1-Err'

        if numRr2>-1:
            parval=str_par_ToFloat(str_change,'Rr2')
            if isinstance(parval,str):
                strout+=',Rr2-'
                strout+=parval
            else: 
                fa[0]=parval
                wrf=WriteFloatMBus(portname,boud,0x4d,0x41,1,fa,MainWindow)
                if wrf:  
                    strout+=',Rr2-OK'
                else:
                    strout+=',Rr2-Err'

        if numRr3>-1:
            parval=str_par_ToFloat(str_change,'Rr3')
            if isinstance(parval,str):
                strout+=',Rr3-'
                strout+=parval
            else: 
                fa[0]=parval
                wrf=WriteFloatMBus(portname,boud,0x4d,0x42,1,fa,MainWindow)
                if wrf:
                    strout+=',Rr3-OK'
                else:
                    strout+=',Rr3-Err'

        if numRp1>-1:
            parval=str_par_ToFloat(str_change,'Rp1')
            if isinstance(parval,str):
                strout+=',Rp1-'
                strout+=parval
            else: 
                fa[0]=parval
                wrf=WriteFloatMBus(portname,boud,0x4d,0x57,1,fa,MainWindow)
                if wrf:
                    strout+=',Rp1-OK'
                else:
                    strout+=',Rp1-Err'
        if numRp2>-1:
            parval=str_par_ToFloat(str_change,'Rp2')
            if isinstance(parval,str):
                strout+=',Rp2-'
                strout+=parval
            else: 
                fa[0]=parval
                wrf=WriteFloatMBus(portname,boud,0x4d,0x58,1,fa,MainWindow)
                if wrf:
                    strout+=',Rp2-OK'
                else:
                    strout+=',Rp2-Err'
        if numRp3>-1:
            parval=str_par_ToFloat(str_change,'Rp3')
            if isinstance(parval,str):
                strout+=',Rp3-'
                strout+=parval
            else: 
                fa[0]=parval
                wrf=WriteFloatMBus(portname,boud,0x4d,0x59,1,fa,MainWindow)
                if wrf:
                    strout+=',Rp3-OK'
                else:
                    strout+=',Rp3-Err'
        if numRp4>-1:
            parval=str_par_ToFloat(str_change,'Rp4')
            if isinstance(parval,str):
                strout+=',Rp4-'
                strout+=parval
            else: 
                fa[0]=parval
                wrf=WriteFloatMBus(portname,boud,0x4d,0x5a,1,fa,MainWindow)
                if wrf:
                    strout+=',Rp4-OK'
                else:
                    strout+=',Rp4-Err'
        if numRp5>-1:
            parval=str_par_ToFloat(str_change,'Rp5')
            if isinstance(parval,str):
                strout+=',Rp5-'
                strout+=parval
            else: 
                fa[0]=parval
                wrf=WriteFloatMBus(portname,boud,0x4d,0x5b,1,fa,MainWindow)
                if wrf:
                    strout+=',Rp5-OK'
                else:
                    strout+=',Rp5-Err'
        if numRp6>-1:
            parval=str_par_ToFloat(str_change,'Rp6')
            if isinstance(parval,str):
                strout+=',Rp6-'
                strout+=parval
            else: 
                fa[0]=parval
                wrf=WriteFloatMBus(portname,boud,0x4d,0x5c,1,fa,MainWindow)
                if wrf:
                    strout+=',Rp6-OK'
                else:
                    strout+=',Rp6-Err'
        if numRp7>-1:
            parval=str_par_ToFloat(str_change,'Rp7')
            if isinstance(parval,str):
                strout+=',Rp7-'
                strout+=parval
            else: 
                fa[0]=parval
                wrf=WriteFloatMBus(portname,boud,0x4d,0x5d,1,fa,MainWindow)
                if wrf:
                    strout+=',Rp7-OK'
                else:
                    strout+=',Rp7-Err'
        if numRp8>-1:
            parval=str_par_ToFloat(str_change,'Rp8')
            if isinstance(parval,str):
                strout+=',Rp8-'
                strout+=parval
            else: 
                fa[0]=parval
                wrf=WriteFloatMBus(portname,boud,0x4d,0x5e,1,fa,MainWindow)
                if wrf:
                    strout+=',Rp8-OK'
                else:
                    strout+=',Rp8-Err'

        if numish1A>-1:
            parval=str_par_ToFloat(str_change,'ish1A')
            if isinstance(parval,str):
                strout+=',ish1A-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x4e,1,fa,MainWindow):
                    strout+=',ish1A-OK'
                else:
                    strout+=',ish1A-Err'
        if numish1B>-1:
            parval=str_par_ToFloat(str_change,'ish1B')
            if isinstance(parval,str):
                strout+=',ish1B-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x4f,1,fa,MainWindow):
                    strout+=',ish1B-OK'
                else:
                    strout+=',ish1B-Err'
        if numish1C>-1:
            parval=str_par_ToFloat(str_change,'ish1C')
            if isinstance(parval,str):
                strout+=',ish1C-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x50,1,fa,MainWindow):
                    strout+=',ish1C-OK'
                else:
                    strout+=',ish1C-Err'
        if numish1D>-1:
            parval=str_par_ToFloat(str_change,'ish1D')
            if isinstance(parval,str):
                strout+=',ish1D-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x51,1,fa,MainWindow):
                    strout+=',ish1D-OK'
                else:
                    strout+=',ish1D-Err'
        if numish1Wal>-1:
            parval=str_par_ToFloat(str_change,'ish1Wal')
            if isinstance(parval,str):
                strout+=',ish1Wal-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x52,1,fa,MainWindow):
                    strout+=',ish1Wal-OK'
                else:
                    strout+=',ish1Wal-Err'
        if numish1Rttb>-1:
            parval=str_par_ToFloat(str_change,'ish1Rttb')
            if isinstance(parval,str):
                strout+=',ish1Rttb-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x53,1,fa,MainWindow):
                    strout+=',ish1Rttb-OK'
                else:
                    strout+=',ish1Rttb-Err'
        if numish1M>-1:
            parval=str_par_ToFloat(str_change,'ish1M')
            if isinstance(parval,str):
                strout+=',ish1M-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x54,1,fa,MainWindow):
                    strout+=',ish1M-OK'
                else:
                    strout+=',ish1M-Err'
             
        if numish4C0>-1:
            parval=str_par_ToFloat(str_change,'ish4C0')
            if isinstance(parval,str):
                strout+=',ish4C0-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x55,1,fa,MainWindow):
                    strout+=',ish4C0-OK'
                else:
                    strout+=',ish4C0-Err'
        if numish4C1>-1:
            parval=str_par_ToFloat(str_change,'ish4C1')
            if isinstance(parval,str):
                strout+=',ish4C1-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x56,1,fa,MainWindow):
                    strout+=',ish4C1-OK'
                else:
                    strout+=',ish4C1-Err'
        if numish4C2>-1:
            parval=str_par_ToFloat(str_change,'ish4C2')
            if isinstance(parval,str):
                strout+=',ish4C2-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x57,1,fa,MainWindow):
                    strout+=',ish4C2-OK'
                else:
                    strout+=',ish4C2-Err'
        if numish4C3>-1:
            parval=str_par_ToFloat(str_change,'ish4C3')
            if isinstance(parval,str):
                strout+=',ish4C3-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x58,1,fa,MainWindow):
                    strout+=',ish4C3-OK'
                else:
                    strout+=',ish4C3-Err'
        if numish4C4>-1:
            parval=str_par_ToFloat(str_change,'ish4C4')
            if isinstance(parval,str):
                strout+=',ish4C4-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x59,1,fa,MainWindow):
                    strout+=',ish4C4-OK'
                else:
                    strout+=',ish4C4-Err'
        if numish4C5>-1:
            parval=str_par_ToFloat(str_change,'ish4C5')
            if isinstance(parval,str):
                strout+=',ish4C5-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x5a,1,fa,MainWindow):
                    strout+=',ish4C5-OK'
                else:
                    strout+=',ish4C5-Err'
        if numish4C6>-1:
            parval=str_par_ToFloat(str_change,'ish4C6')
            if isinstance(parval,str):
                strout+=',ish4C6-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x5b,1,fa,MainWindow):
                    strout+=',ish4C6-OK'
                else:
                    strout+=',ish4C6-Err'
        if numish4C7>-1:
            parval=str_par_ToFloat(str_change,'ish4C7')
            if isinstance(parval,str):
                strout+=',ish4C7-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x5c,1,fa,MainWindow):
                    strout+=',ish4C7-OK'
                else:
                    strout+=',ish4C7-Err'
        if numish4C8>-1:
            parval=str_par_ToFloat(str_change,'ish4C8')
            if isinstance(parval,str):
                strout+=',ish4C8-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x5d,1,fa,MainWindow):
                    strout+=',ish4C8-OK'
                else:
                    strout+=',ish4C8-Err'
        if numish4C9>-1:
            parval=str_par_ToFloat(str_change,'ish4C9')
            if isinstance(parval,str):
                strout+=',ish4C9-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x5e,1,fa,MainWindow):
                    strout+=',ish4C9-OK'
                else:
                    strout+=',ish4C9-Err'
          
        if numish3tPPOZn>-1:
            parval=str_par_ToFloat(str_change,'ish3tPPOZn')
            if isinstance(parval,str):
                strout+=',ish3tPPOZn-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x60,1,fa,MainWindow):
                    strout+=',ish3tPPOZn-OK'
                else:
                    strout+=',ish3tPPOZn-Err'
        if numish3tPPOAl>-1:
            parval=str_par_ToFloat(str_change,'ish3tPPOAl')
            if isinstance(parval,str):
                strout+=',ish3tPPOAl-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x61,1,fa,MainWindow):
                    strout+=',ish3tPPOAl-OK'
                else:
                    strout+=',ish3tPPOAl-Err'
        if numish3tPPOCu>-1:
            parval=str_par_ToFloat(str_change,'ish3tPPOCu')
            if isinstance(parval,str):
                strout+=',ish3tPPOCu-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x62,1,fa,MainWindow):
                    strout+=',ish3tPPOCu-OK'
                else:
                    strout+=',ish3tPPOCu-Err'
        if numish3uPPOZn>-1:
            parval=str_par_ToFloat(str_change,'ish3uPPOZn')
            if isinstance(parval,str):
                strout+=',ish3uPPOZn-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x63,1,fa,MainWindow):
                    strout+=',ish3uPPOZn-OK'
                else:
                    strout+=',ish3uPPOZn-Err'
        if numish3uPPOAl>-1:
            parval=str_par_ToFloat(str_change,'ish3uPPOAl')
            if isinstance(parval,str):
                strout+=',ish3uPPOAl-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x64,1,fa,MainWindow):
                    strout+=',ish3uPPOAl-OK'
                else:
                    strout+=',ish3uPPOAl-Err'
        if numish3tPPOCu>-1:
            parval=str_par_ToFloat(str_change,'ish3tPPOCu')
            if isinstance(parval,str):
                strout+=',ish3uPPOCu-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x65,1,fa,MainWindow):
                    strout+=',ish3uPPOCu-OK'
                else:
                    strout+=',ish3uPPOCu-Err'
          

        if numish2tPROAl>-1:
            parval=str_par_ToFloat(str_change,'ish2tPROAl')
            if isinstance(parval,str):
                strout+=',ish2tPROAl-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x66,1,fa,MainWindow):
                    strout+=',ish2tPROAl-OK'
                else:
                    strout+=',ish2tPROAl-Err'
        if numish2tPROCu>-1:
            parval=str_par_ToFloat(str_change,'ish2tPROCu')
            if isinstance(parval,str):
                strout+=',ish2tPROCu-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x67,1,fa,MainWindow):
                    strout+=',ish2tPROCu-OK'
                else:
                    strout+=',ish2tPROCu-Err'
        if numish2tPROPd>-1:
            parval=str_par_ToFloat(str_change,'ish2tPROPd')
            if isinstance(parval,str):
                strout+=',ish2tPROPd-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x68,1,fa,MainWindow):
                    strout+=',ish2tPROPd-OK'
                else:
                    strout+=',ish2tPROPd-Err'
        if numish2tPROPt>-1:
            parval=str_par_ToFloat(str_change,'ish2tPROPt')
            if isinstance(parval,str):
                strout+=',ish2tPROPt-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x69,1,fa,MainWindow):
                    strout+=',ish2tPROPt-OK'
                else:
                    strout+=',ish2tPROPt-Err'
        if numish2uPROAl>-1:
            parval=str_par_ToFloat(str_change,'ish2uPROAl')
            if isinstance(parval,str):
                strout+=',ish2uPROAl-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x6a,1,fa,MainWindow):
                    strout+=',ish2uPROAl-OK'
                else:
                    strout+=',ish2uPROAl-Err'
        if numish2uPROCu>-1:
            parval=str_par_ToFloat(str_change,'ish2uPROCu')
            if isinstance(parval,str):
                strout+=',ish2uPROCu-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x6b,1,fa,MainWindow):
                    strout+=',ish2uPROCu-OK'
                else:
                    strout+=',ish2uPROCu-Err'
        if numish2uPROPd>-1:
            parval=str_par_ToFloat(str_change,'ish2uPROPd')
            if isinstance(parval,str):
                strout+=',ish2uPROPd-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x6c,1,fa,MainWindow):
                    strout+=',ish2uPROPd-OK'
                else:
                    strout+=',ish2uPROPd-Err'
        if numish2uPROPt>-1:
            parval=str_par_ToFloat(str_change,'ish2uPROPt')
            if isinstance(parval,str):
                strout+=',ish2uPROPt-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,0x4d,0x6d,1,fa,MainWindow):
                    strout+=',ish2uPPOPt-OK'
                else:
                    strout+=',ish2uPPOPt-Err'

        if numstartmeas>-1:
            fa[0]=1.0
            if WriteFloatMBus(portname,boud,0x4d,0x111,1,fa,MainWindow):
                strout+=',startmeas-OK'
            else:
                strout+=',startmeas-Err'

        if numstopmeas>-1:
            fa[0]=1.0
            if WriteFloatMBus(portname,boud,0x4d,0x110,1,fa,MainWindow):
                strout+=',stopmeas-OK'
            else:
                strout+=',stopmeas-Err'

        if numzerocalibr>-1:
            fa[0]=1.0
            if WriteFloatMBus(portname,boud,0x4d,0x112,1,fa,MainWindow):
                strout+=',zerocalibr-OK'
            else:
                strout+=',zerocalibr-Err'
    return strout
    # конец объявления функции exchange_data_itm

# def callback(ch, method, properties, body):
#     global str_change
#     str_received=body
#     print(str_received) 
#     strout=exchange_data_itm(str_received,"/dev/ttyUSB0",19200)
#     str_change=str(strout)
#     print('str_change=',str_change)

#     connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
#     channel = connection.channel()
#     channel.queue_declare(queue='itmS')

#     channel.basic_publish(exchange='',
#                       routing_key='itmS',
#                       body=str_change)
#     #print('strsend=',str_change)
#     connection.close()

# connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
# channel = connection.channel()
# channel.queue_declare(queue='itmR')
# channel.basic_consume('itmR',callback,auto_ack=True)
# channel.start_consuming()