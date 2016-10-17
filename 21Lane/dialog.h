#ifndef DIALOG_H
#define DIALOG_H

#include "settings.h"

#include <QDialog>
#include <QListWidget>

namespace Ui {
class Dialog;
}

class Dialog : public QDialog
{
    Q_OBJECT

public:
    explicit Dialog(QWidget *parent = 0);
    void populateForm();
    ~Dialog();

private slots:
    void on_sharedLocationBtn_clicked();

    void on_downloadLocationBtn_clicked();

    void on_speedLimitSlider_valueChanged(int value);

    void on_speedLimitSpin_valueChanged(int value);

    void on_toggleShareBtn_clicked();

private:
    Ui::Dialog *ui;
    Settings settings;
};

#endif // DIALOG_H
