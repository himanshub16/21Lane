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
}

Dialog::~Dialog()
{
    delete ui;
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
}
