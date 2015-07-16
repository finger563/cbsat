clc
close all

x=(0:5:180);
inst1=80*ones(37);inst1=inst1(1,:);inst1=inst1*60; % convert to kb/min
inst2=(0:5:180)*0;inst2(1:6:37)=150;inst2(2:6:37)=150;inst2=inst2*60; % same

% number of total kilobytes sent over link for each instrument
data1=cumtrapz(x,inst1);
% data1=cumtrapz(x,data1);
data2=cumtrapz(x,inst2);
% data2=cumtrapz(x,data2);
figure 
plot(x,data1);
hold
plot(x,data2);

% Note: These curve values were determined manually from the graphs of
% data1 and data 2
% figure
func1 = rtccurve([[0 0 4.5e4/5];[5 4.5e4 2.25e4/5]],[[0 0 0];[15 0 2.25e4/5];[20 2.25e4 4.5e4/5];[25 6.75e4 2.25e4/5]],10,6.75e4,30,1.575e5-6.75e4);
% rtcplot(func1,180);
% hold;
func2 = rtccurve([[0 0 2.4e4/5]]);
% rtcplot(func2,180);

%[p j d s] = rtcconvpjd(data1,90)

% p = period, j = jitter, d = minimum inter-arrival distance
% rtcpjd(p,j,d)

% B = bandwidth (fully available)
% rtcfs(B)

% This corresponds to Module 1 with 1A(pers) and 1B(lat/long)
[p, j, d, s] = rtcconvpjd([func2 func2], 30);
a11=rtcpjd(p,j,d);a11 = rtctimes(a11,s);
rtcplot(a11);
a12=rtcpjd(30,0,5);
e1 = 1; e2 = 1;
b11 = rtctdma(3,10,1);
b12 = rtctdma(7,10,1);
[a11_out, b12, del1, buf1] = rtcgpc(a11, b11, e1);
[a12_out, b13, del2, buf2] = rtcgpc(a12, b12, e2);
figure
subplot(2,1,1); rtcplot(a11,'b', a11_out, 'r', 180); title('a11 (blue); a11_{out} (red)');
subplot(2,1,2); rtcplot(a12,'b', a12_out, 'r', 180); title('a12 (blue); a12_{out} (red)');
figure
subplot(2,1,1); rtcplot(b11,'b', b12, 'r', 180); title('b11 (blue); b12 (red)');
subplot(2,1,2); rtcplot(b12,'b', b13, 'r', 180); title('b12 (blue); b13 (red)');
disp(['delay1 = ', num2str(del1), '; delay2 = ', num2str(del2)]);


% This corresponds to Module 2 with 2A(pers) and 2B(periodic)
a21=rtcpjd(5,0,1);
a22=rtcpjd(10,0,0);
e3 = 1; e4 = 1;
b21 = rtctdma(3,10,1);
b22 = rtctdma(7,10,1);
[a21_out, b22, del3, buf3] = rtcgpc(a21, b21, e3);
[a22_out, b23, del4, buf4] = rtcgpc(a22, b22, e4);
figure
subplot(2,1,1); rtcplot(a21,'b', a21_out, 'r', 180); title('a21 (blue); a21_{out} (red)');
subplot(2,1,2); rtcplot(a22,'b', a22_out, 'r', 180); title('a22 (blue); a22_{out} (red)');
figure
subplot(2,1,1); rtcplot(b21,'b', b22, 'r', 180); title('b21 (blue); b22 (red)');
subplot(2,1,2); rtcplot(b22,'b', b23, 'r', 180); title('b22 (blue); b23 (red)');
disp(['delay3 = ', num2str(del3), '; delay4 = ', num2str(del4)]);

% This corresponds to Module 3 with 3A(pers) and 3B(lat/long)
a31=rtcpjd(5,0,1);
a32=rtcpjd(20,15,10);
e5 = 2; e6 = 1;
b31=rtcfs(1);
[a31_out, b32, del5, buf5] = rtcgpc(a31, b31, e5);
[a32_out, b33, del6, buf6] = rtcgpc(a32, b32, e6);
figure
subplot(2,1,1); rtcplot(a31,'b', a31_out, 'r', 180); title('a31 (blue); a31_{out} (red)');
subplot(2,1,2); rtcplot(a32,'b', a32_out, 'r', 180); title('a32 (blue); a32_{out} (red)');
figure
subplot(2,1,1); rtcplot(b31,'b', b32, 'r', 180); title('b31 (blue); b32 (red)');
subplot(2,1,2); rtcplot(b32,'b', b33, 'r', 180); title('b32 (blue); b33 (red)');
disp(['delay5 = ', num2str(del5), '; delay6 = ', num2str(del6)]);


