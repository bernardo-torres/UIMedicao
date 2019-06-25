from UI import *
import sys
import serial
from UICode_methods import *
from PyQt5 import QtCore, QtWidgets
import numpy as np
import pyqtgraph as pg
from time import sleep, time


global porta, readAvailable, tim, lastTime, energia_acumulada, current_minute, last_en_time, error_count
porta = serial.Serial()
Nchannels = 3
Nsamples = 150  # no of samples per channel`
Nbytes = Nsamples*2  # no of bytes received per channel
tam = Nbytes * Nchannels  # no of bytes received total
readAvailable = False
samplingFreq = 2083
error_count = 0
tim = time()
lastTime = time()
last_en_time = time()
counter = 0

current_minute = 0
energia_acumulada = 0
En = np.array([])
x_tE = np.array([])

tensao = 0
corrente = np.zeros(int(Nsamples))
potencia = np.zeros(int(Nsamples))
iluminancia = np.zeros(int(Nsamples/3))
termopar = np.zeros(int(Nsamples/3))
lm35 = np.zeros(int(Nsamples/3))

# Vetores de tempo
temp = np.arange(0, 1000/samplingFreq*Nsamples, 1000/samplingFreq)
temp2 = np.arange(0, 1000/samplingFreq*Nsamples, 3000/samplingFreq)

line60hz1 = np.zeros(2)
line60hz2 = np.zeros(2)
line60hz1[0] = 60
line60hz1[1] = 60
line60hz2[0] = 0
line60hz2[1] = 1


class values:
    def __init__(self):
        self.tensao = 0
        self.corrente = 0
        self.iluminancia = 0
        self.termopar = 0
        self.lm35 = 0
        self.temperatura = 0
        self.fft_tensao = 0
        self.fft_corrente = 0
        self.potencia = 0


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


# Separa buffer de dados em um vetor com inicio em init e fim em end
def separate_buffer(buf, init, end):
    vect = np.zeros(int((end-init)/2))
    for i in range(init, end, 2):
        aux = buf[i]
        vect[int((i-init)/2)] = (aux << 8) | buf[i+1]
    return vect


