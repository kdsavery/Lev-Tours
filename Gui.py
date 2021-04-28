# Multi-frame tkinter application v2.1


# all imports
import tkinter as tk
from tkinter import font as tkFont
from tkinter import filedialog
from PIL import Image, ImageTk
import webbrowser
from tkinter import messagebox
import time
import building as bd
from Fonts import *
import os
import shutil
from threading import Thread
import wifi_scanning as ws
import logger as log
import random

# Constants
LIGHT_GREY = "#D3D3D3"
NAVY = "#003466"
GOLD = "#FFD200"
SILVER = "#C0C0C0"
DARK_GREY = "#A9A9A9"
ROBOT_SPEED = 4.583 #ft/s

# Globals
NodeList = []
deleteLabel = tk.Label
adminFlag = False
start = ""
end = ""
currentFloorIndex = 0
currentBldg = None
currentPath = []
path_to_start = False
path_running = False
tour_running = False
remaining_tour = []
currentTour = ""
tourSelected = False
pause = False


init_entries = ["Start", "Destination",
                "Node Name", "Node Type (p/s/t)",
                "Node 1", "Node 2", "Node Distance",
                "Building Name", "Floor Number",
                "Enter Nearby", "Enter Tour Name"]

# Init all buildings
buildings = []
for bldg in bd.get_buildings():
    new_bldg = bd.Building(bldg)
    new_bldg.load(bldg.lower())
    buildings.append( new_bldg)


def get_building(name):
    for building in buildings:
        if building.name == name.lower():
            return building

    messagebox.showerror("Load Error", "Notice: Building does not exist")
    return None

# Function to clear entry boxes when they contain initializing information
def entry_handler(event, object):
    if(object.get() in init_entries):
        object.delete(0, 'end')


class TourGuideApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        #blank frame for initalization purposes
        self._frame = None

        #sweting window name
        self.title("Lev tours")
        #setting background color
        self.configure(bg=NAVY)
        #setting window to fullscreen
        self.attributes("-fullscreen", True)


        # setting screen info
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        #binding escape to close full screen
        self.bind('<Escape>', self.end_fullscreen)

        #switching th frame to the home page
        self.switch_frame(HomePage)

        #setting a font that can be genral usage
        helv36 = tkFont.Font(family='Helvetica', size=36, weight='bold')


    # switch frame function
    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

        # Split up new frame class string for output
        frame_str = str(frame_class)
        try:
            # format: "<class '__main__.FRAMENAME'>
            frame_str = frame_str.split(".")
            frame_str = frame_str[1].strip("'>")
        except:
            frame_str = str(frame_class)
        log.logging.info("Frame switch to " + frame_str)

        if(not currentBldg == None and frame_str == "adminLandingPage"):
            currentBldg.save(currentBldg.name.lower())

    #end full screen function for binds, currently linked to escape
    def end_fullscreen(self, event=None):
        self.state = False
        self.attributes("-fullscreen", False)
        return "break"

#homescreen class page works as a frame
class HomePage(tk.Frame):
    def __init__(self, master):


        #font creation may change to a global font class
        helv36 = tkFont.Font(family='Helvetica', size=36)
        helv20 = tkFont.Font(family='Helvetica', size=20)

        global currentFloorIndex
        currentFloorIndex = 0

        #loading and rendering the nau image banner
        load = Image.open("images/nau.jpg")
        render = ImageTk.PhotoImage(load)

        #, width=master.screen_width, height=master.screen_height
        tk.Frame.__init__(self, master, bg=NAVY , width=master.screen_width, height=master.screen_height)

        # creating buttons  fg = font bg = background color
        infoBut = tk.Button(self,fg = 'white', bg = DARK_GREY,
        text= "Info Page",font = helv36,width=10,height =2, command=lambda: master.switch_frame(infoPage))

        adminBut = tk.Button(self, fg = 'white',
        bg = DARK_GREY,text= "Admin Page",
        font = helv36,width=10,height =2,  command=lambda: master.switch_frame(adminLogin))

        toursBut = tk.Button(self, fg = 'white',
        bg = DARK_GREY,text= "Tours Page", font = helv36, width=10,height =2,  command=lambda: master.switch_frame(ChooseBuildingPage))

        #using the image to create a label
        img = tk.Label(self, image=render, bg = GOLD)

        img.image = render

        #placing all widgets to correct screen locations
        img.place(relx = .5, rely =.2,  anchor = 'c' )

        toursBut.place(relx=.5, rely = .81, anchor = 'c')

        infoBut.place(relx=.2, rely = .81, anchor = 'c')

        adminBut.place(relx=.8, rely = .81, anchor = 'c')

'''
Class: infoPage
Description: a page for information such as a FAQ and a link to the teams website
Note: FAQ currently not set up
Author: Erik Clark
'''
class infoPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg=NAVY, width=master.screen_width, height=master.screen_height)

        #setting up fon this will be moved to a class eventually
        helv15 = tkFont.Font(family='Helvetica', size=15)
        helv20 = tkFont.Font(family='Helvetica', size=20)
        helv36 = tkFont.Font(family='Helvetica', size=36)

        #loading banner image
        load = Image.open("images/nau.jpg")
        load.resize((200,400), Image.NEAREST)
        render = ImageTk.PhotoImage(load)

        img = tk.Label(self, image=render, bg = GOLD)
        img.image = render

        #web button for opening a webpage that directs users to the teams webpage
        webButton = tk.Button(self, fg = 'white',
        font = helv36, width=12,height =2,bg = DARK_GREY,
        text = "Team Website",command=lambda: self.openweb())

        #return to home screen button
        returnButton = tk.Button(self, fg = 'white',bg = DARK_GREY,
        text= "Back", font = helv20, width=10,height =2,
        command=lambda: master.switch_frame(HomePage))

        faqListBox = tk.Listbox(self, selectmode = 'single', font = Helvetica(16),
            width = 60, height = 16, justify = 'left',fg = 'white', bg =NAVY,
            highlightthickness = 4, highlightcolor = 'white')
        faqListBox.place(relx = .31, rely = .74, anchor = 'c')

        FaQ = []

        # Question/Answer 1
        FaQ.append("Q1. Can a front end user use this software in any building?")
        FaQ.append("A1. A back end user must completely  set up a building")
        FaQ.append("       before a front end user can take tours in the building.")
        FaQ.append("       So as long is the building is set up, the software")
        FaQ.append("       can be used there.")

        # Question/Answer 2
        FaQ.append("Q2. What buildings can this be set up in?")
        FaQ.append("A2. Any building that has multiple access points in it")
        FaQ.append("       with Wi-Fi capabilities. Note: during building set")
        FaQ.append("       up a back end user also needs a map image of the")
        FaQ.append("       building.")

        # Question/Answer 3
        FaQ.append("Q3. Where do I put map images on the computer?")
        FaQ.append("A3. They can be put anywhere on the computer as long as")
        FaQ.append("       they can find it in file explorer.")

        # Question/Answer 4
        FaQ.append("Q4. What happens when I get to a transitional period?")
        FaQ.append("A4. Enter the transitional point and head to the desire floor")
        FaQ.append("       shown by instructions, while following all instructions")
        FaQ.append("       on screen.")


        for faq in range(len(FaQ)):
            faqListBox.insert("end", FaQ[faq])
            faqListBox.insert("end", "")

        #unused string right now
        teamInfoString = "Learn more about \nLevTours on our website!"


        teamInfoLab = tk.Label(self, fg = 'white',bg=NAVY,text = teamInfoString, font = helv20)

        faqLab = tk.Label(self, fg = 'white',bg=NAVY,text = "FAQ", font = helv20)
        faqLab.place(relx= .06, rely = .47, anchor = 'center')

        #placing all widgets
        img.place(relx = .5, rely =.2,  anchor = 'c' )

        webButton.place(relx = .85, rely= .78, anchor = 'c')

        returnButton.place(relx = .85, rely = .92, anchor = 'c')

        teamInfoLab.place(relx = .85, rely = .65, anchor = 'c')

    #function used to open to a web page
    def openweb(self):
        #set the page here
        url = "https://ceias.nau.edu/capstone/projects/CS/2021/LevTours-F20/landing_page.html"
        webbrowser.open(url,new=1)
        log.logging.info("Team website opened")

