from array import array
import struct
import serial
# from serial.tools.list_ports import *
inbuff=bytearray()

fa=[] # список float array
for i in range(50):
	fa.append([i+0.1])
ia=[] # список integer array
for i in range(50):
	ia.append([i])

# -------- записываем в mBus--------------
# comportname - имя COM-порта
# boud - скорость передачи данных
# modbusnum - номер шины modbus
# address - адрес устройства в шине
# data - передаваемые данные

# Unit16 (0-65535)
def WriteUint16_tMBus(comportname,boud,modbusnum,address,numreg,data,MainWindow):
	bytearr=bytearray(numreg*2)
	for i in range(numreg):
		uint16_tBytes=bytearray(2)
		uint16_tBytes=uint16_tToBytes(data[i])
		uint16_tBytes=TwoBytesReverse(uint16_tBytes)
		for j in range(2):
			bytearr[(j+i*2)]=uint16_tBytes[j]
	if SendMBus (comportname, boud, modbusnum, 0x10, address, bytearr, numreg,MainWindow):
		return 1
	else:
		return 0


# 4 байта
def WriteFourBytesMBus(comportname,boud,modbusnum,address,numbyte,data,MainWindow):
	byte_arr=bytearray(numbyte)
	for i in range(numbyte): 
		byte_arr[i]=data[i]
	numreg=int(numbyte/2)
	if(SendMBus(comportname,boud,modbusnum,0x10,address,byte_arr,numreg,MainWindow)):
		return 1
	else :
		return 0

# 2 байта
def WriteTwoBytesMBus(comportname,boud,modbusnum,address,numreg,data,MainWindow):
	byte_arr=bytearray(2)
	byte_arr[1]=data[0]
	byte_arr[0]=data[1]
	if(SendMBus(comportname,boud,modbusnum,0x10,address,byte_arr,1,MainWindow)):
		return 1
	else :
		return 0

# float (Число двойной точности) 8 байт
def WriteFloatMBus(comportname,boud,modbusnum,address,numfloat,data,MainWindow):
	byte_arr=bytearray(numfloat*4)
	for i in range(numfloat):
		FloatBytes=bytearray(4)
		#print('data',i,'=',data[i])
		FloatBytes=FloatToBytes(data[i])
		FloatBytes=FourBytesReverse(FloatBytes)
		for j in range(4):
			byte_arr[(j+i*4)]=FloatBytes[j]
 
	if(SendMBus(comportname,boud,modbusnum,0x10,address,byte_arr,numfloat*2,MainWindow)):
		return 1
	else :
		return 0

# -------- читаем из mBus--------------
# comportname - имя COM-порта
# boud - скорость передачи данных
# modbusnum - номер шины modbus
# address - адрес устройства в шине
# numreg - количество читаемых регистров

# UShot - 0-65535
def ReadUShortMBus(comportname,boud,modbusnum,address,numreg,ia,MainWindow):
	inbuff = SendMBus(comportname,boud,modbusnum,3,address,0,numreg,MainWindow)
	if inbuff:
		for i in range(numreg):
			UShortBytes=bytearray(2)
			for j in range(2):
				UShortBytes[j]=inbuff[(j+i*4)+3]
		UShortBytes=TwoBytesReverse(UShortBytes)		
		ia[i]=BytesToUShort(UShortBytes)
		#ia[i]=valin
		return ia
	else :
		return 0

# Uint16 - 0-65535
def ReadUint16_tMBus(comportname,boud,modbusnum,address,numreg,ia,MainWindow):
	inbuff = SendMBus(comportname,boud,modbusnum,3,address,0,numreg,MainWindow)
	if inbuff:
		for i in range(numreg):
			UShortBytes=bytearray(2)
			for j in range(2):
				UShortBytes[j]=inbuff[(j+i*4)+3]
			UShortBytes=TwoBytesReverse(UShortBytes)		
			ia[i]=BytesToUShort(UShortBytes)
			return ia
	else :
		return 0

# Читаем байты
# numbytes - количество читаемых байт
def ReadBytesMBus(comportname,boud,modbusnum,address,numbytes,MainWindow):
	byte_arr=bytearray(numbytes)
	inbuff = SendMBus(comportname,boud,modbusnum,3,address,0,numreg,MainWindow)
	numreg=int(numbytes/2)
	if inbuff:
		for i in range(numbytes):
			byte_arr[i]=inbuff[i+3]
		return byte_arr
	else :
		return 0

