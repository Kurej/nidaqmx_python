import sys
import time
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg

np.random.seed(10**7)
chans = 2
buffer = 100
plotsize = 30*buffer
loop_pause_seconds = 0.0

class App(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)

        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtGui.QVBoxLayout())

        self.canvas = pg.GraphicsLayoutWidget()
        self.mainbox.layout().addWidget(self.canvas)

        self.label = QtGui.QLabel()
        self.mainbox.layout().addWidget(self.label)


        # Setup the two line plots
        self.plot1 = self.canvas.addPlot()
        self.h1 = self.plot1.plot(pen='y')

        self.canvas.nextRow()
        self.otherplot = self.canvas.addPlot()
        self.h2 = self.otherplot.plot(pen='y')


        #### Set Data  #####################
        self.y = np.zeros(shape=(plotsize, chans))
        self.x = np.linspace(start=0, stop=plotsize, num=self.y.shape[0])
        self.counter = 0
        self.fps = 0.
        self.lastupdate = time.time()

        #### Start  #####################
        self._update()

    def _update(self):

        for chan in range(chans):
            newdata = np.random.randn(buffer)
            self.y[:,chan] = np.append(self.y[buffer:, chan], newdata)

        self.h1.setData(self.y[:,0])
        self.h2.setData(self.y[:,1])

        now = time.time()
        dt = (now-self.lastupdate)
        if dt <= 0:
            dt = 0.000000000001
        fps2 = 1.0 / dt
        self.lastupdate = now
        self.fps = self.fps * 0.9 + fps2 * 0.1
        tx = 'Mean Frame Rate:  {fps:.3f} FPS'.format(fps=self.fps )
        self.label.setText(tx)
        QtCore.QTimer.singleShot(1, self._update)
        self.counter += 1
        time.sleep(loop_pause_seconds)


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    thisapp = App()
    thisapp.show()
    sys.exit(app.exec_())