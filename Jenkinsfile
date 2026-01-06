pipeline {
    agent any

    parameters {
        booleanParam(name: 'RUN_EXTENDED_TESTS', defaultValue: false, description: 'Run extended test suite')
        choice(name: 'DEPLOY_ENV', choices: ['dev', 'qa', 'prod'], description: 'Select deployment environment')
        string(name: 'CUSTOM_MESSAGE', defaultValue: 'Hello from Jenkins!', description: 'Custom echo message')
    }

    environment {
        BUILD_OWNER  = "Charles"
        FEATURE_FLAG = "ENABLED"
        REPO_URL     = "https://github.com/daycharles/gatewise_ui.git"
        SAMPLE_TOKEN = credentials('sample-token-id')   // safe: only echoes masked
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 20, unit: 'MINUTES')
        retry(1)
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Checking out repository: ${env.REPO_URL}"
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/master']],
                    userRemoteConfigs: [[url: env.REPO_URL]]
                ])
            }
        }

        stage('Environment Info') {
            steps {
                echo "Build Owner: ${env.BUILD_OWNER}"
                echo "Feature Flag: ${env.FEATURE_FLAG}"
                echo "Custom Message: ${params.CUSTOM_MESSAGE}"
                echo "Masked Credential Value: ${env.SAMPLE_TOKEN}"
            }
        }

        stage('Matrix Demo') {
            matrix {
                axes {
                    axis {
                        name 'OS'
                        values 'windows', 'linux'
                    }
                    axis {
                        name 'BROWSER'
                        values 'chrome', 'firefox'
                    }
                }
                stages {
                    stage('Run Matrix Job') {
                        steps {
                            echo "Running on OS=${OS}, Browser=${BROWSER}"
                        }
                    }
                }
            }
        }

        stage('Retry Logic Demo') {
            steps {
                script {
                    retry(3) {
                        echo "Attempting operation (this is a demo, so it always succeeds)..."
                    }
                }
            }
        }

        stage('Conditional Extended Tests') {
            when {
                expression { return params.RUN_EXTENDED_TESTS }
            }
            steps {
                echo "Running extended test suite..."
            }
        }

        stage('Scripted Logic Demo') {
            steps {
                script {
                    def items = ['alpha', 'beta', 'gamma', 'delta']
                    echo "Iterating through items..."
                    items.eachWithIndex { item, idx ->
                        echo "Item ${idx + 1}: ${item}"
                    }

                    def randomValue = new Random().nextInt(100)
                    echo "Generated random value: ${randomValue}"
                }
            }
        }

        stage('Archive Artifacts Demo') {
            steps {
                echo "Pretending to generate artifacts..."
                writeFile file: 'output.txt', text: 'Sample output content'
                archiveArtifacts artifacts: 'output.txt', fingerprint: true
            }
        }

        stage('Deploy Logic Demo') {
            steps {
                echo "Pretending to deploy to: ${params.DEPLOY_ENV}"
            }
        }
    }

    post {
        always {
            echo "Pipeline finished (always runs)."
            cleanWs()
        }
        success {
            echo "Pipeline succeeded!"
        }
        failure {
            echo "Pipeline failed!"
        }
        unstable {
            echo "Pipeline marked unstable."
        }
        cleanup {
            echo "Performing cleanup tasks..."
        }
    }
}
