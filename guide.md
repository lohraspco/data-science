# Work with remote server 
I have a Linux server and I connect to it using VSCode "Remote - SSH" plugin. 
Refer to https://code.visualstudio.com/docs/remote/troubleshooting#_installing-a-supported-ssh-client
1- on the host server: sudo apt-get install openssh-server
2- on the client server install "Remote - SSH" VSCode plugin (refer to https://code.visualstudio.com/docs/remote/troubleshooting#_installing-a-supported-ssh-server)

# Clone this repo
- create SSH key
`ssh-keygen -t ed25519 -C "email@gmail.com" `
- add SSH pub to github SSH keys
cat /home/matt/.ssh/sshkey.pub
- clone git@github.com:lohraspco/data-science.git 

# Config database
- sudo snap install docker
- docker pull postgres
- start docker from image 
`docker run --name stock-postgres -e POSTGRES_PASSWORD=StrongPass123 -d postgres`
- `docker ps`
- Access the container's shell
`sudo docker exec -it stock-postgres bash`
- List available postgres users
`psql -U postgres -c "\du"`
- Connect to a database
`psql -U postgres`


# Run 
uvicorn frontend.app::app