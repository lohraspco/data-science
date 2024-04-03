# Work with remote server 
I have a Linux server and I connect to it using VSCode "Remote - SSH" plugin. 
Refer to https://code.visualstudio.com/docs/remote/troubleshooting#_installing-a-supported-ssh-client
1- on the host server: sudo apt-get install openssh-server
2- on the client server install "Remote - SSH" VSCode plugin (refer to https://code.visualstudio.com/docs/remote/troubleshooting#_installing-a-supported-ssh-server)

For ssh remote in vscode here is the content of config file

Host 192.168.0.208
  HostName 192.168.0.208
  IdentityFile C:/Users/CXJ2872/.ssh/id_rsa_localn
  User matt
  Port 22
  RemoteCommand cd /home/matt/lohrasp/data-science/ && bash -l



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
`docker run -d -p 5433:5432 --name stock-postgres -e POSTGRES_PASSWORD=StrongPass123 postgres`
- `docker ps`
- execute in docker shell
`docker exec -it stock-postgres bash -c "psql -h localhost -p 5432 -U postgres -c \"\\l \""`
- Access the container's shell
`sudo docker exec -it stock-postgres bash`
- List available postgres users
`psql -U postgres -c "\du"`
- login as postgres `su postgres`
- Connect to a database
`psql -U postgres`
psql -h localhost -U postgres -p 5432 -d postgres

## in the case needed pgadmin
`sudo docker run -p 80:80 -e 'PGADMIN_DEFAULT_EMAIL=lohraspco@gmail.com' -e 'PGADMIN_DEFAULT_PASSWORD=StrongPass123' -d dpage/pgadmin4`

# after the code is ready
## Run 
uvicorn frontend.app:app




Configure nginx to make the site live
###
sudo nano /etc/nginx/sites-available/lohrasp.com
server {
    listen 80;
    server_name www.lohrasp.com lohrasp.com;

    location / {
        proxy_pass http://127.0.0.1:8000; # should match with the fastapi port
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
###
sudo systemctl restart nginx


configure the modem for port forwarding
configure the domain DNS record to point to the ip of the host server. 
udo ln -s /etc/nginx/sites-available/lohrasp.com.conf /etc/nginx/sites-enabled/lohrasp.com.conf

https://dylancastillo.co/fastapi-nginx-gunicorn/
sudo adduser fastapiuser
b..d832
sudo gpasswd -a fastapiuser sudo


sudo certbot --nginx -d lohrasp.com -d www.lohrasp.com

https://portal.databasemart.com/kb/a2134/how-to-install-nginx-with-https-on-ubuntu.aspx

https://www.youtube.com/watch?v=qlcVx-k-02E



https://www.ssls.com/knowledgebase/how-to-install-an-ssl-certificate-on-a-nginx-server/


