#ifndef SETTINGS_H
#define SETTINGS_H

#include <QString>

#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonParseError>

#define CONFIG_FILE "settings.json"

class Settings
{
public:
    Settings();
    bool loadSettings();
    bool saveSettings() const;

    QString publicName;
    QString downloadLocation;
    QString sharedLocation;
    int port;
    int speedLimit;
    QString exchangeURL;

};

#endif // SETTINGS_H
