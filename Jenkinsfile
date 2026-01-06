pipeline {
    agent any

    parameters {
        booleanParam(
            name: 'RUN_EXTENDED_TESTS',
            defaultValue: false,
            description: 'Run extended test suite'
        )
        choice(
            name: 'DEPLOY_ENV',
            choices: ['dev', 'qa', 'prod'],
            description: 'Select deployment environment'
        )
        string(
            name: 'CUSTOM_MESSAGE',
            defaultValue: 'Hello from Jenkins!',
            description: 'Custom echo message'
        )
    }

    environment {
        BUILD_OWNER  = "Charles"
        FEATURE_FLAG = "ENABLED"
        REPO_URL     = "https://github.com/daycharles/gatewise_ui.git"
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '20'))
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

        stage('Initialize') {
            steps {
                echo "Initializing pipeline..."
                echo "Build Owner: ${env.BUILD_OWNER}"
                echo "Feature Flag: ${env.FEATURE_FLAG}"
                echo "Custom Message: ${params.CUSTOM_MESSAGE}"
            }
        }

        stage('Conditional Logic Demo') {
            steps {
                script {
                    if (params.DEPLOY_ENV == 'prod') {
                        echo "Production selected — performing extra validation..."
                    } else {
                        echo "Environment is ${params.DEPLOY_ENV} — normal flow."
                    }
                }
            }
        }

        stage('Parallel Demo') {
            parallel {
                stage('Stage A') {
                    steps {
                        echo "Running Stage A in parallel..."
                    }
                }
                stage('Stage B') {
                    steps {
                        echo "Running Stage B in parallel..."
                    }
                }
                stage('Stage C') {
                    steps {
                        echo "Running Stage C in parallel..."
                    }
                }
            }
        }

        stage('Extended Tests (Conditional)') {
            when {
                expression { return params.RUN_EXTENDED_TESTS }
            }
            steps {
                echo "Running extended test suite..."
            }
        }

        stage('Scripted Block Example') {
            steps {
                script {
                    def items = ['alpha', 'beta', 'gamma']
                    echo "Iterating through items..."
                    items.each { item ->
                        echo "Processing item: ${item}"
                    }
                }
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
