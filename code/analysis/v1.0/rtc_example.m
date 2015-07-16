function rtc_example()
    clc 
    close all
    
    time_length=60; % Number of seconds to plot the curves for.
    
    %  Make a constant data stream (as defined in the JPL document)
    [conU, conL] = cmakeUL(8);
    %  Make a periodic data stream for the CFS data
    [cfsU, cfsL] = pmakeUL(1,.1,10);
    %  Make a periodic data stream for an instrument (as defined in the JPL
    %  document)
    [pU, pL] = pmakeUL(30*60,5/30,15);

    % This corresponds to the configuration found in RTC_example.pdf
    CFS1=[cfsL,cfsU];
    Periodic=[pL,pU];
    CFS2=[cfsL,cfsU];
    Constant=[conL,conU];
    %  The e's are the processor demands and are effectively (?) useless
    %  here
    e1 = 1; e2 = 1; e3 = 1; e4 = 1; e5 = 1;
    %  Still have not verified that they are part of the same TDMA schedule
    b11 = rtctdma(.3,1,20,'bus1');
    b12 = rtctdma(.3,1,20,'bus1');
    b13 = rtctdma(.3,1,20,'bus1');
    b21 = rtcfs(10);
    [CFS1_out, b11_out, del1, buf1] = rtcgpc(CFS1, b11, e1);
    [CFS2_out, b12_out, del2, buf2] = rtcgpc(CFS2, b12, e2);
    [Constant_out, b13_out, del3, buf3] = rtcgpc(Constant, b13, e3);
    b14 = rtcplus(b11_out,b12_out);
    b14 = rtcplus(b14,b13_out);
    [Periodic_out, b14_out, del4, buf4] = rtcgpc(Periodic, b14, e4);
    Ground = rtcplus(Periodic_out,Constant_out);
    
%     figure;rtcplot(Periodic_out,'r',Constant_out,'b',time_length); title('Periodic_{out} (red); Constant_{out} (blue)');
%     figure;rtcplot(Ground(1),'r',Ground(2),'b',time_length); title('Ground Lower (red); Ground Upper (blue)');
    
    [Ground_out, b21_out, del5, buf5] = rtcgpc(Ground,b21,e5);

    figure; rtcplot(CFS1,'b', CFS1_out, 'r', time_length); title('CFS2 (blue); CFS2_{out} (red)');
    figure; rtcplot(CFS2,'b', CFS2_out, 'r', time_length); title('CFS2 (blue); CFS2_{out} (red)');
    figure; rtcplot(Constant,'b', Constant_out, 'r', time_length); title('Constant (blue); Constant_{out} (red)');
    figure; rtcplot(Periodic,'b', Periodic_out, 'r', time_length); title('Periodic (blue); Periodic_{out} (red)');
    figure; rtcplot(Ground,'b', Ground_out, 'r', time_length); title('Ground (blue); Ground_{out} (red)');
    
    figure; rtcplot(b11,'b', b11_out, 'r', time_length); title('b11 (blue); b11_{out} (red)');
    figure; rtcplot(b12,'b', b12_out, 'r', time_length); title('b12 (blue); b12_{out} (red)');
    figure; rtcplot(b13,'b', b13_out, 'r', time_length); title('b13 (blue); b13_{out} (red)');
    figure; rtcplot(b14,'b', b14_out, 'r', time_length); title('b14 (blue); b14_{out} (red)');
    figure; rtcplot(b21,'b', b21_out, 'r', time_length); title('b21 (blue); b21_{out} (red)');

    disp(['delay1 = ', num2str(del1), '; delay2 = ', num2str(del2) '; delay3 = ', num2str(del3),'; delay4 = ', num2str(del4)]);
end

function [x, y] = sqperiod(timeslice,len,period,duty,rate)
    x(1)=0;
    y(1)=rate;
    i=2;   
    time = timeslice;
    while time<len
        if mod(time,period) >= 0 && mod(time,period) < (duty*period)
            if y(i-1) ~= rate
                x(i) = time;
                y(i) = 0;
                i = i+1;
                x(i) = time;
                y(i) = rate;
                i = i+1;
            end
        else
            if y(i-1) ~= 0
                x(i) = time;
                y(i) = rate;
                i = i+1;
                x(i) = time;
                y(i) = 0;
                i = i+1;
            end
        end
        time = time + timeslice;
    end
    if x(end)<len
        x(end+1) = len;
        y(end+1) = y(end);
    end
end

function [dmin, dmax] = minmax(xdata,data)
    dmax=zeros(1, length(data));
    dmin=zeros(1, length(data));
    for i = 1:length(data)
        dmin(i)=data(i);
        dmax(i)=data(i);
        for j = 1:length(data)-i
            if (data(j+i)-data(j)) > dmax(i) && (xdata(j+i)-xdata(j))>0
                dmax(i) = data(j+i) - data(j);
            end
            if (data(j+i)-data(j)) < dmin(i) && (xdata(j+i)-xdata(j))>0
                dmin(i) = data(j+i) - data(j);
            end
        end
    end
end

function [U, L] = upperlower(xdata,dmax,dmin)
    slope=-1;
    L=[];
    for i = 2:length(dmin)
        if (xdata(i)-xdata(i-1))==0
            slope = -1;
        elseif (dmin(i)-dmin(i-1))/(xdata(i)-xdata(i-1)) ~= slope
            slope = (dmin(i)-dmin(i-1))/(xdata(i)-xdata(i-1));
            x=xdata(i-1);
            y=dmin(i-1);
            L = [L;[x y slope]];
        end
    end
    if isempty(L)
        L=[xdata(1) dmin(1) 0];
    end
    slope=-1;
    U=[];
    for i = 2:length(dmax)
        if (xdata(i)-xdata(i-1))==0
            slope = -1;
        elseif (dmax(i)-dmax(i-1))/(xdata(i)-xdata(i-1)) ~= slope
            slope = (dmax(i)-dmax(i-1))/(xdata(i)-xdata(i-1));
            x=xdata(i-1);
            y=dmax(i-1);
            U = [U;[x y slope]];
        end
    end
    if isempty(U)
        U=[xdata(1) dmax(1) 0];
    end
end

% makes upper and lower curves for periodic square wave with period,duty
% cycle, and bitrate
function [U, L] = pmakeUL(period,duty,rate)
    bits_per_period = rate*duty*period;
    U = rtccurve([[0 0 rate];[2*duty*period 2*bits_per_period 0]],[[0 0 rate];[duty*period bits_per_period 0]],period+duty*period,2*bits_per_period,period,bits_per_period);
    L = rtccurve([[0 0 0]],[[0 0 rate];[duty*period bits_per_period 0]],2*(period-duty*period),0,period);
end

% makes upper and lower curves for constant bit rate
function [U, L] = cmakeUL(rate)
    U = rtccurve([[0 0 rate]]);
    L = rtccurve([[0 0 rate]]);
end