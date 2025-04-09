pipeline{
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = 'ace-wording-455116-q0'
        GCLOUD_PATH = "var/jenkins_home/google-cloud-sdk/bin"
        KUBECTL_AUTH_PLUGIN = "/usr/lib/google-cloud-sdk/bin"
    }

    stages{

        stage("Cloning from github...."){
            steps{
                script{
                    echo 'Cloning from github....'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/SagarAgg31/MLOPS-COURSE-PROJECT-2.git']])
                }
            }
        }

        stage("Making a virtual environment...."){
            steps{
                script{
                    echo '"Making a virtual environment...."'
                    sh '''
                        python -m venv ${VENV_DIR}
                        . ${VENV_DIR}/bin/activate
                        pip install --upgrade pip
                        pip install -e .
                        pip install dvc
                        '''
                }
            }
        }

        stage("DVC Pull"){
            steps{
                script{
                    withCredentials([file(credentialsId:'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]){
                        script{
                            echo 'DVC Pull.....'
                            sh '''
                                . ${VENV_DIR}/bin/activate
                                dvc pull
                                '''
                        }
                    }
                }
            }
        }

      stage("Build and push image to GCR"){
            steps{
                script{
                    withCredentials([file(credentialsId:'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]){
                        script{
                            echo 'Build and push image to GCR.....'
                            sh '''
                                export PATH=$PATH:${GCLOUD_PATH}
                                gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                                gcloud config set project ${GCP_PROJECT}
                                gcloud auth configure-docker --quiet
                                docker build -t gcr.io/${GCP_PROJECT}/mlops-project:latest .
                                docker push gcr.io/${GCP_PROJECT}/mlops-project:latest 
                                '''
                                }
                            }
                        }
                    }
                }   
        stage("Deploying to Kubernetes..."){
                    steps{
                        script{
                            withCredentials([file(credentialsId:'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]){
                                script{
                                    echo 'Deploying to Kubernetes....'
                                    sh '''
                                        export PATH=$PATH:${GCLOUD_PATH}:${KUBECTL_AUTH_PLUGIN}
                                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                                        gcloud config set project ${GCP_PROJECT}
                                        gcloud container clusters get-credentials ml-app-cluster --region us-central1
                                        kubectlapply -f deployement.yaml
                                        
                                        '''
                                        }
                                    }
                                }
                            }
                        }

    }
}
