#include "dialog.h"
#include "ui_dialog.h"


#include <QFileDialog>
#include <QDir>
#include <QSpacerItem>
#include <QProgressBar>
#include <QNetworkReply>

QString toHumanReadable(double size)
{
    double bytes = size;
    double kb    = bytes / 1024;
    double mb    = bytes / 1048576;
    double gb    = bytes / 1073741824;

    if ((int)gb > 0) {
        return QString::number(gb, 'f', 2).append(" GB");
    } else if ((int)mb > 0) {
        return QString::number(mb, 'f', 2).append(" MB");
    } else if ((int)kb > 0) {
        return QString::number(kb, 'f', 2).append(" KB");
    } else {
        return QString::number(bytes).append(" bytes");
    }
}


Dialog::Dialog(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::Dialog)
{
    ui->setupUi(this);
    this->populateForm();

    this->ftpserver.setProgram(PYTHON);
    connect(&this->ftpserver, SIGNAL(started()), this, SLOT(ftpServerStarted()));
    connect(&this->ftpserver, SIGNAL(finished(int)), this, SLOT(ftpServerFinished(int)));;
    connect(&this->ftpserver, SIGNAL(error(QProcess::ProcessError)), this, SLOT(ftpServerError(QProcess::ProcessError)));

    this->statsMonitor.addPath(QDir(QDir::current()).filePath(STATS_FILE));
    connect(&this->statsMonitor, SIGNAL(fileChanged(QString)), this, SLOT(statsUpdater(QString)));
}

Dialog::~Dialog()
{
    delete ui;
}

void Dialog::statsUpdater(QString fileName)
{
    QFile statsFile(fileName);
    if (!statsFile.open(QIODevice::ReadOnly)) {
        qWarning("Cannot open stats file.");
        return;
    }
    QJsonDocument statsJson (QJsonDocument::fromJson(statsFile.readAll()));
    QJsonObject statsObject (statsJson.object());

    ui->stats_connected->setText(QString::number(statsObject["connected"].toDouble()));
    ui->stats_files->setText(QString::number(statsObject["files_transferred"].toDouble()).append(" files"));
    ui->stats_bytes->setText(toHumanReadable(statsObject["bytes_transferred"].toDouble()));
    statsFile.close();
}

void Dialog::populateForm()
{
    this->settings.loadSettings();
    ui->publicName->setText(this->settings.publicName);
    ui->port->setValue(this->settings.port);
    ui->sharedLocationInput->setText(this->settings.sharedLocation);
    ui->downloadLocationInput->setText(this->settings.downloadLocation);
    ui->exchangeURL->setText(this->settings.exchangeURL);
    ui->speedLimitSlider->setValue(this->settings.speedLimit);
    ui->speedLimitSpin->setValue(this->settings.speedLimit);
}

void Dialog::closeEvent(QCloseEvent *e)
{
    qDebug() << "closeevent called";
    qDebug() << "close accepted";
    e->accept();
}

void Dialog::keyPressEvent(QKeyEvent *e)
{
    if (e->key() == Qt::Key_Escape) {
        qDebug() << "Escape key pressed";
        e->ignore();
    }
}

void Dialog::on_sharedLocationBtn_clicked()
{
    QString dirName = QFileDialog::getExistingDirectory(this, tr("Select location to share"), QDir::homePath(), QFileDialog::ShowDirsOnly);
    ui->sharedLocationInput->setText(dirName);
}

void Dialog::on_downloadLocationBtn_clicked()
{
    QString dirName = QFileDialog::getExistingDirectory(this, tr("Select location to share"), QDir::homePath(), QFileDialog::ShowDirsOnly);
    ui->downloadLocationInput->setText(dirName);
}

void Dialog::on_speedLimitSlider_valueChanged(int value)
{
    ui->speedLimitSpin->setValue(value);
}

void Dialog::on_speedLimitSpin_valueChanged(int value)
{
    ui->speedLimitSlider->setValue(value);
}

void Dialog::on_toggleShareBtn_clicked()
{
    this->settings.publicName = ui->publicName->text();
    this->settings.port       = ui->port->value();
    this->settings.sharedLocation = ui->sharedLocationInput->text();
    this->settings.downloadLocation = ui->downloadLocationInput->text();
    this->settings.speedLimit = ui->speedLimitSpin->value();
    this->settings.exchangeURL = ui->exchangeURL->text();
    this->settings.saveSettings();

    if( this->settings.publicName.isEmpty() ||
        this->settings.port == 0 ||
        this->settings.sharedLocation.isEmpty() ||
        this->settings.downloadLocation.isEmpty() ) {
        QMessageBox::warning(this, "Arrghh...", "Please fill proper details.", QMessageBox::Ok, QMessageBox::Ok);
        return;
    }

    if (!QDir(this->settings.sharedLocation).exists()) {
//        QMessageBox::warning(this, "Invalid", "The shared location chosen does not exist.", QMessageBox::Ok, QMessageBox::OK);
        return;
    }

    if (!QDir(this->settings.downloadLocation).exists()) {
        QMessageBox::warning(this, "Invalid", "The download location chosen does not exist.", QMessageBox::Ok, QMessageBox::Ok);
        return;
    }

    this->toggleServer();
}