# Читаем два байта (один регистр)
# numreg - количество читаемых регистров
def ReadTwoBytesMBus(comportname,boud,modbusnum,address,numreg,MainWindow):
	byte_arr=bytearray(2*numreg)
	inbuff = SendMBus(comportname,boud,modbusnum,3,address,0,numreg,MainWindow)
	if inbuff:
		byte_arr[0]=inbuff[4]
		byte_arr[1]=inbuff[3]
		return byte_arr
	else :
		return 0

# Чтения статуса шины?
def ReadStMBus(comportname,boud,modbusnum,MainWindow):
	inbuff = SendMBus(comportname,boud,modbusnum,0x07,0,0,1,MainWindow)
	if inbuff:
		bytearr=tuple(inbuff)
		return bytearr[2]
	else :
		return 0

def ReadInfMBus(comportname,boud,modbusnum,MainWindow):
	strinf=SendMBus(comportname,boud,modbusnum,0x11,0,0,1,MainWindow)
	if strinf:
		return strinf
	else :
		return 0

def ReadIntMBus(comportname,boud,modbusnum,address,numint,ia,MainWindow):
	inbuff = SendMBus(comportname,boud,modbusnum,3,address,0,numint*2,MainWindow)
	if inbuff:
		for i in range(numint):
			IntBytes=bytearray(4)
			for j in range(4):
				IntBytes[j]=inbuff[(j+i*4)+3]
			IntBytes=FourBytesReverse(IntBytes)		
			ia[i]=BytesToInt(IntBytes)
		return ia
	else :
		return 0

def ReadInt32_tMBus(comportname,boud,modbusnum,address,numint,ia,MainWindow):
	inbuff = SendMBus(comportname,boud,modbusnum,3,address,0,numint*2,MainWindow)
	if inbuff:	
		for i in range(numint):
			IntBytes=bytearray(4)
			for j in range(4):
				IntBytes[j]=inbuff[(j+i*4)+3]
			IntBytes=FourBytesReverse(IntBytes)		
			ia[i]=BytesToInt(IntBytes)
		return ia
	else :
		return 0

def ReadRegMBus(comportname,boud,modbusnum,address,numreg,MainWindow):
	byte_arr=bytearray(numreg*2)
	inbuff = SendMBus(comportname,boud,modbusnum,3,address,0,numreg,MainWindow)
	if inbuff:	
		ab=bytearray(numreg*2)
		byte_arr=tuple(inbuff)
		for i in range(numreg*2):
			ab[i]=byte_arr[i+3] 
		#print('ab=',ab)
		return ab
	else :
		return 0

def ReadFloatMBus(comportname,boud,modbusnum,address,numfloat,fa,MainWindow):
	inbuff = SendMBus(comportname,boud,modbusnum,3,address,0,numfloat*2,MainWindow)
	if inbuff:
		bytearr=tuple(inbuff)
		for i in range(numfloat):
			FloatBytes=bytearray(4)
			for j in range(4):
				FloatBytes[j]=bytearr[(j+i*4)+3]
			FloatBytes=FourBytesReverse(FloatBytes)		
			fa[i]=BytesToFloat(FloatBytes)
		return fa
	else :
		return 0

# обмен данными с mBus
# comportname - номер COM порта
# boud - скорость передачи COM порта
# modbusnum - номер устройства modBus
# modbusfun - номер функции, которую требуется выполнить
# address - адрес устройства?
# data - записываемые данные, array
# lengthreg - длина регистра (количество байт)

