#include "downloader.h"

void Downloader::run()
{
    this->completed = 0;
    QNetworkRequest req(this->URL);
    this->reply = manager.get(req);
    output = new QFile(this->targetPath);

    if (!output->open(QIODevice::WriteOnly)) {
        qWarning("Cannot open file for writing.");
        return;
    }

    // rather than implementing complete signal slot mechanism and interfacing it,
    // make the slots in the main thread, and data members of this class public
    /*
    connect(this->reply, &QNetworkReply::readyRead, [=]() {
        this->output->write(this->reply->readAll());
    });

    connect(this->reply, &QNetworkReply::finished, [=]() {
        this->output->close();
    });*/
}