void Dialog::toggleServer()
{
    if (this->ftpserver.state() == QProcess::NotRunning) {
        this->serverArgs.clear();
        this->serverArgs << QDir(QDir::current()).filePath("ftpserver.py") << QString::number(this->settings.port) << this->settings.sharedLocation;
        this->ftpserver.setArguments(this->serverArgs);
        this->ftpserver.start();
        ui->toggleShareBtn->setEnabled(false);
    } else if (this->ftpserver.state() == QProcess::Running) {
        this->ftpserver.kill();
        ui->toggleShareBtn->setEnabled(false);
    }
}

void Dialog::ftpServerStarted()
{
    ui->toggleShareBtn->setText("Stop Sharing");
    ui->toggleShareBtn->setEnabled(true);
    qDebug() << "Server started";
}

void Dialog::ftpServerFinished(int exitCode)
{
    ui->toggleShareBtn->setText("Start Sharing");
    qDebug() << "Server finished " << (this->ftpserver.state() == QProcess::NotRunning) ;
    ui->toggleShareBtn->setEnabled(true);
}

void Dialog::ftpServerError(QProcess::ProcessError err)
{
    qDebug() << "Server error";
}

void Dialog::on_browserGoBtn_clicked()
{
    this->clientPrevPath = this->clientCurrentPath;
    this->clientCurrentPath = ui->browserInput->text();
    this->clientHost = "localhost";
    this->clientPort = 2121;

    switch(QProcess::execute(PYTHON, QStringList() << QDir(QDir::current()).filePath("ftpclient.py") << this->clientHost << QString::number(this->clientPort) << this->clientCurrentPath)) {
    case -1:
        qDebug() << "Program crashed.";
        return;

    case -2:
        qDebug() << "Program cannot be started";
        return;
    }

    QFile listFile(LIST_FILE);
    if (!listFile.open(QIODevice::ReadOnly)) {
        qDebug() << "dirlist file cannot be opened for reading.";
        return;
    }

    QByteArray jsonData = listFile.readAll();
    QJsonDocument jsonDoc (QJsonDocument::fromJson(jsonData));
    if(!jsonDoc.isArray()) {
        qDebug() << "Directory listing is not a json array";
        return;
    }
    QJsonArray dirList(jsonDoc.array());

    // we are successful so far.
    // clear the browser grid
    while(ui->browserGrid->count()) {
        ui->browserGrid->takeAt(0)->widget()->deleteLater();
    }

    ui->browserGrid->update();

    // adding headers
    int i = 0;
    ui->browserGrid->addWidget(new QLabel("<b>Size</b>"), i, 1);
    ui->browserGrid->addWidget(new QLabel("<b>Name</b>"), i, 2);
    i++;

    foreach (QJsonValue item, dirList) {
        QJsonObject obj = item.toObject();
        if (obj["isDir"].toBool()) {
            QPushButton *chdirBtn = new QPushButton(QIcon(":images/folder.png"), "");
            chdirBtn->setFixedSize(30 , 30);
            connect(chdirBtn, &QPushButton::clicked, [=]() {
                ui->browserInput->setText(obj["ftpPath"].toString());
                ui->browserGoBtn->click();
            });
            ui->browserGrid->addWidget(chdirBtn, i, 0, Qt::AlignCenter);

        } else {
            QPushButton *downBtn = new QPushButton(QIcon(":images/download.png"),"");
            downBtn->setFixedSize(30, 30);
            ui->browserGrid->addWidget(downBtn, i, 0, Qt::AlignCenter);

            connect(downBtn, &QPushButton::clicked, [=]() {
                Downloader *worker = new Downloader;
                worker->URL = obj["URL"].toString();
                QDir targetFile(this->settings.downloadLocation);
                QString t = targetFile.filePath(obj["fileName"].toString());
                if (QDir(t).exists()) {
                    int i = 0;
                    while (QDir(t).exists()) {
                        t = QString::number(i);
                    }
                }
                worker->targetPath = t;

                connect(worker->reply, &QNetworkReply::readyRead, [=](){
                    QByteArray data = worker->reply->readAll();
                    worker->output->write(data);
                    worker->completed += data.length();
                    qDebug() << worker->completed;
                });
            });
        }

        ui->browserGrid->addWidget(new QLabel(QString(toHumanReadable(obj["fileSize"].toDouble()))), i, 1, Qt::AlignLeft);
        ui->browserGrid->addWidget(new QLabel(obj["fileName"].toString()), i, 2);
        i++;
    }

    QSpacerItem *spacer = new QSpacerItem(0, 0, QSizePolicy::Minimum, QSizePolicy::MinimumExpanding);
    ui->browserGrid->addItem(spacer, i, 0);
    ui->browserGrid->setSpacing(10);
}

void Dialog::ftpList(QString host, int port, QString path)
{

}

void Dialog::on_pushButton_clicked()
{
    ui->browserInput->setText("/");
    ui->browserGoBtn->click();
}

void Dialog::on_browserPrevBtn_clicked()
{
    ui->browserInput->setText(this->clientPrevPath);
    ui->browserGoBtn->click();
}
