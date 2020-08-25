# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 12:49:53 2020

@author: Itay
"""

# pyinstaller --onefile -w CC_GUI_Final.py

import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image,ImageTk
import numpy as np
import time
import pickle


# SARSA L Parameters
alpha=0.1
gamma=0.4
lam=0.4
epsilon=0

#State Life Expectancy deterioration rate
EDrop=0.99999
#Life expectency (episodes*assumed mean rolls per episode)
lifeExpectencey=100000*20
#State deletion threshold
maxStatesStored=100000


# [Nearby, Far, Abroad]
diceReset=[3,4,2]

diceDict={0:"Nearby",1:"Far",2:"Abroad"}
dicColorDict={0:"blue",1:"green",2:"red"}


#[Safe Return, Mask, Exposure]
NearbyDie=[3,2,1]
FarDie=[2,2,2]
AbroadDie=[1,2,3]
diceStats=np.array([NearbyDie,FarDie,AbroadDie])

#Score required to win
goal=10

roundRewardNone=-1
roundRewardLost=-2

winReward=10
loseReward=-5
reachGoalReward=3


# [green left, yellow left, red left, brains, shotguns, green footsteps,
#  yellow footsteps, red footsteps, current score, maximal opponent score]
stateReset=[diceReset[0],diceReset[1],diceReset[2],0,0,0,0,0,0,0]


global keepPlaying
keepPlaying=1

global new_width,new_height,ratio
new_height=560
new_width=800
ratio=1

root=tk.Tk()
root.geometry("800x560")
root.title("COVID Clash")

def newGame():
    global keepPlaying
    keepPlaying=1
    
    ########## Window Resize Function ##########
    def resizeWindow(event):
        global new_width,new_height,ratio
        new_width = root.winfo_width()
        new_height = root.winfo_height()
        if new_width/800>new_height/560:
            new_width=int(800*new_height/560)
        else:
            new_height=int(560*new_width/800)
            
        ratio=new_width/800
        canvas.config(width=new_width,height=new_height)
        #####
        image = bgImgOrigin.resize((new_width, new_height))
        global bgPhoto
        bgPhoto = ImageTk.PhotoImage(image)
        canvas.itemconfig(background,image=bgPhoto)
        #####
        scale=0.6*ratio
        resizeSize=(int(logoImgOrigin.size[0]*scale),int(logoImgOrigin.size[1]*scale))
        image = logoImgOrigin.resize(resizeSize)
        global logoPhoto,logo
        logoPhoto = ImageTk.PhotoImage(image)
        canvas.delete(logo)
    
        logo=canvas.create_image(int(0.5*new_width),0,anchor="n",image=logoPhoto)
        #####
        global P1ScoreText,P2ScoreText
        canvas.delete(P1ScoreText)
        canvas.delete(P2ScoreText)
        P1ScoreText=canvas.create_text(int(1/3*new_width),0.18*new_height,anchor="n",text=P1ScoreInput,font=("Arial",int(38*ratio),"bold"),justify=tk.CENTER)
        P2ScoreText=canvas.create_text(int(2/3*new_width),0.18*new_height,anchor="n",text=P2ScoreInput,font=("Arial",int(38*ratio),"bold"),justify=tk.CENTER)
        
        global dice,diceImages
        # canvas.delete(diceFrame)
        canvas.delete(dice[0])
        canvas.delete(dice[1])
        canvas.delete(dice[2])
        # diceFrameWidth=ratio*500
        # diceFrameHeight=ratio*160
        # diceFrame=canvas.create_rectangle(int(new_width*0.5-diceFrameWidth/2),int(new_height*0.55-diceFrameHeight/2),int(new_width*0.5+diceFrameWidth/2),int(new_height*0.55+diceFrameHeight/2),outline="#fffac3",width=4)
        
        diceSize=int(140*ratio)
    
        blankDie=blankOrigin.resize((diceSize,diceSize))
        blueExposure=blueExposureOrigin.resize((diceSize,diceSize))
        blueMask=blueMaskOrigin.resize((diceSize,diceSize))
        blueSafe=blueSafeOrigin.resize((diceSize,diceSize))
        greenExposure=greenExposureOrigin.resize((diceSize,diceSize))
        greenMask=greenMaskOrigin.resize((diceSize,diceSize))
        greenSafe=greenSafeOrigin.resize((diceSize,diceSize))
        redExposure=redExposureOrigin.resize((diceSize,diceSize))
        redMask=redMaskOrigin.resize((diceSize,diceSize))
        redSafe=redSafeOrigin.resize((diceSize,diceSize))
            
        diceImages=list()
        
        blueImages=list()
        blueImages.append(ImageTk.PhotoImage(blankDie))
        blueImages.append(ImageTk.PhotoImage(blueExposure))
        blueImages.append(ImageTk.PhotoImage(blueMask))
        blueImages.append(ImageTk.PhotoImage(blueSafe))
        diceImages.append(blueImages)
        
        greenImages=list()
        greenImages.append(ImageTk.PhotoImage(blankDie))
        greenImages.append(ImageTk.PhotoImage(greenExposure))
        greenImages.append(ImageTk.PhotoImage(greenMask))
        greenImages.append(ImageTk.PhotoImage(greenSafe))
        diceImages.append(greenImages)
        
        redImages=list()
        redImages.append(ImageTk.PhotoImage(blankDie))
        redImages.append(ImageTk.PhotoImage(redExposure))
        redImages.append(ImageTk.PhotoImage(redMask))
        redImages.append(ImageTk.PhotoImage(redSafe))
        diceImages.append(redImages)
        
        for i in range(3):
            dice[i]=canvas.create_image(int(new_width*0.4-160*ratio+i*160*ratio),int(new_height*0.55),anchor="center",image=diceImages[diceColor[i]][diceState[i]])
        
        #####################################################
            
        continueButton.config(font=("Arial",int(20*ratio),"bold"))
        continueButton.place(x=int(new_width*0.4+270*ratio),y=int(new_height*0.55-70*ratio),anchor="nw",width=int(140*ratio),height=int(70*ratio))
        
        stopButton.config(font=("Arial",int(20*ratio),"bold"))
        stopButton.place(x=int(new_width*0.4+270*ratio),y=int(new_height*0.55),anchor="nw",width=int(140*ratio),height=int(70*ratio))
        
        #####################################################
        
        global RemDiceTitle,nearDiceText,farDiceText,abroadDiceText,curStateTitle,safeTripText,exposureText
        canvas.delete(RemDiceTitle)
        canvas.delete(nearDiceText)
        canvas.delete(farDiceText)
        canvas.delete(abroadDiceText)
        canvas.delete(curStateTitle)
        canvas.delete(safeTripText)
        canvas.delete(exposureText)
        
        RemDiceTitle=canvas.create_text(int(new_width*0.28),int(new_height*0.75),anchor="center",text="Remaining Dice",font=("Arial",int(14*ratio),"bold"))
        nearDiceText=canvas.create_text(int(new_width*0.18),int(new_height*0.82),anchor="center",text=nearDiceInput,font=("Arial",int(14*ratio),"bold"),justify=tk.CENTER,fill="blue")
        farDiceText=canvas.create_text(int(new_width*0.28),int(new_height*0.82),anchor="center",text=farDiceInput,font=("Arial",int(14*ratio),"bold"),justify=tk.CENTER,fill="green")
        abroadDiceText=canvas.create_text(int(new_width*0.38),int(new_height*0.82),anchor="center",text=abroadDiceInput,font=("Arial",int(14*ratio),"bold"),justify=tk.CENTER,fill="red")
        
        curStateTitle=canvas.create_text(int(new_width*0.72),int(new_height*0.75),anchor="center",text="Current Status",font=("Arial",int(14*ratio),"bold"))
        safeTripText=canvas.create_text(int(new_width*0.64),int(new_height*0.82),anchor="center",text=safeTripInput,font=("Arial",int(14*ratio),"bold"),justify=tk.CENTER,fill="maroon1")
        exposureText=canvas.create_text(int(new_width*0.80),int(new_height*0.82),anchor="center",text=exposureInput,font=("Arial",int(14*ratio),"bold"),justify=tk.CENTER,fill="maroon1")
        
        #####################################################
        
        global copyrightText
        canvas.delete(copyrightText)
        copyrightText=canvas.create_text(int(new_width*0.005),int(new_height*0.995),anchor="sw",text="Created by Itay Grinberg",font=("Arial",int(12*ratio),"italic"))
        
        #####################################################
        
        victoryRateBar.place(relx=0.5,rely=0.90,width=int(400*ratio),height=int(15*ratio),anchor="center")
        
        global victoryRateText
        canvas.delete(victoryRateText)
        victoryRateText=canvas.create_text(int(new_width*0.5),int(new_height*0.94),text=victoryRateTextInput,font=("Arial",int(12*ratio),"bold"),anchor="center")
        
        ####################################################
        helpButton.config(font=("Arial",int(15*ratio),"bold"))
        helpButton.place(x=new_width*0.995,y=new_height*0.995,anchor="se",width=int(ratio*40),height=int(ratio*40))
        
        ####################################################
        try:
            global helpCanvas,S,tabControl,aboutText,rulesText,exitButton
            S.configure('TNotebook.Tab', font=('Arial',int(15*ratio),'bold'))
            helpCanvas.config(width=new_width*0.87,height=new_height*0.81)
            helpCanvas.place(x=new_width*0.5,y=new_height*0.15,anchor="n")
            tabControl.place(relx=0.5,rely=0.5,anchor="center",width=new_width*0.86,height=new_height*0.8)
            aboutText.config(font=("Arial",int(12*ratio)))
            aboutText.pack(expand=True,fill="both")
            # aboutText.config(state="disabled")
            rulesText.config(font=("Arial",int(11*ratio)))
            rulesText.pack(expand=True,fill="both")
            rulesText.tag_add("steps",2.0,6.0)
            rulesText.tag_configure("steps",font=("Arial",int(11*ratio),"italic bold"))
            # rulesText.config(state="disabled")
            exitButton.config(font=("Arial",int(ratio*13)))
            exitButton.place(relx=0.5,rely=0.98,anchor="s",width=30*ratio,height=30*ratio)
        except:
            1
            
        ####################################################
        try:
            global winnerText,endGameFrame,winnerLabel,newGameButton,endGameButton
            endGameFrame.config(highlightthickness=int(5*ratio))
            endGameFrame.place(relx=0.5,rely=0.6,width=0.4*new_width,height=0.4*new_height,anchor="center")
            winnerLabel.config(font=("Arial",int(23*ratio),"bold"))
            winnerLabel.place(relx=0.5,rely=0.1,anchor="n")
            newGameButton.config(font=("Arial",int(17*ratio)))
            newGameButton.place(relx=0.5,rely=0.9,anchor="se",width=0.45*0.4*new_width,height=0.3*0.4*new_height)
            endGameButton.config(font=("Arial",int(17*ratio)))
            endGameButton.place(relx=0.5,rely=0.9,anchor="sw",width=0.45*0.4*new_width,height=0.3*0.4*new_height)
        except:
            1
    
    ########## Game Functions ##########
    def loadParameters():
        with open("data/SARSA.dat","rb") as filehandle:
            [stateLabels1,stateLabels2,SE1,SE2,Q1,Q2,E1,E2]=pickle.load(filehandle)
        try:
            with open('data/stats.dat', 'rb') as filehandle:
                stats=pickle.load(filehandle)
        except:
            stats=np.zeros((2))
        
        return stateLabels1,stateLabels2,Q1,Q2,SE1,SE2,E1,E2,stats
    
    def saveParameters():
        with open('data/SARSA.dat',"wb") as filehandle:
            pickle.dump([stateLabels1,stateLabels2,SE1,SE2,Q1,Q2,E1,E2],filehandle)
            
        # with open('data/stateLabels1.dat', 'w') as filehandle:
        #     for listitem in stateLabels1:
        #         for seclistitem in listitem:
        #             filehandle.write('%s,' % seclistitem)
        #         filehandle.write('\n')
                
        # with open('data/stateLabels2.dat', 'w') as filehandle:
        #     for listitem in stateLabels2:
        #         for seclistitem in listitem:
        #             filehandle.write('%s,' % seclistitem)
        #         filehandle.write('\n')
        
        # with open('data/SE1.dat', 'w') as filehandle:
        #     for listitem in SE1:
        #             filehandle.write('%s' % listitem)
        #             filehandle.write('\n')
                    
        # with open('data/SE2.dat', 'w') as filehandle:
        #     for listitem in SE2:
        #             filehandle.write('%s' % listitem)
        #             filehandle.write('\n')
        
        # with open('data/Q1.dat', 'w') as filehandle:
        #     for listitem in Q1:
        #         for seclistitem in listitem:
        #             filehandle.write('%s,' % seclistitem)
        #         filehandle.write('\n')
                
        # with open('data/Q2.dat', 'w') as filehandle:
        #     for listitem in Q2:
        #         for seclistitem in listitem:
        #             filehandle.write('%s,' % seclistitem)
        #         filehandle.write('\n')
        
        # with open('data/E1.dat', 'w') as filehandle:
        #     for listitem in E1:
        #         for seclistitem in listitem:
        #             filehandle.write('%s,' % seclistitem)
        #         filehandle.write('\n')
                
        # with open('data/E2.dat', 'w') as filehandle:
        #     for listitem in E2:
        #         for seclistitem in listitem:
        #             filehandle.write('%s,' % seclistitem)
        #         filehandle.write('\n')
        # return 0
                
    def decide(state,stateLabels,Q):
        if (sum(state[0:3])==0) & (sum(state[5:8])==0):
            action=0
        elif state[4]>=3:
            action=0        
        else:
            try:
                currentStateLabel=stateLabels.index(state)
                print(Q[currentStateLabel])
                if Q[currentStateLabel][0]==Q[currentStateLabel][1]:
                    prob=[0.5,0.5]
                else:
                    greedyAction=np.where(Q[currentStateLabel]==max(Q[currentStateLabel]))[0][0]
                    prob=[((1-greedyAction)*(1-epsilon)+greedyAction*epsilon),((1-greedyAction)*epsilon+greedyAction*(1-epsilon))]
            except:
                prob=[0.5,0.5]
            action=np.random.choice([0,1],p=prob)
        return action
       
    def rollDice(state):
        global dice,diceImages,canvas
        global diceState,diceColor

        currentDice=state[5:8]
        state[5:8]=[0,0,0]
        diceNeeded=3-sum(currentDice)
        diceAvailable=sum(state[0:3])
        for i in range(min([diceNeeded,diceAvailable])):
            newDie=np.random.choice(range(3),p=np.array(state[0:3])/sum(np.array(state[0:3])))
            currentDice[newDie]=currentDice[newDie]+1
            state[newDie]=state[newDie]-1
        counter=-1
        for i in range(3):
            for j in range(currentDice[i]):
                counter=counter+1
                newRoll=np.random.choice(range(3),p=diceStats[i]/6)
                if newRoll==2:
                    diceState[counter]=2
                    diceColor[counter]=i
                    canvas.itemconfig(dice[counter],image=diceImages[diceColor[counter]][diceState[counter]])
                    state[5+i]=state[5+i]+1
                elif newRoll==0:
                    diceState[counter]=3
                    diceColor[counter]=i
                    canvas.itemconfig(dice[counter],image=diceImages[diceColor[counter]][diceState[counter]])
                    state[3+newRoll]=state[3+newRoll]+1
                else:
                    diceState[counter]=1
                    diceColor[counter]=i
                    canvas.itemconfig(dice[counter],image=diceImages[diceColor[counter]][diceState[counter]])
                    state[3+newRoll]=state[3+newRoll]+1
        
        global nearDiceText,farDiceText,abroadDiceText,safeTripText,exposureText
        global nearDiceInput,farDiceInput,farDiceInput,abroadDiceInput,safeTripInput,exposureInput
        
        nearDiceInput="Nearby\n"+str(state[0])
        canvas.itemconfig(nearDiceText,text=nearDiceInput)
        
        farDiceInput="Far\n"+str(state[1])
        canvas.itemconfig(farDiceText,text=farDiceInput)
        
        abroadDiceInput="Abroad\n"+str(state[2])
        canvas.itemconfig(abroadDiceText,text=abroadDiceInput)        
                
        safeTripInput="Safe Trips\n"+str(state[3])
        canvas.itemconfig(safeTripText,text=safeTripInput)
        
        exposureInput="Exposures\n"+str(state[4])
        canvas.itemconfig(exposureText,text=exposureInput)
        canvas.update()
        return state
    
    def PCTurn(statePC):
        global statePCOld    
        global Q1
        global Q2
        global E1
        global E2
        global SE1
        global SE2
        global stateLabels1
        global stateLabels2

        action=1
        if PC=="P1":
            time.sleep(0.7)
            while action==1:
                # stateOld=statePC.copy()
                # actionOld=action
                statePCOld=statePC.copy()
                statePC=rollDice(statePC.copy())
                print(statePC)
                action=decide(statePC.copy(),stateLabels1,Q1)
                if statePC[4]<3:
                    Q1,E1,SE1,stateLabels1=stateExistance(statePC.copy(),Q1,E1,SE1,stateLabels1)
                    Q1,E1,SE1=recalcQ(statePC.copy(),statePCOld.copy(),1,1,Q1,E1,SE1,stateLabels1,0)
                time.sleep(2)
        if PC=="P2":
            time.sleep(0.7)
            while action==1:
                # stateOld=statePC.copy()
                # actionOld=action
                statePCOld=statePC.copy()
                statePC=rollDice(statePC.copy())
                print(statePC)
                action=decide(statePC.copy(),stateLabels2,Q2)
                if statePC[4]<3:
                    Q2,E2,SE2,stateLabels2=stateExistance(statePC.copy(),Q2,E2,SE2,stateLabels2)
                    Q2,E2,SE2=recalcQ(statePC.copy(),statePCOld.copy(),1,1,Q2,E2,SE2,stateLabels2,0)
                time.sleep(2)
        return statePC
    
    def scoreUpdate(state,otherState):
        if state[4]<3:
            state[-2]=state[-2]+state[3]
            state=[diceReset[0],diceReset[1],diceReset[2],0,0,0,0,0,state[-2],state[-1]]
            otherState[-1]=state[-2]
        else:
            state=[diceReset[0],diceReset[1],diceReset[2],0,0,0,0,0,max([state[-2]-1,0]),state[-1]]
            otherState[-1]=state[-2]
        state=[diceReset[0],diceReset[1],diceReset[2],0,0,0,0,0,state[-2],state[-1]]
        return state,otherState
    
    def scoreBoardUpdate():
        global P1ScoreText,P2ScoreText,P1ScoreInput,P2ScoreInput,canvas
    
        if PC=="P1":
            P1ScoreInput="PC\n"+str(statePC[8])
            P2ScoreInput="USER\n"+str(stateUser[8])
        else:
            P2ScoreInput="PC\n"+str(statePC[8])
            P1ScoreInput="USER\n"+str(stateUser[8])
        canvas.itemconfig(P1ScoreText,text=P1ScoreInput)
        canvas.itemconfig(P2ScoreText,text=P2ScoreInput)
    
    def recalcQ(state,stateOld,action,actionOld,Q,E,SE,stateLabels,reward):
    
        if (state[0:3]==diceReset) & (state[8]<goal):
            currentStateLabel=stateLabels.index(state)
            Q[currentStateLabel]=Q[currentStateLabel]*0
        if stateOld[0:3]==diceReset:
            oldStateLabel=stateLabels.index(stateOld)
            Q[oldStateLabel]=Q[oldStateLabel]*0
            return Q,E,SE
    
        currentStateLabel=stateLabels.index(state)
        oldStateLabel=stateLabels.index(stateOld)
    
        delta=reward+gamma*Q[currentStateLabel][action]-Q[oldStateLabel][actionOld]
        E[oldStateLabel][actionOld]=E[oldStateLabel][actionOld]+1
        print(reward,"+",gamma*Q[currentStateLabel][action],"-",Q[oldStateLabel][actionOld],"=",delta)
        print(E[oldStateLabel][actionOld])
        Q=Q+alpha*delta*E
        E=gamma*lam*E
        SE[oldStateLabel]=SE[oldStateLabel]+1
        SE=EDrop*SE
        return Q,E,SE

    def stateExistance(state,Q,E,SE,stateLabels):
        if state not in stateLabels:
            stateLabels.append(state)
            Q=np.append(Q,np.zeros((1,2)),axis=0)
            SE=np.append(SE,[1],axis=0)
            E=np.append(E,np.zeros((1,2)),axis=0)
        return Q,E,SE,stateLabels
    
    def endGamePanel():
        global winnerText,endGameFrame,winnerLabel,newGameButton,endGameButton
        endGameFrame=tk.Frame(canvas,highlightbackground="red", highlightthickness=int(5*ratio))
        endGameFrame.place(relx=0.5,rely=0.6,width=0.4*new_width,height=0.4*new_height,anchor="center")
        winnerLabel=tk.Label(endGameFrame,text=winnerText,font=("Arial",int(23*ratio),"bold"))
        winnerLabel.place(relx=0.5,rely=0.1,anchor="n")
        newGameButton=tk.Button(endGameFrame,text="New Game",font=("Arial",int(17*ratio)),command=newGameButtonCommand)
        newGameButton.place(relx=0.5,rely=0.9,anchor="se",width=0.45*0.4*new_width,height=0.3*0.4*new_height)
        endGameButton=tk.Button(endGameFrame,text="Quit",font=("Arial",int(17*ratio)),command=endGameButtonCommand)
        endGameButton.place(relx=0.5,rely=0.9,anchor="sw",width=0.45*0.4*new_width,height=0.3*0.4*new_height)
    
    def newGameButtonCommand():
        canvas.destroy()
        newGame()
        
    def endGameButtonCommand():
        root.destroy()
        
    def resetRemDiceState():
        global RemDiceTitle,nearDiceText,farDiceText,abroadDiceText,curStateTitle,safeTripText,exposureText
        global nearDiceInput,farDiceInput,farDiceInput,abroadDiceInput,safeTripInput,exposureInput
            
        nearDiceInput="Nearby\n"+str(stateReset[0])
        canvas.itemconfig(nearDiceText,text=nearDiceInput)
        
        farDiceInput="Far\n"+str(stateReset[1])
        canvas.itemconfig(farDiceText,text=farDiceInput)
        
        abroadDiceInput="Abroad\n"+str(stateReset[2])
        canvas.itemconfig(abroadDiceText,text=abroadDiceInput)
        
        safeTripInput="Safe Trips\n"+str(stateReset[3])
        canvas.itemconfig(safeTripText,text=safeTripInput)
        
        exposureInput="Exposures\n"+str(stateReset[4])
        canvas.itemconfig(exposureText,text=exposureInput)

        

    
#####################################
    keepPlaying=0
    #Choose who starts
    PC=np.random.choice(["P1","P2"])
    global winnerText
    winnerText=""
    print(PC)
    
    global stateUser
    
    global stats
    
    global statePC
    
    stateUser=stateReset.copy()
    statePC=stateReset.copy()
    
    if PC=="P1":
        currentState=statePC.copy()
    else:
        currentState=stateUser.copy()
    
    global statePCOld    
    global stateUserOld    
    global Q1
    global Q2
    global E1
    global E2
    global SE1
    global SE2
    global stateLabels1
    global stateLabels2
    stateUserOld=stateUser.copy()
    statePCOld=statePC.copy()
    stateLabels1,stateLabels2,Q1,Q2,SE1,SE2,E1,E2,stats = loadParameters()
    
    ################################################
    global new_width,new_height,ratio
    ################################################
    
    bgImgOrigin=Image.open(r"data/bg.png")
    bgImg=ImageTk.PhotoImage(bgImgOrigin)
    
    global canvas
    canvas=tk.Canvas(root,width=new_width,height=new_height)
    canvas.place(relx=0.5,rely=0.5,anchor="center")
    
    canvas.update()
    
    background=canvas.create_image(0,0,anchor="nw",image=bgImg)
    
    ###############################################
    
    logoImgOrigin=Image.open("data/Logo.png")
    scale=0.6*new_width/800
    resizeSize=(int(logoImgOrigin.size[0]*scale),int(logoImgOrigin.size[1]*scale))
    logoImg=logoImgOrigin.resize(resizeSize, Image.ANTIALIAS)
    logoImg=ImageTk.PhotoImage(logoImg)
    global logo
    logo=canvas.create_image(int(0.5*new_width),0,anchor="n",image=logoImg)
    
    ##############################################
    
    global P1ScoreText,P2ScoreText,P1ScoreInput,P2ScoreInput
    
    if PC=="P1":
        P1ScoreInput="PC\n"+str(statePC[8])
        P2ScoreInput="USER\n"+str(stateUser[8])
    else:
        P2ScoreInput="PC\n"+str(statePC[8])
        P1ScoreInput="USER\n"+str(stateUser[8])
    
    P1ScoreText=canvas.create_text(int(1/3*new_width),0.18*new_height,anchor="n",text=P1ScoreInput,font=("Arial",int(38*ratio),"bold"),justify=tk.CENTER)
    P2ScoreText=canvas.create_text(int(2/3*new_width),0.18*new_height,anchor="n",text=P2ScoreInput,font=("Arial",int(38*ratio),"bold"),justify=tk.CENTER)
    
    ##############################################
    global dice,diceImages
    
    blankOrigin=Image.open("data/blank.png")
    
    blueExposureOrigin=Image.open("data/Exposure_Blue.png")
    blueMaskOrigin=Image.open("data/Mask_Blue.png")
    blueSafeOrigin=Image.open("data/ReturnSafely_Blue.png")
    
    greenExposureOrigin=Image.open("data/Exposure_Green.png")
    greenMaskOrigin=Image.open("data/Mask_Green.png")
    greenSafeOrigin=Image.open("data/ReturnSafely_Green.png")
    
    redExposureOrigin=Image.open("data/Exposure_Red.png")
    redMaskOrigin=Image.open("data/Mask_Red.png")
    redSafeOrigin=Image.open("data/ReturnSafely_Red.png")
    
    diceSize=int(140*ratio)
    
    blankDie=blankOrigin.resize((diceSize,diceSize))
    blueExposure=blueExposureOrigin.resize((diceSize,diceSize))
    blueMask=blueMaskOrigin.resize((diceSize,diceSize))
    blueSafe=blueSafeOrigin.resize((diceSize,diceSize))
    greenExposure=greenExposureOrigin.resize((diceSize,diceSize))
    greenMask=greenMaskOrigin.resize((diceSize,diceSize))
    greenSafe=greenSafeOrigin.resize((diceSize,diceSize))
    redExposure=redExposureOrigin.resize((diceSize,diceSize))
    redMask=redMaskOrigin.resize((diceSize,diceSize))
    redSafe=redSafeOrigin.resize((diceSize,diceSize))
    
    diceImages=list()
    
    blueImages=list()
    blueImages.append(ImageTk.PhotoImage(blankDie))
    blueImages.append(ImageTk.PhotoImage(blueExposure))
    blueImages.append(ImageTk.PhotoImage(blueMask))
    blueImages.append(ImageTk.PhotoImage(blueSafe))
    diceImages.append(blueImages)
    
    greenImages=list()
    greenImages.append(ImageTk.PhotoImage(blankDie))
    greenImages.append(ImageTk.PhotoImage(greenExposure))
    greenImages.append(ImageTk.PhotoImage(greenMask))
    greenImages.append(ImageTk.PhotoImage(greenSafe))
    diceImages.append(greenImages)
    
    redImages=list()
    redImages.append(ImageTk.PhotoImage(blankDie))
    redImages.append(ImageTk.PhotoImage(redExposure))
    redImages.append(ImageTk.PhotoImage(redMask))
    redImages.append(ImageTk.PhotoImage(redSafe))
    diceImages.append(redImages)
    
    global diceState,diceColor
    diceState={0:0,1:0,2:0}
    diceColor={0:0,1:0,2:0}
    dice=list()
    dice.append(canvas.create_image(int(new_width*0.4-160*ratio),int(new_height*0.55),anchor="center",image=diceImages[diceColor[0]][diceState[0]]))
    dice.append(canvas.create_image(int(new_width*0.4),int(new_height*0.55),anchor="center",image=diceImages[diceColor[1]][diceState[1]]))
    dice.append(canvas.create_image(int(new_width*0.4+160*ratio),int(new_height*0.55),anchor="center",image=diceImages[diceColor[2]][diceState[2]]))
    
    ##############################################
    
    global RemDiceTitle,nearDiceText,farDiceText,abroadDiceText,curStateTitle,safeTripText,exposureText
    global nearDiceInput,farDiceInput,farDiceInput,abroadDiceInput,safeTripInput,exposureInput
    
    RemDiceTitle=canvas.create_text(int(new_width*0.28),int(new_height*0.75),anchor="center",text="Remaining Dice",font=("Arial",int(14*ratio),"bold"))

    nearDiceInput="Nearby\n"+str(stateReset[0]) ##### Fix Later #####
    nearDiceText=canvas.create_text(int(new_width*0.18),int(new_height*0.82),anchor="center",text=nearDiceInput,font=("Arial",int(14*ratio),"bold"),justify=tk.CENTER,fill="blue")
    
    farDiceInput="Far\n"+str(stateReset[1]) ##### Fix Later #####
    farDiceText=canvas.create_text(int(new_width*0.28),int(new_height*0.82),anchor="center",text=farDiceInput,font=("Arial",int(14*ratio),"bold"),justify=tk.CENTER,fill="green")
    
    abroadDiceInput="Abroad\n"+str(stateReset[2]) ##### Fix Later #####
    abroadDiceText=canvas.create_text(int(new_width*0.38),int(new_height*0.82),anchor="center",text=abroadDiceInput,font=("Arial",int(14*ratio),"bold"),justify=tk.CENTER,fill="red")
    
    
    curStateTitle=canvas.create_text(int(new_width*0.72),int(new_height*0.75),anchor="center",text="Current Status",font=("Arial",int(14*ratio),"bold"))
    
    safeTripInput="Safe Trips\n"+str(stateReset[3])
    safeTripText=canvas.create_text(int(new_width*0.64),int(new_height*0.82),anchor="center",text=safeTripInput,font=("Arial",int(14*ratio),"bold"),justify=tk.CENTER,fill="maroon1")
    
    exposureInput="Exposures\n"+str(stateReset[4])
    exposureText=canvas.create_text(int(new_width*0.80),int(new_height*0.82),anchor="center",text=exposureInput,font=("Arial",int(14*ratio),"bold"),justify=tk.CENTER,fill="maroon1")
    
    ##############################################
    
    global copyrightText
    
    copyrightText=canvas.create_text(int(new_width*0.005),int(new_height*0.995),anchor="sw",text="Created by Itay Grinberg",font=("Arial",int(12*ratio),"italic"))
    
    ##############################################
    
    global S
    S=ttk.Style()
    S.theme_use("clam")
    S.configure("red.Horizontal.TProgressbar", foreground='black', background='#fffac3')#("red.Horizontal.TProgressbar", foreground="#fffac3")
    
    victoryRateBar=ttk.Progressbar(canvas,style="red.Horizontal.TProgressbar",length=100)
    
    victoryRateBar.place(relx=0.5,rely=0.9,width=int(400*ratio),height=int(15*ratio),anchor="center")
    if stats[0]==0:
        victoryRateBar["value"]=0
        victoryRateTextInput="You have won "+str(100)+"% of "+str(0)+" games"

    else:
        victoryRateBar["value"]=stats[1]/stats[0]*100
        victoryRateBar.update()
        victoryRateTextInput="You have won "+str(round(stats[1]/stats[0]*100,1))+"% of "+str(int(stats[0]))+" games"

    global victoryRateText
    
    victoryRateText=canvas.create_text(int(new_width*0.5),int(new_height*0.94),text=victoryRateTextInput,font=("Arial",int(12*ratio),"bold"),anchor="center")
    
    ##############################################
    
    def continueButtonCommand():
        global stateUserOld,statePC,stateUser
        global Q1,Q2,E1,E2,SE1,SE2,stateLabels1,stateLabels2
        stateUserOld=stateUser.copy()
        stateUser=rollDice(stateUser.copy())
        
        stopButton["state"]="normal"
        
        if stateUser[4]>=3:
            continueButton["state"]="disable"
        else:
            if PC=="P1":
                Q2,E2,SE2,stateLabels2=stateExistance(stateUser.copy(),Q2,E2,SE2,stateLabels2)
                Q2,E2,SE2=recalcQ(stateUser.copy(),stateUserOld.copy(),1,1,Q2,E2,SE2,stateLabels2,0)
            else:
                Q1,E1,SE1,stateLabels1=stateExistance(stateUser.copy(),Q1,E1,SE1,stateLabels1)
                Q1,E1,SE1=recalcQ(stateUser.copy(),stateUserOld.copy(),1,1,Q1,E1,SE1,stateLabels1,0)
        return 0
    
    def stopButtonCommand():
        
        global stats
        global Q1,Q2,E1,E2,SE1,SE2,stateLabels1,stateLabels2
        global statePC,statePCOld,stateUser,stateUserOld
        global diceState,diceColor
        global winnerText

        
        continueButton["state"]="disable"
        stopButton["state"]="disable"
        
        diceState={0:0,1:0,2:0}
        diceColor={0:0,1:0,2:0}
        for i in range(3):
            canvas.itemconfig(dice[i],image=diceImages[diceColor[i]][diceState[i]])
        
        if (stateUser[4]<3) & (stateUser[3]>0):
            rewardUser=min([2,stateUser[3]])
        elif (stateUser[4]<3) | (stateUser[-2]==0):
            rewardUser=roundRewardNone
        else:
            rewardUser=roundRewardLost
        if PC=="P1":
            Q2,E2,SE2,stateLabels2=stateExistance(stateUser.copy(),Q2,E2,SE2,stateLabels2)
            Q2,E2,SE2=recalcQ(stateUser.copy(),stateUserOld.copy(),0,1,Q2,E2,SE2,stateLabels2,rewardUser)
        else:
            Q1,E1,SE1,stateLabels1=stateExistance(stateUser.copy(),Q1,E1,SE1,stateLabels1)
            Q1,E1,SE1=recalcQ(stateUser.copy(),stateUserOld.copy(),0,1,Q1,E1,SE1,stateLabels1,rewardUser)
        statUserOld=stateUser.copy()
        statePCOld=statePC.copy()
        stateUser,statePC=scoreUpdate(stateUser.copy(),statePC.copy())
        scoreBoardUpdate()
        
        if (stateUser[8]>=goal) & (stateUser[8]>statePC[8]):
            if PC=="P1":
                print("Human Wins!")
                winnerText="HUMANITY\nWINS!"
                if PC=="P1":
                    Q1,E1,SE1,stateLabels1=stateExistance(statePC.copy(),Q1,E1,SE1,stateLabels1)
                    Q1,E1,SE1=recalcQ(statePC.copy(),statePCOld.copy(),1,0,Q1,E1,SE1,stateLabels1,loseReward)
                    Q2,E2,SE2,stateLabels2=stateExistance(stateUser.copy(),Q2,E2,SE2,stateLabels2)
                    Q2,E2,SE2=recalcQ(stateUser.copy(),stateUserOld.copy(),1,0,Q2,E2,SE2,stateLabels2,winReward)
                else:
                    Q1,E1,SE1,stateLabels1=stateExistance(stateUser.copy(),Q1,E1,SE1,stateLabels1)
                    Q1,E1,SE1=recalcQ(stateUser.copy(),stateUserOld.copy(),1,0,Q1,E1,SE1,stateLabels1,winReward)
                    Q2,E2,SE2,stateLabels2=stateExistance(statePC.copy(),Q2,E2,SE2,stateLabels2)
                    Q2,E2,SE2=recalcQ(statePC.copy(),statePCOld.copy(),1,0,Q2,E2,SE2,stateLabels2,loseReward)
                saveParameters()
                stats=stats+1
                saveStats()
                endGamePanel()
                # diceSpaceFrame.destroy()
                # diceSpaceFrame = tk.Frame(canvasMainPage,height=140,width=400,bg="Black")
                # diceSpaceFrame.grid(row=1,column=0)
                # diceSpaceFrame.grid_propagate(0)
                # vicotryLabel = tk.Label(diceSpaceFrame,text="Human Wins!",bg="Black",fg="red")
                # vicotryLabel.place(relx=0.5, rely=0.5, anchor="c")
                # NewGameButton=tk.Button(diceSpaceFrame,text="New Game",padx=10,pady=5,command=newGameButtonCommand)
                # NewGameButton.place(relx=0.5,rely=0.3,anchor="c")
                return 0
        elif (statePC[8]>=goal) & (statePC[8]>=stateUser[8]):
            if PC=="P1":
                print("Computer Wins!")
                winnerText="GAME OVER!\nComputer Wins!"
                if PC=="P1":
                    Q1,E1,SE1,stateLabels1=stateExistance(statePC.copy(),Q1,E1,SE1,stateLabels1)
                    Q1,E1,SE1=recalcQ(statePC.copy(),statePCOld.copy(),1,0,Q1,E1,SE1,stateLabels1,winReward)
                    Q2,E2,SE2,stateLabels2=stateExistance(stateUser.copy(),Q2,E2,SE2,stateLabels2)
                    Q2,E2,SE2=recalcQ(stateUser.copy(),stateUserOld.copy(),1,0,Q2,E2,SE2,stateLabels2,loseReward)
                else:
                    Q1,E1,SE1,stateLabels1=stateExistance(stateUser.copy(),Q1,E1,SE1,stateLabels1)
                    Q1,E1,SE1=recalcQ(stateUser.copy(),stateUserOld.copy(),1,0,Q1,E1,SE1,stateLabels1,loseReward)
                    Q2,E2,SE2,stateLabels2=stateExistance(statePC.copy(),Q2,E2,SE2,stateLabels2)
                    Q2,E2,SE2=recalcQ(statePC.copy(),statePCOld.copy(),1,0,Q2,E2,SE2,stateLabels2,winReward)
                saveParameters()
                stats[0]=stats[0]+1
                saveStats()
                endGamePanel()
                # diceSpaceFrame.destroy()
                # diceSpaceFrame = tk.Frame(canvasMainPage,height=140,width=400,bg="Black")
                # diceSpaceFrame.grid(row=1,column=0)
                # diceSpaceFrame.grid_propagate(0)
                # vicotryLabel = tk.Label(diceSpaceFrame,text="Computer Wins!",bg="Black",fg="red")
                # vicotryLabel.place(relx=0.5, rely=0.5, anchor="c")
                # NewGameButton=tk.Button(diceSpaceFrame,text="New Game",padx=10,pady=5,command=newGameButtonCommand)
                # NewGameButton.place(relx=0.5,rely=0.3,anchor="c")
                return 0
            else:
                if PC=="P1":
                    Q1,E1,SE1,stateLabels1=stateExistance(statePC.copy(),Q1,E1,SE1,stateLabels1)
                    Q1,E1,SE1=recalcQ(statePC.copy(),statePCOld.copy(),1,0,Q1,E1,SE1,stateLabels1,0)
                    Q2,E2,SE2,stateLabels2=stateExistance(stateUser.copy(),Q2,E2,SE2,stateLabels2)
                    Q2,E2,SE2=recalcQ(stateUser.copy(),stateUserOld.copy(),1,0,Q2,E2,SE2,stateLabels2,0)
                else:
                    Q1,E1,SE1,stateLabels1=stateExistance(stateUser.copy(),Q1,E1,SE1,stateLabels1)
                    Q1,E1,SE1=recalcQ(stateUser.copy(),stateUserOld.copy(),1,0,Q1,E1,SE1,stateLabels1,0)
                    Q2,E2,SE2,stateLabels2=stateExistance(statePC.copy(),Q2,E2,SE2,stateLabels2)
                    Q2,E2,SE2=recalcQ(statePC.copy(),statePCOld.copy(),1,0,Q2,E2,SE2,stateLabels2,0)
        time.sleep(0.2)
        statePC=PCTurn(statePC.copy())
        
        if (statePC[4]<3) & (statePC[3]>0):
            rewardPC=min([2,statePC[3]])
        elif (statePC[4]<3) | (statePC[-2]==0):
            rewardPC=roundRewardNone
        else:
            rewardPC=roundRewardLost
        if PC=="P2":
            Q2,E2,SE2,stateLabels2=stateExistance(statePC.copy(),Q2,E2,SE2,stateLabels2)
            Q2,E2,SE2=recalcQ(statePC.copy(),statePCOld.copy(),0,1,Q2,E2,SE2,stateLabels2,rewardPC)
        else:
            Q1,E1,SE1,stateLabels1=stateExistance(statePC.copy(),Q1,E1,SE1,stateLabels1)
            Q1,E1,SE1=recalcQ(statePC.copy(),statePCOld.copy(),0,1,Q1,E1,SE1,stateLabels1,rewardPC)

        stateUserOld=stateUser.copy()
        statePCOld=statePC.copy()
        statePC,stateUser=scoreUpdate(statePC.copy(),stateUser.copy())
        scoreBoardUpdate()
        
        time.sleep(1)
        if (stateUser[8]>=goal) & (stateUser[8]>=statePC[8]):
            if PC=="P2":
                print("Human Wins!")
                winnerText="HUMANITY\nWINS!"
                if PC=="P1":
                    Q1,E1,SE1,stateLabels1=stateExistance(statePC.copy(),Q1,E1,SE1,stateLabels1)
                    Q1,E1,SE1=recalcQ(statePC.copy(),statePCOld.copy(),1,0,Q1,E1,SE1,stateLabels1,loseReward)
                    Q2,E2,SE2,stateLabels2=stateExistance(stateUser.copy(),Q2,E2,SE2,stateLabels2)
                    Q2,E2,SE2=recalcQ(stateUser.copy(),stateUserOld.copy(),1,0,Q2,E2,SE2,stateLabels2,winReward)
                else:
                    Q1,E1,SE1,stateLabels1=stateExistance(stateUser.copy(),Q1,E1,SE1,stateLabels1)
                    Q1,E1,SE1=recalcQ(stateUser.copy(),stateUserOld.copy(),1,0,Q1,E1,SE1,stateLabels1,winReward)
                    Q2,E2,SE2,stateLabels2=stateExistance(statePC.copy(),Q2,E2,SE2,stateLabels2)
                    Q2,E2,SE2=recalcQ(statePC.copy(),statePCOld.copy(),1,0,Q2,E2,SE2,stateLabels2,loseReward)
                saveParameters()
                stats=stats+1
                saveStats()
                endGamePanel()
                # diceSpaceFrame.destroy()
                # diceSpaceFrame = tk.Frame(canvasMainPage,height=140,width=400,bg="Black")
                # diceSpaceFrame.grid(row=1,column=0)
                # diceSpaceFrame.grid_propagate(0)
                # vicotryLabel = tk.Label(diceSpaceFrame,text="Human Wins!",bg="Black",fg="red")
                # vicotryLabel.place(relx=0.5, rely=0.5, anchor="c")
                # NewGameButton=tk.Button(diceSpaceFrame,text="New Game",padx=10,pady=5,command=newGameButtonCommand)
                # NewGameButton.place(relx=0.5,rely=0.3,anchor="c")
                return 0
        elif (statePC[8]>=goal) & (statePC[8]>stateUser[8]):
            if PC=="P2":
                winnerText="GAME OVER!\nComputer Wins!"
                time.sleep(1)
                if PC=="P1":
                    Q1,E1,SE1,stateLabels1=stateExistance(statePC.copy(),Q1,E1,SE1,stateLabels1)
                    Q1,E1,SE1=recalcQ(statePC.copy(),statePCOld.copy(),1,0,Q1,E1,SE1,stateLabels1,winReward)
                    Q2,E2,SE2,stateLabels2=stateExistance(stateUser.copy(),Q2,E2,SE2,stateLabels2)
                    Q2,E2,SE2=recalcQ(stateUser.copy(),stateUserOld.copy(),1,0,Q2,E2,SE2,stateLabels2,loseReward)
                else:
                    Q1,E1,SE1,stateLabels1=stateExistance(stateUser.copy(),Q1,E1,SE1,stateLabels1)
                    Q1,E1,SE1=recalcQ(stateUser.copy(),stateUserOld.copy(),1,0,Q1,E1,SE1,stateLabels1,loseReward)
                    Q2,E2,SE2,stateLabels2=stateExistance(statePC.copy(),Q2,E2,SE2,stateLabels2)
                    Q2,E2,SE2=recalcQ(statePC.copy(),statePCOld.copy(),1,0,Q2,E2,SE2,stateLabels2,winReward)
                saveParameters()
                stats[0]=stats[0]+1
                saveStats()
                endGamePanel()
                # diceSpaceFrame.destroy()
                # diceSpaceFrame = tk.Frame(canvasMainPage,height=140,width=400,bg="Black")
                # diceSpaceFrame.grid(row=1,column=0)
                # diceSpaceFrame.grid_propagate(0)
                # vicotryLabel = tk.Label(diceSpaceFrame,text="Computer Wins!",bg="Black",fg="red")
                # vicotryLabel.place(relx=0.5, rely=0.5, anchor="c")
                # NewGameButton=tk.Button(diceSpaceFrame,text="New Game",padx=10,pady=5,command=newGameButtonCommand)
                # NewGameButton.place(relx=0.5,rely=0.3,anchor="c")
                return 0 
            else:
                if PC=="P1":
                    Q1,E1,SE1,stateLabels1=stateExistance(statePC.copy(),Q1,E1,SE1,stateLabels1)
                    Q1,E1,SE1=recalcQ(statePC.copy(),statePCOld.copy(),1,0,Q1,E1,SE1,stateLabels1,0)
                    Q2,E2,SE2,stateLabels2=stateExistance(stateUser.copy(),Q2,E2,SE2,stateLabels2)
                    Q2,E2,SE2=recalcQ(stateUser.copy(),stateUserOld.copy(),1,0,Q2,E2,SE2,stateLabels2,0)
                else:
                    Q1,E1,SE1,stateLabels1=stateExistance(stateUser.copy(),Q1,E1,SE1,stateLabels1)
                    Q1,E1,SE1=recalcQ(stateUser.copy(),stateUserOld.copy(),1,0,Q1,E1,SE1,stateLabels1,0)
                    Q2,E2,SE2,stateLabels2=stateExistance(statePC.copy(),Q2,E2,SE2,stateLabels2)
                    Q2,E2,SE2=recalcQ(statePC.copy(),statePCOld.copy(),1,0,Q2,E2,SE2,stateLabels2,0)
        continueButton["state"]="normal"
        time.sleep(0.7)
        diceState={0:0,1:0,2:0}
        diceColor={0:0,1:0,2:0}
        for i in range(3):
            canvas.itemconfig(dice[i],image=diceImages[diceColor[i]][diceState[i]])
        resetRemDiceState()
    
    continueButton=tk.Button(canvas,text="Roll",font=("Arial",int(20*ratio),"bold"),fg="green",command=continueButtonCommand)
    continueButton.place(x=int(new_width*0.4+270*ratio),y=int(new_height*0.55-70*ratio),anchor="nw",width=int(140*ratio),height=int(70*ratio))
    
    stopButton=tk.Button(canvas,text="End Turn",font=("Arial",int(20*ratio),"bold"),fg="red",command=stopButtonCommand)
    stopButton.place(x=int(new_width*0.4+270*ratio),y=int(new_height*0.55),anchor="nw",width=int(140*ratio),height=int(70*ratio))
    stopButton["state"]="disable"
    
    ##############################################
    
    with open('data/text.dat', 'rb') as textFile:
        [aboutTextInput,rulesTextInput] = pickle.load(textFile)
    
    def helpButtonCommand():
        global helpCanvas,tabControl,aboutText,rulesText,exitButton,S
        S.configure('TNotebook.Tab', font=('Arial',int(15*ratio),'bold'))
        helpCanvas=tk.Canvas(canvas,width=new_width*0.87,height=new_height*0.81,bg="#fffac3")
        helpCanvas.place(x=new_width*0.5,y=new_height*0.15,anchor="n")
        tabControl=ttk.Notebook(helpCanvas)
        aboutTab=ttk.Frame(tabControl)
        rulesTab=ttk.Frame(tabControl)
        tabControl.add(aboutTab,text="About the Game")
        tabControl.add(rulesTab,text="Game Rules")
        aboutText=tk.Text(aboutTab,wrap="word",font=("Arial",int(12*ratio)))
        aboutText.pack(expand=True,fill="both")
        aboutText.insert('insert',aboutTextInput)
        aboutText.config(state="disabled")
        rulesText=tk.Text(rulesTab,wrap="word",font=("Arial",int(11*ratio)))
        rulesText.pack(expand=True,fill="both")
        rulesText.insert('insert',rulesTextInput)
        rulesText.tag_add("steps",2.0,6.0)
        rulesText.tag_configure("steps",font=("Arial",int(11*ratio),"italic bold"))
        rulesText.config(state="disabled")
        tabControl.place(relx=0.5,rely=0.5,anchor="center",width=new_width*0.86,height=new_height*0.8)
        exitButton=tk.Button(helpCanvas,text="X",font=("Arial",int(ratio*13)),command=exitButtonCommand)
        exitButton.place(relx=0.5,rely=0.99,anchor="s",width=30*ratio,height=30*ratio)
    
    def exitButtonCommand():
        global helpCanvas
        helpCanvas.destroy()
        
        
    helpButton=tk.Button(canvas,text="?",font=("Arial",15,"bold"),command=helpButtonCommand)
    helpButton.place(x=new_width*0.995,y=new_height*0.995,anchor="se",width=40*ratio,height=40*ratio)
    
    root.bind('<Configure>', resizeWindow)
    
    def player():
        if PC=="P1":
            print("PC starts")
            stopButtonCommand()
    
    def saveStats():
        with open('data/stats.dat', 'wb') as filehandle:
            pickle.dump(stats,filehandle)
        # with open('data/stats.dat', 'w') as filehandle:
        #     for listitem in stats:
        #         filehandle.write('%s\n' % listitem)
    
    root.after(1000,player)

newGame()
 
root.mainloop()