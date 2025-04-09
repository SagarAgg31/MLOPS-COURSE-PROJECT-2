pipeline{
    agent any

    stages{
        stage("Cloning from github...."){
            steps{
                script{
                    echo 'Cloning from github....'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/SagarAgg31/MLOPS-COURSE-PROJECT-2.git']])
                }
            }
        }
    }
}