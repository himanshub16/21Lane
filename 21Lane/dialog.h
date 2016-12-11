#ifndef DIALOG_H
#define DIALOG_H

#include "settings.h"
#include "downloader.h"

#include <QDialog>
#include <QListWidget>
#include <QProcess>
#include <QMessageBox>
#include <QDir>
#include <QDebug>
#include <QCloseEvent>
#include <QKeyEvent>
#include <QStringList>
#include <QFileSystemWatcher>
#include <QJsonArray>
#include <QJsonValue>
#include <QThreadPool>
#include <QTime>

#define STATS_FILE "stats.json"
#define LIST_FILE "dirlist.json"
#define MAX_WORKERS 3

QString toHumanReadable(double size);

namespace Ui {
class Dialog;
}

class Dialog : public QDialog
{
    Q_OBJECT

public:
    explicit Dialog(QWidget *parent = 0);
    ~Dialog();

private slots:

    void on_sharedLocationBtn_clicked();

    void on_downloadLocationBtn_clicked();

    void on_speedLimitSlider_valueChanged(int value);

    void on_speedLimitSpin_valueChanged(int value);

    void on_toggleShareBtn_clicked();

    void ftpServerStarted();
    void ftpServerFinished(int exitCode);
    void ftpServerError(QProcess::ProcessError err);
    void statsUpdater(QString fileName);
    void ftpList(QString host, int port, QString path);

    void on_browserGoBtn_clicked();

    void on_pushButton_clicked();

    void on_browserPrevBtn_clicked();

private:
    Ui::Dialog *ui;
    Settings settings;
    QProcess ftpserver;
    QStringList serverArgs;
    QFileSystemWatcher statsMonitor;

#ifndef Q_OS_UNIX
    QString PYTHON = QDir(QDir::current()).filePath("python");
#else
    QString PYTHON = "python";
#endif

    // for the browser
    QProcess ftpClient;
    QString clientHost;
    int clientPort;
    QString clientCurrentPath;
    QString clientPrevPath;


    void populateForm();
    void toggleServer();

protected:
    void closeEvent(QCloseEvent *) Q_DECL_OVERRIDE;
    void keyPressEvent(QKeyEvent *);
};

#endif // DIALOG_H
