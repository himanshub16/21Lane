#ifndef DOWNLOADER_H
#define DOWNLOADER_H

#pragma once

#include <QRunnable>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QNetworkRequest>
#include <QFile>

class Downloader : public QObject, public QRunnable
{
    Q_OBJECT
public:
    void run();
    QNetworkReply *reply;
    QFile *output;
    QString targetPath;
    QString URL;
    qint64 completed;

private:
    QNetworkAccessManager manager;
};

#endif // DOWNLOADER_H
