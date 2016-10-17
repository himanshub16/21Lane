#include "settings.h"

Settings::Settings()
{
    this->publicName = "anonymous";
    this->port = 2121;
    this->sharedLocation = "";
    this->downloadLocation = "";
    this->speedLimit = 2;
    this->exchangeURL = "";
}


bool Settings::loadSettings()
{
    QFile file(CONFIG_FILE);

    if (!file.open(QIODevice::ReadOnly)) {
        qWarning("File cannot be opened");
        return false;
    }

    QByteArray jsonData = file.readAll();
    file.close();
    if(jsonData.size() == 0) {
        qWarning("Configuration file empty. Using defaults.");
        return false;
    }
    QJsonParseError *err = new QJsonParseError();

    QJsonDocument jsonDoc (QJsonDocument::fromJson(jsonData, err));
    if (jsonDoc.isNull()) {
        qWarning("Settings file empty.");
        return false;
    }

    auto jObject = jsonDoc.object();

    if(err->error != 0) {
        qWarning("Error while parsing settings file.");
        return false;
    }

    this->publicName = jObject["publicName"].toString();
    this->port = jObject["port"].toInt();
    this->sharedLocation = jObject["sharedLocation"].toString();
    this->downloadLocation = jObject["downloadLocation"].toString();
    this->exchangeURL = jObject["exchangeURL"].toString();
    this->speedLimit = jObject["speedLimit"].toInt();

    delete err;
    return true;
}

bool Settings::saveSettings() const
{
    QFile file(CONFIG_FILE);
    if (!file.open(QIODevice::WriteOnly)) {
        qWarning("Cannot open file for writing.");
        file.close();
        return false;
    }

    QJsonObject jObject
    {
        {"publicName", this->publicName},
        {"port", this->port},
        {"sharedLocation", this->sharedLocation},
        {"downloadLocation", this->downloadLocation},
        {"exchangeURL", this->exchangeURL},
        {"speedLimit", this->speedLimit}
    };

    QJsonDocument jsonDoc(jObject);
    file.write(jsonDoc.toJson());
    file.close();

    return true;

}