def SendMBus(comportname,boud,modbusnum,modbusfun,address,data,lengthreg,MainWindow):
	balen=bytearray(4)
	balen=IntToBytes(lengthreg) # заполняем длину регистра
	ba1=bytearray(4)
	ba1=IntToBytes(address) # запоняем адрес
	sizein=0
	if(modbusfun==0x07): #---------------- Read status?
		outbuff=bytearray(4)
		outbuff[0]=modbusnum
		outbuff[1]=7
		crc16=CalcMbusCrc16(outbuff,2)
		ba1=IntToBytes(crc16)
		outbuff[2]=ba1[0]
		outbuff[3]=ba1[1]
		sizeout=4
		sizein=5
	elif(modbusfun==0x03):	#----------------read bytes from address
		outbuff=bytearray(8)
		outbuff[0]=modbusnum
		outbuff[1]=3
		outbuff[2]=ba1[1] #adrhbyte
		outbuff[3]=ba1[0] #adrlbyte
		outbuff[4]=0
		outbuff[5]=balen[0]
		crc16=CalcMbusCrc16(outbuff,6)
		ba1=IntToBytes(crc16)
		outbuff[6]=ba1[0]
		outbuff[7]=ba1[1]
		sizein=lengthreg*2+5 # len bytes
	elif(modbusfun==0x10):	#----------------write bytes
		outbuff=bytearray(lengthreg*2+9)
		outbuff[0]=modbusnum
		outbuff[1]=0x10
		outbuff[2]=ba1[1] #adrhbyte
		outbuff[3]=ba1[0] #adrlbyte
		outbuff[4]=0
		outbuff[5]=balen[0]
		outbuff[6] = lengthreg*2
		sizeout=7
		for i in range(lengthreg*2):
			outbuff[7+i]=data[i]
			sizeout+=1
		crc16=CalcMbusCrc16(outbuff,sizeout)
		ba1=IntToBytes(crc16)
		outbuff[sizeout]=ba1[0]
		outbuff[sizeout+1]=ba1[1]
		sizein=8 
	elif(modbusfun==0x11):	#----------------read inf device
		outbuff=bytearray(4)
		outbuff[0]=modbusnum
		outbuff[1]=0x11
		crc16=CalcMbusCrc16(outbuff,2)
		ba1=IntToBytes(crc16)
		outbuff[2]=ba1[0]
		outbuff[3]=ba1[1]
		sizeout=4
		sizein=128
	#ser=serial.Serial("/dev/ttyUSB0",19200,timeout=0.1)
	#ser=serial.Serial("/dev/ttyS3",9600,timeout=0.1)
	try:
		serial_port=serial.Serial(comportname, boud, timeout=1)
	except serial.SerialException as error:
		# print("Невозможно открыть Com порт: ", comportname)
		# print("Класс исключения: ", error.__class__)
		# print("Исключение", error.args)
		return False
	# print("Com порт ", comportname, " открыт.")
	inbuff = b''
	try_count = 0
	while True:
		if MainWindow.portname_itm == comportname and MainWindow.itm_exchange_stop:
			MainWindow.itm_exchange_stop = False
			serial_port.close()
			return
		if comportname == MainWindow.portname_itm: print('Попытка чтения №(мах=10):',try_count)
		if inbuff == b'': serial_port.write(outbuff)
		inbuff=serial_port.read(sizein)
		if MainWindow.portname_itm == comportname: print('read itm:',inbuff)
		else: print('read bu7:',inbuff)
		if inbuff == b'' or inbuff == b'M\x83\x06\x00\xe5': try_count+=1
		if inbuff != b'M\x83\x06\x00\xe5' and inbuff != b'' or try_count > 50: break
	serial_port.close()
	# print('final:',inbuff)
	leninbuff=len(inbuff)
	if(modbusfun==0x11):
		# Считали серийный номер устройства
		crc16=CalcMbusCrc16(inbuff,leninbuff)
		if crc16==0:
			bytestr=bytearray(leninbuff-5)
			for i in range(leninbuff-5):
				bytestr[i]=inbuff[i+3]
				infstring=bytestr.decode('cp1251')
			return infstring
		else:
			return 0
	else:
		# Считали любые данные, кроме серийного номера устройства
		# print('inbuff=',inbuff)
		if(len(inbuff)==0):
			return 0
		crc16=CalcMbusCrc16(inbuff,leninbuff)
		if(crc16==0):
			return inbuff
		else:
			return (0)

	# print('outbuff=',outbuff)

# вычисляем контрольную сумму
# buffer - данные, array
# length - количесвто данных
# 
# возвращает контрольную сумму

def CalcMbusCrc16(buffer,length):
	# print(list(buffer))
	# print(length)
	crc16ret=0xFFFF
	k=0
	for k in range(length):
		crc16ret ^=buffer[k]   #XOR
		crc16ret &=0xFFFF #-?
		for i in range(8):
			if (crc16ret & 0x0001):
				crc16ret=(crc16ret >> 1) ^ 0xA001
			else :
				crc16ret=crc16ret >> 1
				crc16ret &=0xFFFF
	return crc16ret


def uint16_tToBytes(value):
	ba = bytearray(struct.pack( "H" , value)) # H - short int, 2 байта
	buffer=tuple(ba)                          # в кортеж
	return buffer


