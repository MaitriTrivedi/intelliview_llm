pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE_NAME = 'interview-llm'
        DOCKER_HUB_USERNAME = 'prabal2011singh'
        GITHUB_REPO_URL = 'https://github.com/MaitriTrivedi/intelliview_llm.git'
    }
    
    stages {
        stage('Checkout from GitHub') {
            steps {
                script {
                    // Clone the code from the GitHub repository
                    git branch: 'main', url: "${GITHUB_REPO_URL}"
                }
            }
        }
        
        stage('Check Existing Image') {
            steps {
                script {
                    // Check if the image already exists locally
                    def imageExists = sh(script: "docker images -q ${DOCKER_IMAGE_NAME}", returnStdout: true).trim()
                    if (imageExists) {
                        echo "Docker image already exists. Skipping build."
                        env.SKIP_BUILD = 'true'
                    } else {
                        echo "Building new Docker image..."
                        env.SKIP_BUILD = 'false'
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            when {
                expression { return env.SKIP_BUILD == 'false' }
            }
            steps {
                script {
                    docker.build("${DOCKER_IMAGE_NAME}", '.')
                }
            }
        }
        
        // stage('Test Docker Image') {
        //     when {
        //         expression { return env.SKIP_BUILD == 'false' }
        //     }
        //     steps {
        //         script {
        //             // Test 1: Check if the image can start correctly
        //             sh """
        //                 docker run --name test-container -d --rm ${DOCKER_IMAGE_NAME} sleep 10
        //                 if [ \$? -ne 0 ]; then
        //                     echo "Failed to start container"
        //                     exit 1
        //                 fi
        //                 docker stop test-container || true
        //             """
                    
        //             // Test 2: Check if Ollama is included in the image
        //             sh """
        //                 docker run --rm ${DOCKER_IMAGE_NAME} which ollama
        //                 if [ \$? -ne 0 ]; then
        //                     echo "Ollama binary not found in image"
        //                     exit 1
        //                 fi
        //             """
                    
        //             echo "All tests passed successfully"
        //         }
        //     }
        // }
        
        stage('Push Docker Image') {
            when {
                expression { return env.SKIP_BUILD == 'false' }
            }
            steps {
                script {
                    docker.withRegistry('', 'DockerHubCredentials') {
                        sh "docker tag ${DOCKER_IMAGE_NAME} ${DOCKER_HUB_USERNAME}/${DOCKER_IMAGE_NAME}:latest"
                        sh "docker push ${DOCKER_HUB_USERNAME}/${DOCKER_IMAGE_NAME}:latest"
                    }
                }
            }
        }
        
        stage('Run Ansible Playbook') {
            steps {
                script {
                    withEnv(["ANSIBLE_HOST_KEY_CHECKING=False"]) {
                        ansiblePlaybook(
                            playbook: 'deploy-playbook.yml',
                            inventory: 'inventory.ini',
                            extras: "-e docker_image=${DOCKER_HUB_USERNAME}/${DOCKER_IMAGE_NAME}:latest -e skip_docker_pull=${env.SKIP_BUILD}"
                        )
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo "Deployment completed successfully!"
        }
        failure {
            echo "Deployment failed. Please check the logs for details."
        }
        always {
            cleanWs()
        }
    }
}