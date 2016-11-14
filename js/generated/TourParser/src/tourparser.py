
import re
import datetime
import os
filesys = os.path.dirname(os.path.realpath(__file__)) + "\\"
print filesys
# filesys = ""

def generateMenu():
    menu = readCSV(filesys + "Menu.csv")
    js = open(filesys + "menu_lists.js", "w")
    now = datetime.datetime.now()
    
    js.write("/*Autogenerated from Menu.csv on " + now.date().isoformat()+ " at " + now.time().isoformat() + "*/\n")
    buildMenu(menu, js, [])
    js.close()
    
def buildMenu(m, js, loc):
    if len(m) == 0:
        return 
    menu = m[0] 
    indent = 0
    while menu[indent] == "":
        indent = indent +1 #Check for length of menu
    if indent == len(loc) + 1: #Starting a new submenu
        myLoc = loc + [0]
    elif indent > len(loc) + 1:
        print "Too much indentation: " + str(menu) + " " + str(loc)
    elif indent == 0:
        myLoc = []
    else:
        #print str(indent)
        #print str(loc)
        myLoc = loc[0:indent-1] + [loc[indent-1]+1]
        
  
    js.write(mvName(myLoc) + " = ")
    menuName = menu[indent]
    icon = menu[indent + 1]
    if len(menu) == indent + 2 or menu[indent + 2] == "": #Submenu here
        js.write("menu_sub(" + jsString(menuName) + ", " + jsString(icon) + ");\n")
    elif menu[indent + 2] == "external":
        js.write("menu_external(" +  jsString(menuName) + ", " + jsString(icon) + ", " +
                    jsString(menu[indent + 3]) + ");\n")
    elif menu[indent + 2] == "location":
        js.write("menu_location(" +  jsString(menuName) + ", " + jsString(icon) + ", " +
                    jsString(menu[indent + 3]) + ");\n")
    else:
        print "Unrecognized menu type: " + str(menu)
    if len(loc) != 0:
        js.write(mvName(myLoc[0:len(myLoc) - 1]) + ".items.push(" + mvName(myLoc)
                 + ");\n")
    buildMenu(m[1:], js, myLoc)
    
def mvName(loc):
    r = "menu"
    for i in loc:
        r = r + "_" + str(i)
    return r
      
    
def generateLoc():
    locations = readCSV(filesys + "locations.csv")
    #print str(locations)
    locations = locations[1:]#remove headers
    js = open(filesys + "locations.js", "w")
    now = datetime.datetime.now()
    
    
    js.write("/*Autogenerated from locations.csv on " + now.date().isoformat()+ " at " + now.time().isoformat() + "*/\n")
    allLocs = []
    js.write("var locations = []\n")
    locInfo = {}
    for loc in locations: 
        tag = loc[0]
        allLocs.append(tag)
        title = loc[1]
        locationType = loc[2]
        description = loc[3]
        onCampus = loc[4] == "T" #Check to make sure T/F
        if len(loc) >= 6:
            
            pixelCoords = parseP2(loc[5])
            if pixelCoords is None:
                pixelCoords = 0,0 #Fix this later, Error Message
        else:
            pixelCoords = 0,0
    
        nextLoc = "#begin"
        arrowType = "left"
        arrowLoc = 0,0
        ttip = ""
        if(len(loc)>= 7 ):
            nextLoc = loc[6]
        if(len(loc)>= 8 ):
            arrowType = loc[7]
        if(len(loc)>= 9 ):
            ttip = loc[8]
        if(len(loc)>= 10 ):
            arrowLoc = parseP2(loc[9])
        locInfo[tag] = nextLoc, arrowType, ttip, arrowLoc, locationType
        #print str(locInfo[tag])
        
            
        print "Reading Location " + tag
        js.write("locations.push(new Location(" + jsString(tag) + ", ")
        js.write(jsString(title) + ", ")
        js.write(jsString(locationType) + ", \n" )
        js.write("     " + jsString(description) + ", ")
        js.write(jsBool(onCampus) + ", ")
        js.write(str(pixelCoords[0]) + ", ")
        js.write(str(pixelCoords[1]) + "));\n ")
    js.write("\n")
    js.write("navs = []\n")
    for loc in allLocs:
        if (loc != "#begin"):
            print "Writing Nav: " + loc
            back = "#begin"
            tipBack = "Return to the Start"
            typeBack = "academic"
            nextLoc, arrowType, ttip, arrowLoc, locationType = locInfo[loc]
            tipNext = locInfo[nextLoc][2]
            typeNext = locInfo[nextLoc][4]

            for backLoc in allLocs:
                if (locInfo[backLoc][0] == loc):
                    back = backLoc
                    tipBack = locInfo[backLoc][2]
                    typeBack = locInfo[backLoc][4]



            js.write("navs.push(new Navigation(")
            js.write(jsString(loc) + ", ")
            js.write(jsString(loc + "_to_" + nextLoc)+ ", ")
            js.write(jsString(tipNext) + ", ")
            js.write(jsString(arrowType) + ", ")
            js.write(str(arrowLoc[0]) + ", ")
            js.write(str(arrowLoc[1]) + ", ")
            js.write(str(locTypeToNum(typeNext)) + "));\n ")


            js.write("navs.push(new Navigation(")
            js.write(jsString(loc) + ", ")
            js.write(jsString(loc + "_to_" + back)+ ", ")
            js.write(jsString(tipBack) + ", ")
            js.write('"back", 50, 17, ')
            js.write(str(locTypeToNum(typeBack)) + "));\n ")



  
    js.close()
    
