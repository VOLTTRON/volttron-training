sudo systemctl start postgresql
sudo su postgres -c "createuser -d -l -R -S -P django"
sudo su postgres -c "createdb -O django hackathon-docker"