def IntToBytes(value):
	ba = bytearray(struct.pack( "l" , value)) # l - long int, 4 байта
	buffer=tuple(ba)
	return buffer

def Int32_tToBytes(value):
	ba = bytearray(struct.pack( "l" , value))
	buffer=tuple(ba)
	return buffer

def UInt32_tToBytes(value):
	ba = bytearray(struct.pack( "L" , value)) # L - unsigned long, 4 байта
	buffer=tuple(ba)
	return buffer


def FloatToBytes(value):
	ba = bytearray(struct.pack( "f" , value)) # f - float, 4 байта
	buffer=tuple(ba)
	return buffer
	#return(ba)

def FourBytesReverse(buffer):
	ab=tuple(buffer)
	ba=bytearray(4)
	ba[3]=ab[0]
	ba[2]=ab[1]
	ba[1]=ab[2]
	ba[0]=ab[3]
	bufferout=tuple(ba)
	return bufferout

def TwoBytesReverse(buffer):
	ab=tuple(buffer)
	ba=bytearray(2)
	ba[1]=ab[0]
	ba[0]=ab[1]
	bufferout=tuple(ba)
	return bufferout


def BytesToInt32_t(buffer):
	ba=bytearray(4)
	ba[0]=buffer[0]
	ba[1]=buffer[1]
	ba[2]=buffer[2]
	ba[3]=buffer[3]
	value=struct.unpack( "l" ,ba)
	valueout=list(value) 
	return valueout

def BytesToUInt32_t(buffer):
	ba=bytearray(4)
	ba[0]=buffer[0]
	ba[1]=buffer[1]
	ba[2]=buffer[2]
	ba[3]=buffer[3]
	value=struct.unpack( "L" ,ba)
	valueout=list(value) 
	return valueout

def BytesToInt(buffer):
	ba=bytearray(4)
	ba[0]=buffer[0]
	ba[1]=buffer[1]
	ba[2]=buffer[2]
	ba[3]=buffer[3]
	value=struct.unpack( "l" ,ba)
	valueout=list(value) 
	return valueout

def BytesToUShort(buffer):
	ba=bytearray(2)
	ba[0]=buffer[0]
	ba[1]=buffer[1]
	value=struct.unpack( "H" ,ba)
	valueout=list(value) 
	return valueout


def BytesToFloat(buffer):
	ba=bytearray(4)
	ba[0]=buffer[0]
	ba[1]=buffer[1]
	ba[2]=buffer[2]
	ba[3]=buffer[3]
	value=struct.unpack( "f" ,ba)
	vall=list(value)
	valf=float(vall[0])
	return valf

def insert_err_param(string,par):
	lenstr=len(string)
	lenpar=len(par)
	ns=string.find(par,0,lenstr)
	if ns>-1:
		s1=string[:ns]
		s2=par+'-Err'
		s4=string[ns+lenpar:]
		s5=s1+s2+s4
		return s5
	else: return string


def insert_equ_param(string,par,value):
	lenstr=len(string)
	lenpar=len(par)
	ns=string.find(par,0,lenstr)
	if ns>-1:
		s1=string[:ns]
		s2=str(par)+'='
		s3=str(value)
		s4=string[ns+lenpar:]
		s5=s1+s2+s3+s4
		return s5
	else: return string

def insert_def_param(string,par,value):
	lenstr=len(string)
	lenpar=len(par)
	ns=string.find(par,0,lenstr)
	if ns>-1:
		s1=string[:ns]
		s2=str(par)+'-'
		s3=str(value)
		s4=string[ns+lenpar:]
		s5=s1+s2+s3+s4
		return s5
	else: return string


def extract_val_param(str_change,par):
	str_change=str(str_change)
	ns=str_change.find(par)
	if ns>-1:
		lenpar=len(par)
		str1=str_change[ns+lenpar:]
		if str1[0]!='=':
			return 'errval='
		else: 
			str2=str1[1:]
			ns=str2.find(',')
			if ns>-1:
				str3=str2[:ns]
			else:
				ns=str2.find("'")
				if ns>-1:
					str3=str2[:ns]
				else: 
					str3=str2
		return str3
	return 0


