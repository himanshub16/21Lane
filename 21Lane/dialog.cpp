#include "dialog.h"
#include "ui_dialog.h"

#include <QFileDialog>
#include <QDir>

Dialog::Dialog(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::Dialog)
{
    ui->setupUi(this);
    this->populateForm();

//    this->ftpserver.setProgram(QDir(QDir::current()).filePath(FTP_SERVER));
    this->ftpserver.setProgram("python");
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
    ui->stats_bytes->setText(statsObject["bytes_transferred_str"].toString());
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
    qDebug() << "Server finished " << (this->ftpserver.state() == QProcess::NotRunning) ;
    ui->toggleShareBtn->setEnabled(true);
}

void Dialog::ftpServerError(QProcess::ProcessError err)
{
    qDebug() << "Server error";
}