def buffer_analisys(buf):
    # Separa buffer em variaveis especificas de tensao, corrente,
    # iluminancia e temperaturas. Buffer na ordem:
    # Nbytestensao, Nbytescorrente, Nbytes/3iluminancia, Nbytes/3temp1
    # e Nbytes/3temp2
    init = 0
    end = int(Nbytes)
    tensao = separate_buffer(buf, init, end)

    init = int(Nbytes)
    end = int(2*Nbytes)
    corrente = separate_buffer(buf, init, end)

    init = int(2*Nbytes)
    end = int(2*Nbytes + Nbytes/3)
    iluminancia = separate_buffer(buf, init, end)

    init = int(2*Nbytes + Nbytes/3)
    end = int(2*Nbytes + 2*Nbytes/3)
    termopar = separate_buffer(buf, init, end)

    init = int(2*Nbytes + 2*Nbytes/3)
    end = int(3*Nbytes)
    lm35 = separate_buffer(buf, init, end)
    temperatura = lm35 + termopar

    correcao = 5/1023
    ui.label_31.setText(str(np.mean(tensao*correcao)))
    ui.label_32.setText(str(np.mean(corrente*correcao)))
    ui.label_33.setText(str(np.mean(iluminancia*correcao)))
    ui.label_34.setText(str(np.mean(termopar*correcao)))
    ui.label_36.setText(str(np.mean(lm35*correcao)))
    # Aplica ganhos
    if ui.checkBox.isChecked() == 1:

        ganho_ampiso = 1/8

        ganho_tensao = 1001
        ganho_corrente = 5/6
        offset = 2.35

        ganho_LM = 100/(1 + 2000/220)

        ganho_transimp = 1/150000
        ganho_fotodiodo = 10000000000/778

        offset_erro = 2.75
        ganho_inversor = -270/180
        ganho_termopar = 82/200082
        ganho_seebeck = 10000000/406

        tensao = correcao*tensao - offset
        tensao = ganho_tensao*ganho_ampiso*tensao

        corrente = correcao*corrente - offset
        corrente = ganho_corrente*ganho_ampiso*corrente*1000  # corrente em mA

        iluminancia = correcao*ganho_transimp*ganho_fotodiodo*iluminancia

        lm35 = correcao*ganho_LM*lm35
        termopar = correcao*termopar - offset_erro
        termopar = ganho_inversor*ganho_termopar*ganho_seebeck*termopar
        temperatura = lm35 + termopar

    # Computa fft
    fft_tensao = np.fft.fft(tensao)
    fft_corrente = np.fft.fft(corrente)

    # calcula grafico tensao na freq
    fft_tensao = abs(fft_tensao) * 1/Nsamples
    fft_corrente = abs(fft_corrente) * 1/Nsamples
    # pega so as freq na banda de passagem. multiplica por dois por causa da simetria da transformada
    tensao_freq = 2*fft_tensao[:int(Nsamples/2)]
    fft_corrente = 2*fft_corrente[:int(Nsamples/2)]
    # tensao dc foi multiplicada por dois, voltamos ao valor original
    tensao_freq[0] *= 0.5
    fft_corrente[0] *= 0.5

    potencia = tensao*corrente/1000

    # energia (multiplica sempre pelo periodo)
    global energia_acumulada, current_minute, last_en_time, x_tE, En
    energia_acumulada += sum(potencia)/samplingFreq
    if time() - last_en_time > 60:
        last_en_time = time()
        if current_minute < 10:
            En = np.append(En, energia_acumulada)
            x_tE = np.append(x_tE, current_minute)
        else:
            En = np.append(En, energia_acumulada)
            En = np.delete(En, 0)
            x_tE += 1
            ui.graphicsView_4.setXRange(current_minute - 9, current_minute)
        ui.graphicsView_4.clear()
        ui.graphicsView_4.plot(x_tE, En,pen=pg.mkPen('r'))
        current_minute += 1
        energia_acumulada = 0

    data = values()
    data.tensao = tensao
    data.corrente = corrente
    data.iluminancia = iluminancia
    data.termopar = termopar
    data.lm35 = lm35
    data.temperatura = temperatura
    data.fft_tensao = tensao_freq
    data.fft_corrente = fft_corrente
    data.potencia = potencia

    return data


