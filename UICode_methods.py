from UI import *
import sys
import serial
from UICode_methods import *
from PyQt5 import QtCore, QtWidgets
import numpy as np
import pyqtgraph as pg
from time import sleep, time
from datetime import datetime


global porta, N, readAvailable, currTime, tim, lastTime
porta = serial.Serial()
Nchannels = 3
Nsamples = 105  # no of samples per channel
Nbytes = Nsamples*2  # no of bytes received per channel
tam = Nbytes * Nchannels  # no of bytes received total
readAvailable = False
samplingFreq = 1096
last_en_time = 0
error_count = 0
tim = time()
lastTime = time()



tensao = 0
corrente = np.zeros(int(Nsamples))
potencia = np.zeros(int(Nsamples))
iluminancia = np.zeros(int(Nsamples/3))
termopar = np.zeros(int(Nsamples/3))
lm35 = np.zeros(int(Nsamples/3))
temp = np.arange(0, 1000/samplingFreq*Nsamples, 1000/samplingFreq)
temp2 = np.arange(0, 1000/samplingFreq*Nsamples, 3000/samplingFreq)


# Lista as portas seriais disponiveis
def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


# Atualiza portas seriais disponiveis
def update_ports():
    ui.comboBox_SerialPorts.clear()
    ui.comboBox_SerialPorts.addItems(serial_ports())
    #ui.comboBox_SerialPorts.currentIndexChanged.connect(selection_port())


def selection_port(i):
    return ui.comboBox_SerialPorts.itemText(i)


# Inicializa o programa
def start_program():
    # abre e configura a porta serial utilizando os valores definidos
    try:
        porta.baudrate = int(ui.comboBox_Baudrate.currentText())
        porta.port = str(ui.comboBox_SerialPorts.currentText())
        porta.timeout = 1
        porta.open()
        print(" Porta serial " + str(porta.name) + " aberta")
        print(porta.is_open)
        global readAvailable
        readAvailable = True
        sleep(2)
        print('aq')
        # Inicia programa
        program()
        print('Fecho')
    except serial.serialutil.SerialException:
        dlg = QMessageBox(None)
        dlg.setWindowTitle("Error!")
        dlg.setIcon(QMessageBox.Warning)
        dlg.setText(
            "<center>Failed to receive data!<center> \n\n <center>Check Serial Ports and Telemetry System.<center>")
        dlg.exec_()


def separate_buffer(buf, init, end):
    vect = np.zeros(int((end-init)/2))
    for i in range(init, end, 2):
        aux = buf[i]
        vect[int((i-init)/2)] = (aux << 8) | buf[i+1]
    return vect


def program():
    try:
        if readAvailable:
            # Le conjunto de dados da porta serial
            read_buffer = read_all()
            # print(read_buffer)

            init = 0
            end = int(Nbytes)
            tensao = separate_buffer(read_buffer, init, end)

            init = int(Nbytes)
            end = int(2*Nbytes)
            corrente = separate_buffer(read_buffer, init, end)

            init = int(2*Nbytes)
            end = int(2*Nbytes + Nbytes/3)
            iluminancia = separate_buffer(read_buffer, init, end)

            init = int(2*Nbytes + Nbytes/3)
            end = int(2*Nbytes + 2*Nbytes/3)
            termopar = separate_buffer(read_buffer, init, end)

            init = int(2*Nbytes + 2*Nbytes/3)
            end = int(3*Nbytes)
            lm35 = separate_buffer(read_buffer, init, end)

            # Atualiza grafico tensao
            ui.graphicsView.clear()
            ui.graphicsView.plot(temp, tensao, pen='r')
            ui.lineEdit.setText(str(np.amax(tensao)))
            ui.lineEdit_2.setText(str(round(np.amax(tensao)/np.sqrt(2), 2)))

            # Atualiza grafico corrente
            ui.graphicsView_2.clear()
            ui.graphicsView_2.plot(temp, corrente, pen=pg.mkPen('b'))
            ui.lineEdit_3.setText(str(np.amax(corrente)))
            ui.lineEdit_4.setText(str(round(np.amax(corrente)/np.sqrt(2), 2)))

            # Atualiza grafico potencia
            potencia = tensao*corrente
            ui.graphicsView_3.clear()
            ui.graphicsView_3.plot(temp, potencia, pen='r')

            # Atualiza grafico iluminancia
            ui.graphicsView_6.clear()
            ui.graphicsView_6.plot(temp2, iluminancia, pen=pg.mkPen('r'))

            # Atualiza grafico temperaturas
            ui.graphicsView_5.clear()
            ui.graphicsView_5.plot(temp2, termopar, pen=pg.mkPen('r'))
            ui.graphicsView_5.plot(temp2, lm35, pen=pg.mkPen('b'))

            # Calcula FPS
            global tim, lastTime
            tim = time()
            deltaT = round((tim - lastTime)*1000)
            fps = round(1/(tim-lastTime), 2)
            ui.label_15.setText(str(fps))
            lastTime = tim

    finally:
        # Chama de novo funcao prgram() depois de update_time segundos
        QtCore.QTimer.singleShot(update_time, program)