'''
Class: adminLogin
Description: Login page for team members to gain access to GUI editing features
Note: user and password currently hard coded but will eventually be switched to encypted file
Author: David M Robb
'''
class adminLogin(tk.Frame):

    '''
    Method: __init__
    Description: basic initalization function for adminLogin class
    Note: no extra variables needed for initalization
    '''
    def __init__(self, master):

        load = Image.open("images/nau.jpg")
        render = ImageTk.PhotoImage(load)

        # create main frame
        tk.Frame.__init__(self, master, bg=NAVY, width=master.screen_width,
        height=master.screen_height)

        #initalize variables
        helv20 = tkFont.Font(family='Helvetica', size=20)

        # create labels and entry boxs for login functions
        usernameLabel = tk.Label(self, text = 'User Name', bg = NAVY, font = helv20, fg = 'white')
        passLabel = tk.Label(self, text= 'Password', bg = NAVY, font = helv20, fg = 'white')

        username = tk.Entry(self, width = 30, bg = 'black', fg = 'white')
        password = tk.Entry(self, show='*', width = 30, bg = 'black', fg = 'white')

        # place labels and entry boxes for login functions
        usernameLabel.place(relx = .375, rely = .35)
        username.place(relx = .375, rely = .4 )

        passLabel.place(relx = .375, rely = .45)
        password.place(relx =.375, rely = .5)

        # create login button
        # method/command: checkLogin()
        loginButton = tk.Button(self, fg = 'white',bg = DARK_GREY,text= "Login",
        font = helv20, width=10,height =2,  command=lambda: self.checkLogin(master, username.get(), password.get()))
        loginButton.place(relx = .4, rely = .6)

        # create return button
        # method/command: master.switch_frame()
        returnButton = tk.Button(self, fg = 'white',bg = DARK_GREY,text= "Back",
        font = helv20, width=10,height =3,  command=lambda: master.switch_frame(HomePage))

        returnButton.place(relx = .9, rely = .9, anchor = 'c')

    # a check login function that makes sure user and password are correct
    def checkLogin(self, master, userAttempt, passAttempt):
        global adminFlag
        passwords = open("admin/password.txt").readlines()

        for words in range(len(passwords)):
            passwords[words] = self.decrypt(passwords[words])
            passwords[words] = passwords[words].strip('\n')

        for word in passwords:
            splitpass = word.split(":")
            try:
                username = splitpass[0].strip(" ")
                password = splitpass[1].strip(" ")
            except IndexError:
                return
            if(userAttempt == username and passAttempt == password):
                log.logging.info("User [" + userAttempt + "] accessed admin section")
                adminFlag = True
                master.switch_frame(adminLandingPage)

        if(not adminFlag):
            pass
            log.logging.info("Failed access to admin section")

    '''
    method: decrypt()
    description: takes in a string
                 Uses built in key to decrypt string and returns it
    Note: Key only works with Alphanumeric passwords
    Author: Ariana Clark-Futrell
    '''
    def decrypt(self,password):
        de = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        en = ['@','=','#','!','.^.','{*}','xxx',';','%^','()','(&)','```','~~','****','??','^%','-_-','(9)',',.,','&','+','[]','{}','<','>','$$']
        decrypted = password
        for let in range(26):
            decrypted = decrypted.replace(en[let], de[let])
        return decrypted

'''
class: adminLandingPage()
description: the landing page for post admin log in navigates to the rest of the
main features easily
Note: none
Author: Erik Clark
'''
class adminLandingPage(tk.Frame):
    def __init__(self, master):
        # create main frame
        tk.Frame.__init__(self, master, bg=NAVY, width=master.screen_width, height=master.screen_height)

        # fonts
        helv20 = tkFont.Font(family='Helvetica', size=20)
        helv36 = tkFont.Font(family='Helvetica', size=36)

        global currentFloorIndex
        currentFloorIndex = 0

        #banner laod
        load = Image.open("images/nau.jpg")
        render = ImageTk.PhotoImage(load)

        # banner plce
        img = tk.Label(self, image=render, bg = GOLD)
        img.image = render
        img.place(relx = .5, rely =.21,  anchor = 'c' )

        # new building button with place and function
        newBuildBut = tk.Button(self, fg = 'white', bg= DARK_GREY,text = "New \nBuilding",
        font = helv36, width=10,height =2, command=lambda: master.switch_frame(newBuildingPage))
        newBuildBut.place(relx = .8, rely = .74, anchor = 'c')

        #load building button with function and place
        loadBuildBut = tk.Button(self, fg = 'white', bg= DARK_GREY,text = "Load \nBuilding",
        font = helv36, width=10,height =2,command=lambda: master.switch_frame(ChooseBuildingPage))
        loadBuildBut.place(relx = .5, rely = .74, anchor = 'c')

        # edit passwords button with place and funcitons
        editPassBut = tk.Button(self, fg = 'white', bg= DARK_GREY,text = "Add\nUser",
        font = helv36, width=10,height =2,command=lambda: master.switch_frame(passAdjust))
        editPassBut.place(relx = .2, rely = .74, anchor = 'c',)

        # return to home page button
        returnButton = tk.Button(self, fg = 'white',bg = DARK_GREY,text= "Back",
        font = helv20, width=8,height =2,  command=lambda: exitAdmin())
        returnButton.place(relx = .91, rely = .91, anchor = 'c')

        def exitAdmin():
            global adminFlag
            adminFlag = False
            master.switch_frame(HomePage)

class ChooseBuildingPage(tk.Frame):
    def __init__(self, master):
        # create main frame
        tk.Frame.__init__(self, master, bg=NAVY, width=master.screen_width, height=master.screen_height)

        #globals
        global buildings

        #initalize variables
        buildingList = []

        # fonts
        helv20 = tkFont.Font(family='Helvetica', size=20)
        helv30 = tkFont.Font(family='Helvetica', size=30)

        BuildingListBox = tk.Listbox(self, selectmode = 'single', font = Helvetica(15), width = 30, justify = 'center')

        if buildings == []:
            messagebox.showerror("Notice", "Error: No buildings are set up, please set one up to access this page")
            if(adminFlag):
                master.switch_frame(adminLandingPage)
            else:
                master.switch_frame(HomePage)

        else:

            for building_name in bd.get_buildings():
                # Exclude incomplete buildings for tour listing
                if(adminFlag):
                    buildingList.append(building_name)
                else:
                    building_obj = get_building(building_name)
                    if(building_obj.is_connected()):
                        buildingList.append(building_name)


            BuildingListBox.place(relx = .5, rely = .5, anchor = 'c')

            buildingEntry = tk.Entry(self, font = Helvetica(15))

            buildingEntry.place(relx = .5, rely = .2, anchor = 'c')

            searchLabel = tk.Label(self, font = Helvetica(15), text = 'Search:', bg = NAVY, fg = 'white')
            searchLabel.place(relx = .5, rely = .15, anchor = 'c')

            if(adminFlag):
                returnBut = tk.Button(self, fg = 'white', bg= DARK_GREY,text = "Back",
                font = helv20, width=8,height =1,command=lambda: master.switch_frame(adminLandingPage))
                returnBut.place(relx = .9, rely = .9, anchor = 'c')
            else:
                returnBut = tk.Button(self, fg = 'white', bg= DARK_GREY,text = "Back",
                font = helv20, width=8,height =1,command=lambda: master.switch_frame(HomePage))
                returnBut.place(relx = .9, rely = .9, anchor = 'c')

        def checkkey(event):

            #initalize variables
            currentEntry = event.widget.get()

            tempList = []

            # get data from l
            if currentEntry == '':
                tempList = buildingList

            else:
                for item in buildingList:
                    if currentEntry.lower() in item.lower():
                        tempList.append(item)

                # update data in listbox
            update(tempList, BuildingListBox)


        def update(bldgList, listboxwidget ):

            # clear previous data
            listboxwidget.delete(0, 'end')

            # put new data
            for item in bldgList:
                listboxwidget.insert('end', item)

        def selectBuilding(event):
            global currentBldg
            listbox = tk.Listbox(self)
            listbox = event.widget
            coords = listbox.curselection()
            currentEntry = listbox.get(coords)
            currentBldg = get_building(currentEntry)
            log.logging.info("Current Building set to " + currentBldg.name)
            if(currentBldg.floors == {}):
                if(messagebox.askquestion("Notice", "This building has no "
                    + "floor maps added, would you like to add one now?") == "yes"):
                    master.switch_frame(newFloor)
                    return
                else:
                    return
            master.switch_frame(dragAndDrop)

        update(buildingList, BuildingListBox)
        buildingEntry.bind("<KeyRelease>", checkkey)
        BuildingListBox.bind("<Double-Button-1>", selectBuilding)
        BuildingListBox.bind("<Return>", selectBuilding)


