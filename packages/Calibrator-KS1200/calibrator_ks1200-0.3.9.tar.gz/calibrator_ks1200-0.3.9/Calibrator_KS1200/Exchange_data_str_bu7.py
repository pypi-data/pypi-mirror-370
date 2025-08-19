from  func_lib import *

# for i in range(50):
#     fa.append([i+0.1])

def exchange_data_bu7(MainWindow,
                      str_received, # строка с командами для выполнения
                      portname, # Имя порта /dev/ttyS3
                      boud = 9600, # скорость передачи
                      ):
    strout=None
    str_change=str(str_received)
    numT1=str_change.find('T1') # Измеренная температура/канал
    numT2=str_change.find('T2') # Значение — Вещественные числа (Градус цельсия)
    numT3=str_change.find('T3') # Чтение
    numP1=str_change.find('P1') # Мощность регулирования/канал
    numP2=str_change.find('P2') # Значение — Вещественные числа (Проценты)
    numP3=str_change.find('P3') # Чтение
    numPi1=str_change.find('Pi1') # Мощность интегральная/канал
    numPi2=str_change.find('Pi2') # Значение — Вещественные числа (Проценты)
    numPi3=str_change.find('Pi3') # тение
    numon1=str_change.find('on1') # Мощность регулирования ШИМ/канал
    numon2=str_change.find('on2') # Значение — Вещественные числа (Проценты).
    numon3=str_change.find('on3') # Чтение
    numTs1=str_change.find('Ts1') # ?
    numTs2=str_change.find('Ts2') #
    numTs3=str_change.find('Ts3') #
    numkp1=str_change.find('kp1') # Коэффициент пропорциональности/канал
    numkp2=str_change.find('kp2') # Значения - Вещественные числа. Относительные значения.  
    numkp3=str_change.find('kp3') # Запись/чтение
    numki1=str_change.find('ki1') # коэффициент интегрирования/канал
    numki2=str_change.find('ki2') # Значения - Вещественные числа. Относительные значения
    numki3=str_change.find('ki3') # Запись/чтение
    numkd1=str_change.find('kd1') # коэффициент дифференцирования/канал
    numkd2=str_change.find('kd2') # Значения - Вещественные числа. Относительные значения
    numkd3=str_change.find('kd3') # Запись/чтение
    numPimax1=str_change.find('Pimax1') # Мощность интегральная максимальная/канал — сумма
    numPimax2=str_change.find('Pimax2') # Значение — Вещественные числа (Проценты).
    numPimax3=str_change.find('Pimax3') # Запись/чтение
    numPimin1=str_change.find('Pimin1') # Мощность интегральная минимальная/канал — сумма
    numPimin2=str_change.find('Pimin2') # Значение — Вещественные числа (Проценты).
    numPimin3=str_change.find('Pimin3') # Запись/чтение
    numkpmax1=str_change.find('kpmax1') # коэффициент пропорциональности максимальный/канал
    numkpmax2=str_change.find('kpmax2') # Значения - Вещественные числа. Относительные значения
    numkpmax3=str_change.find('kpmax3') # Запись/чтение
    numkpcalc1=str_change.find('kpcalc1') # расчетный коэффициент пропорциональности/канал
    numkpcalc2=str_change.find('kpcalc2') # Значения - Вещественные числа. Относительные значения
    numkpcalc3=str_change.find('kpcalc3') # Чтение
    numTmax1=str_change.find('Tmax1') # верхний предел установки температуры/канал
    numTmax2=str_change.find('Tmax2') # Значение — Вещественные числа (Градус цельсия).
    numTmax3=str_change.find('Tmax3') # Запись/чтение
    numTmin1=str_change.find('Tmin1') # нижний предел установки температуры/канал
    numTmin2=str_change.find('Tmin2') # Значение — Вещественные числа (Градус цельсия).
    numTmin3=str_change.find('Tmin3') # Запись/чтение.
    numdevtype=str_change.find('devtype') # Название устройства, значение - Строковое описание устройства регулирования, Чтение
    numcalpr=str_change.find('calpr') # признак калибровки устройства, Значения OK – калибровка выполнена None – не выполнена, Чтение
    numpowset=str_change.find('powset') # установка режима мощности, Значения ON – регулирование мощности включено / OFF – регулирование отключено, Чтение/запись
    numpolicoeff1=str_change.find('policoeff1') # коэффициенты полинома отклонения измеренной температуры от установленной.
    numpolicoeff2=str_change.find('policoeff2') # Значение Вещественные числа.
    numpolicoeff3=str_change.find('policoeff3') # Запись/чтение.
    numuppTmpcorr1=str_change.find('uppTmpcorr1') # Температура для коррекции градиента в верху/температурные точки
    numuppTmpcorr2=str_change.find('uppTmpcorr2') # Значения - Вещественные числа. Градус цельсия.  
    numuppTmpcorr3=str_change.find('uppTmpcorr3') # Запись/чтение.
    numuppTmpcorr4=str_change.find('uppTmpcorr4') #
    numuppTmpcorr5=str_change.find('uppTmpcorr5') #
    numcentralTmpcorr1=str_change.find('centralTmpcorr1') # Температура для коррекции градиента в центре/температурные точки
    numcentralTmpcorr2=str_change.find('centralTmpcorr2') # Значения - Вещественные числа. Градус цельсия.  
    numcentralTmpcorr3=str_change.find('centralTmpcorr3') # Запись/чтение.
    numcentralTmpcorr4=str_change.find('centralTmpcorr4') #
    numcentralTmpcorr5=str_change.find('centralTmpcorr5') #
    numdownTmpcorr1=str_change.find('downTmpcorr1') # Температура для коррекции градиента в низу/температурные точки.
    numdownTmpcorr2=str_change.find('downTmpcorr2') # Значения - Вещественные числа. Градус цельсия.  
    numdownTmpcorr3=str_change.find('downTmpcorr3') # Запись/чтение.
    numdownTmpcorr4=str_change.find('downTmpcorr4') #
    numdownTmpcorr5=str_change.find('downTmpcorr5') #

    str_change=str(str_received) # опять?
    len_str=len(str_change)
    if str_change[0]=='R':  #read data

        if numcentralTmpcorr1>-1 or numcentralTmpcorr2>-1 or numcentralTmpcorr3>-1 or numcentralTmpcorr4>-1 or numcentralTmpcorr5>-1:
            inbuff=ReadFloatMBus(portname,boud,1,278*2,5,fa,MainWindow) # modbusnum = 1, addres = 278*2, numfloat = 5
            if inbuff:
                if numcentralTmpcorr1>-1:
                    str_change=insert_equ_param(str_change,'centralTmpcorr1',inbuff[0])
                if numcentralTmpcorr2>-1:
                    str_change=insert_equ_param(str_change,'centralTmpcorr2',inbuff[1])
                if numcentralTmpcorr3>-1:
                    str_change=insert_equ_param(str_change,'centralTmpcorr3',inbuff[2])
                if numcentralTmpcorr4>-1:
                    str_change=insert_equ_param(str_change,'centralTmpcorr4',inbuff[3])
                if numcentralTmpcorr5>-1:
                    str_change=insert_equ_param(str_change,'centralTmpcorr5',inbuff[4])
        else:
            if numcentralTmpcorr1>-1:
                str_change=insert_err_param(str_change,'centralTmpcorr1')
            if numcentralTmpcorr2>-1:
                str_change=insert_err_param(str_change,'centralTmpcorr2')
            if numcentralTmpcorr3>-1:
                str_change=insert_err_param(str_change,'centralTmpcorr3')
            if numcentralTmpcorr4>-1:
                str_change=insert_err_param(str_change,'centralTmpcorr4')
            if numcentralTmpcorr5>-1:
                str_change=insert_err_param(str_change,'centralTmpcorr5')

        if numuppTmpcorr1>-1 or numuppTmpcorr2>-1 or numuppTmpcorr3>-1 or numuppTmpcorr4>-1 or numuppTmpcorr5>-1 or numdownTmpcorr1>-1 or numdownTmpcorr2>-1 or numdownTmpcorr3>-1 or numdownTmpcorr4>-1 or numdownTmpcorr5>-1: 
            inbuff=ReadFloatMBus(portname,boud,1,190*2,10,fa,MainWindow)
            if inbuff: 
                if numuppTmpcorr1>-1:
                    str_change=insert_equ_param(str_change,'uppTmpcorr1',inbuff[0])
                if numdownTmpcorr1>-1:
                    str_change=insert_equ_param(str_change,'downTmpcorr1',inbuff[1])
                if numuppTmpcorr2>-1:
                    str_change=insert_equ_param(str_change,'uppTmpcorr2',inbuff[2])
                if numdownTmpcorr2>-1:
                    str_change=insert_equ_param(str_change,'downTmpcorr2',inbuff[3])
                if numuppTmpcorr3>-1:
                    str_change=insert_equ_param(str_change,'uppTmpcorr3',inbuff[4])
                if numdownTmpcorr3>-1:
                    str_change=insert_equ_param(str_change,'downTmpcorr3',inbuff[5])
                if numuppTmpcorr4>-1:
                    str_change=insert_equ_param(str_change,'uppTmpcorr4',inbuff[6])
                if numdownTmpcorr4>-1:
                    str_change=insert_equ_param(str_change,'downTmpcorr4',inbuff[7])
                if numuppTmpcorr5>-1:
                    str_change=insert_equ_param(str_change,'uppTmpcorr5',inbuff[8])
                if numdownTmpcorr5>-1:
                    str_change=insert_equ_param(str_change,'downTmpcorr5',inbuff[9])
            else : 
                if numuppTmpcorr1>-1:
                    str_change=insert_err_param(str_change,'uppTmpcorr1')
                if numdownTmpcorr1>-1:
                    str_change=insert_err_param(str_change,'downTmpcorr1')
                if numuppTmpcorr2>-1:
                    str_change=insert_err_param(str_change,'uppTmpcorr2')
                if numdownTmpcorr2>-1:
                    str_change=insert_err_param(str_change,'downTmpcorr2')
                if numuppTmpcorr3>-1:
                    str_change=insert_err_param(str_change,'uppTmpcorr3')
                if numdownTmpcorr3>-1:
                    str_change=insert_err_param(str_change,'downTmpcorr3')
                if numuppTmpcorr4>-1:
                    str_change=insert_err_param(str_change,'uppTmpcorr4')
                if numdownTmpcorr4>-1:
                    str_change=insert_err_param(str_change,'downTmpcorr4')
                if numuppTmpcorr5>-1:
                    str_change=insert_err_param(str_change,'uppTmpcorr5')
                if numdownTmpcorr5>-1:
                    str_change=insert_err_param(str_change,'downTmpcorr5')
          
        if numpolicoeff1>-1 or numpolicoeff2>-1 or numpolicoeff3>-1:
            inbuff=ReadFloatMBus(portname,boud,1,180*2,3,fa,MainWindow)
            if inbuff:
                if numpolicoeff1>-1:
                    str_change=insert_equ_param(str_change,'policoeff1',inbuff[0])
                if numpolicoeff2>-1:
                    str_change=insert_equ_param(str_change,'policoeff2',inbuff[1])
                if numpolicoeff3>-1:
                    str_change=insert_equ_param(str_change,'policoeff3',inbuff[2])
            else:
                if numpolicoeff1>-1:
                    str_change=insert_err_param(str_change,'policoeff1')
                if numpolicoeff2>-1:
                    str_change=insert_err_param(str_change,'policoeff2')
                if numpolicoeff3>-1:
                    str_change=insert_err_param(str_change,'policoeff3')
              
        if numT1>-1 or numT2>-1 or numT3>-1 or numP1>-1 or numP2>-1 or numP3>-1 or numPi1>-1 or numPi2>-1 or numPi3>-1 or numon1>-1 or numon2>-1 or numon3>-1:
            inbuff=ReadFloatMBus(portname,boud,1,20000,12,fa,MainWindow)
            if inbuff:
                if numT1>-1:
                    str_change=insert_equ_param(str_change,'T1',inbuff[0])
                if numT2>-1:
                    str_change=insert_equ_param(str_change,'T2',inbuff[1])
                if numT3>-1:
                    str_change=insert_equ_param(str_change,'T3',inbuff[2])
                if numP1>-1: 
                    str_change=insert_equ_param(str_change,'P1',inbuff[3])
                if numP2>-1: 
                    str_change=insert_equ_param(str_change,'P2',inbuff[4])
                if numP3>-1: 
                    str_change=insert_equ_param(str_change,'P3',inbuff[5])
                if numPi1>-1: 
                    str_change=insert_equ_param(str_change,'Pi1',inbuff[6])
                if numPi2>-1: 
                    str_change=insert_equ_param(str_change,'Pi2',inbuff[7])
                if numPi3>-1: 
                    str_change=insert_equ_param(str_change,'Pi3',inbuff[8])
                if numon1>-1: 
                    str_change=insert_equ_param(str_change,'on1',inbuff[9])
                if numon2>-1: 
                    str_change=insert_equ_param(str_change,'on2',inbuff[10])
                if numon3>-1: 
                    str_change=insert_equ_param(str_change,'on3',inbuff[11])
            else:
                if numT1>-1:
                    str_change=insert_err_param(str_change,'T1')
                if numT2>-1:
                    str_change=insert_err_param(str_change,'T2') 
                if numT3>-1:
                    str_change=insert_err_param(str_change,'T3')
                if numP1>-1: 
                    str_change=insert_err_param(str_change,'P1') 
                if numP2>-1: 
                    str_change=insert_err_param(str_change,'P2') 
                if numP3>-1: 
                    str_change=insert_err_param(str_change,'P3')
                if numPi1>-1: 
                    str_change=insert_err_param(str_change,'Pi1') 
                if numPi2>-1: 
                    str_change=insert_err_param(str_change,'Pi2') 
                if numPi3>-1: 
                    str_change=insert_err_param(str_change,'Pi3') 
                if numon1>-1: 
                    str_change=insert_err_param(str_change,'on1') 
                if numon2>-1: 
                    str_change=insert_err_param(str_change,'on2') 
                if numon3>-1: 
                    str_change=insert_err_param(str_change,'on3') 
            
        if numTs1>-1 or numTs2>-1 or numTs3>-1:
            inbuff=ReadFloatMBus(portname,boud,1,10*2,3,fa,MainWindow)
            if inbuff:
                if numTs1>-1:
                    str_change=insert_equ_param(str_change,'Ts1',inbuff[0])
                if numTs2>-1:
                    str_change=insert_equ_param(str_change,'Ts2',inbuff[1])
                if numTs3>-1:
                    str_change=insert_equ_param(str_change,'Ts3',inbuff[2])
            else:
                if numTs1>-1:
                    str_change=insert_err_param(str_change,'Ts1')
                if numTs2>-1:
                    str_change=insert_err_param(str_change,'Ts2') 
                else:
                    str_change=insert_err_param(str_change,'Ts3') 
            
        if numkp1>-1 or numkp2>-1 or numkp3>-1 or numki1>-1 or numki2>-1 or numki3>-1 or numkd1>-1 or numkd2>-1 or numkd3>-1:
            inbuff=ReadFloatMBus(portname,boud,1,206*2,9,fa,MainWindow)
            if inbuff: 
                if numkp1>-1:
                    str_change=insert_equ_param(str_change,'kp1',inbuff[0])
                if numkp2>-1:
                    str_change=insert_equ_param(str_change,'kp2',inbuff[1])
                if numkp3>-1:
                    str_change=insert_equ_param(str_change,'kp3',inbuff[2])
                if numki1>-1:
                    str_change=insert_equ_param(str_change,'ki1',inbuff[3])
                if numki2>-1:
                    str_change=insert_equ_param(str_change,'ki2',inbuff[4])
                if numki3>-1:
                    str_change=insert_equ_param(str_change,'ki3',inbuff[5])
                if numkd1>-1:
                    str_change=insert_equ_param(str_change,'kd1',inbuff[6])
                if numkd2>-1:
                    str_change=insert_equ_param(str_change,'kd2',inbuff[7])
                if numkd3>-1:
                    str_change=insert_equ_param(str_change,'kd3',inbuff[8])
            else:
                if numkp1>-1:
                    str_change=insert_err_param(str_change,'kp1')
                if numkp2>-1:
                    str_change=insert_err_param(str_change,'kp2') 
                if numkp3>-1:
                    str_change=insert_err_param(str_change,'kp3') 
                if numki1>-1:
                    str_change=insert_err_param(str_change,'ki1')
                if numki2>-1:
                    str_change=insert_err_param(str_change,'ki2') 
                if numki3>-1:
                    str_change=insert_err_param(str_change,'ki3') 
                if numkd1>-1:
                    str_change=insert_err_param(str_change,'kd1')
                if numkd2>-1:
                    str_change=insert_err_param(str_change,'kd2') 
                if numkd3>-1:
                    str_change=insert_err_param(str_change,'kd3') 

        if numPimax1>-1 or numPimax2>-1 or numPimax3>-1 or numPimin1>-1 or numPimin2>-1 or numPimin3>-1 or numkpmax1>-1 or numkpmax2>-1 or numkpmax3>-1 or numTmax1>-1 or numTmax2>-1 or numTmax3>-1 or numTmin1>-1 or numTmin2>-1 or numTmin3 >-1:
            inbuff=ReadFloatMBus(portname,boud,1,215*2,15,fa,MainWindow)
            if inbuff:
                if numPimax1>-1:
                    str_change=insert_equ_param(str_change,'Pimax`',inbuff[0])
                if numPimax2>-1:
                    str_change=insert_equ_param(str_change,'Pimax2',inbuff[1])
                if numPimax3>-1:
                    str_change=insert_equ_param(str_change,'Pimax3',inbuff[2])
                if numPimin1>-1:
                    str_change=insert_equ_param(str_change,'Pimin1',inbuff[3])
                if numPimin2>-1:
                    str_change=insert_equ_param(str_change,'Pimin2',inbuff[4])
                if numPimin3>-1:
                    str_change=insert_equ_param(str_change,'Pimin3',inbuff[5])
                if numkpmax1>-1:
                    str_change=insert_equ_param(str_change,'kpmax1',inbuff[6])
                if numkpmax2>-1:
                    str_change=insert_equ_param(str_change,'kpmax2',inbuff[7])
                if numkpmax3>-1:
                    str_change=insert_equ_param(str_change,'kpmax3',inbuff[8])
                if numTmax1>-1:
                    str_change=insert_equ_param(str_change,'Tmax1',inbuff[9])
                if numTmax2>-1:
                    str_change=insert_equ_param(str_change,'Tmax2',inbuff[10])
                if numTmax3>-1:
                    str_change=insert_equ_param(str_change,'Tmax3',inbuff[11])
                if numTmin1>-1:
                    str_change=insert_equ_param(str_change,'Tmin1',inbuff[12])
                if numTmin2>-1:
                    str_change=insert_equ_param(str_change,'Tmin2',inbuff[13])
                if numTmin3>-1:
                    str_change=insert_equ_param(str_change,'Tmin3',inbuff[14])
                
            else :
                if numPimax1>-1:
                    str_change=insert_err_param(str_change,'Pimax1')
                if numPimax2>-1:
                    str_change=insert_err_param(str_change,'Pimax2')
                if numPimax3>-1:
                    str_change=insert_err_param(str_change,'Pimax3')
                if numPimin1>-1:
                    str_change=insert_err_param(str_change,'Pimin1')
                if numPimin2>-1:
                    str_change=insert_err_param(str_change,'Pimin2')
                if numPimin3>-1:
                    str_change=insert_err_param(str_change,'Pimin3')
                if numkpmax1>-1:
                    str_change=insert_err_param(str_change,'kpmax1')
                if numkpmax2>-1:
                    str_change=insert_err_param(str_change,'kpmax2')
                if numkpmax3>-1:
                    str_change=insert_err_param(str_change,'kpmax3')
                if numTmax1>-1:
                    str_change=insert_err_param(str_change,'Tmax1') 
                if numTmax2>-1:
                    str_change=insert_err_param(str_change,'Tmax2')
                if numTmax3>-1:
                    str_change=insert_err_param(str_change,'Tmax3')
                if numTmin1>-1:
                    str_change=insert_err_param(str_change,'Tmin1')
                if numTmin2>-1:
                    str_change=insert_err_param(str_change,'Tmin2')
                if numTmin3>-1:
                    str_change=insert_err_param(str_change,'Tmin3')
               
        if numkpcalc1>-1 or numkpcalc2>-1 or numkpcalc3>-1:
            inbuff=ReadFloatMBus(portname,boud,1,112*2,15,fa,MainWindow)
            if inbuff:
                if numkpcalc1>-1:
                    str_change=insert_equ_param(str_change,'kpcalc1',inbuff[0])
                if numkpcalc2>-1:
                    str_change=insert_equ_param(str_change,'kpcalc2',inbuff[1])
                if numkpcalc3>-1:
                    str_change=insert_equ_param(str_change,'kpcalc3',inbuff[2])
            else:
                if numkpcalc1>-1:
                    str_change=insert_err_param(str_change,'kpcalc1')
                if numkpcalc2>-1:
                    str_change=insert_err_param(str_change,'kpcalc2')
                if numkpcalc3>-1:
                    str_change=insert_err_param(str_change,'kpcalc3')   
           
        if numdevtype>-1 or numcalpr>-1 or numpowset>-1 :
            inbuff=ReadBytesMBus(portname,boud,1,0x400,4,MainWindow)
            if inbuff:
                if numdevtype>-1:
                    par=strvaldev(inbuff[0])
                    str_change=insert_equ_param(str_change,'devtype',par)
                
                if numcalpr>-1:
                    if inbuff[2]==0x05:
                        par='Ok'
                    else:
                        par='None'
                    str_change=insert_equ_param(str_change,'calpr',par)
                
                if numpowset>-1:
                    if inbuff[3]==0x05:
                        par='ON'
                    elif inbuff[3]==0xf0:
                        par='OFF'
                    str_change=insert_equ_param(str_change,'powset',par)
        strout=str_change
        return strout  

    elif str_change[0]=='W':  #whrite data
        strout='W'
        #print('str_change=',str_change)
         
        if numcentralTmpcorr1>-1:
            parval= str_par_ToFloat(str_change,'centralTmpcorr1')
            if isinstance(parval,str):
                strout+=',centralTmpcorr1-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,278*2,1,fa,MainWindow): 
                    strout+=',centralTmpcorr1-OK'
                else:
                    strout+=',centralTmpcorr1-Err'
        if numcentralTmpcorr2>-1:
            parval= str_par_ToFloat(str_change,'centralTmpcorr3')
            if isinstance(parval,str):
                strout+=',centralTmpcorr3-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,279*2,1,fa,MainWindow): 
                    strout+=',centralTmpcorr2-OK'
                else:
                    strout+=',centralTmpcorr2-Err'
        if numcentralTmpcorr3>-1:
            parval= str_par_ToFloat(str_change,'centralTmpcorr3')
            if isinstance(parval,str):
                strout+=',centralTmpcorr3-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,280*2,1,fa,MainWindow): 
                    strout+=',centralTmpcorr3-OK'
                else:
                    strout+=',centralTmpcorr3-Err'
        if numcentralTmpcorr4>-1:
            parval= str_par_ToFloat(str_change,'centralTmpcorr4')
            if isinstance(parval,str):
                strout+=',centralTmpcorr4-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,281*2,1,fa,MainWindow): 
                    strout+=',centralTmpcorr4-OK'
                else:
                    strout+=',centralTmpcorr4-Err'
        if numcentralTmpcorr5>-1:
            parval= str_par_ToFloat(str_change,'centralTmpcorr5')
            if isinstance(parval,str):
                strout+=',centralTmpcorr5-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,282*2,1,fa,MainWindow): 
                    strout+=',centralTmpcorr5-OK'
                else:
                    strout+=',centralTmpcorr5-Err'

        if numdownTmpcorr1>-1:
            parval= str_par_ToFloat(str_change,'downTmpcorr1')
            if isinstance(parval,str):
                strout+=',downTmpcorr1-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,191*2,1,fa,MainWindow): 
                    strout+=',downTmpcorr1-OK'
                else:
                    strout+=',downTmpcorr1-Err'
        if numdownTmpcorr2>-1:
            parval= str_par_ToFloat(str_change,'downTmpcorr2')
            if isinstance(parval,str):
                strout+=',downTmpcorr2-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,193*2,1,fa,MainWindow): 
                    strout+=',downTmpcorr2-OK'
                else:
                    strout+=',downTmpcorr2-Err'
        if numdownTmpcorr3>-1:
            parval= str_par_ToFloat(str_change,'downTmpcorr3')
            if isinstance(parval,str):
                strout+=',downTmpcorr3-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,195*2,1,fa,MainWindow): 
                    strout+=',downTmpcorr3-OK'
                else:
                    strout+=',downTmpcorr3-Err'
        if numdownTmpcorr4>-1:
            parval= str_par_ToFloat(str_change,'downTmpcorr4')
            if isinstance(parval,str):
                strout+=',downTmpcorr4-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,197*2,1,fa,MainWindow): 
                    strout+=',downTmpcorr4-OK'
                else:
                    strout+=',downTmpcorr4-Err'
        if numdownTmpcorr5>-1:
            parval= str_par_ToFloat(str_change,'downTmpcorr5')
            if isinstance(parval,str):
                strout+=',downTmpcorr5-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,199*2,1,fa,MainWindow): 
                    strout+=',downTmpcorr5-OK'
                else:
                    strout+=',downTmpcorr5-Err'
         
        if numuppTmpcorr1>-1:
            parval= str_par_ToFloat(str_change,'uppTmpcorr1')
            if isinstance(parval,str):
                strout+=',uppTmpcorr1-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,190*2,1,fa,MainWindow): 
                    strout+=',uppTmpcorr1-OK'
                else:
                    strout+=',uppTmpcorr1-Err'
        if numuppTmpcorr2>-1:
            parval= str_par_ToFloat(str_change,'uppTmpcorr2')
            if isinstance(parval,str):
                strout+=',uppTmpcorr2-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,192*2,1,fa,MainWindow): 
                    strout+=',uppTmpcorr2-OK'
                else:
                    strout+=',uppTmpcorr2-Err'
        if numuppTmpcorr1>-1:
            parval= str_par_ToFloat(str_change,'uppTmpcorr3')
            if isinstance(parval,str):
                strout+=',uppTmpcorr3-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,194*2,1,fa,MainWindow): 
                    strout+=',uppTmpcorr3-OK'
                else:
                    strout+=',uppTmpcorr3-Err'
        if numuppTmpcorr1>-1:
            parval= str_par_ToFloat(str_change,'uppTmpcorr4')
            if isinstance(parval,str):
                strout+=',uppTmpcorr4-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,196*2,1,fa,MainWindow): 
                    strout+=',uppTmpcorr4-OK'
                else:
                    strout+=',uppTmpcorr4-Err'
        if numuppTmpcorr1>-1:
            parval= str_par_ToFloat(str_change,'uppTmpcorr5')
            if isinstance(parval,str):
                strout+=',uppTmpcorr5-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,198*2,1,fa,MainWindow): 
                    strout+=',uppTmpcorr5-OK'
                else:
                    strout+=',uppTmpcorr5-Err'
           
        if numpolicoeff1>-1:
            parval= str_par_ToFloat(str_change,'policoeff1')
            if isinstance(parval,str):
                strout+=',policoeff1-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,180*2,1,fa,MainWindow): 
                    strout+=',policoeff1-OK'
                else:
                    strout+=',policoeff1-Err'
        if numpolicoeff2>-1:
            parval= str_par_ToFloat(str_change,'policoeff2')
            if isinstance(parval,str):
                strout+=',policoeff2-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,181*2,1,fa,MainWindow): 
                    strout+=',policoeff2-OK'
                else:
                    strout+=',policoeff3-Err'
        if numpolicoeff3>-1:
            parval= str_par_ToFloat(str_change,'policoeff3')
            if isinstance(parval,str):
                strout+=',policoeff3-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,182*2,1,fa,MainWindow): 
                    strout+=',policoeff3-OK'
                else:
                    strout+=',policoeff3-Err'
         
        if numTs1>-1:
            parval= str_par_ToFloat(str_change,'Ts1')
            if isinstance(parval,str):
                strout+=',Ts1-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,10*2,1,fa,MainWindow): 
                    strout+=',Ts1-OK'
                else:
                    strout+=',Ts1-Err'

        if numTs2>-1:
            parval= str_par_ToFloat(str_change,'Ts2')
            if isinstance(parval,str):
                strout+=',Ts2-'
                strout+=parval
            else: 
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,11*2,1,fa,MainWindow):
                    strout+=',Ts2-OK'
                else:
                    strout+=',Ts2-Err'
        if numTs3>-1:
            parval= str_par_ToFloat(str_change,'Ts3')
            if isinstance(parval,str):
                strout+=',Ts3-'
                strout+=parval
            else:
                fa[0]=parval
                if WriteFloatMBus(portname,boud,1,12*2,1,fa,MainWindow): 
                    strout+=',Ts3-OK'
                else:
                    strout+=',Ts3-Err'

        if numkp1>-1:
            parval= str_par_ToFloat(str_change,'kp1')
            if isinstance(parval,str):
                strout+=',kp1-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,206*2,1,fa,MainWindow): 
                    strout+=',kp1-OK'
                else:
                    strout+=',hp1-Err'
        if numkp2>-1:
            parval= str_par_ToFloat(str_change,'kp2')
            if isinstance(parval,str):
                strout+=',kp2-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,207*2,1,fa,MainWindow): 
                    strout+=',kp2-OK'
                else:
                    strout+=',hp2-Err'
        if numkp3>-1:
            parval= str_par_ToFloat(str_change,'kp3')
            if isinstance(parval,str):
                strout+=',kp3-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,208*2,1,fa,MainWindow): 
                    strout+=',kp3-OK'
                else:
                    strout+=',hp3-Err'
        if numki1>-1:
            parval= str_par_ToFloat(str_change,'ki1')
            if isinstance(parval,str):
                strout+=',ki1-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,209*2,1,fa,MainWindow): 
                    strout+=',ki1-OK'
                else:
                    strout+=',ki1-Err'

        if numki2>-1:
            parval= str_par_ToFloat(str_change,'ki2')
            if isinstance(parval,str):
                strout+=',ki2-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,210*2,1,fa,MainWindow): 
                    strout+=',ki2-OK'
                else:
                    strout+=',ki2-Err'

        if numki3>-1:
            parval= str_par_ToFloat(str_change,'ki3')
            if isinstance(parval,str):
                strout+=',ki3-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,211*2,1,fa,MainWindow): 
                    strout+=',ki3-OK'
                else:
                    strout+=',ki3-Err'
             
        if numkd1>-1:
            parval= str_par_ToFloat(str_change,'kd1')
            if isinstance(parval,str):
                strout+=',kd1-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,212*2,1,fa,MainWindow):
                    strout+=',kd1-OK'
                else:
                    strout+=',kd1-Err'

        if numkd2>-1:
            parval= str_par_ToFloat(str_change,'kd2')
            if isinstance(parval,str):
                strout+=',kd2-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,213*2,1,fa,MainWindow): 
                    strout+=',kd2-OK'
                else:
                    strout+=',kd2-Err'

        if numkd3>-1:
            parval= str_par_ToFloat(str_change,'kd3')
            if isinstance(parval,str):
                strout+=',kd3-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,214*2,1,fa,MainWindow): 
                    strout+=',kd3-OK'
                else:
                    strout+=',kd3-Err'

        if numPimax1>-1:
            parval=str_par_ToFloat(str_change,'Pimax1')
            if isinstance(parval,str):
                strout+=',Pimax1-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,215*2,1,fa,MainWindow): 
                    strout+=',Pimax1-OK'
                else:
                    strout+=',Pimax1-Err'

        if numPimax2>-1:
            parval=str_par_ToFloat(str_change,'Pimax2')
            if isinstance(parval,str):
                strout+=',Pimax2-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,216*2,1,fa,MainWindow): 
                    strout+=',Pimax2-OK'
                else:
                    strout+=',Pimax2-Err'

        if numPimax3>-1:
            parval=str_par_ToFloat(str_change,'Pimax3')
            if isinstance(parval,str):
                strout+=',Pimax3-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,217*2,1,fa,MainWindow): 
                    strout+=',Pimax3-OK'
                else:
                    strout+=',Pimax3-Err'

        if numPimin1>-1:
            parval=str_par_ToFloat(str_change,'Pimin1')
            if isinstance(parval,str):
                strout+=',Pimin1-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,218*2,1,fa,MainWindow): 
                    strout+=',Pimin1-OK'
                else:
                    strout+=',Pimin1-Err'

        if numPimin2>-1:
            parval=str_par_ToFloat(str_change,'Pimin2')
            if isinstance(parval,str):
                strout+=',Pimin2-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,219*2,1,fa,MainWindow): 
                    strout+=',Pimin2-OK'
                else:
                    strout+=',Pimin2-Err'

        if numPimin3>-1:
            parval=str_par_ToFloat(str_change,'Pimin3')
            if isinstance(parval,str):
                strout+=',Pimin3-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,220*2,1,fa,MainWindow): 
                    strout+=',Pimin3-OK'
                else:
                    strout+=',Pimin3-Err'
         
        if numkpmax1>-1:
            parval=str_par_ToFloat(str_change,'kpmax1')
            if isinstance(parval,str):
                strout+=',kpmax1-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,221*2,1,fa,MainWindow): 
                    strout+=',kpmax1-OK'
                else:
                    strout+=',kpmax1-Err'
         
        if numkpmax2>-1:
            parval=str_par_ToFloat(str_change,'kpmax2')
            if isinstance(parval,str):
                strout+=',kpmax2-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,222*2,1,fa,MainWindow): 
                    strout+=',kpmax2-OK'
                else:
                    strout+=',kpmax2-Err'
         
        if numkpmax3>-1:
            parval=str_par_ToFloat(str_change,'kpmax3')
            if isinstance(parval,str):
                strout+=',kpmax3-'
                strout+=parval
            else:
                fa[0]=parval  
                if WriteFloatMBus(portname,boud,1,223*2,1,fa,MainWindow): 
                    strout+=',kpmax3-OK'
                else:
                    strout+=',kpmax3-Err'
            
        if numTmax1>-1:
            parval=str_par_ToFloat(str_change,'Tmax1')
            if isinstance(parval,str):
                strout+=',Tmax1-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,224*2,1,fa,MainWindow): 
                    strout+=',Tmax1-OK'
                else:
                    strout+=',Tmax1-Err'
           
        if numTmax2>-1:
            parval=str_par_ToFloat(str_change,'Tmax2')
            if isinstance(parval,str):
                strout+=',Tmax2-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,225*2,1,fa,MainWindow): 
                    strout+=',Tmax2-OK'
                else:
                    strout+=',Tmax2-Err'

        if numTmax3>-1:
            parval=str_par_ToFloat(str_change,'Tmax3')
            if isinstance(parval,str):
                strout+=',Tmax3-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,226*2,1,fa,MainWindow): 
                    strout+=',Tmax3-OK'
                else:
                    strout+=',Tmax3-Err'
          
        if numTmin1>-1:
            parval=str_par_ToFloat(str_change,'Tmin1')
            if isinstance(parval,str):
                strout+=',Tmin1-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,227*2,1,fa,MainWindow): 
                    strout+=',Tmin1-OK'
                else:
                    strout+=',Tmin1-Err'

        if numTmin2>-1:
            parval=str_par_ToFloat(str_change,'Tmin2')
            if isinstance(parval,str):
                strout+=',Tmin2-'
                strout+=parval
            else:
                fa[0]=parval   
                if WriteFloatMBus(portname,boud,1,228*2,1,fa,MainWindow): 
                    strout+=',Tmin2-OK'
                else:
                    strout+=',Tmin2-Err'

        if numTmin3>-1:
            parval=str_par_ToFloat(str_change,'Tmin3')
            if isinstance(parval,str):
                strout+=',Tmin3-'
                strout+=parval
            else:
                fa[0] = parval   
                if WriteFloatMBus(portname,boud,1,229*2,1,fa,MainWindow): 
                    strout+=',Tmin3-OK'
                else:
                    strout+=',Tmin3-Err'
         
        if numpowset>-1:
            inbuff=ReadBytesMBus(portname,boud,1,0x400,4,MainWindow) 
            if numpowset>-1:
                par= extract_val_param(str_change,'powset')
                if par=='ON':
                    inbuff[3]=0x05
                    if WriteFourBytesMBus(portname,boud,1,0x400,4,inbuff,MainWindow):
                        strout+=',powset-OK'
                    else: strout+=',powset-Err'
                elif par=='OFF': 
                    inbuff[3]=0xf0
                    if WriteFourBytesMBus(portname,boud,1,0x400,4,inbuff,MainWindow):
                        strout+=',powset-OK'
                    else: strout+=',powset-Err'
          
        return strout
# конец объявления функции exchange_data_bu7

# def callback(ch, method, properties, body):
#     global str_change
#     str_received=body
#     # print('str_received=',str_received) 
#     strout=exchange_data_bu7(str_received,"/dev/ttyS3",9600)
#     # print('strout=',strout)
#     connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
#     channel = connection.channel()
#     channel.queue_declare(queue='urS')
#     channel.basic_publish(exchange='', routing_key='urS', body=strout)
#     #print('strsend=',str_change)
#     connection.close()

# connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
# channel = connection.channel()
# channel.queue_declare(queue='urR')
# channel.basic_consume('urR', callback, auto_ack=True)
# channel.start_consuming()