def str_par_ToUint16_t(str_change,par):
	ns=str(str_change).find(par)
	if ns>-1:
		lenpar=len(par)
		str1=str_change[ns+lenpar+1:]
		ns=str1.find(',')
		if ns>-1:
			str2=str1[:ns]
		else:
			ns=str1.find("'")
			if ns>-1:
				str2=str1[:ns]
			else: 
				str2=str1
		return str2 #valfloat
	return 0


def str_par_ToFloat(str_change,par):
	str_change=str(str_change)
	len_str_change=len(str_change)
	ns=str_change.find(par,0,len_str_change)
	lenpar=len(par)
	str1=str_change[ns+lenpar:]
	if str1[0]!='=':
		return 'errval='
	else: 
		str2=str1[1:]
		nsp=str2.find('.')
		if nsp==-1:
			return 'errvalnp'
		else:
			ns=str2.find(',')
			if ns>-1:
				str3=str2[:ns]
			else:
				ns=str2.find("'")
				if ns>-1: 
					str3=str2[:ns]
				else: #'errval' - не понятно, что он имел ввиду
					str3=str2
				lenstr3=len(str3) # в str3 значение параметра par
				np=0 # счетчик количества точек
				for i in range(lenstr3):
					ordstr3=ord(str3[i]) # возвращает код ASCII аргумента
					if ordstr3==46: # код точки .
						np+=1
					if np>1:
						return 'errvalp' # если в значении больше одной точки, то вываливаемся
					if ordstr3>57: # проверяем, что в значении только цифры
						if ordstr3==69 or ordstr3==101: # коды Е или е
							pass
						else: return 'errvalstr'
		try:
			valfloat=float(str3)
			return valfloat
		except ValueError:
			return 'errval'
 
def TuplToFloat(tupltval):
	inttp1=tupltval[0] 
	if inttp1<0:
		inttp1+=1    
	valfloat=float(inttp1)
	return valfloat

def meascurrentparstr (par):
	if par==5:
		return '1.0'
	elif par==0:
		return '4.0'
	elif par==1:
		return '3.0'
	elif par==2:
		return '2.5'
	elif par==3:
		return '2.0'
	elif par==4:
		return '1.5'
	elif par==6:
		return '0.7'
	elif par==7:
		return '0.4'
	else:
		return 'err'


def meascurrentstrpar (par):
	if par=='1.0':
		return 5
	elif par=='4.0':
		return 0
	elif par=='3.0':
		return 1
	elif par=='2.5':
		return 2
	elif par=='2.0':
		return 3
	elif par=='1.5':
		return 4
	elif par=='0.7':
		return 6
	elif par=='0.4':
		return 7
	else:
		return 'errval'


def Rrefparstr (par):
	if par==0:
		return 'R3'
	elif par==64:
		return 'R30'
	elif par==128:
		return 'R300'
	elif par==192:
		return 'Re'
	else:
		return 'err'

def Rrefrstrpar (par):
	if par=='R3':
		return 0
	elif par=='R30':
		return 64
	elif par=='R300':
		return 128
	elif par=='Re':
		return 192
	else:
		return 'errval'

def strvalsen(par):
	if par==0:
		return 'u'
	if par==1:
		return 'R'
	elif par==2:
		return 'S'
	elif par==3:
		return 'B'
	elif par==4:
		return 'J'
	elif par==5:
		return 'T'
	elif par==6:
		return 'E'
	elif par==7:
		return 'K'
	elif par==8:
		return 'N'
	elif par==9:
		return 'A1'
	elif par==10:
		return 'A2'
	elif par==11:
		return 'A3'
	elif par==12:
		return 'L'
	#elif par==13:
	# return 'M'
	elif par==13:
		return 'r'
	elif par==14:
		return '10M'
	elif par==15:
		return '50M'
	elif par==16:
		return '100M'
	elif par==17:
		return '10P'
	elif par==18:
		return '50P'
	elif par==19:
		return '100P'
	elif par==20:
		return '500P'
	elif par==21:
		return 'Pt10'
	elif par==22:
		return 'Pt50'
	elif par==23:
		return 'Pt100'
	elif par==24:
		return 'ISH1'
	elif par==25:
		return 'ISH2'
	elif par==26:
		return 'ISH3'
	#elif par==28:
	# return 'ISH4'
	elif par==255:
		return 'non'
	else:
		return 'errval'
	