def read_all():
    """Read all characters on the serial port and return them."""
    if not porta.timeout:
        raise TypeError('Port needs to have a timeout set!')

    read_buffer = b''
    while True:
        while (porta.inWaiting() == 0):
            pass
        firstByte = porta.read()
        print('FB = ' + str(int.from_bytes(firstByte, byteorder='big')))
        if int.from_bytes(firstByte, byteorder='big') == 254:
            #print("achou first byte")
            break
        else:
            error_count = error_count + 1
            ui.label_17.setText(str(error_count))
    while True:
        # Read in chunks. Each chunk will wait as long as specified by
        # timeout. Increase chunk_size to fail quicker

        byte_chunk = porta.read(size=tam)
        read_buffer += byte_chunk
        if len(byte_chunk) == tam:
            break
        else:
            print('Chegou aqui')

    return read_buffer

def processOneThing():
    print(22)


# Roda janela
app = QtWidgets.QApplication(sys.argv)
app.setStyle("fusion")
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)

# Conecta sinal do botao com a funcao
ui.comboBox_SerialPorts.addItems(serial_ports())  # mostra as portas seriais disponíveis
ui.pushButton_UpdatePorts.clicked.connect(update_ports)  # botão para atualizar as portas seriis disponíveis
ui.pushButton_StartProgram.clicked.connect(start_program)  # botão para iniciar o programa
# ui.comboBox_Baudrate.currentIndexChanged.connect(self.selection_baudrate)
update_time = ui.doubleSpinBox_UpdateTime.value() * 1000

# Labels tensao
ui.graphicsView.setLabel('left', "Tensão", units='V')
ui.graphicsView.setLabel('bottom', "Tempo", units='ms')
ui.graphicsView.setYRange(0, 1000)

# Labels corrente
ui.graphicsView_2.setLabel('left', "Corrente", units='A')
ui.graphicsView_2.setLabel('bottom', "Tempo", units='ms')
ui.graphicsView_2.setYRange(0, 1000)

# Labels potencia
ui.graphicsView_3.setLabel('left', "Potencia", units='W')
ui.graphicsView_3.setLabel('bottom', "Tempo", units='ms')
ui.graphicsView_3.setYRange(0, 1000)

# Labels temperatura
ui.graphicsView_5.setLabel('left', "Temperatura", units='C')
ui.graphicsView_5.setLabel('bottom', "Tempo", units='ms')
ui.graphicsView_5.setYRange(0, 300)

# Labels iluminancia
ui.graphicsView_6.setLabel('left', "Iluminancia", units='lx')
ui.graphicsView_6.setLabel('bottom', "Tempo", units='ms')
ui.graphicsView_6.setYRange(0, 300)

# Sampling freq
ui.label_16.setText(str(samplingFreq))


MainWindow.show()
sys.exit(app.exec_())
