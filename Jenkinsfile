pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = 'ace-wording-455116-q0'
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
        KUBECTL_AUTH_PLUGIN = "/usr/lib/google-cloud-sdk/bin"
        IMAGE_NAME = "gcr.io/${GCP_PROJECT}/mlops-project:latest"
    }

    stages {

        stage("Cloning from GitHub") {
            steps {
                echo 'Cloning from GitHub...'
                checkout scmGit(
                    branches: [[name: '*/main']],
                    extensions: [],
                    userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/SagarAgg31/MLOPS-COURSE-PROJECT-2.git']]
                )
            }
        }

        stage("Set up virtual environment") {
            steps {
                echo 'Setting up virtual environment...'
                sh """
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    pip install dvc
                """
            }
        }

        stage("DVC Pull") {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    echo 'Running DVC Pull...'
                    sh """
                        . ${VENV_DIR}/bin/activate
                        export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}
                        dvc pull
                    """
                }
            }
        }

        stage("Build and Push Docker Image to GCR") {
            steps {
                withCredentials([
                    file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS'),
                    string(credentialsId: 'COMET_API_KEY', variable: 'COMET_API_KEY')
                ]) {
                    sh """
                        echo "Authenticating with GCP..."
                        export PATH=$PATH:${GCLOUD_PATH}
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud auth configure-docker --quiet

                        echo "Building Docker image..."                    
                        docker build --build-arg COMET_API_KEY=${COMET_API_KEY} -t ${IMAGE_NAME} .

                        echo "Pushing Docker image..."
                        docker push ${IMAGE_NAME}
                    """
                }
            }
        }

        stage("Deploying to Kubernetes...") {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    echo 'Deploying to Kubernetes...'
                    sh """
                        export PATH=$PATH:${GCLOUD_PATH}:${KUBECTL_AUTH_PLUGIN}
                        export HOME=/var/jenkins_home
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud container clusters get-credentials ml-app-cluster --region us-central1

                        echo "Current K8s context:"
                        kubectl config current-context

                        kubectl apply -f deployment.yaml
                    """
                }
            }
        }
    }
}
