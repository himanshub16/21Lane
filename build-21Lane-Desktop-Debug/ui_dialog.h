/********************************************************************************
** Form generated from reading UI file 'dialog.ui'
**
** Created by: Qt User Interface Compiler version 5.5.1
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_DIALOG_H
#define UI_DIALOG_H

#include <QtCore/QVariant>
#include <QtWidgets/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QButtonGroup>
#include <QtWidgets/QDialog>
#include <QtWidgets/QDoubleSpinBox>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QLabel>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QSlider>
#include <QtWidgets/QSpacerItem>
#include <QtWidgets/QSpinBox>
#include <QtWidgets/QTabWidget>
#include <QtWidgets/QTableWidget>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_Dialog
{
public:
    QVBoxLayout *verticalLayout_4;
    QTabWidget *downloadsTable;
    QWidget *settingsTab;
    QWidget *widget;
    QVBoxLayout *verticalLayout_2;
    QGridLayout *gridLayout;
    QLineEdit *sharedLocationInput;
    QLineEdit *publicName;
    QPushButton *sharedLocationBtn;
    QLineEdit *downloadLocationInput;
    QLabel *label_4;
    QPushButton *downloadLocationBtn;
    QSpinBox *port;
    QLabel *label_2;
    QLabel *label;
    QDoubleSpinBox *speedLimitSpin;
    QSlider *speedLimitSlider;
    QLabel *label_5;
    QLineEdit *exchangeURL;
    QSpacerItem *verticalSpacer_3;
    QLabel *label_3;
    QSpacerItem *verticalSpacer_2;
    QHBoxLayout *horizontalLayout;
    QSpacerItem *horizontalSpacer;
    QPushButton *toggleShareBtn;
    QSpacerItem *horizontalSpacer_2;
    QSpacerItem *verticalSpacer;
    QWidget *usersListTab;
    QHBoxLayout *horizontalLayout_2;
    QTableWidget *usersTable;
    QWidget *browserTab;
    QVBoxLayout *verticalLayout;
    QHBoxLayout *horizontalLayout_4;
    QPushButton *browserPrevBtn;
    QPushButton *browserNextBtn;
    QLineEdit *browserInput;
    QPushButton *browserGoBtn;
    QTableWidget *browserTable;
    QWidget *downloadsTab;
    QHBoxLayout *horizontalLayout_3;
    QTableWidget *downloadsTable_2;

    void setupUi(QDialog *Dialog)
    {
        if (Dialog->objectName().isEmpty())
            Dialog->setObjectName(QStringLiteral("Dialog"));
        Dialog->resize(558, 348);
        verticalLayout_4 = new QVBoxLayout(Dialog);
        verticalLayout_4->setSpacing(6);
        verticalLayout_4->setContentsMargins(11, 11, 11, 11);
        verticalLayout_4->setObjectName(QStringLiteral("verticalLayout_4"));
        downloadsTable = new QTabWidget(Dialog);
        downloadsTable->setObjectName(QStringLiteral("downloadsTable"));
        downloadsTable->setTabBarAutoHide(false);
        settingsTab = new QWidget();
        settingsTab->setObjectName(QStringLiteral("settingsTab"));
        widget = new QWidget(settingsTab);
        widget->setObjectName(QStringLiteral("widget"));
        widget->setGeometry(QRect(9, 9, 521, 281));
        verticalLayout_2 = new QVBoxLayout(widget);
        verticalLayout_2->setSpacing(6);
        verticalLayout_2->setContentsMargins(11, 11, 11, 11);
        verticalLayout_2->setObjectName(QStringLiteral("verticalLayout_2"));
        verticalLayout_2->setContentsMargins(0, 0, 0, 0);
        gridLayout = new QGridLayout();
        gridLayout->setSpacing(6);
        gridLayout->setObjectName(QStringLiteral("gridLayout"));
        gridLayout->setSizeConstraint(QLayout::SetMaximumSize);
        sharedLocationInput = new QLineEdit(widget);
        sharedLocationInput->setObjectName(QStringLiteral("sharedLocationInput"));

        gridLayout->addWidget(sharedLocationInput, 1, 1, 1, 4);

        publicName = new QLineEdit(widget);
        publicName->setObjectName(QStringLiteral("publicName"));
        publicName->setMaxLength(100);

        gridLayout->addWidget(publicName, 0, 1, 1, 2);

        sharedLocationBtn = new QPushButton(widget);
        sharedLocationBtn->setObjectName(QStringLiteral("sharedLocationBtn"));

        gridLayout->addWidget(sharedLocationBtn, 1, 0, 1, 1);

        downloadLocationInput = new QLineEdit(widget);
        downloadLocationInput->setObjectName(QStringLiteral("downloadLocationInput"));

        gridLayout->addWidget(downloadLocationInput, 3, 1, 1, 4);

        label_4 = new QLabel(widget);
        label_4->setObjectName(QStringLiteral("label_4"));
        QSizePolicy sizePolicy(QSizePolicy::Preferred, QSizePolicy::Preferred);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(label_4->sizePolicy().hasHeightForWidth());
        label_4->setSizePolicy(sizePolicy);

        gridLayout->addWidget(label_4, 2, 0, 1, 1, Qt::AlignHCenter|Qt::AlignVCenter);

        downloadLocationBtn = new QPushButton(widget);
        downloadLocationBtn->setObjectName(QStringLiteral("downloadLocationBtn"));

        gridLayout->addWidget(downloadLocationBtn, 3, 0, 1, 1, Qt::AlignHCenter|Qt::AlignVCenter);

        port = new QSpinBox(widget);
        port->setObjectName(QStringLiteral("port"));
        port->setLayoutDirection(Qt::LeftToRight);
        port->setMinimum(1025);
        port->setMaximum(65535);
        port->setValue(2121);

        gridLayout->addWidget(port, 0, 4, 1, 1);

        label_2 = new QLabel(widget);
        label_2->setObjectName(QStringLiteral("label_2"));
        sizePolicy.setHeightForWidth(label_2->sizePolicy().hasHeightForWidth());
        label_2->setSizePolicy(sizePolicy);

        gridLayout->addWidget(label_2, 0, 3, 1, 1, Qt::AlignHCenter|Qt::AlignVCenter);

        label = new QLabel(widget);
        label->setObjectName(QStringLiteral("label"));
        sizePolicy.setHeightForWidth(label->sizePolicy().hasHeightForWidth());
        label->setSizePolicy(sizePolicy);

        gridLayout->addWidget(label, 0, 0, 1, 1, Qt::AlignHCenter|Qt::AlignVCenter);

        speedLimitSpin = new QDoubleSpinBox(widget);
        speedLimitSpin->setObjectName(QStringLiteral("speedLimitSpin"));

        gridLayout->addWidget(speedLimitSpin, 2, 4, 1, 1);

        speedLimitSlider = new QSlider(widget);
        speedLimitSlider->setObjectName(QStringLiteral("speedLimitSlider"));
        speedLimitSlider->setOrientation(Qt::Horizontal);

        gridLayout->addWidget(speedLimitSlider, 2, 1, 1, 3);

        label_5 = new QLabel(widget);
        label_5->setObjectName(QStringLiteral("label_5"));

        gridLayout->addWidget(label_5, 4, 0, 1, 1, Qt::AlignHCenter|Qt::AlignVCenter);

        exchangeURL = new QLineEdit(widget);
        exchangeURL->setObjectName(QStringLiteral("exchangeURL"));

        gridLayout->addWidget(exchangeURL, 4, 1, 1, 4);


        verticalLayout_2->addLayout(gridLayout);

        verticalSpacer_3 = new QSpacerItem(20, 40, QSizePolicy::Minimum, QSizePolicy::Expanding);

        verticalLayout_2->addItem(verticalSpacer_3);

        label_3 = new QLabel(widget);
        label_3->setObjectName(QStringLiteral("label_3"));
        QFont font;
        font.setItalic(true);
        label_3->setFont(font);

        verticalLayout_2->addWidget(label_3, 0, Qt::AlignHCenter);

        verticalSpacer_2 = new QSpacerItem(20, 40, QSizePolicy::Minimum, QSizePolicy::Expanding);

        verticalLayout_2->addItem(verticalSpacer_2);

        horizontalLayout = new QHBoxLayout();
        horizontalLayout->setSpacing(6);
        horizontalLayout->setObjectName(QStringLiteral("horizontalLayout"));
        horizontalSpacer = new QSpacerItem(40, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

        horizontalLayout->addItem(horizontalSpacer);

        toggleShareBtn = new QPushButton(widget);
        toggleShareBtn->setObjectName(QStringLiteral("toggleShareBtn"));

        horizontalLayout->addWidget(toggleShareBtn);

        horizontalSpacer_2 = new QSpacerItem(37, 17, QSizePolicy::Expanding, QSizePolicy::Minimum);

        horizontalLayout->addItem(horizontalSpacer_2);


        verticalLayout_2->addLayout(horizontalLayout);

        verticalSpacer = new QSpacerItem(20, 40, QSizePolicy::Minimum, QSizePolicy::Expanding);

        verticalLayout_2->addItem(verticalSpacer);

        downloadsTable->addTab(settingsTab, QString());
        usersListTab = new QWidget();
        usersListTab->setObjectName(QStringLiteral("usersListTab"));
        horizontalLayout_2 = new QHBoxLayout(usersListTab);
        horizontalLayout_2->setSpacing(6);
        horizontalLayout_2->setContentsMargins(11, 11, 11, 11);
        horizontalLayout_2->setObjectName(QStringLiteral("horizontalLayout_2"));
        usersTable = new QTableWidget(usersListTab);
        if (usersTable->columnCount() < 3)
            usersTable->setColumnCount(3);
        QTableWidgetItem *__qtablewidgetitem = new QTableWidgetItem();
        usersTable->setHorizontalHeaderItem(0, __qtablewidgetitem);
        QTableWidgetItem *__qtablewidgetitem1 = new QTableWidgetItem();
        usersTable->setHorizontalHeaderItem(1, __qtablewidgetitem1);
        QTableWidgetItem *__qtablewidgetitem2 = new QTableWidgetItem();
        usersTable->setHorizontalHeaderItem(2, __qtablewidgetitem2);
        usersTable->setObjectName(QStringLiteral("usersTable"));
        usersTable->setSortingEnabled(true);
        usersTable->setColumnCount(3);
        usersTable->horizontalHeader()->setStretchLastSection(true);

        horizontalLayout_2->addWidget(usersTable);

        downloadsTable->addTab(usersListTab, QString());
        browserTab = new QWidget();
        browserTab->setObjectName(QStringLiteral("browserTab"));
        verticalLayout = new QVBoxLayout(browserTab);
        verticalLayout->setSpacing(6);
        verticalLayout->setContentsMargins(11, 11, 11, 11);
        verticalLayout->setObjectName(QStringLiteral("verticalLayout"));
        horizontalLayout_4 = new QHBoxLayout();
        horizontalLayout_4->setSpacing(6);
        horizontalLayout_4->setObjectName(QStringLiteral("horizontalLayout_4"));
        browserPrevBtn = new QPushButton(browserTab);
        browserPrevBtn->setObjectName(QStringLiteral("browserPrevBtn"));

        horizontalLayout_4->addWidget(browserPrevBtn);

        browserNextBtn = new QPushButton(browserTab);
        browserNextBtn->setObjectName(QStringLiteral("browserNextBtn"));

        horizontalLayout_4->addWidget(browserNextBtn);

        browserInput = new QLineEdit(browserTab);
        browserInput->setObjectName(QStringLiteral("browserInput"));

        horizontalLayout_4->addWidget(browserInput);

        browserGoBtn = new QPushButton(browserTab);
        browserGoBtn->setObjectName(QStringLiteral("browserGoBtn"));

        horizontalLayout_4->addWidget(browserGoBtn);


        verticalLayout->addLayout(horizontalLayout_4);

        browserTable = new QTableWidget(browserTab);
        if (browserTable->columnCount() < 3)
            browserTable->setColumnCount(3);
        QTableWidgetItem *__qtablewidgetitem3 = new QTableWidgetItem();
        browserTable->setHorizontalHeaderItem(0, __qtablewidgetitem3);
        QTableWidgetItem *__qtablewidgetitem4 = new QTableWidgetItem();
        browserTable->setHorizontalHeaderItem(1, __qtablewidgetitem4);
        QTableWidgetItem *__qtablewidgetitem5 = new QTableWidgetItem();
        browserTable->setHorizontalHeaderItem(2, __qtablewidgetitem5);
        browserTable->setObjectName(QStringLiteral("browserTable"));
        browserTable->horizontalHeader()->setStretchLastSection(true);

        verticalLayout->addWidget(browserTable);

        downloadsTable->addTab(browserTab, QString());
        downloadsTab = new QWidget();
        downloadsTab->setObjectName(QStringLiteral("downloadsTab"));
        horizontalLayout_3 = new QHBoxLayout(downloadsTab);
        horizontalLayout_3->setSpacing(6);
        horizontalLayout_3->setContentsMargins(11, 11, 11, 11);
        horizontalLayout_3->setObjectName(QStringLiteral("horizontalLayout_3"));
        downloadsTable_2 = new QTableWidget(downloadsTab);
        if (downloadsTable_2->columnCount() < 4)
            downloadsTable_2->setColumnCount(4);
        QTableWidgetItem *__qtablewidgetitem6 = new QTableWidgetItem();
        downloadsTable_2->setHorizontalHeaderItem(0, __qtablewidgetitem6);
        QTableWidgetItem *__qtablewidgetitem7 = new QTableWidgetItem();
        downloadsTable_2->setHorizontalHeaderItem(1, __qtablewidgetitem7);
        QTableWidgetItem *__qtablewidgetitem8 = new QTableWidgetItem();
        downloadsTable_2->setHorizontalHeaderItem(2, __qtablewidgetitem8);
        QTableWidgetItem *__qtablewidgetitem9 = new QTableWidgetItem();
        downloadsTable_2->setHorizontalHeaderItem(3, __qtablewidgetitem9);
        downloadsTable_2->setObjectName(QStringLiteral("downloadsTable_2"));
        downloadsTable_2->horizontalHeader()->setStretchLastSection(true);

        horizontalLayout_3->addWidget(downloadsTable_2);

        downloadsTable->addTab(downloadsTab, QString());

        verticalLayout_4->addWidget(downloadsTable);


        retranslateUi(Dialog);

        downloadsTable->setCurrentIndex(0);


        QMetaObject::connectSlotsByName(Dialog);
    } // setupUi

    void retranslateUi(QDialog *Dialog)
    {
        Dialog->setWindowTitle(QApplication::translate("Dialog", "Dialog", 0));
        sharedLocationBtn->setText(QApplication::translate("Dialog", "Shared location", 0));
        label_4->setText(QApplication::translate("Dialog", "Speed Limits", 0));
        downloadLocationBtn->setText(QApplication::translate("Dialog", "Download location", 0));
        label_2->setText(QApplication::translate("Dialog", "Port", 0));
        label->setText(QApplication::translate("Dialog", "Public Name", 0));
        speedLimitSpin->setSuffix(QApplication::translate("Dialog", " Mbps", 0));
        label_5->setText(QApplication::translate("Dialog", "Exchange URL", 0));
        label_3->setText(QApplication::translate("Dialog", "Don't randomly hit your mouse. It hurts!", 0));
        toggleShareBtn->setText(QApplication::translate("Dialog", "Start Sharing", 0));
        downloadsTable->setTabText(downloadsTable->indexOf(settingsTab), QApplication::translate("Dialog", "Settings", 0));
        QTableWidgetItem *___qtablewidgetitem = usersTable->horizontalHeaderItem(0);
        ___qtablewidgetitem->setText(QApplication::translate("Dialog", "Go", 0));
        QTableWidgetItem *___qtablewidgetitem1 = usersTable->horizontalHeaderItem(1);
        ___qtablewidgetitem1->setText(QApplication::translate("Dialog", "Shared Size", 0));
        QTableWidgetItem *___qtablewidgetitem2 = usersTable->horizontalHeaderItem(2);
        ___qtablewidgetitem2->setText(QApplication::translate("Dialog", "Name", 0));
        downloadsTable->setTabText(downloadsTable->indexOf(usersListTab), QApplication::translate("Dialog", "Connected Users", 0));
        browserPrevBtn->setText(QApplication::translate("Dialog", "Back", 0));
        browserNextBtn->setText(QApplication::translate("Dialog", "Forth", 0));
        browserGoBtn->setText(QApplication::translate("Dialog", "Go", 0));
        QTableWidgetItem *___qtablewidgetitem3 = browserTable->horizontalHeaderItem(0);
        ___qtablewidgetitem3->setText(QApplication::translate("Dialog", "Go", 0));
        QTableWidgetItem *___qtablewidgetitem4 = browserTable->horizontalHeaderItem(1);
        ___qtablewidgetitem4->setText(QApplication::translate("Dialog", "Size", 0));
        QTableWidgetItem *___qtablewidgetitem5 = browserTable->horizontalHeaderItem(2);
        ___qtablewidgetitem5->setText(QApplication::translate("Dialog", "Name", 0));
        downloadsTable->setTabText(downloadsTable->indexOf(browserTab), QApplication::translate("Dialog", "Browser", 0));
        QTableWidgetItem *___qtablewidgetitem6 = downloadsTable_2->horizontalHeaderItem(0);
        ___qtablewidgetitem6->setText(QApplication::translate("Dialog", "cancel/open", 0));
        QTableWidgetItem *___qtablewidgetitem7 = downloadsTable_2->horizontalHeaderItem(1);
        ___qtablewidgetitem7->setText(QApplication::translate("Dialog", "Size", 0));
        QTableWidgetItem *___qtablewidgetitem8 = downloadsTable_2->horizontalHeaderItem(2);
        ___qtablewidgetitem8->setText(QApplication::translate("Dialog", "Name", 0));
        QTableWidgetItem *___qtablewidgetitem9 = downloadsTable_2->horizontalHeaderItem(3);
        ___qtablewidgetitem9->setText(QApplication::translate("Dialog", "Path", 0));
        downloadsTable->setTabText(downloadsTable->indexOf(downloadsTab), QApplication::translate("Dialog", "Downloads", 0));
    } // retranslateUi

};

namespace Ui {
    class Dialog: public Ui_Dialog {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_DIALOG_H