'''
class: newBuildingPage()
description: and admin page for adding a building into the saved buildings list
Note: directs the user to set up a floor otherwise building wont save
Author: Erik Clark
'''
class newBuildingPage(tk.Frame):

    def __init__(self, master):

        tk.Frame.__init__(self, master, bg=NAVY, width=master.screen_width, height=master.screen_height)


        #banner laod
        load = Image.open("images/nau.jpg")
        render = ImageTk.PhotoImage(load)

        # banner plce
        img = tk.Label(self, image=render, bg = GOLD)
        img.image = render
        img.place(relx = .5, rely =.2,  anchor = 'c' )

        #font
        helv20 = tkFont.Font(family='Helvetica', size=20)

        #discriptor labels
        entLabel = tk.Label(text = "Enter the building's name", fg="white",font = helv20, bg = NAVY)
        entLabel.place(relx = .5, rely = .45, anchor = 'c')

        #entry box for taking in text
        enterNodeName = tk.Entry(self, font =helv20, justify = 'center',
        bg = 'black',fg= 'white')
        enterNodeName.place(relx = .5, rely = .5, anchor = 'c')
        enterNodeName.insert(0,"Building Name")

        #button for confirming building
        enterBut = tk.Button(self, fg = 'black', bg= DARK_GREY,text = "Enter",
        font = helv20, width=8,height =1,command=lambda: self.newBuilding(master,enterNodeName.get()))
        enterBut.place(relx = .5, rely = .6, anchor = 'c')

        #return button to the admin login page
        returnButton = tk.Button(self, fg = 'black',bg = DARK_GREY,text= "Back",
        font = helv20, width=10,height =3,  command=lambda: master.switch_frame(adminLandingPage))
        returnButton.place(relx = .9, rely = .9, anchor = 'c')

        enterNodeName.bind("<Button-1>", lambda event, entry=enterNodeName: entry_handler(event, entry))


    #function for creating a new building comes with checks against names
    #changes frame to floor frame if successful
    def newBuilding(self, master, name):

        global buildings
        global currentBldg

        if("_floor_" in name):
            messagebox.showerror("Notice", "Building cannot contain '_floor_'")
        elif("" == name):
            messagebox.showerror("Notice", "Building name cannot be empty")
        elif("Building Name" == name):
            messagebox.showerror("Notice", "Please enter a name for the building")
        else:
            newBuilding = bd.Building(name)
            buildings.append(newBuilding)
            currentBldg = newBuilding
            master.switch_frame(newFloor)
'''
class: newFloor()
description:  admin page for adding a floor to a building that was just created
Note: adds a floor to a building that was just created
Author: Erik Clark
'''
class newFloor(tk.Frame):
    def __init__(self, master):

        tk.Frame.__init__(self, master, bg=NAVY, width=master.screen_width, height=master.screen_height)
        load = Image.open("images/nau.jpg")
        render = ImageTk.PhotoImage(load)

        # banner plce
        img = tk.Label(self, image=render, bg = GOLD)
        img.image = render
        img.place(relx = .5, rely =.2,  anchor = 'c' )

        #font
        helv20 = tkFont.Font(family='Helvetica', size=20)


        #entry box for takinf in name
        enterNodeName = tk.Entry(self, font =helv20, justify = 'center',
        bg = 'black', fg = 'white')
        enterNodeName.place(relx = .5, rely = .5, anchor = 'c')
        enterNodeName.insert(0,"Floor Number")

        #entry box for taking in image name
        uploadBut = tk.Button(self, fg = 'black', bg= DARK_GREY,text = "Upload Map",
        font = helv20, width=10,height =1,
        command=lambda: self.uploadMap(master))
        uploadBut.place(relx = .5, rely = .6, anchor = 'c')

        #acceptor button
        createBut = tk.Button(self, fg = 'black', bg= DARK_GREY,text = "Add",
        font = helv20, height=1,
        command=lambda: self.addFloor(master, enterNodeName.get()))
        createBut.place(relx = .5, rely = .7, anchor = 'c')

        #return button
        returnButton = tk.Button(self, fg = 'black',bg = DARK_GREY,text= "Back",
        font = helv20, width=10,height =3,
        command=lambda: self.returnBack(master,adminLandingPage))
        returnButton.place(relx = .9, rely = .9, anchor = 'c')

        enterNodeName.bind("<Button-1>", lambda event, entry=enterNodeName: entry_handler(event, entry))

    def addFloor(self, master, floor):
        if(not currentBldg == None and floor in currentBldg.floors):
            messagebox.showerror("Notice", "This floor name already exists")
        elif("_floor_" in floor):
            messagebox.showerror("Notice", "Floor cannot contain '_floor_'")
        elif(":" in floor):
            messagebox.showerror("Notice", "Floor cannot contain ':'")
        elif("" == floor):
            messagebox.showerror("Notice", "Floor name cannot be empty")

        else:
            try:
                currentBldg.add_floor(floor, bd.Floor(floor), map_img)
            except NameError:
                messagebox.showerror("Notice", "No map image has been uploaded.")
                return
            currentBldg.save(currentBldg.name)
            messagebox.showinfo("Floor " + str(floor) + " added to " + bd.capitalize(currentBldg.name),
                    "You can go back to the admin page or continue adding floors.")
            master.switch_frame(newFloor)


    def uploadMap(self, master):
        global map_img
        last_bldg = buildings[-1]
        dest_path = os.path.join(bd.BD_DIRECTORY, last_bldg.name)
        if(not os.path.isdir(dest_path)):
            os.mkdir(dest_path)
        filename = filedialog.askopenfilename()
        shutil.copy(filename, dest_path)
        map_img = filename.split("/")[-1]

    #pops the building because not set up properly
    def returnBack(self, master, page):
        global buildings

        if len(buildings[0].floor_keys) == 0:
            buildings.pop()
        master.switch_frame(page)


'''
class: newFloor()
description: an admin page for adding a user and password into the admin list
Note: adds a user and a password for them to use
Author: Ariana Clark-Futrell
'''
class passAdjust(tk.Frame):
    user = ""
    passwrd = ""

    '''
    Method: __init__
    Description: basic initalization function for adminLogin class
    Note: no extra variables needed for initalization
    '''
    def __init__(self, master):


        # create main frame
        tk.Frame.__init__(self, master, bg=NAVY, width=master.screen_width, height=master.screen_height)

        #initalize variables
        helv20 = tkFont.Font(family='Helvetica', size=20)
        flag = True


        # create labels and entry boxs for login functions
        usernameLabel = tk.Label(self, text = 'New Username', bg = NAVY,fg='white', font = helv20,)
        passLabel = tk.Label(self, text= 'New Password', bg = NAVY,fg='white', font = helv20)

        returnButton = tk.Button(self, fg = 'black',bg = DARK_GREY,
        text= "Back", font = ("Helvetica", 20), width=10,height =3,
        command=lambda: master.switch_frame(HomePage))

        newUsername = tk.Entry(self,text= "use",width = 30,
        bg = 'black', fg ='white')
        newPassword = tk.Entry(self, show='*', text= "pass",width = 30,
        fg = 'white',bg='black')

        # Place labels and entry boxes for login functions
        usernameLabel.place(relx = .375, rely = .35)
        newUsername.place(relx = .375, rely = .4 )

        passLabel.place(relx = .375, rely = .45)
        newPassword.place(relx =.375, rely = .5)


        # create login button
        # method/command: checkPassword()
        confirm = tk.Button(self, fg = 'white',bg = DARK_GREY,text= "Confirm",
        font = helv20, width=10,height =2,
        command=lambda: self.checkPassword(master, flag, newPassword.get(), newUsername.get()))
        confirm.place(relx = .4, rely = .6)


        # create return button
        returnButton = tk.Button(self, fg = 'white',bg = DARK_GREY,text= "Back",
        font = helv20, width=10,height =3,  command=lambda: master.switch_frame(adminLandingPage))

        returnButton.place(relx = .9, rely = .9, anchor = 'c')

    '''
    method: checkPassword()
    description: takes in a strings, a password
                 checks to see if the password contains special characters
                 if it does returns false
    Note: Password cannot contain special characters
    Author:  Ariana Clark-Futrell
    '''
    def checkPassword(self, master, flag, passAttempt, userAtt):
        specialChars = ['!','@','#','.',',','<','>','{','}','$','%','^','&','*','(',')','_','-', '"', "'", '+','=','~','`','[',']',':',';']
        for char in specialChars:
            if(char in passAttempt):
                messagebox.showinfo("Notice", "Passwords cannot contain special characters")
                return

        for letter in passAttempt:
            if letter in specialChars:
                flag = False
                break
            else:
                flag = True
        self.passwrd = passAttempt
        self.user = userAtt

        if flag == True:
            file = open("admin/password.txt", 'a')
            file.write(self.user)
            file.write(' : ')
            file.write(self.encrypt(self.passwrd))
            file.write('\n')
            file.close()
            master.switch_frame(adminLandingPage)
        else:
            messagebox.showerror("Notice", "Building does not exist")



    '''
    method: encrypt()
    description: takes in a string
                 Uses built in key to decrypt string and returns it
    Note: Key only works with Alphanumeric passwords
    Author: Ariana Clark-Futrell
    '''

    def encrypt(self,password):
        de = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        en = ['@','=','#','!','.^.','{*}','xxx',';','%^','()','(&)','```','~~','****','??','^%','-_-','(9)',',.,','&','+','[]','{}','<','>','$$']
        encrypted = password
        for let in range(26):
            encrypted = encrypted.replace(de[let], en[let])
        return encrypted


