function fvw_manipulator()

global V_TIMING;
V_TIMING = zeros(0,100);
cd('C:\Jouni\flyvirtualworld');
delete(findobj('tag','gmo t'));
delete(instrfind);
%Screen('Preference', 'SkipSyncTests', 1);
global seri framenumber videoobj savevideo espSeri origin_time;

%Default settings 
PsychDefaultSetup(2);

%Screen numbers
screens = Screen('Screens');
screenNumber =0;% max(screens);
backroundc = BlackIndex(screenNumber);
[window, windowRect] = PsychImaging('OpenWindow', screenNumber, backroundc);
[screenXpixels, screenYpixels] = Screen('WindowSize', window);
rectoff = windowRect;
rectoff(3)=windowRect(3)/2;  
[windowOff,rectoff]=Screen('OpenOffscreenWindow',window ,backroundc,rectoff);
%Maximum priority level
topPriorityLevel = MaxPriority(window);
Priority(topPriorityLevel);
ifi = Screen('GetFlipInterval', window);
HideCursor(screenNumber);

running =1;
ledrect = [850 1000 912 1140];
screen1rect =[0 0 912 1140];
screen2rect =[912 0 912*2 1140];

video =[];
Texture =[];

triggered =0;
framenumber =-1;
videoframecount =0;
adaptationduration = 0;
xpos =512;
ypos = 364;
xscale =1;
yscale =1;
angle=0;
framelength =1;
whitebackround =0;
inversecolour =0;
savevideo =0;
repeatstim =0;

%Setup AI
AI = analoginput('nidaq','Dev1');
chan = addchannel(AI,0);
AI.SampleRate = 4000;
AI.InputType = 'SingleEnded';
ActualRate = AI.SampleRate;
AI.TriggerType = 'HwDigital';
AI.HwDigitalTriggerSource = 'PFI0';
AI.TriggerCondition = 'PositiveEdge';
AI.TriggerFcn = {@ExternalTrigger};

% diode??
dio = digitalio('nidaq','Dev1');
addline(dio,1:2,'out');
bvdata = logical([0 0]);
putvalue(dio,bvdata);
%Setup keyboard

KbName('UnifyKeyNames');
escapeKey = KbName('Escape');


%Setup of tracking
COMport = 'COM4';
seri=serial(COMport);
seri.baudrate=1250000;%1152000;
seri.inputbuffersize=50000;
fopen(seri);
trackingbuffer=[];



% Second COM port for talking to the 2photon pc
espCOMport = 'COM6';
espSeri = serial(espCOMport);
espSeri.baudrate=115200;
fopen(espSeri);
message = '';

%setup camera
videoobj = videoinput('gentl', 1, 'Mono8');
src = getselectedsource(videoobj);
videoobj.LoggingMode = 'disk';
src.IIDCMode = 'Mode2';
src.ExposureTime = 2000;
diskLogger = VideoWriter('C:\Jouni\flyvirtualworld\buffervideo.avi', 'Grayscale AVI');
diskLogger.FrameRate =60;
videoobj.DiskLogger = diskLogger;
%For data saving
SEdata =[];
SEpos =1;
AIdata = [];
AIpos =1;


