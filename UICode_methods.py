from UI import *
import sys
import serial
from PyQt5 import QtCore, QtWidgets

global porta
porta = serial.Serial()


def handleButton():
    print("clk")
    #while (porta.inWaiting() == 0):
    #    pass
    #line = porta.readline()
    print(4)


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

        # Inicia programa
        program()
        print(2)
    except serial.serialutil.SerialException:
        dlg = QMessageBox(None)
        dlg.setWindowTitle("Error!")
        dlg.setIcon(QMessageBox.Warning)
        dlg.setText(
            "<center>Failed to receive data!<center> \n\n <center>Check Serial Ports and Telemetry System.<center>")
        dlg.exec_()


def program():
    try:
        if porta.is_open:
            while True:
                while (porta.inWaiting() == 0):
                    pass
                line = porta.readline()
                print(line)
                break
    finally:
        QtCore.QTimer.singleShot(time, program)


def processOneThing():
    print(22)


# Roda janela
app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)

# Conecta sinal do botao com a funcao
ui.pushButton.clicked.connect(handleButton)
ui.comboBox_SerialPorts.addItems(serial_ports())  # mostra as portas seriais disponíveis
ui.pushButton_UpdatePorts.clicked.connect(update_ports)  # botão para atualizar as portas seriis disponíveis
ui.pushButton_StartProgram.clicked.connect(start_program)  # botão para iniciar o programa
# ui.comboBox_Baudrate.currentIndexChanged.connect(self.selection_baudrate)
time = ui.doubleSpinBox_UpdateTime.value() * 1000
#timer = QtCore.QTimer()
#timer.timeout.connect(program)
#timer.start(time)
