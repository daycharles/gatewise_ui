pipeline {
    agent any

    /* ────────────────────────────────────────────────
       PARAMETERS
       ──────────────────────────────────────────────── */
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

    /* ────────────────────────────────────────────────
       ENVIRONMENT VARIABLES
       ──────────────────────────────────────────────── */
    environment {
        BUILD_OWNER   = "Charles"
        FEATURE_FLAG  = "ENABLED"
        REPO_URL      = "https://github.com/daycharles/gatewise_ui.git"
    }

    /* ────────────────────────────────────────────────
       PIPELINE OPTIONS
       ──────────────────────────────────────────────── */
    options {
        timestamps()
        ansiColor('xterm')
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    /* ────────────────────────────────────────────────
       STAGES
       ──────────────────────────────────────────────── */
    stages {

        stage('📦 Checkout Repository') {
            steps {
                echo "\u001B[36mChecking out repository: ${env.REPO_URL}\u001B[0m"
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/master']],
                    userRemoteConfigs: [[url: env.REPO_URL]]
                ])
            }
        }

        stage('🚀 Initialize') {
            steps {
                echo "\u001B[32mInitializing pipeline...\u001B[0m"
                echo "Build Owner: ${env.BUILD_OWNER}"
                echo "Feature Flag: ${env.FEATURE_FLAG}"
                echo "Custom Message: ${params.CUSTOM_MESSAGE}"
            }
        }

        stage('🔍 Conditional Logic Demo') {
            steps {
                script {
                    if (params.DEPLOY_ENV == 'prod') {
                        echo "\u001B[33mProduction selected — performing extra validation...\u001B[0m"
                    } else {
                        echo "Environment is ${params.DEPLOY_ENV} — normal flow."
                    }
                }
            }
        }

        stage('⚡ Parallel Demo') {
            parallel {
                Stage_A: {
                    echo "\u001B[35mRunning Stage A in parallel...\u001B[0m"
                }
                Stage_B: {
                    echo "\u001B[36mRunning Stage B in parallel...\u001B[0m"
                }
                Stage_C: {
                    echo "\u001B[34mRunning Stage C in parallel...\u001B[0m"
                }
            }
        }

        stage('🧪 Extended Tests (Conditional)') {
            when {
                expression { return params.RUN_EXTENDED_TESTS }
            }
            steps {
                echo "\u001B[32mRunning extended test suite...\u001B[0m"
            }
        }

        stage('📜 Scripted Block Example') {
            steps {
                script {
                    def items = ['alpha', 'beta', 'gamma']
                    echo "\u001B[36mIterating through items...\u001B[0m"
                    items.each { item ->
                        echo "Processing item: ${item}"
                    }
                }
            }
        }

        stage('🚚 Deploy Logic Demo') {
            steps {
                echo "\u001B[33mPretending to deploy to: ${params.DEPLOY_ENV}\u001B[0m"
            }
        }
    }

    /* ────────────────────────────────────────────────
       POST ACTIONS
       ──────────────────────────────────────────────── */
    post {
        always {
            echo "\u001B[90mPipeline finished (always runs).\u001B[0m"
        }
        success {
            echo "\u001B[32mPipeline succeeded!\u001B[0m"
        }
        failure {
            echo "\u001B[31mPipeline failed!\u001B[0m"
        }
        unstable {
            echo "\u001B[33mPipeline marked unstable.\u001B[0m"
        }
        cleanup {
            echo "\u001B[90mPerforming cleanup tasks...\u001B[0m"
        }
    }
}