%Main loop
while running

    %Poll keyboard
    [~, ~, keyCode, ~] = KbCheck(-1);
    if keyCode(escapeKey)
        running =0;      
    end
    
    % Read message from 2P PC
    if espSeri.BytesAvailable % this is taking .9ms to check, perhaps too long?

        message = fgetl(espSeri);
    end
    
    %Handle the message
    if (~isempty(message))
        
        % Quit
        elseif(strcmp(message,'Q'))

            running = 0;

        % Save Video
        elseif(strcmp(message,'S'))

            if(AIpos>1 && SEpos >1)
                dt = datestr(now,'yymmddHHMMSS');
                %end
                stim_type = strsplit(stimfilename,'.');
                datafilename = strcat('.\data\data', dt, '_', stim_type(1), '_', num2str(angle), '.mat');
                param.stimfilename =stimfilename;
                param.adaptationduration = adaptationduration;
                param.xpos = xpos;
                param.ypos = ypos;
                param.xscale = xscale;
                param.yscale = yscale;
                param.angle = angle;
                param.framelength =framelength;
                param.whitebackround =whitebackround;
                param.inversecolour =inversecolour;
                if(savevideo)
                    while(videoobj.FramesAcquired~= videoobj.DiskLoggerFrameCount)
                        pause(0.1);
                    end
                     pause(1);
                    videofilename =strcat('.\data\data', dt, '_', stim_type(1), '_', num2str(angle), '.avi');
                    movefile('buffervideo.avi',cell2mat(videofilename),'f');
                    save(cell2mat(datafilename),'AIdata','SEdata','param');
                else
                    save(cell2mat(datafilename),'AIdata','SEdata','param');
                end
            end

        % Reset 
        elseif(strcmp(message,'R'))
            framenumber =-1;
            fwrite(seri,[254,0]);
            triggered =0;
            bvdata = logical([0 0]);
            putvalue(dio,bvdata);
            stop(AI);
            if(~isempty(Texture))
                Screen('Close',Texture);
                Texture =[];
            end

        % Change Parameters
        elseif(strcmp(message,'C')) 
            adaptationduration = str2double(fgetl(espSeri));
            xpos = str2double(fgetl(espSeri));
            ypos = str2double(fgetl(espSeri));
            xscale = str2double(fgetl(espSeri));
            yscale = str2double(fgetl(espSeri));
            angle = str2double(fgetl(espSeri));
            framelength = str2double(fgetl(espSeri));
            whitebackround = str2double(fgetl(espSeri));
            inversecolour = str2double(fgetl(espSeri));
            externaltrigger = str2double(fgetl(espSeri));
            savevideo = str2double(fgetl(espSeri));
            repeatstim = str2double(fgetl(espSeri));
            
            if(whitebackround == 0)
                Screen('FillRect',window,[0 0 0],  windowRect);
                Screen('FillRect',windowOff,[0 0 0],  rectoff);
            end

        % Load a stimulus file
        elseif(strcmp(message,'L'))
            if(isempty(video) ==0)
                clear video;
            end
            stimfilename = fgetl(espSeri);
            if(exist(['.\stimulus\' stimfilename], 'file'))
                file=load(['.\stimulus\' stimfilename]);
                for n = 1:size(file.video,3)
                    video(n).Image = squeeze(file.video(:,:,n));
                end 
                clear file;
            end

        % Trigger
        elseif(strcmp(message,'T'))

            triggered =1;
            fprintf(espSeri, 'triggered');

            frameorder = 1:length(video);
            frame_buffer = zeros(size(video(1).Image,1), size(video(1).Image,2),3);
                        
            for n = 1:ceil(length(frameorder)/3)
                
                frame_buffer(:,:,:) =0;

                frame_buffer(:,:,3) = video(frameorder(1+3*(n-1))).Image;
                
                if(2+3*(n-1)<=length(frameorder))
                    frame_buffer(:,:,1) = video(frameorder(2+3*(n-1))).Image;
                end
                
                if(3+3*(n-1)<=length(frameorder))
                    frame_buffer(:,:,2) = video(frameorder(3+3*(n-1))).Image;
                end
                Texture(n) = Screen('MakeTexture', window, frame_buffer);
            end
            
            clear frame_buffer;
            videoframecount=length(Texture);
            
            V_TIMING = zeros(0,videoframecount);
            
            duration = videoframecount/120;

            planned_timings = (0: framelength : framelength * (videoframecount-1));

            %data logging
            AI.SamplesPerTrigger = round(duration*ActualRate);
            AIdata = zeros(AI.SamplesPerTrigger,2);
            AIpos =1;
           
            SEdata = zeros(round(duration*4000),4);
            SEpos =1;
            
            videoobj.FramesPerTrigger = round(60*duration);
            
            % check trigger type
            if(externaltrigger)
                AI.TriggerType = 'HwDigital';
                AI.HwDigitalTriggerSource = 'PFI0';
                AI.TriggerCondition = 'PositiveEdge';
                AI.TriggerFcn = {@ExternalTrigger};
            else
                AI.TriggerType = 'Manual';
            end
            if(externaltrigger)
                framenumber =-1;
                start(AI);
            else
                framenumber=1;
                if(savevideo)
                    start(videoobj);
                end
                start(AI);
                trigger(AI);
                fwrite(seri,[255,0]);
                origin_time = Screen('Flip', window);
            end
    end
    message = '';
    
    %End of stimulus
    if(framenumber> videoframecount)
        if(repeatstim)
             framenumber =1;
        else
            framenumber =-1;

            fwrite(seri,[254,0]);
            triggered =0;
            bvdata = logical([0 0]);
            putvalue(dio,bvdata);
            stop(AI);
            if(~isempty(Texture))
                Screen('Close',Texture);
                Texture =[];
            end
        end
    end

    %White backround
    if(whitebackround ==1)
        Screen('FillRect',window,[1 1 1],windowRect);
         Screen('FillRect',windowOff,[1 1 1],rectoff);
    end
    %Read DAG
    if(AI.SamplesAvailable >0)
        DAGdata = getdata(AI,AI.SamplesAvailable);
        AIdata(AIpos:(AIpos+length(DAGdata)-1),1)= framenumber;
        AIdata(AIpos:(AIpos+length(DAGdata)-1),2) =DAGdata;
        AIpos = AIpos+length(DAGdata);
    end

    %Read tracking
    if (seri.bytesavailable>0)
        raw=fread(seri,seri.bytesavailable);
        
        %Handle the parsing
        if(~isempty(trackingbuffer))
            raw =[trackingbuffer; raw];
            trackingbuffer =[];
        end
            
        zinds=find(raw==0);
        if((length(raw)-zinds(end)+1)~=12)
            trackingbuffer =raw(zinds(end):end);
            raw = raw(1:(zinds(end)-1));
            zinds =zinds(1:end-1);
        end
            
        if(sum(diff(zinds)~=12)>1)
            %Add nans if corrupted data sets
            for k =2 :length(zinds)
                dd = zinds(k)-zinds(k-1);
                if(dd < 12)
                    raw = [raw(1:zinds(k-1)-1); 0; raw(zinds(k)+1)-1; NaN(10,1); raw(zinds(k):end)];
                end
                   
            end
            zinds=find(raw==0);
        end
        ind=raw(zinds+1);
        % Ind
        md=min(diff(ind));
         
        %Handle missing datasegment
        if(max(diff(ind))>1)|~(md==1|md==-254)
            %Add NaNs when missing data
            for k =2 :length(zinds)
                dd = raw(zinds(k)+1)-raw(zinds(k-1)+1);
                if(~(md==1|md==-254))
                    raw = [raw(1:zinds(k)-1);0; NaN(11,1); raw(zinds(k):end)];
                end
            end 
            zinds=find(raw==0);
        end
        raw(zinds+2) = raw(zinds+2)-128;
        raw(zinds+3) = raw(zinds+3)-128;
        raw(zinds+4) = raw(zinds+4)-128;
        raw(zinds+5) = raw(zinds+5)-128;
    
        x0=raw(zinds+3);
        y0=raw(zinds+2);
        x1=raw(zinds+5);
        y1=raw(zinds+4);
        theta = (x0 +x1)/2*180/200;
       
        forward = (y0+y1)*0.7071*180/200;
        side = (y0-y1) *0.7071*180/200;
        SEdata(SEpos:(SEpos+length(x0)-1),1)= framenumber;
        SEdata(SEpos:(SEpos+length(x0)-1),2) =forward;
        SEdata(SEpos:(SEpos+length(x0)-1),3) =side;
        SEdata(SEpos:(SEpos+length(x0)-1),4) =theta;
        SEpos = SEpos +length(x0);
    end
    
    %Draw    
    if(triggered)

        if(framenumber>0)
             
            rect = [0 0 size(video(1).Image,2) size(video(1).Image,1)]; 
            pos=CenterRectOnPoint(rect,xpos,ypos);
            % Translate, rotate, re-tranlate and draw
            Screen('glPushMatrix', windowOff);
            Screen('glTranslate', windowOff, xpos, ypos);
            Screen('glScale', windowOff, 1, 2);
            Screen('glRotate', windowOff, angle, 0, 0);
            Screen('glScale', windowOff, xscale, yscale);
            Screen('glTranslate', windowOff, -xpos, -ypos);
            %Draw all of the texures to screen
            Screen('DrawTextures', windowOff,Texture(framenumber),[],pos);
            Screen('glPopMatrix', windowOff);
            Screen('DrawTextures', window,windowOff,[], screen1rect);
            Screen('DrawTextures',window,windowOff,[],screen2rect);
            Screen('FillRect',window,[1 1 1], ledrect);
            Screen('FillRect',window,[1 1 1], ledrect+[912 0 912 0]);
        else
            Screen('FillRect',window,[0 0 0], ledrect);
            Screen('FillRect',window,[0 0 0], ledrect+[912 0 912 0]);
        end

        %Update frame number
        if(externaltrigger)
            if (framenumber > 0) framenumber = framenumber + 1; end
        else
            framenumber = framenumber+1;
        end
    else
        Screen('FillRect',window,[0 0 0], ledrect);
        Screen('FillRect',window,[0 0 0], ledrect+[912 0 912 0]);
    end

    %Flip and note time.
    if(triggered)
        if(framenumber > 1)
            V_TIMING(framenumber-1) = Screen('Flip', window, origin_time + planned_timings(framenumber-1)); 
        end
    end
end

%End of main loop
if(triggered)
    fwrite(seri,[254,0]);
    stop(AI);
end

%Close AI
delete(AI);
clear AI;
delete(dio);
delete(videoobj);
% close psycophysics toolbox
sca;

%Close tracking
fwrite(seri,[254,0]);
fclose(seri);
delete(seri);
fclose(espSeri);
delete(espSeri);
end

% start everything when we get the TTL from scanner head.
function ExternalTrigger(~,~)

    global seri framenumber videoobj savevideo espSeri origin_time;
    fwrite(seri,[255,0]);
    fwrite(espSeri, 't');
    framenumber=1;
    if(savevideo)
        start(videoobj);
    end
    origin_time = Screen('Flip', window);
end