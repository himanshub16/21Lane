#ifndef HTTPHANDLER_H
#define HTTPHANDLER_H

#include <QObject>

class HttpHandler : public QObject
{
    Q_OBJECT
public:
    explicit HttpHandler(QObject *parent = 0);

signals:

public slots:
};

#endif // HTTPHANDLER_H