'''
class: dragAndDrop()
description: allows the user to move nodes by clicking and dragging with the mouse
             User is also able to add, delete and save the state of the Nodes to
             a file. this file is also used to load previously created nodes to the
             Screen.
Author: David M Robb  / Erik Clark / Kyle Savery
'''

class dragAndDrop(tk.Frame):

    '''
    Method: __init__
    Description: basic initalization function for adminLogin class
    Note: no extra variables needed for initalization
    '''
    def __init__(self, master):

        # create main frame
        tk.Frame.__init__(self, master, bg=NAVY, width=master.screen_width, height=master.screen_height)

        #global
        global adminFlag
        global buildings
        global NodeList
        global currentBldg
        global currentFloor
        global start
        global end
        global path_to_start
        global pause
        pause = False

        # initalize variables
        helv15 = tkFont.Font(family='Helvetica', size=15)
        helv20 = tkFont.Font(family='Helvetica', size=20)
        helv8 = tkFont.Font(family='Helvetica', size=8)

        currentFloor = currentBldg.floor_keys[currentFloorIndex]

        log.logging.info("Current Floor set to " + currentFloor + ", within building '" + currentBldg.name +"'")
        NodeList = currentBldg.get_node_info(currentFloor)
        img_path = bd.img_path(currentBldg.name, currentBldg.floor_maps[currentFloor])
        x = master.screen_width - 300
        y = master.screen_height - 100
        load = Image.open(img_path)
        resize = load.resize((x, y), Image.NEAREST)
        resizedMap = ImageTk.PhotoImage(resize)
        img = tk.Label(self, image=resizedMap, fg = GOLD)
        img.image = resizedMap

        img.place(x=30,y=30)

        # display loaded Nodes
        # method: initalizeNodesInGUI()
        self.initalizeNodesInGUI(NodeList)

        #   Label for showing the current building
        bldg_name = bd.capitalize(currentBldg.name)
        bldgLabel = tk.Label(self, text = bldg_name, bg=NAVY,fg='white', font = helv15)
        bldgLabel.place(relx=.5,rely=.02, anchor = 'c')

        if adminFlag:

            # location for draging and droping a node to delete
            deleteNodeArea = tk.Label(self, bg = '#FF0000', padx = 20, pady = 10, borderwidth=2, relief="sunken")
            deleteNodeArea.place(x=0,y=0)

            #descriptor label for delete node
            RemoveLabel = tk.Label(self, text='← Drop here to delete', font = helv15, bg = NAVY, fg = 'white')
            RemoveLabel.place(relx = 0.037, rely = 0.005)

            #entry box for putting in node names insert adds text to the box
            enterNodeName = tk.Entry(self, bg = 'black', fg = 'white',justify = 'center')
            enterNodeName.place(relx = .91, rely = .70, anchor = 'c')
            enterNodeName.delete(0, 'end')
            enterNodeName.insert(0,"Node Name")

            #entry box for adding a node type resets text on every load of the frame
            enterNodeType = tk.Entry(self, bg = 'black', fg = 'white',justify = 'center')
            enterNodeType.place(relx = .91, rely = .75, anchor = 'c')
            enterNodeType.delete(0, 'end')
            enterNodeType.insert(0,"Node Type (p/s/t)")

            nodeListLabel = tk.Label(self, text = "Nodes", bg=NAVY,fg='white', font = helv15)
            nodeListLabel.place(relx=.91,rely=.14, anchor = 'c')

            NodeListBox = tk.Listbox(self, selectmode = 'single', font = Helvetica(15),
                width = 15, height = 10, justify = 'center')
            NodeListBox.place(relx = .91, rely = .30, anchor = 'c')

            nodenames = currentBldg.get_names(currentFloor).copy()
            nodenames.sort()
            for name in nodenames:
                NodeListBox.insert("end", name)


            editNodeBut = tk.Button(self, bg = DARK_GREY,fg='black', font=helv15,
            text = "Edit Node", command=lambda: editNode(editNodeBut))
            editNodeBut.place(relx = .91, rely = .5, anchor = 'c')

            editToursBut = tk.Button(self, bg = DARK_GREY,fg='black', font=helv15,
            text = "Edit Tours", command=lambda: editTours())
            editToursBut.place(relx = .91, rely = .56, anchor = 'c')


            #button for adding a node to the map grabs name from enter box
            addNodeButton = tk.Button(self,bg = DARK_GREY,fg='black', font=helv15,
            text = 'Add Node', command = lambda: self.addNode(master, NodeList, enterNodeName.get(), enterNodeType.get()))
            addNodeButton.place(relx = .91, rely = .80, anchor = 'c')

            #save node button for saving all nodes on a map
            saveNodeStateButton = tk.Button(self, text= "Save",bg = DARK_GREY, font=helv15,
            fg='black', command=lambda: self.saveState(NodeList, currentBldg, currentFloor,NodeListBox))
            saveNodeStateButton.place(relx =.91, rely = .88, anchor = 'c')

            #current floor label
            floorLabel = tk.Label(self, text = "Floor: " + str(currentFloorIndex + 1),
                                                            bg=NAVY,fg='white', font = helv15)
            floorLabel.place(relx=.9,rely=.066, anchor = 'c')

            upFloorButton = tk.Button(self, bg = DARK_GREY,fg='black', font=helv15,
            text = "▲", command=lambda: changeFloor(currentFloorIndex + 1))
            upFloorButton.place(relx=.82, rely = .039)

            downFloorButton = tk.Button(self, bg = DARK_GREY,fg='black', font=helv15,
            text = "▼", command=lambda: changeFloor(currentFloorIndex - 1))
            downFloorButton.place(relx=.945, rely = .039)

            #button for finishing nodes to move to do paths
            finishNodeBut = tk.Button(self, bg = DARK_GREY,fg='black', font=helv15,
            text = "Edit Paths", command=lambda: switchToPath())
            finishNodeBut.place(relx = .91, rely = .62, anchor = 'c')

            enterNodeName.bind("<Button-1>", lambda event, entry=enterNodeName: entry_handler(event, entry))
            enterNodeType.bind("<Button-1>", lambda event, entry=enterNodeType: entry_handler(event, entry))

            returnButton = tk.Button(self, text="Back to Admin",bg = DARK_GREY,
            font = helv15, command=lambda: master.switch_frame(adminLandingPage))
            returnButton.place(relx = .08, rely = .95, anchor = 'c')


        # Tour section, no admin access
        else:

            nodeOneEnt = tk.Entry(self, relief = "sunken",
            bg = 'black', fg = 'white', justify="center")
            nodeOneEnt.place(relx = .849, rely = .5)

            if start != "":
                nodeOneEnt.insert(0,start)
            else:
                nodeOneEnt.insert(0,"Start")
            nodeTwoEnt = tk.Entry(self, text="Ending Location", relief = "sunken",
            bg = 'black', fg = 'white',justify="center")
            nodeTwoEnt.place(relx = .849, rely = .55)
            nodeTwoEnt.delete(0,"end")
            if end != "":
                nodeTwoEnt.insert(0,end)
            else:
                nodeTwoEnt.insert(0,"Destination")

            NodeListBox = tk.Listbox(self, selectmode = 'single', font = Helvetica(15),
                width = 20, height = 10, justify = 'left')
            NodeListBox.place(relx = .91, rely = .33, anchor = 'c')
            nodeListLabel = tk.Label(self, text = "Legend", bg=NAVY,fg='white', font = helv15)
            nodeListLabel.place(relx=.91,rely=.165, anchor = 'c')

            nameList = currentBldg.format_multiname(currentFloor).copy()
            #nameList.sort()
            for node in nameList:
                NodeListBox.insert("end", node)

            #current floor label
            floorLabel = tk.Label(self, text = "Floor: " + str(currentFloorIndex + 1),
                                                            bg=NAVY,fg='white', font = helv15)
            floorLabel.place(relx=.9,rely=.066, anchor = 'c')


            upFloorButton = tk.Button(self, bg = DARK_GREY,fg='black', font=helv15,
            text = "▲", command=lambda: changeFloor(currentFloorIndex + 1, nodeOneEnt.get(), nodeTwoEnt.get()))

            if(currentFloorIndex != len(currentBldg.floors) - 1):
                upFloorButton.place(relx=.82, rely = .039)

            downFloorButton = tk.Button(self, bg = DARK_GREY,fg='black', font=helv15,
            text = "▼", command=lambda: changeFloor(currentFloorIndex - 1, nodeOneEnt.get(), nodeTwoEnt.get()))

            if(currentFloorIndex != 0):
                downFloorButton.place(relx=.945, rely = .039)

            # Place the pause button behind the start button
            togglePauseButton = tk.Button(self, text = "Pause",bg = DARK_GREY,
            font = helv15, width=10, command=lambda: self.toggle_pause())
            togglePauseButton.place(relx = .86, rely = .62)

            if(not path_running):
                startRoute = tk.Button(self, text = "Start Route",bg = DARK_GREY,
                font = helv15, width=10, command=lambda: self.travel_starter(master, nodeOneEnt.get(), nodeTwoEnt.get(), startRoute))
                startRoute.place(relx = .86, rely = .62)

            # Bind the entry boxes to delete there contents on first click
            nodeOneEnt.bind("<Button-1>", lambda event, entry=nodeOneEnt: entry_handler(event, entry))
            nodeTwoEnt.bind("<Button-1>", lambda event, entry=nodeTwoEnt: entry_handler(event, entry))

            self.nodeColorStart()

            if(remaining_tour == []):
                tourBut = tk.Button(self, text="Select a Tour",bg = DARK_GREY,
                font = helv15, command=lambda: chooseTour())
                tourBut.place(relx = .911, rely = .75, anchor = 'c')

            returnButton = tk.Button(self, text="Back to Home",bg = DARK_GREY,
            font = helv15, command=lambda: exitAdmin())
            returnButton.place(relx = .91, rely = .95, anchor = 'c')

            if(path_to_start):
                startButton = tk.Button(self, text="Switched to starting floor \nPress here to start route",width=40,height=6,bg = DARK_GREY,
                font = helv15, command=lambda: self.travel(master, currentPath[0], currentPath[-1], startButton))
                startButton.place(relx = .5, rely = .5, anchor = 'c')
                path_to_start = False

            elif(not currentPath == []):
                continueButton = tk.Button(self, text="Enter the elevator and proceed to floor " + str(currentFloor) + "\nPress here once you exit the elevator",width=40,height=6,bg = DARK_GREY,
                font = helv15, command=lambda: self.travel(master, currentPath[0], currentPath[-1], continueButton))
                continueButton.place(relx = .5, rely = .5, anchor = 'c')

            elif(not remaining_tour == []):
                continueTour = tk.Button(self, text="Press here to continue the tour",width=40,height=6,bg = DARK_GREY,
                font = helv15, command=lambda: self.run_tour(master, currentTour, startRoute, continueTour))
                continueTour.place(relx = .5, rely = .5, anchor = 'c')


        def chooseTour():
            nodeOneEnt.place_forget()
            nodeTwoEnt.place_forget()
            NodeListBox.place_forget()
            startRoute.place_forget()
            tourBut.place_forget()
            togglePauseButton.place_forget()
            nodeListLabel.place_forget()
            ListLabel = tk.Label(self, text = "Available Tours", bg=NAVY,fg='white', font = helv15)
            ListLabel.place(relx=.91,rely=.171, anchor = 'c')
            TourListBox = tk.Listbox(self, selectmode = 'single', font = Helvetica(15),
                width = 15, height = 10, justify = 'center')
            TourListBox.place(relx = .91, rely = .33, anchor = 'c')

            tourList =  list(currentBldg.tours.keys()).copy()
            tourList.sort()
            for name in tourList:
                TourListBox.insert("end", name)

            pauseTourButton = tk.Button(self, text = "Pause",bg = DARK_GREY,
            font = helv15, width=10, command=lambda: self.toggle_pause())
            pauseTourButton.place(relx = .91, rely = .55, anchor='c')

            startTourBut = tk.Button(self, text = "Start Tour",bg = DARK_GREY,
            font = helv15, width=10, command=lambda: self.run_tour(master,
                TourListBox.get(TourListBox.curselection()), start=startTourBut))
            startTourBut .place(relx = .91, rely = .55, anchor = 'c')

            retRouteBut = tk.Button(self, text = "Back",bg = DARK_GREY,
            font = helv15, command=lambda: master.switch_frame(dragAndDrop))
            retRouteBut .place(relx = .91, rely = .65, anchor = 'c')

        def switchToPath():

            #globals
            global currentBldg

            #removing old buttons
            addNodeButton.place_forget()
            enterNodeName.place_forget()
            finishNodeBut.place_forget()
            editNodeBut.place_forget()
            enterNodeType.place_forget()
            editToursBut.place_forget()

            saveNodeStateButton = tk.Button(self, text= "Save",bg = DARK_GREY, font=helv15,
            fg='black', command=lambda: self.saveState(NodeList, currentBldg, currentFloor))
            saveNodeStateButton.place(relx =.91, rely = .88, anchor = 'c')

            #adding new labels and buttons
            nodeOneEnt = tk.Entry(self, text="Node 1", relief = "sunken",
            bg = 'black', fg = 'white', justify="center")
            nodeOneEnt.place(relx = .85, rely = .5)
            nodeOneEnt.delete(0,"end")
            nodeOneEnt.insert(0,"Node 1")

            nodeTwoEnt = tk.Entry(self, text="Node 2", relief = "sunken",
            bg = 'black', fg = 'white',justify="center")
            nodeTwoEnt.place(relx = .85, rely = .55)
            nodeTwoEnt.delete(0,"end")
            nodeTwoEnt.insert(0,"Node 2")

            #entry box for adding a node distance resets text on every load of the frame
            enterNodeDist = tk.Entry(self, bg = 'black', fg = 'white',justify = 'center')
            enterNodeDist.place(relx = .91, rely = .616, anchor = 'c')
            enterNodeDist.delete(0, 'end')
            enterNodeDist.insert(0,"Node Distance")

            setPathBut = tk.Button(self, text = "Set Path",bg = DARK_GREY, fg="black",
            font = helv15, command = lambda: set_edge(nodeOneEnt.get(), nodeTwoEnt.get(), enterNodeDist.get()))
            setPathBut.place(relx = .91, rely = .68, anchor = 'c')


            retNodeBut = tk.Button(self, text = "Back",bg = DARK_GREY, fg="black",
            font = helv15, command = lambda: master.switch_frame(dragAndDrop))
            retNodeBut.place(relx = .91, rely = .95, anchor = 'c')

            # Populate list box with connected nodes and their distances
            NodeListBox.delete(0, 'end')
            for connection in currentBldg.get_edges(currentFloor):
                NodeListBox.insert('end', connection)


            nodeOneEnt.bind("<Button-1>", lambda event, entry=nodeOneEnt: entry_handler(event, entry))
            nodeTwoEnt.bind("<Button-1>", lambda event, entry=nodeTwoEnt: entry_handler(event, entry))
            enterNodeDist.bind("<Button-1>", lambda event, entry=enterNodeDist: entry_handler(event, entry))

            def set_edge(nameone, nametwo, distance):
                global currentBldg
                try:
                    if(distance.lower() == 'inf' or distance.lower() == 'infinity'):
                        distance = bd.INFINITY
                    else:
                        distance = float(distance)
                    if(distance <= 0.0):
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Notice", "Distance must be a positive number")
                    return
                currentBldg.set_edge(nameone, nametwo, distance)
                edges = currentBldg.get_edges(currentFloor).copy()
                edges.sort()
                NodeListBox.delete(0, 'end')
                for connection in edges:
                    NodeListBox.insert('end', connection)


        def editTours():
            addNodeButton.place_forget()
            enterNodeName.place_forget()
            finishNodeBut.place_forget()
            enterNodeType.place_forget()
            editNodeBut.place_forget()
            editToursBut.place_forget()
            saveNodeStateButton.place_forget()
            NodeListBox.place_forget()
            nodeListLabel.place_forget()

            TourListBox = tk.Listbox(self, selectmode = 'single', font = Helvetica(15),
                width = 15, height = 10, justify = 'center')
            TourListBox.place(relx = .91, rely = .3, anchor = 'c')

            tourList =  list(currentBldg.tours.keys())
            for name in tourList:
                TourListBox.insert("end", name)

            addTourEnt = tk.Entry(self, bg = 'black', fg = 'white',justify = 'center')
            addTourEnt.place(relx = .91, rely = .64, anchor = 'c')
            addTourEnt.insert(0, "Enter Tour Name")
            addTourEnt.bind("<Button-1>", lambda event, entry=addTourEnt: entry_handler(event, entry))

            addTourBut = tk.Button(self, text="Add tour",bg = DARK_GREY,
            font = helv15, command=lambda: addTour(addTourEnt.get()))
            addTourBut.place(relx = .91, rely = .69, anchor = 'c')

            removeSpotBut = tk.Button(self, text="Remove Tour",bg = DARK_GREY,
            font = helv15, command=lambda: removeTour())
            removeSpotBut.place(relx = .91, rely = .56, anchor = 'c')

            tourLab = tk.Label(self, text = "Created Tours", bg=NAVY,fg='white', font = helv15)
            tourLab.place(relx = .91, rely = .13, anchor = 'c')

            editTourBut = tk.Button(self, bg = DARK_GREY,fg='black', font=helv15,
            text = "Edit Tour", command=lambda: editTour())
            editTourBut.place(relx = .91, rely = .5, anchor = 'c')

            backBut = tk.Button(self, bg = DARK_GREY,fg='black', font=helv15,
            text = "Back", command=lambda: master.switch_frame(dragAndDrop))
            backBut.place(relx = .903, rely = .95, anchor = 'c')

            def addTour(add):
                currentBldg.tours[add] = []
                TourListBox.insert("end", add)

            def removeTour():
                try:
                    tour = TourListBox.get(TourListBox.curselection())
                except:
                    messagebox.showerror("Notice", "Please select a tour from the list to remove it.")
                    return
                currentBldg.tours.pop(tour)
                TourListBox.delete(0, 1000)
                tourList =  list(currentBldg.tours.keys())
                for name in tourList:
                    TourListBox.insert("end", name)

            def editTour():
                try:
                    tour = TourListBox.get(TourListBox.curselection())
                except:
                    messagebox.showerror("Notice", "Please select a tour from the list to edit it.")
                    return
                tourLab.place_forget()
                editTourBut.place_forget()
                TourListBox.place_forget()
                addTourBut.place_forget()
                addTourEnt.place_forget()
                removeSpotBut.place_forget()


                nodeLab = tk.Label(self, text = "All nodes on current floor", bg=NAVY,fg='white', font = helv15)
                nodeLab.place(relx = .903, rely = .13, anchor = 'c')
                NodeListBox = tk.Listbox(self, selectmode = 'single', font = Helvetica(15),
                    width = 15, height = 10, justify = 'center')
                NodeListBox.place(relx = .903, rely = .29, anchor = 'c')

                for name in currentBldg.get_names(currentFloor):
                    NodeListBox.insert("end", name)

                addNodeBut = tk.Button(self, bg = DARK_GREY,fg='black', font=helv15,
                text = "Add to tour", command=lambda: addLoc(tour))
                addNodeBut.place(relx = .903, rely = .47, anchor = 'c')

                tourListBox = tk.Listbox(self, selectmode = 'single', font = Helvetica(15),
                    width = 15, height = 10, justify = 'center')
                tourListBox.place(relx = .903, rely = .65, anchor = 'c')

                delNodeBut = tk.Button(self, bg = DARK_GREY,fg='black', font=helv15,
                text = "Delete from tour", command=lambda: delLoc(tour))
                delNodeBut.place(relx = .903, rely = .83, anchor = 'c')

                moveUpBut = tk.Button(self, bg = DARK_GREY,fg='black', font=helv15,
                text = "▲", width=1, command=lambda: reorder(tour, "UP"))
                moveUpBut.place(relx = .825, rely = .65, anchor = 'c')
                moveDownBut = tk.Button(self, bg = DARK_GREY,fg='black', font=helv15,
                text = "▼", width=1, command=lambda: reorder(tour, "DOWN"))
                moveDownBut.place(relx = .98, rely = .65, anchor = 'c')

                for name in currentBldg.tours[tour]:
                    tourListBox.insert("end", name)


                def addLoc(tour):
                    try:
                        name = NodeListBox.get(NodeListBox.curselection())
                    except:
                        messagebox.showinfo("Notice", "Please select a node from the top list to add to '"+tour+"'")
                        return

                    currentBldg.tours[tour].append(name)
                    tourListBox.insert("end", name)

                def delLoc(tour):
                    try:
                        name = tourListBox.get(tourListBox.curselection())
                    except:
                        messagebox.showinfo("Notice", "Please select a node from the bottom list above to remove")
                        return
                    idx = currentBldg.tours[tour].index(name)
                    currentBldg.tours[tour].pop(idx)
                    tourListBox.delete(0, 1000)
                    for name in currentBldg.tours[tour]:
                        tourListBox.insert("end", name)


                def reorder(tour, direction):
                    try:
                        name = tourListBox.get(tourListBox.curselection())
                    except:
                        messagebox.showinfo("Notice", "Please select a node from the bottom list to reorder")
                        return
                    idx = currentBldg.tours[tour].index(name)
                    temp = currentBldg.tours[tour][idx]
                    shift = 1
                    if(direction == "UP"):
                        shift = -1
                    currentBldg.tours[tour][idx] = currentBldg.tours[tour][idx+shift]
                    currentBldg.tours[tour][idx+shift] = temp
                    tourListBox.delete(0, 1000)
                    for name in currentBldg.tours[tour]:
                        tourListBox.insert("end", name)


        def editNode(editNodeBut):
            if (NodeListBox.curselection() != ()):

                addNodeButton.place_forget()
                enterNodeName.place_forget()
                finishNodeBut.place_forget()
                enterNodeType.place_forget()
                editToursBut.place_forget()
                editNodeBut.place_forget()

                value=NodeListBox.get(NodeListBox.curselection())
                NodeListBox.delete(0,'end')

                obj = currentBldg.get_node(value)
                for name in obj.associated:
                    NodeListBox.insert("end", name)


                #save node button replaced to save just node placements
                saveNodeStateButton = tk.Button(self, text= "Save",bg = DARK_GREY, font=helv15,
                fg='black', command=lambda: self.saveState(NodeList, currentBldg, currentFloor))
                saveNodeStateButton.place(relx =.91, rely = .88, anchor = 'c')

                backBut = tk.Button(self, bg = DARK_GREY,fg='black', font=helv15,
                text = "Back", command=lambda: master.switch_frame(dragAndDrop))
                backBut.place(relx = .91, rely = .95, anchor = 'c')

                addNameBut = tk.Button(self, bg = DARK_GREY,fg='black', font=helv15,
                text = "Add Nearby", command=lambda: addName())
                addNameBut.place(relx = .91, rely = .52, anchor = 'c')

                deleteNameBut = tk.Button(self, bg = DARK_GREY,fg='black', font=helv15,
                text = "Delete Nearby", command=lambda: deleteName())
                deleteNameBut.place(relx = .91, rely = .57, anchor = 'c')

                addNameEnt = tk.Entry(self, bg = 'black', fg = 'white',justify = 'center')
                addNameEnt.place(relx = .91, rely = .47, anchor = 'c')
                addNameEnt.delete(0,"end")
                addNameEnt.insert(0,"Enter Nearby")
                addNameEnt.bind("<Button-1>", lambda event, entry=addNameEnt: entry_handler(event, entry))

                wifiLab = tk.Label(self, text = "Wi-Fi Stored: " + currentBldg.has_wifi(obj),
                    bg=NAVY,fg='white', font = helv15)
                wifiLab.place(relx=.91,rely=.64, anchor = 'c')

                scanBut = tk.Button(self, bg = DARK_GREY,fg='black', font=helv15,
                    text = "Scan Wi-Fi", command=lambda: scanHelper(master, obj, wifiLab))
                scanBut.place(relx = .91, rely = .69, anchor = 'c')

                delWifiBut = tk.Button(self, bg = DARK_GREY,fg='black', font=helv15,
                    text = "Delete Wi-Fi Data", command=lambda: deleteWifi(master, obj, wifiLab))
                delWifiBut.place(relx = .91, rely = .74, anchor = 'c')

            # Display that no node is selected
            else:
                messagebox.showinfo("Notice", "Please select a node from the list to edit")

            def scanHelper(master, node, wifiLab):
                scanTimeRemaining = tk.Label(self, bg=DARK_GREY, fg=DARK_GREY, font = helv20, width=40, height=10)
                scanTimeRemaining.place(relx=0.5, rely=0.5, anchor='c')

                log.logging.info("Scanning Wi-Fi for node " + obj.name)
                total = ws.getScanAmount()
                scanning = Thread(target=node.scan_wifi)
                scanning.start()
                while(ws.getScansCompleted() < total):
                    scanTimeRemaining.config(fg='black',
                            text="Do Not Move!\nPerforming Wi-Fi Setup for '"
                                    + node.name + "'\n\nScans Complete: "
                                    + str(ws.getScansCompleted())+"/"+str(total))
                    master.update()

                scanning.join()
                ws.setScansCompleted(0)

                scanTimeRemaining.place_forget()
                wifiLab.config(text="Wi-Fi Stored: " + currentBldg.has_wifi(node))
                master.update()
                log.logging.info("Scanning Complete for node " + obj.name)

            def deleteWifi(master, obj, wifiLab):
                obj.wifi_data = []
                wifiLab.config(text="Wi-Fi Stored: NO")
                master.update()

            def deleteName():
                try:
                    value=NodeListBox.get(NodeListBox.curselection())
                except:
                    messagebox.showerror("Notice", "Please select an associated location from the list to remove it.")
                    return
                obj.associated.remove(value)
                NodeListBox.delete(0,'end')
                for name in obj.associated:
                    NodeListBox.insert("end", name)

                self.saveState(NodeList, currentBldg, currentFloor)

            def addName():
                val = addNameEnt.get()
                obj.associated.append(val)
                if(not NodeListBox == None):
                    NodeListBox.delete(0,'end')
                addNameEnt.delete(0,'end')
                for name in obj.associated:
                    NodeListBox.insert("end", name)

                self.saveState(NodeList, currentBldg, currentFloor)


        #leaving the admin page will be changed to going back to admin landing page
        def exitAdmin():
            global adminFlag
            global start
            global end
            start = ""
            end = ""

            adminFlag = False
            master.switch_frame(HomePage)

        def changeFloor(NewFloorIndex, startString = None, goalString = None):

            global currentBldg
            global currentFloor
            global currentFloorIndex
            global start
            global end

            if (startString != "Start" and startString != None):
                start = startString
            if (goalString != "Destination" and goalString != None):
                end = goalString

            if NewFloorIndex < 0:
                messagebox.showerror("Notice", "You are already on the lowest floor")

            elif (NewFloorIndex > len(currentBldg.floors) - 1):
                if adminFlag:
                    # pop up would you like to create new floor
                    if(str(messagebox.askquestion("Already on the top floor", "Would you like to add a new floor?")) == 'yes'):
                        master.switch_frame(newFloor)

                else:
                    # already at top floor
                    return None
            else:

                currentFloorIndex = NewFloorIndex
                currentFloor = currentBldg.floor_keys[currentFloorIndex]
                log.logging.info("Current Floor set to " + currentFloor + ", within building '" + currentBldg.name +"'")


                master.switch_frame(dragAndDrop)

    '''
    method: initalizeNodesInGUI
    Description: takes the previously saved Nodes from a global list and displays them on the GUI
    Note: Nodes from this function will be set up/ bound for drag and drop
    '''
    def initalizeNodesInGUI(self, nodelist):

        # initalize variables
        newNodeList = []
        tempList = []


        # start loop
        for item in nodelist:
            # take x and y coordinates from  list
            name = item[0]
            x= item[1]
            y= item[2]
            try:
                nodeType = item[4]
            except IndexError:
                nodeType = item[3]


            if nodeType == 't' or nodeType == 'T':
                # create new node at the x and y coordinates
                newNode = tk.Label(self, text = name, padx = 10, pady = 4, bg='pink')

            else:
                # create new node at the x and y coordinates
                newNode = tk.Label(self, text = name, padx = 10, pady = 4, bg='grey')
            newNode.place(x=x,y=y)

            # bind the node to drag and drop functions

            if adminFlag:
                newNode.bind("<Button-1>", self.clickNode)
                newNode.bind("<B1-Motion>", self.moveNode)
                newNode.bind("<ButtonRelease-1>", self.onRelease)

            # save the nodes data and new label ID to temp list
            newNodeList.append(name)
            newNodeList.append(newNode)
            newNodeList.append(x)
            newNodeList.append(y)
            newNodeList.append(nodeType)
            tempList.append(newNodeList)

            # prepare new node for next node
            newNodeList = []

        # clear Node List
        nodelist.clear()


        # loop through temp list and store nodes with new IDs in NodeList
        for items in tempList:
            nodelist.append(items)

        #clear tempList
        tempList.clear()


    '''
    method: saveState
    Description: saves the current state of the GUI by writing to a file
    '''
    def saveState(self, nodeslist, building, floor, listBox=None):

        # Add/update nodes
        for new in nodeslist:
            found = False
            for old in building.get_nodes(floor):
                if(new[0] == old.name):

                    old.set_loc((new[2], new[3]))
                    found = True
            if(not found):
                new_node = bd.Node(new[0], location=(new[2], new[3]))
                if(new[4].lower() == 't'):
                    new_node.transition = True
                elif(new[4].lower() == 's'):
                    new_node.status = bd.SECONDARY
                building.floors[floor].add_node(new_node)
                if(not listBox == None):
                    listBox.insert("end", new_node.name)


        # Remove Deleted Nodes
        to_remove = []
        for old in building.get_names(floor):
            found = False
            for new in nodeslist:
                if(old == new[0]):
                    found = True
            if(not found):
                to_remove.append(old)

        for node in to_remove:
            building.remove(node)

        building.set_directions()
        building.save(building.name.lower())
        if(not listBox == None):
            listBox.delete(0, 'end')
            names = currentBldg.get_names(currentFloor).copy()
            names.sort()
            for name in names:
                listBox.insert("end", name)


    '''
    method: clickNode
    Description: takes in an event(click of left mouse button) and prepares global list for adjusted Node coordinates
    Note: None
    Original Author: Bro Code(youTuber)
    Editor: David Robb
    '''
    def clickNode(self, event):

        event.widget.config(bg = 'yellow')
        widget = event.widget
        for Nodes in NodeList:
            if Nodes[1] != widget:
                Nodes[1].config(bg = 'grey')

            if Nodes[4] == 't' or Nodes[4] == 'T':
                Nodes[1].config(bg = 'pink')


        widget.startX = event.x
        widget.startY = event.y



    '''
    method: moveNode
    Description: takes in an event(mouse movement) and moves the node with the mouse
    Note: None
    Original Author: Bro Code(youTuber)
    Editor: David Robb
    '''
    def moveNode(self, event):

        if "<Button-1>":

            # initalize
            widget = event.widget
            widget.lift()

            # Track x and y coordinates
            x = widget.winfo_x() - widget.startX + event.x
            y = widget.winfo_y() - widget.startY + event.y

            # replace the Node at the new x and y
        widget.place(x=x,y=y)


    '''
    method: onRelease
    Description: when a node is un clicked/ realeased from the drag function
                onRealease saves the new  position of the node in the global list
    Note: None
    '''
    def onRelease(self, event):

            # initalize variables
            widget = event.widget
            x = widget.winfo_x()
            y = widget.winfo_y()
            name = ''
            movedNode = []
            nodeType = ''

            # prepare global list for adjusted Node coordinates
            for item in NodeList:

                # check to make sure node is in list
                if widget in item:
                    name = item[0]
                    nodeType = item[4]
                    NodeList.remove(item)

            # format Nodes Data
            movedNode = [name, widget, x, y, nodeType]

            if x < 20 and y < 20:
                widget.destroy()

            else:
                # store the Node list in global node list
                NodeList.append(movedNode)

    '''
    method: addNode
    Description: when called a new node with drag and drop features will be created
    Note: create for use as button command
    '''
    def addNode(self, master, nodelist, name, nodeType):


        # initialize variables
        newNodeList = []
        nodeName = name
        nameTaken = False

        typeList = ["p", "P", "s", "S", "t", "T"]

        for items in nodelist:
            if name == items[0]:
                nameTaken = True

        if nameTaken:
            messagebox.showerror("Notice", "Error: Node Name already in use")

        elif name == 'Node Name' or name == '':
            messagebox.showerror("Notice", "Nodes must have a name")

        elif nodeType not in typeList:
            messagebox.showerror("Incorrect Type",'Node type incorrect\nTypes: p - Primary, s - Secondary, t - Transitional')

        else:
            x= master.screen_width - 250
            y= master.screen_height - 166

            if name == '':
                messagebox.showerror("Notice", "Nodes must have a name")

            else:

                for Nodes in nodelist:

                        Nodes[1].config(bg = 'grey')

                if nodeType == 't' or nodeType == 'T':
                    # create new node
                    newNode = tk.Label( self, text = name, padx = 10, pady = 4, bg = 'pink' )

                elif nodeType == 's' or nodeType == 'S':
                    newNode = tk.Label( self, text = name, padx = 6, pady = 2, bg = 'yellow')

                else:
                    newNode = tk.Label( self, text = name, padx = 10, pady = 4, bg = 'yellow' )


                # place node at desired x y coordinates
                newNode.place(x=x,y=y)

                # bind the node to the drag and drop functions
                newNode.bind("<Button-1>", self.clickNode)
                newNode.bind("<B1-Motion>", self.moveNode)
                newNode.bind("<ButtonRelease-1>", self.onRelease)

                # add the Nodes data and label ID to global list
                newNodeList.append(nodeName)
                newNodeList.append(newNode)
                newNodeList.append(x)
                newNodeList.append(y)
                newNodeList.append(nodeType)

                nodelist.append(newNodeList)

    #color fuction
    def nodeColorStart (self):
        global NodeList


        for item in NodeList:
            item[1].config(bg = NAVY,fg = 'white')

    def toggle_pause(self):
        global pause
        pause = not pause

    def run_tour(self, master, tour, start=None, continueTour=None):

        if(not continueTour == None):
            continueTour.place_forget()

        tour_list = currentBldg.tours[tour]
        global currentTour
        currentTour = tour
        if(len(tour_list) < 2):
            log.logging.warning("Tour does not contain enough locations")
            return
        global remaining_tour
        if(remaining_tour == []):
            remaining_tour = tour_list
            log.logging.info("Tour: '"+str(tour)+"' started")
        else:
            remaining_tour = remaining_tour[1:]

        if(len(remaining_tour) < 2):
            remaining_tour = []
            return
        if(not start == None):
            start.place_forget()
        self.travel(master, remaining_tour[0], remaining_tour[1])
        if(len(remaining_tour) == 2):
            remaining_tour = []
            log.logging.info("Tour: '"+str(tour)+"' complete")
        master.switch_frame(dragAndDrop)
        return


    def travel_starter(self, master, start, end, startButton=None):
        startNode = currentBldg.get_node_by_multiname(start)
        endNode = currentBldg.get_node_by_multiname(end)
        if(startNode == None or endNode == None):
            messagebox.showerror("Error", "Unknown node name")
            return
        startButton.place_forget()
        self.travel(master, startNode.name, endNode.name)

    def travel(self, master, start, end, continueButton=None):

        global NodeList
        global currentPath
        global currentPathPlace
        global currentFloor
        global currentFloorIndex
        global path_to_start
        global path_running
        global pause

        path_running = True

        if(not continueButton == None):
            continueButton.place_forget()

        names = currentBldg.get_names()
        helv36 = tkFont.Font(family='Helvetica', size=20, weight='bold')
        img = ImageTk.PhotoImage(Image.open("images/robot.png").resize((28,23)))
        robot = tk.Label(image= img)

        if(not start in names or not end in names):
             messagebox.showerror("Error", "Error: Unknown Node Name")
             return

        # Calculate nodes to visit
        path = currentBldg.get_path(start, end)

        # Scan Wi-Fi to estimate position while a tour is running
        ws.start_scanning(currentBldg.get_nodes_by_names(path))

        # Switch to floor that contains start node if not there
        if(not start in currentBldg.get_names(currentFloor)):

            path_to_start = True
            currentPath = path
            currentFloor = currentBldg.get_floor(start)
            currentFloorIndex = currentBldg.floor_keys.index(currentFloor)
            log.logging.info("Current Floor set to "
                    + currentFloor + ", within building " + currentBldg.name)
            # Switch to next floor to continue route
            master.switch_frame(dragAndDrop)
            return

        log.logging.info("Begin route from "+start+" to "+end)

        for node in NodeList:

            if node[0] not in path:
                if(node[4] == 's' or node[4] == 'S'):
                     node[1].lower()

            if(not (node[0] == path[0] or node[0] == path[-1])):
                node[1].config(bg="grey", fg = 'black')

            if(node[0] == path[0]):
                node[1].config(bg="green", fg="white")
                x = node[1].winfo_x()
                y = node[1].winfo_y()

                robot.place(x=x,y=y)



            if(node[0] == path[-1]):
                node[1].config(bg="red", fg="white")

        for name in path[1:-1]:
            for node in NodeList:
                if(node[0] == name):
                    master.update()
                    time.sleep(0.5)
                    node[1].config(bg="yellow", fg="black")
        master.update()

        header = "Directions: "
        transitions = currentBldg.get_trans_by_name()
        current = 0
        while(current < len(path)):
            desc = currentBldg.next_direction(path, current)
            if(current == len(path)-1):
                directLabel.place_forget()
                master.update()
                # Stop scanning Wi-Fi
                ws.stop_scanning()
                messagebox.showinfo("Notice", desc)
                break

            directLabel = tk.Label(self, text = header + desc, bg = NAVY, fg ='white',font = helv36)
            directLabel.place(relx = .2, rely = .93)
            master.update()

            # Wait till robot exits elevator, this box is for human users and demonstrations
            if(not current == len(path)-1 and
                path[current] in transitions and
                path[current+1] in transitions):

                # Change globals for current floor and path
                currentFloor = currentBldg.get_floor(path[current+1])
                log.logging.info("Current Floor set to " + currentFloor + ", within building " + currentBldg.name)
                currentFloorIndex = currentBldg.floor_keys.index(currentFloor)
                currentPath = path[current+1:]

                # Switch to next floor to continue route
                master.switch_frame(dragAndDrop)
                return


            if(pause):
                messagebox.showinfo("", "Click OK to Resume")
                self.toggle_pause()

            # Seconds to travel
            time_to_travel = currentBldg.get_dist(path[current], path[current+1])/ROBOT_SPEED
            log.logging.info("Waiting for " + str(round(time_to_travel, 2))
                             + " seconds to go from " + path[current]
                             + " to " + path[current+1])
            start = time.perf_counter()
            while(time.perf_counter() - start < time_to_travel):
                pass

            current += 1
            for node in NodeList:
                if(node[0] == path[current-1]):
                    node[1].config(bg="grey", fg = 'black')
                try:
                    if(node[0] == path[current]):
                        node[1].config(bg="green")
                        x = node[1].winfo_x()
                        y = node[1].winfo_y()
                        robot.place(x=x,y=y)
                except IndexError:
                    pass
            directLabel.place_forget()
            master.update()

        # No path is running, remove current path
        currentPath = []
        # Move robot image off screen
        robot.place(x=99999999,y=99999999)

        for node in NodeList:
            node[1].lift()

        # Recolor nodes to NAVY
        self.nodeColorStart()
        log.logging.info("Route complete, current location now " + end)
        path_running = False
        master.switch_frame(dragAndDrop)


if __name__ == "__main__":
    app = TourGuideApp()
    app.mainloop()
    ws.stop_scanning()
