    pipeline {
        agent any

        stages {
            stage('Checkout') {
                steps {
                    echo 'Checking out mcp-demo from GitHub'
                }
            }

            stage('Verify Source') {
                steps {
                    sh 'pwd'
                    sh 'ls -la'
                    sh 'cat requirements.txt'
                }
            }

            stage('Install Dependencies') {
                steps {
                    sh 'python3 -m venv .venv'
                    sh '.venv/bin/pip install -r requirements.txt'
                }
            }

            stage('Run Tests') {
                environment {
                    REDIS_HOST = 'mcp-demo-redis-1'
                    REDIS_PORT = '6379'
                    DB_NAME = 'jenkins_test.db'
                }
                steps {
                    sh '.venv/bin/python -m pytest -v'
                }
    }
            }
        }

        post {
            success {
                
            }
            failure {
                echo 'Pipeline failed. Check the console output.'
            }
        }
    }