adduser ldm
chmod +w /etc/sudoers
sed '$a ldm ALL=(ALL) NOPASSWD:ALL' /etc/sudoers