def locTypeToNum(t):
    if(t == "academic"):
        return 1
    if(t == "studentlife"):
        return 2
    if(t == "athletic"):
        return 3
    print "Invalid tour number: " + t
    return 0
    
# Convert a csv file to a 2-d list of strings.  Recognize the Excel quoting convention (fields with commas are in double quotes, quotes in quoted fields are doubled
def readCSV(file):
    f = open(file, "r")
    lines = []
    for line in f:
        line = line[0:len(line)-1]  # Strip off final newline
        i = 0
        res = []
        while i < len(line):
            #print "line: " + line[i:]
            ch = line[i]
            if ch == ",":
                res.append("")
                #print "empty field " + str(res)
                i = i + 1
            elif ch == '"':
                tok = ""
                i = i + 1
                while i < len(line):
                    if line[i] == '"':
                        if i+1 < len(line) and line[i+1] == '"':
                            tok = tok + '"'
                            i = i + 2
                        else:
                            res.append(tok)
                            i = i + 1
                            if i<len(line):
                                if line[i] == ",":
                                    i = i + 1
                                else:
                                    print "Junk after quoted entry: " + line
                            break
                    else:
                        tok = tok + line[i]
                        i = i + 1
                        if i == len(line):
                            print "Unmatched quote on " + line
            else:
                tok = ch
                i = i + 1
                while i < len(line):
                    if line[i] == ",":
                        i = i + 1
                        break
                    else:
                        tok = tok + line[i]
                        i = i + 1
                res.append(tok)
        lines.append(res)
    return lines

urlRegex = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

# Apply fn, a function from String to String, to each URL in a string.  Characters outside the url remain unchanged.
def processUrls(s, fn):
    res = ""
    while (True):
        print "Matching: " + s
        m = urlRegex.search(s)
        if m is None:
            print "No match"
            res = res + s
            return res
        print "Match from " + str(m.start()) + " to " + str(m.end())
        res = res + s[0:m.start()]
        res = res + fn(s[m.start():m.end()])
        s = s[m.end():]


# Convert a string to Javascript source code format (add double quote, escape double quotes in the string
def jsString(s):
    res = '"'
    for c in s:
        if c == '"':
            res = res + '\\"'
        else:
            res = res + c
    return res + '"'

def jsBool(b):
    if b:
        return "true"
    else: 
        return "false"

def parseP2(s):
    a = s.split(",")
    if len(a) == 2:
        try:
            x = int(a[0])
            y = int(a[1])
        except ValueError:
            return None
        return x,y
    return None

generateLoc()
# Tests
#print readCSV("C:\\Users\\fac_peterson\\Desktop\\TourParser\\src\\test.csv") - for JP's crappy computer that doesn't support UNC paths
#print readCSV("test.csv") # should work on most computers

#print jsString("abc")
#print jsString('"abc"')

#print processUrls("hello http://western.edu and http://haskell.org", lambda s : "[url:" + s + "]")

#print str(parseP2("1,2"))
#print str(parseP2(" 1, 2"))
#print str(parseP2("1,2,3"))