# Programa principal, roda continuamente
def program():
    try:
        if readAvailable:
            # Le conjunto de dados da porta serial
            read_buffer = read_all()
            # print(read_buffer)

            # Calcula FPS
            global tim, lastTime
            tim = time()
            deltaT = round((tim - lastTime)*1000)
            fps = round(1/(tim-lastTime), 2)
            ui.label_15.setText(str(fps))
            lastTime = tim

            if ui.checkBox_2.isChecked() == 1:
                return

            data = buffer_analisys(read_buffer)

            # Atualiza grafico tensao

            ui.graphicsView.clear()
            ui.graphicsView.plot(temp, data.tensao, pen='r')
            ui.lineEdit.setText(str(round(np.amax(data.tensao), 2)))
            rms = np.sqrt(np.mean(data.tensao**2))
            ui.lineEdit_2.setText(str(round(rms, 2)))

            # Atualiza grafico corrente
            ui.graphicsView_2.clear()
            ui.graphicsView_2.plot(temp, data.corrente, pen=pg.mkPen('b'))
            ui.lineEdit_3.setText(str(round(np.amax(data.corrente),2)))
            rms = np.sqrt(np.mean(data.corrente**2))
            ui.lineEdit_4.setText(str(round(rms, 2)))

            tab_index = ui.tabWidget_2.currentIndex()
            if tab_index == 0:
                # Atualiza grafico potencia
                ui.graphicsView_3.clear()
                ui.graphicsView_3.plot(temp, data.potencia, pen='r')

            elif tab_index == 2:
                # Atualiza grafico iluminancia
                ui.graphicsView_6.clear()
                ui.graphicsView_6.plot(temp2, data.iluminancia, pen=pg.mkPen('r'))
                ui.lineEdit_5.setText(str(round(np.mean(data.iluminancia), 2)))

                # Atualiza grafico temperaturas
                ui.graphicsView_5.clear()
                ui.graphicsView_5.plot(temp2, data.termopar, pen=pg.mkPen('r'))
                ui.graphicsView_5.plot(temp2, data.lm35, pen=pg.mkPen('b'))
                ui.graphicsView_5.plot(temp2, data.temperatura, pen=pg.mkPen('g'))
                ui.lineEdit_6.setText(str(round(np.mean(data.lm35), 2)))
                ui.lineEdit_7.setText(str(round(np.mean(data.termopar), 2)))
            elif tab_index == 1:

                # Vetor de frequencias
                if (Nsamples/2-1) == len(data.fft_tensao):
                    f = np.arange(0, int(Nsamples/2-1))/Nsamples
                else:
                    f = np.arange(0, int(Nsamples/2))/Nsamples

                f = samplingFreq*f
                # FFt tensao
                max = np.max(data.fft_tensao)
                ui.graphicsView_7.clear()
                ui.graphicsView_7.plot(f, data.fft_tensao, pen=pg.mkPen('k'))
                #ui.graphicsView_7.addLine(x=60, y=None, pen=pg.mkPen('g'))
                ui.graphicsView_7.plot(line60hz1, max*line60hz2,  pen=pg.mkPen('g'))
                ui.graphicsView_7.plot(2*line60hz1, max*line60hz2,  pen=pg.mkPen('g'))
                ui.graphicsView_7.plot(3*line60hz1, max*line60hz2,  pen=pg.mkPen('g'))

                # FFt corrente
                max = np.max(data.fft_corrente)
                ui.graphicsView_8.clear()
                ui.graphicsView_8.plot(f, data.fft_corrente,  pen=pg.mkPen('k'))
                ui.graphicsView_8.plot(line60hz1, max*line60hz2,  pen=pg.mkPen('g'))
                ui.graphicsView_8.plot(2*line60hz1, max*line60hz2,  pen=pg.mkPen('g'))
                ui.graphicsView_8.plot(3*line60hz1, max*line60hz2,  pen=pg.mkPen('g'))

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
        #print('FB = ' + str(int.from_bytes(firstByte, byteorder='big')))
        if int.from_bytes(firstByte, byteorder='big') == 254:
            a = porta.read()
            #print(a)
            #print("achou first byte")
            break
        else:
            global error_count
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
ui.graphicsView.setYRange(-200, 200)

# Labels corrente
ui.graphicsView_2.setLabel('left', "Corrente", units='mA')
ui.graphicsView_2.setLabel('bottom', "Tempo", units='ms')
ui.graphicsView_2.setYRange(-150, 150)

# Labels potencia
ui.graphicsView_3.setLabel('left', "Potencia", units='W')
ui.graphicsView_3.setLabel('bottom', "Tempo", units='ms')
ui.graphicsView_3.setYRange(-30, 50)

# Labels energia
ui.graphicsView_4.setLabel('left', "Energia acumulada", units='J/min')
ui.graphicsView_4.setLabel('bottom', "Tempo", units='min')
#ui.graphicsView_4.setYRange(0, 1000)


# Labels temperatura
ui.graphicsView_5.setLabel('left', "Temperatura", units='C')
ui.graphicsView_5.setLabel('bottom', "Tempo", units='ms')
ui.graphicsView_5.setYRange(-5, 90)

# Labels iluminancia
ui.graphicsView_6.setLabel('left', "Iluminancia", units='lux')
ui.graphicsView_6.setLabel('bottom', "Tempo", units='ms')
ui.graphicsView_6.setYRange(0, 400)

# Labels tensao fft
ui.graphicsView_7.setLabel('left', "Amplitude")
ui.graphicsView_7.setLabel('bottom', "Frequencia", units='Hz')
# ui.graphicsView_7.setYRange(0, 1000)

# Labels corrente fft
ui.graphicsView_8.setLabel('left', "Amplitude")
ui.graphicsView_8.setLabel('bottom', "Frequencia", units='Hz')
# ui.graphicsView_8.setYRange(0, 1000)

# Sampling freq
ui.label_16.setText(str(samplingFreq) + ' Hz')

# Data points
ui.label_19.setText(str(Nsamples))


MainWindow.show()
sys.exit(app.exec_())