def valsenstr(par):
	if par=='u':
		return 0
	if par=='R':
		return 1
	elif par=='S':
		return 2
	elif par=='B':
		return 3
	elif par=='J':
		return 4
	elif par=='T':
		return 5
	elif par=='E':
		return 6
	elif par=='K':
		return 7
	elif par=='N':
		return 8
	elif par=='A1':
		return 9
	elif par=='A2':
		return 10
	elif par=='A3':
		return 11
	elif par=='L':
		return 12
	elif par=='M':
		return 13
	elif par=='r':
		return 13
	elif par=='10M':
		return 14
	elif par=='50M':
		return 15
	elif par=='100M':
		return 16
	elif par=='10P':
		return 17
	elif par=='50P':
		return 18
	elif par=='100P':
		return 19
	elif par=='500P':
		return 20
	elif par=='Pt10':
		return 21
	elif par=='Pt50':
		return 22
	elif par=='Pt100':
		return 23
	elif par=='ISH1':
		return 24
	elif par=='ISH2':
		return 25
	elif par=='ISH3':
		return 26
	elif par=='ISH4':
		return 27
	elif par=='non':
		return 255
	else:
		return 'errval'
	

def valstrdev(par):
	if par=='УТМ-2':
		return 0
	if par=='ТР-1М':
		return 1
	elif par=='ТР-1М-У1':
		return 2
	elif par=='ТРС 1500':
		return 3
	elif par=='ТР20':
		return 4
	elif par=='КР-40-2':
		return 5
	elif par=='КР80':
		return 6
	elif par=='ТС600':
		return 7
	elif par=='МТП-2МР-50-500':
		return 8
	elif par=='АЧТ 45/40/100':
		return 9
	elif par=='МТП-2МР-70-1000':
		return 10
	elif par=='ПШ 1200':
		return 11
	elif par=='ВТП1600-1':
		return 12
	elif par=='МТП 1200-4':
		return 13
	elif par=='РЕЗЕРВ':
		return 14
	elif par=='АЧТ 165/40/100':
		return 15
	elif par=='ПЧТ 540/40/100':
		return 16
	elif par=='ПЧТ 280/40/450':
		return 17
	elif par=='ПРТ 50-700':
		return 18
	elif par=='ПРТ 600-1100':
		return 19
	elif par=='ТС 1100':
		return 20
	elif par=='ТС25':
		return 21
	elif par=='ТР-1-М-В':
		return 22
	elif par=='КР-190':
		return 23
	elif par=='АЧТ 70/-40/80':
		return 24
	elif par=='АЧТ 80/50/1500':
		return 25
	elif par=='КС-1200':
		return 26
	elif par=='КС-150':
		return 27
	elif par=='ВТП-1800':
		return 28
	#elif par==255:
	# return 'non'
	else:
		return 'errval'

def strvalmode(par):
	if par==0:
		return 'OFF'
	if par==1:
		return 'ON'
 
def strvaldev(par):
	if par==0:
		return 'УТМ-2'
	if par==1:
		return 'ТР-1М'
	elif par==2:
		return 'ТР-1М-У1'
	elif par==3:
		return 'ТРС 1500'
	elif par==4:
		return 'ТР20'
	elif par==5:
		return 'КР-40-2'
	elif par==6:
		return 'КР80'
	elif par==7:
		return 'ТС600'
	elif par==8:
		return 'МТП-2МР-50-500'
	elif par==9:
		return 'АЧТ 45/40/100'
	elif par==10:
		return 'МТП-2МР-70-1000'
	elif par==11:
		return 'ПШ 1200'
	elif par==12:
		return 'ВТП1600-1'
	elif par==13:
		return 'МТП 1200-4'
	elif par==14:
		return 'РЕЗЕРВ'
	elif par==15:
		return 'АЧТ 165/40/100'
	elif par==16:
		return 'ПЧТ 540/40/100'
	elif par==17:
		return 'ПЧТ 280/40/450'
	elif par==18:
		return 'ПРТ 50-700'
	elif par==19:
		return 'ПРТ 600-1100'
	elif par==20:
		return 'ТС 1100'
	elif par==21:
		return 'ТС25'
	elif par==22:
		return 'ТР-1-М-В'
	elif par==23:
		return 'КР-190'
	elif par==24:
		return 'АЧТ 70/-40/80'
	elif par==25:
		return 'АЧТ 80/50/1500'
	elif par==26:
		return 'КС-1200'
	elif par==27:
		return 'КС-150'
	elif par==28:
		return 'ВТП-1800'
	#elif par==255:
	# return 'non'
	else:
		return 'errval'