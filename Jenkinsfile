pipeline {
    agent any
    stages {
        stage('Clone Repositories') {
            steps {
                dir('cu-tech/Development') {
                    checkout scm: [$class: 'GitSCM', userRemoteConfigs: [[url: 'https://daycdev@bitbucket.org/cushingsystemsinc/psims.git']], branches: [[name: '*/develop']]]
                }
                dir('cu-tech/dev-psims-anywhere') {
                    checkout scm: [$class: 'GitSCM', userRemoteConfigs: [[url: 'https://daycdev@bitbucket.org/cushingsystemsinc/psims-anywhere.git']], branches: [[name: '*/develop']]]
                    dir('PSIMSFrontEnd') {
                        checkout scm: [$class: 'GitSCM', userRemoteConfigs: [[url: 'https://daycdev@bitbucket.org/cushingsystemsinc/web-connect.git']], branches: [[name: '*/develop']]]
                    }
                    dir('PSIMSWebAPi') {
                        checkout scm: [$class: 'GitSCM', userRemoteConfigs: [[url: 'https://daycdev@bitbucket.org/cushingsystemsinc/web-api.git']], branches: [[name: '*/develop']]]
                    }
                    dir('PSIMSData') {
                        checkout scm: [$class: 'GitSCM', userRemoteConfigs: [[url: 'https://daycdev@bitbucket.org/cushingsystemsinc/psims-data.git']], branches: [[name: '*/develop']]]
                    }
                }
                dir('cu-tech/dev-agisent-common') {
                    checkout scm: [$class: 'GitSCM', userRemoteConfigs: [[url: 'https://daycdev@bitbucket.org/cushingsystemsinc/agisent-common.git']], branches: [[name: '*/main']]]
                }
                dir('cu-tech/dev-agisent-interoperability') {
                    checkout scm: [$class: 'GitSCM', userRemoteConfigs: [[url: 'https://daycdev@bitbucket.org/cushingsystemsinc/agisent-interoperability.git']], branches: [[name: '*/master']]]
                }
                dir('cu-tech/dev-documenter') {
                    checkout scm: [$class: 'GitSCM', userRemoteConfigs: [[url: 'https://daycdev@bitbucket.org/cushingsystemsinc/documenter.git']], branches: [[name: '*/main']]]
                }
                dir('cu-tech/dev-psims-evidence-label-printer') {
                    checkout scm: [$class: 'GitSCM', userRemoteConfigs: [[url: 'https://daycdev@bitbucket.org/cushingsystemsinc/psims-evidence-label-printer-service.git']], branches: [[name: '*/main']]]
                }
            }
        }
        stage('Build PSIMSGeneral') {
            steps {
                script{
                    build job: 'MultiProjectBuildClassic', wait: true
                }
            }
        }
        stage('Build PSIMSWeb and Others') {
            steps {
                script {
                    build job: 'MultiProjectBuildPSA', wait: true
            }
        }
        stage('Publish PSIMSAnywhere') {
            steps {
                script {
                    bat "xcopy /I /E /Y D:\\CU-TECH\\dev-psims-anywhere\\PSIMSWebApi\\Src\\WebApi D:\\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMSWebApi"
                }
                script {
                    bat "xcopy /I /E /Y D:\\CU-TECH\\dev-psims-anywhere\\PSIMSFrontEnd\\Src\\Web\\Mvc\\bin D:\\PSIMS\\Release\\PSIMSWebConnect"
                }
            }
        }
        stage('Merge Data') {
            steps {
                script {
                    bat "xcopy \\CU-TECH\\dev-psims-anywhere\\PSIMSWebApi\\Src\\WebApi\\bin\\Authentication\\*.* \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMSWebApi\\bin\\Authentication\\*.* /s /Q /Y"
                    bat "del /q \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMSWebConnect\\OSMPlot.html"
                    bat "copy \\CU-TECH\\dev-PSIMSMapserver\\apps\\OSMPlot.html \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMSWebConnect"
                    bat "del  /f/s/q \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMSWebConnect\\symbols\\*.*"
                    bat "xcopy \\CU-TECH\\dev-PSIMSMapserver\\apps\\Symbols\\*.* \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMSWebConnect\\Symbols\\*.* /s /Q /Y"
                    bat "del  /f/s/q \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMSWebApi\\symbols\\*.*"
                    bat "xcopy \\CU-TECH\\dev-PSIMSMapserver\\apps\\Symbols\\*.* \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMSWebApi\\Symbols\\*.* /s /Q /Y"
                    bat "copy Web.Backload.config \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMSWebConnect"
                    bat "copy Web.Backload.config \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMSWebConnect\\backload"
                    bat "copy \\CU-TECH\\dev-psims-anywhere\\PSIMSData\\AllRelease1Migration.sql \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\scripts"
                    bat "copy \\CU-TECH\\dev-psims-anywhere\\PSIMSData\\AllMigration.sql \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\scripts"
                    bat "if exist \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMSWebConnect\\web.config.dev del \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMSWebConnect\\web.config.dev"
                    bat "ren \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMSWebConnect\\web.config  web.config.dev"
                    bat "if exist \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMSWebApi\\web.config.dev del \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMSWebApi\\web.config.dev"
                    bat "ren \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMSWebApi\\web.config  web.config.dev"
                    bat "del /f/s/q  \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Common\\CustomForms\\*.*"
                    bat "del /f/s/q \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Common\\Html\\*.*"
                    bat "del /f/s/q \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Common\\Reports\\*.*"
                    bat "del /f/s/q \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Common\\Validation\\NIBRS\\XML\\*.*"
                    bat "xcopy \\CU-TECH\\Development\\CustomForms\\*.* \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Common\\CustomForms\\*.* /s /Q /Y"
                    bat "xcopy \\CU-TECH\\Development\\Html\\*.* \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Common\\Html\\*.* /s /Q /Y"
                    bat "del \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Common\\Html\\*.xml"
                    bat "del \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Common\\Html\\*.txt"
                    bat "xcopy \\CU-TECH\\Development\\Reports\\*.* \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Common\\Reports\\*.* /s /Q /Y"
                    bat "xcopy \\CU-TECH\\Development\\SQL\\*.* \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Scripts\\SQL\\*.* /s /Q /Y"
                    bat "xcopy \"\\CU-TECH\\Development\\Stored Procedures and Functions\\*.*\" \"\\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Scripts\\Stored Procedures and Functions\\*.*\" /s /Q /Y"
                    bat "xcopy \\CU-TECH\\Development\\Manuals\\*.* \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Manuals\\*.* /s /Q /Y"
                    bat "copy \\CU-TECH\\Development\\NIBRSBuildFed\\de.xml \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Common\\Validation\\NIBRS\\XML"
                    bat "copy \\CU-TECH\\Development\\NIBRSBuildFed\\err.xml \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Common\\Validation\\NIBRS\\XML"
                    bat "copy \\CU-TECH\\Development\\NIBRSFiles\\Illinois\\IL*.xml \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Common\\Validation\\NIBRS\\XML"
                    bat "copy \\CU-TECH\\Development\\NIBRSFiles\\Indiana\\IN*.xml \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Common\\Validation\\NIBRS\\XML"
                    bat "copy \\CU-TECH\\Development\\NIBRSFiles\\Idaho\\ID*.xml \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Common\\Validation\\NIBRS\\XML"
                    bat "copy \\CU-TECH\\Development\\NIBRSFiles\\Missouri\\MO.xml \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Common\\Validation\\NIBRS\\XML"
                    bat "copy \\CU-TECH\\Development\\NIBRSFiles\\Montana\\MT*.xml \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Common\\Validation\\NIBRS\\XML"
                    bat "copy \"\\CU-TECH\\Development\\NIBRSFiles\\New York\\NY*.xml\" \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Common\\Validation\\NYSIBR\\XML"
                    bat "copy \\CU-TECH\\Development\\NIBRSFiles\\Oklahoma\\OK*.xml \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Common\\Validation\\NIBRS\\XML"
                    bat "copy \\CU-TECH\\Development\\NIBRSFiles\\Texas\\TX*.xml \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Common\\Validation\\NIBRS\\XML"
                    bat "del /f/s/q \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMSG-Release\\*.*"
                    bat "del /f/s/q \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\WebServices\\*.*"
                    bat "del /f/s/q \"\\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMS Brother Label Printing Installers\\*.msi\""
                    bat "del /f/s/q \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMSBridgeSetupProject.msi"
                    bat "del /f/s/q \\PSIMS\\Release\\PSIMSStateILNIBRSReports.exe.config.dev"
                    bat "ren \\PSIMS\\Release\\PSIMSStateILNIBRSReports.exe.config PSIMSStateILNIBRSReports.exe.config.dev"
                    bat "copy \\PSIMS\\Release\\*.* \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMSG-Release\\*.*"
                    bat "del /f/s/q WebServices\\PSIMSNIBRSMonitor\\appSettings.dev"
                    bat "ren WebServices\\PSIMSNIBRSMonitor\\appSettings.json appSettings.json.dev"
                    bat "xcopy WebServices \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\WebServices\\*.* /s /Q /Y"
                    bat "copy PSIMSBridgeSetupProject.msi \\CU-TECH\\dev-PSIMSAnyWhere-Publish"
                    bat "copy PSIMSBrotherLabelPrinterServiceSetup.msi \"\\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PSIMS Brother Label Printing Installers\\*.*\""
                    bat "del /f/s/q \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\Setup*.bat"
                    bat "copy Setup*.bat \\CU-TECH\\dev-PSIMSAnyWhere-Publish\*.*"
                    bat "copy NEWInstallCommands.txt \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\*.*"
                    bat "del /f/s/q \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\PS-RunScriptPermission.txt"
                    bat "copy PS-RunScriptPermission.txt \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\*.*"
                    bat "del /f/s/q \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\DBCompressedBackupsOnForAll.BAT"
                    bat "copy DBCompressedBackupsOnForAll.BAT \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\*.*"
                    bat "del /f/s/q \\CU-TECH\\dev-PSIMSAnyWhere-Publish\\NEWInstallCommands.txt"
                }
            }
        }
        stage('Zip Data') {
            steps {
                script {
                    // Generate a date string in the format YYYYMMDD
                    def date = new Date()
                    def formattedDate = date.format('yyyyMMdd')

                    // Create the zip file name
                    def zipFileName = "PSIMSReleaseAll-${formattedDate}.zip"

                    // Use the zip file name in the 7z command
                    bat "\"C:\\Program Files\\7-Zip\\7z.exe\" a -tzip ${zipFileName} D:\\CU-TECH\\dev-PSIMSAnyWhere-Publish\\*"

                    bat "move ${zipFileName} D:\\PSIMS\\ReleaseZips\\"
                }
            }
        }
        stage('Update HTML and Text Release Notes') {
            steps {
                // This PowerShell script should be present at the path below on your build agent.
                powershell 'D:/CU-TECH/dev-psims-anywhere/scripts/update_release_notes.ps1'
            }
        }
        stage('Jira Release Update') {
            steps {
                // Placeholder for future Jira integration script
                echo "Jira release automation goes here!"
            }
        }
        stage('Upload to SFTP') {
            steps {
                // Script to merge, zip, and upload files
            }
        }
    }
}
