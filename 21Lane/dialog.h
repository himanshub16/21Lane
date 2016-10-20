#ifndef DIALOG_H
#define DIALOG_H

#include "settings.h"

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

#define STATS_FILE "stats.json"

#define FTP_SERVER "python"
// unix lovers like me. Pardon for .exe
// But don't want to change code for compiling on windows.
// and file extension does not matter on Unix.
// Well, that's absracted behind the application.

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
private:
    Ui::Dialog *ui;
    Settings settings;
    QProcess ftpserver;
    QStringList serverArgs;
    QFileSystemWatcher statsMonitor;

    void populateForm();
    void toggleServer();

protected:
    void closeEvent(QCloseEvent *) Q_DECL_OVERRIDE;
    void keyPressEvent(QKeyEvent *);
};

#endif // DIALOG_H
