
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Jenkins is checking out mcp-demo'
            }
        }

        stage('Verify Source') {
            steps {
                sh 'pwd'
                sh 'ls -la'
                sh 'cat requirements.txt'
            }
        }
    }

    post {
        success {
            echo 'Source checkout and verification succeeded!'
        }
        failure {
            echo 'Pipeline failed. Check the console output.'
        }
    }
}
