# -*- coding: utf-8 -*-

import logging

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QStatusBar
from .CStatusBarLabel import CustomStatusBarLabel

from misc import debounce, getHumanBytesNumber

class CustomStatusBar(QStatusBar):
    app = None
    def __init__(self, parent = None):
        super().__init__(parent)
        self.app = QGuiApplication.instance()
        self.setupStatusBar()

    def setupStatusBar(self):
        self.xwaredStatus = CustomStatusBarLabel(self)
        self.etmStatus = CustomStatusBarLabel(self)
        self.frontendStatus = CustomStatusBarLabel(self)

        sp = self.frontendStatus.sizePolicy()
        sp.setHorizontalStretch(1)
        self.frontendStatus.setSizePolicy(sp)

        self.dlStatus = CustomStatusBarLabel(self)
        self.ulStatus = CustomStatusBarLabel(self)

        self.app.xwaredpy.sigXwaredStatusPolled.connect(self.slotXwaredStatusPolled)
        self.app.xwaredpy.sigETMStatusPolled.connect(self.slotETMStatusPolled)
        self.app.frontendpy.sigFrontendStatusChanged.connect(self.slotFrontendStatusChanged)
        self.app.etmpy.sigTasksSummaryUpdated[bool].connect(self.slotTasksSummaryUpdated)
        self.app.etmpy.sigTasksSummaryUpdated[dict].connect(self.slotTasksSummaryUpdated)

    @pyqtSlot(bool)
    def slotXwaredStatusPolled(self, enabled):
        self.app.mainWin.menu_backend.setEnabled(enabled)
        if enabled:
            self.xwaredStatus.setText(
                "<img src=':/image/check.png' width=14 height=14><font color='green'>xwared</font>")
            self.xwaredStatus.setToolTip("<div style='color:green'>xwared运行中</div>")
        else:
            self.xwaredStatus.setText(
                "<img src=':/image/attention.png' width=14 height=14><font color='red'>xwared</font>")
            self.xwaredStatus.setToolTip("<div style='color:red'>xwared未启动</div>")

    @pyqtSlot()
    def slotETMStatusPolled(self):
        enabled = self.app.xwaredpy.etmStatus

        self.app.mainWin.action_ETMstart.setEnabled(not enabled)
        self.app.mainWin.action_ETMstop.setEnabled(enabled)
        self.app.mainWin.action_ETMrestart.setEnabled(enabled)

        overallCheck = False
        tooltips = []
        if enabled:
            activationStatus = self.app.etmpy.getActivationStatus()
            tooltips.append("<div style='color:green'>ETM运行中</div>")
            if activationStatus.status == 1:
                overallCheck = True
                tooltips.append(
                    "<div style='color:green'>"
                        "<img src=':/image/connected.png' width=16 height=16>"
                    "设备已激活</div>")
            else:
                tooltips.append(
                    "<div style='color:red'>"
                        "<img src=':/image/disconnected.png' width=16 height=16>"
                    "设备未激活</div>")
        else:
            tooltips.append("<div style='color:red'>ETM未启动</div>")

        if overallCheck:
            self.etmStatus.setText(
                    "<img src=':/image/check.png' width=14 height=14><font color='green'>ETM</font>")
        else:
            self.etmStatus.setText(
                "<img src=':/image/attention.png' width=14 height=14><font color='red'>ETM</font>")

        self.etmStatus.setToolTip("".join(tooltips))

    @pyqtSlot()
    @debounce(0.5, instant_first = True)
    def slotFrontendStatusChanged(self):
        frontendStatus = self.app.frontendpy.getFrontendStatus()
        if all(frontendStatus):
            self.frontendStatus.setText(
                "<img src=':/image/check.png' width=14 height=14><font color='green'>前端</font>")
        else:
            self.frontendStatus.setText(
                "<img src=':/image/attention.png' width=14 height=14><font color='red'>前端</font>")

        self.frontendStatus.setToolTip(
            "<div style='color:{}'>页面代码已插入</div>\n"
            "<div style='color:{}'>设备已登录</div>\n"
            "<div style='color:{}'>设备在线</div>".format(*map(lambda s: "green" if s else "red",
                                                              frontendStatus)))
        print(frontendStatus)

    @pyqtSlot(bool)
    @pyqtSlot(dict)
    def slotTasksSummaryUpdated(self, summary):
        if not summary:
            self.dlStatus.setText(
                "<img src=':/image/down.png' height=14 width=14>获取下载状态失败"
            )
            self.dlStatus.setToolTip("")
            self.ulStatus.setText(
                "<img src=':/image/up.png' height=14 width=14>获取上传状态失败"
            )
            return

        self.dlStatus.setText(
            "<img src=':/image/down.png' height=14 width=14>{}/s".format(
                                        getHumanBytesNumber(summary["dlSpeed"])))
        self.dlStatus.setToolTip("{}任务下载中".format(summary["dlNum"]))
        self.ulStatus.setText(
            "<img src=':/image/up.png' height=14 width=14>{}/s".format(getHumanBytesNumber(summary["upSpeed"]))
        )
