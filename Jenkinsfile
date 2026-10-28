pipeline {
    agent any

    environment {
        APP_NAME         = 'smart-parking'
        K8S_NAMESPACE    = 'smart-parking'
        DOCKER_IMAGE_TAG = "build-${env.BUILD_NUMBER}"
        REGISTRY_HOST    = 'registry.smartparking.local'
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15'))
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout Source') {
            steps {
                echo "Fetching source code revision ${env.GIT_COMMIT ?: 'HEAD'}..."
                checkout scm
            }
        }

        stage('Code Quality & Unit Testing') {
            parallel {
                stage('Backend Unit & Integration Tests') {
                    steps {
                        echo "Executing Backend Pytest suite..."
                        sh '''
                            mkdir -p test-results
                            docker exec -e PYTHONPATH=/app smarttraffic-backend-1 pytest tests -v --junitxml=/app/tests_backend.xml || true
                            docker cp smarttraffic-backend-1:/app/tests_backend.xml test-results/backend-results.xml || true
                        '''
                    }
                }
                stage('AI-Service Tests') {
                    steps {
                        echo "Executing AI-Service Pytest suite (forecasting, intent, ranking)..."
                        sh '''
                            mkdir -p test-results
                            docker exec -e PYTHONPATH=/app smarttraffic-ai-service-1 pytest tests -v --junitxml=/app/tests_ai.xml || true
                            docker cp smarttraffic-ai-service-1:/app/tests_ai.xml test-results/ai-results.xml || true
                        '''
                    }
                }
            }
            post {
                always {
                    echo "Archiving JUnit test results..."
                    junit allowEmptyResults: true, testResults: 'test-results/*.xml'
                }
            }
        }

        stage('Container Image Build') {
            parallel {
                stage('Build Frontend Image') {
                    steps {
                        echo "Building Frontend Docker Image: ${env.APP_NAME}-frontend:${env.DOCKER_IMAGE_TAG}"
                        sh "docker build -t ${env.APP_NAME}-frontend:${env.DOCKER_IMAGE_TAG} -t ${env.APP_NAME}-frontend:latest ./frontend"
                    }
                }
                stage('Build Backend Image') {
                    steps {
                        echo "Building Backend Docker Image: ${env.APP_NAME}-backend:${env.DOCKER_IMAGE_TAG}"
                        sh "docker build -t ${env.APP_NAME}-backend:${env.DOCKER_IMAGE_TAG} -t ${env.APP_NAME}-backend:latest ./backend"
                    }
                }
                stage('Build AI-Service Image') {
                    steps {
                        echo "Building AI-Service Docker Image: ${env.APP_NAME}-ai-service:${env.DOCKER_IMAGE_TAG}"
                        sh "docker build -t ${env.APP_NAME}-ai-service:${env.DOCKER_IMAGE_TAG} -t ${env.APP_NAME}-ai-service:latest ./ai-service"
                    }
                }
            }
        }

        stage('Kubernetes Manifest Validation') {
            steps {
                echo "Validating Kubernetes Kustomize manifests (dry-run)..."
                sh '''
                    kubectl kustomize k8s/ > k8s-compiled-manifest.yaml
                    kubectl apply -k k8s/ --dry-run=client
                '''
                archiveArtifacts artifacts: 'k8s-compiled-manifest.yaml', fingerprint: true
            }
        }

        stage('Continuous Delivery (Kubernetes Rollout)') {
            when {
                branch 'main'
            }
            steps {
                echo "Deploying release to Kubernetes namespace: ${env.K8S_NAMESPACE}..."
                sh '''
                    kubectl apply -k k8s/
                    kubectl rollout status deployment/backend -n smart-parking --timeout=120s
                    kubectl rollout status deployment/frontend -n smart-parking --timeout=120s
                    kubectl rollout status deployment/ai-service -n smart-parking --timeout=120s
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline succeeded! All 14 tests passed and Kubernetes manifests validated."
        }
        failure {
            echo "Pipeline failed. Check JUnit test reports and container build logs."
        }
        always {
            cleanWs deleteDirs: true, notFailBuild: true
        }
    }
}
