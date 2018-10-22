#scripts for fetching multicast files.

wget https://raw.githubusercontent.com/UVA-High-Speed-Networks/Multicast/master/Steve/send_recv_test.h
wget https://raw.githubusercontent.com/UVA-High-Speed-Networks/Multicast/master/Steve/send_test.c
wget https://raw.githubusercontent.com/UVA-High-Speed-Networks/Multicast/master/Steve/recv_test.c
c99 -o send_test send_test.c
c99 -o recv_test recv_test.c
wget https://raw.githubusercontent.com/UVA-High-Speed-Networks/Multicast/master/Yuanlong/mcast_recv.c
wget https://raw.githubusercontent.com/UVA-High-Speed-Networks/Multicast/master/Yuanlong/yt_mcast_send.c
gcc -o mc_send yt_mcast_send.c
gcc -o mc_recv mcast_recv.c
