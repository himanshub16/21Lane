#-------------------------------------------------
#
# Project created by QtCreator 2016-10-16T12:12:57
#
#-------------------------------------------------

QT       += core gui widgets network
CONFIG   += c++11

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = 21Lane
TEMPLATE = app


SOURCES += main.cpp\
        dialog.cpp \
    settings.cpp \
    downloader.cpp

HEADERS  += dialog.h \
    settings.h \
    downloader.h

FORMS    += dialog.ui

RESOURCES += resources.qrc
